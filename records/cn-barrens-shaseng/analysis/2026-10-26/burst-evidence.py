"""Measure this two-log comparison without reconstructing unobserved cooldowns."""

import bisect
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AZURE = {443421, 443616, 1238904}
CORE = {113656, 101546, 100780, 100784, 107428, 467307, 152175, 443028, 443591}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


result = {"method": {
    "rsk_pairing": "Match primary185099 to automatic392959 on the same target instance within650ms; reject if another RSK/RWK cast intervenes. Crit uses hitType2. No cooldown-ready or resource state is inferred.",
    "fof_coverage": "Actual117418 damage amount carrying any of the three Azure buff IDs, including tier extra hits; not a count of full normal channels.",
    "pulse_groups": "Group damage within50ms under each preceding113656 cast. Tier extra hits at initial pulse are not additional normal pulses. Fewer than5 groups is a review candidate, not proven interruption.",
    "opening": "First75s of each log; not identical pulls or target distributions.",
}, "samples": {}}

for name, fight_id, source_id in (("elite", 28, 1), ("shaseng", 4, 2)):
    meta = load(f"wcl-{name}-metadata.json")
    fight = next(row for row in meta["fights"] if row["id"] == fight_id)
    start, end = fight["start_time"], fight["end_time"]
    casts = load(f"wcl-{name}-casts.json")
    damage = load(f"wcl-{name}-fof-damage.json")
    opening = load(f"wcl-{name}-opening-damage.json")
    main = load(f"wcl-{name}-damage-185099.json")
    dawn = load(f"wcl-{name}-damage-392959.json")
    for payload in (casts, damage, opening, main, dawn):
        assert payload["complete"] and not payload.get("nextPageTimestamp")
    actions = sorted((e for e in casts["events"] if e["type"] == "cast" and e["sourceID"] == source_id), key=lambda e: e["timestamp"])
    attacks = [e for e in actions if e["ability"]["guid"] in CORE]
    fof_casts = [e for e in actions if e["ability"]["guid"] == 113656]
    times = [e["timestamp"] for e in fof_casts]
    buckets = [[] for _ in fof_casts]
    for event in damage["events"]:
        assert event["sourceID"] == source_id and event["ability"]["guid"] == 117418
        idx = bisect.bisect_right(times, event["timestamp"]) - 1
        assert idx >= 0 and event["timestamp"] - times[idx] < 7000
        buckets[idx].append(event)
    channels = []
    for cast, hits in zip(fof_casts, buckets):
        groups = []
        for hit in hits:
            if not groups or hit["timestamp"] - groups[-1][0]["timestamp"] > 50:
                groups.append([])
            groups[-1].append(hit)
        amount = sum(e.get("amount", 0) for e in hits)
        covered = sum(e.get("amount", 0) for e in hits if AZURE & {int(v) for v in e.get("buffs", "").split(".") if v})
        channels.append({"time": round((cast["timestamp"] - start) / 1000, 3), "pulse_groups": len(groups),
                         "amount": amount, "azure_amount": covered,
                         "pulses": [{"time": round((g[0]["timestamp"] - start) / 1000, 3),
                                     "targets": len({(e.get("targetID"), e.get("targetInstance", 0)) for e in g}),
                                     "azure_rows": sum(bool(AZURE & {int(v) for v in e.get("buffs", "").split(".") if v}) for e in g),
                                     "rows": len(g)} for g in groups]})
    rsk = []
    for hit in main["events"]:
        assert hit["sourceID"] == source_id and hit["ability"]["guid"] == 185099
        paired = [e for e in dawn["events"] if e.get("sourceID") == source_id and
                  (e.get("targetID"), e.get("targetInstance", 0)) == (hit.get("targetID"), hit.get("targetInstance", 0)) and
                  0 <= e["timestamp"] - hit["timestamp"] <= 650 and
                  not any(hit["timestamp"] + 50 < a["timestamp"] < e["timestamp"] and a["ability"]["guid"] in (107428, 467307) for a in actions)]
        assert len(paired) <= 1
        next_actions = [e for e in attacks if e["timestamp"] > hit["timestamp"] + 50][:4]
        next_fof = next((e for e in fof_casts if e["timestamp"] > hit["timestamp"]), None)
        rsk.append({"time": round((hit["timestamp"] - start) / 1000, 3),
                    "main_crit": hit["hitType"] == 2, "dawn_present": bool(paired),
                    "dawn_crit": bool(paired and paired[0]["hitType"] == 2),
                    "crit_count": int(hit["hitType"] == 2) + sum(e["hitType"] == 2 for e in paired),
                    "next_fof_seconds": round((next_fof["timestamp"] - hit["timestamp"]) / 1000, 3) if next_fof else None,
                    "next_actions": [{"time": round((e["timestamp"] - start) / 1000, 3), "id": e["ability"]["guid"], "name": e["ability"]["name"]} for e in next_actions]})
    tier_consumptions = []
    for event in load(f"wcl-{name}-buffs.json")["events"]:
        if event.get("targetID") != source_id or event["ability"]["guid"] != 1297033 or event["type"] != "removebuff":
            continue
        candidates = [e for e in actions if e["ability"]["guid"] in (101546, 107428, 467307) and abs(e["timestamp"] - event["timestamp"]) <= 120]
        if len(candidates) != 1:
            tier_consumptions.append({"time": round((event["timestamp"] - start) / 1000, 3), "action": "unresolved", "pull_kind": "unknown"})
            continue
        action = candidates[0]
        pull = next((p for p in fight["dungeonPulls"] if p["start_time"] <= action["timestamp"] < p["end_time"]), None)
        tier_consumptions.append({"time": round((action["timestamp"] - start) / 1000, 3), "action": action["ability"]["name"],
                                  "id": action["ability"]["guid"], "pull_kind": "boss" if pull and pull["boss"] else "trash" if pull else "unclassified"})
    total = sum(c["amount"] for c in channels)
    azure = sum(c["azure_amount"] for c in channels)
    result["samples"][name] = {"fight": fight_id, "source": source_id, "duration": (end - start) / 1000,
                                "fof_casts": len(channels), "fof_damage": total, "fof_azure_damage": azure,
                                "fof_azure_damage_percent": azure / total * 100,
                                "pulse_group_distribution": dict(Counter(c["pulse_groups"] for c in channels)),
                                "fof_channels": channels, "rsk_crit_counts": dict(Counter(e["crit_count"] for e in rsk)), "rsk": rsk,
                                "opening_fof": [c for c in channels if c["time"] < 75],
                                "opening_rsk": [e for e in rsk if e["time"] < 75],
                                "tier_consumptions": tier_consumptions,
                                "tier_consumption_counts": dict(Counter(e["action"] for e in tier_consumptions)),
                                "opening_damage_scope": "Player damage and owned pets as returned; full first75s pagination verified; no whole-key damage share inferred from this window."}

(ROOT / "burst-evidence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for name, data in result["samples"].items():
    print(name, "FoF Azure damage%", round(data["fof_azure_damage_percent"], 2), "pulses", data["pulse_group_distribution"], "RSK", data["rsk_crit_counts"])
