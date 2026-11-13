"""Compare complete attainable end states with common sockets and core levels."""

import argparse
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dated_study', HERE / 'personal-study.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
PAIRS = ('ch', 'cm', 'hm')
MODELS = {'long': (5, 180), 'aoe': (5, 90), 'st': (1, 240)}


def sockets(gear, family='mixed'):
    gear = dict(gear)
    gems = {'head': 240906, 'finger1': 240898, 'finger2': 240890, 'wrist': 240890, 'waist': 240898}
    diamond = 240967
    neck_gem = 240914
    if family in ('haste', 'mastery', 'crit'):
        diamond = 240983
        gem = {'haste': 240890, 'mastery': 240898, 'crit': 240906}[family]
        gems = {slot: gem for slot in gems}
        neck_gem = gem
    for slot, gem in gems.items():
        f = s.fields(gear[slot])
        bonus = f.get('bonus_id', '').split('/')
        if slot in ('wrist', 'waist') and '13695' not in bonus:
            bonus.append('13695')
        if slot.startswith('finger') and '13668' not in bonus:
            bonus.append('13668')
        gear[slot] = s.update(gear[slot], bonus_id='/'.join(bonus), gem_id=gem)
    gear['neck'] = s.update(gear['neck'], gem_id=f'{diamond}/{neck_gem}')
    return gear


def ring(label, pair):
    if label == 'claw':
        return s.item('finger1', 268252, bonus='13334/12854/13668', enchant_id=7967)
    if label == 'serpent':
        return s.item('finger1', 272148, bonus='13334/12854/13668', enchant_id=7967)
    if label == 'amani':
        return s.item('finger1', 273792, bonus='13334/12854/13668', enchant_id=7967)
    if label == 'craft':
        return s.craft('finger1', 240949, pair, enchant=7967)
    raise ValueError(label)


def structure(placement, ring_label, pair):
    _, gear = s.load()
    gear['trinket2'] = s.update(gear['trinket2'], bonus_id='13334/12856', ilevel=341)
    gear['finger1'] = ring(ring_label, pair)
    craft_ids = {'back': 239656, 'wrist': 244584, 'waist': 244581, 'feet': 244577}
    for slot in ('back', 'wrist', 'waist', 'feet'):
        if slot in placement:
            ench = 7963 if slot == 'feet' else None
            gear[slot] = s.craft(slot, craft_ids[slot], pair, lining=True, enchant=ench)
        elif slot == 'back':
            gear[slot] = s.item(slot, 268253)
        elif slot == 'wrist':
            gear[slot] = s.item(slot, 272254)
        elif slot == 'waist':
            gear[slot] = s.craft(slot, craft_ids[slot], pair) if placement == ('back', 'wrist') else s.item(slot, 268254)
    return sockets(gear)


def candidates():
    actor, raw = s.load()
    result = {'current': {'gear': raw, 'options': {}, 'stage': 'reference'}}
    ref = dict(raw)
    ref['trinket2'] = s.update(ref['trinket2'], bonus_id='13334/12856', ilevel=341)
    result['owned_endstate'] = {'gear': sockets(ref), 'options': {}, 'stage': 'reference'}
    placements = {'bw': ('back', 'wrist'), 'ww': ('wrist', 'waist'), 'wf': ('wrist', 'feet'),
                  'bf': ('back', 'feet'), 'bv': ('back', 'waist'), 'vf': ('waist', 'feet')}
    for code, slots in placements.items():
        for label in ('claw', 'serpent', 'amani', 'craft'):
            for pair in PAIRS:
                result[f'{code}_{label}_{pair}'] = {'gear': structure(slots, label, pair), 'options': {},
                    'stage': 'structure', 'placement': list(slots), 'ring': label, 'pair': pair}
    for label in ('claw', 'serpent', 'amani', 'craft'):
        for pair in PAIRS:
            gear = structure(('back', 'wrist'), label, pair)
            gear['waist'] = s.item('waist', 268254)
            result[f'bwr_{label}_{pair}'] = {'gear': sockets(gear), 'options': {},
                'stage': 'structure', 'placement': ['back', 'wrist'], 'ring': label, 'pair': pair,
                'waist_source': '334raid268254,replaces331ordinarycraft'}
    tune = HERE / 'endstate-tuning-bases.json'
    if tune.exists():
        for base in json.loads(tune.read_text(encoding='utf-8')):
            for family in ('mixed', 'haste', 'mastery', 'crit'):
                for flask, item in (('mastery', 'flask_of_the_magisters_2'), ('haste', 'flask_of_the_blood_knights_2'), ('crit', 'flask_of_the_shattered_sun_2')):
                    result[f'tune_{base}_{family}_{flask}'] = {'gear': sockets(result[base]['gear'], family),
                        'options': {'flask': item}, 'stage': 'tune', 'base': base, 'gem_family': family, 'flask': flask}
    extra = HERE / 'endstate-extra-candidates.json'
    if extra.exists():
        for row in json.loads(extra.read_text(encoding='utf-8')):
            source = result[row['base']]
            gear = {**source['gear'], **row.get('changes', {})}
            for slot in row.get('remove_slots', []):
                gear.pop(slot, None)
            result[row['key']] = {**source, 'stage': 'extra', 'gear': gear,
                                  'options': {**source['options'], **row.get('options', {})}, 'source_base': row['base']}
    return result


def validate_gear(gear):
    tiers = sum(int(s.fields(l)['id']) in s.TIERS for l in gear.values())
    lining = sum('12384' in s.fields(l).get('bonus_id', '').split('/') for l in gear.values())
    loa = sum(int(s.fields(l)['id']) == 251513 for l in gear.values())
    ritual = sum('13771' in s.fields(l).get('bonus_id', '').split('/') for l in gear.values())
    vendor_items = [int(s.fields(l)['id']) for l in gear.values() if int(s.fields(l)['id']) in (272148, 272254, 272252, 272248, 272225, 272226, 272227, 272230)]
    vendor = json.loads((HERE / 'reward-source-evidence.json').read_text(encoding='utf-8'))
    types = {r['item_id']: r['inventory_type'] for r in vendor['jindozan']['catalogue']['shaman_caster_items']}
    allowed = {'head': {1}, 'neck': {2}, 'shoulder': {3}, 'chest': {5, 20}, 'waist': {6}, 'legs': {7},
               'feet': {8}, 'wrist': {9}, 'hands': {10}, 'finger1': {11}, 'finger2': {11}, 'back': {16},
               'main_hand': {13, 17, 21}, 'off_hand': {14, 22, 23}, 'trinket1': {12}, 'trinket2': {12}}
    for slot, line in gear.items():
        f = s.fields(line)
        ident = int(f['id'])
        if ident in types and types[ident] not in allowed[slot]:
            raise ValueError(f'Illegal vendor slot {ident}: {slot}')
        if int(f.get('ilevel', 0)) > 334 and slot not in {'neck', 'main_hand', 'trinket1', 'trinket2'}:
            raise ValueError(f'Unattainable level {slot}')
    if int(s.fields(gear['main_hand'])['id']) == 245770 and 'off_hand' in gear:
        raise ValueError('Two-handed staff cannot retain an offhand')
    if tiers < 4 or lining + loa + ritual > 2 or len(vendor_items) > 2:
        raise ValueError((tiers, lining, loa, ritual, vendor_items))
    return {'tier_count': tiers, 'lining_count': lining, 'loa_count': loa, 'ritual_count': ritual, 'vendor_items': vendor_items}


def run(key, config, mode, iterations, seed, unbuffed=False):
    gear = config['gear']
    legality = validate_gear(gear)
    options = {'flask': 'flask_of_the_magisters_2', 'food': 'harandar_celebration', 'potion': 'lights_potential_2',
               'augmentation': 'void_touched', 'temporary_enchant': 'main_hand:thalassian_phoenix_oil_2,if=!talent.flametongue_weapon'}
    options.update(config['options'])
    if unbuffed:
        options = {k: 'disabled' for k in options}
    target, length = MODELS[mode]
    path = HERE / f'endstate70783-{"stats" if unbuffed else mode}-{key}-{iterations}-{seed}.simc'
    content = '\n'.join(['# Attainable future end-state; no acquisition or expenditure implied.',
        '# Ordinary334/craft331/qualifying core341, at mosttwo future vendor items.', 'ptr=0', 'item_db_source=local',
        *s.load()[0], 'talents=' + s.talents(mode), *gear.values(), *[f'{k}={v}' for k, v in options.items()],
        'optimal_raid=0', 'override.bloodlust=0', 'fight_style=Patchwerk', f'desired_targets={target}',
        f'max_time={30 if unbuffed else length}', 'vary_combat_length=0', 'fixed_time=1', 'threads=8',
        f'iterations={iterations}', f'seed={seed}', 'confidence=0.95']) + '\n'
    if path.exists() and path.read_text(encoding='utf-8') != content:
        raise ValueError(f'Preserve existing different input: {path.name}')
    path.write_text(content, encoding='utf-8')
    check = path.with_suffix('.validation.json')
    if check.exists() and path.with_suffix('.json').exists() and json.loads(check.read_text(encoding='utf-8')).get('accepted'):
        return
    with path.with_suffix('.run.log').open('w', encoding='utf-8') as log:
        r = subprocess.run([str(s.ENGINE), str(path), f'json2={path.with_suffix(".json")}',
                            f'output={path.with_suffix(".txt")}'], stdout=log, stderr=subprocess.STDOUT)
    d = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    a = d['sim']['players'][0]
    severe = bool(d.get('errors') or d['sim'].get('errors')) or any('severe' in x.get('level', '').lower() for x in d.get('logs', []))
    dp = a['collected_data']['dps']
    result = {'key': key, 'model': 'stats' if unbuffed else mode, 'accepted': r.returncode == 0 and a.get('valid_fight_style') is True and not severe,
        'iterations': iterations, 'seed': seed, 'samples': dp['count'], 'dps': dp['mean'],
        'ci95_half_width': dp['mean_std_dev'] * d['sim']['options']['confidence_estimator'],
        'gear': a['gear'], 'stats': a['collected_data']['buffed_stats'], 'options': options,
        'config': {k: v for k, v in config.items() if k not in ('gear', 'options')}, **legality,
        'valid_fight_style': a.get('valid_fight_style'), 'logs': d.get('logs', [])}
    check.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('key', 'model', 'accepted', 'dps', 'ci95_half_width')}, ensure_ascii=False), flush=True)
    if not result['accepted']:
        raise ValueError(path.name)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--key', action='append', default=[])
    p.add_argument('--stage', choices=['reference', 'structure', 'tune', 'extra'])
    p.add_argument('--model', action='append', choices=MODELS, default=[])
    p.add_argument('--iterations', type=int, default=1200)
    p.add_argument('--seed', type=int, default=26111371)
    p.add_argument('--unbuffed', action='store_true')
    args = p.parse_args()
    configs = candidates()
    selected = args.key or [k for k, c in configs.items() if c['stage'] == (args.stage or 'reference')]
    manifest = {'recorded_at': datetime.now().astimezone().isoformat(), 'scope': 'Future attainableBiS,not weekly affordability;ordinary334/crafted331/qualifying341;two vendor items at most in the full quest chain,onlyone currently reported.',
        'raw_sha256': hashlib.sha256(s.RAW.read_bytes()).hexdigest(), 'engine_sha256': hashlib.sha256(s.ENGINE.read_bytes()).hexdigest(),
        'source_commit': subprocess.check_output(['git', '-C', str(s.SOURCE), 'rev-parse', 'HEAD'], text=True).strip(),
        'models': MODELS, 'screen_seed': 26111371, 'sockets': 'Head1,neck2,rings1each,wrist1,waist1;one diamond maximum;no extra head/neck/ring sockets.',
        'limitations': 'Fixed-target supported Patchwerk only. Gloves/Swarmcaller damage splitting and rune targets unverified. Future source and socket eligibility qualified separately.'}
    (HERE / 'endstate-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (HERE / 'endstate-candidates.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for mode in args.model or ['long']:
        for key in selected:
            run(key, configs[key], mode, args.iterations, args.seed, args.unbuffed)


if __name__ == '__main__':
    main()
