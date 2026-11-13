"""Compare the dated Elemental snapshot with obtainable rewards and full sets."""

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RAW = HERE.parents[1] / 'snapshots/2026-11-13-1320.simc'
ENGINE = REPO / '.local/simc-build-70783/Release/simc.exe'
SOURCE = REPO / '.local/simc-source-70783'
SLOTS = 'head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand off_hand'.split()
TIERS = {271483, 271481, 271486, 271484, 271482}
MODELS = {'aoe': (5, 90), 'st': (1, 240), 'burst': (8, 40), 'long': (5, 180)}
PAIR = {'ch': '32/36', 'cm': '32/49', 'hm': '36/49'}


def fields(line):
    return dict(p.split('=', 1) for p in line.split('=', 1)[1].split(',') if '=' in p)


def update(line, **changes):
    f = fields(line)
    for k, v in changes.items():
        if v is None:
            f.pop(k, None)
        else:
            f[k] = str(v)
    return line.split('=', 1)[0] + '=,' + ','.join(f'{k}={v}' for k, v in f.items())


def load():
    lines = [l for l in RAW.read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    gear = {l.split('=', 1)[0]: l for l in lines if l.split('=', 1)[0] in SLOTS}
    actor = [l for l in lines if l.split('=', 1)[0] not in SLOTS + ['shirt', 'tabard', 'talents']]
    return actor, gear


def bag(ident, slot):
    line = next(l[2:] for l in RAW.read_text(encoding='utf-8').splitlines()
                if l.startswith('# ') and re.search(r',id=' + str(ident) + r'(?:,|$)', l))
    return slot + line[line.index('='):]


def item(slot, ident, level=334, bonus='13334/12854', **kwargs):
    return update(f'{slot}=,id={ident}', ilevel=level, bonus_id=bonus, **kwargs)


def recraft(line, pair, lining=None):
    # Missive bonuses replace crafted-stat placeholders before crafted_stats is read.
    removed = {'8790', '8791', '8792', '8793', '8794', '8795'}
    if lining is not None:
        removed |= {'12384', '13771'}
    f = fields(line)
    bonuses = [b for b in f.get('bonus_id', '').split('/') if b and b not in removed]
    if lining:
        bonuses.append('12384')
    return update(line, bonus_id='/'.join(bonuses), crafted_stats=PAIR[pair])


def craft(slot, ident, pair='ch', lining=False, gem=None, enchant=None):
    b = '12214/13667/12497/13751/14001/13836'
    if lining:
        b += '/8960/12384'
    return item(slot, ident, 331, b, crafting_quality=5, content_tuning=3615,
                crafted_stats=PAIR[pair], gem_id=gem, enchant_id=enchant)


def candidates():
    _, base = load()
    result = {'current': ({}, {})}
    for ident in (268249, 252258, 159459, 272149):
        result[f'owned_ring_{ident}'] = ({'finger1': bag(ident, 'finger1')}, {})
    for level in (318, 321, 334):
        b = {318: '13334/12849', 321: '13440/12846', 334: '13334/12854'}[level]
        for ident, label in ((270170, 'gland'), (250215, 'flask')):
            for slot, old in (('trinket2', 'bag'), ('trinket1', 'tendril')):
                result[f'vault_{label}_{level}_for_{old}'] = ({slot: item(slot, ident, level, b)}, {})
        result[f'vault_belt_{level}'] = ({'waist': item('waist', 268254, level, b + '/13696')}, {})
        result[f'vault_weapon_{level}'] = ({'main_hand': item('main_hand', 273780, level, b, enchant_id=8689)}, {})
        cloak = {'back': item('back', 268248, level, b)}
        result[f'vault_cloak_{level}'] = (cloak, {})
        result[f'vault_cloak_{level}_move_lining'] = (
            {**cloak, 'waist': recraft(base['waist'], 'ch', lining=True)}, {})
    for ident in (273796, 270161, 270173):
        result[f'owned_trinket_{ident}'] = ({'trinket2': bag(ident, 'trinket2')}, {})
    for ident, label in ((270168, 'font'), (270169, 'idol'), (273649, 'emblem'), (273796, 'vial'), (270161, 'fang'), (273794, 'knot'), (270175, 'heart'), (270167, 'seastone')):
        result[f'target_{label}_334'] = ({'trinket2': item('trinket2', ident)}, {})
    for pair in PAIR:
        result[f'crafts_{pair}'] = ({slot: recraft(base[slot], pair) for slot in ('back', 'wrist', 'waist')}, {})
        result[f'crafted_ring_{pair}'] = ({'finger1': craft('finger1', 240949, pair, gem=240890, enchant=7967)}, {})
        result[f'crafted_shoulder_{pair}'] = ({'shoulder': craft('shoulder', 244580, pair, enchant=8001)}, {})
    result['h5_ring'] = ({'finger1': item('finger1', 268252, bonus='13334/12854/13668', enchant_id=7967, gem_id=240890)}, {})
    result['amani334'] = ({'finger1': update(base['finger1'], bonus_id='13334/12854/13668', ilevel=334, content_tuning=None)}, {})
    result['alternative_shield334'] = ({'off_hand': item('off_hand', 268262)}, {})
    result['alternative_ring272148_321'] = ({'finger1': item('finger1', 272148, 321, '13440/12846/13668', enchant_id=7967, gem_id=240898)}, {})
    for pair in PAIR:
        result[f'feet_271440_{pair}'] = ({'feet': item('feet', 271440, crafted_stats=PAIR[pair], enchant_id=7963)}, {})
    for slot, ident, label in (('main_hand', 271092, 'weapon'), ('neck', 268265, 'neck'), ('trinket2', 270164, 'bag')):
        line = update(base[slot], ilevel=341, bonus_id=fields(base[slot])['bonus_id'].replace('12854', '12856'))
        result[f'ascend_{label}_341'] = ({slot: line}, {})
    result['h7_cloak_wrist_waist_lining'] = ({
        'back': item('back', 268253),
        'waist': recraft(base['waist'], 'ch', lining=True)}, {})
    for family, gem in (('crit_haste', 240906), ('haste_crit', 240890), ('crit_mastery', 240908), ('mastery_crit', 240898)):
        changes = {}
        for slot in ('head', 'neck', 'finger1', 'finger2'):
            changes[slot] = update(base[slot], gem_id=f'240967/{gem}' if slot == 'neck' else gem)
        result[f'gems_{family}'] = (changes, {})
    for label, flask in (('crit', 'flask_of_the_shattered_sun_2'), ('haste', 'flask_of_the_blood_knights_2')):
        result[f'flask_{label}'] = ({}, {'flask': flask})
    ready = {slot: recraft(base[slot], 'ch') for slot in ('back', 'wrist', 'waist')}
    for slot in ('head', 'neck', 'finger1', 'finger2'):
        ready[slot] = update(base[slot], gem_id='240967/240906' if slot == 'neck' else 240906)
    opt = {'flask': 'flask_of_the_shattered_sun_2'}
    result['ready'] = (ready, opt)
    for label, line in (
        ('h5', result['h5_ring'][0]['finger1']),
        ('amani334', result['amani334'][0]['finger1']),
        ('craft_ch', craft('finger1', 240949, 'ch', gem=240906, enchant=7967)),
        ('owned_alchemist', update(bag(268249, 'finger1'), gem_id=240906)),
    ):
        target = {**ready, 'finger1': update(line, gem_id=240906)}
        result[f'ready_{label}'] = (target, opt)
        result[f'ready_{label}_flask334'] = ({**target, 'trinket2': item('trinket2', 250215)}, opt)
        result[f'ready_{label}_vial334'] = ({**target, 'trinket2': item('trinket2', 273796)}, opt)
    target = result['ready_h5'][0]
    result['target_shoulder_ch'] = ({**target, 'shoulder': craft('shoulder', 244580, 'ch', enchant=8001)}, opt)
    result['target_bag341'] = ({**target, 'trinket2': result['ascend_bag_341'][0]['trinket2']}, opt)
    result['target_cloak334'] = ({**target, **result['h7_cloak_wrist_waist_lining'][0]}, opt)
    for gem in (240890, 240908, 240898):
        gems = dict(target)
        for slot in ('head', 'neck', 'finger1', 'finger2'):
            gems[slot] = update(gems[slot], gem_id=f'240967/{gem}' if slot == 'neck' else gem)
        result[f'target_gems_{gem}'] = (gems, opt)
    for pair in ('ch', 'cm'):
        loa = {'finger1': craft('finger1', 251513, pair, gem=240906, enchant=7967),
               'back': recraft(base['back'], 'ch', lining=False)}
        result[f'loa_{pair}'] = (loa, {})
    for label, changes in (('current', {}), ('ready_h5', target)):
        gems = dict(changes)
        for slot in ('head', 'neck', 'finger1', 'finger2'):
            line = gems.get(slot, base[slot])
            gems[slot] = update(line, gem_id='240983/240906' if slot == 'neck' else 240906)
        result[f'{label}_diamond983'] = (gems, opt if label != 'current' else {})
    for ring_label, ring in (('h5', result['h5_ring'][0]['finger1']),
                             ('craft', result['crafted_ring_ch'][0]['finger1'])):
        for flask_label, flask in (('crit', 'flask_of_the_shattered_sun_2'),
                                   ('haste', 'flask_of_the_blood_knights_2')):
            changes = {'finger1': update(ring, gem_id=240898)}
            options = {'flask': flask}
            result[f'joint_{ring_label}_{flask_label}'] = (changes, options)
            result[f'joint_{ring_label}_{flask_label}_waistch'] = (
                {**changes, 'waist': recraft(base['waist'], 'ch')}, options)
    for ident in (272147, 272148, 272149, 272150):
        result[f'vendor_ring_{ident}'] = ({
            'finger1': item('finger1', ident, bonus='13334/12854/13668', enchant_id=7967, gem_id=240898)}, {})
    for slot, ident in (('shoulder', 272252), ('feet', 272248), ('hands', 272249), ('legs', 272251), ('waist', 272253), ('off_hand', 272276)):
        ench = {'shoulder': 8001, 'feet': 7963, 'legs': 7935}.get(slot)
        result[f'vendor_{slot}' + ('_272251' if slot == 'legs' else '')] = ({slot: item(slot, ident, enchant_id=ench)}, {})
    result['vendor_wrist'] = ({'wrist': item('wrist', 272254),
                              'waist': recraft(base['waist'], 'ch', lining=True)}, {})
    for ident in (272225, 272226, 272227, 272230):
        result[f'vendor_cloak_{ident}'] = ({'back': item('back', ident),
                                          'waist': recraft(base['waist'], 'ch', lining=True)}, {})
    for ident in (272147, 272148, 272149, 272150):
        for label, flask in (('crit', 'flask_of_the_shattered_sun_2'), ('haste', 'flask_of_the_blood_knights_2')):
            result[f'joint_vendor_{ident}_{label}'] = (result[f'vendor_ring_{ident}'][0], {'flask': flask})
    for label, source in (('shoulder', 'vendor_shoulder'), ('wrist', 'vendor_wrist'), ('cloak', 'vendor_cloak_272226')):
        changes, options = result['joint_h5_haste']
        result[f'joint_h5_vendor_{label}'] = ({**changes, **result[source][0]}, options)
    for gem in (240898, 240890):
        wrist = update(base['wrist'], bonus_id=fields(base['wrist'])['bonus_id'] + '/13695', gem_id=gem)
        result[f'vault_socket_{gem}'] = ({'wrist': wrist}, {})
        changes, options = result['joint_vendor_272148_haste']
        result[f'free_route_socket_{gem}'] = ({**changes, 'wrist': wrist}, options)
    return result


def talents(mode):
    raw = RAW.read_text(encoding='utf-8')
    if mode == 'st':
        return re.search(r'# Saved Loadout: 单体\n# talents=(.+)', raw)[1]
    return re.search(r'^talents=(.+)', raw, re.M)[1]


def run(key, mode, iterations, seed, unbuffed=False):
    actor, gear = load()
    changes, options = candidates()[key]
    gear.update(changes)
    vendor = json.loads((HERE / 'reward-source-evidence.json').read_text(encoding='utf-8'))
    types = {r['item_id']: r['inventory_type'] for r in vendor['jindozan']['catalogue']['shaman_caster_items']}
    allowed = {'head': {1}, 'neck': {2}, 'shoulder': {3}, 'chest': {5, 20}, 'waist': {6}, 'legs': {7},
               'feet': {8}, 'wrist': {9}, 'hands': {10}, 'finger1': {11}, 'finger2': {11}, 'back': {16},
               'main_hand': {13, 17, 21}, 'off_hand': {14, 22, 23}, 'trinket1': {12}, 'trinket2': {12}}
    for slot, line in gear.items():
        ident = int(fields(line)['id'])
        if ident in types and types[ident] not in allowed[slot]:
            raise RuntimeError(f'Illegal inventory slot: {ident} in {slot}')
        if int(fields(line).get('ilevel', 0)) > 334 and slot not in {'neck', 'main_hand', 'trinket1', 'trinket2'}:
            raise RuntimeError(f'Unsupported ascension slot: {slot}')
    settings = {'flask': 'flask_of_the_magisters_2', 'food': 'harandar_celebration',
                'potion': 'lights_potential_2', 'augmentation': 'void_touched',
                'temporary_enchant': 'main_hand:thalassian_phoenix_oil_2,if=!talent.flametongue_weapon'}
    settings.update(options)
    if unbuffed:
        settings = {k: 'disabled' for k in settings}
    targets, length = MODELS[mode]
    stem = f'live70783-{"stats" if unbuffed else mode}-{key}-{iterations}-{seed}'
    path = HERE / f'{stem}.simc'
    content = '\n'.join(['# User 2026-11-13 13:20 export; hypothetical replacements are not acquisitions.',
                         '# Supported fixed-target reference only; Elemental rejects DungeonSlice/Route.',
                         'ptr=0', 'item_db_source=local', *actor, 'talents=' + talents(mode), *gear.values(),
                         *[f'{k}={v}' for k, v in settings.items()], 'optimal_raid=0', 'override.bloodlust=0',
                         'fight_style=Patchwerk', f'max_time={30 if unbuffed else length}',
                         f'desired_targets={targets}', 'vary_combat_length=0', 'fixed_time=1',
                         'threads=8', f'iterations={iterations}', f'seed={seed}', 'confidence=0.95']) + '\n'
    if path.exists() and path.read_text(encoding='utf-8') != content:
        raise RuntimeError(f'Preserving different existing input: {path.name}')
    path.write_text(content, encoding='utf-8')
    validation = path.with_suffix('.validation.json')
    if validation.exists() and path.with_suffix('.json').exists() and json.loads(validation.read_text(encoding='utf-8')).get('accepted'):
        return
    with path.with_suffix('.run.log').open('w', encoding='utf-8') as log:
        proc = subprocess.run([str(ENGINE), str(path), f'json2={path.with_suffix(".json")}',
                               f'output={path.with_suffix(".txt")}'], stdout=log, stderr=subprocess.STDOUT)
    data = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    player = data['sim']['players'][0]
    tiers = sum(int(fields(line).get('id', 0)) in TIERS for line in gear.values())
    linings = sum('12384' in fields(line).get('bonus_id', '').split('/') for line in gear.values())
    loa_count = sum(int(fields(line).get('id', 0)) == 251513 for line in gear.values())
    severe = bool(data.get('errors') or data['sim'].get('errors')) or any(
        'severe' in x.get('level', '').lower() for x in data.get('logs', []))
    dps = player['collected_data']['dps']
    result = {'candidate': key, 'model': 'stats' if unbuffed else mode, 'iterations': iterations, 'seed': seed,
              'accepted': proc.returncode == 0 and player.get('valid_fight_style') is True and not severe and tiers >= 4 and linings + loa_count <= 2,
              'exit_code': proc.returncode, 'valid_fight_style': player.get('valid_fight_style'),
              'tier_count': tiers, 'lining_count': linings, 'dps': dps['mean'], 'samples': dps['count'],
              'ci95': dps['mean_std_dev'] * data['sim']['options']['confidence_estimator'],
              'stats': player['collected_data']['buffed_stats'], 'gear': player['gear'], 'logs': data.get('logs', []),
              'buff_names': [x['name'] for x in player.get('buffs', []) + player.get('buffs_constant', [])],
              'action_names': [x['name'] for x in player.get('stats', [])]}
    validation.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('candidate', 'model', 'accepted', 'dps', 'ci95', 'samples')}, ensure_ascii=False), flush=True)
    if not result['accepted']:
        raise RuntimeError(f'Rejected: {stem}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', action='append', default=[])
    p.add_argument('--model', action='append', choices=MODELS, default=[])
    p.add_argument('--iterations', type=int, default=1500)
    p.add_argument('--seed', type=int, default=26111331)
    p.add_argument('--unbuffed', action='store_true')
    args = p.parse_args()
    manifest = {'recorded_at': datetime.now().astimezone().isoformat(),
                'source_commit': subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip(),
                'engine_sha256': hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
                'raw_sha256': hashlib.sha256(RAW.read_bytes()).hexdigest(),
                'live_build': '12.1.5.70783', 'models': MODELS, 'candidates': list(candidates()),
                'talents': {m: talents(m) for m in MODELS}, 'hero_tree': 'Farseer; ancestor pet and call_of_the_ancestors confirmed',
                'boundaries': 'Ordinary Myth334/Crafted331/ascended341; no M7/M8 9/6; no socket tool ownership reported for this character.',
                'effects': 'Gland kill resets absent during fixed-target survival. Gloves and Swarmcaller use unverified non-split AoE. Rune targeting unverified.',
                'craft_stats': 'Baseline keeps all bonus IDs; 8790/8791 missive bonuses intentionally override stale crafted_stats placeholders. Recraft candidates remove missive bonuses before applying chosen pairs.'}
    (HERE / 'simc-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for mode in args.model or ['aoe']:
        for key in args.candidate or ['current']:
            run(key, mode, args.iterations, args.seed, args.unbuffed)


if __name__ == '__main__':
    main()
