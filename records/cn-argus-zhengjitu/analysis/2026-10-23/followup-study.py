"""Compare the user's immediate shoulder and two-coin route alternatives."""

import argparse
import json
import math
import runpy
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
study = runpy.run_path(str(ROOT / "build-study.py"))


def prepare():
    p = study["prepared"]()
    craft, item, modify = (study[key] for key in ("craft", "item", "modify"))
    double = dict(p)
    bonuses = study["fields"](p["back"])["bonus_id"].split("/")
    double["back"] = modify(p["back"], bonus_id="/".join(bonus for bonus in bonuses if bonus != "12715") + "/12384")
    double["main_hand"] = item("main_hand", 271092, enchant_id=8689)
    double["off_hand"] = item("off_hand", 268196)
    candidates = {
        "Shoulder_CH": ("331普通制造肩：暴击急速，保留现有头胸手腿四件", [craft("shoulder", 244580, stats="32/36", enchant_id=8001)]),
        "Shoulder_CM": ("331普通制造肩：暴击精通，保留现有头胸手腿四件", [craft("shoulder", 244580, stats="32/49", enchant_id=8001)]),
        "Shoulder_HM": ("331普通制造肩：急速精通，保留现有头胸手腿四件", [craft("shoulder", 244580, stats="36/49", enchant_id=8001)]),
        "Shoulder_H7": ("H7神话334游魂护肩化生；需获取", [item("shoulder", 271481, redirected_base_stats=268231, enchant_id=8001)]),
        "H3_owned_dagger": ("H3盾334＋背包已有匕首331，不迁移第二美化", [modify(study["bag"]("main_hand", 271092), enchant_id=8689), item("off_hand", 268196)]),
        "H3_dagger334": ("H3盾334＋已有匕首升334，不迁移第二美化", [item("main_hand", 271092, enchant_id=8689), item("off_hand", 268196)]),
        "H3_complete": ("H3盾334＋已有匕首升334＋腕披双奥纹", list(double.values())),
        "Craft_shield_complete": ("331普通制造盾＋已有匕首升334＋腕披双奥纹", list({**double, "off_hand": craft("off_hand", 237831)}.values())),
        "H10_tendril": ("H10触须334替现有321毒液，保留无底袋", [item("trinket1", 281215)]),
        "H3_H10_complete": ("H3与H10两目标均获取＋334匕首＋双奥纹", list({**double, "trinket1": item("trinket1", 281215)}.values())),
        "Shoulder_CH_H10": ("331暴击急速普通制造肩＋H10触须334", [craft("shoulder", 244580, stats="32/36", enchant_id=8001), item("trinket1", 281215)]),
    }
    for name, (_, changes) in candidates.items():
        gear = dict(p)
        gear.update({line.split("=", 1)[0]: line for line in changes})
        ids = [int(study["fields"](line)["id"]) for line in gear.values()]
        assert len(set(ids) & {271481, 271482, 271483, 271484, 271486}) >= 4, name
        embellishments = [bonus for line in gear.values() for bonus in study["fields"](line).get("bonus_id", "").split("/") if bonus in ("12384", "13771")]
        assert len(embellishments) <= 2, name
        assert not (245770 in ids and "off_hand" in gear), name
    for mode in ("raid", "dungeon"):
        study["emit"](f"followup-{mode}", mode, p, candidates, iterations=6000, seed=36102026, stage="followup")
    study["MANIFEST_PATH"].write_text(json.dumps(study["MANIFEST"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render():
    manifest = json.loads((ROOT / "study-manifest.json").read_text(encoding="utf-8"))
    batches = []
    for key in ("followup-raid", "followup-dungeon", "followup-target-raid", "followup-target-dungeon"):
        if not (ROOT / f"{key}.json").exists():
            continue
        mode = "raid" if key.endswith("-raid") else "dungeon"
        sim = study["measured"](key)
        dps = sim["players"][0]["collected_data"]["dps"]
        rows = []
        for row in sim["profilesets"]["results"]:
            rows.append({"name": row["name"], "label": manifest[key]["labels"][row["name"]], "mean": row["mean"],
                         "gain_percent": 100 * (row["mean"] / dps["mean"] - 1), "error95": row["mean_error"],
                         "difference_error95": math.hypot(row["mean_error"], 1.96 * dps["mean_std_dev"])})
        batches.append({"key": key, "mode": mode, "baseline": dps["mean"], "baseline_stderr": dps["mean_std_dev"],
                        "context": "recommended target gear and its haste flask" if "target" in key else "prepared current gear and its crit flask",
                        "targets": sim["options"]["desired_targets"], "seconds": sim["options"]["max_time"],
                        "model": sim["options"]["fight_style"], "valid_fight_style": True,
                        "requested_iterations": 6000, "seed": sim["options"]["seed"], "results": rows})
    data = {"checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "baseline": "Each batch declares its current or final-target baseline. Chosen-mode talents, race, buffs and consumables are controlled within each batch.",
            "batches": batches,
            "limits": ["Candidate acquisition is hypothetical, not a guaranteed bonus-roll result or spending event.",
                       "H3 dagger334 requires normal upgrade costs and two-lining conversion requires a complete craft plan.",
                       "Plain crafted shoulder331 replaces the fifth tier piece; current head/chest/hands/legs remain four-piece.",
                       "Dungeon reference is supported fixed-five-target90s Patchwerk, with unverified split-AOE effects and target-switching limitations.",
                       "Difference intervals use an independence approximation and do not correct multiple comparisons."]}
    (ROOT / "followup-sim-summary.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# H3／H10与制造肩补充对照", "", "基准：现装仅补齐头附魔、虫群戒附魔与已确认空孔；候选装备均未视为已获取。", ""]
    for batch in batches:
        context = "未来成型套装基准" if "target" in batch["key"] else "补齐现装基准"
        lines += [f"## {'团本单体' if batch['mode'] == 'raid' else '大米固定多目标参考'}／{context}", "", f"{batch['model']}，{batch['targets']}目标，{batch['seconds']}秒，6000次；基准{batch['baseline']:.2f} DPS。", "", f"|候选|DPS|相对{context}|均值95%半宽|", "|---|---:|---:|---:|"]
        for row in sorted(batch["results"], key=lambda row: row["mean"], reverse=True):
            lines.append(f"|{row['label']}|{row['mean']:.2f}|{row['gain_percent']:+.2f}%|±{row['error95']:.2f}|")
        lines += [""]
    lines += ["这些是装备兑现后的收益，不能乘上未核实的R币命中率计算期望收益。无底袋的已R记录与H7未R记录见本角色周记录；普通掉落表不等于完整剩余R池。", ""]
    (ROOT / "followup-comparison.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({batch["key"]: {row["name"]: round(row["gain_percent"], 3) for row in batch["results"]} for batch in batches}, ensure_ascii=False))


def targets():
    for mode in ("raid", "dungeon"):
        gear = study["load_gear"](f"recommended-{mode}")
        player = study["measured"](f"recommended-{mode}")["players"][0]
        choices = {f"Shoulder_{pair}": (f"成型套装改331普通制造肩{study['PAIR_NAMES'][pair]}，保留头胸手腿四件", [study["craft"]("shoulder", 244580, stats=stats, enchant_id=8001)]) for pair, stats in study["PAIRS"].items()}
        choices["Keep_321"] = ("成型套装暂用已有321肩，其余配置不变", [study["prepared"]()["shoulder"]])
        choices["Other_334"] = ("另获现有同来源272252神话334肩并化生", [study["item"]("shoulder", 271481, redirected_base_stats=272252, enchant_id=8001)])
        study["emit"](f"followup-target-{mode}", mode, gear, choices, iterations=6000, seed=37102026, stage="followup-target", flask=player["flask"])
    study["MANIFEST_PATH"].write_text(json.dumps(study["MANIFEST"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "render", "targets"))
    args = parser.parse_args()
    globals()[args.action]()
