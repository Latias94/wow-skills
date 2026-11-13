"""Summarize the completed, validated gear runs and retain their provenance."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def static_stats(document):
    actor = document["sim"]["players"][0]
    snapshot = actor["collected_data"]["buffed_stats"]
    return {"race": actor["race"], "agility": snapshot["attribute"]["agility"],
            "ratings": {s: snapshot["stats"][s + "_rating"] for s in ("crit", "haste", "mastery", "versatility")},
            "percentages": {s: snapshot["stats"][s + "_pct"] * 100 for s in ("crit", "haste", "mastery", "versatility")},
            "consumables": {s: actor[s] for s in ("flask", "food", "augmentation", "potion", "temporary_enchant")},
            "external_raid_buffs": document["sim"].get("overrides", {}),
            "note": "Precombat model snapshot including retained talents, gear, enchants and passive effects; not a live client panel measurement."}


def potion_triggers(actor):
    positive = [b for b in actor["buffs"] if b["name"].startswith("potion_of_recklessness_") and "penalty" not in b["name"]]
    negative = [b for b in actor["buffs"] if b["name"].startswith("potion_of_recklessness_penalty_")]
    total = sum(b["start_count"] for b in positive)
    return {"positive_triggers_per_fight": total,
            "positive_trigger_share_pct": {b["name"].removeprefix("potion_of_recklessness_"): 100 * b["start_count"] / total for b in positive} if total else {},
            "penalty_triggers_per_fight": {b["name"].removeprefix("potion_of_recklessness_penalty_"): b["start_count"] for b in negative}}


manifest = read("gear-manifest.json")
compat_manifest = read("gear-compat341-manifest.json")
combatant_check = read("gear-combatant-check.json")
talent_manifest = read("gear-talent-manifest.json")
snapshot = ROOT / manifest["snapshot"]
assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == manifest["snapshot_sha256"]
actor_fields = dict(s.split("=", 1) for s in snapshot.read_text(encoding="utf-8-sig").splitlines()
                    if s and not s.startswith("#") and "=" in s)
runs = {}
for path in sorted(HERE.glob("gear-*.json")):
    doc = json.loads(path.read_text(encoding="utf-8"))
    if "sim" not in doc:
        continue
    actor = doc["sim"]["players"][0]
    options = doc["sim"]["options"]
    text = (HERE / f"{path.stem}.run.log").read_text(encoding="utf-8") + (HERE / f"{path.stem}.txt").read_text(encoding="utf-8")
    severe = [row for row in doc.get("logs", []) if "severe" in row.get("level", "").lower()]
    accepted = all(a.get("valid_fight_style") is True for a in doc["sim"]["players"]) and not severe and not re.search(r"\bsevere\b", text, re.I)
    assert accepted, path.name
    is_talent_control = path.stem.startswith("gear-talents-")
    expected_talents = talent_manifest["runs"][path.stem]["talents"] if is_talent_control else actor_fields["talents"]
    assert actor["race"] == "pandaren" and actor["talents"] == expected_talents, path.name
    assert doc["git_revision"] == "73a372b761" and actor["dbc"]["version_used"] == "Live", path.name
    tier_ids = {271517, 271518, 271519, 271520, 271522}
    decoded = []
    for item in actor["gear"].values():
        encoded = dict(part.split("=", 1) for part in item["encoded_item"].split(",") if "=" in part)
        decoded.append(encoded)
    tier_count = sum(int(item["id"]) in tier_ids for item in decoded)
    embellishments = sum("12384" in item.get("bonus_id", "").split("/") for item in decoded)
    assert tier_count >= 4 and embellishments == 2, path.name
    is_compat = path.stem.startswith("gear-compat341-") or is_talent_control
    overridden = [item for item in decoded if "ilevel" in item]
    if is_compat:
        compat_name = talent_manifest["runs"][path.stem]["source"].removesuffix(".simc") if is_talent_control else path.stem
        expected = compat_manifest["runs"][compat_name]["overrides"]
        assert len(overridden) == len(expected), path.name
        assert all(item["ilevel"] == "341" and "12856" in item["bonus_id"].split("/") for item in overridden), path.name
        for slot, source in expected.items():
            item = actor["gear"][slot]
            encoded = dict(part.split("=", 1) for part in item["encoded_item"].split(",") if "=" in part)
            assert item["ilevel"] == 341 and int(encoded["id"]) == source["item_id"], path.name
            assert set(encoded["bonus_id"].split("/")) == set(source["bonus_id"].split("/")), path.name
    else:
        assert not overridden, path.name
    validation_path = HERE / f"{path.stem}.validation.json"
    if validation_path.exists():
        validation = read(validation_path.name)
        assert validation["accepted"] and validation["exit_code"] == 0, path.name
    dps = actor["collected_data"]["dps"]
    # Ratings come from the precombat snapshot; transient potion selections come from buff starts.
    runs[path.stem] = {
        "accepted": True, "valid_fight_style": actor["valid_fight_style"], "severe_count": 0,
        "tier_count": tier_count, "embellishment_count": embellishments, "item_level_override": bool(overridden),
        "data_model": "wcl341_explicit_compatibility" if is_compat else "original_bonus_old_dbc",
        "comparison_kind": "talent_string_control" if is_talent_control else "gear_or_smoke",
        "talents_equal_user": actor["talents"] == actor_fields["talents"],
        "input": f"{path.stem}.simc", "result": path.name, "text": f"{path.stem}.txt", "log": f"{path.stem}.run.log",
        "dps": dps["mean"], "standard_error": dps["mean_std_dev"],
        "ci95_half_width": dps["mean_std_dev"] * options["confidence_estimator"],
        "sample_count": dps["count"], "reported_option_iterations": options["iterations"],
        "seed": options["seed"], "fight_style": options["fight_style"], "max_time": options["max_time"],
        "desired_targets": options["desired_targets"], "optimal_raid": options["optimal_raid"],
        "effective_overrides": doc["sim"].get("overrides", {}), "warnings": doc.get("logs", []),
        "potion_triggers": potion_triggers(actor),
        "zenith": {"actions": [{"name": stat["name"], "num_executes": stat.get("num_executes")} for stat in actor["stats"] if stat["name"] == "zenith"],
                   "buffs": [{field: buff.get(field) for field in ("name", "start_count", "refresh_count", "duration", "uptime")}
                             for buff in actor["buffs"] if buff["name"] == "zenith"]},
        "modeled_item_effects": [{"name": s["name"], "item_id": s.get("item_id"), "spell_id": s.get("id"),
                                  "dps": s["portion_aps"]["mean"]} for s in actor["stats"]
                                 if s.get("item_id") or s["name"] in ("void_eruption", "acidbrood_scourge")],
    }

screening, verification = {}, {}
for stage, target in (("screen", screening), ("verify", verification)):
    for mode in ("slice", "raid"):
        base_key = f"gear-{stage}-{mode}-current"
        baseline = runs[base_key]["dps"]
        rows = []
        for key, candidate in manifest["candidates"].items():
            name = f"gear-{stage}-{mode}-{key}"
            if name not in runs:
                continue
            r = runs[name]
            rows.append({"candidate": key, "label": candidate["label"], "dps": r["dps"],
                         "delta_pct": 100 * (r["dps"] / baseline - 1),
                         "ci95_half_width": r["ci95_half_width"], "sample_count": r["sample_count"], "run": name})
        target[mode] = {"baseline": base_key, "rows": rows}

user_items = read("gear-items.json")
elite_items = read("gear-elite-items.json")
user_by_slot = {i["slot"]: i for i in user_items["items"]}
elite_by_slot = {i["slot"]: i for i in elite_items["items"]}
slot_comparison = [{"slot": slot, "user": user_by_slot[slot], "elite": elite_by_slot[slot],
                    "user_wcl_item_level": 341 if "12856" in user_by_slot[slot]["bonus_ids"].split("/") else user_by_slot[slot]["item_level"],
                    "elite_wcl_item_level": 341 if "12856" in elite_by_slot[slot]["bonus_ids"].split("/") else elite_by_slot[slot]["item_level"]}
                   for slot in user_by_slot]
elite_comparison = {}
for mode in ("slice", "raid"):
    elite = runs[f"gear-screen-{mode}-elite_full"]
    literal = runs[f"gear-screen-literal-{mode}-current"]
    recovered = runs[f"gear-screen-{mode}-current"]
    elite_comparison[mode] = {"elite_dps": elite["dps"], "elite_ci95_half_width": elite["ci95_half_width"],
                              "user_literal_dps": literal["dps"], "user_literal_ci95_half_width": literal["ci95_half_width"],
                              "delta_vs_literal_pct": 100 * (elite["dps"] / literal["dps"] - 1),
                              "delta_vs_recovered_pct": 100 * (elite["dps"] / recovered["dps"] - 1),
                              "interpretation": "Original-bonus old-DBC gear counterfactual only; not current live item-level evidence, combat-equipment evidence or skill attribution."}

compat_comparisons = {}
for mode in ("slice", "raid"):
    baseline = runs[f"gear-compat341-{mode}-current"]
    rows = []
    for key in ("current", "waist_331_cm", "raid_ring_334"):
        name = f"gear-compat341-{mode}-{key}"
        r = runs[name]
        rows.append({"candidate": key, "dps": r["dps"], "delta_pct": 100 * (r["dps"] / baseline["dps"] - 1),
                     "ci95_half_width": r["ci95_half_width"], "sample_count": r["sample_count"], "run": name,
                     "metadata_family": "historical_precursor_continuity"})
    elite = runs[f"gear-compat341-{mode}-elite_full"]
    literal = runs[f"gear-compat341-{mode}-literal-current"]
    compat_comparisons[mode] = {
        "actions": {"baseline": f"gear-compat341-{mode}-current", "rows": rows},
        "elite_comparison": {"baseline": f"gear-compat341-{mode}-literal-current", "elite_run": f"gear-compat341-{mode}-elite_full",
                             "user_dps": literal["dps"], "user_ci95_half_width": literal["ci95_half_width"],
                             "elite_dps": elite["dps"], "elite_ci95_half_width": elite["ci95_half_width"],
                             "delta_pct": 100 * (elite["dps"] / literal["dps"] - 1),
                             "metadata_family": "literal_export_for_both", "mixed_precursor_baselines": False},
    }

talent_comparisons = {}
for mode in ("slice", "raid"):
    user = runs[f"gear-talents-{mode}-user"]
    elite = runs[f"gear-talents-{mode}-bisset"]
    talent_comparisons[mode] = {
        "user_run": f"gear-talents-{mode}-user", "bisset_run": f"gear-talents-{mode}-bisset",
        "user_dps": user["dps"], "user_ci95_half_width": user["ci95_half_width"],
        "bisset_talents_dps": elite["dps"], "bisset_talents_ci95_half_width": elite["ci95_half_width"],
        "delta_pct": 100 * (elite["dps"] / user["dps"] - 1), "user_zenith": user["zenith"], "bisset_zenith": elite["zenith"],
        "fixed_user_gear_and_race": True, "recommendation_to_switch": False,
    }

jade_runtime_buffs = {}
for mode in ("slice", "raid"):
    filename = f"gear-compat341-{mode}-current.json"
    actor = read(filename)["sim"]["players"][0]
    jade_runtime_buffs[mode] = {
        "source": filename,
        "buffs": {buff["name"]: {field: buff.get(field) for field in ("spell", "duration", "start_count", "refresh_count", "uptime")}
                  for buff in actor["buffs"] + actor.get("buffs_constant", [])
                  if buff["name"] in ("heart_of_the_jade_serpent", "heart_of_the_jade_serpent_unity_within",
                                      "heart_of_the_jade_serpent_yulons_avatar", "jade_sanctuary")},
    }

summary = {
    "schema_version": 2, "generated_at": datetime.now().astimezone().isoformat(),
    "character": "CN/Barrens/沙僧", "elite_reference": manifest["elite_reference"],
    "manifest": "gear-manifest.json", "source_evidence": "gear-source-evidence.json",
    "item_level_conflict_evidence": "gear-level-evidence.json",
    "fight_equipment_check": {"evidence": "gear-combatant-check.json", "conclusion": combatant_check["conclusion"],
                              "stat_interpretation": combatant_check["stat_interpretation"],
                              "characters": {key: {field: character[field] for field in
                                             ("source", "fight", "all_15_item_ids_equal", "gear_equal_on_exported_fields",
                                              "fight_equipped_average", "differences", "raw_start_stats", "start_auras", "highest_raw_secondary_field")}
                                             for key, character in combatant_check["characters"].items()}},
    "engine": {"path": manifest["engine"], "sha256": manifest["engine_sha256"],
               "source_commit": manifest["source_commit"], "version": read("gear-unbuffed.json")["version"],
               "data": read("gear-unbuffed.json")["sim"]["players"][0]["dbc"],
               "modified": False},
    "scope": {"candidate_count_including_current": len(manifest["candidates"]),
              "initial_candidates_including_current": 6, "added_after_elite_arrived": ["elite_full", "raid_ring_334"],
              "screen_requested_iterations": 3500, "verification_requested_iterations": 6000,
              "single_target": "Patchwerk 240s, one target, optimal_raid=1, Bloodlust enabled",
              "dungeon": "DungeonSlice 360s, valid for this Windwalker actor, optimal_raid=0, Bloodlust disabled; synthetic, not a measured route",
              "auxiliary_only": "Patchwerk fixed five targets 90s smoke; not used as final ranking evidence",
              "consumables": {"flask": "flask_of_the_magisters_2", "food": "harandar_celebration", "augmentation": "void_touched",
                              "potion": "potion_of_recklessness_2", "temporary_enchant": "main_hand:thalassian_phoenix_oil_2"},
              "excluded": manifest["excluded_historical_fields"]},
    "metadata_uncertainty": manifest["historical_metadata_recovery"],
    "current_stats": {"model": "Explicit ilevel=341 compatibility model sourced from WCL display; not a live client panel measurement or updated DBC evidence.",
                      "literal_oct26_export": static_stats(read("gear-compat341-unbuffed-literal-current.json")),
                      "historical_precursor_continuity_model": static_stats(read("gear-compat341-unbuffed-current.json")),
                      "elite_gear_under_user_race_talents": static_stats(read("gear-compat341-unbuffed-elite_full.json")),
                      "highest_static_secondary_in_all_three": "mastery"},
    "equipment": {"user_average": 331.75, "elite_average": 334.81, "average_source": "Current logged-in WCL character-page display",
                  "old_dbc_tooltip_user_average": user_items["equipped_average"], "old_dbc_tooltip_elite_average": elite_items["equipped_average"],
                  "average_method": "WCL displayed averages. Two-handed weapon counts twice; applying +1 to the ascended items explains +0.25 and +0.3125 over old-DBC averages.",
                  "ascended_bonus": 12856, "ascended_parsed_level": 340,
                  "ascended_wcl_displayed_level": 341, "item_level_conflict": True,
                  "user_ascended": ["neck", "trinket1", "main_hand"],
                  "user_unascended_trinket": {"slot": "trinket2", "item_id": 270173, "level": 334},
                  "user_tier_pieces": ["shoulder", "chest", "hands", "legs"],
                  "elite_tier_pieces": ["head", "shoulder", "chest", "hands"],
                  "user_crafted": {"back": "331 crit/haste, arcanoweave", "wrist": "331 crit/mastery, arcanoweave",
                                   "feet": "331 crit/mastery, ordinary", "finger2": "331 crit/mastery, ordinary"},
                  "embellishment_count": 2, "slot_comparison": slot_comparison},
    "original_bonus_results": {"model": "Old-DBC original-bonus 340 model, retained for audit; not current live item-level evidence.",
                               "screening": screening, "verification": verification, "elite_comparison": elite_comparison,
                               "stats": {"literal_oct26_export": static_stats(read("gear-smoke-raw.json")),
                                         "historical_precursor_continuity_model": static_stats(read("gear-unbuffed.json")),
                                         "elite_gear_under_user_race_talents": static_stats(read("gear-elite-unbuffed.json"))},
                               "audit_summary": "gear-summary-original-bonus.json"},
    "compatibility_341": {"manifest": "gear-compat341-manifest.json", "requested_iterations": 6000, "seed": 2610202631,
                          "candidate_identities": compat_manifest["candidate_identities"],
                          "override_source": compat_manifest["override_source"], "source_limits": compat_manifest["source_limits"],
                          "comparisons": compat_comparisons, "global_optimum_claim": False,
                          "combatantinfo_cross_check": "Bisset selected fight directly confirms four 341 items. Shaseng selected fight confirms heart/weapon at 341, but its neck was then 334; the current 341 neck is sourced from the current page, not that earlier fight."},
    "build_comparability": {
        "combatantinfo_source": "gear-combatant-check.json",
        "known_fight_talent_differences": [
            {"bisset_entry": 124824, "bisset_spell": 280197, "bisset_name": "Spiritual Focus", "bisset_effect": "Zenith cooldown reduced by 20 seconds",
             "user_entry": 124825, "user_spell": 391370, "user_name": "Drinking Horn Cover", "user_effect": "Zenith duration extended by 5 seconds", "source": "User/main-agent decoded combatantinfo nodes"},
            {"bisset_entry": 125015, "bisset_spell": 1272685, "bisset_name": "Martial Agility",
             "user_entry": 124829, "user_spell": 451498, "user_name": "Energy Burst", "source": "User/main-agent decoded combatantinfo nodes"},
        ],
        "fight_duration_context": "Bisset Zenith nominally 15s vs user 20s from the supplied talent interpretation. Cooldown/cast counts cannot be attributed solely to skill; build, fight length and targeting matter.",
        "talent_control_manifest": "gear-talent-manifest.json", "requested_iterations": 3500, "seed": 2610202641,
        "interpretation": talent_manifest["interpretation"] + " Corrected runtime validation shows effective Jade Serpent buffs at about 6s/4s, consistent with the logs; the raw DBC 8s reference does not establish a mismatch. The +3.20%/+2.63% results remain controlled-model references rather than guaranteed live gains.",
        "comparisons": talent_comparisons,
    },
    "live_model_duration_mismatch": {
        "status": "corrected_prior_inference_withdrawn", "active_mismatch": False,
        "evidence": ["cast-review.md", "gear-compat341-slice-current.json", "gear-compat341-raid-current.json"],
        "spells": [443421, 443616, 1238904],
        "live_observed_seconds": "Ordinary/major Jade Serpent intervals are usually about 6s and Yulon's Avatar about 4s; prematurely replaced intervals are separate observations.",
        "raw_dbc_reference_seconds": 8, "raw_dbc_is_effective_runtime_duration": False,
        "examples_bisset_seconds": {"ordinary_443421": [31.934, 37.917], "major_443616": [40.027, 46.025]},
        "effective_runtime_buffs": jade_runtime_buffs,
        "effective_duration_consistent_with_logs": True, "engine_modified": False, "simulation_rerun": False,
        "corrected_note": "Raw DBC duration is not effective runtime duration. Existing result JSON verifies ordinary Jade Serpent mean durations about 5.903s/5.936s, major Jade Serpent 6s and Yulon's Avatar 4s, consistent with the observed 6s/4s log durations. jade_sanctuary (448508) is a different 8s buff and must not be treated as the 443421/443616 duration.",
        "interpretation": "Withdraw the previous active duration-mismatch claim. Ordinary-buff reported duration is an observed mean that can be shortened by early replacement/end of combat, not a contradiction of a 6s runtime buff. Model DPS percentages still do not guarantee identical live gains, for the general encounter/build/model limitations rather than this withdrawn mismatch.",
    },
    "recommendations": [
        {"priority": 1, "action": "优先规划321腰替换；普通331暴击精通制造腰为本批可靠改善方案。", "candidate": "waist_331_cm",
         "constraint": "资源和拥有状态未知；不推断10月23日火花、毒液石或货币余额。"},
        {"priority": 2, "action": "大米可考虑334邪恶炼金师指环替331制造戒，保留虫群戒；团本收益接近零。", "candidate": "raid_ring_334",
         "constraint": "获取条件和当前资源未知；不可将单项收益与制造腰直接相加。"},
        {"priority": 3, "action": "321手、腿和肩是后续护甲提升位；保留四件套。模仿高手改制造腿时必须同时用套装头补足四件。"},
        {"priority": 4, "action": "保留现有暴击精通制造戒、腕和鞋；不建议全部制造件改急速精通。披风和单颗宝石调整收益较小且存在场景分歧。"},
    ],
    "limitations": [
        "Fresh exports omit redirected_base_stats. Historical precursor restoration is explicitly conditional, while elite precursor stats are unknown.",
        "Old DBC and tooltip bonus resolution returns 340, while current WCL pages display 341. Tooltip retrieval/HTTP dates do not establish item-data hotfix currency; 340 cannot determine current live item levels.",
        "The appended compatibility batch explicitly overrides ascended items to ilevel=341 from current WCL display while preserving bonuses. This is not new bonus evidence, a repaired engine, or a measured global optimum.",
        "Corrected duration note: raw DBC duration is not effective runtime duration. Existing slice/raid results show ordinary Jade Serpent mean durations about 5.903s/5.936s, major Jade Serpent 6s and Yulon's Avatar 4s, consistent with the logs. jade_sanctuary is a distinct 8s buff. The prior active live/model duration-mismatch inference is withdrawn; no rerun or engine change was needed. DPS deltas remain model references rather than guaranteed live gains under the other stated limitations.",
        "Battle Gi Void Eruption and Band of the Swarmcaller AoE splitting remain unverified in this engine. bugs=1 preserves the implemented live-bug behavior.",
        "Potion of Recklessness selects current effective secondary ratings on each use; the highest precombat rating does not guarantee the same potion stat after procs.",
        "DPS errors are 95% confidence-interval half-widths from JSON mean_std_dev times confidence_estimator; overlapping intervals do not establish equivalence.",
        "Elite website gear dated October 26 is not equipment at a particular logged fight. Ranking and score are supplied context, not used as model inputs.",
        "A subsequent saved combatantinfo check matches Bisset fight 28 permanent gear to the current export, but Shaseng fight 4 had a 334 neck rather than the current 341 neck. Current-gear simulations do not reproduce Shaseng fight 4.",
        "No ownership, resources, acquisition events, or untested combined gains are inferred.",
    ],
    "validation": {"all_runs_accepted": True, "accepted_run_count": len(runs), "severe_count": 0,
                   "all_race_equal_user": True, "all_gear_comparison_talents_equal_user": True,
                   "explicit_talent_control_runs": 4, "all_live_data": True,
                   "snapshot_hash_unchanged": True, "error_definition": "95% CI half-width; standard error retained separately."},
    "runs": runs,
}
(HERE / "gear-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"file": "gear-summary.json", "validated_runs": len(runs),
                  "compatibility_341": compat_comparisons}, ensure_ascii=False, indent=2))
