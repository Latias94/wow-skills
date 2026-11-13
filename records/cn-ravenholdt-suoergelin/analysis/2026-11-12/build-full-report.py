"""Reconcile the full18:29 import and accepted personal measurements."""

from copy import deepcopy
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import re

ROOT=Path('records/cn-ravenholdt-suoergelin')
HERE=ROOT/'analysis/2026-11-12'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now().astimezone().isoformat()
data=read(HERE/'report-data.json')
intake=read(ROOT/'snapshots/2026-11-12-1829.items.json')
icons=read(HERE/'item-icons.json')
icons.update(read(HERE/'full-report-icons.json'))
models=('slice','st','aoe')
keys=['current','ring_fill','ready','h7_chest','h8_legs','ready_h7','ready_h8','heart334_replace_zuljin','heart341_replace_zuljin','heart341_replace_tendril','core','target_haste','target_haste_h5']
labels={'current':'当前完整实装（18:29）','ring_fill':'只填虫群空孔＋7967附魔（仍318）','ready':'现装补齐：虫群334＋镶嵌附魔＋1腰孔＋鞋附魔','h7_chest':'只换334H7胸（化生，保四件套）','h8_legs':'只换334H8毒咒腿','ready_h7':'现装补齐后＋334H7胸','ready_h8':'现装补齐后＋334H8毒咒腿','heart334_replace_zuljin':'已有334乌心替祖尔金，保留触须','heart341_replace_zuljin':'乌心晋升341替祖尔金，保留触须','heart341_replace_tendril':'乌心晋升341替触须，保留祖尔金','core':'现装补齐＋H7胸＋H8腿，保留321阿曼尼戒','target_haste':'终局候选A：上述三项＋331暴急制作戒','target_haste_h5':'终局候选B：以334H5爪戒替第二戒'}
results={}
for mode in models:
    results[mode]={}
    for key in keys:
        row=read(HERE/f'full70783-{mode}-{key}-6000-26111253.validation.json')
        assert row['accepted'] and row['tier_count']>=4 and row['lining_count']==2
        results[mode][key]=row
comparisons=[]
for key in keys:
    values={}
    for mode in models:
        r=results[mode][key];base=results[mode]['current'];ready=results[mode]['ready']
        values[mode]={'dps':r['dps'],'ci':f"±{r['ci95']:,.1f}（95%半宽）",'ci95_half_width':r['ci95'],'delta':100*(r['dps']/base['dps']-1),'delta_from_ready':100*(r['dps']/ready['dps']-1),'samples':r['samples'],'iterations':6000,'seed':26111253}
    comparisons.append({'key':key,'label':labels[key],'values':values})
write(HERE/'full-comparison-results.json',{'recorded_at':now,'comparisons':comparisons,'all_runs':[read(p) for p in HERE.glob('full70783-*.validation.json')],
      'methodology':'Screen2000/seed26111231;final6000/seed26111253. Model-specific means;CI95 half-widths,not standard errors or paired tests. No measured DPS from the preliminary WCL-only import is used.'})
def snapshot(key):return read(HERE/f'full70783-stats-{key}-20-26111255.validation.json')['stats']['stats']
current=snapshot('current');goal=snapshot('target_haste');alternate=snapshot('target_haste_h5')
stats=[]
for name,rating,pct,advice in [('暴击','crit_rating','crit_pct','当前偏低，随胸腿及第二戒整体调整；不为凑35%强行牺牲急速。'),('急速','haste_rating','haste_pct','已有合理急速；本次保留240890急速为主的普通宝石。'),('精通','mastery_rating','mastery_pct','维持适量精通，原有肩膀与双奥纹制作不必为了表格重做。'),('全能','versatility_rating','versatility_pct','当前胸119＋腿120＝239全能；换两件目标后只剩项链105。')]:
    stats.append({'name':name,'rating':current[rating],'percent':current[pct]*100,'comparison':f"终局候选A：{goal[rating]:.0f}等级／{goal[pct]*100:.2f}%；前五参考见下表。",'advice':advice})
slot_names=dict(zip('head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand'.split(),'头部 项链 肩部 披风 胸部 护腕 手部 腰带 腿部 鞋子 戒指一 戒指二 饰品一 饰品二 双手武器'.split()))
native_slot={'shoulder':'shoulders','wrist':'wrists'}
names={int(x['modifiers']['id']):re.sub(r' \(\d+\)$','',x['name_level']) for x in intake['gear'].values()}
names.update({271878:'无羁深仇腿甲',240949:'精工辛多雷指环',268252:'顶级蛮兵爪戒'})
def fields(line):return dict(x.split('=',1) for x in line.split('=',1)[1].split(',') if '=' in x)
def input_gear(key):
    lines=(HERE/f'full70783-slice-{key}-6000-26111253.simc').read_text(encoding='utf-8').splitlines()
    return {l.split('=',1)[0]:fields(l) for l in lines if l.split('=',1)[0] in slot_names}
def equipment(key):
    g=input_gear(key);native=results['slice'][key]['gear'];rows=[]
    for slot,f in g.items():
        v=native[native_slot.get(slot,slot)];ident=int(f['id'])
        green='／'.join(f'{label}{v[field]}' for label,field in [('暴击','crit_rating'),('急速','haste_rating'),('精通','mastery_rating'),('全能','versatility_rating')] if v.get(field))
        note='导入模型实际绿字：'+green+'。'
        source='已有装备保留'
        if f.get('redirected_base_stats'):
            source='化生前驱'+f['redirected_base_stats'];note+=' 悬浮默认套装绿字不能替代来源继承值。'
        if slot=='chest':note+=' 当前前驱272255为71急速119全能；目标新来源268222需先化生再穿。'
        if slot=='legs':note+=(' 目标毒咒腿，可化生为271455保留来源效果。' if ident==271878 else ' 当前腿含120全能；背包321原生套腿初筛不占优。')
        if slot=='waist':note+=(' 目标使用已拥有的1个打孔器新增此孔；尚未记为使用。' if '13695' in f.get('bonus_id','').split('/') else ' 当前13696不加孔；唯一打孔器建议给此334腰。')
        if slot=='finger1':note+=(' 当前无宝石/附魔，318神话1/6；可以升级同一枚。' if key=='current' else ' 同一枚现有虫群戒，假设升级334并补宝石、7967附魔。')
        if slot=='finger2' and ident==240949:source='331普通制作候选';note+=' 新制作需火花、80神话纹章及金币等，不新增美化。当前97纹章优先留给已有戒和新R护甲升级。'
        if slot=='finger2' and ident==268252:source='H5候选第二戒';note+=' 尚未获得；与331制作戒整套差距很小，不占当前唯一R币。'
        if slot in ('wrist','feet'):note+=' 保留8790暴急铭文与奥纹；crafted_stats占位值不覆盖铭文。'
        if slot=='feet' and key=='current':note+=' 当前无鞋附魔。'
        if slot.startswith('trinket'):note+=' 341触须＋祖尔金为本次三模型优先保留组合；334乌心已在背包。'
        rows.append({'slot':slot_names[slot],'name':names[ident],'id':ident,'level':v['ilevel'],'bonus':f.get('bonus_id',''),'icon_data':icons.get(str(ident),''),'source':source,'note':note,
                     'gems':[{'id':int(i),'name':'费解之永歌钻石' if i=='240983' else '无瑕致命榄石' if i=='240890' else '无瑕迅捷榴石'} for i in f.get('gem_id','').split('/') if i and int(i)>0]})
    return rows
eq=equipment('current');target=equipment('target_haste')
data.update(meta={'date':'2026-11-12 · 完整SimC18:29','character':'索尔葛林 · 屠戮者武器战','patch':'12.1.5.70783','content':'大秘境 · 完整个人模拟与1币路线','engine':'原生70783 / de11f57 · 6000次复测','budget_note':'已确认：1枚R币、1个宝库打孔器、10枚晋升毒液石、10枚当季潮汐火花、97神话雾纹章。乌心334已在背包。当前未记录任何计划消耗。'},
      lead='先补现装：虫群戒填空孔＋7967附魔，已有318神话戒升级334；唯一打孔器给334腰。\n按完整配装复测，334H8毒咒腿的装备收益高于334H7胸：两边都能定向时先H8腿；若H8有杂项而H7预览只剩胸，则先H7。\n341触须＋祖尔金保留；已有334乌心即使晋升341也未超过当前组合，10枚毒液石先留。第二戒不占当前唯一R币。',
      stats=stats,equipment=eq,target_equipment=target,comparisons=comparisons,
      models=[{'id':'slice','label':'大米切片','detail':'DungeonSlice360秒；6000次、独立seed26111253，当前天赋和Omnium固定。表中区间为95%均值半宽。'},
              {'id':'st','label':'单体','detail':'Patchwerk240秒、1目标；相对本模型当前完整实装，不等同团本最优配装。'},
              {'id':'aoe','label':'五目标','detail':'Patchwerk90秒、5目标；模型不是实际整把路线，机制假设见来源边界。'}])
data['branches']=[{'outcome':'唯一1枚R · 两个池都只剩目标时','preferred':'先H8无羁深仇腿甲271878','reason':'单换334腿：切片＋2.36%、单体＋2.81%、五目标＋2.15%。现装补齐后再换腿的边际收益仍高于胸。','comparison':'补齐后＋H8腿，相对当前约＋5.41%切片；相对补齐后基准额外＋2.23%。H8乌心及项链均已有R历史，但跨专精/扩展context共享排除仍以预览为准。'},
 {'outcome':'H8仍有杂项，H7预览只剩胸时','preferred':'先H7狂野精魂胸甲268222','reason':'四件H7记录明确：武器、祖尔金、腰、披风，均武器专精。H7胸升334并化生后，单换切片＋0.70%、单体＋1.25%、五目标＋0.25%。','comparison':'补齐后＋H7胸，相对当前约＋3.90%切片。先看实际奖励预览，未确认时不承诺必出。拿胸后停止继续投H7。'},
 {'outcome':'打孔器和当前戒指','preferred':'1工具给334腰；先填虫群现有空孔','reason':'现有头已一孔，腕/腰无孔。填虫群空孔＋戒指附魔单项就约＋1.95%切片；升级戒、加腰孔等整套补齐约＋3.11%。','comparison':'填空孔不消耗打孔器。腰新增孔才消耗唯一工具，计划与实际使用分开。两孔均先用240890无瑕致命榄石。'},
 {'outcome':'晋升毒液石10枚','preferred':'暂不用于334乌心','reason':'你已拥有乌心334且有一次晋升材料。晋升341后，替祖尔金切片−2.84%；替触须−4.40%。三个测试模型均未超过现有组合。','comparison':'这不是乌心永久无价值的结论；以你当前Slayer天赋/Omnium和装备为条件。它已是拥有物，不再列成待R目标。'},
 {'outcome':'胸腿补齐后的第二戒','preferred':'保留321阿曼尼过渡，再比较331暴急制作戒或334爪戒','reason':'终局制作戒方案约＋7.05%切片，爪戒方案约＋7.01%，差距小于本次误差；不为这点差异消耗唯一R币。','comparison':'现有97神话纹章需同时覆盖已有戒和新R装备升级，331制作另需80神话纹章；先看实际减免和剩余材料。10潮汐火花不是10光耀火花。'}]
data['actions']=[{'title':'立即填虫群空孔和补戒指附魔','body':'用240890无瑕致命榄石（16急速7暴击）填虫群戒自带空孔，补7967附魔；这个空孔不需要打孔器。单项复测约＋1.95%切片。'},
 {'title':'已有戒升级334，唯一打孔器给334腰','body':'当前虫群为神话1/6，可升级同一枚至334；头已有孔。打孔器优先给长期保留的H7腰带，镶240890。鞋附魔一并补齐。此整套补齐约＋3.11%切片、＋3.37%单体、＋2.72%五目标。实际纹章扣费以已有槽位水位及账号减免为准。'},
 {'title':'这1枚R按实际剩余池决定','body':'两个池都只剩目标时，先H8毒咒腿；H8有杂项而H7只剩胸时，先H7胸。H7四次历史均spec71；H8项链为spec73、乌心为spec71，跨专精与context的服务器共享排除仍需界面确认。'},
 {'title':'保留当前341武器、项链和双饰品','body':'触须＋祖尔金在三个复测模型都优于乌心替换。10枚晋升毒液石先留。H10圣光剑仅切片初筛不占优，本次不为另一武器分配R币。'},
 {'title':'不急做桥接腿或改肩膀','body':'331暴急制作腿、背包321原生套腿、改334暴急肩，当前初筛没有形成足以优先投入的优势。先解决目标胸腿和现装补齐。不要因背包套腿能变五件套就替换，五件没有额外套装奖励。'},
 {'title':'终局候选A，再新增331暴急普通制作戒','body':'保留现有双奥纹腕鞋，第三件普通制作戒不增加美化。候选A无消耗品属性约30.43%暴击、23.10%急速、29.80%精通、1.94%全能。候选B爪戒约33.46%暴击、20.04%急速；两套模型差距很小，按实际获取和成本选择。'}]
data['consumables']=[{'name':'宝石','current':'240983钻石＋240890普通宝石；虫群目前为空','recommendation':'保留现有宝石方向；两颗新增宝石用240890。更偏暴击的240906已做整套初筛，未形成优先更换依据。','url':'https://www.method.gg/guides/arms-warrior/stats-races-and-consumables'},
 {'name':'合剂与输出消耗品','current':'Addon未导出实际饮用情况','recommendation':'比较统一急速合剂2、哈籁尼尔盛宴、虚触强化符文、鲁莽药水2、凤凰油2。当前暴击合剂切片初筛不占优；面板截图计算则显式关闭这些消耗品。','url':'https://www.method.gg/guides/arms-warrior/stats-races-and-consumables'},
 {'name':'制作材料','current':'潮汐火花274476×10；神话雾纹章3446×97','recommendation':'当季火花足够构造候选，但纹章要先给已有戒和R护甲升级。331制作一般另需80神话纹章，不默认所有目标今天都能同时做完。','url':'https://www.wowhead.com/guide/midnight/item-level-gear-upgrades-dawncrests'},
 {'name':'晋升材料','current':'晋升毒液石280562×10，可支持一次晋升','recommendation':'乌心334已经拥有；本次比较不支持为了当前大米把它升341替换双饰品。先保留材料。','url':'https://nether.wowhead.com/tooltip/item/280562?dataEnv=1&locale=4'}]
data['limits']=[
 '完整原始导出18:29，客户端12.1.5.70783；天赋、Omnium、种族、专业及全部modifiers保留。当前15槽、背包40行、资源和10条R历史已独立保存，未与沙僧角色共享余额。',
 '当前与目标属性为原生导入计算的战前静态快照：关闭食物、合剂、强化符文、药水、武器油、团队增益和嗜血，保留装备、种族、天赋常驻效果。短20次跑仅取静态属性，不用于DPS排名。',
 'DPS初筛2000次seed26111231；决赛复测6000次seed26111253。最终每项5999有效样本，均支持fight_style、无严重诊断、至少4套及恰好2奥纹。置信区间为均值95%半宽，不是实际路线收益区间或配对误差检验。',
 'DPS固定当前天赋及Omnium：136814/136821/136817/136816/136822，固定急速合剂2、盛宴、虚触符文、鲁莽药水2、凤凰油2，无团队增益/嗜血。DungeonSlice360秒、单体240秒、5目标90秒，均为模型。',
 '头、肩、胸、手前驱分别281239/272260/272255/268220，已按用户完整导出保留。当前胸实际71急速119全能，头实际60急速141精通；不能改回默认套装绿字。制作腕鞋8790实际暴急覆盖crafted_stats占位字段，原始字段仍完整保留。',
 '目标普通神话334、制作331、晋升核心341，排除不可达M7/M8 9/6。H7胸/H8腿从新神话轨来源升334后才对应本表收益；它们不是R到手就334，也不代表今天全部材料都已足够。',
 '已有1枚R、1工具、10当季火花、10毒液石；目标仅使用1个新增腰孔，头保留已有孔，未凭空加腕孔。现有空虫群孔与新增腰孔收益分开。所有目标与计划未记为获得或实际支出。',
 '5=RaidHeroic，95=RaidHeroicExtended_3，均为H来源家族的itemcontext；第四字段是treasureContextLevel，不是副本难度。官方Addon定义已核验，枚举参考70448与角色70783存在版本差异。服务端跨context、跨专精共享排除未公开验证，不能据此写必出或精确概率。',
 '原始R历史H8乌心270175(spec71)、项链268265(spec73)；H7四件均spec71；H10头、坦克饰品、虫群、触须均有记录。没有把缺少某Boss历史误当该池从未R过。',
 '头与虫群伤害不分摊、烈火符文触发目标仍有引擎未实服核验假设。默认bugs=true未额外假定毒咒为头特效增加15%伤害；毒咒腿自身急速buff与当前物品伤害均在结果中实际触发。',
 '331制作戒与334爪戒整套均强于当前，但它们之间的小差距不足以排成确定名次。相近置信区间不是统计等效证明；先考虑拥有情况、R币和制作成本。',
 '武器H10、桥接制作腿、改肩、合剂与部分宝石只做2000次切片初筛，未扩称为所有场景结论。目标A/B只是在本次有界候选里更优，不是穷尽所有装备的全局BiS。',
 '高手资料为11月12日18:00前后核验的Slayer前五，个人页16:53更新；美欧韩台，不含CN。百分比取整且增益口径未知，不当硬阈值。前驱和单件完整bonus未知的高手装备没有被虚构成可复现输入。']
data['sources'] += [
 {'title':'官方SimC Addon的R历史字段定义','url':'https://github.com/simulationcraft/simc-addon/blob/83fdb00762fa0fb9ba3e3251a8fa7f3e4a92edba/bonusrolls.lua'},
 {'title':'客户端ItemContext枚举参考（build70448）','url':'https://github.com/Ketho/BlizzardInterfaceResources/blob/f3b334b33bd19fa6a0250f7922ecfa83db7fe356/Resources/LuaEnum.lua'},
 {'title':'纹章升级、减免和制作80纹章说明','url':'https://www.wowhead.com/guide/midnight/item-level-gear-upgrades-dawncrests'}]
data['downloads']=[{'title':'18:29完整原始SimC（含背包/R历史）','path':'../../snapshots/2026-11-12-1829.simc'},{'title':'当前完整实装比较输入','path':'current-full-equipped.simc'},
 {'title':'终局候选A：331暴急制作戒','path':'recommended-dungeon.simc'},{'title':'终局候选B：334H5爪戒','path':'alternative-h5-ring.simc'},
 {'title':'候选A单体复测输入（非团本BiS声明）','path':'reference-single-target.simc'},{'title':'全部测量和最终对照','path':'full-comparison-results.json'},
 {'title':'历史字段语义与服务器排除局限','path':'roll-history-interpretation.json'},{'title':'引擎和输入哈希','path':'full-simc-manifest.json'},
 {'title':'当日高手来源证据','path':'elite-evidence.json'},{'title':'当前1币与材料记录','path':'../../weeks/2026-11-12.json'}]
write(HERE/'full-report-data.json',data)
write(HERE/'full-target-slot-map.json',{'status':'Hypothetical best-tested bounded candidate,not acquired gear.','equipment':target,'alternative_ring':268252,'one_socket_token_target':'waist','tier_count':4,'arcanoweave_count':2,'current_core_budget':1})
for key,name,mode in [('current','current-full-equipped.simc','slice'),('target_haste','recommended-dungeon.simc','slice'),('target_haste_h5','alternative-h5-ring.simc','slice'),('target_haste','reference-single-target.simc','st')]:
    source=HERE/f'full70783-{mode}-{key}-6000-26111253.simc'
    lines=[l for l in source.read_text(encoding='utf-8').splitlines() if not l.startswith('#')]
    header=['# Complete user18:29 talents,Omnium and retained sources;Live70783.', '# '+('Owned current gear with explicit comparison consumables.' if key=='current' else 'Hypothetical attainable target;newH7/H8 sources,one owned socket token,not acquired gear.'), '# Ordinary334/crafted331;current ascended341;four-tier andtwoArcanoweave maintained.']
    (HERE/name).write_text('\n'.join(header+lines)+'\n',encoding='utf-8')
builder_path=Path('records/cn-barrens-shaseng/analysis/2026-10-29/build-report.py')
spec=importlib.util.spec_from_file_location('gear_report',builder_path);builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
table=builder.table(['部位','候选装备','装等','宝石','来源与条件'],[builder.equipment_row(x) for x in target],'终局候选A · 尚未获得，保4套/2奥纹，仅新增1腰孔')
section=builder.section('targets','完整目标配装',table,'目标A为331暴急制作戒，目标B换334H5爪戒。两套差距小，按获取成本选择。')
document=builder.render(data).replace('<section id="branches"',section+'<section id="branches"',1)
document=document.replace('<a href="#branches">R币与兑换</a>','<a href="#targets">目标配装</a><a href="#branches">R币与兑换</a>',1)
(HERE/'full-report.html').write_text(document,encoding='utf-8')
week=read(ROOT/'weeks/2026-11-12.json')
week['budget']={'reported_balance':1,'currency_id':3418,'reported_at':'2026-11-12T18:29:00+08:00','evidence':'Full user export bonus_roll_currencies=3418:1/3511:0;latest baseline already includes all prior spending.'}
week['snapshot']='snapshots/2026-11-12-1829.simc'
week['resources']={'current_season_sparks':{'item_id':274476,'quantity':10},'ascendant_venomstones':{'item_id':280562,'quantity':10,'cost_per_ascension':10},'myth_mistcrests':{'currency_id':3446,'quantity':97},'socket_tool':{'quantity':1,'status':'owned_unspent','evidence':'User: 我还有个宝库兑换的打孔器'},'catalyst_raw':'2813:8/3269:8/3116:8/3378:8/3465:5'}
history=next(l.split('=',1)[1] for l in (ROOT/'snapshots/2026-11-12-1829.simc').read_text(encoding='utf-8').splitlines() if l.startswith('# bonus_roll_items='))
week['observed_roll_history']=[dict(zip(('currency','source','context','treasure_context_level','item_id','loot_spec'),map(int,row.split(':')))) for row in history.split('/')]
week['history_interpretation']='All observed contexts5/95 areHeroic source family;server shared knockout across context/spec remains unverified. Do not double-debit old records.'
week['pools'][0].update(history_difficulty_separately_confirmed=True,heroic_context_family_observed=[5,95],history_loot_specs=[71],current_remaining_preview_verified=False)
week['pools'][1].update(reported_rolled_owned_ids=[270175,268265],history_loot_specs=[71,73],current_remaining_preview_verified=False)
week['pools'][3].update(reported_rolled_owned_ids=[281239,280617,281029,281215],confirmed_head_source=281239,head_predecessor_status='Confirmed by full user redirected_base_stats=281239.')
week['plan'].update(evidence='analysis/2026-11-12/full-report.html',current_allocation=1,allocation_status='Conditional proposal,not spent',
 ordered_priorities=['Prepare the ownedSwarmcaller anduse the owned socket tool on the retained334 waist.','If bothH7/H8 previews are clean,prioritizeH8Venomcursedlegs by measured value.','IfH8 has filler butH7 preview onlychest,prioritize the certainH7chest.','Hold10venomstones;do not force334Heart to341 for currentM+.','After chest/legs,compare the owned321Amani with crafted331 orH5ring;reserve crests for existing/new gear upgrades first.'])
week['unresolved']=['Actual remainingH7/H8 preview andserver knockout scope','Exact crest discounts andgold/material costs at upgrade/craftUI','CurrentVault offers andactual upcoming acquisition results']
write(ROOT/'weeks/2026-11-12.json',week)
profile=read(ROOT/'profile.json');profile.update(latest_simc='snapshots/2026-11-12-1829.simc',latest_full_simc='snapshots/2026-11-12-1829.simc',latest_items='snapshots/2026-11-12-1829.items.json',
 latest_snapshot_scope='Full addon12.1.5-04 export18:29:equipped gear,Catalyst predecessors,Omnium,bags,currencies andobserved R history;one socket tool separately user-reported.',
 latest_gear_review='analysis/2026-11-12/full-report.html',latest_gear_evidence='analysis/2026-11-12/full-review.md',target_slot_map='analysis/2026-11-12/full-target-slot-map.json',
 target_loadouts={'dungeon':'analysis/2026-11-12/recommended-dungeon.simc','alternative':'analysis/2026-11-12/alternative-h5-ring.simc','single_target_reference':'analysis/2026-11-12/reference-single-target.simc','evidence':'analysis/2026-11-12/full-report.html'},
 target_loadouts_status='Best-tested bounded full-import candidates,not acquisitions orglobalBiS;ordinary334/crafted331,one socket token,held341 core items. Primarycraft ring andH5alternative are near ties.',
 initial_source_plan='analysis/2026-11-12/report.html',roll_history_coverage='Ten observed addon tuples plususer statement;contexts5/95Heroic family,but exact server shared-exclusion scope/current previews unknown.')
write(ROOT/'profile.json',profile)
rows=['|Candidate|Slice|Single target|Five targets|','|---|---:|---:|---:|']
for c in comparisons:rows.append('|'+c['label']+'|'+'|'.join(f"{c['values'][m]['delta']:+.3f}%" for m in models)+'|')
review='''# Complete Arms/Slayer personal study — November12,2026

The full18:29 addon import supersedes the source-only WCL phase without overwriting that raw snapshot or preliminary report. Source data is nativeLive70783,de11f57. Current race,talents,Omnium,professions,modifiers andCatalyst predecessors are held fixed. Currentunbuffed model stats:25.93%crit,21.38%haste,27.79%mastery,6.37%vers. Chest272255 contributes119vers andlegs159435 contribute120vers. Crafted8790 missives resolve the exported placeholder-crafted stats tocrit/haste.

Real budget:one roll core,one socket tool,ten current-seasonSparksOfTides274476,tenAscendantVenomstones280562 and97MythMistcrests3446. The280562 stack supports one ascension. The owned334Heart was already rolled;it is not a missing acquisition. No planned action has been recorded as spent or acquired.

The current318MythSwarmcaller has an empty socket and no ring enchant. Filling and enchanting alone is about1.95% in the three final models. Preparation includes upgrading thatsame ring to334,filling/enchanting,one newwaist socket using the owned tool,andboot enchant. Currenthead already has one socket;no extra wrist socket is invented. Preparation yields3.11%slice. These stages are separate toavoid counting the same socket twice.

H8Venomcursedlegs outrankH7chest by equipment value in all final models,including after preparation. If bothremaining previews are clean,preferH8legs;whereH8still has filler butH7onlychest,prefer the certainH7result. Context5=RaidHeroic and95=RaidHeroicExtended_3;these areitemcontexts,not different resettable raid difficulties. The addon fourth field is treasureContextLevel. Server shared exclusions acrosscontext/spec remain unverified,so no exact odds or unconditional guarantee is claimed.

Both341Heart substitutions underperform the current341Tendril+Zuljin pair in the final supported models. Hold the tenvenomstones fornow. FulltargetA retains the twoArcanoweave crafts anduses an ordinary331crit/haste ring. FulltargetB uses the334H5claw ring instead. Their mean differences are small relative to uncertainty anddo not justify dedicating the currentone core toH5. The owned321Amani remains a practical bridge. Crafting a new331piece costs80Mythcrests before other costs;reserve resources forupgrading existing andnew rolled items first.

'''+ '\n'.join(rows)+'''

Screening2000 iterations/seed26111231;finalists6000/seed26111253. Final comparisons have5999samples,valid_fight_style=true,no severe diagnostics,at leastfourtier pieces andexactlytwoArcanoweave instances. DungeonSlice360s,single-targetPatchwerk240s,andfive-targetPatchwerk90s aremodels,not actual high-key routes. CI95fields arehalf-widths of eachmean,not standard errors or paired-difference tests. Similar intervals are not anequivalence proof.

AllDPSruns explicitly usehasteflask2,HarandarCelebration,VoidTouchedaugmentation,RecklessnessPotion2 andPhoenixOil2,with no raidbuffs/Bloodlust. Static20-iteration snapshots explicitly disable those consumables and are notDPS evidence. Current head14049 andSwarmcaller non-split damage,plusRuneUnleashedFire target assumptions remain unverified ingame. Defaultbugs=true does not grant a speculative additional15%head bonus whileVenomcursed. Current item actions andVenomcursed buffs are observed in resultJSON.

Clean exports are replayed separately. Target loadouts are hypothetical source-qualified334/331candidates,not acquired gear,not today’s fully funded purchase list,andnot globally optimizedBiS. The original source-only report remains dated history. Allreferences are embedded in full-report-data.json;roll-history-interpretation.json retains the source andcontext audit.
'''
(HERE/'full-review.md').write_text(review,encoding='utf-8')
print({'report':str(HERE/'full-report.html'),'finalist_comparisons':len(keys)*3,'current_rows':len(eq),'target_rows':len(target),'budget_core':1,'socket_tools':1})
