"""Assemble the bounded personal study, clean exports and proposed weekly plan."""

import importlib.util
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAR = HERE.parents[1]
REPO = HERE.parents[3]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
write = lambda p, d: p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
now = datetime.now().astimezone().isoformat()
spec = importlib.util.spec_from_file_location('personal_study', HERE / 'personal-study.py')
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
spec = importlib.util.spec_from_file_location('report_renderer', HERE / 'report-renderer.py')
ui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui)
ui.MODELS = (('aoe', '五目标90秒'), ('long', '五目标180秒'), ('st', '单目标240秒'))
MODELS = [m for m, _ in ui.MODELS]
PRIMARY = 'free_route_socket_240890'
ALTERNATIVE = 'joint_h5_vendor_wrist'
labels = {
    'current': '当前完整实装：13:20导出',
    'vendor_ring_272148': '只换金多赞长蛇绕环334，保持当前消耗品',
    'vault_socket_240898': '只新增一个腕孔＋240898，保持当前消耗品',
    PRIMARY: '首选：长蛇绕环334＋1腕孔240890＋急速合剂',
    'free_route_socket_240898': '首选近似替代：新增腕孔改240898',
    'h5_ring': '只换H5爪戒334（假设R成功并升满）',
    'joint_h5_haste_waistch': 'H5爪戒＋现有腰改暴急＋急速合剂，不花金多赞',
    ALTERNATIVE: 'R路线：H5爪戒＋金多赞腕334＋腰奥纹＋急速合剂',
    'crafted_ring_ch': '只新增331普通暴急制作戒',
    'vault_flask_334_for_bag': '低保水壶升334，替现有334无底袋',
    'vault_gland_334_for_bag': '低保涌流腺体升334，替无底袋；模型无击杀减CD',
    'vault_cloak_334_move_lining': '低保阿曼尼披巾334，并将披风奥纹迁至腰',
    'ascend_bag_341': '未来凑10石：已有无底袋334晋升341',
}
all_final = {}
for f in HERE.glob('live70783-*-6000-26111353.validation.json'):
    d = read(f)
    if d['accepted']:
        all_final.setdefault(d['model'], {})[d['candidate']] = d
comparisons = []
for key, label in labels.items():
    values = {}
    for mode in MODELS:
        d = all_final[mode][key]
        assert d['accepted'] and d['valid_fight_style'] and d['tier_count'] >= 4
        values[mode] = {'dps': d['dps'], 'delta': 100 * (d['dps'] / all_final[mode]['current']['dps'] - 1),
                        'ci': f"±{d['ci95']:,.1f}（均值95%半宽）", 'ci95_half_width': d['ci95'],
                        'samples': d['samples'], 'iterations': 6000, 'seed': 26111353}
    comparisons.append({'key': key, 'label': label, 'values': values})
write(HERE / 'comparison-results.json', {'recorded_at': now, 'comparisons': comparisons,
    'all_final_accepted': all_final, 'rejected_exploratory_runs': read(HERE / 'rejected-runs.json'),
    'methodology': 'Screen1500 seed26111331; finalist6000 independent seed26111353. Not paired inference. Native gear parsing is supplemented by source eligibility and inventory-slot checks.'})

intake = read(CHAR / 'snapshots/2026-11-13-1320.items.json')
refs = read(HERE / 'item-reference-cache.json')
icons = read(HERE / 'item-icon-cache.json')
elite = read(HERE / 'elite-evidence.json')
rewards = read(HERE / 'reward-source-evidence.json')
names = {int(x['modifiers']['id']): x['name'] for x in intake['items']}
names.update({int(k): v['name'] for k, v in refs.items()})
slot_names = dict(zip(study.SLOTS, '头部 项链 肩部 披风 胸部 护腕 手部 腰带 腿部 鞋子 戒指一 戒指二 饰品一 饰品二 主手 副手'.split()))
native_slots = {'shoulder': 'shoulders', 'wrist': 'wrists'}


def equipment(key):
    gear = study.load()[1]
    gear.update(study.candidates()[key][0])
    native = all_final['aoe'][key]['gear']
    rows = []
    for slot in study.SLOTS:
        f = study.fields(gear[slot])
        ident = int(f['id'])
        n = native[native_slots.get(slot, slot)]
        green = '／'.join(f'{label}{n[field]}' for label, field in (
            ('暴击', 'crit_rating'), ('急速', 'haste_rating'), ('精通', 'mastery_rating'), ('全能', 'versatility_rating')) if n.get(field))
        source = '现有装备保留'
        note = '模型导入实际绿字：' + green + '。'
        if f.get('redirected_base_stats'):
            source = '化生前驱 ' + f['redirected_base_stats']
            note += ' 套装默认提示不能替代前驱继承属性。'
        if slot == 'chest':
            note += ' 保留271876毒咒精通效果13846；此护甲不在晋升毒液石适用部位。'
        if slot == 'hands':
            note += ' 保留281238来源的14049特效；其AoE分摊仍有引擎假设。'
        if ident == 272148:
            source = '瓦杜：3枚神话灵魂残片，先321神话2/6，再升级334'
            note += ' 替321阿曼尼戒；商品1孔按公开实测目录建模，购买时核对完整提示。兑换不是R排除。'
        if ident == 268252:
            source = 'H5斯索拉克R目标，尚未获取'
            note += ' 按318神话1/6来源升334；不能从历史假定必中。'
        if ident == 272254:
            source = '瓦杜腕334对照候选，尚未获取'
            note += ' 需将原护腕奥纹迁到腰；与保留原腕的整套差距很小，不优先花唯一兑换。'
        if slot == 'wrist' and key == PRIMARY:
            note += ' 此处唯一新孔来自本次低保6代币购买的打孔器，尚未领取或使用。'
        if slot in ('back', 'wrist', 'waist'):
            note += ' 现装8790/8791铭文会覆盖crafted_stats占位字段；原始导出完整保留。'
        if slot == 'waist' and key == ALTERNATIVE:
            note += ' 对照方案改暴急并接收第二奥纹。'
        if slot.startswith('trinket'):
            note += ' 保留341触须＋334袋子；先知前五中4人同配对。'
        rows.append({'slot': slot_names[slot], 'id': ident, 'name': names[ident], 'level': n['ilevel'],
                     'bonus': f.get('bonus_id', ''), 'source': source, 'note': note,
                     'icon_data': icons.get(str(ident), ''), 'gems': [
                         {'id': int(g), 'name': names.get(int(g), f'宝石{g}')} for g in f.get('gem_id', '').split('/') if g and int(g) > 0]})
    return rows


def snapshot(key):
    return read(HERE / f'live70783-stats-{key}-20-26111355.validation.json')['stats']['stats']


current_stats, target_stats = snapshot('current'), snapshot(PRIMARY)
stats = []
for name, rating, pct, advice in (
    ('暴击', 'crit_rating', 'crit_pct', '当前与先知高分样本接近；爪戒并非必须补齐的巨大缺口。'),
    ('急速', 'haste_rating', 'haste_pct', '长蛇绕环会换掉大量急速；首选整套明确搭配急速合剂2，裸面板不当通用阈值。'),
    ('精通', 'mastery_rating', 'mastery_pct', '保留毒咒胸与已有精通；不将指南1200等级照搬为必须凑到的硬门槛。'),
    ('全能', 'versatility_rating', 'versatility_pct', '长蛇绕环增加全能与生存能力；本次没有为了追最低全能而降低整套表现。')):
    stats.append({'name': name, 'rating': current_stats[rating], 'percent': current_stats[pct] * 100,
                  'comparison': f"首选无增益快照：{target_stats[rating]:.0f}等级／{target_stats[pct]*100:.2f}%", 'advice': advice})

sources = [{'title': 'Murlok当日先知50人及前五样本（不含国服）', 'url': 'https://murlok.io/shaman/elemental/farseer/m+'},
           {'title': 'Celz：元素萨装备建议，10月14日更新', 'url': 'https://www.method.gg/guides/elemental-shaman/gearing'},
           {'title': 'Celz：先知属性与消耗品', 'url': 'https://www.method.gg/guides/elemental-shaman/stats-races-and-consumables'},
           {'title': '国服官方12.1.5规则：晋升适用武器／饰品／项链', 'url': 'https://wow.blizzard.cn/news/24304162/'},
           {'title': '金多赞321神话2/6自选装备的正式服实测目录', 'url': 'https://www.wowhead.com/news/myth-2-6-piece-of-loot-now-available-from-labyrinths-383603'},
           {'title': '瓦杜兑换商人和玩家物品目录', 'url': 'https://www.wowhead.com/npc=264886/wahdu'},
           {'title': '低保6代币与当季打孔器规则', 'url': 'https://www.icy-veins.com/wow/great-vault-guide'},
           {'title': '低保直接选择R币的规则与条件', 'url': 'https://www.method.gg/guides/how-to-obtain-bonus-rolls-nebulous-voidcores-in-wow-midnight-patch-12-1-5'},
           {'title': '当前Raidbots普通掉落／专精数据（不等于剩余R池）', 'url': 'https://www.raidbots.com/static/data/live/encounter-items.json'}]
players = []
for p in elite['farseer_top_five']:
    s = {r['stat']: r['percent'] for r in p['secondary_stats']}
    players.append({'name': p['name'], 'url': p['source_url'], 'score': p['mplus_score'], 'level': p['equipped_average_item_level'],
                    'crit': s['Critical Strike'], 'haste': s['Haste'], 'mastery': s['Mastery'], 'vers': s['Versatility']})
data = {
    'meta': {'date': '2026-11-13 · 完整导出13:20', 'character': '正极兔 · 先知元素萨', 'patch': '12.1.5.70783',
             'content': '大秘境配装 · 低保与金多赞联合选择', 'engine': 'Live70783／de11f57 · 6000次独立seed复测',
             'budget_note': '现有1R、3枚神话灵魂残片（一次兑换）、8晋升毒液石、3潮汐火花、105神话纹章。五件低保均已确认神话1/6；均未领取。'},
    'lead': '首选确定提升：金多赞兑换长蛇绕环272148，升334替321阿曼尼戒；低保选6代币，换当季打孔器给现有奥纹护腕新增一孔，镶240890。整套使用急速合剂2。\n现有1枚R先保留。H5爪戒是可选目标，但相对免费兑换戒差距很小；只有实际奖励预览能接近定向时再考虑。不要默认切恢复能缩池。\n武器、项链、触须与毒咒胸均保留；8枚晋升石还不足一次，凑10后优先考虑现有袋子晋升341。',
    'stats': stats, 'equipment': equipment('current'), 'target_equipment': equipment(PRIMARY),
    'comparisons': comparisons,
    'models': [{'id': 'aoe', 'label': '五目标90秒', 'detail': '当前大米天赋，Patchwerk固定5目标90秒，无团队增益／嗜血，明确消耗品。不是实测整把路线。'},
               {'id': 'long', 'label': '五目标180秒', 'detail': '当前大米天赋，固定5目标180秒，检验战斗长度与饰品冷却敏感性。'},
               {'id': 'st', 'label': '单目标240秒', 'detail': '用户保存的“单体”天赋，固定1目标240秒；同模型内只比较装备，不横比绝对DPS。'}],
    'branches': [
        {'outcome': '首选：本周可确定取得', 'preferred': '金多赞长蛇绕环＋低保打孔器，保留1R',
         'reason': '兑换戒334与H5戒334在当前装备中差距很小；新增一孔提供确定提升，不必为第二枚R币放弃本周孔。',
         'comparison': '方案包括戒指334、腕新增一孔240890及急速合剂；三个模型的累计收益见对照表。这里没有消耗现有R，也没有把兑换和低保当成已领取。'},
        {'outcome': '想继续追H5爪戒时', 'preferred': '先核对斯索拉克实际R预览，元素／恢复都不缩池',
         'reason': '数据库推导262与264均为268233鞋、268252爪戒、270920腿兑换物。你有270920的R历史，但当前循环、context与服务器排除状态未确认。',
         'comparison': '若预览只剩爪戒且本周仍有资格，可先用现有1R再决定金多赞。若仍有鞋子等，优先免费路线；不宣称必中或准确概率。'},
        {'outcome': 'H5已经出爪戒后的金多赞', 'preferred': '可以继续保留兑换，不急换334腕或肩',
         'reason': '最终整套重测中，换新腕与保留原腕＋腰改属性差距很小；新肩、新披风也仅小幅变化。',
         'comparison': '不能用早期单件筛选，为最终整套几乎没有增益的腕部替换强行分配唯一兑换。对照候选有单独SimC导出。'},
        {'outcome': '坚持从低保拿装备', 'preferred': '水壶是可用备选，收益与袋子接近',
         'reason': '水壶334替袋子在三个模型约−0.10%至＋0.31%；阿曼尼披巾334需迁移奥纹，约＋0.21%至＋0.32%。新月刃334仍不如341匕首。',
         'comparison': '涌流腺体的高血量与击杀减CD已实现，但固定存活目标无法兑现整把钥石击杀重置，不能把本表当它实际大米的完整排名。'},
        {'outcome': '晋升材料', 'preferred': '先保留8石，凑10再考虑袋子341',
         'reason': '现有匕首、项链、触须均已341；袋子334是还可以进一步晋升的当前核心。胸、其他护甲与戒指不在官方晋升部位中。',
         'comparison': '袋子341只测量未来收益，没有把尚缺的2枚石当成拥有，也没有记录任何实际晋升。'}],
    'actions': [
        {'title': '瓦杜选长蛇绕环272148，升级至334', 'body': '花3枚已确认残片兑换321神话2/6版本；用神话路线升334后替321阿曼尼戒。保留334虫群戒，戒指7967附魔与240898宝石按导出配置。购买预览核对自带孔与轨道。'},
        {'title': '低保6代币换一个当季打孔器', 'body': '本周已解锁5格，满足至少3格取得6代币。给现有331奥纹护腕加一个孔，插240890无瑕致命榄石；头部已有孔，不重复加。此工具来自计划兑换，不混用之前武器战角色的工具。'},
        {'title': '首选整套搭配急速合剂2', 'body': '长蛇绕环替换大量急速，合剂随整套改为急速。其他宝石和费力铭文不一概重做；已有四种宝石颜色保留。240898作为腕孔近似替代也已复测，差距很小。'},
        {'title': '现有1R保留，H5只作条件目标', 'body': '若实际预览只剩爪戒且有本周奖励资格，可先R后决定金多赞。其余情况免费兑换戒已解决第二戒，不为0.1%级差异清空杂项池。恢复与元素的H5数据库池相同。'},
        {'title': '保留核心与现有双奥纹', 'body': '保留341匕首、341项链、341触须＋334袋子、334毒咒套胸和特效套手。首选仍5件套、披风＋腕双奥纹；未新增第三美化。背包334邪恶炼金师戒在最终三模型均弱于当前321阿曼尼，先不换。'}],
    'elite': players,
    'usage': [{'name': '先知前五：触须', 'value': '5/5', 'note': '物品ID281215；不是相同完整bonus或装等的保证。'},
              {'name': '先知前五：触须＋袋子', 'value': '4/5', 'note': '另一人触须＋大毒液273796；与你现有组合一致。'},
              {'name': '先知前五：主手／项链', 'value': '5/5同款', 'note': '271092／268265；不把未知化生前驱从套装名反推。'},
              {'name': '先知前五：H5爪戒／长蛇绕环', 'value': '3/5 ／ 2/5', 'note': '每人另一枚均为虫群；两条第二戒路线都有样本。'},
              {'name': '样本范围', 'value': '11月13日；50人／前五', 'note': 'US/EU/KR/TW，不含CN；角色当前快照不一定等于最高分那把的配装。'}],
    'consumables': [
        {'name': '腕孔宝石', 'current': '当前头有孔，腕／腰无孔', 'recommendation': '首选新增腕孔240890；240898近似替代也可，保持其他孔与钻石。', 'url': 'https://www.wowhead.com/cn/item=240890'},
        {'name': '首选整套消耗品', 'current': '导出不证明游戏中实际饮用哪种合剂', 'recommendation': '急速合剂2、哈籁尼尔盛宴、虚触符文、圣光潜能药水2、符合天赋条件的凤凰油2；团队增益与嗜血关闭以控制比较。', 'url': 'https://www.method.gg/guides/elemental-shaman/stats-races-and-consumables'},
        {'name': '纹章与火花', 'current': '105神话纹章，3潮汐火花', 'recommendation': '金多赞321→334未减免基准80神话纹章；318→334基准100。实际槽位／战团减免看升级界面。首选不新做装备、不耗火花。', 'url': 'https://www.wowhead.com/cn/guide/midnight/item-level-gear-upgrades-dawncrests'},
        {'name': '晋升石', 'current': '280562×8，不足一次', 'recommendation': '达到10再对已满级袋子考虑晋升；护甲与戒指不适用。', 'url': 'https://wow.blizzard.cn/news/24304162/'}],
    'limits': [
        '原始完整导出保留16实装槽、60背包行、全部前驱、天赋、Omnium与10条R历史。低保导出为空，但用户截图提供5个候选，随后确认均神话1/6；3残片及一次兑换也已确认。',
        '引擎为原生Live70783 de11f57，11月13日核对仍与官方midnight远端最新SHA一致；无需重编译。英雄树由ancestor宠物和祖先召唤效果确认。',
        '元素模块明确拒绝DungeonSlice和DungeonRoute；没有将拒绝模型的数据用于推荐。三个Patchwerk模型仍不是实际整把钥石，尤其不能模拟涌流腺体的所有击杀减CD。',
        '初筛1500次seed26111331；决赛6000次独立seed26111353，5999有效样本。CI为各均值95%半宽，不是配对差值检验；小差异不当硬排名或统计等效。',
        '首选与R候选都重新放回完整配装比较。换新腕相对保留原腕＋腰改属性的收益很小，因此不以初筛为由强制花唯一兑换。',
        '普通神话上限334、制作331，已晋升核心341；不含M7/M8 9/6。源目录和物品部位另做合法性检查，错槽和护甲341探索输入已明确作废并保留审计记录。',
        '无增益面板显式关闭合剂、食物、药水、强化符文、油和团队增益，保留天赋／种族／装备常驻效果。20次短跑仅取静态属性，不作DPS证据。',
        '现装属性按8790／8791实际铭文处理，crafted_stats只替换未被铭文覆盖的占位属性。原始字段没有被覆盖；新增重铸候选才清理旧铭文。',
        '毒咒胸13846和项链13987效果保留；手与虫群的伤害不分摊、烈火符文触发目标仍有引擎未实服核验假设。',
        '金多赞目录为正式服公开实测与数据库，未远程观察此角色商人窗口；戒指孔和完整bonus需购买预览核对。所有目标升级按334测量，不是321兑换到手或318低保拿到手的即时收益。',
        'H5普通专精池与角色当前剩余R池不同。5/95为Heroic家族itemcontext，第4字段为keyLevel；服务器共享排除、循环重置及本周资格未知，不给精确概率或必中承诺。',
        '旧记录将失落探险者称H3，本次来源箱278286确认为H4；以来源箱／首领名字匹配，旧记录保留不按序号误合并。',
        '首选是本次有界候选中成本合理的组合；不是穷尽所有装备、天赋、实际路线后的全局BiS。当前1R、3残片、低保和晋升石均没有实际消耗。'],
    'sources': sources,
    'downloads': [{'title': '原始13:20完整导出', 'path': '../../snapshots/2026-11-13-1320.simc'},
                  {'title': '当前完整实装比较输入', 'path': 'current-equipped.simc'},
                  {'title': '首选确定路线：大米固定目标参考', 'path': 'recommended-dungeon.simc'},
                  {'title': '首选装备＋保存单体天赋参考', 'path': 'recommended-raid-reference.simc'},
                  {'title': 'R爪戒＋兑换腕对照输入', 'path': 'alternative-r-route.simc'},
                  {'title': '全部最终对照与作废项索引', 'path': 'comparison-results.json'},
                  {'title': '当日高手来源证据', 'path': 'elite-evidence.json'},
                  {'title': '金多赞目录、R字段和池证据', 'path': 'reward-source-evidence.json'},
                  {'title': '引擎与输入哈希', 'path': 'simc-manifest.json'},
                  {'title': '本周资源及未执行计划', 'path': '../../weeks/2026-11-12.json'}],
}
write(HERE / 'report-data.json', data)
write(HERE / 'target-slot-map.json', {'status': 'hypothetical_not_acquired', 'primary': data['target_equipment'],
    'alternative_R': equipment(ALTERNATIVE), 'vendor_cost_fragments': 3, 'vault_choice': '6merit_to_one_socket_tool',
    'new_socket_slot': 'wrist', 'new_sockets': 1, 'R_spent_primary': 0, 'R_remaining_primary_if_executed': 1,
    'sparks_spent_primary': 0, 'current_balance_unchanged': True})
for key, name, mode in [('current', 'current-equipped.simc', 'aoe'), (PRIMARY, 'recommended-dungeon.simc', 'aoe'),
                         (PRIMARY, 'recommended-raid-reference.simc', 'st'), (ALTERNATIVE, 'alternative-r-route.simc', 'aoe')]:
    source = HERE / f'live70783-{mode}-{key}-6000-26111353.simc'
    header = ['# Live70783/de11f57; complete user13:20 source modifiers andOmnium.',
              '# ' + ('Owned gear; explicit comparison consumables.' if key == 'current' else 'Hypothetical candidate,not acquired; only one newsocket in the primary route.'),
              '# Supported fixed-target reference,not an actual dungeon route or global raidBiS.']
    (HERE / name).write_text('\n'.join(header + [l for l in source.read_text(encoding='utf-8').splitlines() if not l.startswith('#')]) + '\n', encoding='utf-8')

target_table = ui.table(['部位', '首选候选装备', '装等', '宝石', '来源与条件'],
                      [ui.equipment_row(x) for x in data['target_equipment']], '首选完整目标 · 尚未领取／升级／打孔')
target_section = ui.section('targets', '首选完整配装', target_table, '保留现有5件套与披风／腕双奥纹；本次只换第二戒和增加1腕孔，明确搭配急速合剂。')
watchlist = [
    ('vendor', '瓦杜／金多赞', 272148, '长蛇绕环', '首选一次兑换；321神话2/6→334，替第二戒。'),
    ('vault', '本周宏伟宝库', None, '6代币→当季打孔器', '新增1腕孔；不同时领取装备或额外R币。'),
    ('raid', 'H5斯索拉克', 268252, '顶级蛮兵爪戒', '条件目标；元素和恢复同推导池，预览未确认不承诺必出。'),
    ('raid', '失落探险者', 270164, '盖博的无底袋', '已有334；未来10石晋升，不再次为当前核心追R。'),
    ('raid', 'H8乌拉特克', 271092, '简斯拉泽与项链／毒咒胸', '主手341、项链341、胸334均已有，停止重复分配R。'),
    ('raid', '基希克斯', 281215, '触须／虫群戒／特效手', '当前三件均已有；保留实际bonus与化生前驱。'),
    ('other', '大米／低保', 273796, '一瓶肮脏的烈性毒液', '可用替代，但334袋子已成熟，不为近似收益强投新池。'),
    ('other', '普通制作', 240949, '精工辛多雷指环', '331暴急可用；本周免费兑换戒无需另花火花与制作纹章。'),
]
watch_rows = []
for kind, source, ident, name, note in watchlist:
    label = ui.link(ui.text(name), f'https://www.wowhead.com/cn/item={ident}', f'item={ident}&domain=cn') if ident else ui.text(name)
    watch_rows.append(ui.row(ui.text(source), label, ui.text(note)).replace('<tr>', f'<tr data-source-kind="{kind}">', 1))
watch_table = ui.table(['来源', '候选／已有核心', '优先级与停止条件'], watch_rows, '候选观察表；不是角色当前完整剩余R池')
watch_filter = '<label for="source-filter">筛选来源　</label><select id="source-filter"><option value="all">全部</option><option value="vendor">金多赞</option><option value="vault">低保</option><option value="raid">团本R</option><option value="other">大米／制作</option></select>'
watch_section = ui.section('watchlist', '来源与停止条件', watch_filter + watch_table, '装备价值、普通掉落池与实际剩余R池分开记录。')
document = ui.render(data).replace("selectModel('slice');", "selectModel('aoe');")
document = document.replace('<section id="branches"', target_section + '<section id="branches"', 1)
document = document.replace('<section id="samples"', watch_section + '<section id="samples"', 1)
document = document.replace('<a href="#branches">R币与兑换</a>', '<a href="#targets">目标配装</a><a href="#branches">低保与兑换</a>', 1)
document = document.replace('</body>', '<script>document.querySelector("#source-filter").addEventListener("change",function(){document.querySelectorAll("[data-source-kind]").forEach(row=>{row.hidden=this.value!=="all"&&row.dataset.sourceKind!==this.value;});});</script></body>')
(HERE / 'report.html').write_text(document, encoding='utf-8')

week_path = CHAR / 'weeks/2026-11-12.json'
week = read(week_path)
week['rules'].update(vault_merit_for_five_unlocked_slots=6, socket_tool_merit_cost=6,
                     vault_direct_R_alternative=1, ascension_allowed_slots=['weapons', 'trinkets', 'necklaces'])
week['plan'] = {'status': 'proposed_not_executed', 'analysis': '../analysis/2026-11-13/report.html',
                'coins_allocated_now': 0, 'coins_reserved': 1, 'vendor_fragments_planned': 3,
                'vendor_item_id': 272148, 'vault_planned_choice': '6merit_to_one_socket_tool',
                'socket_planned_slot': 'wrist', 'socket_planned_gem': 240890, 'new_sockets_planned': 1,
                'sparks_planned': 0, 'venomstones_planned_now': 0,
                'sequence': ['Exchange3 confirmed fragments for Myth2/6 AnguineGyre272148; upgrade334 then replace321Amani.',
                             'Claim6VaultMerit, buy one current-season socket tool; socket the retained Arcanoweave wrist once.',
                             'Use hasteflask2 with this complete candidate; retain other gems and gear.',
                             'Keep the existing1R unless actualH5 reward preview makes the smallClawRing target compelling.',
                             'At10venomstones consider the owned334GebboBag to341,not armor ascension.'],
                'H5_spec': 'Elemental262 andRestoration264 have the same database-derived pool; no restoration shrink advantage.',
                'H5_if_target_obtained_first': 'Do not auto-spend the unique vendor redemption on wrists; final full-set comparison versus keeping the owned wrist is near uncertainty.',
                'stop': 'No H8weapon/neck/chest orH10tendril/Swarmcaller/glove chasing; those cores are already owned.',
                'accounting': 'A proposal only; current1R,3fragments,unclaimedVault,8stones remain unchanged.'}
week['pools'] = [p for p in rewards['encounter_pools'] if p.get('pool_key', '').startswith('H5')]
write(week_path, week)
profile_path = CHAR / 'profile.json'
profile = read(profile_path)
profile.update(recommended_raid_simc='analysis/2026-11-13/recommended-raid-reference.simc',
               recommended_dungeon_reference_simc='analysis/2026-11-13/recommended-dungeon.simc',
               target_slot_map='analysis/2026-11-13/target-slot-map.json',
               target_loadouts_status='Best-tested bounded practical candidates,not acquisitions or globally optimizedBiS.')
profile['constraints']['ascension_allowed_slots'] = ['weapons', 'trinkets', 'necklaces']
write(profile_path, profile)
rows = ['|Candidate|5t90s|5t180s|1t240s|', '|---|---:|---:|---:|']
rows += ['|' + c['label'] + '|' + '|'.join(f"{c['values'][m]['delta']:+.3f}%" for m in MODELS) + '|' for c in comparisons]
review = '''# Zhengjitu personal gearing study — November13,2026

The complete13:20 export is preserved separately from the October study. Current Farseer talents are used for fixed-target AoE; the supplied saved single-target talents are used for the ST model. Omnium, race and professions are retained. NativeLive70783 engine de11f57 still matches the remote midnight head checked today. Elemental explicitly rejects DungeonSlice and DungeonRoute; all ranked inputs use supported Patchwerk workloads.

The user confirmed five318 Myth1/6 Vault offers and3MythicSoulFragments285065, sufficient for one unclaimed vendor exchange. Existing balance is1R,8Venomstones,3currentSeasonSparks,105Mythcrests and8Catalyst charges. Previous warrior socket ownership is not transferred. The primary plan obtains its one new wrist socket from six current VaultMerit tokens, not an already-owned tool. No acquisition or expenditure has been recorded.

The practical recommendation exchanges for AnguineGyre272148 at321Myth2/6, upgrades334, retains Swarmcaller, adds one wrist socket with240890 and uses hasteflask2. It keeps all five tier items and two Arcanoweave pieces. A RClawRing+newvendorwrist alternative is not materially stronger in these bounded model comparisons; keeping the existing wrist and changing the waist is explicitly rechecked. The vendor wrist is not forced on the strength of an earlier single-item screen. If H5 becomes a clean target and the player prefers that route, use an actual preview and preserve the redemption until the result. Restoration does not shrink the H5 database pool.

The merchant ring's socket is based on the public live-player catalogue, not an observed CN merchant hyperlink. Validate that full merchant item preview before acquisition. Rank-only lookups do not prove all bonuses. Vendor exchange does not count as a bonus-roll exclusion. All replacement comparisons are at334 except ordinary crafts331; these are not immediate321/318 claim gains. Normal321to334 cost is80Mythcrests before source-specific slot/Warband discounts; exact UI charge is not inferred.

Current334alchemist ring loses to the321Amani in final models. Current341dagger/neck/tendril and334Venomcursed chest are retained. Only weapons,trinkets andnecklaces qualify for AscendantVenomstone upgrades under officialCN12.1.5 notes. Exploratory armor341 inputs and two incorrectly slotted vendor-item inputs are marked rejected and excluded, even though SimC parses them. Existing8stones cannot ascend any item today. At10the owned334GebboBag is the remaining eligible current core to consider.

Screen1500 iterations/seed26111331; final6000/seed26111353. Each final comparison has5999samples and a95%mean half-width. These are not paired tests or statistical-equivalence proofs. Fixed surviving targets omit mid-fight kill resets forVexhul270170. Its lower fixed-target results are not an actual key ranking. Gloves/Swarmcaller assume non-split damage and RuneUnleashedFire targeting remains unverified. Static snapshots explicitly disable all consumables/raidbuffs and are not DPS evidence. Baseline missive8790/8791 overrides placeholder crafted_stats as intended by the native item loader; hypothetical recrafts remove the previous missive.

'''+ '\n'.join(rows) + '\n\nAll source URLs, profile counts, model settings, rejected input reasons and raw measurements are available through report-data.json,comparison-results.json,simc-manifest.json and the evidence files. Original October analysis and other characters remain untouched.\n'
(HERE / 'review.md').write_text(review, encoding='utf-8')
print({'report': str(HERE / 'report.html'), 'current_rows': len(data['equipment']), 'target_rows': len(data['target_equipment']),
       'final_accepted_comparisons': sum(len(v) for v in all_final.values()), 'visible_candidates': len(comparisons),
       'R_balance': week['budget']['current_balance'], 'vendor_fragments': week['kindo_jan']['owned_fragments']})
