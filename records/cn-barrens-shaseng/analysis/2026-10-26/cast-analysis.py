"""Analyze the two local cast/buff exports without network access or damage inference."""

from bisect import bisect_right
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from statistics import mean, median
import json


ROOT = Path(__file__).resolve().parent
SAMPLES = (
    ("elite", "Bisset", "4Ab97gnVjKhZP1Nf", 28, 1, 28623648),
    ("shaseng", "沙僧", "G9HVRL18nAkzFyab", 4, 2, 4979324),
)
NAMES = {
    113656: "怒雷", 101546: "神鹤", 107428: "旭日", 100784: "幻灭",
    100780: "猛虎", 467307: "疾风踢", 152175: "升龙", 123904: "白虎",
    1249625: "乾元", 443028: "天神", 1272696: "乾元镇踏", 393056: "真气破",
    443591: "众神聚心机制事件",
}
CORE = {113656, 101546, 107428, 100784, 100780, 467307, 152175}
BLUE = {443421: "普通青龙", 1238904: "乾元青龙", 443616: "大青龙"}
BUFF_NAMES = {**BLUE, 1249625: "乾元", 123904: "白虎", 443028: "天神通道", 1248992: "天神可用"}
STATE_IDS = set(BUFF_NAMES) - {1248992}


def read_json(name):
    raw = (ROOT / name).read_bytes()
    return json.loads(raw.decode("utf-8-sig")), {"file": name, "sha256": sha256(raw).hexdigest()}


def ability(event):
    return event.get("abilityGameID") or event.get("ability", {}).get("guid")


def paged_validation(data):
    events = data["events"]
    page_count = sum(page["count"] for page in data["pages"])
    if not data.get("complete") or data.get("nextPageTimestamp") is not None:
        raise ValueError("The input export is not complete.")
    if page_count != len(events):
        raise ValueError("Page counts do not match the event array.")
    return {
        "complete": True, "next_page_timestamp": None, "pages": len(data["pages"]),
        "raw_events": len(events), "page_event_sum": page_count,
        "event_types": dict(Counter(e["type"] for e in events)),
        "observed_at": data.get("observedAt"),
    }


def interval_summary(intervals):
    durations = [x["duration_ms"] / 1000 for x in intervals if x["closed"] and not x["refresh_indices"]]
    return {
        "interval_count": len(intervals), "duration_ms": sum(x["duration_ms"] for x in intervals),
        "closed_unrefreshed_count": len(durations),
        "closed_unrefreshed_duration_s": {
            "min": min(durations), "median": median(durations), "max": max(durations)
        } if durations else None,
    }


def parse_buffs(data, source, fight_id, start, end):
    spans = {sid: [] for sid in BUFF_NAMES}
    opened, seen, roles, anomalies = {}, set(), Counter(), []
    selected = duplicates = rejected = 0
    for index, event in sorted(enumerate(data["events"]), key=lambda pair: (pair[1]["timestamp"], pair[0])):
        sid = ability(event)
        if sid not in spans:
            continue
        roles[(event.get("sourceID"), event.get("targetID"))] += 1
        if event.get("sourceID") != source or event.get("targetID") != source or event.get("fight") != fight_id:
            rejected += 1
            continue
        selected += 1
        signature = json.dumps(event, sort_keys=True, ensure_ascii=False)
        if signature in seen:
            duplicates += 1
            continue
        seen.add(signature)
        timestamp, kind = event["timestamp"], event["type"]
        if kind == "applybuff":
            if sid in opened:
                anomalies.append({"type": "apply_while_open", "spell_id": sid, "event_index": index})
            else:
                opened[sid] = {"start_ms": timestamp, "apply_index": index, "refresh_indices": []}
        elif kind == "refreshbuff":
            if sid in opened:
                opened[sid]["refresh_indices"].append(index)
            else:
                anomalies.append({"type": "refresh_without_apply", "spell_id": sid, "event_index": index})
        elif kind == "removebuff":
            if sid not in opened:
                anomalies.append({"type": "remove_without_apply", "spell_id": sid, "event_index": index})
                continue
            span = opened.pop(sid)
            span.update(end_ms=timestamp, remove_index=index, closed=True)
            spans[sid].append(span)
    for sid, span in opened.items():
        span.update(end_ms=end, remove_index=None, closed=False)
        spans[sid].append(span)
    for intervals in spans.values():
        for span in intervals:
            span["start_ms"], span["end_ms"] = max(start, span["start_ms"]), min(end, span["end_ms"])
            span["duration_ms"] = span["end_ms"] - span["start_ms"]
            span["start_relative_s"] = (span["start_ms"] - start) / 1000
            span["end_relative_s"] = (span["end_ms"] - start) / 1000
    return spans, {
        "selected_raw_events": selected, "selected_exact_duplicates_skipped": duplicates,
        "selected_events_rejected_by_source_target_fight": rejected,
        "roles_before_filter": [{"source_id": s, "target_id": t, "count": n} for (s, t), n in roles.items()],
        "anomalies": anomalies,
    }


def active_ids(spans, timestamp, ids=STATE_IDS):
    return sorted(sid for sid in ids if any(x["start_ms"] <= timestamp < x["end_ms"] for x in spans[sid]))


def overlap_ms(intervals, start, end):
    return sum(max(0, min(end, x["end_ms"]) - max(start, x["start_ms"])) for x in intervals)


def event_ref(event):
    return {key: event[key] for key in (
        "event_index", "timestamp_ms", "relative_s", "spell_id", "name", "target_id", "target_instance"
    )}


def scope_keys(segment):
    clock = "burst_30s" if segment["in_white_30s"] else "outside_30s"
    actual = "buff_burst" if segment["active_buff_ids"] else "buff_steady"
    kind = segment["pull_kind"]
    keys = ["all", clock, actual, kind]
    if segment["pull_ids"]:
        keys += ["recognized_pulls", "recognized_" + clock, "recognized_" + actual]
    if kind in {"boss", "trash"}:
        keys += [kind + "_" + clock, kind + "_" + actual]
    return keys


def metric(counter, duration_ms):
    return {
        "duration_ms": duration_ms,
        "cast_counts": {str(sid): counter[sid] for sid in NAMES},
        "core_cast_count": sum(counter[sid] for sid in CORE),
        "core_cpm": sum(counter[sid] for sid in CORE) * 60000 / duration_ms if duration_ms else None,
        "spell_cpm": {str(sid): counter[sid] * 60000 / duration_ms if duration_ms else None for sid in NAMES},
    }


def conduit_context(event, ledger, spans, window_start):
    timestamp = event["timestamp_ms"]
    prior_wdp = [x for x in ledger if x["spell_id"] == 152175 and x["event_index"] < event["event_index"] and x["timestamp_ms"] <= timestamp]
    wdp = prior_wdp[-1] if prior_wdp else None
    next_core = next((x for x in ledger if x["spell_id"] in CORE and x["event_index"] > event["event_index"] and x["timestamp_ms"] >= timestamp), None)
    small = {}
    for sid in (443421, 1238904):
        previous = [x for x in spans[sid] if x["start_ms"] <= timestamp]
        span = previous[-1] if previous else None
        small[str(sid)] = {
            "active_at_cast": bool(span and timestamp < span["end_ms"]),
            "latest_interval": span,
            "cast_minus_observed_remove_ms": timestamp - span["end_ms"] if span else None,
        }
    channel = next((x for x in spans[443028] if abs(x["start_ms"] - timestamp) <= 100), None)
    big = next((x for x in spans[443616] if timestamp <= x["start_ms"] <= timestamp + 5000), None)
    return {
        "cast": event_ref(event), "since_white_s": (timestamp - window_start) / 1000,
        "previous_wdp": event_ref(wdp) if wdp else None,
        "since_previous_wdp_s": (timestamp - wdp["timestamp_ms"]) / 1000 if wdp else None,
        "previous_wdp_in_this_window": bool(wdp and wdp["timestamp_ms"] >= window_start),
        "next_core_cast": event_ref(next_core) if next_core else None,
        "next_core_delay_s": (next_core["timestamp_ms"] - timestamp) / 1000 if next_core else None,
        "small_blue_state": small,
        "both_small_inactive_at_cast": not any(x["active_at_cast"] for x in small.values()),
        "channel_buff_interval": channel,
        "big_blue_after_cast": big,
        "big_blue_apply_delay_s": (big["start_ms"] - timestamp) / 1000 if big else None,
    }


def analyze_sample(config):
    key, name, report, fight_id, source, expected_start = config
    casts, cast_input = read_json(f"wcl-{key}-casts.json")
    buffs, buff_input = read_json(f"wcl-{key}-buffs.json")
    metadata, meta_input = read_json(f"wcl-{key}-metadata.json")
    validation = {"casts": paged_validation(casts), "buffs": paged_validation(buffs)}
    fight = next(x for x in metadata["fights"] if x["id"] == fight_id)
    start, end = fight["start_time"], fight["end_time"]
    if start != expected_start:
        raise ValueError(f"Unexpected fight start for {key}.")
    actor = next(x for x in metadata["friendlies"] if x["id"] == source)
    if actor["name"] != name:
        raise ValueError(f"Unexpected actor for {key}.")
    spans, validation["buff_roles"] = parse_buffs(buffs, source, fight_id, start, end)
    source_roles = Counter((e.get("sourceID"), e.get("fight")) for e in casts["events"])
    validation["casts"]["source_fight_counts"] = [
        {"source_id": s, "fight_id": f, "count": n} for (s, f), n in source_roles.items()
    ]
    signatures = [json.dumps(e, sort_keys=True, ensure_ascii=False) for e in casts["events"]]
    validation["casts"]["exact_duplicate_count"] = len(signatures) - len(set(signatures))
    if any(e.get("sourceID") != source or e.get("fight") != fight_id for e in casts["events"]):
        raise ValueError(f"Unexpected cast source or fight for {key}.")
    ledger = []
    outside = 0
    for index, event in enumerate(casts["events"]):
        if event["type"] != "cast":
            continue
        if not start <= event["timestamp"] < end:
            outside += 1
            continue
        sid = ability(event)
        ledger.append({
            "event_index": index, "timestamp_ms": event["timestamp"],
            "relative_s": (event["timestamp"] - start) / 1000,
            "spell_id": sid, "name": NAMES.get(sid, event.get("ability", {}).get("name", str(sid))),
            "target_id": event.get("targetID", event.get("target", {}).get("id")),
            "target_instance": event.get("targetInstance"),
            "reported_is_off_gcd": event.get("ability", {}).get("isOffGCD"),
        })
    ledger.sort(key=lambda x: (x["timestamp_ms"], x["event_index"]))
    validation["casts"]["cast_events_outside_fight"] = outside
    whites = [x for x in ledger if x["spell_id"] == 123904]
    windows = [{"index": i, "start_ms": w["timestamp_ms"], "end_ms": min(end, w["timestamp_ms"] + 30000)} for i, w in enumerate(whites, 1)]
    pulls = [{
        "id": p["id"], "name": p["name"], "boss_id": p["boss"],
        "kind": "boss" if p["boss"] else "trash",
        "start_ms": max(start, p["start_time"]), "end_ms": min(end, p["end_time"]),
    } for p in fight["dungeonPulls"] if p["start_time"] < end and p["end_time"] > start]
    cuts = {start, end}
    for interval in pulls + windows + [x for sid in STATE_IDS for x in spans[sid]]:
        cuts.update((interval["start_ms"], interval["end_ms"]))
    cuts = sorted(cuts)
    segments = []
    for lo, hi in zip(cuts, cuts[1:]):
        current_pulls = [p for p in pulls if p["start_ms"] <= lo < p["end_ms"]]
        kinds = {p["kind"] for p in current_pulls}
        segments.append({
            "start_ms": lo, "end_ms": hi, "duration_ms": hi - lo,
            "start_relative_s": (lo - start) / 1000, "end_relative_s": (hi - start) / 1000,
            "pull_ids": [p["id"] for p in current_pulls],
            "pull_kind": next(iter(kinds)) if len(kinds) == 1 else ("unclassified" if not kinds else "ambiguous"),
            "in_white_30s": any(w["start_ms"] <= lo < w["end_ms"] for w in windows),
            "active_buff_ids": active_ids(spans, lo),
        })
    duration, counts, patterns, pattern_duration = Counter(), {}, {}, Counter()
    for segment in segments:
        for label in scope_keys(segment):
            duration[label] += segment["duration_ms"]
            counts.setdefault(label, Counter())
        pattern = "+".join(map(str, segment["active_buff_ids"])) or "none"
        pattern_duration[pattern] += segment["duration_ms"]
        patterns.setdefault(pattern, Counter())
    for event in ledger:
        segment = segments[bisect_right(cuts, event["timestamp_ms"]) - 1]
        event.update({k: segment[k] for k in ("pull_ids", "pull_kind", "in_white_30s", "active_buff_ids")})
        for label in scope_keys(segment):
            counts[label][event["spell_id"]] += 1
        pattern = "+".join(map(str, segment["active_buff_ids"])) or "none"
        patterns[pattern][event["spell_id"]] += 1
    scopes = {label: metric(counts[label], ms) for label, ms in duration.items()}
    for i, (window, white) in enumerate(zip(windows, whites)):
        lo, hi = window["start_ms"], window["end_ms"]
        events = [x for x in ledger if lo <= x["timestamp_ms"] < hi]
        window.update({
            "white_cast": event_ref(white), "relative_s": white["relative_s"], "duration_ms": hi - lo,
            "previous_white_interval_s": (lo - windows[i - 1]["start_ms"]) / 1000 if i else None,
            "clipped_at_fight_end": hi - lo < 30000,
            "anchor_pull_ids": white["pull_ids"], "anchor_pull_kind": white["pull_kind"],
            "cast_counts": {str(sid): sum(e["spell_id"] == sid for e in events) for sid in NAMES},
            "conduits": [conduit_context(e, ledger, spans, lo) for e in events if e["spell_id"] == 443028],
            "blue": {str(sid): {
                "duration_ms": overlap_ms(spans[sid], lo, hi),
                "fof_starts": sum(e["spell_id"] == 113656 and sid in e["active_buff_ids"] for e in events),
            } for sid in BLUE},
            "sequence": [event_ref(e) for e in events if e["spell_id"] in NAMES and e["spell_id"] != 393056],
        })
        window["any_blue_duration_ms"] = sum(
            max(0, min(hi, s["end_ms"]) - max(lo, s["start_ms"]))
            for s in segments if set(s["active_buff_ids"]) & BLUE.keys()
        )
        window["any_blue_fof_starts"] = sum(e["spell_id"] == 113656 and bool(set(e["active_buff_ids"]) & BLUE.keys()) for e in events)
    for pull in pulls:
        pull_events = [e for e in ledger if pull["id"] in e["pull_ids"]]
        pull.update(metric(Counter(e["spell_id"] for e in pull_events), pull["end_ms"] - pull["start_ms"]))
        pull["start_relative_s"], pull["end_relative_s"] = (pull["start_ms"] - start) / 1000, (pull["end_ms"] - start) / 1000
    gaps = [w["previous_white_interval_s"] for w in windows[1:]]
    blue_summary = {}
    for sid in BLUE:
        blue_summary[str(sid)] = {
            **interval_summary(spans[sid]),
            "fof_starts": sum(e["spell_id"] == 113656 and sid in e["active_buff_ids"] for e in ledger),
            "sck_starts": sum(e["spell_id"] == 101546 and sid in e["active_buff_ids"] for e in ledger),
        }
    blue_summary["union"] = {
        "duration_ms": sum(s["duration_ms"] for s in segments if set(s["active_buff_ids"]) & BLUE.keys()),
        "fof_starts": sum(e["spell_id"] == 113656 and bool(set(e["active_buff_ids"]) & BLUE.keys()) for e in ledger),
    }
    all_conduits = [c for w in windows for c in w["conduits"]]
    if len(all_conduits) != counts["all"][443028]:
        raise ValueError("A conduit cast falls outside the fixed white windows; add explicit outside handling.")
    consistency = {
        "time_partition": sum(s["duration_ms"] for s in segments) == end - start,
        "cast_clock_partition": counts["all"] == counts.get("burst_30s", Counter()) + counts.get("outside_30s", Counter()),
        "cast_buff_partition": counts["all"] == counts.get("buff_burst", Counter()) + counts.get("buff_steady", Counter()),
        "fof_blue_union_bounded": blue_summary["union"]["fof_starts"] <= counts["all"][113656],
        "selected_buff_reconstruction_clean": not validation["buff_roles"]["anomalies"],
    }
    if not all(consistency.values()):
        raise ValueError(f"Analysis consistency check failed for {key}: {consistency}")
    return {
        "key": key, "name": name, "report": report, "fight_id": fight_id, "source_id": source,
        "url": f"https://www.warcraftlogs.com/reports/{report}?fight={fight_id}&source={source}",
        "fight_start_ms": start, "fight_end_ms": end, "fight_duration_ms": end - start,
        "completion_time_metadata_ms": fight.get("completionTime"), "keystone_level": fight["keystoneLevel"],
        "inputs": [cast_input, buff_input, meta_input], "validation": validation, "checks": consistency,
        "scopes": scopes, "white_windows": windows,
        "white_interval_s": {"count": len(gaps), "min": min(gaps), "median": median(gaps), "mean": mean(gaps), "max": max(gaps)},
        "zenith_outside_30s": [event_ref(e) for e in ledger if e["spell_id"] == 1249625 and not e["in_white_30s"]],
        "blue_summary": blue_summary,
        "buff_duration_summary": {str(sid): interval_summary(spans[sid]) for sid in BUFF_NAMES},
        "buff_intervals": {str(sid): items for sid, items in spans.items()},
        "conduit_small_blue_summary": {
            "casts": len(all_conduits),
            "both_small_inactive_at_cast": sum(c["both_small_inactive_at_cast"] for c in all_conduits),
            "small_active_at_cast": sum(not c["both_small_inactive_at_cast"] for c in all_conduits),
            "small_active_and_observed_remove_more_than_50ms_later": sum(
                any(s["active_at_cast"] and s["cast_minus_observed_remove_ms"] < -50 for s in c["small_blue_state"].values()) for c in all_conduits
            ),
        },
        "state_combinations": {key: metric(patterns[key], ms) for key, ms in pattern_duration.items()},
        "pulls": pulls, "segments": segments, "cast_ledger": ledger,
    }


def make_examples(samples):
    opening, conduit = {}, {}
    for sample in samples:
        window = sample["white_windows"][0]
        sequence = window["sequence"]
        sun = next(e for e in sequence if e["spell_id"] == 107428)
        wdp = next(e for e in sequence if e["spell_id"] == 152175 and e["timestamp_ms"] >= sun["timestamp_ms"])
        middle = [e for e in sequence if sun["timestamp_ms"] < e["timestamp_ms"] < wdp["timestamp_ms"]]
        opening[sample["key"]] = {
            "white_relative_s": window["relative_s"], "first_sun": sun, "first_wdp": wdp,
            "fof_between_first_sun_and_first_wdp": sum(e["spell_id"] == 113656 for e in middle),
            "sequence": [e for e in sequence if e["timestamp_ms"] <= wdp["timestamp_ms"]],
        }
        context = window["conduits"][0]
        following_fof = next(e for e in sequence if e["spell_id"] == 113656 and e["timestamp_ms"] > context["cast"]["timestamp_ms"])
        conduit[sample["key"]] = {
            "white_relative_s": window["relative_s"], "context": context,
            "sequence": [e for e in sequence if context["previous_wdp"]["timestamp_ms"] <= e["timestamp_ms"] <= following_fof["timestamp_ms"]],
        }
    return {"opening_sun_to_wdp": opening, "opening_conduit_small_blue": conduit}


def fnum(value, digits=3):
    return "—" if value is None else f"{value:.{digits}f}"


def clock(seconds):
    minutes = int(seconds // 60)
    return f"{minutes:02d}:{seconds - minutes * 60:06.3f}"


def sequence_text(events, anchor):
    return " → ".join(f"{clock(e['relative_s'])}（白虎+{(e['timestamp_ms'] - anchor) / 1000:.3f}）{e['name']}[#{e['event_index']}]" for e in events)


def make_review(result):
    samples = result["samples"]
    elite, shaseng = samples
    lines = [
        "# 完整施法与增益的窄范围比较（2026-10-26）", "",
        "仅分析本地完整 cast/buff 与 dungeonPulls 元数据，未读取网页、操作 CDP、读取本轮 damage 或模拟个人收益。参考样本 Bisset 为毒牙祭坛 +23，沙僧为 +15；不同层数、拉法、目标寿命、构筑与增益持续时间限制直接比较。下文确认施法顺序和增益状态，不推断当时冷却、资源、暴击、逐跳伤害或最优选择。", "",
        "最需要交给主代理综合的两点：首轮旭日后的怒雷/升龙顺序不同；首轮沙僧开天神时普通青龙仍在，而 Bisset 已结束。它们是同一首轮的两处可复查观察，不是两份独立样本，更不是已经证明的伤害损失。", "",
        "## 数据与统计定义", "",
        "脚本 `python cast-analysis.py` 重建 `cast-analysis.json` 和本文件。JSON 保留输入 SHA-256、原始 events 数组的零基下标、绝对毫秒与相对秒、全部 cast 台账、真实 buff 区间、互斥分段及逐窗计数，便于主代理复核。", "",
        "| 样本 | 报告 / fight / source | 起点 ms | 战斗时长 s | cast 原始事件 / 页数 | buff 原始事件 / 页数 |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for s in samples:
        lines.append(f"| {s['name']} +{s['keystone_level']} | [{s['report']}]({s['url']}) / {s['fight_id']} / {s['source_id']} | {s['fight_start_ms']} | {s['fight_duration_ms']/1000:.3f} | {s['validation']['casts']['raw_events']} / {s['validation']['casts']['pages']} | {s['validation']['buffs']['raw_events']} / {s['validation']['buffs']['pages']} |")
    lines += ["", "两人的 cast/buff 均为 complete=true、next=null，分页 count 总和与数组长度一致；cast 无完全重复记录。选取的七种 buff 均严格过滤 sourceID=targetID=本玩家及对应 fight，重建无孤立移除/刷新。只计 type=cast，排除 begincast；不以页面 `isOffGCD` 字段估算 GCD，怒雷、神鹤等事件在该字段也被标为 true。", "",
        "核心 CPM 明确定义为怒雷113656、神鹤101546、旭日107428、幻灭100784、猛虎100780、疾风467307、升龙152175七种 cast 次数之和 ÷ 该统计域分钟数。它是动作密度，不是 GCD 利用率；白虎123904、天神443028、乾元1249625、乾元镇踏1272696、众神聚心443591另计机制/爆发事件，不由这些事件倒推玩家额外按键。真气破393056完全排除核心数及任何 GCD 计数，不用网页全部 cast 条数当按键数。", "",
        "两套时间轴并行：①白虎后固定 `[t0,t0+30s)` 是分析窗，30秒不是白虎或青龙实际持续时间；窗外只称窗外，不能自动称平稳。末窗遇战斗结束截断；汇总用并集不重复计时。②真实 buff 分段按白虎123904、乾元1249625、普通青龙443421、乾元青龙1238904、大青龙443616、天神通道443028的实际获得/移除边界切片，重叠组合单列，任何一种生效称“实际增益段”，六种皆无称“无上述增益段”。后者是本次平稳代理口径，不保证没有饰品/嗜血或场地机制；1248992仅是天神可用，不等于通道，不能据其单独判爆发。两套口径不互相替代。", "",
        "所有区间左闭右开；计数依 cast 时间归属。三种青龙的“覆盖”只指时间区间覆盖及其内怒雷起手数，不代表怒雷整条通道或逐跳伤害覆盖。施法/增益时间存在数毫秒不同，靠边界的归属保留原始值，不移动时间点。", "",
        "可识别 pull 时长取 metadata.dungeonPulls 区间并集；分子只取这些区间内的 cast，非全程次数硬除 pull 时长。Boss/trash 按 pull.boss 是否为0分类，不从目标名字猜；pull内时间仍可能含移动、免疫、死亡，不能等同玩家可输出时间。战斗时长用 end_time-start_time，不混用 completionTime。", "",
        "## 核心密度、固定分析窗与实际增益分段", "",
        "| 统计域 | Bisset 时长s / 核心数 / CPM / 怒雷 / 神鹤 | 沙僧 时长s / 核心数 / CPM / 怒雷 / 神鹤 |",
        "| --- | ---: | ---: |",
    ]
    labels = [("all", "战斗全程"), ("recognized_pulls", "可识别pull并集"), ("boss", "Boss pull"), ("trash", "小怪pull"), ("unclassified", "未归入pull"), ("burst_30s", "白虎后30s分析窗并集"), ("outside_30s", "固定分析窗外"), ("recognized_buff_burst", "pull内实际增益段"), ("recognized_buff_steady", "pull内无上述增益段"), ("boss_buff_burst", "Boss实际增益段"), ("boss_buff_steady", "Boss无上述增益段"), ("trash_buff_burst", "小怪实际增益段"), ("trash_buff_steady", "小怪无上述增益段")]
    for label, title in labels:
        cells = []
        for s in samples:
            m = s["scopes"].get(label, metric(Counter(), 0))
            cells.append(f"{m['duration_ms']/1000:.3f} / {m['core_cast_count']} / {fnum(m['core_cpm'],2)} / {m['cast_counts']['113656']} / {m['cast_counts']['101546']}")
        lines.append(f"| {title} | {' | '.join(cells)} |")
    lines += ["", "本次小怪pull总体核心CPM几乎相同（37.41与37.45），全程差距不能直接解释为沙僧平稳期一直按得慢。pull内实际增益段为44.31与40.91，无上述增益段为39.47与37.88；Boss、小怪及两种状态的结果须分别看。CPM只度量次数，不按伤害、通道长度或每次命中目标数加权，不代表哪段伤害更高。", "",
        "| 技能 | Bisset 全程数 / 全程CPM / pull内CPM | 沙僧 全程数 / 全程CPM / pull内CPM |", "| --- | ---: | ---: |"]
    for sid in NAMES:
        cells = []
        for s in samples:
            m, p = s["scopes"]["all"], s["scopes"]["recognized_pulls"]
            cells.append(f"{m['cast_counts'][str(sid)]} / {m['spell_cpm'][str(sid)]:.2f} / {p['spell_cpm'][str(sid)]:.2f}")
        lines.append(f"| {NAMES[sid]} {sid}{'（核心外）' if sid not in CORE else ''} | {' | '.join(cells)} |")
    lines += ["", "pull内怒雷CPM为5.79与5.71，神鹤为10.11与10.46；仅看全程怒雷165与132次会放大不同总时长及分包时间的影响。这些密度差异没有控制急速、通道占用、目标数量与团队拉法，不能据此直接算沙僧漏了多少 GCD 或损失多少伤害。", "", "## 每次白虎的固定30秒分析窗", "",
        "相对时间均以各自战斗起点为零；Δ白虎为两次真实施法间隔，不是冷却时长。天神列写白虎后秒数；距升龙为距之前最近一次升龙施法的秒数，星号表示该升龙不在本次30秒窗内。末窗若被战斗结束截断明确标注。", ""]
    for s in samples:
        gaps = s["white_interval_s"]
        lines += [f"### {s['name']} +{s['keystone_level']}", "", f"白虎{s['scopes']['all']['cast_counts']['123904']}次；相邻间隔中位数{gaps['median']:.3f}秒，范围{gaps['min']:.3f}–{gaps['max']:.3f}秒。", "",
            "| # | 白虎相对时间 | Δ白虎s | 锚点类型/pull | 窗长s | 乾元 | 怒雷 | 神鹤 | 天神：白虎后s / 距升龙s |", "| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |"]
        for w in s["white_windows"]:
            ctext = "; ".join(f"{c['since_white_s']:.3f} / {fnum(c['since_previous_wdp_s'])}{'*' if not c['previous_wdp_in_this_window'] else ''}" for c in w["conduits"]) or "无"
            counts = w["cast_counts"]
            lines.append(f"| {w['index']} | {clock(w['relative_s'])} | {fnum(w['previous_white_interval_s'])} | {w['anchor_pull_kind']}/{','.join(map(str,w['anchor_pull_ids']))} | {w['duration_ms']/1000:.3f}{' 截断' if w['clipped_at_fight_end'] else ''} | {counts['1249625']} | {counts['113656']} | {counts['101546']} | {ctext} |")
        outside = ", ".join(f"{clock(e['relative_s'])}[#{e['event_index']}]" for e in s["zenith_outside_30s"])
        lines += ["", f"乾元在固定30秒窗外还有{len(s['zenith_outside_30s'])}次：{outside or '无'}。因此同窗乾元次数不能替代完整爆发轮的一/二乾元判定。", ""]
    lines += ["## 三种青龙实际区间与怒雷起手", "",
        "下列持续时间来自成对apply/remove，时长范围只取闭合且无refresh的区间；完整区间和刷新索引见JSON。普通青龙被大青龙接替时可提前结束，不能把短区间都当自然时长。三种青龙独立列允许重叠；并集单列避免双计。", "",
        "| 样本 / 增益 | 区间数 | 无刷新闭合时长中位数s / 范围s | 合计存在s | 其内怒雷起手 |", "| --- | ---: | ---: | ---: | ---: |"]
    for s in samples:
        for sid, title in BLUE.items():
            b = s["blue_summary"][str(sid)]
            ds = b["closed_unrefreshed_duration_s"]
            lines.append(f"| {s['name']} / {title}{sid} | {b['interval_count']} | {ds['median']:.3f} / {ds['min']:.3f}–{ds['max']:.3f} | {b['duration_ms']/1000:.3f} | {b['fof_starts']} |")
        union = s["blue_summary"]["union"]
        lines.append(f"| {s['name']} / 任一青龙并集 | — | — | {union['duration_ms']/1000:.3f} | {union['fof_starts']} |")
    lines += ["", "实际记录的普通/大青龙通常约6秒、乾元青龙约4秒；本轮区间统计按实际apply/remove。现有 `gear-compat341-slice-current.json` / `gear-compat341-raid-current.json` 的有效buff统计同样为普通青龙平均5.902689/5.936036秒、大青龙6.0秒、乾元青龙4.0秒，与日志一致；8.0秒的是另一增益 `jade_sanctuary`。raw DBC的8秒字段不等于有效模型时长，不能据此声称模型与实服时长冲突。另一个比较限制是乾元自身持续不同：", ""]
    for s in samples:
        d = s["buff_duration_summary"]["1249625"]
        ds = d["closed_unrefreshed_duration_s"]
        lines.append(f"- {s['name']}：{d['interval_count']}个乾元区间，无刷新闭合段中位数{ds['median']:.3f}秒，范围{ds['min']:.3f}–{ds['max']:.3f}秒。")
        for span in s["buff_intervals"]["1249625"]:
            if span["refresh_indices"]:
                lines.append(f"- {s['name']}另有刷新合并的乾元区间{clock(span['start_relative_s'])}–{clock(span['end_relative_s'])}，共{span['duration_ms']/1000:.3f}秒；一次refresh不另算独立存在区间，cast次数仍独立计数。")
    lines += ["", "### 每个30秒分析窗的青龙时间覆盖与怒雷起手", "",
        "每格为“该buff覆盖秒数 / 该buff内怒雷起手数”；并集百分比=任一青龙覆盖时间÷该窗实际长度。百分比不是怒雷伤害覆盖率。", "",
        "| 样本# | 普通青龙 s/怒雷 | 乾元青龙 s/怒雷 | 大青龙 s/怒雷 | 任一青龙 s/占窗%/怒雷 |", "| --- | ---: | ---: | ---: | ---: |"]
    for s in samples:
        for w in s["white_windows"]:
            cells = [f"{w['blue'][str(sid)]['duration_ms']/1000:.3f}/{w['blue'][str(sid)]['fof_starts']}" for sid in BLUE]
            union = f"{w['any_blue_duration_ms']/1000:.3f}/{w['any_blue_duration_ms']/w['duration_ms']*100:.1f}%/{w['any_blue_fof_starts']}"
            lines.append(f"| {s['name']}#{w['index']} | {' | '.join(cells)} | {union} |")
    lines += ["", "## 天神施法时是否等到小青龙结束", "",
        "按实际天神cast时点检查普通443421及乾元青龙1238904，而不是只计算距升龙几秒。小青龙状态的“仍在”只表示cast在已记录apply/remove区间内；距观察到的remove有多久不是自然剩余冷却/自然持续时间，因大青龙可能提前替换。", ""]
    for s in samples:
        c = s["conduit_small_blue_summary"]
        overlaps = []
        for w in s["white_windows"]:
            for context in w["conduits"]:
                for sid, state in context["small_blue_state"].items():
                    if state["active_at_cast"]:
                        overlaps.append(f"白虎#{w['index']}天神{clock(context['cast']['relative_s'])}，{BLUE[int(sid)]}在观察到的{-state['cast_minus_observed_remove_ms']/1000:.3f}秒后移除")
        lines += [f"- {s['name']}：{c['casts']}次天神中，{c['both_small_inactive_at_cast']}次两种小青龙均不在，{c['small_active_at_cast']}次仍在；其中距记录移除超过50毫秒的有{c['small_active_and_observed_remove_more_than_50ms_later']}次。仍在的明细：{'；'.join(overlaps) or '无'}。"]
    lines += ["", "50毫秒只用于提示边界敏感性，不是判错阈值。尤其1毫秒/33毫秒等差值不足以推断玩家有意提前开天神；原始时间保留，不强行纠正。是否应等、等多久及伤害后果由主代理结合damage、资源和战斗轴综合。", "",
        "## 两处可复核序列差异（均为首轮小怪白虎）", "", "### 观察一：首旭日与首升龙之间的怒雷", ""]
    for s in samples:
        x = result["examples"]["opening_sun_to_wdp"][s["key"]]
        lines.append(f"- {s['name']}：{sequence_text(x['sequence'], s['white_windows'][0]['start_ms'])}。首旭日至首升龙之间有{x['fof_between_first_sun_and_first_wdp']}发怒雷。")
    lines += ["", "事实置信度高：两个序列顺序由cast直接确认。Bisset是首旭日后接升龙，沙僧在30.952秒打出怒雷，再于33.539秒升龙，已经存在不同分支响应，不能判为完全僵硬照搬。主代理另补充该次旭日为双暴；该暴击结论来自主代理的damage核验，本脚本没有独立读取damage，也不能说Bisset当时一定没刷新。后续可比较“怒雷可施放时先升龙还是直接怒雷”对青龙与后续冷却窗口顺序的影响，但沙僧30.952秒时升龙是否可用及资源是否允许仍未知，不能断定当时应该先升龙。验证动作：主代理对齐对应旭日主命中和晨晖暴击、目标数、后续逐跳伤害及升龙可用性，再解释分支收益。", "",
        "### 观察二：首天神与尚存小青龙的关系", ""]
    for s in samples:
        x = result["examples"]["opening_conduit_small_blue"][s["key"]]
        context = x["context"]
        blue = context["small_blue_state"]["443421"]
        span = blue["latest_interval"]
        lines.append(f"- {s['name']}：{sequence_text(x['sequence'], s['white_windows'][0]['start_ms'])}。普通青龙实际区间{clock(span['start_relative_s'])}–{clock(span['end_relative_s'])}，天神cast距该区间记录终点{blue['cast_minus_observed_remove_ms']/1000:+.3f}秒；下一大青龙在天神后{context['big_blue_apply_delay_s']:.3f}秒获得。")
    lines += ["", "事实置信度高：Bisset首天神在普通青龙结束后，沙僧首天神时普通青龙仍在。Bisset该普通青龙31.934–37.917秒内有33.930秒的一发怒雷起手；沙僧33.540–37.450秒内没有怒雷起手，前一发30.952秒在升龙之前。沙僧37.450秒同毫秒移除普通青龙并获得大青龙，是实际发生的提前替换；普通青龙仅3.910秒应与本轮通常约6秒的记录比较，不能用DBC8秒推算“丢了4.09秒”。这里仍不把短区间直接折算伤害损失，也不把两种不同刷新状态硬配成同一最优序列。下一把只训练“开天神前确认两种小青龙状态”，最终是否等待交由完整窗口收益和机制需要决定。", "",
        "## 拉怪元数据与可比性", "",
        "pull是WCL元数据分段，不是目标数时间线。Bisset首个小怪pull持续342.166秒，沙僧首个小怪pull72.628秒，说明同序号pull不能直接配对；Boss阶段也有不同战斗长度。以下保留各段，避免混用全程分母。", "",
        "| 样本 / pull | 类型 / 名称 | 起止相对时间 | 时长s | 怒雷 | 神鹤 | 核心CPM |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for s in samples:
        for p in s["pulls"]:
            lines.append(f"| {s['name']} / {p['id']} | {p['kind']} / {p['name']} | {clock(p['start_relative_s'])}–{clock(p['end_relative_s'])} | {p['duration_ms']/1000:.3f} | {p['cast_counts']['113656']} | {p['cast_counts']['101546']} | {fnum(p['core_cpm'],2)} |")
    lines += ["", "白虎前19秒禁升龙、8秒禁怒雷只是指南的轴策略，本报告不设这两类自动失误；距实际白虎施法多久也不等于当时白虎冷却。两人的白虎间隔差异、乾元段长差异和分包方式都不支持直接用固定常量判责。", "",
        "## 交接与边界", "",
        "主代理可优先对齐首轮两处观察的damage：旭日185099与晨晖392959各自是否暴击，怒雷117418的正常脉冲与套装额外伤害，以及三种青龙跨边界覆盖。cast/buff能证明怒雷何时起手、当时有什么增益；不能证明完整读条、完整命中、暴击触发了重置或当时资源足够。", "",
        "本分析不按cast间隔构造“怒雷CD已好”的假定，不推算未观察到的真气/能量，不按疑似通道中断计算损失。真实增益分段的无上述增益段也仍受其他增益影响，未控制嗜血、饰品及团队任务，不能给出净操作差距或伤害因果。JSON中的互斥时间与cast分区、青龙并集上界、所选buff配对检查均通过；未修改机制交接文件、输入数据或其他产物，未提交。", "",
        f"工具调用简报：生成于{result['generated_at']}；仅本地Python读取两组casts/buffs/metadata六份输入，校验完整性、身份与区间，写入指定JSON/Markdown。无网页、CDP或外部服务调用，无网络重试。",
    ]
    return "\n".join(lines) + "\n"


def main():
    result = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "method": {
            "white_analysis_window_ms": 30000, "intervals": "left-closed right-open",
            "core_spell_ids": sorted(CORE), "mechanism_or_excluded_ids": sorted(set(NAMES) - CORE),
            "actual_burst_buff_ids": sorted(STATE_IDS), "ready_only_buff_id": 1248992,
            "blue_coverage": "buff interval time and FoF cast starts; not damage/tick/channel coverage",
            "gcd_utilization_estimated": False, "event_indices": "zero-based original input events array",
        },
        "samples": [analyze_sample(config) for config in SAMPLES],
    }
    result["examples"] = make_examples(result["samples"])
    review = make_review(result)
    (ROOT / "cast-analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "cast-review.md").write_text(review, encoding="utf-8")
    print(json.dumps({s["key"]: {"core_casts": s["scopes"]["all"]["core_cast_count"], "fof": s["scopes"]["all"]["cast_counts"]["113656"], "sck": s["scopes"]["all"]["cast_counts"]["101546"], "checks": s["checks"]} for s in result["samples"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
