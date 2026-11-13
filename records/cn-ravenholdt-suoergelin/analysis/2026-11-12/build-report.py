"""Build a source-based Arms plan while the full addon export is pending."""

from copy import deepcopy
from datetime import datetime
import importlib.util
import json
from pathlib import Path

ROOT = Path('records/cn-ravenholdt-suoergelin')
HERE = ROOT / 'analysis/2026-11-12'
read = lambda path: json.loads(path.read_text(encoding='utf-8-sig'))
write = lambda path, value: path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
now = datetime.now().astimezone().isoformat()
intake = read(ROOT / 'snapshots/2026-11-12-wcl.items.json')
elite = read(HERE / 'elite-evidence.json')
icons = read(HERE / 'item-icons.json')
tips = read(HERE / 'candidate-tooltips.json')
current_tips = read(HERE / 'current-tooltips.json')
raw = (ROOT / 'snapshots/2026-11-12-wcl.simc').read_text(encoding='utf-8')
gear = {line.split('=', 1)[0]: dict(part.split('=', 1) for part in line.split('=', 1)[1].split(',') if '=' in part)
        for line in raw.splitlines() if line and not line.startswith('#') and ',id=' in line}
slot_names = dict(zip('head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand'.split(),
                      '头部 项链 肩部 披风 胸部 护腕 手部 腰带 腿部 鞋子 戒指一 戒指二 饰品一 饰品二 双手武器'.split()))
notes = {
    'head': ('现有334套装头，带H10特效14049', '保留。特效对应H10板甲头281239；WCL未给化生前驱，默认套装绿字不可当实际绿字。当前头已有一孔。'),
    'neck': ('现有341亚基项链', '前五5/5同款；已到本次晋升上限，暂不再追。'),
    'shoulder': ('现有334套装肩', '保留；前驱未知。若后续换暴急前驱，可比较克拉西斯封印者肩铠239037化生，当前不为此多花R币。'),
    'back': ('H7丝质巫毒斗篷334', '保留；前五4/5同款。用户确认团本来源装备均来自R。'),
    'chest': ('321英雄6/6套装胸', '不能沿当前英雄轨直接升334。目标H7狂野精魂胸甲268222神话轨版本，先化生为271459后再换，保持四件套。'),
    'wrist': ('331制作，暴急＋奥纹', '符合主流制作位置；保留。13696不加孔，当前无腕孔。'),
    'hands': ('现有334套装手', '保留四件套；前驱未知，暂不凭默认套装绿字重做制作或再R此槽。'),
    'waist': ('H7剧毒悔恨束带334', '保留；前五4/5同款。13696不加孔，后续可补腰孔。'),
    'legs': ('321英雄6/6充能二元腿铠', '当前71暴击＋120全能。首选H8无羁深仇腿甲271878神话轨版本，334时201暴击并带毒咒急速触发；可化生为271455。'),
    'feet': ('331制作，暴急＋奥纹', '与护腕组成双奥纹，暂不重做；当前导出无鞋附魔。'),
    'finger1': ('318神话1/6虫群戒', '直接升级现有这枚到334，无需再R同一戒。当前gem_id=0，且无戒指附魔：先补240890与7967。'),
    'finger2': ('321英雄6/6阿曼尼督军戒', '当前136暴击＋239急速。后续可选334爪戒268252，或331制作戒240949／神话轨大米戒；最终组合等完整SimC。'),
    'trinket1': ('341触须', '与祖尔金搭配，被当前前五3人共同使用，可保留。'),
    'trinket2': ('341祖尔金', '与触须搭配，被当前前五3人共同使用。乌心不是本角色当前大米第一R目标。'),
    'main_hand': ('H7迈兹罗阿341', '前五5/5同款；现有强武器保留，不为H10圣光剑优先投入R币。'),
}
equipment = []
for item in intake['items']:
    slot = item['slot']; f = gear[slot]; source, note = notes[slot]
    gems = [{'id': int(i), 'name': '费解之永歌钻石' if i == '240983' else '无瑕致命榄石'}
            for i in (f.get('gem_id') or '').split('/') if i and int(i) > 0]
    equipment.append({'slot': slot_names[slot], 'name': item['name'], 'id': item['item_id'], 'level': item['item_level'],
                      'bonus': item['bonus_ids'], 'icon_data': icons[str(item['item_id'])], 'source': source, 'note': note, 'gems': gems})
targets = deepcopy(equipment)
for item in targets:
    item['note'] = '已有装备继续保留；非新增获取。' + item['note']
    if item['slot'] == '胸部':
        item.update(id=268222, name='狂野精魂胸甲 → 化生胸铠', level=334, bonus='13334/12854', icon_data=icons['271459'],
                    source='H7盘卷祭坛 · 神话轨来源', note='目标尚未获得。334原始副属性143急速＋58精通；需先化生为271459以保持至少四件套。')
    elif item['slot'] == '腿部':
        item.update(id=271878, name='无羁深仇腿甲（可化生）', level=334, bonus='13334/12854/13847', icon_data=icons['271878'],
                    source='H8乌拉特克 · 毒咒腿', note='目标尚未获得。334为201暴击；毒咒触发急速并降低其他次要属性，可化生为271455保留来源属性和效果。')
    elif item['slot'] == '戒指一':
        item.update(level=334, bonus=item['bonus'].replace('12849', '12854'), gems=[{'id':240890,'name':'无瑕致命榄石'}],
                    source='升级已有神话1/6虫群戒', note='当前已拥有318版本：用纹章等材料升级、补宝石和7967戒指附魔，不分配额外R币。')
    elif item['slot'] == '戒指二':
        item.update(id=268252, name='顶级蛮兵爪戒（候选A）', level=334, bonus='13334/12854/13668', icon_data=icons['268252'],
                    source='H5斯索拉克 · 候选第二戒', note='不是唯一BiS。目标按一孔建表，实际完整奖励需复核；候选B为331暴急制作戒240949，前五有3人使用制作戒。')
write(HERE / 'target-slot-map.json', {'status':'Source-based attainable candidates,not acquired or personally simulated rankings.', 'scope':'OrdinaryMyth334/Crafted331/ascended341,no inaccessibleM7/M8 9/6.', 'equipment':targets,
                                    'alternatives':{'second_ring':[240949,273792,268252],'temporary_legs':237833,'future_shoulder_precursor':239037},
                                    'requires_full_addon_simc_for':['Actual Catalyst predecessor stats','Omnium nodes','personal ring/trinket/gem ranking','actual currency and reward-preview scope']})
verified_raid_ids = [268265,268253,268259,281029,281215,270173,268213]
pools = [
 {'boss':'H7 / 盘卷祭坛','loot_spec':'arms','source':'h7-modern-wowhead-loot.json','derived_arms_spec_ids':[268213,268222,268253,268259,270173],
  'reported_rolled_owned_ids':[268213,268253,268259,270173],'current_target_ids':[268222], 'history_difficulty_separately_confirmed':False,
  'current_remaining_preview_verified':False,'exact_remaining_ids':None,'exact_probability':None,
  'decision':'If all four previous results belong to the current Heroic exclusion scope and the preview only contains268222,spend the next core here;otherwise inspect remaining outcomes before committing.'},
 {'boss':'H8 / 乌拉特克','loot_spec':'arms','source':'h8-wowhead-loot.json','reported_rolled_owned_ids':[268265],'current_target_ids':[271878],
  'other_normal_loot_requiring_preview_check':[270175,270168,270909],'current_remaining_preview_verified':False,'exact_remaining_ids':None,'exact_probability':None,
  'decision':'Target theVenomcursed plate legs;do not assume all remaining outcomes are legs or Heart. Current341 Tendril+Zuljin is a valid high-key pair.'},
 {'boss':'H5 / 斯索拉克','loot_spec':'arms','current_target_ids':[268252],'history_coverage':'unknown','current_remaining_preview_verified':False,'exact_probability':None,
  'decision':'Secondary-ring alternative after chest/legs;compare crafted331 or Myth-track dungeon/Vault ring before spending on a pool with one main target.'},
 {'boss':'H10 / 基希克斯','loot_spec':'arms','reported_rolled_owned_ids':[281029,281215], 'equipped_head_effect':14049,'inferred_head_source':281239,
  'head_predecessor_status':'inferred from unique raid effect,not supplied by the WCL export','current_target_ids':[], 'alternative_weapon_id':280799,
  'decision':'Existing341 Maze-roa is retained;upgrade the owned318 Swarmcaller instead of rolling it again. H10 is currently low priority.'}
]
write(HERE / 'roll-pools.json', {'recorded_at':now,'history_evidence':'User: 可以。这个赛季R到的，身上的所有团本装备都是R到的。',
                               'history_coverage':'Blanket acquisition statement;not a full per-difficulty/current-cycle addon history.','pools':pools})
week = {'schema_version':1,'character_id':'cn-ravenholdt-suoergelin','reset_date':'2026-11-12','timezone':'Asia/Shanghai','patch':'12.1.5','season':'MidnightSeason2',
        'reset_date_basis':'CN Thursday grouping used in established workspace records;no separate maintenance-time claim.',
        'budget':{'reported_balance':None,'reported_at':None,'evidence':'User did not supply a current balance;never inherit the monk character balance.'},
        'snapshot':'snapshots/2026-11-12-wcl.simc','vault':{'status':'unknown','candidates':[]},'pools':pools,
        'plan':{'status':'proposed_not_spent','current_allocation':None,'ordered_priorities':['Check H7 Arms remaining preview for268222 chest after four reported owned R results.','Then H8 for271878 Venomcursed plate legs.','Then consider H5 ring only against actual remaining preview and guaranteed craft/Vault alternatives.','Upgrade and enchant/gem the owned318 Myth Swarmcaller without another roll.'],
                'stop_conditions':['Stop H7 after obtaining a suitable Myth-track chest.','Lower H8 priority after legs;Heart is not an unconditional M+ target.','Keep341 weapon/neck/trinkets and reassess after each actual acquisition.']},
        'events':[{'event_id':'2026-11-12-current-raid-roll-history-confirmation','reported_at':now,'occurred_at':None,'kind':'history_confirmation','acquisition_kind':'bonus_roll','status':'confirmed',
                   'evidence':'User blanket statement that all equipped raid-origin items came from bonus rolls.','identified_raid_base_ids':verified_raid_ids,'difficulty':None,'loot_spec_at_acquisition':None,'cost_paid':None,
                   'tier_sources_not_assumed_from_tier_ids':[271456,271454,271459,271457]}],
        'unresolved':['Full addon export including Catalyst predecessors andOmnium','Current core balance and exclusion difficulty/cycle','Actual H7/H8 reward previews','Vault offers,bag alternatives,crests,sparks andCatalyst charges']}
write(ROOT / 'weeks/2026-11-12.json', week)
profile = {'schema_version':1,'character_id':'cn-ravenholdt-suoergelin','name':'索尔葛林','region':'cn','server':'拉文霍德','timezone':'Asia/Shanghai','class':'warrior','combat_spec':'arms','target_spec':'arms','hero_talents':'slayer',
           'hero_talents_evidence':'Native70783 imports supplied code and produces106 SlayerStrike executes across19 samples;ColossusSmash is a baselineArms ability,not proof of theColossus hero tree.',
           'primary_content':'mythic_plus','goal':'Attainable Arms/Slayer Mythic+ source and stat plan,then allocate rolls using actual remaining reward previews.',
           'constraints':{'mythic_raid_7_8_access':False,'exclude_9_of_6_raid_ceiling':True,'comparison_loot_ilvl':334,'comparison_crafted_ilvl':331,'ascended_core_ilvl':341,'source':'User confirmed the previously stated H/R+M+/Vault scope.'},
           'latest_simc':'snapshots/2026-11-12-wcl.simc','latest_full_simc':None,'latest_items':'snapshots/2026-11-12-wcl.items.json',
           'latest_snapshot_scope':'Equipped-only WCL export1794476649000=Nov12 17:44:09CST;no Catalyst predecessor fields,Omnium,bags or currencies. Full addon export explicitly deferred by user.',
           'latest_gear_review':'analysis/2026-11-12/report.html','latest_gear_evidence':'analysis/2026-11-12/review.md','target_slot_map':'analysis/2026-11-12/target-slot-map.json',
           'target_loadouts_status':'Source-based candidate map only;no precise personal DPS or verified user panel published. Full input needed for whole-loadout ranking.',
           'roll_history_coverage':'Current raid-origin base items reported rolled;individual difficulty/cycle/timestamps remain unknown.','latest_acquisition_update':'weeks/2026-11-12.json#2026-11-12-current-raid-roll-history-confirmation'}
assert not (ROOT / 'profile.json').exists(), 'Preserving an existing profile requires a separate merge.'
write(ROOT / 'profile.json', profile)
players = []
for a in elite['current_player_samples']:
    s=a['secondary_stats'];players.append({'name':a['name'],'score':a['score'],'level':a['item_level'],'url':a['profile_url'],
        **{k:s[source]['percent'] for k,source in [('crit','Critical Strike'),('haste','Haste'),('mastery','Mastery'),('vers','Versatility')]}})
sources = [
 {'title':'11月12日Slayer大米原站榜单（50人）','url':'https://murlok.io/warrior/arms/slayer/m%2B'},
 {'title':'Method Danwarr武器战装备指南（10月25日，12.1.5）','url':'https://www.method.gg/guides/arms-warrior/gearing'},
 {'title':'Method属性和消耗品（10月25日）','url':'https://www.method.gg/guides/arms-warrior/stats-races-and-consumables'},
 {'title':'Icy Veins Archimtiros装备/化生/R规则指南（10月12日）','url':'https://www.icy-veins.com/wow/arms-warrior-pve-dps-gear-best-in-slot'},
 {'title':'H7当前NPC掉落及专精元数据','url':'https://www.wowhead.com/npc=259854/hex-lord-malacrass'},
 {'title':'H7完整首领奖励说明','url':'https://www.wowhead.com/guide/midnight/raids/venomous-abyss-coiled-altar-boss-strategy-abilities'},
 {'title':'H8当前NPC掉落资料','url':'https://www.wowhead.com/npc=268956/ulatek'},
 {'title':'H8完整首领奖励说明','url':'https://www.wowhead.com/guide/midnight/raids/venomous-abyss-ulatek-boss-strategy-abilities'},
 {'title':'334毒咒无羁深仇腿甲完整提示','url':tips['271878_effect']['source_url']},
 {'title':'334狂野精魂胸甲','url':tips['268222']['source_url']},
 {'title':'无瑕致命榄石：16急速7暴击','url':tips['240890']['source_url']},
 {'title':'已核验的官方SimC70783源码','url':'https://github.com/simulationcraft/simc/tree/de11f57df75dda668bae6ac7043a43b98831fa96'}]
stats = [{'name':'高手暴击参考','rating':'951–1231','percent':'31–37','comparison':'Slayer前五当前实装，非你的已验证面板。','advice':'以暴击与急速为主要绿字方向，完整SimC再确定比例。'},
         {'name':'高手急速参考','rating':'740–1070','percent':'19–27','comparison':'前五分布跨度较大，种族及增益口径未知。','advice':'现有暴急制作腕鞋可保留；不用为了某一百分比重做整套。'},
         {'name':'高手精通参考','rating':'801–940','percent':'28–31','comparison':'这是武器战重伤精通，按当前英雄树比较。','advice':'保留合理精通；不要把来源不明的套装默认绿字作为当前真实面板。'},
         {'name':'高手全能参考','rating':'107–155','percent':'2–3','comparison':'你当前腿部单件就有120全能，项链另有105。','advice':'腿部是明确可调整位置；优先以适合的高等级来源替换。'}]
usage=[{'name':'武器268213／项链268265','value':'前五各5/5','note':'装备ID相同；未获取高手单件装等、完整bonus及化生前驱。'},
       {'name':'触须＋祖尔金完整饰品组合','value':'前五3/5','note':'Farover、Tankdmg、Doxorsw与用户同组合；先保留341双饰品。'},
       {'name':'守护者的躁动核心270165','value':'前五2/5','note':'分别搭配祖尔金或触须。这是躁动核心，不是乌心270175。'},
       {'name':'制作戒240949','value':'前五3/5','note':'普通第三件制作不受双美化数量限制；没有额外美化即可与现有双奥纹共存。'},
       {'name':'H5爪戒268252','value':'前五1/5','note':'是第二戒候选之一，不能把单件采用率当成个人模拟最优。'},
       {'name':'腰带268259／披风268253','value':'前五各4/5','note':'两件你已经334，不需要重复追。'},
       {'name':'双奥纹','value':'前五4/5；用户已两件','note':'余下一人洛阿戒＋稳定宝石弹药带；不是每个高手都同一美化组合。'}]
limits=[
 '用户确认当前获取范围H团本R＋大米/低保，排除M7/M8的9/6；普通神话334、制作331，现有晋升武器/项链/饰品341以完整bonus及原生数据为准。高手337–339均装不直接作为你必须追的上限。',
 '当前只收到WCL实装导出，完整游戏内SimC用户晚点提供。化生前驱、Omnium、背包、资源和当前R币数未知；当前套装名称不证明它来自团本、也不证明默认副属性就是实际副属性。',
 '已做原生70783身份验证：单体和DungeonSlice均支持，SlayerStrike实际产生伤害；本次未做可用于个人排名的DPS比较，也不发布未经确认的角色属性百分比。',
 'Native原始WCL默认套装解析仅供检查输入；头带14049，可推定H10板甲头281239来源，但需要完整导出确认继承属性。不能将这次默认解析的1058暴击/766急速等直接当你的真实面板。',
 'Slayer榜11月12日10:05更新，前五个人页16:53更新，评分4309–4380；样本覆盖美欧韩台，不含国服。高手百分比取整且增益口径未知，仅作参考范围。',
 '前五单件装等、完整bonus、前驱和制作属性均未获证实；套装腿采用5/5不证明五人都是同一前驱。',
 '身上团本来源均R来的，是用户确认事实；每次R难度、当前排除轮次、已重置与否没有逐项记录。H7四件是否同属当前H排除范围，需奖励预览或完整R历史确认。',
 'H7数据库明确武器专精的五件战斗装备为武器268213、胸268222、披风268253、腰268259、饰品270173；用户已有其中四件来自R。数据库掉落过滤仍不等同于实际剩余R奖励预览，不写100%保证。',
 'H8有其他饰品和珍玩等普通掉落资料；当前实际R资格/排除未全核，不能把剩余奖励直接简化为腿＋乌心。',
 '318神话1/6虫群戒可升级334；321英雄6/6胸、腿、阿曼尼戒需新神话轨来源。现有头已打孔，只有腕／腰额外孔待资源核实，不能套用另一个角色的三孔缺口。',
 '新增胸需先化生再穿以保持四件套；毒咒腿可以作为第五套化生，但没有第五件套额外奖励。制作桥接腿必须考虑它会替换未来H8腿和消耗的火花成本。',
 '指南使用率和常规属性优先级不能替代整套个人模拟。饰品、第二戒与宝石最终配比保留到完整SimC后验证。',
 '引擎对套装头/虫群戒的伤害不分摊机制仍有未实服核验假设；本次只做输入身份验证，不据此给出精确实战DPS增幅。']
data={'meta':{'date':'2026-11-12 · WCL17:44:09','character':'索尔葛林 · 拉文霍德 · 屠戮者武器战','patch':'12.1.5 / 原生70783身份验证','content':'大秘境 · 可获取配装与R路线','engine':'身份验证通过；精确收益待完整SimC','budget_note':'当前R币数未提供。用户确认身上团本来源均R获得；难度/排除轮次仍需预览。按H/R＋大米/低保规划，不考虑M7/M8的9/6。'},
      'lead':'先检查H7武器专精剩余预览：你已R到武器、祖尔金、腰带和披风，胸甲是当前主要缺口。若同H排除范围只剩胸，下一枚R给H7；拿胸后停。\n再追H8毒咒暴击腿。现有341武器、项链、触须和祖尔金保留；318虫群戒直接升级、补宝石附魔。\n当前双饰品与前五3人相同；第二戒有爪戒、制作戒和大米戒多条路线，等完整SimC决定细微优劣。',
      'stats':stats,'equipment':equipment,'target_equipment':targets,'elite':players,'usage':usage,
      'models':[{'id':'slice','label':'大米切片','detail':'身份验证支持此模型。本次缺化生前驱和Omnium，不发布当前个人DPS排名；后续完整输入后比较整套。'},
                {'id':'st','label':'单体','detail':'已完成短跑身份验证，未作为个人收益估计。'},
                {'id':'aoe','label':'多目标','detail':'待完整输入后与单体、切片共同验证，避免把单一场景当全局BiS。'}],
      'comparisons':[],
      'branches':[{'outcome':'下一枚R · 条件优先','preferred':'H7盘卷祭坛，拾取专精武器','reason':'五件明确武器专精战斗装备中，你已有武器、披风、腰带、祖尔金四件R结果。缺狂野精魂胸甲268222。','comparison':'先核四次结果是否同H排除范围；若预览只剩胸，直接针对胸。胸从321换新神话轨来源，升334后先化生再穿。'},
                  {'outcome':'H7胸到手后','preferred':'H8乌拉特克：无羁深仇腿甲271878','reason':'当前腿321且带120全能；目标334为201暴击并带毒咒触发。现有341项链已R，可在同范围内核对排除。','comparison':'此处的首要目标是腿；当前双饰品已是高分实装组合，不因一般指南写乌心就优先换掉触须。'},
                  {'outcome':'胸腿补齐后的第二戒','preferred':'H5爪戒／331制作戒／神话轨大米戒','reason':'前五有3人用制作戒、1人用爪戒，另有大米/迷宫组合。制作戒不增加美化就能与现有两奥纹共存。','comparison':'如果H5预览填充物多，先用可确定的制作或低保来源；当前321阿曼尼戒不能沿英雄轨直接升334。'},
                  {'outcome':'无需额外R币的立即行动','preferred':'升级已有虫群戒、补空孔和附魔','reason':'虫群318神话1/6，可以升334。当前空孔gem_id=0、缺7967附魔；头已有孔，腕和腰孔后续按资源补。','comparison':'现有H10头特效、341触须、318虫群戒已具备；341迈兹罗阿为前五5/5武器，当前不为H10另一把武器优先R。'}],
      'actions':[{'title':'先处理当前已有装备','body':'把318虫群戒升334，补无瑕致命榄石240890和7967戒指附魔；鞋附魔也缺。保留341武器、项链和双饰品，334腰/披风与331双奥纹腕鞋。'},
                 {'title':'H7胸：核预览、拿到后停','body':'按武器专精核对武器、祖尔金、腰、披风四个已R结果的H排除范围。主要目标是狂野精魂胸甲268222，拿新神话轨来源升334并化生271459，保四件套。'},
                 {'title':'H8腿：替换321暴全腿','body':'追无羁深仇腿甲271878毒咒版，原始334为201暴击。可化生271455保留毒咒；若短期拿不到，再比较331暴急制作腿237833作为桥接，避免提前消耗火花。'},
                 {'title':'第二戒不要只认一张BiS表','body':'H5顶级蛮兵爪戒268252、331普通暴急制作戒240949、334神话轨阿曼尼戒或其他大米戒都是候选。腕鞋已经双奥纹，第三件普通制作戒合法。'},
                 {'title':'属性先走暴击＋急速，细调等完整SimC','body':'通用起点力量＞暴击＞急速＞精通＞全能。前五暴31–37%、急19–27%、精28–31%、全2–3%，只作实装参考。你现有无瑕致命榄石为16急速7暴击，可先维持。'},
                 {'title':'补完整导出后再定最后几步','body':'核对化生前驱、Omnium、背包、当前R币/排除历史与低保，再比较触须/祖尔金/躁动核心/乌心、第二戒及宝石合剂的完整组合。当前不虚报个人提升百分比。'}],
      'consumables':[{'name':'宝石','current':'现有240983钻石与240890普通宝石；虫群戒孔为空','recommendation':'先填空孔。240890是16急速＋7暴击，与通用推荐一致；最终暴击/急速分配等完整导出后整套比较。','url':tips['240890']['source_url']},
                     {'name':'双奥纹和制作','current':'331暴急制作腕＋331暴急制作鞋','recommendation':'保留这两个美化部位；第三件普通制作戒不计入美化上限。','url':'https://www.method.gg/guides/arms-warrior/gearing'},
                     {'name':'合剂与食物','current':'WCL导出未提供','recommendation':'通用指南以急速合剂、输出食物为起点；不把它们算进未经核实的角色面板。','url':'https://www.method.gg/guides/arms-warrior/stats-races-and-consumables'},
                     {'name':'附魔','current':'虫群戒无附魔、制作鞋无附魔；另一戒已7967','recommendation':'先补7967戒指附魔；鞋按现版本输出/移动需求补齐，现有武器8689继续保留。','url':'https://www.method.gg/guides/arms-warrior/stats-races-and-consumables'}],
      'limits':limits,'sources':sources,
      'downloads':[{'title':'原始WCL完整实装文本','path':'../../snapshots/2026-11-12-wcl.simc'},
                   {'title':'逐件完整bonus/装等查验','path':'../../snapshots/2026-11-12-wcl.items.json'},
                   {'title':'当前高手实装及来源更新时间','path':'elite-evidence.json'},
                   {'title':'可获取目标槽位与备选（非已获得）','path':'target-slot-map.json'},
                   {'title':'R池与历史局限','path':'roll-pools.json'},
                   {'title':'当前周计划与已报告事实','path':'../../weeks/2026-11-12.json'}]}
write(HERE/'report-data.json',data)
builder_path=Path('records/cn-barrens-shaseng/analysis/2026-10-29/build-report.py')
spec=importlib.util.spec_from_file_location('gear_report',builder_path);builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
target_table=builder.table(['部位','候选装备','装等','宝石','来源与条件'],[builder.equipment_row(x) for x in targets],'可获取目标配装 · 来源候选，尚未个人整套排名')
extra_section=builder.section('targets','可获取目标配装',target_table,'沿用当前强装备，替换胸／腿、升级虫群，第二戒保留多路线。下表目标与已获得装备分开记录。')
document=builder.render(data).replace('<section id="branches"',extra_section+'<section id="branches"',1)
document=document.replace('<a href="#branches">R币与兑换</a>','<a href="#targets">目标配装</a><a href="#branches">R币与兑换</a>',1)
(HERE/'report.html').write_text(document,encoding='utf-8')
review='''# Arms/Slayer Mythic+ source plan — November12,2026

Character:CN/Ravenholdt 索尔葛林. The supplied WCL timestamp is2026-11-12 17:44:09CST. Raw equipped average is332.375 by tooltip lookup,with a two-handed weapon counted twice. Four current tier pieces and two Arcanoweave linings are present. The raw import is immutable;Chinese race anddps role are normalized only in the native identity inputs.

Native70783/de11f57 imports the supplied build and produces SlayerStrike damage. Both single-target andDungeonSlice identity checks report supported fight styles with no severe diagnostics. These short runs establish identity,not reliable personal DPS or verified panel stats. WCL lacks Catalyst predecessors,Omnium,bags and currencies. In particular,the14049 head effect suggests H10 source281239,whose retained stats differ substantially from default tier stats. Full addon export is explicitly deferred by the user.

Current source-backed route:H7 chest first if the Arms remaining preview is clean after four existing results;thenH8 Venomcursed plate legs;then compareH5 ring with crafted/Vault alternatives. The modernH7 NPC259854 metadata explicitly associates spec71 with268213,268222,268253,268259,270173. Four are owned and user-reported as rolled. Their exact difficulty/current-cycle scope still needs confirmation;there is no unconditional100% claim. The legacyNPC24239 extraction mismatch is not an empty pool. H8 normal loot data includes other trinkets and a curio;normal loot eligibility is not a complete remainingR preview.

The user confirms all currently equipped raid-origin items were rolled. This establishes ownership/method for identifiable raid bases,not precursor origins for every tier ID,and not individual costs/difficulties/dates. Current coin balance remainsnull. No balance is inherited from the monk character and no proposed action is recorded as spending.

The currently equipped341 Tendril+Zuljin pair is used by three of the Slayer top-five. Two others use270165 KeeperSeethingCore with one of those trinkets;270165 is not270175 UlatekHeart. All five use268213 and268265. Keep the owned341 weapon/neck/trinkets rather than applying a generic raid trinket ranking to Mythic+ without personal testing.

Clear gaps:321 Hero6/6 chest andlegs;318 Myth1/6 Swarmcaller with an empty socket/no enchant;321 Hero6/6 Amani ring. The Swarmcaller can be upgraded directly to334,but the Hero-track items need new Myth-track sources. Current321 legs have120 versatility. TargetH7 chest268222 must be catalyzed before replacing the current tier chest;H8 legs271878 retain201crit and Venomcursed effect13847 at334. Current wrists/boots already provide two Arcanoweave instances;another ordinary craft does not violate the embellishment limit.

Matched player sample:five current Arms/Slayer profiles,4309–4380 score,337–339 average item level,updated16:53CST. The Slayer page has50 players4188–4380 and was updated10:05CST. RegionsUS/EU/KR/TW excludeCN. Displayed stat ranges:crit31–37%(951–1231),haste19–27%(740–1070),mastery28–31%(801–940),vers2–3%(107–155). These are rounded population observations with unknown buff basis,not required thresholds or a replacement for the missing player panel.

report.html includes current gear,a separate attainable target map,conditional roll routes,player profiles and source limitations. No precise personal DPS deltas or globally optimalBiS claim are published. Full addonSimC should drive later whole-loadout trinket/ring/gem/consumable comparisons.

'''+ '\n'.join(f"- [{x['title']}]({x['url']})" for x in sources)+'\n'
(HERE/'review.md').write_text(review,encoding='utf-8')
write(HERE/'identity-validation.json',{'checked_at':now,'native_build':'12.1.5.70783','source_commit':'de11f57df75dda668bae6ac7043a43b98831fa96','hero_tree':'Slayer',
       'hero_evidence':'SlayerStrike19 samples,106 total executes','single_target_valid':True,'dungeon_slice_valid':True,'current_tier_pieces':4,'lining_instances':2,
       'personal_dps_ranking_published':False,'user_panel_stats_verified':False,'omnium_supplied':False,'catalyst_predecessors_supplied':False,
       'source_freshness':'source-freshness.json','scope':'Short native identity only;raw default tier stats are provisional.'})
print({'report':str(HERE/'report.html'),'current_gear_rows':len(equipment),'target_rows':len(targets),'elite_players':len(players),'coin_balance':None,'personal_dps_published':False})
