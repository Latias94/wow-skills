from pathlib import Path
from datetime import datetime
import json,re,statistics
p=Path(__file__).resolve().parent
root=p.parents[1]
read=lambda f:json.loads(f.read_text(encoding='utf-8'))
intake=read(root/'snapshots/2026-11-10-2203.items.json')
elite=read(p/'elite-evidence.json')
icons=read(p/'item-icons.json')
old=read(root/'analysis/2026-10-29/report-data.json')
tips=read(p/'candidate-tooltips.json')
gem_names={str(g['id']):g['name'] for item in old['equipment'] for g in item.get('gems',[])}
gem_names.update({k:v['name'] for k,v in tips.items()})
models=('slice','st','aoe')
keys=['current','legs_h7','legs_delve','bag_gloves_hm','ring_268249','ring_268252','owned_h5_prepared','core_h7','target_mc_sockets','target_mh_keep_crafted_ring']
labels={
 'current':'当前实装：11月10日22:03',
 'legs_h7':'只换334盘卷妖术护腿（H7）',
 'legs_delve':'只换334雾猎者腿甲（迷宫备选）',
 'bag_gloves_hm':'只换背包331急精制作手（保四件套）',
 'ring_268249':'334邪恶炼金师指环替换制作戒（同孔）',
 'ring_268252':'334爪戒替换制作戒（升满、有孔、镶嵌附魔）',
 'owned_h5_prepared':'已有318爪戒替换制作戒（补镶嵌附魔）',
 'core_h7':'H7腿＋腰＋披风；奥纹由披风移到鞋',
 'target_mc_sockets':'目标B：H7三件＋邪炼戒＋三孔＋致命紫晶',
 'target_mh_keep_crafted_ring':'目标A：保留制作戒，H7三件＋三孔＋迅捷紫晶'}
measurements={m:{} for m in models}
for mode in models:
 for key in keys:
  row=read(p/f'live70783-{mode}-{key}-6000-26111029.validation.json')
  assert row['accepted'] and row['tier_count']>=4 and row['lining_count']==2
  measurements[mode][key]=row
comparisons=[]
for key in keys:
 values={}
 for mode in models:
  r=measurements[mode][key];b=measurements[mode]['current']
  values[mode]={'dps':r['dps'],'ci':f"±{r['ci95']:,.1f}（95%半宽）",'ci95_half_width':r['ci95'],'delta':100*(r['dps']/b['dps']-1),'samples':r['samples'],'iterations':6000,'seed':26111029}
 comparisons.append({'key':key,'label':labels[key],'values':values})
all_runs=[read(f) for f in p.glob('live70783-*.validation.json')]
assert all(r['accepted'] for r in all_runs)
(p/'comparison-results.json').write_text(json.dumps({'recorded_at':datetime.now().astimezone().isoformat(),'finalists':comparisons,'all_native70783_runs':all_runs,'methodology':'Finalists6000 iterations,independent seed26111029;screen2000 seed26111011. Model-specific means only;CI fields are95% half-widths,not standard errors or practical prediction intervals.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stats(key,seed=26111003):return read(p/f'live70783-stats-{key}-20-{seed}.validation.json')['stats']['stats']
current=stats('current',26111001);target=stats('target_mh_keep_crafted_ring')
stat_specs=[('crit','暴击','crit_rating','crit_pct','前五27–33%；等级593–886','通过腿、腰、披风与宝石整套调整，目标A为31.28%。'),('haste','急速','haste_rating','haste_pct','前五18–23%；等级814–1011','目标A为20.23%；合剂与宝石取向应随整套复测。'),('mastery','精通','mastery_rating','mastery_pct','前五71–91%；等级1035–1431','当前低于前五中位数；目标A为87.13%。'),('vers','全能','versatility_rating','versatility_pct','前五2–7%；多数约2%','维持低全能取向，生存需求另行权衡。')]
stats_cards=[{'name':name,'rating':current[r],'percent':current[pct]*100,'comparison':comparison,'advice':advice} for _,name,r,pct,comparison,advice in stat_specs]
slot_names=dict(zip('head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand'.split(),'头部 项链 肩部 披风 胸部 护腕 手部 腰带 腿部 鞋子 戒指一 戒指二 饰品一 饰品二 双手武器'.split()))
notes={
 'head':('化生前驱271875','334；保留特效13847。13696不代表已有孔；当前无宝石。'),
 'neck':('当前341核心装备','与前五5/5同款；两孔均已镶嵌。'),
 'shoulder':('雾猎者护肩272244化生','334急速暴击前驱；当前导出缺肩附魔，可补8001生存附魔。'),
 'back':('331制作，奥纹','保留方案可继续用；换H7披风前把奥纹移至现有制作鞋。'),
 'chest':('化生前驱281236','334，保留H10胸特效14049；本次不作为替换目标。'),
 'wrist':('331制作，奥纹','当前双奥纹之一；目标保留。13696不加孔。'),
 'hands':('狂热防御护手251124化生','334暴急带吸血；已有331急精制作手可作切片备选，单体/五目标无稳定优势。'),
 'waist':('331暴击精通制作','H7急精334为后续候选；当前无孔。'),
 'legs':('巧手交易马裤251130化生','321，唯一明显低装等护甲槽；首补334急精H7腿或迷宫腿。'),
 'feet':('331制作','模拟解析为暴击精通。目标A保留此鞋并承接披风奥纹，双奥纹总数仍为2。'),
 'finger1':('当前334虫群戒','前五5/5、前50中47/50使用；保留其伤害特效。'),
 'finger2':('331暴击精通制作','当前199暴击＋199精通（不含宝石）。可保留到目标A；无需因318爪戒已获得就替换。'),
 'trinket1':('当前341乌心','前五5/5、前50中50/50使用。'),
 'trinket2':('当前341触须','前五5/5、前50中42/50使用；不为通用指南的被动饰品名单退回祖尔金。'),
 'main_hand':('当前341深渊巢魔长柄','前五5/5、前50中50/50使用，保留特效13846与附魔8689。')}
equipment=[]
for slot,fields in intake['gear'].items():
 namelevel=intake['names'][slot];name=re.sub(r' \(\d+\)$','',namelevel);level=int(re.search(r'\((\d+)\)$',namelevel).group(1))
 source,note=notes[slot]
 equipment.append({'slot':slot_names[slot],'name':name,'id':int(fields['id']),'level':level,'bonus':fields.get('bonus_id',''),'icon_data':icons.get(fields['id'],''),'source':source,'note':note,'gems':[{'id':int(g),'name':gem_names.get(g,g)} for g in fields.get('gem_id','').split('/') if g]})
players=[]
for player in elite['current_player_samples']:
 s=player['secondary_stats']
 players.append({'name':player['name'],'score':player['mythic_plus_score'],'level':player['average_item_level'],'url':player['profile_url'],**{key:s['versatility' if key=='vers' else key]['percent'] for key in ('crit','haste','mastery','vers')}})
usage=[{'name':'项链268265／武器268215／乌心270175','value':'各50/50','note':'11月10日天神御师大米专页；装备同款率不表示单件装等或绿字相同。'},{'name':'触须281215／虫群戒281029','value':'42/50／47/50','note':'两饰品与两戒按持有人统计；不能把两栏相加当玩家总数。'},{'name':'331制作戒240949','value':'14/50；前五中2/5','note':'顶尖配装也保留制作戒；第二戒存在多种可行组合。'},{'name':'H7腰268256／披风268253','value':'23/50／21/50','note':'已有制作披风也有17/50使用，换披风需一起安排美化。'},{'name':'H5爪戒268252','value':'4/50；本次前五0/5','note':'使用率不是个人最优证据；本角色三模型替换均下降。'},{'name':'奥纹','value':'50人共97个美化实例','note':'不能解释成97名玩家；前五四人双奥纹，一人混用其他美化。'}]
source_list=[{'title':'Murlok天神御师大米前50：11月10日18:03更新','url':'https://murlok.io/monk/windwalker/conduit-of-the-celestials/m%2B'},{'title':'Method J-Funk装备指南（10月14日，12.1.5）','url':'https://www.method.gg/guides/windwalker-monk/gearing'},{'title':'Method属性与消耗品（10月14日）','url':'https://www.method.gg/guides/windwalker-monk/stats-races-and-consumables'},{'title':'Icy Veins装备与化生来源属性说明（10月12日）','url':'https://www.icy-veins.com/wow/windwalker-monk-pve-dps-gear-best-in-slot'},{'title':'迷宫神话2/6兑换物品与三碎片要求','url':'https://www.wowhead.com/news/myth-2-6-piece-of-loot-now-available-from-labyrinths-383603'},{'title':'顶级蛮兵爪戒334完整提示','url':tips['268252']['source_url']},{'title':'邪恶炼金师指环334提示','url':tips['268249']['source_url']},{'title':'无瑕迅捷紫晶：16精通＋7急速','url':tips['240900']['source_url']},{'title':'SimulationCraft官方70783源码：de11f57','url':'https://github.com/simulationcraft/simc/tree/de11f57df75dda668bae6ac7043a43b98831fa96'}]
limits=[
 '高手资料：11月10日原站天神御师榜单前五，评分4159–4259；完整专页50人4026–4259，覆盖美欧韩台，不含国服。个人页约16:59更新；单件装等、化生前驱和属性增益口径并非全部已知。',
 '当前与目标百分比由70783原生数据计算；显式关闭合剂、食物、强化符文、药水、武器油、团队增益和嗜血，保留天赋、装备和种族常驻效果。20次短跑仅取战前静态属性，不作DPS证据。',
 '配装对照固定用户当前天赋、Omnium、种族；无团队增益及嗜血，统一精通合剂2、哈籁尼尔盛宴、虚触符文、鲁莽药水2、凤凰油2。数据不能直接预测你的实战秒伤。',
 '初筛2000次seed26111011，决赛复测6000次seed26111029。表中仅展示独立seed的6000次复测，样本有效5999。区间为各均值95%半宽；相近区间不等于完成统计等效或配对误差检验。',
 '大米切片DungeonSlice360秒，单体Patchwerk240秒，五目标Patchwerk90秒，固定战斗时长。均valid_fight_style=true，无严重诊断。它们是模型，不是实际高层路线或全局BiS证明。',
 '可获取范围由用户确认：H团本R币＋大米/低保，普通神话装334、制作331、武器/项链/饰品现有341；排除M7/M8不可达9/6。目标装备与额外三孔均是假设，尚未记为获得或已经打孔。',
 '目标A保留制作戒，三颗已有普通宝石与三颗新增孔统一240900（16精通7急速），钻石仍240983。头腕腰新增13695真实孔；目前的13696不加孔。实际打孔器资源未知。',
 '目标B同时更换334邪恶炼金师戒和240898宝石；A/B差值是整套差值，不能全部归因于戒指。隔离戒指的同孔/同宝石控制已保留在初筛结果中。',
 '目标H7普通装备缺实际奖励完整链接，因此固定334并公开比较bonus；来源绿字取当前数据库。新戒均按一孔对比，318H5原始空孔/无附魔单独保留。实际奖励副属性、孔、第三属性需以完整导出复核。',
 '所有目标保持四件套与两奥纹；H7散腿与当前头肩胸手构成四件套。若改用331制作手，必须先把新腿化生为套装并保留H7急精前驱，避免只剩三件套。',
 '胸甲、虫群戒伤害不分摊与烈火符文触发目标在引擎中仍有未实服核验假设，已保留日志；模型差异和真实路线可能改变小差距选择。',
 '当前余额0来自22:03最新导出，已经包含H5新结果；不可再扣一次。当前H7完整奖励预览和排除轮次未独立验证，不提供精确掉率或保证下次必出。']
data={'meta':{'date':'2026-11-10 · 22:03最新完整快照','character':'沙僧 · 国服贫瘠之地','patch':'12.1.5.70783','content':'天神御师 · 踏风大秘境','engine':'SimC1210-01 / Live70783 / de11f57','budget_note':'R币3418＝0，3511＝0。新H5爪戒318在背包；装备与21:35相同。H团本R＋大米/低保范围，排除M7/M8的9/6。'},
 'lead':'核心装备已齐：341项链、武器、乌心、触须，334虫群戒与特效头胸均保留。\n先把321腿补到334；之后看H7腰带、披风与三孔。331制作戒可继续留到目标配装。\n已有318爪戒先留背包：即使升334并补齐宝石附魔，替换当前制作戒在三种模型都降低伤害。',
 'stats':stats_cards,'equipment':equipment,'elite':players,'usage':usage,
 'models':[{'id':'slice','label':'大米切片','detail':'DungeonSlice360秒，6000次，seed26111029；固定当前天赋/Omnium/消耗品，95%区间半宽。'},{'id':'st','label':'单体','detail':'Patchwerk240秒、1目标，6000次；与本模型当前实装基准比较。'},{'id':'aoe','label':'五目标','detail':'Patchwerk90秒、5目标，6000次；此场景目标A保留制作戒更好。'}],
 'comparisons':comparisons,
 'branches':[{'outcome':'当前可用R币：0','preferred':'本轮不再分配额外尝试','reason':'22:03余额为最新基线；H5新戒已列入R历史。','comparison':'318爪戒即便补齐同款宝石与附魔，大米切片−2.38%；升334后−2.02%。这是替换当前第二戒的结果。'},{'outcome':'获得下一枚币后','preferred':'先检查H7盘卷祭坛 · 踏风奖励预览','reason':'腿268225优先，腰268256与披风268253也可改善整套。武器268209和祖尔金270173已见历史。','comparison':'H7三件整套：切片＋1.86%、单体＋0.92%、五目标＋0.65%；单换H7腿分别＋1.25%、＋0.88%、＋0.72%。'},{'outcome':'迷宫碎片替代路线','preferred':'334雾猎者腿甲272243可替代H7腿','reason':'若能买到神话2/6版本，可升级334；与H7腿差距很小，优先实际能拿到的。肩膀已334，无需再换肩。','comparison':'单换迷宫腿：切片＋1.09%、单体＋0.74%、五目标＋0.74%。不要先把305旧腿误当可升级到334的同轨物品。'},{'outcome':'第二戒的终局选择','preferred':'目标A继续用331制作戒','reason':'前五也有2人用制作戒；目标A成本更低、五目标更好。邪炼戒268249、衔尾蛇印玺272150、妖术指环272149是替代候选。','comparison':'目标A整套＋2.98%切片／＋1.82%单体／＋1.66%五目标；目标B为＋3.16%／＋1.71%／＋1.29%。两套宝石也不同。'}],
 'actions':[{'title':'保留已齐的核心','body':'341深渊长柄、亚基项链、乌心、触须；334特效头、特效胸和虫群戒均保留。当前已五件套。'},{'title':'首补334急速精通腿','body':'H7盘卷妖术护腿，或迷宫神话轨雾猎者腿甲。当前321套腿无法凭现有英雄轨升级到334；需要神话轨新来源。拿到腿后再安排是否化生和是否用制作手。'},{'title':'H7腰、披风整套安排','body':'孤寂容器束带268256与丝质巫毒斗篷268253是后续目标。披风替换会拿掉一奥纹，需先把同一美化搬到现有331制作鞋；与护腕组成两奥纹。'},{'title':'第二制作戒保留，爪戒暂缓升级','body':'318爪戒是新增拥有物，不是当前更优替换。先保留199暴击＋199精通的331制作戒。邪炼戒等第二戒可等实际奖励或低保再复测，不优先为此花R币。'},{'title':'补三孔，再按整套选宝石','body':'目标A头／腕／腰各加一孔，合计七颗宝石：1颗现有钻石＋6颗无瑕迅捷紫晶240900。当前三颗普通宝石可先按预算换；打孔器资源和实际新装备孔位需另核。目标A无增益属性约31.28%暴击、20.23%急速、87.13%精通、1.94%全能。'},{'title':'制作手和肩附魔的处理','body':'背包331急精手仅切片约＋0.44%，单体−0.13%、五目标−0.11%，不用为此新增制作投入；当前334套手可继续使用。肩补8001阿梅达希尔之赐，属于生存补齐。'}],
 'consumables':[{'name':'无瑕迅捷紫晶240900','current':'现有普通宝石为240892、240908×2','recommendation':'目标A使用16精通＋7急速；名字带迅捷，但主属性是精通。目标B则用240898，具体随整套复测。','url':tips['240900']['source_url']},{'name':'合剂与食物','current':'本次Addon未导出实际使用情况','recommendation':'比较统一精通合剂2与哈籁尼尔盛宴；不要仅为追高手急速百分比改急速合剂。初筛当前急速合剂低约1.36%，后续装备变化后需重测。','url':'https://www.method.gg/guides/windwalker-monk/stats-races-and-consumables'},{'name':'戒指与武器附魔','current':'7967双戒；8689武器','recommendation':'本次目标保留。新H5比较已补同一附魔后仍不优于当前戒；未将空附魔损失误当成戒指属性结论。','url':'https://www.method.gg/guides/windwalker-monk/stats-races-and-consumables'},{'name':'肩部附魔','current':'334新肩未带enchant_id','recommendation':'补8001阿梅达希尔之赐，生存向；不计入本次DPS增幅。','url':tips['243991']['source_url']}],
 'limits':limits,'sources':source_list,
 'downloads':[{'title':'最新22:03完整原始SimC','path':'../../snapshots/2026-11-10-2203.simc'},{'title':'当前实装干净大米输入','path':'current-equipped.simc'},{'title':'目标A：保留制作戒的大米配装','path':'recommended-dungeon.simc'},{'title':'目标B：邪炼戒与致命紫晶备选','path':'alternate-raid-ring.simc'},{'title':'目标A单体比较输入（非团本BiS声明）','path':'comparison-single-target.simc'},{'title':'全部测量与验收结果','path':'comparison-results.json'},{'title':'高手原站证据与更新时间','path':'elite-evidence.json'},{'title':'模拟引擎与输入溯源','path':'simc-manifest.json'},{'title':'当前周余额与H5获取记录','path':'../../weeks/2026-11-05.json'}]}
(p/'report-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for key,filename,mode in [('current','current-equipped.simc','slice'),('target_mh_keep_crafted_ring','recommended-dungeon.simc','slice'),('target_mc_sockets','alternate-raid-ring.simc','slice'),('target_mh_keep_crafted_ring','comparison-single-target.simc','st')]:
 lines=(p/f'live70783-{mode}-{key}-6000-26111029.simc').read_text(encoding='utf-8').splitlines()
 header=['# November10,2026;Live70783;current user talents and Omnium.', '# '+('Owned equipped gear; explicit comparison consumables.' if key=='current' else 'Hypothetical attainable target;ordinary334/crafted331;not acquired gear.'),'# Two Arcanoweave linings and four-piece retained.','# Additional head,wrist,waist sockets in target exports require real socket resources.']
 lines=[x for x in lines if not x.startswith('#')]
 (p/filename).write_text('\n'.join(header+lines)+'\n',encoding='utf-8')
stat_rows=['|Stat|Current unbuffed|Target A unbuffed|Top-five displayed range|','|---|---:|---:|---|']
for _,name,r,pct,comparison,_ in stat_specs:stat_rows.append(f'|{name}|{current[r]:.0f} / {current[pct]*100:.2f}%|{target[r]:.0f} / {target[pct]*100:.2f}%|{comparison}|')
result_rows=['|Configuration|DungeonSlice|Single target|Five targets|','|---|---:|---:|---:|']
for c in comparisons:result_rows.append('|'+c['label']+'|'+'|'.join(f"{c['values'][m]['delta']:+.3f}%" for m in models)+'|')
md='''# Shaseng attainable Windwalker Mythic+ review — 2026-11-10

Latest complete user snapshot:22:03 CN/Barrens,Live12.1.5.70783. Equipped gear,talents and Omnium are identical to the21:35 import;bag ring268252 and current currency change are retained separately. User explicitly excludes inaccessible Mythic7/8 9/6 gear. Current roll balance is zero,already including the new H5 result.

The341 neck,weapon,Heart,Tendril and334 Swarmcaller ring match the current hero-filtered top-five item IDs. Four-piece is already active with five tier pieces. The321 leg is the clearest gear-level gap. Prioritize334 haste/mastery legs,then evaluate H7 waist/cloak as a complete set. Move the cloak Arcanoweave lining to the existing crafted boots before equipping the raid cloak.

Target A retains the owned331 crafted crit/mastery ring and334 tier hands. It adds H7 legs/waist/cloak,three real head/wrist/waist sockets,and240900 rare gems. Target B changes both the second ring and gem allocation;their difference is a complete-loadout comparison. Neither is a global BiS proof. Target A is the practical default because it retains the ring and performs better in the five-target workload. The standalone owned331 haste/mastery glove is not a universal upgrade.

'''+ '\n'.join(stat_rows)+'\n\n'+ '\n'.join(result_rows)+'''

The318 H5 ring is owned but remains in bags. Prepared318 and max334 versions both preserve one socket and use the current ring enchant/gem,so their loss is not an empty-socket or missing-enchant artifact. Do not prioritize its upgrades for this loadout. H7 legs and Myth-track Labyrinth legs are close;the existing305 bag leg must not be treated as the new Myth-track copy. Retain at least four tier pieces when switching gloves.

## Measurement and acquisition boundaries

Source commit de11f57df75dda668bae6ac7043a43b98831fa96 was built in a detached local worktree with native70783 data. The original SimC checkout and binary were preserved. Screening used2000 iterations/seed26111011;finalists used6000/seed26111029. DungeonSlice360s,Patchwerk240s single-target,andPatchwerk90s five-target are supported models. Finalist reports have5999 samples,valid_fight_style=true,no severe diagnostics,at least four tier pieces and exactly two Arcanoweave instances. CI fields are95% half-widths of each mean,not practical prediction intervals or paired-difference tests.

Damage comparisons hold the supplied talents,Omnium,race and consumables constant. Raid buffs and Bloodlust are disabled. Consumables are explicitly mastery flask2,Harandar Celebration,Void-Touched augmentation,Recklessness potion2 andPhoenix oil2. Static stat snapshots disable all these consumables. Short20-iteration identity runs supply static stats only and are not DPS evidence.

Engine assumptions still include non-split chest/Swarmcaller damage and the Rune of Unleashed Fire trigger target. Models cannot establish an actual dungeon route or eliminate mechanic uncertainty. Population stats have unknown buff basis and rounded percentages;they are not hard breakpoints. The current player sample is the first five in the November10 Conduit Mythic+ page,not an unfiltered monk list;US/EU/KR/TW only,not CN. The complete sample has50 characters and4026–4259 score.

Actual H7 reward-preview eligibility,knockout scope,Vault offers and socket-token availability remain unresolved. Current balance is not an income rate. Targets and clean target exports are hypothetical acquisitions,not ledger events. No exact bonus-roll success probability is claimed.

## Artifacts and sources

- report.html / report-data.json:Chinese user-facing report.
- comparison-results.json:all native70783 result summaries and final comparisons.
- elite-evidence.json:original-site timestamps,equipment and top-five profiles.
- candidate-tooltips.json:dated item/gem source responses.
- simc-manifest.json:engine/source/input hashes.
- ../../snapshots/2026-11-10-2203.simc:exact latest full import.
- ../../weeks/2026-11-05.json:zero balance and confirmed H5 acquisition;the latest balance is never double-debited.

'''+ '\n'.join(f"- [{s['title']}]({s['url']})" for s in source_list)+'\n'
(p/'review.md').write_text(md,encoding='utf-8')
print({'report_data_saved':True,'completed_native_runs':len(all_runs),'finalist_comparisons':len(comparisons)*len(models),'target_a_unbuffed':{k:target[k] for k in ('crit_rating','haste_rating','mastery_rating','versatility_rating')}})
