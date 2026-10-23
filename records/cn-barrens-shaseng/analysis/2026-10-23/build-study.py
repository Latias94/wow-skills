"""Build the dated Shaseng comparison inputs; run SimC separately."""

import argparse
from datetime import datetime
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT.parents[1] / "snapshots/2026-10-23.simc"
SLOTS = "head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand".split()
RAW = SNAPSHOT.read_text(encoding="utf-8-sig")
ACTOR = [line for line in RAW.splitlines() if line and not line.startswith("#")]
GEAR = {line.split("=", 1)[0]: line for line in ACTOR if line.split("=", 1)[0] in SLOTS}
MANIFEST_PATH = ROOT / "study-manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if MANIFEST_PATH.exists() else {}


def modify(line, **changes):
    slot, rest = line.split("=", 1)
    fields = dict(part.split("=", 1) for part in rest.split(",") if "=" in part)
    for key, value in changes.items():
        if value is None:
            fields.pop(key, None)
        else:
            fields[key] = str(value)
    return slot + "=," + ",".join(f"{key}={value}" for key, value in fields.items())


def item(slot, ident, level=334, **fields):
    return modify(f"{slot}=,id={ident}", ilevel=level, **fields)


def craft(slot, ident, stats="32/49", embellish=True, level=331, **fields):
    return item(slot, ident, level, crafted_stats=stats, crafting_quality=5,
                bonus_id="12384" if embellish else None, **fields)


def recraft(line, stats):
    bonus = re.search(r"bonus_id=([^,]+)", line)
    # Missive bonuses override crafted_stats in this build; keep the embellishment.
    bonuses = "/".join(value for value in bonus[1].split("/") if value not in ("8790", "8791", "8792", "8793")) if bonus else None
    return modify(line, crafted_stats=stats, bonus_id=bonuses)


def equipped(**updates):
    return {**GEAR, **updates}


def prepared():
    gear = equipped()
    for slot, enchant in {"head": 8017, "chest": 7987, "feet": 7963}.items():
        gear[slot] = modify(gear[slot], enchant_id=enchant)
    # Socket counts are checked against the complete bonus-aware tooltips.
    gear["neck"] = modify(gear["neck"], gem_id="240983/240908")
    for slot in ("finger1", "finger2"):
        gear[slot] = modify(gear[slot], gem_id=240908)
    return gear


def emit(key, mode, gear, candidates, iterations=1500, seed=23102026, stage="screen", flask=None):
    flask = flask or ("flask_of_the_shattered_sun_2" if mode == "raid" else "flask_of_the_magisters_2")
    lines = ["# October 23 live-data study. Targets are not owned items.", "ptr=0"]
    lines += [line for line in ACTOR if line.split("=", 1)[0] not in SLOTS + ["shirt", "tabard"]]
    lines += list(gear.values())
    lines += [f"flask={flask}", "food=harandar_celebration", "augmentation=void_touched",
              "potion=potion_of_recklessness_2", "temporary_enchant=main_hand:thalassian_phoenix_oil_2",
              f"optimal_raid={1 if mode == 'raid' else 0}", f"override.bloodlust={1 if mode == 'raid' else 0}",
              f"fight_style={'Patchwerk' if mode == 'raid' else 'DungeonSlice'}",
              f"max_time={240 if mode == 'raid' else 360}", "vary_combat_length=0", "threads=12",
              "profileset_work_threads=2", f"iterations={iterations}", f"seed={seed}"]
    for name, (label, changes) in candidates.items():
        for index, change in enumerate(changes):
            lines.append(f'profileset."{name}"{"=" if index == 0 else "+="}{change}')
    (ROOT / f"{key}.simc").write_text("\n".join(lines) + "\n", encoding="utf-8")
    MANIFEST[key] = {"mode": mode, "stage": stage, "baseline_label": "当前导出" if stage == "current" else "本轮基准",
                     "labels": {name: row[0] for name, row in candidates.items()}}


def initial():
    tips = json.loads((ROOT / "item-cache.json").read_text(encoding="utf-8")) if (ROOT / "item-cache.json").exists() else {}
    # This guard prevents filling an assumed socket that is absent on the raw item.
    for slot in ("neck", "finger1", "finger2"):
        if tips and "socket-prismatic" not in tips[f"current:{slot}"]["tooltip"]:
            raise ValueError(f"No confirmed socket on {slot}")
    for mode in ("raid", "dungeon"):
        p = prepared()
        current_set = modify(GEAR["shoulder"], redirected_base_stats=271517)
        tier_shoulder = modify(item("shoulder", 271517, redirected_base_stats=268246, enchant_id=8001),
                               bonus_id="6652/13694/13697/12854")
        changes = {
            "Head_enchant": ("补头部附魔", [p["head"]]),
            "Chest_enchant": ("补胸部附魔", [p["chest"]]),
            "Feet_enchant": ("补鞋部附魔", [p["feet"]]),
            "Empty_sockets": ("填三个现有空孔（项链第二孔＋双戒）", [p[s] for s in ("neck", "finger1", "finger2")]),
            "All_prepared": ("补齐三处附魔与三个现有空孔", [p[s] for s in SLOTS if p[s] != GEAR[s]]),
            "Craft_feet": ("331制造鞋替321鞋，不迁移美化", [craft("feet", 244569, embellish=False, enchant_id=7963)]),
            "Craft_waist": ("331制造腰替321腰（普通制造）", [craft("waist", 244573, embellish=False)]),
            "H4_ring": ("神话334邪恶炼金师指环替制造戒，保留原戒指宝石", [item("finger2", 268249, enchant_id=7967, gem_id=240908)]),
            "Both_raid_rings": ("334邪恶炼金师指环替虫群指环、保留制造戒（另一槽对照）", [item("finger1", 268249, enchant_id=7967, gem_id=240908)]),
            "New_tendril": ("334触须替334祖尔金饰品", [item("trinket2", 281215)]),
            "Myth_tier_shoulder": ("获取334同来源神话肩并化生（非直接升级）", [item("shoulder", 271517, redirected_base_stats=251146, enchant_id=8001)]),
            "Myth_tier_hands": ("获取334神话套装手", [item("hands", 271520)]),
            "Myth_tier_legs": ("获取334同来源神话腿并化生（非直接升级）", [item("legs", 271518, redirected_base_stats=251130, enchant_id=8159)]),
            "H7_waist": ("获取334神话H7腰", [item("waist", 268256)]),
            "Myth_shoulder_4pc": ("取得334神话目标肩并保留四件套", [tier_shoulder]),
            "Myth_shoulder_5pc": ("神话肩替英雄肩（五件套无额外收益）", [modify(tier_shoulder, redirected_base_stats=271517)]),
            "Current_shoulder_bonus_only": ("仅对比当前肩副属性，保持装备与装等", [current_set]),
        }
        emit(f"current-{mode}", mode, GEAR, changes, stage="current")
        # Only items actually present in bags, at their exported levels and bonuses.
        trinkets = {}
        for label, ident in (("Bag_321", 270164), ("Stone_321", 250228), ("Poison_321", 273796),
                             ("Feather_311", 159617), ("Essence_311", 250244), ("Order_311", 250225),
                             ("Fang_311", 270161), ("Ritual_305", 270162), ("Vendetta_298", 270166)):
            found = [(int(m[1]), m[2]) for m in re.findall(
                r"# ([^\n]+) \((\d+)\)\r?\n# trinket1=(.*)", RAW) if f"id={ident}," in m[2]]
            _, best = max(found)
            trinkets[label] = (f"背包饰品：{label}", ["trinket2=" + best])
        emit(f"bags-{mode}", mode, p, trinkets, stage="bags")


def target_base(placement="back_wrist", passive=270173):
    p = prepared()
    p.update({
        "head": item("head", 271519, redirected_base_stats=271875, bonus_id=13847, enchant_id=8017),
        "shoulder": item("shoulder", 271517, redirected_base_stats=268246, enchant_id=8001),
        "hands": item("hands", 251124),
        "waist": item("waist", 268256),
        "legs": item("legs", 271518, redirected_base_stats=268225, enchant_id=8159),
        "feet": item("feet", 251153, enchant_id=7963),
        "finger2": item("finger2", 268249, enchant_id=7967, gem_id=240908),
        "trinket2": item("trinket2", passive),
    })
    if placement == "wrist_feet":
        p["back"] = item("back", 268253)
        p["wrist"] = craft("wrist", 244576)
        p["feet"] = craft("feet", 244569, enchant_id=7963)
    elif placement == "back_feet":
        p["back"] = craft("back", 239656)
        p["wrist"] = item("wrist", 251135)
        p["feet"] = craft("feet", 244569, enchant_id=7963)
    return p


def targets():
    for mode in ("raid", "dungeon"):
        candidates = {}
        for placement in ("back_wrist", "wrist_feet", "back_feet"):
            for passive in (270173, 281215):
                gear = target_base(placement, passive)
                name = f"Target_{placement}_{passive}"
                candidates[name] = (f"终装：{placement}／饰品{passive}", list(gear.values()))
        emit(f"targets-{mode}", mode, prepared(), candidates, stage="target")


def refine():
    for mode in ("raid", "dungeon"):
        result = json.loads((ROOT / f"targets-{mode}.json").read_text(encoding="utf-8"))
        winner = max(result["sim"]["profilesets"]["results"], key=lambda row: row["mean"])["name"]
        placement, passive = winner.removeprefix("Target_").rsplit("_", 1)
        gear = target_base(placement, int(passive))
        candidates = {}
        crafted_slots = [slot for slot, line in gear.items() if "crafting_quality=5" in line]
        for pair, stats in (("CM", "32/49"), ("HM", "36/49"), ("CH", "32/36")):
            for flavor, flask in (("Crit", "shattered_sun"), ("Mastery", "magisters"), ("Haste", "blood_knights")):
                changes = []
                for slot in crafted_slots:
                    changes.append(recraft(gear[slot], stats))
                changes.append(f"flask=flask_of_the_{flask}_2")
                candidates[f"Stats_{pair}_{flavor}"] = (f"制造{pair}＋{flavor}合剂", changes)
        candidates["Gem_CH"] = ("两个空戒指孔改暴击急速，保留原有宝石孔", [modify(gear["finger2"], gem_id=240906)] +
                                         [modify(gear["neck"], gem_id="240983/240906")])
        candidates["Diamond_speed"] = ("主属性钻石改多色移速钻石", [modify(gear["neck"], gem_id="240967/240908")])
        candidates["Other_hands"] = ("H5手替密谋手", [item("hands", 268234)])
        candidates["Tier_hands"] = ("普通神话套装手替密谋手", [item("hands", 271520)])
        candidates["Owned_head"] = ("保持未化生头，改神话套装手维持四件", [prepared()["head"], item("hands", 271520)])
        candidates["Keep_craft_ring"] = ("保留331制造戒，替H4戒，沿用合适宝石", [modify(prepared()["finger2"], gem_id=240908)])
        candidates["Other_passive"] = ("换另一件334被动饰品", [item("trinket2", 281215 if passive == "270173" else 270173)])
        candidates["Elite_core"] = ("高手样本中的334守护者沸腾核心", [item("trinket2", 270165)])
        candidates["Ordinary_chest"] = ("移除H10胸效果，换普通神话套装胸", [item("chest", 271522, enchant_id=7987)])
        emit(f"refine-{mode}", mode, gear, candidates, iterations=2000, seed=24102026, stage="refine")
        (ROOT / f"target-base-{mode}.simc").write_text("\n".join(gear.values()) + "\n", encoding="utf-8")
        MANIFEST[f"refine-{mode}"]["family"] = winner


def verify():
    for mode in ("raid", "dungeon"):
        all_lines = (ROOT / f"refine-{mode}.simc").read_text(encoding="utf-8").splitlines()
        gear = {s: next(line for line in all_lines if line.startswith(s + "=")) for s in SLOTS}
        result = json.loads((ROOT / f"refine-{mode}.json").read_text(encoding="utf-8"))
        ranked = sorted(result["sim"]["profilesets"]["results"], key=lambda row: row["mean"], reverse=True)
        chosen = [r["name"] for r in ranked[:3]] + ["Other_passive", "Elite_core", "Keep_craft_ring", "Owned_head", "Ordinary_chest"]
        candidates = {}
        for name in dict.fromkeys(chosen):
            prefix = f'profileset."{name}"'
            changes = [re.sub(r"^profileset\.\"[^\"]+\"\+?=", "", line)
                       for line in all_lines if line.startswith(prefix + "=") or line.startswith(prefix + "+=")]
            candidates[name] = (MANIFEST[f"refine-{mode}"]["labels"][name], changes)
        candidates["Raw_current"] = ("最新实际装备（未补孔附魔）", list(GEAR.values()))
        candidates["Prepared_current"] = ("现装补齐孔附魔", list(prepared().values()))
        emit(f"verify-{mode}", mode, gear, candidates, iterations=6500, seed=25102026, stage="verify")
        # Keep downloads and the displayed target tied to the exact verified baseline.
        lines = (ROOT / f"verify-{mode}.simc").read_text(encoding="utf-8").splitlines()
        (ROOT / f"recommended-{mode}.simc").write_text(
            "\n".join(line for line in lines if not line.startswith("profileset.")) + "\n", encoding="utf-8")


def practical():
    for mode in ("raid", "dungeon"):
        p = prepared()
        candidates = {
            "Raw_current": ("最新实际装备（未补孔附魔）", list(GEAR.values())),
            "Craft_feet_CM": ("普通331制造鞋，暴击精通", [craft("feet", 244569, embellish=False, enchant_id=7963)]),
            "Craft_waist_CM": ("普通331制造腰，暴击精通", [craft("waist", 244573, embellish=False)]),
            "Craft_both_CM": ("普通331制造鞋＋腰，均暴击精通", [craft("feet", 244569, embellish=False, enchant_id=7963),
                                                                     craft("waist", 244573, embellish=False)]),
            "Craft_both_HM": ("普通331制造鞋＋腰，均急速精通", [craft("feet", 244569, stats="36/49", embellish=False, enchant_id=7963),
                                                                     craft("waist", 244573, stats="36/49", embellish=False)]),
            "Craft_both_CH": ("普通331制造鞋＋腰，均暴击急速", [craft("feet", 244569, stats="32/36", embellish=False, enchant_id=7963),
                                                                     craft("waist", 244573, stats="32/36", embellish=False)]),
            "Craft_ring_CM": ("重做制造戒为暴击精通", [craft("finger2", 240949, stats="32/49", embellish=False,
                                                                   enchant_id=7967, gem_id=240908)]),
            "Recraft_back_wrist_CM": ("保留原美化ID，重造披风护腕为暴击精通", [recraft(p["back"], "32/49"), recraft(p["wrist"], "32/49")]),
            "Recraft_back_wrist_HM": ("保留原美化ID，重造披风护腕为急速精通", [recraft(p["back"], "36/49"), recraft(p["wrist"], "36/49")]),
            "Gem_CH": ("三个现有空孔选暴击急速", [modify(p["neck"], gem_id="240983/240906"),
                                                              modify(p["finger1"], gem_id=240906), modify(p["finger2"], gem_id=240906)]),
            "Bag_321": ("321无底袋替334祖尔金", ["trinket2=,id=270164,bonus_id=6652/13334/12846,content_tuning=7359"]),
            "H4_ring": ("334邪恶炼金师指环替制造戒，与虫群指环同时佩戴", [item("finger2", 268249, enchant_id=7967, gem_id=240908)]),
            "New_tendril": ("获取334扭曲恐兽触须", [item("trinket2", 281215)]),
            "Both_raid_rings": ("H4戒替虫群指环、保留331制造戒（另一槽对照）", [item("finger1", 268249, enchant_id=7967, gem_id=240908)]),
        }
        emit(f"practical-{mode}", mode, p, candidates, iterations=6000, seed=26102026, stage="practical")


def budget_upgrade():
    # Compare the same 10-stone budget both now and after acquiring the target set.
    recommended()
    for mode in ("raid", "dungeon"):
        lines = (ROOT / f"recommended-{mode}.simc").read_text(encoding="utf-8").splitlines()
        target = {line.split("=", 1)[0]: line for line in lines if line.split("=", 1)[0] in SLOTS}
        for context, base in (("current", prepared()), ("target", target)):
            passive = "H10扭曲恐兽触须" if "id=281215," in base["trinket2"] else "H7祖尔金饰品"
            options = {
                "Weapon_341": ("H8长柄334→341", "main_hand"),
                "Neck_341": ("H8项链334→341", "neck"),
                "Heart_341": ("H8乌拉特克之心334→341", "trinket1"),
                "Mode_trinket_341": (passive + "334→341", "trinket2"),
            }
            # Preserve proc bonuses; the older DBC does not know the Oct 23 level rule.
            candidates = {name: ("消耗10枚晋升毒液石：" + label, [modify(base[slot], ilevel=341)])
                          for name, (label, slot) in options.items()}
            key = f"budget-upgrade-{'current-' if context == 'current' else ''}{mode}"
            emit(key, mode, base, candidates, iterations=6500, seed=28102026, stage="upgrade")
            MANIFEST[key]["context"] = context


def recommended():
    for mode in ("raid", "dungeon"):
        result = json.loads((ROOT / f"verify-{mode}.json").read_text(encoding="utf-8"))["sim"]
        combat = result["players"][0]["collected_data"]["dps"]
        winner = max(result["profilesets"]["results"], key=lambda row: row["mean"])
        half_width = math.hypot(winner["mean_error"], 1.96 * combat["mean_std_dev"])
        selected = winner["name"] if winner["mean"] - combat["mean"] > half_width else None
        lines = (ROOT / f"verify-{mode}.simc").read_text(encoding="utf-8").splitlines()
        base = [line for line in lines if not line.startswith("profileset.")]
        if selected:
            prefix = f'profileset."{selected}"'
            changes = [re.sub(r'^profileset\."[^"]+"\+?=', "", line) for line in lines
                       if line.startswith(prefix + "=") or line.startswith(prefix + "+=")]
            for change in changes:
                key = change.split("=", 1)[0]
                base = [line for line in base if line.split("=", 1)[0] != key]
                base.append(change)
        (ROOT / f"recommended-{mode}.simc").write_text("\n".join(base) + "\n", encoding="utf-8")
        MANIFEST[f"recommended-{mode}"] = {"mode": mode, "selected": selected or "Baseline",
                                             "family": MANIFEST[f"refine-{mode}"]["family"]}


def weapons():
    for mode in ("raid", "dungeon"):
        gear = prepared()
        candidates = {"Polearm_341": ("已拥有长柄341（10石）", [modify(gear["main_hand"], ilevel=341)]),
                      "Craft_neck_337": ("普通制造项链337替H8项链（10石；无毒咒）", [
                          modify(craft("neck", 240950, embellish=False, level=337, gem_id="240983/240908"), bonus_id=13668)])}
        for level, budget in ((334, "无毒液石"), (341, "10石")):
            main = item("main_hand", 268209, level, enchant_id=8689)
            for off_id in (268206, 270930):
                candidates[f"Dual_{level}_{off_id}"] = (f"团本单手剑{level}＋副手{off_id}334（{budget}）", [
                    main, item("off_hand", off_id, 334, enchant_id=8689)])
        candidates["Dual_myth_341"] = ("双神话单手均341（20石；与10石预算不等价）", [
            item("main_hand", 268209, 341, enchant_id=8689), item("off_hand", 270930, 341, enchant_id=8689)])
        main = item("main_hand", 268209, 334, enchant_id=8689)
        for stats in ("32/49", "36/49", "32/36"):
            off = craft("off_hand", 237839, stats=stats, embellish=False, level=337, enchant_id=8689)
            candidates[f"Craft_off_{stats.replace('/', '_')}"] = (f"神话单手334＋制造副手337、属性{stats}（10石；保留双奥纹）", [main, off])
            # A ritual-stone weapon consumes one embellishment; remove one armor lining.
            candidates[f"Ritual_off_{stats.replace('/', '_')}"] = (f"神话单手334＋仪式石制造副手337、属性{stats}（10石；单奥纹）", [
                main, modify(off, bonus_id=13771), modify(gear["back"], bonus_id="/".join(
                    bonus for bonus in re.search(r"bonus_id=([^,]+)", gear["back"])[1].split("/") if bonus != "12384"))])
        for name, (_, changes) in candidates.items():
            if name.startswith(("Dual_", "Craft_off_", "Ritual_off_")):
                changes.append("temporary_enchant=main_hand:thalassian_phoenix_oil_2/off_hand:thalassian_phoenix_oil_2")
        emit(f"weapons-{mode}", mode, gear, candidates, iterations=3500, seed=29102026, stage="weapons")


def unbuffed():
    disabled = {"flask", "food", "augmentation", "potion", "temporary_enchant",
                "optimal_raid", "override.bloodlust", "iterations"}
    for mode in ("raid", "dungeon"):
        lines = (ROOT / f"recommended-{mode}.simc").read_text(encoding="utf-8").splitlines()
        lines = [line for line in lines if line.split("=", 1)[0] not in disabled]
        lines += ["optimal_raid=0", "override.bloodlust=0", "iterations=30"]
        lines += [f"{key}=disabled" for key in ("flask", "food", "augmentation", "potion", "temporary_enchant")]
        (ROOT / f"unbuffed-{mode}.simc").write_text("\n".join(lines) + "\n", encoding="utf-8")


def simc_summary(mode, stage):
    prefix = {"upgrade": "budget-upgrade", "upgrade-current": "budget-upgrade-current"}.get(stage, stage)
    path = ROOT / f"{prefix}-{mode}.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    player = result["sim"]["players"][0]
    combat = player["collected_data"]["dps"]
    baseline = combat["mean"]
    label = {"verify": "目标套装高迭代复测", "practical": "当前装备：零R币改进", "target": "完整候选套装初筛",
             "targets": "完整候选套装初筛", "current": "当前装备：附魔与空孔", "bags": "背包饰品对照",
             "upgrade": "目标套装：10枚毒液石选择（341显式覆盖）",
             "upgrade-current": "当前装备：10枚毒液石选择（341显式覆盖）",
             "weapons": "当前装：长柄／双持／337制造副手（显式装等覆盖）"}.get(stage, stage)
    summary = {"key": path.stem, "mode": mode, "stage": stage, "label": label,
               "baseline": baseline, "stderr": combat["mean_std_dev"],
               "iterations": result["sim"]["options"]["iterations"], "seed": result["sim"]["options"]["seed"],
               "model": result["sim"]["options"]["fight_style"], "seconds": result["sim"]["options"]["max_time"],
               "results": []}
    if stage.startswith("upgrade"):
        summary["note"] = "基准为" + ("当前装备补齐孔附魔" if stage == "upgrade-current" else "上方推荐目标套装") + "；每个候选只强化一件、均消耗10石。新装等为截图规则的显式覆盖，不代表引擎已更新。"
    data = MANIFEST.get(summary["key"], {})
    for row in result["sim"].get("profilesets", {}).get("results", []):
        summary["results"].append({"name": row["name"], "label": data.get("labels", {}).get(row["name"], row["name"]),
                                   "mean": row["mean"], "error": row["mean_error"],
                                    "provisional": stage.startswith("upgrade") or stage == "weapons" or mode == "dungeon" and (stage in ("targets", "verify") or "tendril" in row["name"].lower())})
    return summary


def elite_sample_data():
    return {
        "retrieved_at": "2026-10-23",
        "mythic_plus": {"logs": 796, "characters": 172, "period": "最近两周；+20 至 +23"},
        "raid": {"logs": 896, "characters": 343, "period": "最近三周；神话团本"},
        "note": "按职业筛选的高分日志装备出现率；同角色可有多份日志，双饰品等槽位百分比不相加。两／三周窗口横跨版本和热更，并非仅12.1.5第二周样本；不等于该装备导致高分。页面未提供逐角色bonus/化生前驱，故不推断保留特效。",
        "items": [
            {"slot": "主手：乌拉特克长柄", "id": 268215, "mythic_plus": 99.2, "raid": 95.5},
            {"slot": "项链：亚基克星藏骨匣", "id": 268265, "mythic_plus": 97.0, "raid": 94.9},
            {"slot": "饰品：乌拉特克贪婪之心", "id": 270175, "mythic_plus": 99.9, "raid": 99.2},
            {"slot": "饰品：祖尔金处斩技法", "id": 270173, "mythic_plus": 37.8, "raid": 71.0},
            {"slot": "饰品：Keeper's Seething Core", "id": 270165, "mythic_plus": 25.1, "raid": 16.4},
            {"slot": "饰品：扭曲恐兽触须", "id": 281215, "mythic_plus": 17.1, "raid": 4.8},
            {"slot": "制造：银月城特工偏斜腕甲", "id": 244576, "mythic_plus": 85.9, "raid": 74.1},
            {"slot": "制造：银月城特工便鞋", "id": 244569, "mythic_plus": 83.2, "raid": 84.2},
            {"slot": "制造：精工辛多雷指环", "id": 240949, "mythic_plus": 44.3, "raid": 47.4},
            {"slot": "制造披风", "id": 239656, "mythic_plus": 30.2, "raid": 21.0},
            {"slot": "团本披风", "id": 268253, "mythic_plus": 27.1, "raid": 36.4},
            {"slot": "套装手套", "id": 271520, "mythic_plus": 75.5, "raid": 72.1},
            {"slot": "套装头", "id": 271519, "mythic_plus": 90.6, "raid": 89.3},
        ],
    }


def report_data():
    source = json.loads((ROOT / "report-items.json").read_text(encoding="utf-8"))
    source.setdefault("270165", {"name": "Keeper's Seething Core", "source": "高分样本候选；名称来自本地SimC官方DBC"})
    snapshot = json.loads((ROOT.parents[1] / "snapshots/2026-10-23.items.json").read_text(encoding="utf-8"))
    equipped = json.loads((ROOT / "current-raid.json").read_text(encoding="utf-8"))
    dbc = equipped["sim"]["options"]["dbc"]
    for entry in snapshot["items"]:
        if entry["error"]:
            continue
        source_item = source.get(str(entry["item_id"]), {})
        source_item["upgrade_text"] = entry["upgrade_text"]
        source_item["item_level"] = entry["item_level"]
    items = {key: {**value, "tooltip": re.sub(r"<[^>]+>", " ", value.get("tooltip") or "")
                   .replace("&nbsp;", " ").replace("\\b", " ")}
             for key, value in source.items()}
    raw = SNAPSHOT.read_text(encoding="utf-8-sig")
    current_gear = []
    for slot in SLOTS:
        line = GEAR[slot]
        fields = dict(part.split("=", 1) for part in line.split("=", 1)[1].split(",") if "=" in part)
        entry = next(item for item in snapshot["items"] if item["slot"] == slot)
        owned = slot in ("head", "neck", "chest", "finger1", "trinket1", "trinket2", "main_hand")
        source_text = "当前装备 · " + entry["upgrade_text"] if entry["upgrade_text"] else "当前装备"
        current_gear.append({"slot": slot, "id": entry["item_id"], "ilevel": entry["item_level"],
                             "bonus_id": fields.get("bonus_id"), "gem_id": fields.get("gem_id"),
                             "enchant_id": fields.get("enchant_id"), "crafted_stats": fields.get("crafted_stats"),
                             "redirected_base_stats": fields.get("redirected_base_stats"), "owned": True,
                             "source": source_text, "note": "R币获取已确认" if owned else None})
    profiles = {}
    for mode in ("raid", "dungeon"):
        data = json.loads((ROOT / f"recommended-{mode}.json").read_text(encoding="utf-8"))
        filename = ROOT / f"recommended-{mode}.simc"
        profile_raw = filename.read_text(encoding="utf-8")
        lines = [line for line in profile_raw.splitlines() if re.match(rf"^({'|'.join(SLOTS)})=", line)]
        profile_gear = []
        for line in lines:
            slot = line.split("=", 1)[0]
            fields = dict(part.split("=", 1) for part in line.split("=", 1)[1].split(",") if "=" in part)
            ident = int(fields["id"])
            result_slot = {"shoulder": "shoulders", "wrist": "wrists"}.get(slot, slot)
            expected = data["sim"]["players"][0]["gear"][result_slot]["ilevel"]
            current_item = next(row for row in snapshot["items"] if row["slot"] == slot)
            is_owned = ident == current_item["item_id"] and expected == current_item["item_level"]
            note = "已拥有物品；属性／孔附魔可能需重造补齐" if is_owned else "未获取的目标；英雄轨道护甲不能直接用纹章升为神话"
            if fields.get("redirected_base_stats") == str(current_item["item_id"]) and expected == current_item["item_level"] and not is_owned:
                note = "已拥有对应装等前驱，目标需化生；本次导出充能0，不是建议再R一次同物品"
            if fields.get("redirected_base_stats"):
                note += f"；化生前驱ID {fields['redirected_base_stats']}，保留来源属性／词缀"
            profile_gear.append({"slot": slot, "id": ident,
                                 "ilevel": expected, "bonus_id": fields.get("bonus_id"),
                                 "gem_id": fields.get("gem_id"), "enchant_id": fields.get("enchant_id"),
                                 "crafted_stats": fields.get("crafted_stats"),
                                 "redirected_base_stats": fields.get("redirected_base_stats"), "owned": is_owned,
                                 "source": fields.get("source"),
                                 "note": note})
        data_json = data["sim"]
        stats = data_json["players"][0]["collected_data"]["buffed_stats"]["stats"]
        unbuffed = json.loads((ROOT / f"unbuffed-{mode}.json").read_text(encoding="utf-8"))
        unbuffed_stats = unbuffed["sim"]["players"][0]["collected_data"]["buffed_stats"]["stats"]
        profiles[mode] = {"raw": profile_raw, "gear": profile_gear,
                          "family": MANIFEST[f"refine-{mode}"]["family"],
                          "selected": MANIFEST[f"recommended-{mode}"]["selected"],
                          "note": "本次复测选择：" + MANIFEST[f"recommended-{mode}"]["selected"] + "。仅当候选对基准的近似差值区间全为正时才替换；不是全局最优或正式显著性检验。毒液石升级另见对照，这里仍是强化前334/331。" +
                                  ("团本保留现有披风／护腕双美化。" if mode == "raid" else "披风／护腕、护腕／鞋、披风／鞋三族初筛接近，不能按点估计排名认定唯一位置；护腕／鞋为高手常用可选路线。"),
                          "stats": {key: unbuffed_stats[key] for key in ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")},
                          "stats_context": "禁用合剂、食物、符文、药水、武器油及团队增益后的SimC快照；保留角色被动／天赋，不等同游戏内手工抄面板。",
                          "buffed_stats": {key: stats[key] for key in ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")},
                          "consumables": {key: data_json["players"][0][key] for key in ("flask", "food", "augmentation", "potion", "temporary_enchant")}}
    history = [
        {"activity": "H8 英雄", "items": [271875, 268265, 270175, 268215], "scope": "本次用户确认上述H8神话装备均为R币所得；历史样本确认项链268265是2026-10-01 prior roll，earlier record对H8计入排除"},
        {"activity": "H7 英雄", "items": [270173], "scope": "按本次用户确认记录该已拥有饰品的R币来源；对后续同难度排除需以现行角色预览为准"},
        {"activity": "H10 / Kith'ix 英雄", "items": [281029, 281236], "scope": "按本次用户确认记录戒指与被化生胸甲来源；当前难度排除和拾取专精范围待当前预览"},
    ]
    artifact = {
        "meta": {"date": "2026-10-23", "patch": "12.1.5 第二周", "character": "沙僧 · 国服贫瘠之地", "engine_commit": "73a372b761", "wow_version": "12.1.5.70529 Live", "hotfix_date": "2026-10-22（引擎数据；毒液石新规则来自10月23日用户截图）", "budget": 0,
                 "average_ilevel": snapshot["equipped_average"], "catalyst_charges": 0, "empty_sockets": "项链第二孔、两枚戒指各一孔（头／腰／腕无孔）",
                 "armor_upgrade_track": "5件321护甲均为英雄6/6，不能用纹章再升；模拟终装使用334神话来源掉落后再化生",
                 "upgrade_materials": "10枚晋升毒液石：10月23日热更后神话334→341、最高品质制造331→337；仅测试截图/官方规则涵盖的武器、饰品、项链类别。344装等无法强化；SimC数据截止10月22日，候选用ilevel=341显式建模而非伪造新bonus ID",
                 "scope": "当前装比较以当日原始导出与受控假设为准；正式装测试是可达候选族，不是唯一BiS。所有包项用皮甲专精和保留神话词缀。",
                 "snapshot": {"equipped_average": snapshot["equipped_average"], "empty_sockets": "亚基克星藏骨匣第二孔、两戒指各一孔；原有孔位宝石不作覆盖；其他装备逐件tooltip无孔", "upgrades": "肩/手/腰/腿/鞋英雄6/6，装等321；H8四件头/项链/长柄/饰品均334神话6/6；H7饰品334神话6/6；H10虫群指环334神话6/6；H10胸特效已化生保留 bonus 14049；制造披风331 8790+美化，护腕331 8791+美化，戒指331 8790（普通制造）", "tokens": "R币0；纹章余量按用户导出货币ID 3444:44、3446:305；毒液石10（item 280562）；潮汐火花6（item 274476）", "catalyst": "0", "user_history": "用户确认H7/H8/H10全部列入角色当前装备的对应神话物品均来自R币；具体滚取日期和历史全量覆盖未确认"}},
        "current": {"raw": raw, "gear": current_gear}, "profiles": profiles, "items": items,
        "roll_history": history,
        "elite_samples": elite_sample_data(),
        "runs": [simc_summary(mode, stage) for stage in ("current", "practical", "targets", "verify", "upgrade-current", "upgrade", "weapons")
                 for mode in ("raid", "dungeon")],
        "conclusions": ["本周R币为0。H8/H7/H10当前装备中，用户确认的神话物品均为R币所得；只有这些实际已R物品列入排除，仍须进游戏确认当前难度奖励预览。神话纹章上限解除不等于R币可重复ROLL。", "实战样本显示团本主流双饰品为乌拉特克之心＋祖尔金；大米高分样本触须出现率更高但仍低于心/祖尔金。个人模拟将其分内容：团本优先测祖尔金，钥石测触须；触须收益仍受实际换目标节奏影响。", "高分样本与本次候选配装一致支持H8长柄/项链/心、套装四件及腕/鞋制造；样本饰品频率是实战选择，不证明因果或替代个人模拟。", "本次高迭代复测以当日角色种族/天赋和团队模型比较。团本与大米分别使用不同饰品目标；窄幅差异按抽样误差视为备选，不称唯一BiS。", "10月23日截图规则为神话334→341、最高品质制造331→337；毒液石每10枚强化一件，344不可升。按最新SimC数据明确覆盖目标物品装等模拟，但引擎本身仍是10月22日数据库。", "毒液石官方适用范围与截图列明的武器、饰品、项链相符。角色现有331披风/护腕/戒指不因装等达到331就自动具备资格；请以奥林与化生台预览为准。"],
        "routes": [
            {"boss": "兑换／造装／强化：本周先做不花R币的确定项", "priority": "立即", "targets": [], "excluded": [], "spec": "制造／现有装备", "note": "R币0；现有10枚晋升毒液石足够强化一件合资格物品。先补附魔与三个空孔，再比较制造属性和331鞋腰过渡。", "stop": "神话纹章解限仍不改变英雄321护甲的升级轨道。按本页当前装毒液石比较选择武器／项链／饰品；护腕、鞋、制造戒指不在官方毒液石适用槽位。"},
            {"boss": "H8 · Ula'tek／乌拉特克", "priority": "已R出的核心装备", "targets": [271875,268265,270175,268215], "excluded": [271875,268265,270175,268215], "spec": "踏风；进游戏核对奖励预览", "note": "四件H8神话当前装均为用户确认的R币所得：毒咒头、项链、乌拉特克之心、长柄。此次均记录为已R排除；其他未列出/未拥有掉落不自动排除。", "stop": "除非奖励预览显示其他明确升级目标，否则不再为这四件开H8币池。"},
            {"boss": "H7 · The Coiled Altar", "priority": "按大米与单体分流", "targets": [268253,268256,268225,270173], "excluded": [270173], "spec": "踏风；按本周角色预览", "note": "仅披风、腰、腿尚未确认；334 H7饰品已由R币获得。大米最佳备选是H10触须，单体保留H7饰品。", "stop": "拿到所需目标后暂停；不要因饰品旧名将Boss误标祖尔金。"},
            {"boss": "H10／新团队副本 · Kith'ix／基希克斯", "priority": "只剩触须待比较", "targets": [281029,281215,281236], "excluded": [281029,281236], "spec": "踏风；按当前预览", "note": "戒指281029已R出且装等334；胸281236已R出后化生为美猴王套胸，保留bonus 14049。触须281215本次未拥有；其大米模型收益暂定，先等正常掉落／低保／确认奖励预览。", "stop": "先看触须能否自然获取；R币归零后等后续实际余额再评估，不把神话纹章解限误算成R币有余额。"},
            {"boss": "Vashnik the Malignant（旧资料简称H4需核对）", "priority": "第一只剩余有效目标池", "targets": [268249,268246], "excluded": [], "spec": "踏风／按预览", "note": "331制造戒到334邪恶炼金师戒模型提升较大，并会与已拥有H10戒指同时佩戴；Boss数字不要只依据H4书写。肩为套装前驱/四件套选项。", "stop": "达到神话肩/四件套需求并换上戒指后停止为重复槽位花R币。"},
            {"boss": "H7 / The Coiled Altar 护甲池", "priority": "神话腰先于已接近的套装肩手腿", "targets": [268256,268253,268225,270173], "excluded": [270173], "spec": "踏风", "note": "装备有很好的化生胸但0充能；落下的高阶皮甲护甲可补升阶轨道缺口。腰带强于英雄321腰是本次中等迭代对比稳定发现。", "stop": "鞋腰可用331潮汐制造填补，披风/护腕现有双美化尽量保留，实际物品池须看预览。"}
        ],
        "sources": [
            {"title": "12.1.5 国服开放与晋升毒液石、取消纹章上限", "url": "https://wow.blizzard.cn/news/24307306/", "note": "官方公告：10枚用于已满级英雄／神话或最高品质潮汐制造武器、饰品或项链；任务/游戏预览另核。"},
            {"title": "12.1 团本R币规则与成本", "url": "https://wow.blizzard.cn/news/24293281/index.html", "note": "第2赛季每次团本奖励花1币。"},
            {"title": "12.1.5 国服Hotfix", "url": "https://worldofwarcraft.blizzard.com/en-us/news/24307310/hotfixes-october-16-2026", "note": "10月21日修复奖励预览未更新显示，仅是UI修复不改变资格。"},
            {"title": "10月23日晋升毒液石热更截图（用户提供）", "url": "reference-hotfix-2026-10-23.png", "note": "截图明确记载神话334→341、最高品质制造331→337、每件消耗10枚及344无法升级；模拟以ilevel=341覆盖旧引擎数据。"},
            {"title": "12.1.5高分大秘境踏风装备分布", "url": "https://mythicstats.com/spec/windwalker-monk", "note": "检索于2026-10-23；页面样本为最近两周796份+20至+23日志、172名角色。"},
            {"title": "12.1.5神话团本踏风装备分布", "url": "https://mythicstats.com/raid/spec/windwalker-monk", "note": "检索于2026-10-23；页面样本为最近三周896份神话团本日志、343名角色。"},
            {"title": "晋升毒液石官方适用规则", "url": "https://wow.blizzard.cn/news/24307306/", "note": "官方公告列明每10枚用于完全升级的英雄/神话装备或最高品质潮汐制造武器、饰品、项链。最新精确等级另以用户提供的10月23日热更截图为准。"},
            {"title": "基希克斯团队本掉落", "url": "https://www.wowhead.com/guide/midnight/raids/the-unbinding-of-kithix-boss-strategy-abilities-rewards", "note": "只作物品来源辅助，实战难度剩余池以游戏预览为准。"},
            {"title": "毒咒触须官方SimC实现", "url": "https://github.com/simulationcraft/simc/blob/midnight/engine/player/unique_gear_midnight.cpp#L4818", "note": "含每个首次新目标触发3层实现。"},
            {"title": "H4戒指来源（Vashnik）", "url": "https://www.wowhead.com/item=268249/vile-alchemists-band", "note": "避免仅用不稳定H4编号判断Boss。"},
            {"title": "当前SimC数据构建", "url": "https://github.com/simulationcraft/simc/commit/73a372b761", "note": "用户工作区实际 E:/github/simc commit。"},
            {"title": "历史WCL样本原始记录", "url": "../2026-10-10/wcl-top5-evidence.json", "note": "用户2026-10-10提供5份导出，被描述为M+前五；排名口径、时期、分数未经独立验证。本次没有新WCL日志。"},
            {"title": "本次样本备注", "url": "../2026-10-10/wcl-top5-review.md", "note": "10月10日用户提供的五份WCL配装快照仅作为另一组历史实装交叉核查，未独立验证排名。"}
        ],
        "limitations": ["SimC model: current client state exported 2026-10-23; engine DBC is 12.1.5.70529 Live/2026-10-22 hotfix; revision 73a372b761. Oct 23 item-level hotfix is newer than engine data; eligible upgrade comparisons override ilevel to 341 without asserting the DBC knows the new upgrade bonus. Talents/race/party/consumables stay controlled within each run.",
                        "DungeonSlice is a fixed model, not 沙僧实际钥石路线；新目标触发物品价值会随拉怪与换目标节奏变，触须Aoe收益属于暂定。", "SimC marks Battle Gi of the Monkey King (new chest) and Band of the Swarmcaller (ring) AoE damage as unsplit assumptions. No PTR-only AoE factor should be treated as verified live performance.", "H10胸毒咒15%加成当前代码明确说bugs=1（模拟游戏实际 bug）时尚不加，非游戏内已确认机制。", "当前导出英雄头/肩/胸/腕/手/腰/腿/鞋有5件321护甲实为肩手腰腿鞋，均英雄6/6满级，不能直接升级为334；模拟神话护甲、可化生目标属于可达候选，不是本周已在背包内装备。", "该次patch更新后，SimC模型间各自独立随机；95%区间是显示均值误差的独立近似，差值区间不是paired seed和正式显著性检验，不应按小数微胜下结论。", "本次报告是装备和R币计划，不分析完整事件WCL。10月10日的五份历史WCL SimC导出非新一周实况。", "R币排除范围、当前拾取专精、当前难度奖励预览和缓存清空/刷新状态不明。记录历史用户确认的R币来源，但不自动把全部已拥有装备视为当前奖励池都排除；登录后核对角色奖励预览。", "模拟目标用331潮汐制造替换英雄321护甲；1件晋升毒液石不可强化护甲。331最高品质潮汐腰未模拟毒液石升阶；请预览确认且还需任务链。", "本周R币0枚，花费不会被历史记录或用户另一角色的周报建议覆盖。"]
    }
    decisions = []
    for mode in ("raid", "dungeon"):
        run = next(row for row in artifact["runs"] if row["mode"] == mode and row["stage"] == "upgrade-current")
        ranked = sorted(run["results"], key=lambda row: row["mean"], reverse=True)
        best, second = ranked[:2]
        stable = best["mean"] - second["mean"] > math.hypot(best["error"], second["error"])
        decisions.append(f"{'团本' if mode == 'raid' else '大米'}当前装备10石选择：{best['label']}，相对补齐孔附魔基准约+{(best['mean'] / run['baseline'] - 1) * 100:.2f}%；" +
                         ("领先次选超过本批近似均值差误差。" if stable else "与次选差异仍在近似误差内，不强行认定唯一优先。") + "旧DBC建模，实装后仍须复核。")
    artifact["conclusions"] = decisions + artifact["conclusions"]
    practical = {mode: next(row for row in artifact["runs"] if row["mode"] == mode and row["stage"] == "practical") for mode in ("raid", "dungeon")}
    gains = []
    for key, label in (("Craft_ring_CM", "现有制造戒重造暴击精通"), ("Craft_both_CM", "331普通暴击精通鞋＋腰过渡"), ("Recraft_back_wrist_CM", "现有披风＋护腕重造暴击精通，保留双奥纹")):
        values = []
        for mode in ("raid", "dungeon"):
            run = practical[mode]
            row = next(row for row in run["results"] if row["name"] == key)
            values.append(f"{'团本' if mode == 'raid' else '大米'}+{(row['mean']/run['baseline']-1)*100:.2f}%")
        gains.append(label + "：" + "／".join(values))
    artifact["conclusions"].insert(2, "不花R币的当前装改进（均与补孔附魔基准比，不可相加）：" + "；".join(gains) + "。需金币／火花等资源，制造戒在取得目标神话戒后会被替换，按过渡周期决定是否投入。")
    artifact["conclusions"].append("制造属性按完整bonus核对：8790等missive可能覆盖导出crafted_stats；本次有效重造测试移除旧missive、保留12384奥纹美化。不要直接按原始crafted_stats文字判断游戏实际绿字。")
    artifact["conclusions"].append("武器另测了双神话单手、337普通制造副手和337仪式石副手；在本角色其余现装不变时，都没有超过341乌拉特克长柄。今天不建议为改双持而花10石或追逐新单手；这不是所有角色、所有配装的普遍结论。")
    # Put actionable future pools before the already exhausted H8 core targets.
    routes = artifact["routes"]
    artifact["routes"] = [routes[index] for index in (0, 4, 2, 3, 1)]
    artifact["limitations"] += ["高分日志窗口跨最近两／三周，横跨12.1.5开放和毒液石热更；不能当作热更后专属人群。大米样本也包含核心270165（25.1%）和无底袋270164（16.8%）；本次另测核心，不只挑支持触须结论的样本。", "武器对比保留当前其余装备与双手附魔／武器油。337普通制造副手保留双奥纹；337仪式石副手移除一件护甲奥纹，保证只有两个美化。双神话341需要20石，不能用其DPS直接决定今天10石花在哪。"]
    data = json.dumps(artifact, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = (ROOT / "dashboard.template.html").read_text(encoding="utf-8")
    if template.count("__REPORT_DATA__") != 1:
        raise ValueError("Dashboard template must contain exactly one data placeholder.")
    (ROOT / "dashboard.html").write_text(template.replace("__REPORT_DATA__", data), encoding="utf-8")
    summary = {"checked_at": datetime.now().astimezone().isoformat(timespec="seconds"), "simc_revision": "73a372b761",
               "wow_version": dbc["Live"]["wow_version"], "hotfix_date": dbc["Live"]["hotfix_date"],
               "item_level_hotfix": {"date": "2026-10-23", "source": "用户截图", "mythic": 341, "crafted": 337,
                                     "model": "preserve bonuses and override ilevel; not native DBC support"},
               "profiles": profiles, "elite_samples": elite_sample_data(), "runs": artifact["runs"]}
    (ROOT / "study-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = ["# 沙僧：12.1.5第二周配装复核", "", "日期：2026-10-23。使用最新原始导出及本地SimC 73a372b761，数据库热修2026-10-22。", "",
                "## 先执行", ""] + ["- " + text for text in artifact["conclusions"]] + ["", "## 关键模拟", "",
                "每批只与本批基准比较；误差为候选均值95%半宽。不同模型绝对DPS不能横比，收益不可相加。", ""]
    for run in artifact["runs"]:
        if run["stage"] not in ("practical", "verify", "upgrade-current", "upgrade", "weapons"):
            continue
        markdown += [f"### {'团本' if run['mode'] == 'raid' else '大米'} / {run['label']}", "",
                     f"基准：{run['baseline']:.2f} DPS；{run['iterations']}次，种子{run['seed']}，{run['model']} {run['seconds']}秒。", "",
                     "| 候选 | DPS | 相对基准 | 均值误差 |", "|---|---:|---:|---:|"]
        for row in sorted(run["results"], key=lambda row: row["mean"], reverse=True):
            markdown.append(f"| {row['label']} | {row['mean']:.2f} | {(row['mean']/run['baseline']-1)*100:+.2f}% | ±{row['error']:.2f} |")
        markdown.append("")
    markdown += ["## 获取路线", ""] + [f"- {row['boss']}：{row['note']} 停止条件：{row['stop']}" for row in artifact["routes"]]
    markdown += ["", "## 边界", ""] + ["- " + text for text in artifact["limitations"]]
    markdown += ["", "## 来源", ""] + [f"- [{row['title']}]({row['url']})：{row['note']}" for row in artifact["sources"]]
    (ROOT / "recommendation.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("initial", "targets", "refine", "verify", "practical", "budget-upgrade", "weapons", "unbuffed", "report"))
    args = parser.parse_args()
    {"initial": initial, "targets": targets, "refine": refine, "verify": verify, "practical": practical,
     "budget-upgrade": budget_upgrade, "weapons": weapons, "unbuffed": unbuffed, "report": report_data}[args.stage]()
    MANIFEST_PATH.write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
