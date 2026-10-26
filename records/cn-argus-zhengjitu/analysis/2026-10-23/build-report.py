"""Render measured Elemental equipment research without inventing acquisitions."""

import html
import json
import math
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAR = ROOT.parents[1]
SLOTS = "head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand off_hand".split()
ALIASES = {"shoulder": "shoulders", "wrist": "wrists"}
SLOT_NAMES = {"main_hand": "武器", "off_hand": "盾牌", "neck": "项链", "trinket1": "饰品一", "trinket2": "饰品二"}
manifest = json.loads((ROOT / "study-manifest.json").read_text(encoding="utf-8"))
snapshot = json.loads((CHAR / "snapshots/2026-10-23.items.json").read_text(encoding="utf-8"))
items = json.loads((ROOT / "report-items.json").read_text(encoding="utf-8"))
elite = json.loads((ROOT / "elite-research.json").read_text(encoding="utf-8"))
followup = json.loads((ROOT / "followup-sim-summary.json").read_text(encoding="utf-8"))
followup_batches = {batch["key"]: batch for batch in followup["batches"]}
stats_comparison = json.loads((ROOT / "stats-comparison.json").read_text(encoding="utf-8"))
current_stats = stats_comparison["characters"]["cn-argus-zhengjitu"]["current"]["dungeon"]
week = json.loads((CHAR / "weeks/2026-10-22.json").read_text(encoding="utf-8"))
raw = (CHAR / "snapshots/2026-10-23.simc").read_text(encoding="utf-8-sig")


def read_result(key):
    path = ROOT / f"{key}.json"
    assert path.stat().st_mtime >= (ROOT / f"{key}.simc").stat().st_mtime, f"Stale result: {key}"
    payload = json.loads(path.read_text(encoding="utf-8"))
    sim = payload["sim"]
    assert sim["players"][0]["valid_fight_style"], f"Unsupported workload cannot enter report: {key}"
    assert not payload.get("errors") and not sim.get("errors"), key
    assert "Severe:" not in (ROOT / f"{key}.run.log").read_text(encoding="utf-8-sig"), key
    return sim


def parse(line):
    return dict(part.split("=", 1) for part in line.split("=", 1)[1].split(",") if "=" in part)


def human_label(value):
    replacements = {
        "Craft_for_alch": "制造戒替邪恶戒", "Craft_for_swarm": "制造戒替虫群戒",
        "251136_for_alch": "咆哮奴役玺戒替邪恶戒", "268252_for_alch": "顶级蛮兵爪戒替邪恶戒",
        "251136_for_swarm": "咆哮奴役玺戒替虫群戒", "268252_for_swarm": "顶级蛮兵爪戒替虫群戒",
        "BagTendril": "无底袋＋触须", "VenomTendril": "毒液＋触须", "BagVenom": "毒液＋无底袋",
        "back_wrist": "腕＋披风", "wrist_feet": "腕＋鞋", "wrist_waist": "腕＋腰",
        "craft_legs": "制造腿", "raid_legs": "团本散件腿", "Crit合剂": "暴击合剂", "Haste合剂": "急速合剂", "Mastery合剂": "精通合剂",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def gear_rows(text, actual=None):
    rows = []
    owned = {entry["slot"]: entry for entry in snapshot["items"]}
    for line in text.splitlines():
        slot = line.split("=", 1)[0]
        if slot not in SLOTS or line.endswith("=none"):
            continue
        fields = parse(line)
        ident = int(fields["id"])
        entry = owned.get(slot)
        level = actual["gear"][ALIASES.get(slot, slot)]["ilevel"] if actual else entry["item_level"]
        is_owned = bool(entry and ident == entry["item_id"] and level == entry["item_level"])
        note = "当前已拥有；目标属性或宝石／附魔可能需要重造补齐" if is_owned else "未来候选，未记录为获取"
        status = "已拥有，可能需补齐" if is_owned else "目标配置未拥有"
        if actual and ident == 271092:
            is_owned, status = True, "背包已有331，目标需升级"
            note = "已拥有神话5/6简斯拉泽331；目标334只需正常升级，不需重新获取，具体纹章费用看游戏预览"
        elif actual and slot == "shoulder":
            note += "；当前同名肩为英雄321，不能直接升神话334；需神话来源后化生"
        if fields.get("redirected_base_stats"):
            note += f"；化生前驱ID {fields['redirected_base_stats']}，与普通套装属性不同"
        if slot == "off_hand":
            note += "；盾牌方案不自动改成雷击结界天赋"
        if ident == 270164:
            note += "；用户后续确认：此无底袋来自H3 R，已补入历史记录"
        source_id = fields.get("redirected_base_stats", ident)
        source = "专业制造／重造" if "crafted_stats" in fields else items.get(str(source_id), {}).get("source")
        if not source or source == "unknown":
            source = "未核实"
        row = {"slot": slot, "id": ident, "ilevel": level, "owned": is_owned, "status": status, "note": note, "source": source}
        for key in ("bonus_id", "gem_id", "enchant_id", "crafted_stats", "redirected_base_stats", "content_tuning"):
            row[key] = fields.get(key)
        rows.append(row)
    return rows


def run_summary(key):
    sim = read_result(key)
    stats = sim["players"][0]["collected_data"]["dps"]
    info = manifest[key]
    stage = info["stage"]
    labels = {"current": "原始装备：补齐与单件初筛", "practical": "当前装备：武器／制造完整组合", "bags": "背包现有饰品",
              "target": "完整目标套装初筛", "refine": "目标套装：属性、戒指、饰品与盾牌初筛", "joint": "戒指×饰品×制造属性×合剂联合搜索",
              "verify": "独立种子高迭代复测", "final": "最终组合：保留已有套腿与制造位置复核", "validation": "最终配装对原装：同批6000次验证", "robustness": "多目标／时长敏感性检查", "followup": "追加：H3／H10与当前制造肩选择", "followup-target": "追加：未来成型套装的制造肩替代", "upgrade-current": "未来10石：当前装备选择（当前仅7石）", "upgrade-target": "未来10石：目标套装选择（当前仅7石）"}
    assert sim["players"][0]["valid_fight_style"], f"Rejected workload cannot enter report: {key}"
    provisional = stage.startswith("upgrade") or info["mode"] == "dungeon"
    return {"key": key, "mode": info["mode"], "stage": stage, "label": labels.get(stage, stage),
            "baseline": stats["mean"], "stderr": stats["mean_std_dev"], "iterations": sim["options"]["iterations"],
            "seed": sim["options"]["seed"], "model": sim["options"]["fight_style"], "targets": sim["options"]["desired_targets"], "seconds": sim["options"]["max_time"],
            "note": "大米用导出当前天赋，团本用保存的“单体”天赋；同批种族／天赋不变。小幅差异需结合误差；不同批次绝对DPS不能横比。" +
                    ("元素萨不支持DungeonSlice／DungeonRoute，原批次已弃用；本批为支持的固定目标Patchwerk，不是实际大米路线。H10手／虫群戒AOE未分摊假设及触须新目标节奏仍待实战验证。" if info["mode"] == "dungeon" else "") +
                    ("毒液石未花费，341／337为旧DBC上的截图装等覆盖，英雄毒液321的热更终点未知未纳入本批。" if stage.startswith("upgrade") else ""),
            "results": [{"name": row["name"], "label": human_label(info["labels"].get(row["name"], row["name"])), "mean": row["mean"],
                         "error": row["mean_error"], "provisional": provisional or "tendril" in row["name"].lower() or "281215" in row["name"]}
                        for row in sim.get("profilesets", {}).get("results", [])]}


def gain(run, name):
    row = next(row for row in run["results"] if row["name"] == name)
    return (row["mean"] / run["baseline"] - 1) * 100


profiles = {}
stat_names = {"32/36": "暴击急速", "32/49": "暴击精通", "36/49": "急速精通"}
flask_names = {"flask_of_the_shattered_sun_2": "暴击合剂", "flask_of_the_blood_knights_2": "急速合剂", "flask_of_the_magisters_2": "精通合剂"}
for mode in ("raid", "dungeon"):
    key = f"recommended-{mode}"
    sim = read_result(key)
    player = sim["players"][0]
    unbuffed = read_result(f"unbuffed-{mode}")["players"][0]
    text = (ROOT / f"{key}.simc").read_text(encoding="utf-8")
    selected = manifest[key]["selected"]
    selection_key = manifest[key].get("selected_from", f"verify-{mode}")
    gear = gear_rows(text, player)
    by_slot = {row["slot"]: row for row in gear}
    stats_name = stat_names[by_slot["wrist"]["crafted_stats"]]
    legs_name = "保留已有334套腿" if by_slot["legs"]["id"] == 271482 else "另做331制造腿"
    arrangement = f"制造{stats_name}＋{flask_names[player['flask']]}；{legs_name}；" + "／".join(items[str(by_slot[slot]["id"])]["name"] for slot in ("finger1", "trinket1", "trinket2"))
    profiles[mode] = {"raw": text, "gear": gear, "selected": selected, "selected_from": selection_key, "joint_selected": manifest[key].get("joint_selected"), "family": manifest[key]["family"], "arrangement": arrangement,
                      "stats": {stat: unbuffed["collected_data"]["buffed_stats"]["stats"][stat] for stat in ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")},
                      "stats_context": "已禁用合剂／食物／药水／符文／武器油及团队增益的模拟快照，保留角色被动；不是强制属性阈值。",
                      "consumables": {key: player[key] for key in ("flask", "food", "potion", "augmentation", "temporary_enchant")},
                      "note": "本次已测推荐：" + arrangement + "。普通掉落334／制造331，强化另测；部分目标尚未拥有。" +
                              ("固定当前先知天赋、5目标90秒；只作大米装备参考，非实际路线最佳解，暂不据此决定重造或花币。" if mode == "dungeon" else "团本固定导出保存的单体先知天赋，240秒单目标；其他Boss机制未逐场模拟。")}

stages = ("current", "practical", "bags", "targets", "refine", "joint", "verify", "final", "validation", "upgrade-current", "upgrade-target")
runs = [run_summary(f"{stage}-{mode}") for stage in stages for mode in ("raid", "dungeon")]
runs += [run_summary(key) for key in ("robust-5t40", "robust-8t40", "robust-1t180")]
runs += [run_summary(key) for key in ("followup-raid", "followup-dungeon", "followup-target-raid", "followup-target-dungeon")]
practical = {mode: next(run for run in runs if run["key"] == f"practical-{mode}") for mode in ("raid", "dungeon")}
conclusions = [
    "09:57导出为2枚R币、7枚晋升毒液石、2枚潮汐火花、7次化生。后续确认H3无底袋由R获得、H7从未R、H10本周已经R过。H10发生时间与09:57余额先后未知，不能直接再扣一枚，也不能把2枚当作已确认当前余额。H10结果未知，不据此排除手套或戒指。",
    "当前五件套装，肩膀321为英雄6/6；四件套已满足，第五件没有额外套装奖励。头／胸／手／腿均334：可先保留四件334，把弱肩换更好的散件，或取神话肩化生后再评估制造腿。不得先拆成三件套。",
    "确认仅虫群戒有一个现有空孔；头部缺附魔、虫群戒缺附魔。腕／腰本次完整tooltip无孔，不凭bonus编号或制造部位推断插槽。先补这三处，不重插全部宝石。",
    f"背包331简斯拉泽＋321风暴庇护直接替现装法杖并非提升：本次补齐基准对照团本{gain(practical['raid'], 'Owned_dagger_shield'):+.2f}%／大米{gain(practical['dungeon'], 'Owned_dagger_shield'):+.2f}%。换武器会同时失去法杖仪式石，不能把不完整转换当作一手盾毕业强度。",
    f"未来获取334触须替321毒液，在当前装备的5目标90秒支持模型约{gain(practical['dungeon'], 'Tendril_for_venom'):+.2f}%；这不是整场大米收益。DungeonSlice已被元素萨模块明确判定不支持，旧结果全部弃用；不得用旧约6%的结果决定花币或重造。",
    "高分样本与踏风不同：元素萨制造腕很普遍，制造戒／腰／腿也常见；不是默认照抄踏风腕＋鞋。双奥纹在样本中常见，但当前仪式石＋奥纹的合法组合不能仅因使用率低就认定必须重做。",
    "制造属性必须同时清理旧missive bonus；原导出的crafted_stats可能与最终有效属性不符。所有重造保留或明确迁移美化，最多两个输出美化；钥匙链没有被当作第三份DPS美化收益。",
]
conclusions.insert(1, "本周剩余路线改为H3优先、其他币尽量保留；H10本周已用，不再安排，10月29日重置后再看触须。H3的神话轨道套肩和盾都能解决缺口：肩321→神话肩有价值，头胸手腿四件334仍保留。前提是H3本周仍有资格，且实际预览含职业肩兑换物；历史R袋日期未知，不能默认H3本周一定还能R。")
conclusions.insert(2, "H3的1/2只能是条件模型：实际剩余恰为肩兑换物270924、盾268196、智力锤268210、鞋268258四项且等权时，肩或盾合计2/4=50%，盾单独1/4=25%。当前没有完整角色R预览或权重证据，不把条件算术写成已核实概率；普通掉落表含肩token也不等于可R。")
conclusions.insert(3, f"当前真实装备的无消耗品属性快照：暴击{current_stats['percentages']['crit']:.1f}%、急速{current_stats['percentages']['haste']:.1f}%、精通{current_stats['percentages']['mastery']:.1f}%、全能{current_stats['percentages']['versatility']:.1f}%。对照本次刷新高分大米页面的25.2%／20.2%／64.0%／2.7%，暴击已接近、精通偏多而急速偏少，全能已经低；网站未确认完全同口径，不把这些数值当硬阈值。新做制造肩可优先已测暴击急速，不需要为了对齐网站马上全部重造。")
conclusions += [
    f"制造肩不是高手常规部位：17:17单独抓取的大米800日志／160角色约1.4%、团本896日志／450角色约1.8%；没有与15:21旧样本混合。对你当前321第五件套肩，331普通暴击急速制造肩保留头胸手腿四件，补测团本约{gain(followup_batches['followup-raid'], 'Shoulder_CH'):+.2f}%、5目标90秒约{gain(followup_batches['followup-dungeon'], 'Shoulder_CH'):+.2f}%。属于可确定补短板的过渡，不需要把奥纹移到肩。",
    "制造肩也在成型戒指／饰品／急速合剂下单独复测：最佳制造属性与H7来源334肩约0.1%量级差异，近似误差内可保留制造替代路线；不因制造肩使用率低就认为不能穿，也不把过渡的暴击急速写成所有成型组合固定属性。",
    "H3神话334盾有长期配装价值，但不是必须消耗R币才能补齐。补测同为334匕首＋腕披双奥纹时，334掉落盾对331普通制造盾仅团本约+0.17%、5目标约+0.10%，多目标差异接近误差。若盾和肩都能用制造或其他来源补齐，可以不R H3并留币；仅制造盾并不自动消除神话套肩的价值。本次未单独测H3原生套肩，不能冒用H7化生肩的精确收益。",
]
for mode, label in (("dungeon", "大米参考"), ("raid", "团本")):
    run = next(run for run in runs if run["key"] == f"validation-{mode}")
    rows = {row["name"]: row for row in run["results"]}
    raw_gain = (run["baseline"] / rows["Raw_current"]["mean"] - 1) * 100
    prepared_gain = (run["baseline"] / rows["Prepared_current"]["mean"] - 1) * 100
    conclusions.append(f"{label}成型候选：{profiles[mode]['arrangement']}。简斯拉泽334＋毒痕鳞甲盾334；保留H8胸／H10手特效。6000次同批对原装约{raw_gain:+.2f}%，对补齐现装约{prepared_gain:+.2f}%。" + ("只代表固定5目标90秒，不能外推实际钥石路线。" if mode == "dungeon" else "只代表240秒单目标。"))
conclusions += [
    "保留已有334套腿是正式候选，不强行追制造腿。最终戒指／饰品／合剂不变的独立复核若近似误差内，优先不花火花；制造位置也按最终组合复核，不拿旧基准的腿部单件结果代替。神话肩化生不是更换制造腿之前的已完成事实。",
    "现有331制造腰先保留，不能把元素萨直接套成踏风的鞋腰组合。仪式石仍在法杖时，单把它搬成第二奥纹并无明确收益；等单手盾和制造配套一并成立再迁移，避免先拆法杖收益。",
    "大暴击戒若指斯索拉克的顶级蛮兵爪戒268252，值得列为H3之后的条件次选，不是已有双戒334就没用。同334参考属性为338暴击／67急速，对比邪恶戒73暴击／332精通，可替邪恶戒、保留虫群戒；附魔与宝石另行核对。已有团本成型基准6000次复测约+0.97%，不是当前装备立即提升的承诺；大米最终联合候选仍选251136，不把它写成所有场景唯一毕业。实际R池、历史、资格及余额未知前不默认追加一枚预算。",
]
short = next(run for run in runs if run["key"] == "robust-5t40")
wide = next(run for run in runs if run["key"] == "robust-8t40")
conclusions.append(f"饰品按阶段区分：成型的334毒液＋触须在5目标40秒对照里，改毒液＋无底袋约{gain(short, 'BagVenom'):+.2f}%，改触须＋无底袋约{gain(short, 'BagTendril'):+.2f}%；8目标40秒改触须＋无底袋约{gain(wide, 'BagTendril'):+.2f}%。这是完整目标套装的短战斗参考，现有321毒液不等同目标334毒液；无底袋继续保留作不同战斗／配装备选，不据此报废。")
for mode in ("dungeon", "raid"):
    run = next(run for run in runs if run["key"] == f"upgrade-current-{mode}")
    conclusions.append(f"若凑齐10石但还没转单手盾，当前已测{'5目标90秒' if mode == 'dungeon' else '团本'}中法杖331→337约{gain(run, 'Staff337'):+.2f}%，高于项链／无底袋；但英雄321毒液热更终点未知，未纳入。近期准备转匕首盾时应先等路线明确，避免把10石投给将换下的法杖。")
for mode in ("dungeon", "raid"):
    run = next(run for run in runs if run["key"] == f"upgrade-target-{mode}")
    ranked = sorted(run["results"], key=lambda row: row["mean"], reverse=True)
    best, second = ranked[:2]
    stable = best["mean"] - second["mean"] > math.hypot(best["error"], second["error"])
    conclusions.append(f"未来目标套装{'大米' if mode == 'dungeon' else '团本'}10石选择：{best['label']}，相对本批约{(best['mean']/run['baseline']-1)*100:+.2f}%；" +
                       ("领先次选超过本批近似误差。" if stable else "与次选接近，暂不强行排序。") + "不等同今天可以花，必须先凑齐10石、确认目标可达与游戏预览。")

def percentage(mode, category, ident):
    return next((row["percent"] for row in elite["modes"][mode]["selections"][category] if row.get("item_id") == ident), None)

elite_items = [("主手", 271092, "main_hand"), ("主手制造法杖", 245770, "main_hand"), ("副手盾", 268196, "off_hand"), ("制造盾", 237831, "off_hand"),
               ("无底袋", 270164, "trinkets"), ("毒液", 273796, "trinkets"), ("触须", 281215, "trinkets"), ("制造腕", 244584, "crafted"),
               ("制造戒", 240949, "crafted"), ("制造腰", 244581, "crafted"), ("制造腿", 244582, "crafted"), ("制造鞋", 244577, "crafted"),
               ("制造披风", 239656, "crafted"), ("洛阿戒", 251513, "crafted")]
samples = {"retrieved_at": "2026-10-23；冻结15:21快照，不混合刷新比例", "mythic_plus": {"logs": 800, "characters": 160, "period": "最近两周，+22至+24，100%先知"},
           "raid": {"logs": 900, "characters": 473, "period": "最近三周，神话全首领，100%先知"},
           "note": "逐物品边际频率，不等于同一整套同时使用率或个人BiS；窗口跨版本／热更。同名套装不能判定化生前驱。双奥纹组合出现率大米78.6%／团本83.4%，并不证明奥纹一定放在特定部位。", 
           "items": [{"slot": label, "id": ident, "mythic_plus": percentage("mplus", category, ident), "raid": percentage("raid", category, ident)} for label, ident, category in elite_items]}
sources = [
    {"title": "本角色原始导出", "url": "../../snapshots/2026-10-23.simc", "note": "09:57 CN/阿古斯，原文含背包、资源和保存天赋；保留原字节。"},
    {"title": "高分元素萨大米样本", "url": "https://mythicstats.com/spec/elemental-shaman", "note": "冻结单次800日志／160角色；不是独立前五名。"},
    {"title": "高分元素萨团本样本", "url": "https://mythicstats.com/raid/spec/elemental-shaman", "note": "冻结单次900日志／473角色。"},
    {"title": "本次高手证据与来源详情", "url": "elite-research.json", "note": "含比例、ID、窗口、HTTP快照哈希和未核实边界。"},
    {"title": "国服12.1.5内容更新说明", "url": "https://wow.blizzard.cn/news/24304162/", "note": "10月22日周取消纹章上限；每10石强化满级合资格武器、饰品、项链，不包含护甲和戒指。"},
    {"title": "10月23日装等热更用户截图", "url": "../../../cn-barrens-shaseng/analysis/2026-10-23/reference-hotfix-2026-10-23.png", "note": "神话334→341，最高品质制造331→337；精确新bonus尚未验证。"},
    {"title": "SimC源码固定版本", "url": "https://github.com/simulationcraft/simc/commit/73a372b76188c703e48729caded3258cdc5b726b", "note": "本地E:/github/simc，Live12.1.5.70529，数据库热修10月22日。"},
    {"title": "已有8月元素萨机制学习稿（历史）", "url": "../../../../notes/elemental-shaman-12.1-study-guide.md", "note": "不是10月23日循环依据；本次默认APL已改变，不能照抄旧爆发顺序。"},
    {"title": "已弃用DungeonSlice批次与原因", "url": "rejected-dungeonslice/rejection.json", "note": "原始探索输出隔离留档；元素萨valid_fight_style=false，不能用于推荐。正文和下载均已重跑支持模型。"},
    {"title": "后续H3／H10与制造肩四批6000次对照", "url": "followup-comparison.md", "note": "分开补齐现装和未来成型基准；现有四件套保留，制造肩不是额外美化。"},
    {"title": "后续制造肩高手分布快照", "url": "followup-elite-shoulders.json", "note": "独立17:17快照，制造肩244580：大米1.4%、团本1.8%；不同刷新样本不合并。"},
    {"title": "后续各Boss／专精候选与R排除证据", "url": "followup-pools.json", "note": "已确认H3 R袋、H7未R、H10本周已R但结果未知；普通掉落、专精字段和实际R池分别记录。肩token资格、完整剩余池及权重仍未知。"},
    {"title": "10月22日周事实与剩余计划", "url": "../../weeks/2026-10-22.json", "note": "H10本周不可再规划，10月29日后再看；09:57余额2与该次R的先后未知，保留历史余额，不伪造当前余额。H3肩或盾50%仅条件等权算例。"},
    {"title": "大暴击戒的价值与R币条件", "url": "ring-roll-review.md", "note": "区分268252和大米251136；引用已有成型基准，不伪造现装单件收益或完整R概率。条件次选，不记消费。"},
    {"title": "正极兔／沙僧当前属性与高手统计对照", "url": "stats-comparison.md", "note": "四份新跑的当前装备属性快照关闭消耗品／外部团队增益；分开当前、未来目标和新刷新高分统计，不作精确阈值或纯属性DPS归因。"},
]
limitations = [
    "本次目标普通神话334、制造331；不借用全服顶尖玩家更高装等掉落。未来目标不是当前背包；仅神话轨道匕首331→334属于已有物品正常升级，具体纹章成本与当前4枚神话纹章是否足够需游戏预览。",
    "当前只有7枚毒液石。341／337比较是截图规则在10月22日旧DBC上的显式装等覆盖；未确认英雄321毒液的热更终点，因此未将它的毒液石强化纳入完整排名。不得声称已搜索所有合资格当前升级。",
    "元素萨模块明确拒绝DungeonSlice和DungeonRoute；所有旧DungeonSlice结果已隔离，不进入正文排名和建议。重跑为支持的5目标90秒Patchwerk，再以5／8目标40秒及1目标180秒检查；均不代表实际钥石路线，也不构成全路线最佳解。",
    "触须首次新目标叠层、高低波次、目标死亡与转火均影响收益。H10套装手和虫群戒AOE在引擎中明确标记未验证、不分摊伤害假设；Rune of Unleashed Fire的目标选择也尚未验证。因此多目标推荐仍暂定，不单凭此决定两枚R币和全套重造。",
    "当前导出先知已点烈焰武器、未点雷击结界。单手盾比较不同时改成雷击结界；武器油带if条件且烈焰武器时不生效，报告保存油字符串不等于重复灌注收益。天赋优化不是本次全球穷举范围。",
    "同批保持个人种族／对应天赋；团本用保存的单体天赋，大米用当前导出。不能横比两个模式的绝对DPS。各profileset估计近似独立，显示95%均值误差；差值独立近似未校正多重比较，不是全局最优证明。",
    "腕／腰未确认额外孔位，不添加假孔。未来戒指候选按具备一个合法插槽建模，实际获得的插槽／打孔资源需要核对，不把无孔装备视为已打孔。",
    "完整候选先筛制造位置，再做属性／戒指／饰品联合优化，并非穷举所有可掉落物品和每一种宝石混搭。普通参考tooltip不代表本槽真实配置；实际参数以下载和模拟结果为准。",
    "仅观察两／三周高分日志分布，没有逐角色完整WCL事件或新独立前五名复盘。已确认本角色H3无底袋由R获得、H7未R、H10本周已R但结果未知；当前余额、H3本周资格、肩token可R资格、完整剩余池、排除是否耗尽重置及低保仍未知。不能把沙僧H7/H8/H10记录迁移；50%仅四项等权条件算例，不是实测命中率。",
    "未来制造腿／戒指会消耗火花和金币，当前只2火花；配方材料成本未完整核实，不承诺本周全部可做。已有334部位不为极小差距强行报废；近似误差内保留替代路线。",
]
routes = [
    {"boss": "立即：补齐实装与保留现有资源", "priority": "先做", "targets": [], "excluded": [], "spec": "元素", "note": "头部附魔、虫群戒附魔和一个现有空孔；7石不足一次晋升，不提前花。腰／腕已有331，不照抄踏风做鞋腰。", "stop": "保留原装与原宝石，先确认价格；先不为小幅重造或低装等盾浪费金币。"},
    {"boss": "H3／迷失探险者：盾或套装肩", "priority": "本周剩余首选／条件规划最多1币", "targets": [268196, 271481, 268210, 268258, 270164], "excluded": [270164], "spec": "元素；未证实恢复能缩池", "note": "盾和神话套肩都是有效目标：现肩321，头胸手腿334仍保四件。肩通过职业兑换物270924获取，列表展示成品271481，但token可R资格仍须实机预览。无底袋已确认由R取得，排除限对应英雄池尚未耗尽／重置。若实际剩余恰为肩、盾、锤、鞋且等权，则肩或盾2/4=50%，盾单独25%；不是已核实概率。", "stop": "先确认当前至少1币及H3本周仍有资格，历史R袋日期未知。拿到肩后先别制造肩；拿到盾后再完成匕首升级／第二奥纹配套。若肩和盾都已有满意替代，可留币，不为了清池追加。"},
    {"boss": "H10／基希克斯：本周已R，下周再看触须", "priority": "本周不可再安排／10月29日后复核", "targets": [281215, 281238, 281029], "excluded": [], "spec": "元素；当前角色奖励预览为准", "note": "用户确认本周已经R过H10，结果未知；本周不再分配H10币，也不把未知结果写成手套或戒指排除。触须补测相对补齐现装5目标90秒约+2.11%、团本约+1.14%，仅为模型结果。尚无切恢复缩池的可靠依据。", "stop": "10月29日重置后，先确认本次R结果、实际剩余池及可用币，再决定一枚追触须；拿到目标或实际池不含目标就停止。09:57的2币快照不视为最新余额。"},
    {"boss": "已有331简斯拉泽升级＋盾牌来源", "priority": "先改善配套，不重复追武器", "targets": [271092, 268196, 268262, 237831], "excluded": [], "spec": "元素", "note": "331匕首已在背包且是神话5/6，先看升334所需资源；盾牌来自实际掉落／低保或331制造。低盾直接配匕首未必胜过法杖。", "stop": "匕首无需因未装备而当作未拥有；只有具备整套收益和资源时才迁移法杖仪式石。"},
    {"boss": "H7肩／制造肩与保留四件套", "priority": "不默认投入币追肩", "targets": [271481, 268231, 244580], "excluded": [], "spec": "元素", "note": "用户确认H7从未R；1/4只是待验证估计。当前四件334加321肩，普通331制造肩可保留头胸手腿四件。H7神话肩仍是可用来源，但制造肩与大米／低保肩都能替代，不再默认新做腿或为肩清H7池。", "stop": "有可用331制造肩或334神话肩后，不为极小差距专门投H7币；保留H8胸／H10手效果，不拆四件。"},
    {"boss": "斯索拉克：大暴击戒顶级蛮兵爪戒", "priority": "H3后条件次选／不预分配额外预算", "targets": [268252], "excluded": [], "spec": "元素；实际奖励预览为准", "note": "同334为338暴击／67急速，对比现有邪恶戒73暴击／332精通，适合替邪恶戒并保留虫群戒，不能因双戒已334而否定。团本成型基准6000次单戒复测约+0.97%，不是你现装即时收益。大米成型联合方案仍保留251136替代。完整剩余池和既往R记录未知，不报命中率。", "stop": "若H3仍有肩＋盾两种有效目标，先看H3；若H3已解决／无资格，或此Boss实际池更集中，可考虑这一枚。先核对余额、当周资格及历史；拿到满意戒指就停，不为清池硬花，也不虚构下周预算。"},
    {"boss": "其他目标／保留币而非强行消费", "priority": "不默认新增本周R", "targets": [240949, 251136, 273796, 270164], "excluded": [], "spec": "元素", "note": "H7专追肩暂不推荐；H9尼姆瑞莎盾只是H3盾的替代，不同时排两套追盾预算。大米咆哮奴役戒和更高轨道毒液属于后续目标，池／费用／资格未完整核实，不包装成本周必R清单。斯索拉克暴击戒已单列条件次选，不是一律不R。", "stop": "已有双戒334和无底袋334不代表所有同槽物品无收益，但应比较实际提升与机会成本。H3和暴击戒都没有满意机会就保留，待10月29日H10或低保更新后重排；不承诺未知囤币上限。"},
]
data = {"meta": {"date": "2026-10-23", "patch": "12.1.5 第二周", "character": "正极兔 · 元素萨 · CN阿古斯", "engine_commit": "73a372b761", "wow_version": "12.1.5.70529 Live", "hotfix_date": "引擎10月22日；晋升装等按10月23日截图", "budget": week["budget"]["current_balance"], "budget_note": "09:57导出为2枚；后续确认H10本周已R，但发生时间与导出先后未知。当前余额待确认，不重复扣币。本周H10不可再安排；H3为首选，大暴击戒为条件次选，不据未知余额分配总次数。", "average_ilevel": snapshot["equipped_average"], "catalyst_charges": 7,
                   "empty_sockets": "仅虫群戒一个已确认空孔；腕／腰tooltip无孔", "armor_upgrade_track": "肩321英雄6/6，不能纹章升神话；背包匕首331神话5/6可正常升334，具体成本看预览", "upgrade_materials": "晋升毒液石7，差3枚；潮汐火花2。341/337为旧DBC显式覆盖，尚未消费。", "scope": "元素先知；大米当前天赋、团本保存单体天赋。个人模拟＋高手聚合分布，非完整WCL操作复盘。", "snapshot": {"角色": "黑铁矮人元素萨，当前先知；原始导出09:57", "当前装等": snapshot["equipped_average"], "套装": "五件：头胸手腿334＋肩321；四件效果已满足", "美化": "法杖仪式石13771＋护腕奥纹12384；披风钥匙链12715未计作输出美化", "资源": "09:57为R币2／毒液石7／火花2／化生7；H10本周已R但时间／结果未知，当前R币余额待确认；H3已R袋、H7未R", "已拥有的关键背包物品": "331神话5/6简斯拉泽、321风暴庇护，不能视为未获得"}},
        "current": {"raw": raw, "gear": gear_rows(raw), "owned_item_ids": sorted({int(value) for value in re.findall(r'^(?:# )?[a-z0-9_]+=[^\r\n]*?\bid=(\d+)(?:,|$)', raw, re.M)} | {int(value) for value in re.findall(r'\bredirected_base_stats=(\d+)', raw)})}, "profiles": profiles,
        "items": {key: {**value, "tooltip": html.unescape(re.sub(r"<[^>]+>", " ", value.get("tooltip", ""))).replace("\b", " ")} for key, value in items.items()},
        "runs": runs, "conclusions": conclusions, "elite_samples": samples, "routes": routes, "sources": sources, "limitations": limitations}
template = (ROOT / "dashboard.template.html").read_text(encoding="utf-8")
data["meta"]["snapshot"]["当前属性（非未来目标）"] = "／".join(f"{label}{current_stats['percentages'][key]:.1f}%（{current_stats['ratings'][key]:.0f}等级）" for key, label in (("crit", "暴击"), ("haste", "急速"), ("mastery", "精通"), ("versatility", "全能"))) + "；关闭消耗品及外部团队增益，保留角色被动"
assert template.count("__REPORT_DATA__") == 1
(ROOT / "dashboard.html").write_text(template.replace("__REPORT_DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")), encoding="utf-8")
summary = {"checked_at": datetime.now().astimezone().isoformat(timespec="seconds"), "simc_revision": "73a372b761", "meta": data["meta"], "profiles": profiles, "runs": runs, "conclusions": conclusions, "elite_samples": samples, "routes": routes, "limitations": limitations}
(ROOT / "study-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
markdown = ["# 正极兔：12.1.5第二周元素萨配装", "", "## 先执行", ""] + ["- " + text for text in conclusions]
for run in runs:
    if run["stage"] not in ("practical", "verify", "final", "validation", "robustness", "followup", "followup-target", "upgrade-current", "upgrade-target"):
        continue
    markdown += ["", f"## {run['mode']} / {run['label']}", "", f"基准{run['baseline']:.2f} DPS，{run['iterations']}次，种子{run['seed']}，{run['model']} {run['seconds']}秒。", "", "|候选|DPS|相对基准|均值95%误差|", "|---|---:|---:|---:|"]
    for row in sorted(run["results"], key=lambda row: row["mean"], reverse=True):
        markdown.append(f"|{row['label']}|{row['mean']:.2f}|{(row['mean']/run['baseline']-1)*100:+.2f}%|±{row['error']:.2f}|")
markdown += ["", "## 路线与停止条件", ""] + [f"- {row['boss']}：{row['note']} {row['stop']}" for row in routes]
markdown += ["", "## 限制", ""] + ["- " + value for value in limitations]
markdown += ["", "## 来源", ""] + [f"- [{row['title']}]({row['url']})：{row['note']}" for row in sources]
(ROOT / "recommendation.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
print(f"Rendered {len(runs)} measured batches and two exact profiles.")
