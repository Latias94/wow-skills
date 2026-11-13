"""Build and run the bounded October 26 gear comparisons without editing imports."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SNAPSHOT = ROOT / "records/cn-barrens-shaseng/snapshots/2026-10-26-equipped.simc"
OLD = SNAPSHOT.with_name("2026-10-23.simc")
ENGINE = ROOT / ".local/simc-build/Release/simc.exe"
SLOTS = "head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand".split()


def read_import(path):
    return [s.strip() for s in path.read_text(encoding="utf-8-sig").splitlines()
            if s.strip() and not s.startswith("#")]


def fields(line):
    return dict(p.split("=", 1) for p in line.split("=", 1)[1].split(",") if "=" in p)


def update(line, **changes):
    result = fields(line)
    for key, value in changes.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = str(value)
    return line.split("=", 1)[0] + "=," + ",".join(f"{k}={v}" for k, v in result.items())


def build():
    lines = read_import(SNAPSHOT)
    gear = {s.split("=", 1)[0]: s for s in lines if s.split("=", 1)[0] in SLOTS}
    old_gear = {s.split("=", 1)[0]: s for s in read_import(OLD) if s.split("=", 1)[0] in SLOTS}
    recovered = dict(gear)
    recovery = {}
    # Matching IDs and bonuses support continuity, but do not prove current source identity.
    for slot in ("shoulder", "chest", "hands", "waist", "legs"):
        latest, prior = fields(gear[slot]), fields(old_gear[slot])
        assert latest["id"] == prior["id"]
        assert set(latest["bonus_id"].split("/")) == set(prior["bonus_id"].split("/"))
        extra = {k: prior[k] for k in ("redirected_base_stats", "crafted_stats") if k in prior}
        recovered[slot] = update(gear[slot], **extra)
        recovery[slot] = extra
    actor = [s.replace("race=熊猫人", "race=pandaren").replace("role=dps", "role=attack")
             for s in lines if s.split("=", 1)[0] not in SLOTS]

    def haste_mastery(line):
        # Change only the missive pair; keep every other bonus, including embellishments.
        bonuses = ["8793" if b in {"8790", "8791", "8792", "8793", "8794", "8795"} else b
                   for b in fields(line)["bonus_id"].split("/")]
        return update(line, bonus_id="/".join(bonuses))

    candidates = {
        "current": {"label": "当前装备（保留历史前驱元数据的模型）", "changes": {}},
        "cloak_hm": {"label": "仅披风改急速精通，保留奥纹", "changes": {"back": haste_mastery(recovered["back"])}},
        "ring_hm": {"label": "仅制造戒改急速精通", "changes": {"finger2": haste_mastery(recovered["finger2"])}},
        "all_crafts_hm": {"label": "披风、腕、鞋、制造戒全部改急速精通，保留双奥纹", "changes": {
            s: haste_mastery(recovered[s]) for s in ("back", "wrist", "feet", "finger2")}},
        "one_gem_hm": {"label": "仅一颗戒指暴击精通宝石改急速精通，保留另一红色宝石", "changes": {
            "finger2": update(recovered["finger2"], gem_id="240892")}},
        "waist_331_cm": {"label": "普通331暴击精通制造腰替321腰，保留四件套及双奥纹", "changes": {
            "waist": update(recovered["feet"].replace("feet=", "waist=", 1), id=244573, enchant_id=None)}},
    }
    elite_path = HERE / "wcl-elite-profile.simc"
    elite = {}
    if elite_path.exists():
        elite = {s.split("=", 1)[0]: s for s in read_import(elite_path) if s.split("=", 1)[0] in SLOTS}
        assert set(elite) == set(gear)
        candidates["elite_full"] = {
            "label": "Bisset网页整装，保持沙僧熊猫人及当前天赋；高手前驱元数据未知",
            "changes": elite,
        }
        candidates["raid_ring_334"] = {
            "label": "334邪恶炼金师指环替331制造戒，保留原宝石及虫群戒",
            "changes": {"finger2": update(elite["finger1"].replace("finger1=", "finger2=", 1), gem_id="240908")},
        }
    manifest = {
        "created_at": datetime.now().astimezone().isoformat(),
        "snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        "engine": str(ENGINE.relative_to(ROOT)),
        "engine_sha256": hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
        "source_commit": subprocess.check_output(["git", "-C", "E:/github/simc", "rev-parse", "HEAD"], text=True).strip(),
        "normalization": {"race": "熊猫人 -> pandaren", "role": "dps -> attack"},
        "historical_metadata_recovery": {
            "source": str(OLD.relative_to(ROOT)), "fields": recovery,
            "status": "Assumed continuity of five equipped catalyst pieces with matching IDs and all bonuses; not a fresh addon verification.",
        },
        "excluded_historical_fields": ["bags", "currencies", "omnium_talents", "professions", "ilevel overrides", "target profiles"],
        "candidates": candidates,
    }
    if elite:
        manifest["elite_reference"] = {
            "source": "wcl-elite-profile.simc", "sha256": hashlib.sha256(elite_path.read_bytes()).hexdigest(),
            "identity": "Bisset / EU-Kazzak / WCL 61823014",
            "kind": "October 26 website equipment, not equipment at a specific combat event",
            "catalyst_metadata": "Not exported; do not invent precursor stats for the elite character.",
        }
    (HERE / "gear-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return actor, gear, recovered, candidates


def emit(name, actor, gear, mode, iterations, seed, consumes=True, raid=False):
    style, length, targets = {"raid": ("Patchwerk", 240, 1), "aoe": ("Patchwerk", 90, 5),
                               "slice": ("DungeonSlice", 360, 1)}[mode]
    consumables = (["flask=flask_of_the_magisters_2", "food=harandar_celebration", "augmentation=void_touched",
                    "potion=potion_of_recklessness_2", "temporary_enchant=main_hand:thalassian_phoenix_oil_2"]
                   if consumes else [f"{s}=disabled" for s in ("flask", "food", "augmentation", "potion", "temporary_enchant")])
    content = ["# October 26 bounded personal study; recovered catalyst metadata is an explicit assumption.",
               "ptr=0", "item_db_source=local", *actor, *gear.values(), *consumables,
               f"optimal_raid={int(raid)}", f"override.bloodlust={int(raid)}", f"fight_style={style}",
               f"max_time={length}", f"desired_targets={targets}", "vary_combat_length=0", "fixed_time=1",
               "threads=8", f"iterations={iterations}", f"seed={seed}", "confidence=0.95"]
    path = HERE / f"gear-{name}.simc"
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return path


def run(path):
    name = path.stem
    started = datetime.now().astimezone().isoformat()
    with (HERE / f"{name}.run.log").open("w", encoding="utf-8") as log:
        result = subprocess.run([str(ENGINE), str(path), f"json2={HERE / (name + '.json')}",
                                 f"output={HERE / (name + '.txt')}"], cwd=HERE, stdout=log, stderr=subprocess.STDOUT)
    doc = json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))
    actors = doc["sim"]["players"]
    severe = [entry for entry in doc.get("logs", []) if "severe" in entry.get("level", "").lower()]
    text = (HERE / f"{name}.run.log").read_text(encoding="utf-8") + (HERE / f"{name}.txt").read_text(encoding="utf-8")
    severe_text = bool(re.search(r"\bsevere\b", text, re.I))
    accepted = result.returncode == 0 and all(a.get("valid_fight_style") is True for a in actors) and not severe and not severe_text
    record = {"name": name, "started_at": started, "ended_at": datetime.now().astimezone().isoformat(),
              "exit_code": result.returncode, "accepted": accepted,
              "valid_fight_style": [a.get("valid_fight_style") for a in actors],
              "severe": severe, "severe_in_text": severe_text, "logs": doc.get("logs", [])}
    (HERE / f"{name}.validation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run": name, "accepted": accepted, "dps": actors[0]["collected_data"]["dps"]["mean"]}, ensure_ascii=False), flush=True)
    if not accepted:
        raise RuntimeError(f"Rejected evidence: {name}; inspect its validation and logs before proceeding.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["prepare", "smoke", "elite-smoke", "screen", "verify"])
    parser.add_argument("--mode", choices=["raid", "aoe", "slice"], default="slice")
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--literal", action="store_true")
    args = parser.parse_args()
    actor, literal, recovered, candidates = build()
    base = literal if args.literal else recovered
    if args.stage == "prepare":
        return
    if args.stage == "smoke":
        for name, mode, consumes, raid in (("unbuffed", "raid", False, False), ("smoke-aoe", "aoe", True, False),
                                            ("smoke-slice", "slice", True, False), ("smoke-raid", "raid", True, True)):
            run(emit(name, actor, base, mode, 40, 2610202602, consumes, raid))
        return
    if args.stage == "elite-smoke":
        for name, mode, consumes, raid in (("elite-unbuffed", "raid", False, False),
                                          ("elite-smoke-slice", "slice", True, False),
                                          ("elite-smoke-raid", "raid", True, True)):
            run(emit(name, actor, candidates["elite_full"]["changes"], mode, 40, 2610202603, consumes, raid))
        return
    selected = args.candidate or list(candidates)
    for key in selected:
        if key not in candidates:
            raise ValueError(key)
        changes = candidates[key]["changes"]
        name = f"{args.stage}-{'literal-' if args.literal else ''}{args.mode}-{key}"
        run(emit(name, actor, {**base, **changes}, args.mode,
                 3500 if args.stage == "screen" else 6000,
                 2610202611 if args.stage == "screen" else 2610202621,
                 raid=args.mode == "raid"))


if __name__ == "__main__":
    main()
