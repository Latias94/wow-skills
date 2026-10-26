"""Cache ordinary item-ID references, never complete configured gear tooltips.

Run with Python and Pillow. Successful entries are reused; failed entries retain
their error and are retried on the next run. Only report-items.json is written.
"""

import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import html
from http.client import HTTPException
from io import BytesIO
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

from PIL import Image


ROOT = Path(__file__).resolve().parent
CACHE_PATH = ROOT / "report-items.json"
TIMEOUT = 20
MAX_RETRIES = 2
MAX_WORKERS = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
)
REFERENCE_NOTE = (
    "按物品 ID 缓存的普通参考，不是完整配置 tooltip；"
    "未指定装等、升级轨道、品质、附魔、宝石、制造属性、美化或其他 bonus。"
    "source 仅记录本条 tooltip 明示的掉落信息，否则为 unknown。"
)


def collect_item_ids():
    build = (ROOT / "build-study.py").read_text(encoding="utf-8-sig")
    # This dated study uses six-digit item literals; bonuses and seeds differ.
    ids = set(re.findall(r"\b[1-9]\d{5}\b", build))
    research = json.loads((ROOT / "elite-research.json").read_text(encoding="utf-8"))
    ids.update(research["items"])
    for mode in research["modes"].values():
        for rows in mode["selections"].values():
            ids.update(str(row["item_id"]) for row in rows if row.get("item_id"))
    ids.update(
        str(effect["item_id"])
        for effect in research["embellishment_effects"].values()
        if effect.get("item_id")
    )
    snapshot = ROOT.parents[1] / "snapshots" / f"{ROOT.name}.simc"
    exported = snapshot.read_text(encoding="utf-8-sig")
    # Include equipped items, commented bag items, gems and catalyst originals.
    for match in re.finditer(
        r"(?:^|,)(?:id|gem_id|redirected_base_stats)=([0-9/]+)", exported, re.M
    ):
        ids.update(value for value in match[1].split("/") if int(value) > 0)
    return sorted(ids, key=int)


def request_bytes(url):
    for attempt in range(MAX_RETRIES + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.read()
        except (OSError, urllib.error.URLError, HTTPException) as error:
            permanent = isinstance(error, urllib.error.HTTPError) and (
                400 <= error.code < 500 and error.code not in (408, 429)
            )
            if permanent or attempt == MAX_RETRIES:
                raise
            delay = attempt + 1
            print(
                f"retry={attempt + 1}/{MAX_RETRIES} delay={delay}s "
                f"url={url} error={type(error).__name__}: {error}",
                flush=True,
            )
            time.sleep(delay)


def fetch_item(ident):
    url = f"https://nether.wowhead.com/tooltip/item/{ident}?dataEnv=1&locale=4"
    entry = {
        "name": "",
        "icon": "",
        "tooltip": "",
        "source": "unknown",
        "url": url,
        "reference_note": REFERENCE_NOTE,
    }
    stage = "tooltip"
    try:
        payload = json.loads(request_bytes(url).decode("utf-8-sig"))
        if payload.get("error"):
            raise ValueError(str(payload["error"]))
        for key in ("name", "tooltip"):
            value = payload.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Missing {key}")
            entry[key] = value
        dropped = re.findall(
            r'<div\b[^>]*\bwhtt-droppedby\b[^>]*>(.*?)</div>',
            entry["tooltip"],
            re.S | re.I,
        )
        sources = [html.unescape(re.sub(r"<[^>]+>", "", value)).strip() for value in dropped]
        entry["source"] = "; ".join(dict.fromkeys(value for value in sources if value)) or "unknown"
        stage = "icon"
        icon = payload.get("icon", "")
        if not isinstance(icon, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", icon):
            raise ValueError("Missing or invalid icon name")
        icon_url = f"https://wow.zamimg.com/images/wow/icons/large/{icon.lower()}.jpg"
        icon_bytes = request_bytes(icon_url)
        with Image.open(BytesIO(icon_bytes)) as image:
            output = BytesIO()
            image.convert("RGB").save(output, format="JPEG", quality=85)
        entry["icon"] = "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode("ascii")
    except Exception as error:
        entry["error"] = f"{stage}: {type(error).__name__}: {error}"
    entry["retrieved_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return ident, entry


def save_cache(cache):
    ordered = {key: cache[key] for key in sorted(cache, key=int)}
    CACHE_PATH.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ids = collect_item_ids()
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    pending = []
    for ident in ids:
        entry = cache.get(ident, {})
        complete = (
            not entry.get("error")
            and entry.get("name")
            and entry.get("tooltip")
            and entry.get("icon", "").startswith("data:image/jpeg;base64,")
            and entry.get("url")
            == f"https://nether.wowhead.com/tooltip/item/{ident}?dataEnv=1&locale=4"
        )
        if complete:
            entry["reference_note"] = REFERENCE_NOTE
        else:
            pending.append(ident)
    print(f"items={len(ids)} cached={len(ids) - len(pending)} pending={len(pending)} workers={MAX_WORKERS}", flush=True)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(fetch_item, ident) for ident in pending]
        for count, future in enumerate(as_completed(futures), 1):
            ident, entry = future.result()
            cache[ident] = entry
            status = entry.get("error", "ok")
            print(f"[{count}/{len(pending)}] {ident} {entry['name']} {status}", flush=True)
            if count % 10 == 0:
                save_cache(cache)
    save_cache(cache)
    failures = [ident for ident in ids if cache[ident].get("error")]
    print(json.dumps({"total": len(ids), "succeeded": len(ids) - len(failures), "failed_ids": failures}, ensure_ascii=False), flush=True)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
