"""Bounded personal equipment comparisons using the existing local SimC build."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ENGINE = ROOT / ".local/simc-build/Release/simc.exe"
RAW = ROOT / "records/cn-barrens-shaseng/snapshots/2026-10-29-equipped.simc"
SLOTS = "head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand".split()


def fields(line):
    return dict(s.split("=", 1) for s in line.split("=", 1)[1].split(",") if "=" in s)


def update(line, **changes):
    data = fields(line)
    for key, value in changes.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = str(value)
    return line.split("=", 1)[0] + "=," + ",".join(f"{k}={v}" for k, v in data.items())


def load():
    lines = [x for x in RAW.read_text(encoding="utf-8-sig").splitlines() if x and not x.startswith("#")]
    literal = {x.split("=", 1)[0]: x for x in lines if x.split("=", 1)[0] in SLOTS}
    # Build 70575 resolves bonus 12856 to 341 natively; no level override is needed.
    recovered = dict(literal)
    for slot, source in {"head":271875, "shoulder":251146, "chest":281236, "waist":271436, "legs":251130}.items():
        recovered[slot] = update(recovered[slot], redirected_base_stats=source)
    recovered["waist"] = update(recovered["waist"], crafted_stats="36/49")
    actor = [x.replace("race=熊猫人", "race=pandaren").replace("role=dps", "role=attack") for x in lines if x.split("=", 1)[0] not in SLOTS]
    return actor, literal, recovered


def candidates(base):
    def missive(slot, code):
        ids = [str(code) if b in {"8790","8791","8792","8793","8794","8795"} else b for b in fields(base[slot])["bonus_id"].split("/")]
        return update(base[slot], bonus_id="/".join(ids))
    waist = update(base["feet"].replace("feet=", "waist=", 1), id=244573, enchant_id=None)
    def tier(slot, source, level):
        ids = [b for b in fields(base[slot])["bonus_id"].split("/") if b not in {"12846","12850","12854"}]
        ids.append("12850" if level == 321 else "12854")
        return update(base[slot], bonus_id="/".join(ids), redirected_base_stats=source, ilevel=level)
    delve_shoulder = tier("shoulder",272244,334)
    raid_legs = tier("legs",268225,334)
    raid_belt = "waist=,id=268256,bonus_id=13334/12854,ilevel=334"
    tendril = "trinket2=,id=281215,bonus_id=13334/12856"
    route = {"shoulder":delve_shoulder,"legs":raid_legs,"waist":raid_belt,"trinket2":tendril}
    delve_ring = "finger2=,id=272149,bonus_id=12854,ilevel=334,enchant_id=7967"
    return {
        "current": ({}, {}),
        "waist_cm": ({"waist":waist}, {}),
        "waist_hm": ({"waist":update(waist, bonus_id=fields(waist)["bonus_id"].replace("8791","8793"))}, {}),
        "shoulder334": ({"shoulder":update(base["shoulder"], ilevel=334)}, {}),
        "legs334": ({"legs":update(base["legs"], ilevel=334)}, {}),
        "shoulder324": ({"shoulder":update(base["shoulder"], ilevel=324)}, {}),
        "glove_art": ({"hands":update(base["hands"], enchant_id=8727)}, {}),
        "cloak_hm": ({"back":missive("back", 8793)}, {}),
        "glove_cm": ({"hands":missive("hands", 8791)}, {}),
        "gems_hm": ({"finger1":update(base["finger1"], gem_id=240892), "finger2":update(base["finger2"], gem_id=240892)}, {}),
        "flask_haste": ({}, {"flask":"flask_of_the_blood_knights_2"}),
        "flask_crit": ({}, {"flask":"flask_of_the_shattered_sun_2"}),
        "tendril334": ({"trinket2":"trinket2=,id=281215,ilevel=334"}, {}),
        "tendril341": ({"trinket2":"trinket2=,id=281215,ilevel=341"}, {}),
        "tendril341_no_heart": ({"trinket1":"trinket1=,id=281215,ilevel=341"}, {}),
        "delve_shoulder321": ({"shoulder":tier("shoulder",272244,321)}, {}),
        "delve_shoulder334": ({"shoulder":delve_shoulder}, {}),
        "delve_legs334": ({"legs":tier("legs",272243,334)}, {}),
        "h7_legs334": ({"legs":raid_legs}, {}),
        "h7_waist334": ({"waist":raid_belt}, {}),
        "delve_craft_now": ({"shoulder":delve_shoulder,"waist":waist}, {}),
        "route": (route, {}),
        "route_craft_waist": ({**route,"waist":waist}, {}),
        "route_haste_gems": ({**route,"finger1":update(base["finger1"],gem_id=240892),"finger2":update(base["finger2"],gem_id=240892)}, {}),
        "route_haste_flask": (route, {"flask":"flask_of_the_blood_knights_2"}),
        "route_crit_flask": (route, {"flask":"flask_of_the_shattered_sun_2"}),
        "delve_ring334": ({"finger2":delve_ring}, {}),
        "delve_ring334_socket": ({"finger2":update(delve_ring,gem_id=240908)}, {}),
        "post_legs": ({"legs":raid_legs}, {}),
        "post_legs_shoulder": ({"legs":raid_legs,"shoulder":delve_shoulder}, {}),
        "post_legs_ring": ({"legs":raid_legs,"finger2":delve_ring}, {}),
        "post_waist": ({"waist":raid_belt}, {}),
        "post_waist_shoulder": ({"waist":raid_belt,"shoulder":delve_shoulder}, {}),
        "post_waist_legs": ({"waist":raid_belt,"legs":tier("legs",272243,334)}, {}),
        "post_waist_ring": ({"waist":raid_belt,"finger2":delve_ring}, {}),
        "post_both": ({"waist":raid_belt,"legs":raid_legs}, {}),
        "post_both_shoulder": ({"waist":raid_belt,"legs":raid_legs,"shoulder":delve_shoulder}, {}),
        "post_both_ring": ({"waist":raid_belt,"legs":raid_legs,"finger2":delve_ring}, {}),
        "post_both_ring_socket": ({"waist":raid_belt,"legs":raid_legs,"finger2":update(delve_ring,gem_id=240908)}, {}),
        "post_both_raid_shoulder": ({"waist":raid_belt,"legs":raid_legs,"shoulder":tier("shoulder",268246,334)}, {}),
        "route_raid_shoulder": ({**route,"shoulder":tier("shoulder",268246,334)}, {}),
        **{f"post_both_ring_{item}_socket":({"waist":raid_belt,"legs":raid_legs,"finger2":update(delve_ring,id=item,gem_id=240908)}, {}) for item in (272147,272148,272150)},
    }


def emit(key, mode, iterations, seed, literal=False, consumes=True):
    actor, raw, recovered = load()
    base = raw if literal else recovered
    changes, options = candidates(base)[key]
    gear = {**base, **changes}
    style, length, targets = {"slice":("DungeonSlice",360,1), "st":("Patchwerk",240,1), "aoe":("Patchwerk",90,5)}[mode]
    settings = {"flask":"flask_of_the_magisters_2", "food":"harandar_celebration", "augmentation":"void_touched", "potion":"potion_of_recklessness_2", "temporary_enchant":"main_hand:thalassian_phoenix_oil_2"}
    settings.update(options)
    if not consumes:
        settings = {k:"disabled" for k in settings}
    name = f"native70575-{'literal-' if literal else ''}{'stats' if not consumes else mode}-{key}-{iterations}-{seed}"
    path = HERE / f"{name}.simc"
    lines = ["# Native level341 resolution; Catalyst source stats retained per user confirmation and historical export.", "ptr=0", "item_db_source=local", *actor, *gear.values(), *[f"{k}={v}" for k,v in settings.items()], "optimal_raid=0", "override.bloodlust=0", f"fight_style={style}", f"max_time={length}", f"desired_targets={targets}", "vary_combat_length=0", "fixed_time=1", "threads=8", f"iterations={iterations}", f"seed={seed}", "confidence=0.95"]
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")
    return path


def run(path):
    start = datetime.now().astimezone().isoformat()
    with path.with_suffix(".run.log").open("w",encoding="utf-8") as log:
        proc = subprocess.run([str(ENGINE),str(path),f"json2={path.with_suffix('.json')}",f"output={path.with_suffix('.txt')}"],cwd=HERE,stdout=log,stderr=subprocess.STDOUT)
    if not path.with_suffix(".json").exists():
        raise RuntimeError(path.with_suffix(".run.log").read_text(encoding="utf-8"))
    doc=json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    a=doc["sim"]["players"][0]
    text=path.with_suffix(".txt").read_text(encoding="utf-8")+path.with_suffix(".run.log").read_text(encoding="utf-8")
    accepted=proc.returncode==0 and a.get("valid_fight_style") is True and not re.search(r"\bsevere\b",text,re.I) and not any("severe" in x.get("level","").lower() for x in doc.get("logs",[]))
    dps=a["collected_data"]["dps"]
    result={"name":path.stem,"started_at":start,"ended_at":datetime.now().astimezone().isoformat(),"accepted":accepted,"exit_code":proc.returncode,"valid_fight_style":a.get("valid_fight_style"),"dps":dps["mean"],"ci95":dps.get("mean_std_dev",0)*doc["sim"]["options"]["confidence_estimator"],"samples":dps["count"],"logs":doc.get("logs",[])}
    path.with_suffix(".validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False),flush=True)
    if not accepted:
        raise RuntimeError("Rejected workload: "+path.stem)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=["smoke","screen","verify"])
    parser.add_argument("--candidate",action="append")
    parser.add_argument("--mode",action="append",choices=["slice","st","aoe"])
    args=parser.parse_args()
    manifest={"created_at":datetime.now().astimezone().isoformat(),"source_commit":subprocess.check_output(["git","-C","E:/github/simc","rev-parse","HEAD"],text=True).strip(),"engine_sha256":hashlib.sha256(ENGINE.read_bytes()).hexdigest(),"snapshot_sha256":hashlib.sha256(RAW.read_bytes()).hexdigest(),"mode":"Live 12.1.5.70575 / 2026-10-28 hotfix","assumptions":{"ascended_level":"Native bonus12856=341, no override","head_precursor":271875,"other_precursors":"October23 matching bonuses and IDs; user confirms retained stats and effects","balance_and_bags":"unknown"}}
    (HERE/"simc-manifest-native70575.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    if args.stage=="smoke":
        for literal in (True,False):
            run(emit("current","st",40,26102901,literal,False))
        for mode in ("slice","st","aoe"):
            run(emit("current",mode,40,26102901))
        return
    iterations, seed=(3000,26102911) if args.stage=="screen" else (7000,26102921)
    for mode in args.mode or ["slice","st","aoe"]:
        for key in args.candidate or list(candidates(load()[2])):
            run(emit(key,mode,iterations,seed))


if __name__=="__main__":
    main()
