"""Render the dated WCL coaching review from measured local artifacts."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


casts = read("cast-analysis.json")
damage = read("burst-evidence.json")
gear = read("gear-summary.json")
samples = {sample["key"]: sample for sample in casts["samples"]}
compat = gear["compatibility_341"]["comparisons"]
measured = {}
for mode in ("slice", "raid"):
    for row in compat[mode]["actions"]["rows"]:
        measured[f"{row['candidate']}_{mode}"] = f"{row['delta_pct']:+.2f}%"
    measured[f"elite_{mode}"] = f"{compat[mode]['elite_comparison']['delta_pct']:+.2f}%"
    measured[f"talents_{mode}"] = f"{gear['build_comparability']['comparisons'][mode]['delta_pct']:+.2f}%"
data = {"samples": {}, "damage": damage["samples"]}
for key, sample in samples.items():
    ordinary = sample["buff_intervals"]["443421"]
    fof = [e for e in sample["cast_ledger"] if e["spell_id"] == 113656]
    empty = [b for b in ordinary if not any(b["start_ms"] <= e["timestamp_ms"] < b["end_ms"] for e in fof)]
    data["samples"][key] = {**{k: sample[k] for k in ("name", "url", "keystone_level", "fight_duration_ms", "scopes", "white_interval_s", "white_windows", "blue_summary", "buff_intervals", "cast_ledger", "fight_start_ms")},
                              "ordinary_empty_count": len(empty), "ordinary_count": len(ordinary)}
assert data["samples"]["elite"]["ordinary_empty_count"] == 1
assert data["samples"]["shaseng"]["ordinary_empty_count"] == 9

recommendations = [
    "优先练青龙接力与逐跳覆盖：普通青龙48个窗口有9个没有怒雷起手；参考场59个有1个。窗口无起手是复查入口，不自动等于9次操作失误。",
    "旭日后已经会变招：首轮29.142秒主旭日暴击、29.504秒自动晨晖也暴击，随后30.952秒怒雷。当前更明确的改进点是把这次刷新与升龙、天神的青龙接力协调起来。",
    "平稳期按Boss与小怪分开看。小怪可识别pull内核心动作密度37.45与37.41接近；Boss无主要增益段为40.73与46.24次/分钟，且你的神鹤更多、旭日/幻灭更少。仍需控制目标、免费触发和职责，不能一律把神鹤换成旭日。",
]
markdown = """# 沙僧与Bisset：爆发期、平稳期及装备复盘

日期：2026-10-26。已有研究已提交并快进合并到main，远端为`50b6c6e`；本轮分析保存在`analysis/shaseng-wcl-2026-10-26`，未自动提交。

这场的优先训练项是**青龙接力与怒雷逐跳覆盖**。你已经会根据旭日结果改变后续动作；整场怒雷少33次，不足以直接判定漏按。分开小怪、Boss、爆发与平稳后，问题更具体。

## 样本与可比性

| 项目 | 沙僧 | Bisset |
|---|---:|---:|
| 地区／种族 | CN贫瘠之地／熊猫人 | EU Kazzak／暗夜精灵 |
| 日期、地下城 | 10月24日毒牙祭坛 | 10月25日毒牙祭坛 |
| 层数 | +15 | +23 |
| 战斗跨度，不同于钥石计时 | 1548.525秒 | 1764.231秒 |
| WCL显示全程DPS | 382001.6 | 547003.3 |
| 对应层级百分位 | 97 | 100，样本少于50 |
| 可识别pull区间合计 | 1388.197秒 | 1708.899秒 |
| 玩家死亡 | 0 | 0 |
| 当前人物页均装 | 331.75 | 334.81 |

层数、队伍、怪物寿命、拉怪规模、种族和天赋不同。Bisset首个pull为342秒，你的首个pull为73秒，同序号不能视作同一个场景。你当前项链已341，但所选旧日志开场仍334；当前配装模拟与这场旧日志严格分开。

## 爆发期：有分支，接力还可以更完整

| 首轮可复核事件 | 沙僧 | Bisset |
|---|---|---|
| 第一次旭日主命中 | 00:29.142，暴击 | 00:30.940，未暴击 |
| 自动晨晖 | 00:29.504，暴击 | 此次未出现 |
| 后续关键动作 | 00:30.952怒雷→00:33.539升龙 | 00:31.933升龙→00:33.930怒雷 |
| 首个升龙青龙实际区间 | 00:33.540–00:37.450 | 00:31.934–00:37.917 |
| 该区间的怒雷起手 | 0 | 1 |
| 大青龙实际区间 | 00:37.450–00:43.445 | 00:40.027–00:46.025 |
| 大青龙尾部的一发怒雷 | 00:43.411起手；约20.8%该条伤害带青龙 | 00:44.457起手；该条伤害100%带青龙 |

日志事实：你的天神在36.679秒启动，37.450秒同一时间移除普通青龙并获得大青龙。普通青龙只存在3.910秒，尚未打出怒雷。43.411秒的怒雷只剩34毫秒大青龙，正常五个脉冲全部打出，但后四个脉冲的伤害已经没有青龙。**主要问题在覆盖时机，不能把它说成断了怒雷。** 机制后果：起手时有青龙不保证整条怒雷吃满。下一把先看普通青龙剩余时间和怒雷实际冷却，再决定天神接续及填充动作。事实置信度高；如何重排整套最优、可节省多少伤害，仍需可用资源和完整冷却状态。

全程怒雷实际伤害中，带任一青龙的比例为沙僧63.36%、参考场76.44%。按实际damage行的buff字段与伤害额统计，包含套装额外命中，不能当作纯操作损失率。每条正常通道通常形成五个时间脉冲，首脉冲可另有两件套额外命中；多目标行数不等于通道跳数。

完整旭日主命中及自动晨晖配对后，双暴为你21次、参考场14次；这不是暴击率的受控比较，也不能独立证明冷却已经转好。它说明本场不能只用“没有双暴”解释所有青龙空窗。

## 平稳期：分开Boss和小怪

本报告“实际增益段”取白虎、乾元、三种青龙或天神通道的并集；“平稳代理段”指六种均不在，仍可能有饰品、嗜血或其他触发。只在WCL可识别pull区间内比较，分子与分母取同一区间。核心动作只计怒雷、神鹤、旭日、幻灭、猛虎、疾风踢和升龙，不计自动真气破、宠物、额外命中。

| 区域与状态 | 沙僧核心动作/分钟 | Bisset核心动作/分钟 |
|---|---:|---:|
| 小怪，实际增益段 | 39.76 | 42.94 |
| 小怪，平稳代理段 | 35.72 | 33.56 |
| Boss，实际增益段 | 43.11 | 45.85 |
| Boss，平稳代理段 | 40.73 | 46.24 |

小怪pull总体为37.45与37.41，拉法和通道长度不同，不能据此判谁全程按得更快。Boss平稳代理段，你的神鹤9.23次/分钟、旭日5.44、幻灭2.97；参考场为5.51、8.20、7.94。Boss pull也可能有小怪，神鹤还可能消费套装/赤精，以上是**优先级复查线索，中等置信度**。训练时先用真正单目标木桩，检查每次神鹤是否有套装或赤精、是否因此推迟已可用的核心技能；不训练无条件少按神鹤。

四件套消费也有直接线索：按套装1297033移除与技能cast相差不超过120毫秒匹配，你132次移除中123次接神鹤、5次旭日、4次疾风踢。其中小怪pull内有2次旭日和4次疾风踢消费；参考场非神鹤消费均在Boss pull。优先回看你的03:10.343与05:39.370两次旭日，以及11:03.469、17:02.483、17:20.917、20:42.682的疾风踢，确认当时是否仍有多个有效目标；若确有多个目标，套装神鹤通常更值得优先。pull类型不等于瞬时目标数，因此不将这6次全部记为确定失误。

两个Boss窗口尤其适合回看：你的普通青龙08:12.537–08:18.533，怒雷在08:18.722；08:39.205–08:45.200，怒雷在08:45.406。它们都差约0.2秒落在窗外。中间有旭日/幻灭等动作，但日志未给出完整可用冷却与真气状态，暂不判定具体哪一个填充必错。下一把练“升龙之前就规划这一轮怒雷何时转好”，并记录未暴、单暴、双暴不同分支。

## 构筑与爆发轴

你所选日志用乾元延长5秒的节点，实际乾元通常20秒；Bisset用乾元冷却缩短20秒的节点，实际通常15秒。Bisset还有白字攻速节点，你选了能量爆裂。二者都为天神御师，但不是同一构筑；不能套同一个乾元结束秒数或机械复制2112。

白虎间隔中位数为你110.318秒、参考场91.709秒；你还有更多分包间隔。此项应在可持续作战的长pull里规划，不能根据全程差值宣布漏了6个白虎。参考场第一波固定30秒内6怒雷7神鹤，你为5怒雷6神鹤；30秒是分析口径，不等于材料里含尾段的完整双乾元爆发。7怒雷9神鹤是特定构筑、嗜血、触发、目标寿命和窗口长度下的示范。

另做完整天赋字符串控制：保持你的最新装备和熊猫人种族，换成Bisset当前完整天赋，在本批3500次模型中大米__talents_slice__、单体__talents_raid__。这是整套天赋敏感性，不能把收益全归因于一个乾元节点，也不等于要求立刻换天赋。它值得作为下一次木桩对照：先选定20秒延长流或15秒短冷却流，再练对应的爆发接力；不要拿另一套构筑的节拍判自己。

本轮实服事件中普通/大青龙通常约6秒，乾元青龙约4秒。原始DBC字段列有8秒，但本次模拟有效增益输出的大青龙为6秒、乾元青龙4秒、普通青龙平均约5.9秒（可被提前接替），与日志相符；不能拿原始字段冒充有效运行时长。复盘仍按本轮真实apply/remove边界。

## 配装：补护甲短板，保留已完成的改动

你已经具备同款尾王武器、项链、贪婪心、祖尔金、特效头/胸、腕披双奥纹等关键结构，腰/手/腿/肩仍321。Bisset也有321肩，差异更集中在334手腰鞋、套装头换制造腿、第二饰品晋升和戒指组合。不要单独照抄他的制造腿：你目前靠肩胸手腿四件，单换腿会掉四件套。

当前制造腕、鞋、戒已为暴击精通，披风暴击急速。全改急速精通在旧数据控制模型中反而下降；不为攻略的25%或33%字样强行全套重造。鲁莽比较喝药瞬间的评分，不是面板百分比；现装无消耗品最高评分仍为精通，但动态增益可能改变药水选择。

341兼容批次采用保留全部bonus并对已经晋升的部位显式覆盖341，来源为当前WCL与战斗combatantinfo；引擎DBC仍为10月22日，原bonus解析340的结果单独留档。以下是6000次固定种族/天赋模拟模型，不能外推实际整场钥石净提升，也不能将两项相加：

| 独立替换 | 合成大米DungeonSlice360秒 | 单体Patchwerk240秒 |
|---|---:|---:|
| 331普通暴击精通制造腰替321腰 | __waist_331_cm_slice__ | __waist_331_cm_raid__ |
| 334邪恶戒替331制造戒，保留虫群戒 | __raid_ring_334_slice__ | __raid_ring_334_raid__，误差内 |
| 同用户种族天赋，换Bisset整装（双方原导出属性口径） | __elite_slice__ | __elite_raid__ |

高手整装对照缺少双方最新化生前驱，采用两边原样导出口径；单件行动比较采用用户旧快照中同ID/bonus部位的前驱连续性假设，两类基准不混用。当前金币、火花、毒液石和背包未知，不计消费。完整误差、参数、341与旧DBC差异见gear-review.md。

## 下一把只练三件事

1. **青龙接力。**显示怒雷真实冷却、普通/乾元/大青龙剩余时间与套装层数；每个升龙窗口优先检查能否纳入怒雷。对目标仍存活的空窗逐个标注原因，先减少可避免空窗，不追全覆盖100%。不要为了等下一条青龙而把已转好的怒雷无限留着。
2. **旭日后看状态。**主旭日与自动晨晖分别判断；出现双暴后检查怒雷是否真的转好。可用且资源够时及时跟进，仍未好则用符合当前单体/AOE优先级的动作衔接。下一场检查暴击后到下一合法怒雷之间插入了什么，而非只看双暴总数。
3. **分开练单目标与五目标。**单目标无套装/赤精时重点复查神鹤、旭日和幻灭取舍；五目标优先保证怒雷后的套装神鹤及有效目标命中。每次只选一段60秒平稳期和一次实际白虎爆发回看，不把嗜血上限序列强行覆盖所有波次。

## 来源、边界与复现

- [沙僧所选日志](https://cn.warcraftlogs.com/reports/G9HVRL18nAkzFyab?fight=4&type=damage-done&source=2)、[Bisset所选日志](https://cn.warcraftlogs.com/reports/4Ab97gnVjKhZP1Nf?fight=28&type=damage-done&source=1)。两人cast、buff、怒雷damage及旭日/晨晖damage均取完分页，末页游标为空。
- [Bisset人物页](https://cn.warcraftlogs.com/character/id/61823014?mode=detailed&zone=55)、[沙僧人物页](https://cn.warcraftlogs.com/character/id/90530177?mode=detailed&zone=55)。只有一个指定高手参考，不代表高手群体共同规律。
- [用户补充NGA攻略](https://ngabbs.com/read.php?tid=47391002)，本轮已通过用户Edge读取首帖，五张截图及本地速成指南单独保存在references。
- [固定版本SimC武僧模块](https://github.com/simulationcraft/simc/blob/73a372b76188c703e48729caded3258cdc5b726b/engine/class_modules/monk/sc_monk.cpp)、[默认APL](https://github.com/simulationcraft/simc/blob/73a372b76188c703e48729caded3258cdc5b726b/engine/class_modules/apl/apl_monk.cpp)。源代码解释机制，当前实服日志决定本场实际时长。
- 本轮完整分析只覆盖毒牙祭坛一场对一场；单体训练根据其中Boss窗口和机制指导，未额外完成团本Boss对照，也没有分解总DPS差距的精确归因百分比。
- 运行`python cast-analysis.py`、`python burst-evidence.py`、`python build-review.py`重建统计及报告；模拟复现入口gear-run.py，后处理gear-summarize.py。
"""
for key, value in measured.items():
    markdown = markdown.replace(f"__{key}__", value)
(ROOT / "review.md").write_text(markdown, encoding="utf-8")

slot_names = dict(zip("head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand".split(), "头部 项链 肩部 披风 胸甲 护腕 手套 腰带 腿甲 鞋子 戒指一 戒指二 饰品一 饰品二 武器".split()))
gear_rows = []
for row in gear["equipment"]["slot_comparison"]:
    values = []
    for actor in ("user", "elite"):
        item = row[actor]
        level = row.get(actor + "_wcl_item_level", item["item_level"])
        values.append(f'<a href="https://www.wowhead.com/cn/item={item["item_id"]}" target="_blank" rel="noopener">{html.escape(item["name"])}</a><br><small>{level} · ID {item["item_id"]}</small>')
    gear_rows.append(f'<tr><th>{slot_names.get(row["slot"], row["slot"])}</th><td>{values[0]}</td><td>{values[1]}</td></tr>')

page = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>沙僧 × Bisset · 爆发与平稳期复盘 · 2026-10-26</title><style>
:root{color-scheme:dark;--bg:#101814;--panel:#18241e;--line:#34463b;--text:#edf2e8;--muted:#a8baae;--gold:#e5bc68;--green:#83c9a2}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1180px;margin:auto;padding:38px 24px 70px}a{color:var(--gold);text-underline-offset:4px}nav{display:flex;gap:18px;flex-wrap:wrap;border-block:1px solid var(--line);padding:13px 0;margin:25px 0 40px}h1{font-size:clamp(29px,4.2vw,48px);line-height:1.3;font-family:Georgia,"Microsoft YaHei",serif;margin:16px 0}h2{font-size:25px;margin:0 0 18px}h3{font-size:19px;color:var(--green)}.eyebrow{color:var(--gold);letter-spacing:2px;font-size:12px}.muted,small{color:var(--muted)}section{border-top:1px solid var(--line);padding:32px 0;scroll-margin-top:15px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:25px 0}.card{background:var(--panel);padding:20px;border-top:2px solid var(--gold)}.big{font-size:32px;color:var(--gold)}.notice{padding:16px 20px;border-left:3px solid var(--gold);background:#20291d;margin:20px 0}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:630px;font-size:14px}th,td{text-align:left;vertical-align:top;padding:11px 13px;border-bottom:1px solid var(--line)}th{color:var(--green)}select,button{color:var(--text);background:var(--panel);border:1px solid #6d826d;border-radius:4px;padding:10px 12px;font:inherit;max-width:100%}.controls{display:flex;flex-wrap:wrap;gap:14px;margin:18px 0}.controls label{display:grid;gap:5px}.timeline{width:100%;min-width:700px}.timeline text{font-family:system-ui,"Microsoft YaHei",sans-serif;fill:#edf2e8;font-size:12px}.pill{display:inline-block;border:1px solid var(--line);border-radius:3px;padding:2px 8px;margin:3px 8px 3px 0;color:var(--muted);font-size:12px}.training{counter-reset:training}.training article{padding:15px 0;border-bottom:1px solid var(--line)}.training h3:before{counter-increment:training;content:"0" counter(training) " / ";color:var(--gold)}.gallery{display:grid;grid-template-columns:1fr 1fr;gap:15px}.gallery img{width:100%;height:auto;display:block}summary{cursor:pointer;color:var(--gold)}.evidence{font-size:14px}li{margin:8px 0}footer{font-size:13px;color:var(--muted);margin-top:30px}svg{display:block}@media(max-width:700px){main{padding:22px 16px}.cards{grid-template-columns:1fr}.card{padding:13px 17px}.big{font-size:27px}.gallery{grid-template-columns:1fr}table{font-size:13px}section{padding:25px 0}}@media print{body{background:white;color:black}nav,.controls{display:none}.card,.notice{background:#eef3ef}.scroll{overflow:visible}a,th,h3{color:#2b6347}section{break-inside:avoid}table{min-width:0}}
</style></head><body><main>
<div class="eyebrow">2026-10-26 / WINDWALKER FIELD REVIEW</div><h1>沙僧 × Bisset<br>把爆发接力与平稳期分开看</h1><p class="muted">以真实施法、增益和逐跳伤害复盘。当前配装另做控制模拟；每条判断保留证据边界。</p>
<nav><a href="#findings">核心发现</a><a href="#burst">爆发窗口</a><a href="#steady">平稳期</a><a href="#gear">装备对照</a><a href="#practice">下一把训练</a><a href="#sources">证据与下载</a></nav>
<div class="cards"><div class="card"><div class="big">63.4% / 76.4%</div><div>怒雷伤害带青龙 · 沙僧 / 参考场</div><small>实际伤害额加权，含套装额外命中</small></div><div class="card"><div class="big">9/48 · 1/59</div><div>普通青龙无怒雷起手的窗口</div><small>复查入口；目标死亡或职责仍需逐窗排除</small></div><div class="card"><div class="big">+15 / +23</div><div>同副本，不同层数与拉法</div><small>单个指定高手参考；不计算纯手法差距百分比</small></div></div>
<section id="findings"><h2>先把判断说准确</h2><ol>__FINDINGS__</ol><p>两场均为天神御师、玩家零死亡。你所选日志同层百分位97；全程382K对547K伴随显著拉怪、装备、构筑和目标寿命差异。完整cast/buff/怒雷/旭日与晨晖damage已取完分页。</p><div class="notice"><strong>构筑先校准：</strong>你用乾元延长5秒节点，实际通常20秒；Bisset用乾元冷却缩短20秒节点，实际通常15秒，且有白字攻速节点。不能用同一套乾元结束秒数判定谁漏技能。白虎间隔中位数110.3秒对91.7秒，也需要结合更多分包空档解释。</div></section>
<section id="burst"><h2>爆发期：先看青龙接力，再看总次数</h2><p>首轮你的旭日29.142秒与晨晖29.504秒均暴击，30.952秒已跟怒雷。这是一条真实分支。随后33.540秒获得升龙青龙，37.450秒被天神大青龙接替，区间内没有怒雷起手。</p><p>43.411秒的怒雷起手时大青龙还剩34毫秒，正常五个脉冲完整，但仅约20.8%该条伤害带青龙；Bisset 44.457秒那条全部带青龙。重点练前段接力与末段覆盖，不能把后四脉冲没增益说成断条。</p>
<div class="controls"><label>参考角色<select id="actor"><option value="shaseng">沙僧 · +15</option><option value="elite">Bisset · +23</option></select></label><label>实际白虎窗口<select id="window"></select></label></div><p id="window-note" class="muted"></p><div class="scroll"><svg id="timeline" class="timeline" viewBox="0 0 1000 220" role="img" aria-label="白虎后45秒的三种青龙与怒雷时间轴"></svg></div><p class="muted">图中45秒只是观察范围，青龙条使用实际apply/remove。圆点是怒雷起手，不代表整条通道覆盖。</p><div class="scroll"><table><thead><tr><th>白虎后</th><th>战斗时间</th><th>玩家技能 / 机制事件</th><th>当时青龙</th></tr></thead><tbody id="sequence"></tbody></table></div>
<h3>旭日暴击后的判断</h3><p>零暴、单暴、双暴会改变怒雷转好的时点。双暴是两次各自暴击的基础减冷却，仍要看剩余冷却、资源和恢复速率。先确认怒雷是否可用，再处理套装神鹤、旭日解锁升龙或其他填充。首轮双暴参考场14次、你21次是随机结果与状态分布，不能用它作技能评分。</p><p>本轮普通/大青龙实际通常约6秒，乾元青龙约4秒。旧DBC的8秒与当前日志不一致，时间轴以实服事件为准。材料里的7怒雷9神鹤是带条件的完整示范，不用它考核每个固定30秒窗。</p></section>
<section id="steady"><h2>平稳期：Boss与小怪分开</h2><p>只在可识别pull区间统计。实际增益段=白虎、乾元、任一青龙或天神通道存在；平稳代理段=六种皆无，仍可能有饰品和嗜血。CPM是七类核心施法次数/分钟，不是GCD利用率。</p><div class="controls"><label>场景<select id="scope"><option value="trash_buff_burst">小怪 · 实际增益段</option><option value="trash_buff_steady">小怪 · 平稳代理段</option><option value="boss_buff_burst">Boss · 实际增益段</option><option value="boss_buff_steady" selected>Boss · 平稳代理段</option></select></label></div><div class="scroll"><table><thead><tr><th>技能/口径</th><th>沙僧</th><th>Bisset</th></tr></thead><tbody id="metrics"></tbody></table></div><div class="notice">小怪pull总体核心CPM为37.45与37.41，不能把全程次数差全部解释为平稳期手慢。Boss平稳段你神鹤更多、旭日/幻灭更少；Boss仍可能有小怪，需排除套装、赤精与目标差异后才改优先级。</div><p>可回看的Boss窗口：普通青龙08:12.537–08:18.533，怒雷08:18.722；普通青龙08:39.205–08:45.200，怒雷08:45.406。不是简单要求再按快0.2秒；应在升龙前看怒雷余下冷却、旭日结果和真气，规划整个接力。</p></section>
<section id="gear"><h2>装备：结构已接近，先补护甲槽</h2><p>当前人物页均装331.75对334.81。你已拥有同款晋升武器、项链和贪婪心；祖尔金仍334。腰、手、腿、肩321是后续提升位，Bisset自己也有321肩。你所选旧日志项链334，最新导出已341，不能用当前模拟直接倒推旧场伤害。</p><div class="scroll"><table><thead><tr><th>部位</th><th>沙僧最新实装</th><th>Bisset最新实装</th></tr></thead><tbody>__GEAR_ROWS__</tbody></table></div><p class="muted">晋升件表内用当前WCL341；物品链接为普通参考。旧DBC解析340，原始数据在gear-items.json保留。Bisset的制造腿由套装头补四件，你单换腿会掉四件。</p><div class="scroll"><table><thead><tr><th>独立控制候选</th><th>大米合成模型</th><th>单体模型</th></tr></thead><tbody><tr><td>331普通暴击精通制造腰替321腰</td><td>+0.94%</td><td>+0.40%</td></tr><tr><td>334邪恶戒替331制造戒，保留虫群戒</td><td>+0.71%</td><td>−0.03% · 误差内</td></tr><tr><td>高手整装，固定沙僧种族/天赋</td><td>+1.77%</td><td>+1.67%</td></tr></tbody></table></div><p>6000次341兼容模型。大米为支持的DungeonSlice360秒，单体Patchwerk240秒；不是毒牙祭坛路线实测。单件行动用历史前驱连续性模型，整装双方用原导出属性模型，基准分开。单项收益不能相加。</p><p>腕、鞋、制造戒已是暴击精通；不建议全改急速精通。当前静态最高评分仍精通，鲁莽按喝药瞬间评分选择，动态触发可能改选。火花、金币、毒液石和背包余额未知，以上仅候选、不记消费。</p><a href="gear-review.md">查看完整属性、误差、模型与配装证据 →</a></section>
<section id="practice" class="training"><h2>下一把只练三件事</h2><article><h3>青龙接力</h3><p>同时显示怒雷冷却、三种青龙剩余时间、套装层数。标出目标仍存活的普通青龙空窗，先减少可避免空窗；怒雷开始吃到buff与全部伤害吃到buff分开记。</p></article><article><h3>旭日后重新判断</h3><p>分别识别主旭日与晨晖结果。确认怒雷可用、资源足够才及时接怒雷；未好则按单体或AOE优先级衔接。不预设每发都双暴，也不为避免末段半覆盖无限等下一青龙。</p></article><article><h3>单目标与五目标各练一段</h3><p>单目标复查无套装、无赤精时的神鹤是否挤占已可用技能；五目标优先核对套装神鹤与有效命中。每把选一个60秒平稳段与一次白虎窗口复盘，先追稳定，再追示范上限。</p></article></section>
<section id="sources" class="evidence"><h2>证据与可复现产物</h2><p><a href="review.md">完整中文复盘</a> · <a href="cast-review.md">完整逐窗与平稳期统计</a> · <a href="burst-evidence.json">旭日配对/怒雷逐跳数据</a> · <a href="mechanics-review.md">机制与源码定位</a> · <a href="gear-summary.json">模拟结构化结果</a></p><ul><li><a href="https://cn.warcraftlogs.com/reports/G9HVRL18nAkzFyab?fight=4&type=damage-done&source=2" target="_blank" rel="noopener">沙僧 · 毒牙祭坛+15 · 10月24日</a></li><li><a href="https://cn.warcraftlogs.com/reports/4Ab97gnVjKhZP1Nf?fight=28&type=damage-done&source=1" target="_blank" rel="noopener">Bisset · 毒牙祭坛+23 · 10月25日</a></li><li><a href="https://ngabbs.com/read.php?tid=47391002" target="_blank" rel="noopener">NGA原帖</a>、<a href="references/user-windwalker-quickstart.md">用户本地速成指南</a>；示范条件与实服事件分开。</li><li><a href="https://github.com/simulationcraft/simc/blob/73a372b76188c703e48729caded3258cdc5b726b/engine/class_modules/monk/sc_monk.cpp" target="_blank" rel="noopener">SimC固定版本武僧模块</a>；DBC停在10月22日，当前341用显式覆盖，实服青龙时长按日志。</li></ul><details><summary>查看用户补充的五张攻略图</summary><div class="gallery">__GALLERY__</div></details><p class="muted">只完成一场指定参考对一场个人日志；没有额外完成团本Boss样本，不声称群体规律或纯操作收益百分比。无完整资源/客户端冷却记录时，空窗与后续动作仅作复查候选。</p></section><footer>旧研究已推送 main · 50b6c6e。本轮研究位于 analysis/shaseng-wcl-2026-10-26；未自动提交。所有时间以各场战斗起点为零。</footer>
<script id="review-data" type="application/json">__DATA__</script><script>
'use strict';const D=JSON.parse(document.getElementById('review-data').textContent);const $=id=>document.getElementById(id);const labels={'443421':'升龙青龙','1238904':'乾元青龙','443616':'天神大青龙'};const time=t=>`${Math.floor(t/60).toString().padStart(2,'0')}:${(t%60).toFixed(3).padStart(6,'0')}`;function cell(row,text,tag='td'){const el=document.createElement(tag);el.textContent=text;row.append(el)}
function windows(){const s=D.samples[$('actor').value];$('window').replaceChildren(...s.white_windows.map((w,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`第${w.index}次 · ${time(w.relative_s)} · ${w.anchor_pull_kind==='boss'?'Boss':'小怪'}`;return o}));draw()}
function draw(){const s=D.samples[$('actor').value],w=s.white_windows[Number($('window').value)],t=w.relative_s;const svg=$('timeline');svg.replaceChildren();const ns='http://www.w3.org/2000/svg';function shape(tag,attrs,text){const n=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text)n.textContent=text;svg.append(n);return n}for(let i=0;i<=45;i+=5){const x=145+i*18;shape('line',{x1:x,x2:x,y1:15,y2:190,stroke:'#34463b'});shape('text',{x,y:211},`+${i}s`)}
for(const[id,y,color]of[['1238904',28,'#d5b367'],['443421',73,'#65b5a3'],['443616',118,'#7e99dc']]){shape('text',{x:0,y:y+16},labels[id]);for(const v of s.buff_intervals[id]){const lo=Math.max(t,v.start_relative_s),hi=Math.min(t+45,v.end_relative_s);if(hi>lo){const bar=shape('rect',{x:145+(lo-t)*18,y,width:(hi-lo)*18,height:23,fill:color,rx:3});const title=document.createElementNS(ns,'title');title.textContent=`${time(v.start_relative_s)}–${time(v.end_relative_s)}`;bar.append(title)}}}
shape('text',{x:0,y:180},'怒雷起手');for(const a of s.cast_ledger.filter(a=>a.spell_id===113656&&a.relative_s>=t&&a.relative_s<t+45)){const p=shape('circle',{cx:145+(a.relative_s-t)*18,cy:176,r:5,fill:'#f0cf7d'});const title=document.createElementNS(ns,'title');title.textContent=time(a.relative_s);p.append(title)}
$('window-note').textContent=`${s.name} · 白虎后固定30秒内：怒雷${w.cast_counts['113656']}、神鹤${w.cast_counts['101546']}、乾元${w.cast_counts['1249625']}。下图和动作表展示45秒，不能与完整爆发示范直接同分母比较。`;
$('sequence').replaceChildren();for(const a of s.cast_ledger.filter(a=>a.relative_s>=t&&a.relative_s<t+45&&![393056,109132].includes(a.spell_id))){const tr=document.createElement('tr');cell(tr,`+${(a.relative_s-t).toFixed(3)}s`);cell(tr,time(a.relative_s));cell(tr,a.name);cell(tr,a.active_buff_ids.filter(id=>labels[id]).map(id=>labels[id]).join('、')||'—');$('sequence').append(tr)}}
function metrics(){const scopes=['shaseng','elite'].map(k=>D.samples[k].scopes[$('scope').value]);$('metrics').replaceChildren();for(const[id,label]of[['duration_ms','该分段总时长'],['core_cpm','核心施法/分钟'],['113656','怒雷/分钟'],['101546','神鹤/分钟'],['107428','旭日/分钟'],['100784','幻灭/分钟'],['100780','猛虎/分钟'],['467307','疾风踢/分钟'],['152175','升龙/分钟']]){const tr=document.createElement('tr');cell(tr,label,'th');for(const s of scopes){const n=id==='duration_ms'?s[id]/1000:id==='core_cpm'?s[id]:s.spell_cpm[id];cell(tr,n.toFixed(2)+(id==='duration_ms'?'秒':''))}$('metrics').append(tr)}}
$('actor').addEventListener('change',windows);$('window').addEventListener('change',draw);$('scope').addEventListener('change',metrics);windows();metrics();
</script></main></body></html>'''
page = page.replace("__FINDINGS__", "".join(f"<li>{html.escape(text)}</li>" for text in recommendations))
page = page.replace("__GEAR_ROWS__", "".join(gear_rows)).replace("__GALLERY__", "".join(f'<a href="references/nga-guide-{i}.png"><img loading="lazy" src="references/nga-guide-{i}.png" alt="用户补充攻略第{i}张"></a>' for i in range(1, 6)))
page = page.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
page = page.replace("首轮双暴参考场14次、你21次", "全程匹配到的双暴参考场14次、你21次")
page = page.replace("本轮普通/大青龙实际通常约6秒，乾元青龙约4秒。旧DBC的8秒与当前日志不一致，时间轴以实服事件为准。", "本轮普通/大青龙实际通常约6秒，乾元青龙约4秒。原始DBC列8秒，但模拟有效增益输出已为6秒/4秒，与日志相符；不能用原始字段代替有效运行时长。时间轴使用实服事件。")
page = page.replace('<section id="gear">', '<p>套装消费复查：你132次套装增益移除中，123次接神鹤、5次旭日、4次疾风踢。小怪pull内有2旭日、4疾风踢消费；先回看03:10.343、05:39.370及11:03.469、17:02.483、17:20.917、20:42.682时是否仍有多个有效目标。参考场非神鹤消费均在Boss pull。pull类型不等于瞬时目标数，这6次不是已判定的6次失误。</p><section id="gear">')
for old, key in (("+0.94%", "waist_331_cm_slice"), ("+0.40%", "waist_331_cm_raid"), ("+0.71%", "raid_ring_334_slice"), ("−0.03%", "raid_ring_334_raid"), ("+1.77%", "elite_slice"), ("+1.67%", "elite_raid")):
    page = page.replace(old, measured[key])
talent_note = f'<p>固定你的最新装备与熊猫人种族，换Bisset完整天赋的3500次敏感性模型：大米{measured["talents_slice"]}、单体{measured["talents_raid"]}。这是整套天赋对照，不是单个节点的因果收益。可作为木桩试验，先选择20秒延长流或15秒短冷却流，再练对应节奏。</p>'
page = page.replace('<section id="steady">', talent_note + '<section id="steady">')
assert "__DATA__" not in page and "__GEAR_ROWS__" not in page
(ROOT / "review.html").write_text(page, encoding="utf-8")
print("Rendered review.md and interactive review.html from complete logs and 341-compatible sims.")
