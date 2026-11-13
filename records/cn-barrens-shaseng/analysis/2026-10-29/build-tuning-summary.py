"""Collect measured armor tuning and talent comparisons for the existing report."""

from datetime import datetime
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
MODES = ("slice", "aoe", "st")
BRANCHES = {"zuljin":"乌心＋祖尔金341", "tendril":"乌心＋触须341"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def result(path, baseline):
    if not path.exists():
        return None
    run, base = read(path), read(baseline)
    assert run["accepted"] and base["accepted"]
    return {**run, "delta":100*(run["dps"]/base["dps"]-1), "artifact":path.name}


def tune(branch, mode, key, iterations=12000, seed=26102951):
    return result(HERE/f"tuning-{branch}-{mode}-{key}-{iterations}-{seed}.validation.json",
                  HERE/f"tuning-{branch}-{mode}-baseline-{iterations}-{seed}.validation.json")


def talent(branch, mode, key, tuning="baseline", iterations=10000, seed=26102971):
    path = HERE/f"talents-{branch}-{mode}-{key}-{tuning}-{iterations}-{seed}.validation.json"
    value = result(path,HERE/f"talents-{branch}-{mode}-user-baseline-{iterations}-{seed}.validation.json")
    if value:
        same = read(HERE/f"talents-{branch}-{mode}-{key}-baseline-{iterations}-{seed}.validation.json")
        value["tuning_delta_same_talents"] = 100*(value["dps"]/same["dps"]-1)
    return value


def main():
    def snapshot(name):
        return read(HERE/name)["sim"]["players"][0]["collected_data"]["buffed_stats"]
    old=snapshot("native70575-stats-current-40-26102901.json")["stats"]
    upgraded=snapshot("tuning-zuljin-stats-baseline-40-26102931.json")["stats"]
    optional=snapshot("tuning-zuljin-stats-craft_cm_pair_mastery_gems-40-26102931.json")["stats"]
    labels={"gems_240898":"只改三颗普通宝石为16精通／7暴击",
            "craft_cm_pair_mastery_gems":"披风＋手套暴精再造，三颗普通宝石主精通／副暴击",
            "craft_back_hm":"只把披风改急速／精通",
            "diamond_three_colors":"改强能钻石并凑三色普通宝石"}
    comparisons=[{"branch":label,"label":name,"key":key,"values":{mode:tune(branch,mode,key) for mode in MODES}}
                 for branch,label in BRANCHES.items() for key,name in labels.items()]
    summary={
        "summary":"完成334肩腿腰后，先保留现有制作属性、宝石、双鹰眼和精通合剂。小幅再造是可选精修；先试更适合自己的乾元天赋，再决定是否投入。",
        "assumption":"假设雾猎者肩272244、H7腿268225、H7腰268256均升334；头肩胸腿四件套，现有制作仍331、披风护腕双奥纹。分祖尔金／触须两种341饰品。这不是已获取记录。",
        "stats":[{"name":name,"before":f"{old[stat+'_rating']:.0f}／{100*old[stat+'_pct']:.2f}%",
                  "after":f"{upgraded[stat+'_rating']:.0f}／{100*upgraded[stat+'_pct']:.2f}%","note":note}
                 for stat,name,note in [("crit","暴击","下降后仍约31%，无需为了保住原33.5%强补。"),
                                       ("haste","急速","三件升级后自然上升；这不是青龙内有效急速。"),
                                       ("mastery","精通","依旧是最高次级；使用精通合剂时更高。"),
                                       ("versatility","全能","去掉旧肩84全能；低全能是结果，不是必须精确到0的目标。")]],
        "recommendations":[
            {"part":"披风／手套","owned":"披风暴击／急速；手套急速／精通","decision":"默认保留；联合改暴精仅作可选精修","reason":"与宝石联合调整在原天赋切片约＋0.39%～0.42%，会减少146急速评分；更换构筑后另作联合复核。"},
            {"part":"护腕／鞋／制造戒","owned":"均暴击／精通","decision":"保留","reason":"逐槽筛选没有支持为统一急精而重做。保留护腕奥纹；不假设新增宝石孔。"},
            {"part":"普通宝石","owned":"1颗240892急精＋2颗240908暴精","decision":"保留；联合精修时才考虑3颗240898","reason":"只换宝石收益很小且场景有分歧。240898无瑕致命紫晶＝16精通／7暴击，不是240908的16暴击／7精通。"},
            {"part":"特殊钻石","owned":"240983费解之永歌钻石，32主属性","decision":"保留","reason":"强能钻石三色方案差距小；当前仅三个普通宝石位，不假设四色效果。"},
            {"part":"戒指附魔","owned":"双7967鹰眼神视","decision":"保留","reason":"高级29评分的精通／急速、暴击附魔筛选均落后。鹰眼增加暴击效果，不是暴击几率。"},
            {"part":"其他附魔","owned":"强化闪避／阿梅达希尔之赐／世界之魂印记／森林猎手／山猫之敏／哈谢仪式","decision":"方案保留；新肩、新腿重新附上","reason":"没有发现因这次绿字变化而必须更换的依据；未穷举全部武器附魔。手部战艺不计大米收益。"},
            {"part":"合剂／药水／油","owned":"魔导师精通合剂、鲁莽、凤凰之油","decision":"保留","reason":"两种饰品与新天赋复查仍偏精通合剂。鲁莽按使用时有效评分选择，不按百分比。"}],
        "comparisons":comparisons,
        "limits":["本表调优固定原用户天赋，各饰品分支相对自己的334肩腿腰基准；新天赋的联合复核另列，不能直接加百分比。",
                  "筛选3000次／26102941；关键复测12000次、有效11999／独立种子26102951，±为95%均值置信区间半宽。近误差的小差距不构成再造理由。",
                  "当前静态20.64%急速，带本次凤凰油为21%；已确认流转之智使青龙内再乘1.10，约33.1%。这不保证旭日暴击、两个怒雷或实际客户端时序。",
                  "可选微调会使静态急速17.32%、暴击32.43%、精通87.23%；不能拿其低静态急速直接断言不合格，也不能据平均DPS证明拳谱时序不变。",
                  "保留四件套、两件奥纹、已有孔和武器合法性；额外打孔不在本次预算内。全部是假设未来装备，不改当前持有状态。",
                  "仍受胸与虫群戒AOE分摊未验证、默认行动优先级与实际路线差异影响。"],
        "created_at":datetime.now().astimezone().isoformat(),
        "snapshots":{"upgraded_unbuffed":upgraded,"optional_unbuffed":optional},
        "screen_results":[read(p) for p in sorted(HERE.glob("tuning-*-3000-26102941.validation.json"))],
        "haste_evidence":"tuning-haste-evidence.json",
    }
    names={"user":"你当前天赋", "user_short_cd":"只将角杯盖子改灵魂专注",
           "user_short_cd_martial":"保留你的功能天赋，短冷却＋尚武敏捷",
           "bisset_1026":"10月26日保存Bisset完整高层参考"}
    talents={"summary":"相比约0.4%的装备精修，乾元节点在本模型中的影响更大。先试灵魂专注短冷却；再按单体需求和真气容错决定能量爆裂／尚武敏捷。",
             "candidate_results":[{"branch":label,"candidate":key,"label":name,"values":{m:talent(b,m,key) for m in MODES}}
                                  for b,label in BRANCHES.items() for key,name in names.items()],
             "joint_tuning":[{"branch":label,"candidate":"user_short_cd_martial","values":{m:talent(b,m,"user_short_cd_martial","craft_cm_pair_mastery_gems") for m in MODES}}
                             for b,label in BRANCHES.items()],
             "exports":read(HERE/"talent-candidates.json"),
             "screen_results":[read(p) for p in sorted(HERE.glob("talents-*-3000-26102961.validation.json"))],
             "evidence":"elite-talents-research.md",
             "limits":["5位高手只有当前节点观察，没有取得当前完整导出；Bisset整串来自10月26日，明确作为旧参考。另有当前Method与IcyVeins大米作者完整串作筛选，不冒充高手个人。",
                       "两个控制字串从你的原串只改指定选择节点，由SimC原生重新导出；不是声称高手使用该整串。",
                       "旧本地攻略串在新版解析出现额外英雄节点，仅保留审计，不作为当前推荐。",
                       "新天赋复测10000次、有效9999／26102971。固定目标长度和默认优先级会影响乾元施放次数，实服收益取决于路线与按键。",
                       "短冷却15秒与延长20秒乾元的拳谱不同，不能换天赋却继续机械照打旧序列。功能与生存天赋不因低伤害权重而自动删去。"]}
    summary["talents"]=talents
    (HERE/"tuning-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for b in BRANCHES:
        source=HERE/f"talents-{b}-slice-user_short_cd_martial-baseline-10000-26102971.simc"
        shutil.copyfile(source,HERE/f"recommended-talent-{b}-dungeon.simc")
    print("Updated tuning-summary.json and two clean candidate SimC exports.")


if __name__=="__main__":
    main()
