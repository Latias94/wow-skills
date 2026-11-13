"""Tune existing crafts and sockets after the three proposed armor upgrades."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
TOOLS = runpy.run_path(str(HERE / "personal-study.py"))
UPDATE, FIELDS, RUN = (TOOLS[k] for k in ("update", "fields", "run"))
SLOTS, ENGINE = TOOLS["SLOTS"], TOOLS["ENGINE"]


def base_gear(branch):
    actor, _, current = TOOLS["load"]()
    key = "route" if branch == "tendril" else "post_both_shoulder"
    changes, _ = TOOLS["candidates"](current)[key]
    return actor, {**current, **changes}


def variants(base):
    def craft(slot, code):
        bonuses = [str(code) if x in {"8790", "8791", "8792", "8793", "8794", "8795"} else x
                   for x in FIELDS(base[slot])["bonus_id"].split("/")]
        return {slot: UPDATE(base[slot], bonus_id="/".join(bonuses))}

    def gems(gem_id, diamond=240983):
        return {"neck": UPDATE(base["neck"], gem_id=f"{diamond}/{gem_id}"),
                "finger1": UPDATE(base["finger1"], gem_id=gem_id),
                "finger2": UPDATE(base["finger2"], gem_id=gem_id)}

    result = {"baseline": ({}, {})}
    for slot in ("back", "wrist", "hands", "feet", "finger2"):
        owned = set(FIELDS(base[slot])["bonus_id"].split("/"))
        for label, code in (("ch", 8790), ("cm", 8791), ("hm", 8793)):
            if str(code) not in owned:
                result[f"craft_{slot}_{label}"] = (craft(slot, code), {})
    for gem_id in (240890, 240892, 240898, 240900, 240906, 240908, 240888, 240896, 240904):
        result[f"gems_{gem_id}"] = (gems(gem_id), {})
    result["diamond_powerful"] = ({"neck": UPDATE(base["neck"], gem_id="240967/240892")}, {})
    result["diamond_three_colors"] = ({"neck": UPDATE(base["neck"], gem_id="240967/240892"),
                                         "finger1": UPDATE(base["finger1"], gem_id=240908),
                                         "finger2": UPDATE(base["finger2"], gem_id=240898)}, {})
    for label, code in (("mastery",7965), ("haste",8021), ("crit",7997),
                        ("advanced_mastery",7969), ("advanced_haste",8025)):
        result[f"rings_{label}"] = ({s: UPDATE(base[s], enchant_id=code) for s in ("finger1", "finger2")}, {})
    result["flask_haste"] = ({}, {"flask":"flask_of_the_blood_knights_2"})
    result["flask_crit"] = ({}, {"flask":"flask_of_the_shattered_sun_2"})
    result["craft_cm_pair"] = ({**craft("back",8791), **craft("hands",8791)}, {})
    result["craft_cm_pair_mastery_gems"] = ({**craft("back",8791), **craft("hands",8791), **gems(240898)}, {})
    return result


def emit(branch, key, mode, iterations, seed, unbuffed=False):
    actor, base = base_gear(branch)
    changed, options = variants(base)[key]
    gear = {**base, **changed}
    style, length, targets = {"slice":("DungeonSlice",360,1), "st":("Patchwerk",240,1),
                              "aoe":("Patchwerk",90,5)}[mode]
    settings = {"flask":"flask_of_the_magisters_2", "food":"harandar_celebration",
                "augmentation":"void_touched", "potion":"potion_of_recklessness_2",
                "temporary_enchant":"main_hand:thalassian_phoenix_oil_2"}
    settings.update(options)
    if unbuffed:
        settings = {k:"disabled" for k in settings}
    path = HERE / f"tuning-{branch}-{'stats' if unbuffed else mode}-{key}-{iterations}-{seed}.simc"
    lines = ["# Hypothetical armor upgrades: Catalyst272244 shoulder +268225 legs +268256 waist, all334.",
             "# Existing crafts stay331; sockets, four-piece and double Arcanoweave are retained.",
             "ptr=0", "item_db_source=local", *actor, *gear.values(),
             *[f"{k}={v}" for k,v in settings.items()], "optimal_raid=0", "override.bloodlust=0",
             f"fight_style={style}", f"max_time={length}", f"desired_targets={targets}",
             "vary_combat_length=0", "fixed_time=1", "threads=8", f"iterations={iterations}",
             f"seed={seed}", "confidence=0.95"]
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["screen", "verify", "stats"])
    parser.add_argument("--branch", action="append", choices=["zuljin", "tendril"])
    parser.add_argument("--candidate", action="append")
    parser.add_argument("--mode", action="append", choices=["slice", "st", "aoe"])
    args = parser.parse_args()
    iterations, seed = {"screen":(3000,26102941), "verify":(12000,26102951), "stats":(40,26102931)}[args.stage]
    for branch in args.branch or ["zuljin", "tendril"]:
        options = variants(base_gear(branch)[1])
        for key in args.candidate or list(options):
            default_modes = ["slice"] if args.stage == "screen" else ["st"] if args.stage == "stats" else ["slice", "aoe", "st"]
            for mode in args.mode or default_modes:
                RUN(emit(branch,key,mode,iterations,seed,args.stage=="stats"))
    manifest = {"created_at":datetime.now().astimezone().isoformat(),
                "source_commit":subprocess.check_output(["git","-C","E:/github/simc","rev-parse","HEAD"],text=True).strip(),
                "engine_sha256":hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
                "live_data":"12.1.5.70575 / 2026-10-28 hotfix",
                "scope":"Armor shoulder272244/legs268225/waist268256 at334; current331 crafts; two trinket branches; no extra sockets.",
                "validation":"Each run has accepted/valid_fight_style/severe diagnostics; same models and consumables as personal-study.py.",
                "unbuffed_context":"All consumables, raid buffs and bloodlust disabled; gear/talent passives retained.",
                "candidates":list(variants(base_gear("zuljin")[1]))}
    (HERE/"tuning-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
