"""Publish the completed end-state comparisons without spending weekly resources."""

from copy import deepcopy
from datetime import datetime
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAR = HERE.parents[1]
REPO = HERE.parents[3]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
write = lambda p, d: p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
spec = importlib.util.spec_from_file_location('endstate', HERE / 'endstate-study.py')
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
spec = importlib.util.spec_from_file_location('renderer', HERE / 'report-renderer.py')
ui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui)
ui.MODELS = (('aoe', '五目标90秒'), ('long', '五目标180秒'), ('st', '单目标240秒'))
A = 'tune_bw_serpent_ch_mixed_crit'
C = 'tune_bw_claw_ch_mixed_crit'
B = 'finish_vaultcloak_serpent'
V = 'finish_vaultcloak_vial'
configs = study.candidates()
data = deepcopy(read(HERE / 'report-data.json'))
finals = {}
for f in HERE.glob('endstate70783-*-6000-26111393.validation.json'):
    d = read(f)
    assert d['accepted'] and d['valid_fight_style'] and d['tier_count'] >= 4
    finals.setdefault(d['model'], {})[d['key']] = d
assert all(len(finals[m]) == 12 for m, _ in ui.MODELS)
labels = {'current': '当前13:20完整实装', 'owned_endstate': '仅将已有袋子升341＋补齐终局腕腰孔',
    A: '终局A：长蛇334，披风＋腕双奥纹', C: '终局A只换H5爪戒334',
    B: '终局B：长蛇334，阿曼尼披巾334＋腕腰奥纹',
    'finish_vaultcloak_claw': '终局B只换H5爪戒334',
    'finish_vaultcloak_head': '爪戒＋阿曼尼披巾，头改虚痕斗场前驱',
    'finish_vaultcloak_H5boots': '爪戒＋阿曼尼披巾，脚改H5凶暴鳞靴',
    'finish_head_boots': '爪戒＋阿曼尼披巾，同时改头与H5脚',
    'finish_vendorcloak_claw': '爪戒＋金多赞暴急披风334＋腕腰奥纹',
    V: '偏短战斗备选：触须341＋大毒液341',
    'finish_ritual_offhand331': '纯输出副手备选：331仪式灯笼＋一奥纹'}
comparisons = []
for key, label in labels.items():
    values = {}
    for m, _ in ui.MODELS:
        r = finals[m][key]
        values[m] = {'dps': r['dps'], 'delta': 100 * (r['dps'] / finals[m]['current']['dps'] - 1),
            'ci': f"±{r['ci95_half_width']:,.1f}（95%均值半宽）", 'ci95_half_width': r['ci95_half_width'],
            'samples': r['samples'], 'iterations': 6000, 'seed': 26111393}
    comparisons.append({'key': key, 'label': label, 'values': values})
ring_deltas = {m: 100 * (finals[m][C]['dps'] / finals[m][A]['dps'] - 1) for m, _ in ui.MODELS}
ring_deltas_b = {m: 100 * (finals[m]['finish_vaultcloak_claw']['dps'] / finals[m][B]['dps'] - 1) for m, _ in ui.MODELS}
write(HERE / 'endstate-comparison.json', {'as_of': datetime.now().astimezone().isoformat(), 'comparisons': comparisons,
    'finals': finals, 'claw_minus_serpent_percent_A': ring_deltas, 'claw_minus_serpent_percent_B': ring_deltas_b,
    'boundary': 'Best-tested attainable end states,not a globally exhaustiveBiS proof. Current-week materials do not fund every future action.'})
names = {int(r['modifiers']['id']): r['name'] for r in read(CHAR / 'snapshots/2026-11-13-1320.items.json')['items']}
refs = read(HERE / 'item-reference-cache.json')
names.update({int(i): r['name'] for i, r in refs.items()})
icons = read(HERE / 'item-icon-cache.json')
slot_names = dict(zip(study.s.SLOTS, '头部 项链 肩部 披风 胸部 护腕 手部 腰带 腿部 鞋子 戒指一 戒指二 饰品一 饰品二 主手 副手'.split()))


def equipment(key):
    rows = []
    for slot, line in configs[key]['gear'].items():
        f = study.s.fields(line)
        i = int(f['id'])
        n = finals['long'][key]['gear'][{'shoulder': 'shoulders', 'wrist': 'wrists'}.get(slot, slot)]
        source = '现有核心保留'
        green = '／'.join(f'{name}{n[field]}' for name, field in [('暴击','crit_rating'),('急速','haste_rating'),('精通','mastery_rating'),('全能','versatility_rating')] if n.get(field))
        note = '原生模型绿字：' + green + '。'
        if f.get('redirected_base_stats'):
            source = '化生前驱' + f['redirected_base_stats']
            note += ' 按来源继承属性和效果，不使用默认套装绿字。'
        if i == 272148:
            source = '金多赞一次兑换：321神话2/6→334'
            note += ' 可作终局第二戒；自带孔按公开目录假设，购买时看完整预览。'
        if i == 268252:
            source = 'H5斯索拉克：新神话轨来源→334'
            note += ' 小差异替代，不是长蛇必须淘汰的证据。'
        if i == 268248:
            source = '本周低保已提供：318神话1/6→334'
            note += ' 此布局的双奥纹转到腕／腰，披风本身不带美化。'
        if slot in ('back', 'wrist', 'waist') and i in (239656,244584,244581):
            source = '331制作，终局可重铸属性／美化'
            note += ' 奥纹' + ('保留。' if '12384' in f.get('bonus_id','').split('/') else '不放此件；普通制作不占美化名额。')
        if slot in ('wrist', 'waist'):
            note += ' 终局各1孔；目前只确认本周能从低保换1个工具，另一孔是未来目标。'
        if i == 270164:
            source = '已有袋子334，未来凑10石晋升341'
        rows.append({'slot':slot_names[slot],'id':i,'name':names.get(i,n['name']),'level':n['ilevel'],
            'bonus':f.get('bonus_id',''),'source':source,'note':note,'icon_data':icons.get(str(i),''),
            'gems':[{'id':int(g),'name':names.get(int(g),f'宝石{g}')} for g in f.get('gem_id','').split('/') if g]})
    return rows


stat = read(HERE / f'endstate70783-stats-{A}-20-26111395.validation.json')['stats']['stats']
for card, rating, percent in zip(data['stats'], ('crit_rating','haste_rating','mastery_rating','versatility_rating'), ('crit_pct','haste_pct','mastery_pct','versatility_pct')):
    card['comparison'] = f"终局A无消耗品：{stat[rating]:.0f}等级／{stat[percent]*100:.2f}%"
    card['advice'] = '这是具体套装的静态结果；合剂、饰品触发和战斗环境会变化，不是应追的固定阈值。'
data['meta'].update(content='长远可获取BiS · 单独比较完整终局', engine='Live70783/de11f57 · 36组6000次独立seed终局复测',
    budget_note='当前仍是1R、3残片可兑换一次、8晋升石、3火花、105神话纹章；全部未记为消耗。终局额外孔和晋升材料是未来目标。')
data['lead'] = '长蛇绕环可以进入终局，不必因为追BiS就预设以后一定换掉。两种奥纹布局下，爪戒与长蛇直接替换仅约0.05%～0.07%差异，小于本次误差。\n优先把已有袋子334升341、第二戒升334，并补齐腕腰孔。披风＋腕奥纹和334掉落披风＋腕腰奥纹都能构成接近的终局。\n本周免费戒＋打孔路线仍可长期延续；若拿阿曼尼披巾，则按腕腰双奥纹整套重配。H5爪戒／凶暴鳞靴是可选追求，金多赞第二次奖励不必提前花掉。'
data['target_equipment'] = equipment(A)
data['comparisons'] = comparisons
data['models'] = [{'id':m,'label':label,'detail':f'支持的Patchwerk {study.MODELS[m][0]}目标／{study.MODELS[m][1]}秒；6000次，独立seed26111393。按模型内当前实装归一，非实际整把钥石。'} for m,label in ui.MODELS]
data['branches'] = [
    {'outcome':'终局A：延续当前制作位置','preferred':'长蛇334＋虫群334，披风／腕双奥纹，袋子341','reason':'保留目前的披风和腕制作；普通制作腰在本次候选中改暴急，终局腕腰各1孔。整套再调合剂与宝石。','comparison':'无需为了单件榜单强追H5戒，也不必另换披风。第二次金多赞不属于当前余额，不预先分配。'},
    {'outcome':'终局B：本周低保披风','preferred':'阿曼尼披巾334＋腕／腰双奥纹','reason':'本周披风是合法神话轨终局候选，并非拿到后必定淘汰。与终局A在三个模型相差约0.1%以内。','comparison':'若选它，本周就不能同时领取打孔代币或R币；把披风奥纹迁到腰，再做整套属性配平。'},
    {'outcome':'R币','preferred':'想继续追收集时先看H5实际剩余预览','reason':'H5爪戒268252与凶暴鳞靴268233都值得保留；脚在不同模型有小幅取舍。恢复与元素推导池相同。','comparison':'当前只有1R，最多安排一次条件尝试。已有腿兑换物历史不保证两件都在当前排除后池里；不承诺必中或等权概率。'},
    {'outcome':'饰品','preferred':'触须341＋袋子341；大毒液341作为短战斗备选','reason':'同级终局比较：大毒液在5目标90秒更强，袋子在单目标240秒更强，5目标180秒接近。','comparison':'现有毒液是英雄321，不能直接升341；需先获神话轨版本并升334。当前8石不足晋升。'},
    {'outcome':'来源边界','preferred':'不照搬344披风或随机334 BoE靴','reason':'不考虑M7/M8高装等，因此指南腕腰奥纹的344披风前提不直接适用。271440是团本小怪随机绿字BoE，范围内334可达性未证实。','comparison':'保留所有原有来源限定；未把拍卖行、神话小怪、任意重选绿字或护甲晋升341当成已授权可获取来源。'}]
data['actions'] = [
    {'title':'先补真正共同缺口','body':'已有武器、项链、触须341及毒咒胸／特效手保留。第二戒取得神话334版本；袋子在凑10石后升341；腕腰逐步补孔。'},
    {'title':'金多赞不必因BiS而回避长蛇绕环','body':'本次两种终局奥纹布局中，爪戒和长蛇差距都低于0.1%，没有足够证据为这点差异强制花R。一次兑换仍可选长蛇。第二次是任务线未来总额的一部分，不是今天又多一次。'},
    {'title':'低保按最终制作位置选择','body':'保留披风／腕奥纹时，本周打孔器路线仍有长期价值；决定走腕／腰奥纹时，可拿阿曼尼披巾作为334终局披风。两种完整方案差距很小，避免两边同时重复投入。'},
    {'title':'有意追H5时保留两个结果','body':'戒和鞋都不是拿到就要丢的东西。先核对当前奖励预览和周资格；R到爪戒就不再兑换第二枚替代戒，R到鞋则保留作另一套属性配比。'},
    {'title':'终局消耗品重新配平','body':'本次接近的终局候选使用暴击合剂2；先前急速合剂建议针对当时的免费戒＋单孔组合。不要把同一合剂永久固定在所有后续装备上。保留4色钻石方案，补孔在240890／240898之间调节。'}]
data['consumables'] = [
    {'name':'宝石与孔','current':'头1、项链2、双戒各1；腕腰当前无孔','recommendation':'终局腕腰各补1孔，总计7颗宝石含1钻石。候选A为240967钻石与4色普通宝石，额外孔用240890、240898配平。','url':'https://www.method.gg/guides/elemental-shaman/stats-races-and-consumables'},
    {'name':'合剂','current':'此前当前组合建议急速合剂','recommendation':'终局候选已分别比较精通／急速／暴击合剂。本次展示的接近成型组合用暴击合剂2，其余输出消耗品与原研究统一。','url':'https://www.method.gg/guides/elemental-shaman/stats-races-and-consumables'},
    {'name':'341晋升','current':'8枚石，已有匕首／项链／触须341','recommendation':'10石后可升袋子；毒液另需神话轨版本。护甲、戒指和盾牌不当341候选。','url':'https://wow.blizzard.cn/news/24304162/'}]
data['limits'] = [
    '这是终局完整套装研究，和原报告的本周收益方案分开保存。普通掉落334、制作331、已验证可晋升核心341，仍排除M7/M8 9/6。',
    '结构筛选比较六种双奥纹位置、三种制作绿字与多种戒指，随后比较钻石／普通宝石家族、三种合剂、核心饰品、头脚前驱与武器组合。最终36组6000次独立seed复测，不是穷尽全空间的全局最优证明。',
    '两戒直接替换的约0.05%～0.07%均值差小于本次不确定性；不把这当作统计等效证明，也不依据一个最高均值宣布唯一BiS。',
    '三个Patchwerk工作量均被元素模块支持；DungeonSlice／DungeonRoute明确不支持。短战斗饰品差异不是实测整把钥石收益。',
    '未来腕腰两孔、袋子晋升及可能的新神话轨毒液，不代表当前材料全部足够。当前1R、3残片、低保、8石均未领取或消耗。',
    '金多赞六步任务共两次奖励，当前仅一次已确认；没有当作无限可买的每三周装备。已核验披风ID不含项链272228。',
    '271440不作为范围内可选绿字334脚。无拍卖行或神话小怪来源授权时不将其当确定BiS。',
    '刻意保留至少4套和至多2美化；法杖337、洛阿戒＋一奥纹、331仪式副手也作过来源限定比较。副手灯笼会失去盾牌护甲，未验证337副手晋升资格，因此只按331比较。',
    '大毒液341与袋子341在不同目标数／战斗长度有取舍；没有把英雄321毒液当作可以直接升级到神话341。',
    '手和虫群的AoE不分摊及烈火符文目标仍有引擎未实服核验假设。化生前驱与原bonus完整保留。静态20次快照仅取无增益属性，不用于DPS排名。',
    'R实际排除池、循环和跨context共享状态仍未知；普通数据库源集合不能给角色精确命中率。']
data['sources'] += [{'title':'今日终局来源审查：目录／小怪BoE／晋升槽位','url':'endstate-source-audit.json'},
    {'title':'Method：双奥纹推荐依赖344披风前提','url':'https://www.method.gg/guides/elemental-shaman/gearing'}]
data['downloads'] = [{'title':'终局A大米参考SimC','path':'endstate-dungeon.simc'},
    {'title':'终局A保存单体天赋参考','path':'endstate-single-target.simc'},
    {'title':'只替换H5爪戒的同套对照','path':'endstate-claw.simc'},
    {'title':'334披风＋神话大毒液341备选','path':'endstate-vial.simc'},
    {'title':'全部终局数据与逐模型差异','path':'endstate-comparison.json'},
    {'title':'终局输入与来源范围','path':'endstate-manifest.json'},
    {'title':'来源审查与获取条件','path':'endstate-source-audit.json'},
    {'title':'前一版本周方案','path':'report.html'}]
write(HERE / 'endstate-report-data.json', data)
for key, name, model in [(A,'endstate-dungeon.simc','long'),(A,'endstate-single-target.simc','st'),(C,'endstate-claw.simc','long'),(V,'endstate-vial.simc','aoe')]:
    src = HERE / f'endstate70783-{model}-{key}-6000-26111393.simc'
    (HERE / name).write_text('# Hypothetical future attainable set;not current acquisitions.\n# No M7/M8 9/6;334armor,331craft,341qualifyingcores;fixed-target reference.\n'+src.read_text(encoding='utf-8'),encoding='utf-8')
target = ui.section('targets','终局A完整配装',ui.table(['部位','装备','装等','宝石','来源与条件'],[ui.equipment_row(r) for r in equipment(A)],'终局A：长蛇戒，披风＋腕奥纹'), '这是未来目标，不是当前已领取的装备。普通制作腰不新增美化。')
document = ui.render(data).replace("selectModel('slice');","selectModel('aoe');")
document = document.replace('<section id="branches"',target+'<section id="branches"',1)
document = document.replace('<a href="#branches">R币与兑换</a>','<a href="#targets">终局配装</a><a href="#branches">终局路线</a>',1)
(HERE / 'endstate-report.html').write_text(document,encoding='utf-8')
write(HERE / 'endstate-slot-map.json',{'status':'future_target_not_acquired','primary':equipment(A),'alternate_cloak_layout':equipment(B),
    'primary_R_required':False,'vendor_items_primary':1,'future_socket_tools_total':2,'current_confirmed_vendor_exchanges':1,
    'claw_delta_matched_A':ring_deltas,'claw_delta_matched_B':ring_deltas_b})
profile = read(CHAR / 'profile.json')
profile.update(latest_endstate_analysis='analysis/2026-11-13/endstate-report.html',endstate_dungeon_simc='analysis/2026-11-13/endstate-dungeon.simc',
    endstate_slot_map='analysis/2026-11-13/endstate-slot-map.json',goal='Prioritize attainable complete Farseer end-state power, then derive weekly actions; keep current-week affordability separate.')
write(CHAR / 'profile.json',profile)
week = read(CHAR / 'weeks/2026-11-12.json')
week['endstate_plan']={'status':'proposed_not_executed','analysis':'../analysis/2026-11-13/endstate-report.html','primary_ring':272148,'claw_is_mandatory':False,
    'future_bag_level':341,'future_wrist_and_waist_sockets':True,'lining_layout_options':[['back','wrist'],['wrist','waist']],
    'future_vendor_cap':2,'current_owned_fragments':3,'current_available_redemptions':1,'current_R_balance':1,
    'R_optional_target_ids':[268252,268233],'no_spending_or_acquisition_recorded':True}
write(CHAR / 'weeks/2026-11-12.json',week)
lines=['# Farseer attainable end-state study — November13,2026','',
    'Future end states are normalized to334 armor/rings,331crafts,341 qualifying cores and equal head/neck/ring/wrist/waist socket counts. No Mythic7/8 overcap,AHBoEs or armor ascension is assumed. At least four tier pieces and at mosttwo embellishments are checked. Six placement structures,crafted stat pairs,ring alternatives,gems/flasks and supported fixed-target work are screened before36 independent-seed6000 comparisons. This is a bounded search,not a global optimum proof.','',
    'Matched ring replacements in two layouts differ only around0.05–0.07%,within present uncertainty. AnguineGyre272148 is a viable end-state ring;the data does not justify mandatoryClawRing268252 acquisition. BothBack+Wrist andWrist+Waist lining layouts remain close. Current-week one-socket/vendor plan can extend into an end state;the alternativeVaultcloak can also remain in the final set.','',
    'The practical future core keeps the owned dagger,neck,tendril,chest andgloves;upgrades the ownedBag to341 andadds the second wrist/waist socket. Vial341 improves the90s5target reference whileBag341 improves240sST;they are alternative toolsets,not a measured whole-key ranking. Hero321Vial requires a new Myth-track copy toreach341. H5boots268233 are legitimate and remain worth keeping,even when not the best current fixed-target option.','',
    'KindoJan has two total documented quest-chain exchanges,onlyone currently confirmed.271440 is a randomraid-trashBoE without a verified in-scope334 route;it is excluded.337staff and331ritualoffhand were considered with legal embellishment counts;offhand337 ascension is not assumed. Original report andraw snapshot are preserved. No currency was spent.','',
    '|Candidate|5t90s|5t180s|1t240s|','|---|---:|---:|---:|']
lines += ['|'+c['label']+'|'+'|'.join(f"{c['values'][m]['delta']:+.3f}%" for m,_ in ui.MODELS)+'|' for c in comparisons]
(HERE / 'endstate-review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print({'report':str(HERE/'endstate-report.html'),'final_comparisons':36,'ring_delta_A':ring_deltas,'ring_delta_B':ring_deltas_b,'no_resources_spent':True})
