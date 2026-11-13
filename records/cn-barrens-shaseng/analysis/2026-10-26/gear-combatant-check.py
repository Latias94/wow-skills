"""Compare saved combatantinfo equipment with the dated website exports."""

from datetime import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
result = {"checked_at": datetime.now().astimezone().isoformat(), "characters": {},
          "stat_interpretation": "Raw combatantinfo start-state fields retain actual talents, consumables and party auras. Do not compare directly with unbuffed SimC snapshots or attribute differences solely to equipment."}
for key, prefix in (("user", "shaseng"), ("elite", "elite")):
    profile = {}
    for line in (HERE / f"wcl-{prefix}-profile.simc").read_text(encoding="utf-8-sig").splitlines():
        if ",id=" in line and not line.startswith("#"):
            slot, value = line.split("=", 1)
            profile[slot] = dict(part.split("=", 1) for part in value.split(",") if "=" in part)
    source = HERE / f"wcl-{prefix}-combatant.json"
    document = json.loads(source.read_text(encoding="utf-8"))
    event = document["events"][0]
    assert event["type"] == "combatantinfo"
    by_id = {item["id"]: item for item in event["gear"] if item["id"]}
    rows = []
    for slot, item in profile.items():
        fight_item = by_id.get(int(item["id"]))
        expected_level = 341 if "12856" in item.get("bonus_id", "").split("/") else None
        # Other current levels were already read from the character page and full-bonus item lookup.
        if expected_level is None:
            lookup = json.loads((HERE / ("gear-items.json" if key == "user" else "gear-elite-items.json")).read_text(encoding="utf-8"))
            expected_level = next(row["item_level"] for row in lookup["items"] if row["slot"] == slot)
        rows.append({"slot": slot, "current_item_id": int(item["id"]), "fight_item_id": fight_item["id"] if fight_item else None,
                     "current_wcl_level": expected_level, "fight_level": fight_item["itemLevel"] if fight_item else None,
                     "id_equal": fight_item is not None,
                     "level_equal": fight_item is not None and fight_item["itemLevel"] == expected_level,
                     "bonus_equal": fight_item is not None and set(fight_item.get("bonusIDs", [])) == set(map(int, item.get("bonus_id", "").split("/"))),
                     "gems_equal": fight_item is not None and [gem["id"] for gem in fight_item.get("gems", [])] == list(map(int, item["gem_id"].split("/"))) if item.get("gem_id") else not fight_item.get("gems", []),
                     "permanent_enchant_equal": fight_item is not None and fight_item.get("permanentEnchant", 0) == int(item.get("enchant_id", 0)),
                     "fight_temporary_enchant": fight_item.get("temporaryEnchant") if fight_item else None,
                     "fight_bonus_ids": fight_item.get("bonusIDs", []) if fight_item else []})
    assert len(rows) == 15 and all(row["id_equal"] for row in rows)
    stats = {field: event.get(field) for field in ("agility", "strength", "stamina", "intellect", "critMelee", "hasteMelee", "mastery", "versatilityDamageDone", "versatilityHealingDone", "versatilityDamageReduction")}
    total_level = sum(row["fight_level"] for row in rows) + next(row["fight_level"] for row in rows if row["slot"] == "main_hand")
    differences = [row for row in rows if not all(row[field] for field in ("id_equal", "level_equal", "bonus_equal", "gems_equal", "permanent_enchant_equal"))]
    result["characters"][key] = {
        "source": source.name, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_url": document.get("url"), "scope": document.get("scope"),
        "fight": event["fight"], "sourceID": event["sourceID"], "event_timestamp": event["timestamp"],
        "all_15_item_ids_equal": True, "gear_equal_on_exported_fields": not differences,
        "comparison_fields": ["item_id", "item_level", "bonus_ids", "gems", "permanent_enchant"],
        "temporary_enchant_caveat": "Temporary enchants are not present in the website SimC exports; a recorded fight oil is an additional observation, not proof of a changed permanent loadout.",
        "fight_equipped_average": total_level / 16, "differences": differences, "slots": rows,
        "raw_start_stats": stats, "start_auras": event.get("auras", []),
        "highest_raw_secondary_field": max(("critMelee", "hasteMelee", "mastery", "versatilityDamageDone"), key=lambda field: event[field]),
        "talent_tree_nodes": event.get("talentTree", []),
        "talent_policy": "Nodes preserved as fight evidence only. No talent decoding or change to the controlled simulation talents.",
    }
result["conclusion"] = "Bisset fight 28 matches all 15 current website items, levels, bonuses, gems and permanent enchants. Shaseng fight 4 retains the same 15 item IDs but its neck is 334 with bonus 12854, while the current page/export neck is 341 with bonus 12856; other compared permanent gear fields match. Both fights directly record other ascended items at 341."
(HERE / "gear-combatant-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: {field: value[field] for field in ("fight", "gear_equal_on_exported_fields", "fight_equipped_average", "differences", "raw_start_stats")}
                  for key, value in result["characters"].items()}, ensure_ascii=False, indent=2))
