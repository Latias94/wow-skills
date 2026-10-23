"""Check that the dated HTML, downloads and measured artifacts agree."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
embedded = re.search(r'<script id="report-data" type="application/json">(.*?)</script>', html, re.S)
data = json.loads(embedded[1])
summary = json.loads((ROOT / "study-summary.json").read_text(encoding="utf-8"))
assert data["runs"] == summary["runs"]
assert data["meta"]["budget"] == 0
assert data["elite_samples"]["mythic_plus"]["logs"] == 796
assert data["elite_samples"]["raid"]["logs"] == 896
assert len(data["current"]["gear"]) == 15

for mode in ("raid", "dungeon"):
    profile = data["profiles"][mode]
    assert profile["raw"] == (ROOT / f"recommended-{mode}.simc").read_text(encoding="utf-8")
    verified_lines = (ROOT / f"verify-{mode}.simc").read_text(encoding="utf-8").splitlines()
    expected_lines = [line for line in verified_lines if not line.startswith("profileset.")]
    if profile["selected"] != "Baseline":
        prefix = f'profileset."{profile["selected"]}"'
        for line in verified_lines:
            if line.startswith(prefix + "=") or line.startswith(prefix + "+="):
                change = re.sub(r'^profileset\."[^"]+"\+?=', "", line)
                key = change.split("=", 1)[0]
                expected_lines = [entry for entry in expected_lines if entry.split("=", 1)[0] != key]
                expected_lines.append(change)
    assert profile["raw"].splitlines() == expected_lines
    measured = json.loads((ROOT / f"recommended-{mode}.json").read_text(encoding="utf-8"))["sim"]["players"][0]
    unbuffed = json.loads((ROOT / f"unbuffed-{mode}.json").read_text(encoding="utf-8"))["sim"]["players"][0]
    assert len(profile["gear"]) == 15
    input_gear = {line.split("=", 1)[0]: dict(part.split("=", 1) for part in line.split("=", 1)[1].split(",") if "=" in part)
                  for line in profile["raw"].splitlines() if line.split("=", 1)[0] in [g["slot"] for g in profile["gear"]]}
    for gear in profile["gear"]:
        slot = {"shoulder": "shoulders", "wrist": "wrists"}.get(gear["slot"], gear["slot"])
        actual = measured["gear"][slot]
        assert gear["ilevel"] == actual["ilevel"]
        assert f"id={gear['id']}," in actual["encoded_item"]
        assert data["items"][str(gear["id"])]["name"]
        assert unbuffed["gear"][slot]["encoded_item"] == actual["encoded_item"]
        fields = dict(part.split("=", 1) for part in actual["encoded_item"].split(",") if "=" in part)
        for key in ("gem_id", "enchant_id", "crafted_stats", "redirected_base_stats", "content_tuning"):
            assert input_gear[gear["slot"]].get(key) == fields.get(key), (mode, slot, key)
        assert sorted(input_gear[gear["slot"]].get("bonus_id", "").split("/")) == sorted(fields.get("bonus_id", "").split("/"))
    assert unbuffed["flask"] in ("", "disabled")
    assert unbuffed["food"] in ("", "disabled")

for run in data["runs"]:
    assert (ROOT / f"{run['key']}.json").stat().st_mtime >= (ROOT / f"{run['key']}.simc").stat().st_mtime, f"Stale simulation: {run['key']}"
    measured = json.loads((ROOT / f"{run['key']}.json").read_text(encoding="utf-8"))["sim"]
    assert run["baseline"] == measured["players"][0]["collected_data"]["dps"]["mean"]
    expected = {row["name"]: row for row in measured.get("profilesets", {}).get("results", [])}
    assert len(run["results"]) == len(expected)
    for row in run["results"]:
        assert row["mean"] == expected[row["name"]]["mean"]
        assert row["error"] == expected[row["name"]]["mean_error"]
        if run["mode"] == "dungeon" and run["stage"] in ("targets", "verify"):
            assert row["provisional"] is True

for source in data["sources"]:
    if not source["url"].startswith("https://"):
        assert (ROOT / source["url"]).is_file(), source["url"]
for row in data["elite_samples"]["items"]:
    assert data["items"][str(row["id"])]["name"]
assert "升至338" not in html
assert "334→340" not in html
assert "331→338" not in html
assert not re.search(r",slot=", "\n".join(p.read_text(encoding="utf-8") for p in ROOT.glob("*.simc")))
print(f"PASS: {len(data['runs'])} measured runs, 2 exact downloads, 30 target slots, local evidence and hotfix wording")
