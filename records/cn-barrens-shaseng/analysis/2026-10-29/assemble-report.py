"""Assemble the dated report from measured results and preserved research evidence."""

from datetime import datetime
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def measured(key, mode="slice", iterations=7000, seed=26102921):
    path = HERE / f"native70575-{mode}-{key}-{iterations}-{seed}.validation.json"
    if not path.exists():
        return None
    result = read(path)
    assert result["accepted"] is True
    base = read(HERE / f"native70575-{mode}-current-7000-26102921.validation.json")
    return {"dps":result["dps"], "ci":result["ci95"], "delta":100*(result["dps"]/base["dps"]-1), "artifact":path.name}


def gain(key, base, mode="slice"):
    return 100*(measured(key,mode)["dps"]/measured(base,mode)["dps"]-1)


def main():
    elite = read(HERE / "elite-evidence.json")
    icons = read(HERE / "report-icons.json")
    intake = read(ROOT / "records/cn-barrens-shaseng/snapshots/2026-10-29-equipped.items.json")
    stats_actor = read(HERE / "native70575-stats-current-40-26102901.json")["sim"]["players"][0]
    stats = stats_actor["collected_data"]["buffed_stats"]["stats"]
    slots = dict(zip("head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand".split(),"头部 项链 肩部 披风 胸部 护腕 手套 腰带 腿部 鞋子 戒指一 戒指二 饰品一 饰品二 双手武器".split()))
    gear_keys = {"shoulder":"shoulders", "wrist":"wrists"}
    notes = {
        "head":"四件套；前驱271875盘卷守望者的凝视，保留201急速及13847毒咒急速。",
        "shoulder":"四件套；321英雄6/6，前驱251146拾荒者护肩：59暴击／84全能。默认套装绿字不适用。",
        "chest":"四件套；前驱281236具象恐惧护胸，保留58暴击／143急速及14049虚空爆发。",
        "legs":"四件套；321英雄6/6，前驱251130：112暴击／79精通。",
        "waist":"321英雄6/6；非正式套装计数位，历史前驱271436及急速／精通配方。",
        "back":"331制作，暴击／急速，奥纹美化之一。",
        "wrist":"331制作，暴击／精通，奥纹美化之二；当前导出没有已镶宝石。",
        "hands":"331普通制作，急速／精通，不占四件套；无手部战艺附魔不构成大米缺失。",
        "feet":"331普通制作，暴击／精通；不带第三件美化。",
        "finger2":"331普通制作，暴击／精通；已有宝石和鹰眼神视，不应只按裸戒评分比较兑换戒。",
        "trinket2":"已晋升341；大米可争取触须替换，保留祖尔金用于单体及不同遭遇。",
        "trinket1":"已晋升341；本次大米触须对照保留此主动饰品。",
        "main_hand":"已晋升341，保留13846毒咒精通与哈谢仪式；不是本周主要缺口。",
        "neck":"已晋升341，保留13987随机属性毒咒；宝石不动。",
        "finger1":"334虫群戒，已由H10 R获得且装备唯一；第二枚不能用于另一戒指槽。",
    }
    gem_names={240983:"费解之永歌钻石",240892:"无瑕精湛榄石",240908:"无瑕精湛榴石"}
    equipment=[]
    for item in intake["items"]:
        slot=item["slot"]; parsed=stats_actor["gear"][gear_keys.get(slot,slot)]
        equipment.append({"slot":slots[slot],"name":item["name"],"id":item["item_id"],"level":parsed["ilevel"],"bonus":item["bonus_ids"],"icon_data":icons[str(item["item_id"])]["icon_data"],"source":"当前已装备／用户10月29日导出","note":notes[slot],"gems":[{"id":int(i),"name":gem_names.get(int(i),i)} for i in (item["gem_ids"] or "").split("/") if i]})
    comparisons=[]
    labels={"current":"当前完整装备／精通合剂","waist_cm":"仅321腰→331暴击精通普通制作腰","delve_shoulder334":"兑换雾猎者肩→化生→334（急速／暴击）","delve_legs334":"兑换雾猎者腿→化生→334（急速／精通）","post_both":"H7腰＋腿334，保留当前肩","post_both_shoulder":"H7腰腿＋兑换急暴肩334","post_both_raid_shoulder":"H7腰腿＋团本暴精肩334","post_both_ring":"H7腰腿＋兑换妖术戒334（未假定额外孔）","post_both_ring_socket":"H7腰腿＋妖术戒334（额外孔与原宝石）","tendril334":"334触须替341祖尔金，保留乌心","tendril341":"341触须替341祖尔金，保留乌心","route":"H7腰腿＋兑换肩＋341触须（目标组合）","route_craft_waist":"目标组合保留331暴精制作腰","route_raid_shoulder":"H7腰腿＋团本暴精肩＋341触须","flask_haste":"当前装仅换血骑士急速合剂","flask_crit":"当前装仅换破碎残阳暴击合剂","gems_hm":"当前装两枚戒指宝石改急速精通","glove_cm":"当前装仅制作手改暴击精通"}
    for key,label in labels.items():
        comparisons.append({"key":key,"label":label,"values":{mode:measured(key,mode) for mode in ("slice","st","aoe")}})
    branches=[
        {"outcome":"H7尚未拿到腰或腿／本次R出其他物品","preferred":"继续追H7时偏向兑换肩；只看即时切片也可兑换腿","reason":"当前装备下肩不是两种模型都胜出。兑换肩避免与H7腿重叠；若后续不再投入H7，需按常打场景在肩、腿间选择。","comparison":f"相对当前装：兑换肩＋{measured('delve_shoulder334')['delta']:.2f}%（切片）、＋{measured('delve_shoulder334','aoe')['delta']:.2f}%（五目标）；兑换腿＋{measured('delve_legs334')['delta']:.2f}%／＋{measured('delve_legs334','aoe')['delta']:.2f}%。均已化生且升334，非刚兑换321的即时收益。"},
        {"outcome":"H7已拿到腿，腰尚缺","preferred":"优先兑换雾猎者护肩；腰留H7或普通制作","reason":"H7腿已解决套装大部位；兑换肩去掉当前肩的84全能。急暴肩不需要因腿上有急速而排除。","comparison":f"相对拿腿后：兑换肩＋{gain('post_legs_shoulder','post_legs'):.2f}%（切片）、＋{gain('post_legs_shoulder','post_legs','aoe'):.2f}%（五目标）；未假定孔的妖术戒{gain('post_legs_ring','post_legs'):+.2f}%（切片）。"},
        {"outcome":"H7只拿到腰，腿尚缺","preferred":"继续R H7的前提下偏向兑换肩；急需腿也可兑换腿","reason":"切片中两者非常接近，不能宣称某个唯一最优。五目标更偏向肩；兑换肩保留下一次H7腿的获取路线。","comparison":f"相对拿腰后：兑换肩＋{gain('post_waist_shoulder','post_waist'):.2f}%／兑换腿＋{gain('post_waist_legs','post_waist'):.2f}%（切片）；五目标分别＋{gain('post_waist_shoulder','post_waist','aoe'):.2f}%／＋{gain('post_waist_legs','post_waist','aoe'):.2f}%。"},
        {"outcome":"H7腰和腿都已拿到","preferred":"兑换急速／暴击肩，优于本批四种地下堡戒指","reason":"剩余321肩是明确缺口；四种兑换戒即使补同一颗宝石，也未超过本批肩方案。兑换物只能选固定属性，不能自选暴精。","comparison":f"相对H7腰腿基准：兑换肩＋{gain('post_both_shoulder','post_both'):.2f}%（切片）、＋{gain('post_both_shoulder','post_both','aoe'):.2f}%（五目标）；妖术戒补孔后＋{gain('post_both_ring_socket','post_both'):.2f}%／{gain('post_both_ring_socket','post_both','aoe'):+.2f}%。"},
        {"outcome":"已获得334泛沫毒液护肩／合适神话肩","preferred":"不要再兑换重叠肩；先看腿，再复核其他缺口","reason":"团本268246为99暴击／52精通；地下堡272244为57暴击／93急速。本批H7腰腿后，暴精肩略强，但不足以要求花币追小幅差距。","comparison":f"H7腰腿后，团本暴精肩对兑换急暴肩：切片{gain('post_both_raid_shoulder','post_both_shoulder'):+.2f}%，五目标{gain('post_both_raid_shoulder','post_both_shoulder','aoe'):+.2f}%。若腿腰也齐，不为兑换次数而盲换已有好戒。"},
    ]
    data={
        "meta":{"date":"2026-10-29／国服12.1.5补丁第三周","character":"沙僧 · 天神御师踏风","patch":"12.1.5／至暗之夜第2赛季","content":"大秘境优先，附单体与五目标对照","engine":"SimC 710c2408bf／Live70575，10月28日热修","budget_note":"当前R币、残片、神话纹章、化生次数及毒液石余额未知。旧余额不继承；下列均为条件路线，模拟目标不是已获得装备。"},
        "lead":"属性结构合理，不存在必须堆到33%急速的通用合格线。先R再按结果兑换：H7负责腿／腰，地下堡通常补急暴肩；H10追扭曲恐兽触须。保留精通合剂、现有宝石和双奥纹。团本暴精肩是小幅更强备选，并非必须追逐的硬门槛。",
        "stats":[{"name":name,"rating":stats[f"{stat}_rating"],"percent":100*stats[f"{stat}_pct"],"comparison":comparison,"advice":advice} for stat,name,comparison,advice in [("crit","暴击","5位高手快照29%～33%；严格无增益口径未统一。","当前暴击不缺；H7换腿后下降仍需按整套评估，不机械补回原数值。"),("haste","急速","5位高手快照约17%～23%；网站50人汇总21%，不是毕业线。","当前处于合理范围。33%＋是攻略特定多目标爆发条件，不能当全局配装门槛。"),("mastery","精通","5位高手评分1217～1479；你当前1155，且已经是最高次级。","继续采用魔导师精通合剂。总量最高不代表每一点收益永远最高。"),("versatility","全能","5位高手快照2%～6%；你当前3.50%。","换掉当前肩的84全能可自然优化，不需要主动把全能堆成目标。")]],
        "equipment":equipment,
        "elite":[{"name":p["name"]+"－"+p["realm"],"score":p["rio_score"],"level":p["ilvl"],"url":p["source_url"],**dict(zip(("crit","haste","mastery","vers"),p["percent"]))} for p in elite["current_player_samples"]],
        "usage":[{"name":"套装肩","value":"49/50","note":"Murlok天神御师过滤；套装名不证明默认绿字，缺前驱不赋值。"},{"name":"制作手套","value":"15/50；所查5人中2人","note":"你现在331急速／精通制作手属于实际高层路线。"},{"name":"制作腰带","value":"5/50","note":"其余多用团本腰；并非必须鞋＋腰制作。腰不占正式四件套。"},{"name":"奥纹内衬","value":"97个美化实例／至多100位置","note":"5位高手均双奥纹，分布腕鞋／披腕／手鞋；你现有披腕双奥纹可保留。"},{"name":"触须＋乌心","value":"所查5位当前快照均采用","note":"335～339平均装等、+21～+23；不是最高层那场的逐场装备证明。"}],
        "models":[{"id":"slice","label":"合成大米切片","detail":"DungeonSlice360秒；无团队增益与嗜血，固定用户天赋/种族。含新目标，不代表实际路线；正式复测请求7000次、有效6999，独立种子26102921。"},{"id":"st","label":"240秒单目标","detail":"Patchwerk240秒、1目标；同消耗品、无团队增益与嗜血，用来观察首领取舍。"},{"id":"aoe","label":"90秒五目标","detail":"Patchwerk90秒、5固定目标；不会重复刷新新怪，因此不能代替触须的整趟大米收益。"}],
        "comparisons":comparisons,"branches":branches,
        "actions":[{"title":"先确认本周H10／H7奖励预览，再投入R币","body":"H10仍有未取得触须时优先考虑；虫群戒和特效胸已由R取得，不再给重复目标加分。H7继续追腿和腰；祖尔金已341，单手斧须与合法双持整套比较，披风须重新安排双奥纹。完成有效目标后停止固定双R。"},{"title":"H7之后决定地下堡兑换；神话2/6只是321起点","body":"三枚神话灵魂残片向瓦杜选购固定装备。雾猎者肩272244为急速／暴击，化生保持属性并补套装；神话轨可321→324→328→331→334，肩不能用毒液石继续晋升。当前321英雄6/6肩不能直接升成神话。"},{"title":"优先补低装等槽，制作腰是可选过渡","body":"331暴击／精通普通制作腰有个人正收益；但若即将R到H7腰，先等掉落可减少重做。已有双奥纹不限制额外普通制作件，没必要为追高手位置重做披风／腕。"},{"title":"取得触须后保留两套饰品用途","body":"本模型触须在大米与五目标较强，240秒单体则输给现有341祖尔金。取得后先升普通334即可使用，有毒液石再看升341；这次未假定你有剩余毒液石。"}],
        "consumables":[{"name":"魔导师合剂","current":"本次基准采用2星241322，精通＋165","recommendation":"当前优先保留；新版复测对急速、暴击合剂的切片优势可在模型表核对。","url":"https://www.wowhead.com/cn/item=241322"},{"name":"宝石","current":"费解之永歌钻石×1；无瑕精湛榄石×1；无瑕精湛榴石×2","recommendation":"先保持。两枚暴击／精通宝石全改急速／精通未测得收益；不要照抄高手颗数。","url":"https://www.wowhead.com/cn/item=240983"},{"name":"鲁莽药水","current":"本次基准采用2星241288","recommendation":"通常精通最高、全能最低；按使用瞬间有效评分选择，毒咒触发可改变结果，不按百分比判定。","url":"https://www.wowhead.com/cn/item=241288"},{"name":"食物与符文","current":"基准哈籁恩达尔庆典大餐＋虚触强化符文","recommendation":"熊猫人食物收益已由引擎计算。食物／符文为本次控制条件，不宣称已搜索全部食谱。","url":"https://www.wowhead.com/cn/item=255846"},{"name":"头／肩／胸／腿／鞋附魔","current":"8017强化闪避符文；8001阿梅达希尔之赐；7987世界之魂印记；8159森林猎手护甲片；7963山猫之敏","recommendation":"已有常用附魔，不需要整套更换。换新肩、腿后重新附上原方案。","url":"https://www.wowhead.com/cn/item=243991"},{"name":"戒指／武器附魔及油","current":"双7967鹰眼神视；8689哈谢仪式","recommendation":"保留。鹰眼神视提高暴击效果，并非暴击几率；武器配萨拉斯凤凰之油，本次使用2星。","url":"https://www.wowhead.com/cn/item=273071"},{"name":"手套战艺","current":"当前制作手未附8727，符合导出","recommendation":"远古哈谢战技仅地下堡／迷宫生效；不要为大米增伤补它。高手佩戴不等于大米触发。","url":"https://wow.blizzard.cn/24266320/index.html"}],
        "limits":["当前无消耗品属性为SimC战前snapshot，关闭合剂／食物／药水／强化符文／临时武器附魔／团队增益／嗜血；保留天赋、宝石、永久附魔及装备被动。并非战斗均值。","化生保留绿字和特效已经用户确认；当前精简导出不含前驱，头沿用271875，肩胸腰腿采用10/23相同ID和bonus的前驱连续性。换过前驱时须重新导出。","原始Wowhead解析仍对12856返回340，且默认套装绿字不反映化生前驱；正式结论用新版Live70575原生341及显式前驱，不使用旧tooltip平均装等。","表内±为95%均值置信区间半宽，非单次战斗波动；不同战斗模型绝对DPS不可横比。局部整套比较不是全局BiS证明。","胸部虚空爆发、虫群戒AOE分摊仍为引擎未验证实现；药水／特效与实际路线有差异，绝不承诺实服同百分比。","当前R池预览、完整历史、背包和资源未知，不报精确概率或下一币必出；所有拟兑换／拟R物品均未记入获得。","只有头肩胸腿供当前四件套。换肩或腿前必须确认可化生且有次数；普通散件尚未转化时不能按四件套方案直接穿。","当前50人样本不含国服，5位高手快照未统一无增益口径、未取得完整bonus与前驱，不可将其默认套装绿字当实物。","兑换商人完整奖励bonus、孔和三级属性未知；无孔基准与额外补孔假设分开测试。候选rank参数用于模型，不伪称实际获得链接。","构建缓存仍将结果内嵌git_revision显示为73a；实际源码已快进到710c且重新编译，JSON内Live70575、10/28热修和原生341均已核验。以新二进制SHA256和数据版本追溯，不将旧内嵌提交标记当新版未更新。"],
        "sources":[{"title":"Murlok：天神御师大米50人及角色页","url":"https://murlok.io/monk/windwalker/conduit-of-the-celestials/m%2B"},{"title":"当前第三周：瓦杜神话2/6确定兑换目录","url":"https://www.wowhead.com/news/myth-2-6-piece-of-loot-now-available-from-labyrinths-383603"},{"title":"国服官方12.1：化生保留属性与R币规则","url":"https://wow.blizzard.cn/news/24293281/index.html"},{"title":"国服官方12.1.5：纹章、晋升范围与来源","url":"https://wow.blizzard.cn/news/24304162/"},{"title":"SimC本次固定更新提交","url":"https://github.com/simulationcraft/simc/commit/710c2408bf"},{"title":"职业作者属性说明：无强制通用断点","url":"https://www.icy-veins.com/wow/windwalker-monk-pve-dps-stat-priority"},{"title":"Method踏风12.1.5属性与消耗品","url":"https://www.method.gg/guides/windwalker-monk/stats-races-and-consumables"}],
        "downloads":[{"title":"原始10/29已装备SimC","path":"../../snapshots/2026-10-29-equipped.simc"},{"title":"当前装清洁大米模拟输入","path":"current-dungeon.simc"},{"title":"拟获取整套大米模拟输入（兑换肩路线）","path":"recommended-dungeon.simc"},{"title":"团本暴精肩备选模拟输入","path":"alternate-raid-shoulder.simc"},{"title":"高手研究及逐项来源","path":"elite-research.md"},{"title":"兑换与完整基础R池研究","path":"weekly-sources-research.md"},{"title":"正式引擎与数据溯源","path":"simc-manifest-native70575.json"},{"title":"报告原始结构化数据","path":"report-data.json"}],
    }
    data["measured_at"]=datetime.now().astimezone().isoformat()
    data["unbuffed_stat_context"]={"agility":2530,"average_item_level":sum(v["ilevel"]*(2 if k=="main_hand" else 1) for k,v in stats_actor["gear"].items())/16,"snapshot":stats_actor["collected_data"]["buffed_stats"]}
    data["conditional_tests"]={key:{m:measured(key,m) for m in ("slice","aoe")} for key in ["post_legs","post_legs_shoulder","post_legs_ring","post_waist","post_waist_shoulder","post_waist_legs","post_waist_ring","post_both","post_both_shoulder","post_both_ring","post_both_ring_socket"]}
    data["additional_ring_screen"]={str(i):{m:measured(f"post_both_ring_{i}_socket",m,3000,26102911) for m in ("slice","aoe")} for i in (272147,272148,272150)}
    tuning_path = HERE / "tuning-summary.json"
    if tuning_path.exists():
        data["tuning"] = read(tuning_path)
        data["downloads"].extend([{"title":"肩腿腰334后调优结果与原始运行索引","path":"tuning-summary.json"},
                                  {"title":"肩腿腰334后宝石与再造说明","path":"tuning-review.md"},
                                  {"title":"高手与作者天赋来源及缺口","path":"elite-talents-research.md"},
                                  {"title":"短冷却与尚武候选／保留祖尔金／大米输入","path":"recommended-talent-zuljin-dungeon.simc"},
                                  {"title":"短冷却与尚武候选／触须／大米输入","path":"recommended-talent-tendril-dungeon.simc"}])
    crafting_path = HERE / "crafting-followup.json"
    if crafting_path.exists():
        data["crafting_followup"] = read(crafting_path)
        data["meta"]["budget_note"] += " 最新回报：地下堡肩已兑换；当前装等、是否化生和是否穿上未报告。下方装备表仍为兑换前原始导出，不冒充新快照。"
        data["lead"] = "肩膀已确认兑换。现有披风＋护腕双奥纹可继续用，手／鞋／戒也是331普通制作；不必为凑两件重新制作。腰仍321且短期等不到H7腰时，可补331暴精普通制作腰。其余R币与配装按实际获取结果调整。"
        data["actions"].insert(0, {"title":"肩已兑换后的制造安排","body":"保留披风暴急＋护腕暴精双奥纹；鞋暴精、手急精、戒暴精继续使用。若腰仍321，可普通制造331暴精腰，不能再加第三件美化；已有H7腰则跳过。以后实际拿到更好的非制造披风，再把披风奥纹迁到鞋，形成腕＋鞋双奥纹。此次迁移差距小且模型分歧，不提前花钱。"})
        data["downloads"].append({"title":"肩已兑换后的制造部位比较","path":"crafting-followup.md"})
        if data["crafting_followup"].get("additional_two_crafts"):
            data["meta"]["budget_note"] += " 用户另确认火花足够新增两件制作装，未报告精确余额；首选普通331暴精腰，第二件尚无明确增益目标。"
            data["actions"][0]["body"] += " 新增两件预算已单独比较：暴精腰优先；制作腿换回旧321套装手、特殊制作戒均未建立更强第二件目标。火花充足也不用购买重复331部位。"
            data["downloads"].append({"title":"新增两件制作装的组合模拟与假设","path":"two-crafts-summary.json"})
    (HERE/"report-data.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for key,name in [("current","current-dungeon.simc"),("route","recommended-dungeon.simc"),("route_raid_shoulder","alternate-raid-shoulder.simc")]:
        shutil.copyfile(HERE/f"native70575-slice-{key}-7000-26102921.simc",HERE/name)
    print("Assembled report-data.json and three single-loadout SimC exports.")


if __name__=="__main__":
    main()
