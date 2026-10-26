"""Build the dated Elemental study from the preserved character export."""

import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAR = ROOT.parents[1]
RAW = (CHAR / "snapshots/2026-10-23.simc").read_text(encoding="utf-8-sig")
SLOTS = "head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand off_hand".split()
ACTOR = [line for line in RAW.splitlines() if line and not line.startswith("#") and line.split("=", 1)[0] not in ("shirt", "tabard")]
GEAR = {line.split("=", 1)[0]: line for line in ACTOR if line.split("=", 1)[0] in SLOTS}
MANIFEST_PATH = ROOT / "study-manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if MANIFEST_PATH.exists() else {}
PAIR_NAMES = {"CH": "暴击急速", "CM": "暴击精通", "HM": "急速精通"}
PAIRS = {"CH": "32/36", "CM": "32/49", "HM": "36/49"}
STAT_KEYS = ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")
MODES = ("raid", "dungeon")


def fields(line):
    return dict(part.split("=", 1) for part in line.split("=", 1)[1].split(",") if "=" in part)


def measured(key):
    path = ROOT / f"{key}.json"
    if path.stat().st_mtime < (ROOT / f"{key}.simc").stat().st_mtime:
        raise ValueError(f"Stale simulation: {key}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    sim = payload["sim"]
    if sim["players"][0]["valid_fight_style"] is not True:
        raise ValueError(f"Unsupported fight style cannot select gear: {key}")
    if payload.get("errors") or sim.get("errors") or "Severe:" in (ROOT / f"{key}.run.log").read_text(encoding="utf-8-sig"):
        raise ValueError(f"Severe simulation diagnostics: {key}")
    return sim


def modify(line, **changes):
    data = fields(line)
    for key, value in changes.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = str(value)
    return line.split("=", 1)[0] + "=," + ",".join(f"{key}={value}" for key, value in data.items())


def item(slot, ident, level=334, **kwargs):
    return modify(f"{slot}=,id={ident}", ilevel=level, **kwargs)


def craft(slot, ident, stats="32/36", embellish=None, level=331, **kwargs):
    return item(slot, ident, level, crafted_stats=stats, crafting_quality=5, bonus_id=embellish, **kwargs)


def recraft(line, stats, embellish=None):
    data = fields(line)
    removed = {"8790", "8791", "8792", "8793"}
    if embellish is not None:
        removed |= {"12384", "13771"}
    bonuses = [bonus for bonus in data.get("bonus_id", "").split("/") if bonus and bonus not in removed]
    if embellish:
        bonuses.append(str(embellish))
    return modify(line, crafted_stats=stats, bonus_id="/".join(bonuses) or None)


def bag(slot, ident):
    matches = re.findall(r"^# [a-z0-9_]+=([^\n]*\bid=" + str(ident) + r"(?:,|$)[^\n]*)", RAW, re.M)
    if not matches:
        raise ValueError(f"Not in exported bags: {ident}")
    return slot + "=" + matches[0].strip()


def prepared():
    gear = dict(GEAR)
    gear["head"] = modify(gear["head"], enchant_id=8017)
    gear["finger2"] = modify(gear["finger2"], enchant_id=7967, gem_id=240906)
    return gear


def talent(mode):
    if mode == "raid":
        match = re.search(r"# Saved Loadout: 单体\r?\n# talents=([^\r\n]+)", RAW)
        return match[1]
    return next(line.split("=", 1)[1] for line in ACTOR if line.startswith("talents="))


def emit(key, mode, gear, candidates, iterations=1500, seed=23102026, stage="screen", flask=None):
    actor = [line for line in ACTOR if line.split("=", 1)[0] not in SLOTS + ["talents"]]
    lines = ["# Zhengjitu 2026-10-23; hypothetical targets are not acquisitions.", "ptr=0"] + actor + ["talents=" + talent(mode)] + list(gear.values())
    lines += [f"flask={flask or 'flask_of_the_shattered_sun_2'}", "food=harandar_celebration", "potion=lights_potential_2", "augmentation=void_touched",
              "temporary_enchant=main_hand:thalassian_phoenix_oil_2,if=!talent.flametongue_weapon",
              f"optimal_raid={1 if mode == 'raid' else 0}", f"override.bloodlust={1 if mode == 'raid' else 0}",
              "fight_style=Patchwerk", f"desired_targets={1 if mode == 'raid' else 5}", f"max_time={240 if mode == 'raid' else 90}",
              "vary_combat_length=0", "threads=12", "profileset_work_threads=2", f"iterations={iterations}", f"seed={seed}"]
    for name, (label, changes) in candidates.items():
        for i, change in enumerate(changes):
            lines.append(f'profileset."{name}"{"=" if i == 0 else "+="}{change}')
    (ROOT / f"{key}.simc").write_text("\n".join(lines) + "\n", encoding="utf-8")
    MANIFEST[key] = {"mode": mode, "stage": stage, "labels": {name: value[0] for name, value in candidates.items()}}


def initial():
    p = prepared()
    for mode in MODES:
        changes = {
            "Prepared": ("补头部附魔、虫群戒附魔与唯一现有空孔", list(p.values())),
            "Shoulder_334": ("同来源神话肩334并化生；不是英雄321直接升轨道", [item("shoulder", 271481, redirected_base_stats=272252, enchant_id=8001)]),
            "Shoulder_raid": ("334游魂护肩化生套肩，保留四件套", [item("shoulder", 271481, redirected_base_stats=268231, enchant_id=8001)]),
            "Venom_334": ("另获神话毒液饰品334替英雄321毒液", [item("trinket1", 273796)]),
            "Tendril_for_venom": ("334触须替321毒液；需要获取，目标节奏暂定", [item("trinket1", 281215)]),
            "Tendril_for_bag": ("334触须替334无底袋；保留321毒液", [item("trinket2", 281215)]),
            "Owned_dagger_shield": ("背包331简斯拉泽＋321风暴庇护；不额外搬美化", [bag("main_hand", 271092), bag("off_hand", 251150)]),
        }
        emit(f"current-{mode}", mode, GEAR, changes, iterations=2000, stage="current")
        practical = {
            "Raw_current": ("原始现装未补齐", list(GEAR.values())),
            "Owned_dagger_shield": ("背包331简斯拉泽＋321盾；无制造重做", [modify(bag("main_hand", 271092), enchant_id=8689), bag("off_hand", 251150)]),
            "Dagger334_shield321": ("背包神话匕首331升334＋现有321盾", [item("main_hand", 271092, enchant_id=8689), bag("off_hand", 251150)]),
            "Dagger331_craftshield": ("背包331匕首＋331普通制造盾CH", [modify(bag("main_hand", 271092), enchant_id=8689), craft("off_hand", 237831)]),
            "Dagger334_shield334": ("334简斯拉泽＋另获334盾", [item("main_hand", 271092, enchant_id=8689), item("off_hand", 268196)]),
            "Venom_334": ("神话334毒液替英雄321", [item("trinket1", 273796)]),
            "Tendril_for_venom": ("334触须替321毒液", [item("trinket1", 281215)]),
            "Loa_ring": ("331洛阿制造戒替邪恶戒，保留虫群；武器去仪式石保持2美化", [craft("finger1", 251513, enchant_id=7967, gem_id=240906), recraft(p["main_hand"], "32/36", embellish="")]),
        }
        for label, stats in PAIRS.items():
            practical[f"Current_crafts_{label}"] = (f"全部现有普通／美化制造改{PAIR_NAMES[label]}，保留原美化", [recraft(p[slot], stats) for slot in ("back", "wrist", "waist", "main_hand")])
        double = {**p, "back": modify(p["back"], bonus_id="/".join(x for x in fields(p["back"])["bonus_id"].split("/") if x != "12715") + "/12384"), "main_hand": recraft(p["main_hand"], "32/36", embellish="")}
        practical["Double_lining_staff"] = ("保留法杖：仪式石改为披风第二奥纹（替钥匙链）", list(double.values()))
        double["main_hand"] = item("main_hand", 271092, enchant_id=8689)
        double["off_hand"] = craft("off_hand", 237831)
        practical["Double_lining_dagger"] = ("334匕首＋331普通盾；腕披双奥纹完整组合", list(double.values()))
        emit(f"practical-{mode}", mode, p, practical, iterations=2500, seed=24102026, stage="practical")
        bags = {f"Bag_{ident}": (f"背包实际饰品{ident}替321毒液", [bag("trinket1", ident)]) for ident in (270161, 251783, 270173, 273794)}
        emit(f"bags-{mode}", mode, p, bags, iterations=1500, stage="bags")


def target_base(placement="back_wrist", weapon="dagger", tier="legs"):
    p = prepared()
    p["shoulder"] = item("shoulder", 271481, redirected_base_stats=268231, enchant_id=8001)
    p["back"] = craft("back", 239656, embellish=12384)
    p["wrist"] = craft("wrist", 244584, embellish=12384)
    p["waist"] = craft("waist", 244581)
    p["trinket1"] = item("trinket1", 273796)
    p["trinket2"] = item("trinket2", 270164)
    if weapon == "staff":
        p["main_hand"] = recraft(p["main_hand"], "32/36", embellish="")
    else:
        p["main_hand"] = item("main_hand", 271092, enchant_id=8689)
        p["off_hand"] = item("off_hand", 268196)
    if tier == "craft_legs":
        p["legs"] = craft("legs", 244582, enchant_id=7935)
    elif tier == "raid_legs":
        p["legs"] = item("legs", 268237, enchant_id=7935)
    if placement == "wrist_feet":
        p["back"] = item("back", 268253)
        p["feet"] = craft("feet", 244577, embellish=12384, enchant_id=7963)
    elif placement == "wrist_waist":
        p["back"] = item("back", 268253)
        p["waist"] = craft("waist", 244581, embellish=12384)
    return p


def targets():
    for mode in MODES:
        candidates = {}
        for placement in ("back_wrist", "wrist_feet", "wrist_waist"):
            for tier in ("legs", "craft_legs", "raid_legs"):
                gear = target_base(placement, "dagger", tier)
                candidates[f"Set_{placement}_{tier}"] = (f"完整目标：{placement}双奥纹／{tier}腿", list(gear.values()))
        gear = target_base(weapon="staff", tier="craft_legs")
        candidates["Set_staff"] = ("完整目标：现有331法杖＋双奥纹＋制造腿", list(gear.values()))
        emit(f"targets-{mode}", mode, prepared(), candidates, iterations=1800, seed=25102026, stage="target")


def load_gear(key):
    return {line.split("=", 1)[0]: line for line in (ROOT / f"{key}.simc").read_text(encoding="utf-8").splitlines() if line.split("=", 1)[0] in SLOTS}


def extract_candidate(key, name):
    prefix = f'profileset."{name}"'
    return [re.sub(r'^profileset\."[^"]+"\+?=', "", line) for line in (ROOT / f"{key}.simc").read_text(encoding="utf-8").splitlines()
            if line.startswith(prefix + "=") or line.startswith(prefix + "+=")]


def refine():
    for mode in MODES:
        key = f"targets-{mode}"
        data = measured(key)
        winner = max(data["profilesets"]["results"], key=lambda row: row["mean"])["name"]
        gear = load_gear(key)
        gear.update({line.split("=", 1)[0]: line for line in extract_candidate(key, winner)})
        candidates = {}
        for pair, stats in PAIRS.items():
            for flavor, flask in (("Crit", "shattered_sun"), ("Haste", "blood_knights"), ("Mastery", "magisters")):
                changes = [recraft(line, stats) for line in gear.values() if "crafted_stats=" in line]
                candidates[f"Stats_{pair}_{flavor}"] = (f"制造{PAIR_NAMES[pair]}＋{flavor}合剂", changes + [f"flask=flask_of_the_{flask}_2"])
        for ident in (240890, 240908, 240906, 240900):
            changes = [modify(line, gem_id="/".join(str(ident) if gem != "240983" else gem for gem in fields(line)["gem_id"].split("/"))) for line in gear.values() if fields(line).get("gem_id")]
            candidates[f"Gem_{ident}"] = (f"非钻石孔统一宝石{ident}", changes)
        for ident in (281215, 250215, 270167, 270169):
            candidates[f"Trinket_{ident}_for_venom"] = (f"334饰品{ident}替334毒液", [item("trinket1", ident)])
        candidates["Tendril_for_bag"] = ("334触须替334无底袋", [item("trinket2", 281215)])
        for ident in (268262, 237831):
            candidates[f"Shield_{ident}"] = (f"替代盾牌{ident}，制造盾按331", [craft("off_hand", ident) if ident == 237831 else item("off_hand", ident)])
        for ident in (268210, 268203):
            candidates[f"Weapon_{ident}"] = (f"334替代单手{ident}", [item("main_hand", ident, enchant_id=8689)])
        for ident in (251136, 268252, 240949):
            ring = craft("finger1", ident, enchant_id=7967, gem_id=240906) if ident == 240949 else item("finger1", ident, enchant_id=7967, gem_id=240906)
            candidates[f"Ring_{ident}_for_alchemist"] = (f"戒指{ident}替邪恶戒，保留虫群", [ring])
        candidates["Loa_ring"] = ("331洛阿制造戒替邪恶戒；披风去奥纹保留2美化", [craft("finger1", 251513, enchant_id=7967, gem_id=240906), recraft(gear["back"], "32/36", embellish="")]) if "12384" in gear["back"] else ("331洛阿制造戒替邪恶戒；腕去奥纹", [craft("finger1", 251513, enchant_id=7967, gem_id=240906), recraft(gear["wrist"], "32/36", embellish="")])
        candidates["Ordinary_hands"] = ("去H10特效，普通神话套装手", [item("hands", 271484)])
        candidates["Ordinary_chest"] = ("去H8毒咒，普通神话套胸", [item("chest", 271486, enchant_id=7987)])
        candidates["Tier_legs"] = ("换回已有334套装腿（可能为第五件）", [prepared()["legs"]])
        emit(f"refine-{mode}", mode, gear, candidates, iterations=1800, seed=26102026, stage="refine")
        MANIFEST[f"refine-{mode}"]["family"] = winner


def verify():
    for mode in MODES:
        key = f"joint-{mode}"
        result = measured(key)
        rows = sorted(result["profilesets"]["results"], key=lambda row: row["mean"], reverse=True)
        names = [row["name"] for row in rows[:6]]
        candidates = {name: (MANIFEST[key]["labels"][name], extract_candidate(key, name)) for name in names}
        gear = load_gear(key)
        for name in ("Trinket_281215_for_venom", "Tendril_for_bag", "Tier_legs", "Ordinary_hands", "Ordinary_chest"):
            candidates[name] = (MANIFEST[f"refine-{mode}"]["labels"][name], extract_candidate(f"refine-{mode}", name))
        candidates["Current_staff337"] = ("现装制造法杖升337，其他仍现装补齐（未来10石）", list(prepared().values()) + [modify(prepared()["main_hand"], ilevel=337), "off_hand=none"])
        candidates["Raw_current"] = ("原始实际装备", list(GEAR.values()) + ["off_hand=none"])
        candidates["Prepared_current"] = ("现装补齐孔附魔", list(prepared().values()) + ["off_hand=none"])
        emit(f"verify-{mode}", mode, gear, candidates, iterations=6000, seed=27102026, stage="verify")


def joint():
    for mode in MODES:
        gear = load_gear(f"refine-{mode}")
        candidates = {}
        ring_choices = {"Keep": [],
                        "Craft_for_alch": [craft("finger1", 240949, enchant_id=7967, gem_id=240906)],
                        "251136_for_alch": [item("finger1", 251136, enchant_id=7967, gem_id=240906)],
                        "268252_for_alch": [item("finger1", 268252, enchant_id=7967, gem_id=240906)],
                        "Craft_for_swarm": [craft("finger2", 240949, enchant_id=7967, gem_id=240906)],
                        "251136_for_swarm": [item("finger2", 251136, enchant_id=7967, gem_id=240906)],
                        "268252_for_swarm": [item("finger2", 268252, enchant_id=7967, gem_id=240906)]}
        for name, changes in ring_choices.items():
            candidates[f"Ring_{name}"] = (f"双戒对照：{name}", changes or [gear["finger1"]])
        selected_rings = ("Craft_for_alch", "268252_for_alch") if mode == "raid" else ("251136_for_alch", "Craft_for_swarm")
        trinkets = (("BagTendril", 281215, 270164), ("VenomTendril", 273796, 281215)) if mode == "dungeon" else (("BagVenom", 273796, 270164), ("VenomTendril", 273796, 281215))
        for ring_name in selected_rings:
            for trinket_name, first, second in trinkets:
                for pair, stats in PAIRS.items():
                    for flavor, flask in (("Crit", "shattered_sun"), ("Haste", "blood_knights")):
                        full = dict(gear)
                        for change in ring_choices[ring_name]:
                            full[change.split("=", 1)[0]] = change
                        full.update(trinket1=item("trinket1", first), trinket2=item("trinket2", second))
                        for slot, line in list(full.items()):
                            if "crafted_stats=" in line:
                                full[slot] = recraft(line, stats)
                        key = f"Joint_{ring_name}_{trinket_name}_{pair}_{flavor}"
                        candidates[key] = (f"联合：{ring_name}／{trinket_name}／{PAIR_NAMES[pair]}／{flavor}合剂", list(full.values()) + [f"flask=flask_of_the_{flask}_2"])
        emit(f"joint-{mode}", mode, gear, candidates, iterations=1800, seed=31102026, stage="joint")


def select():
    for mode in MODES:
        key = f"verify-{mode}"
        data = measured(key)
        combat = data["players"][0]["collected_data"]["dps"]
        eligible = [row for row in data["profilesets"]["results"] if row["name"] not in ("Raw_current", "Prepared_current", "Current_staff337")]
        winner = max(eligible, key=lambda row: row["mean"])
        selected = winner["name"] if winner["mean"] - combat["mean"] > math.hypot(winner["mean_error"], 1.96 * combat["mean_std_dev"]) else "Baseline"
        gear = load_gear(key)
        changes = extract_candidate(key, selected) if selected != "Baseline" else []
        for change in changes:
            if change.split("=", 1)[0] in SLOTS:
                gear[change.split("=", 1)[0]] = change
        flask = next((line.split("=", 1)[1] for line in changes if line.startswith("flask=")), None)
        emit(f"recommended-{mode}", mode, gear, {}, iterations=6000, seed=28102026, stage="recommended", flask=flask)
        MANIFEST[f"recommended-{mode}"].update(selected=selected, family=MANIFEST[f"refine-{mode}"]["family"])
        lines = (ROOT / f"recommended-{mode}.simc").read_text(encoding="utf-8").splitlines()
        excluded = {"flask", "food", "augmentation", "potion", "temporary_enchant", "optimal_raid", "override.bloodlust", "iterations"}
        unbuffed = [line for line in lines if line.split("=", 1)[0] not in excluded]
        unbuffed += ["optimal_raid=0", "override.bloodlust=0", "iterations=30"] + [f"{key}=disabled" for key in ("flask", "food", "augmentation", "potion", "temporary_enchant")]
        (ROOT / f"unbuffed-{mode}.simc").write_text("\n".join(unbuffed) + "\n", encoding="utf-8")


def upgrades():
    for mode in MODES:
        p = prepared()
        current = {"Staff337": ("10石：现有制造法杖331→337", [modify(p["main_hand"], ilevel=337)]),
                   "Neck341": ("10石：现有项链334→341", [modify(p["neck"], ilevel=341)]),
                   "Bag341": ("10石：现有无底袋334→341", [modify(p["trinket2"], ilevel=341)])}
        emit(f"upgrade-current-{mode}", mode, p, current, iterations=6000, seed=29102026, stage="upgrade-current")
        target = load_gear(f"recommended-{mode}")
        options = {}
        for slot, name in (("main_hand", "武器"), ("neck", "项链"), ("trinket1", "饰品一"), ("trinket2", "饰品二")):
            original = target[slot]
            level = 337 if "crafting_quality=" in original else 341
            options[f"Upgrade_{slot}"] = (f"10石：目标{ name }升{level}", [modify(original, ilevel=level)])
        target_text = (ROOT / f"recommended-{mode}.simc").read_text(encoding="utf-8")
        target_flask = next(line.split("=", 1)[1] for line in target_text.splitlines() if line.startswith("flask="))
        emit(f"upgrade-target-{mode}", mode, target, options, iterations=6000, seed=30102026, stage="upgrade-target", flask=target_flask)


def finalcheck():
    for mode in MODES:
        gear = load_gear(f"recommended-{mode}")
        text = (ROOT / f"recommended-{mode}.simc").read_text(encoding="utf-8")
        flask = next(line.split("=", 1)[1] for line in text.splitlines() if line.startswith("flask="))
        candidates = {"Tier_legs": ("最终戒指／饰品／合剂不变，保留已有334套腿省火花", [prepared()["legs"]])}
        for kind in ("Craft", "Tier"):
            for pair, stats in PAIRS.items():
                changed = dict(gear)
                changed["legs"] = craft("legs", 244582, stats=stats, enchant_id=7935) if kind == "Craft" else prepared()["legs"]
                changes = [recraft(line, stats) for line in changed.values() if "crafted_stats=" in line]
                if kind == "Tier":
                    changes.append(changed["legs"])
                candidates[f"{kind}Legs_{pair}"] = (f"最终组合：{'制造腿' if kind == 'Craft' else '已有334套腿'}＋制造{PAIR_NAMES[pair]}", changes)
        for placement in ("wrist_feet", "wrist_waist"):
            changed = dict(gear)
            changed["back"] = item("back", 268253)
            stats = fields(gear["wrist"])["crafted_stats"]
            if placement == "wrist_feet":
                changed["feet"] = craft("feet", 244577, stats=stats, embellish=12384, enchant_id=7963)
            else:
                changed["waist"] = craft("waist", 244581, stats=stats, embellish=12384)
            for kind in ("Craft", "Tier"):
                changed["legs"] = gear["legs"] if kind == "Craft" else prepared()["legs"]
                candidates[f"{placement}_{kind}"] = (f"最终组合：{placement}双奥纹＋{'制造腿' if kind == 'Craft' else '已有334套腿'}", list(changed.values()))
        emit(f"final-{mode}", mode, gear, candidates, iterations=6000, seed=32102026, stage="final", flask=flask)


def finalize():
    for mode in MODES:
        key = f"final-{mode}"
        data = measured(key)
        dps = data["players"][0]["collected_data"]["dps"]
        rows = data["profilesets"]["results"]
        best = max(rows, key=lambda row: row["mean"])
        selected = best["name"] if best["mean"] - dps["mean"] > math.hypot(best["mean_error"], 1.96 * dps["mean_std_dev"]) else "Baseline"
        reference = best if selected != "Baseline" else {"mean": dps["mean"], "mean_error": 1.96 * dps["mean_std_dev"]}
        save_legs = next(row for row in rows if row["name"] == "Tier_legs")
        if reference["mean"] - save_legs["mean"] <= math.hypot(reference["mean_error"], save_legs["mean_error"]):
            selected = "Tier_legs"
        gear = load_gear(key)
        for change in extract_candidate(key, selected) if selected != "Baseline" else []:
            if change.split("=", 1)[0] in SLOTS:
                gear[change.split("=", 1)[0]] = change
        previous = dict(MANIFEST[f"recommended-{mode}"])
        flask = data["players"][0]["flask"]
        emit(f"recommended-{mode}", mode, gear, {}, iterations=6000, seed=33102026, stage="recommended", flask=flask)
        MANIFEST[f"recommended-{mode}"].update(selected=selected, selected_from=key, joint_selected=previous["selected"], family=previous["family"], selection_rule="Keep owned 334 legs when within the approximate combined 95% error of the best final candidate; not an equivalence proof.")
        lines = (ROOT / f"recommended-{mode}.simc").read_text(encoding="utf-8").splitlines()
        excluded = {"flask", "food", "augmentation", "potion", "temporary_enchant", "optimal_raid", "override.bloodlust", "iterations"}
        lines = [line for line in lines if line.split("=", 1)[0] not in excluded]
        lines += ["optimal_raid=0", "override.bloodlust=0", "iterations=30"] + [f"{value}=disabled" for value in ("flask", "food", "augmentation", "potion", "temporary_enchant")]
        (ROOT / f"unbuffed-{mode}.simc").write_text("\n".join(lines) + "\n", encoding="utf-8")


def robustness():
    mode = "dungeon"
    gear = load_gear("recommended-dungeon")
    player = measured("recommended-dungeon")["players"][0]
    candidates = {"Raw_current": ("原始实装，固定大米当前天赋", list(GEAR.values()) + ["off_hand=none"]),
                  "Prepared_current": ("现装补齐孔与附魔", list(prepared().values()) + ["off_hand=none"]),
                  "BagVenom": ("同套装：334无底袋＋334毒液", [item("trinket1", 273796), item("trinket2", 270164)]),
                  "VenomTendril": ("同套装：334毒液＋334触须", [item("trinket1", 273796), item("trinket2", 281215)]),
                  "BagTendril": ("同套装：334触须＋334无底袋", [item("trinket1", 281215), item("trinket2", 270164)]),
                  "Craft_legs": ("同套装：另做331制造腿", [craft("legs", 244582, stats=fields(gear["wrist"])["crafted_stats"], enchant_id=7935)])}
    for key, count, seconds in (("robust-5t40", 5, 40), ("robust-8t40", 8, 40), ("robust-1t180", 1, 180)):
        emit(key, mode, gear, candidates, iterations=6000, seed=34102026 + count + seconds, stage="robustness", flask=player["flask"])
        path = ROOT / f"{key}.simc"
        text = path.read_text(encoding="utf-8").replace("desired_targets=5", f"desired_targets={count}").replace("max_time=90", f"max_time={seconds}")
        path.write_text(text, encoding="utf-8")


def validation():
    for mode in MODES:
        gear = load_gear(f"recommended-{mode}")
        result = measured(f"recommended-{mode}")["players"][0]
        changes = {"Raw_current": ("原始实装；固定对应模式天赋", list(GEAR.values()) + ["off_hand=none"]),
                   "Prepared_current": ("实装补齐头附魔／虫群戒附魔与唯一现有空孔", list(prepared().values()) + ["off_hand=none"])}
        emit(f"validation-{mode}", mode, gear, changes, iterations=6000, seed=35102026, stage="validation", flask=result["flask"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("initial", "targets", "refine", "joint", "verify", "select", "upgrades", "finalcheck", "finalize", "robustness", "validation"))
    parser.add_argument("--mode", choices=("raid", "dungeon", "all"), default="all")
    args = parser.parse_args()
    MODES = (args.mode,) if args.mode != "all" else ("raid", "dungeon")
    globals()[args.stage]()
    MANIFEST_PATH.write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
