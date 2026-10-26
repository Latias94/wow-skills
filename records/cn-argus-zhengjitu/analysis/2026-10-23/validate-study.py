"""Validate the dated report against supported simulations and exact inputs."""

import base64
import hashlib
import io
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
CHAR = ROOT.parents[1]
SLOTS = "head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand off_hand".split()
ALIASES = {"shoulder": "shoulders", "wrist": "wrists"}
TIER = {271481, 271482, 271483, 271484, 271486}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def options(text):
    return {line.split("=", 1)[0]: line.split("=", 1)[1] for line in text.splitlines()
            if "=" in line and not line.startswith(("#", "profileset."))}


def item_fields(encoded):
    return dict(part.split("=", 1) for part in encoded.split(",") if "=" in part)


def result(key):
    path = ROOT / f"{key}.json"
    assert path.stat().st_mtime >= (ROOT / f"{key}.simc").stat().st_mtime, f"Stale result: {key}"
    payload = read_json(path)
    sim = payload["sim"]
    assert sim["players"][0]["valid_fight_style"] is True, f"Unsupported workload: {key}"
    assert not payload.get("errors") and not sim.get("errors"), key
    assert "Severe:" not in (ROOT / f"{key}.run.log").read_text(encoding="utf-8-sig"), key
    return sim


page = (ROOT / "dashboard.html").read_text(encoding="utf-8")
match = re.search(r'<script id="report-data" type="application/json">(.*?)</script>', page, re.S)
assert match
data = json.loads(match[1])
summary = read_json(ROOT / "study-summary.json")
manifest = read_json(ROOT / "study-manifest.json")
assert data["runs"] == summary["runs"]
assert data["profiles"] == summary["profiles"]
assert data["conclusions"] == summary["conclusions"]
assert data["limitations"] == summary["limitations"]
assert len(data["runs"]) == 29
assert data["meta"]["budget"] is None
assert "H10本周已R" in data["meta"]["budget_note"]
assert data["elite_samples"]["mythic_plus"]["logs"] == 800
assert data["elite_samples"]["mythic_plus"]["characters"] == 160
assert data["elite_samples"]["raid"]["logs"] == 900
assert data["elite_samples"]["raid"]["characters"] == 473
assert len(data["current"]["gear"]) == 15
snapshot_bytes = (CHAR / "snapshots/2026-10-23.simc").read_bytes()
assert snapshot_bytes == Path("C:/Users/Administrator/Downloads/正极兔simc.txt").read_bytes()
profile_record = read_json(CHAR / "profile.json")
assert hashlib.sha256(snapshot_bytes).hexdigest() == profile_record["snapshot_sha256"]
assert data["current"]["raw"] == (CHAR / "snapshots/2026-10-23.simc").read_text(encoding="utf-8-sig")
assert 271092 in data["current"]["owned_item_ids"]
assert 251150 in data["current"]["owned_item_ids"]
assert 281238 in data["current"]["owned_item_ids"]

for mode in ("raid", "dungeon"):
    profile = data["profiles"][mode]
    text = (ROOT / f"recommended-{mode}.simc").read_text(encoding="utf-8")
    assert profile["raw"] == text
    assert "profileset." not in text
    expected_text = (ROOT / f"{profile['selected_from']}.simc").read_text(encoding="utf-8")
    expected = options(expected_text)
    if profile["selected"] != "Baseline":
        prefix = f'profileset."{profile["selected"]}"'
        changes = [line.split("=", 1)[1] for line in expected_text.splitlines()
                   if line.startswith(prefix + "=") or line.startswith(prefix + "+=")]
        assert changes, (mode, profile["selected"])
        for line in changes:
            key, value = line.split("=", 1)
            expected[key] = value
    actual_input = options(text)
    for key in SLOTS + ["race", "talents", "flask", "food", "potion", "augmentation", "temporary_enchant", "fight_style", "desired_targets", "max_time", "optimal_raid", "override.bloodlust"]:
        assert actual_input.get(key) == expected.get(key), (mode, key)
    measured = result(f"recommended-{mode}")["players"][0]
    unbuffed = result(f"unbuffed-{mode}")["players"][0]
    assert len(profile["gear"]) == 16
    assert len([row for row in profile["gear"] if row["id"] in TIER]) >= 4
    assert item_fields(measured["gear"]["main_hand"]["encoded_item"])["id"] == "271092"
    assert "off_hand" in measured["gear"]
    embellishments = []
    for row in profile["gear"]:
        slot = ALIASES.get(row["slot"], row["slot"])
        actual = measured["gear"][slot]
        encoded = item_fields(actual["encoded_item"])
        wanted = item_fields(actual_input[row["slot"]])
        assert int(encoded["id"]) == row["id"]
        assert actual["ilevel"] == row["ilevel"]
        assert unbuffed["gear"][slot]["encoded_item"] == actual["encoded_item"]
        for key in ("id", "gem_id", "enchant_id", "crafted_stats", "redirected_base_stats", "content_tuning"):
            assert wanted.get(key) == encoded.get(key), (mode, slot, key)
        assert sorted(wanted.get("bonus_id", "").split("/")) == sorted(encoded.get("bonus_id", "").split("/")), (mode, slot, "bonus_id")
        embellishments += [bonus for bonus in wanted.get("bonus_id", "").split("/") if bonus in ("12384", "13771")]
        assert data["items"][str(row["id"])]["name"]
        if row["slot"] in ("wrist", "waist"):
            assert not row.get("gem_id"), (mode, "invented socket", slot)
    assert len(embellishments) == 2, mode
    for key in ("flask", "food", "potion", "augmentation", "temporary_enchant"):
        assert profile["consumables"][key] == measured[key]
        assert unbuffed[key] in ("", "disabled"), (mode, "unbuffed", key)
    assert profile["stats"] == {key: unbuffed["collected_data"]["buffed_stats"]["stats"][key] for key in profile["stats"]}
    upgrade = result(f"upgrade-target-{mode}")["players"][0]
    assert upgrade["flask"] == measured["flask"]
    buffs = {buff["name"]: buff for buff in measured["buffs"]}
    for name in ("arcanoweave_insight", "soul_fang_alacrity", "venomcursed_ascendance", "devastating_power", "overcharge_tier"):
        assert buffs[name]["uptime"] > 0, (mode, name)

for run in data["runs"]:
    sim = result(run["key"])
    assert run["baseline"] == sim["players"][0]["collected_data"]["dps"]["mean"]
    assert run["stderr"] == sim["players"][0]["collected_data"]["dps"]["mean_std_dev"]
    assert run["iterations"] == sim["options"]["iterations"]
    assert run["model"] == "Patchwerk"
    assert run["targets"] == sim["options"]["desired_targets"]
    expected_rows = {row["name"]: row for row in sim.get("profilesets", {}).get("results", [])}
    assert len(run["results"]) == len(expected_rows)
    for row in run["results"]:
        assert row["mean"] == expected_rows[row["name"]]["mean"]
        assert row["error"] == expected_rows[row["name"]]["mean_error"]
        if run["mode"] == "dungeon" or run["stage"].startswith("upgrade"):
            assert row["provisional"] is True

for value in data["items"].values():
    assert value["name"] and value["icon"].startswith("data:image/jpeg;base64,")
    image = Image.open(io.BytesIO(base64.b64decode(value["icon"].split(",", 1)[1], validate=True)))
    image.verify()
for source in data["sources"]:
    if not source["url"].startswith("https://"):
        assert (ROOT / source["url"]).is_file(), source["url"]
week = read_json(CHAR / "weeks/2026-10-22.json")
assert week["budget"]["reported_balance"] == 2 and week["resources"]["venomstones"] == 7
assert week["rules"]["remaining_pool_verified"] is False
historical = [event for event in week["events"] if event["event_id"] == "confirmed-h3-bag270164-history-2026-10-23"]
assert len(historical) == 1 and historical[0]["item_id"] == 270164 and historical[0]["status"] == "confirmed"
assert historical[0]["budget_effect_now"] == 0
h10_events = [event for event in week["events"] if event["event_id"] == "confirmed-h10-current-week-roll-2026-10-23"]
assert len(h10_events) == 1 and h10_events[0]["status"] == "confirmed"
assert h10_events[0]["outcome"] == "unknown" and h10_events[0]["item_id"] is None
assert h10_events[0]["budget_effect_now"] is None
assert week["budget"]["current_balance"] is None
assert week["plan"]["coins_reserved"] is None
allocations = {entry["activity"]: entry for entry in week["plan"]["conditional_allocation"]}
assert allocations["H10 / Kithix"]["status"] == "deferred_to_next_reset"
assert allocations["H10 / Kithix"]["earliest_reset_date"] == "2026-10-29"
assert allocations["H3 / The Lost Explorers"]["alternative_target_item_ids"] == [270924]
scenario = week["plan"]["h3_probability_scenario"]
assert scenario["status"].startswith("conditional_")
assert set(scenario["useful_target_item_ids"]) <= set(scenario["hypothetical_remaining_item_ids"])
assert len(scenario["useful_target_item_ids"]) / len(scenario["hypothetical_remaining_item_ids"]) == scenario["useful_target_fraction_if_exact_and_equal_weight"] == 0.5
pools = read_json(ROOT / "followup-pools.json")
assert pools["current_balance"] is None and pools["rules"]["probability"]["numeric_probability"] is None
assert pools["confirmed_history"]["H10"]["current_week_roll_confirmed"]
assert pools["confirmed_history"]["H10"]["confirmed_exclusions"] is None
assert pools["pools"]["H10"]["current_week_eligibility"].startswith("unavailable")
assert data["routes"] == summary["routes"]
h3_route = next(route for route in data["routes"] if route["boss"].startswith("H3／"))
h10_route = next(route for route in data["routes"] if route["boss"].startswith("H10／"))
assert 271481 in h3_route["targets"] and h3_route["excluded"] == [270164]
assert "本周剩余首选" in h3_route["priority"] and "不是已核实概率" in h3_route["note"]
assert "本周不可再安排" in h10_route["priority"] and h10_route["excluded"] == []
ring_route = next(route for route in data["routes"] if route["targets"] == [268252])
ring_plan = week["plan"]["secondary_ring_candidate"]
assert "条件次选" in ring_route["priority"] and ring_route["excluded"] == []
assert ring_plan["item_id"] == 268252 and ring_plan["replaces_item_id"] == 268249 and ring_plan["retain_item_id"] == 281029
assert ring_plan["planned_spend"] is None and ring_plan["status"] == "conditional_alternative_not_allocated"
ring_source = read_json(ROOT / "ring-roll-source.json")
assert ring_source["npc_id"] == 257347 and ring_source["R_pool_completeness"] == "unknown"
assert any(row["id"] == 268252 for row in ring_source["ordinary_drops"])
assert week["plan"]["venomstones_to_spend_now"] == 0
assert week["plan"]["status"] == "proposed"
assert profile_record["roll_history_coverage"] == "partial"
assert read_json(ROOT / "rejected-dungeonslice/rejection.json")["status"] == "rejected"
stats = read_json(ROOT / "stats-comparison.json")
for character in stats["characters"].values():
    for mode, current in character["current"].items():
        actual = read_json(ROOT.parents[3] / current["source"])["sim"]["players"][0]
        assert actual["valid_fight_style"]
        assert all(actual[key] == "disabled" for key in ("flask", "food", "potion", "augmentation", "temporary_enchant"))
        measured_stats = actual["collected_data"]["buffed_stats"]["stats"]
        for key, value in current["ratings"].items():
            assert measured_stats[key + "_rating"] == value
            assert abs(measured_stats[key + "_pct"] * 100 - current["percentages"][key]) < 1e-9
assert "valid_fight_style=false" in " ".join(source["note"] for source in data["sources"])
assert "334→340" not in page and "331→338" not in page
print(f"PASS: {len(data['runs'])} supported batches, 2 exact downloads, full gear modifiers, intact snapshot, resources, icons and evidence")
