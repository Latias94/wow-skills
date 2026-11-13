"""Bounded 70783 comparisons for Shaseng's supplied November 10 loadout."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT / 'records/cn-barrens-shaseng/snapshots/2026-11-10-2203.simc'
ENGINE = ROOT / '.local/simc-build-70783/Release/simc.exe'
SOURCE = ROOT / '.local/simc-source-70783'
SLOTS = 'head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand'.split()
MODELS = {'slice': ('DungeonSlice', 360, 1), 'st': ('Patchwerk', 240, 1), 'aoe': ('Patchwerk', 90, 5)}
MISSIVES = {'ch': '8790', 'cm': '8791', 'hm': '8793'}


def fields(line):
    return dict(part.split('=', 1) for part in line.split('=', 1)[1].split(',') if '=' in part)


def update(line, **changes):
    values = fields(line)
    for key, value in changes.items():
        if value is None:
            values.pop(key, None)
        else:
            values[key] = str(value)
    return line.split('=', 1)[0] + '=,' + ','.join(f'{key}={value}' for key, value in values.items())


def load():
    lines = [line for line in RAW.read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')]
    gear = {line.split('=', 1)[0]: line for line in lines if line.split('=', 1)[0] in SLOTS}
    actor = [line for line in lines if line.split('=', 1)[0] not in SLOTS + ['shirt', 'tabard']]
    return actor, gear


def crafted(line, kind):
    bonuses = [MISSIVES[kind] if value in {'8790', '8791', '8792', '8793', '8794', '8795'} else value
               for value in fields(line)['bonus_id'].split('/')]
    return update(line, bonus_id='/'.join(bonuses), crafted_stats=None)


def candidates():
    _, base = load()
    def ordinary(slot, ident, *, socket=False):
        line = f'{slot}=,id={ident},bonus_id=13334/12854' + ('/13668' if socket else '') + ',ilevel=334'
        for key in ('enchant_id', 'gem_id'):
            if key in fields(base[slot]) and (key != 'gem_id' or socket):
                line = update(line, **{key: fields(base[slot])[key]})
        return line
    leg = ordinary('legs', 268225)
    tier_leg = update(base['legs'], redirected_base_stats=268225, ilevel=334,
                      bonus_id='13334/12854/13693/13698')
    waist = ordinary('waist', 268256)
    shoe_bonuses = fields(base['feet'])['bonus_id'].split('/')
    for bonus in ('8960', '12384'):
        if bonus not in shoe_bonuses:
            shoe_bonuses.append(bonus)
    cloak = {'back': ordinary('back', 268253),
             'feet': update(base['feet'], bonus_id='/'.join(shoe_bonuses))}
    gloves = next(line[2:] for line in RAW.read_text(encoding='utf-8').splitlines()
                  if line.startswith('# hands=,id=244575,'))
    core = {'legs': leg, 'waist': waist, **cloak}
    core_hm_gloves = {**core, 'legs': tier_leg, 'hands': gloves}
    result = {
        'current': ({}, {}),
        'legs_h7': ({'legs': leg}, {}),
        'legs_delve': ({'legs': ordinary('legs', 272243)}, {}),
        'legs_murder': ({'legs': ordinary('legs', 251130)}, {}),
        'waist_h7': ({'waist': waist}, {}),
        'cloak_h7_move_lining': (cloak, {}),
        'shoulder_raid_cm': ({'shoulder': update(base['shoulder'], redirected_base_stats=268246)}, {}),
        'bag_gloves_hm': ({'hands': gloves}, {}),
        'legs_waist': ({'legs': leg, 'waist': waist}, {}),
        'core_h7': (core, {}),
        'core_h7_bag_gloves': (core_hm_gloves, {}),
        'owned_zuljin': ({'trinket2': 'trinket2=,id=270173,bonus_id=6652/13334/12856'}, {}),
        'flask_haste': ({}, {'flask': 'flask_of_the_blood_knights_2'}),
        'flask_crit': ({}, {'flask': 'flask_of_the_shattered_sun_2'}),
    }
    for ident in (268249, 268252, 272148, 272149, 272150, 158366, 252258, 273792):
        ring = ordinary('finger2', ident, socket=True)
        result[f'ring_{ident}'] = ({'finger2': ring}, {})
        result[f'core_ring_{ident}'] = ({**core_hm_gloves, 'finger2': ring}, {})
    result['ring_hex_no_socket'] = ({'finger2': ordinary('finger2', 272149)}, {})
    result['ring_h5_no_socket'] = ({'finger2': ordinary('finger2', 268252)}, {})
    h5_owned = next(line[2:] for line in RAW.read_text(encoding='utf-8').splitlines()
                    if line.startswith('# finger1=,id=268252,')).replace('finger1=', 'finger2=', 1)
    result['owned_h5_raw'] = ({'finger2': h5_owned}, {})
    result['owned_h5_prepared'] = ({'finger2': update(h5_owned, enchant_id=7967, gem_id=240908)}, {})
    for level, bonus in ((318, '12849'), (321, '12850')):
        ring = update(ordinary('finger2', 268252, socket=True), ilevel=level,
                      bonus_id=f'13334/{bonus}/13668')
        result[f'ring_h5_{level}'] = ({'finger2': ring}, {})
    for key, changes in (('current', {}), ('core', core_hm_gloves)):
        gear = {**base, **changes}
        for family, gem in (('mastery_crit', 240898), ('mastery_haste', 240900)):
            gems = {'neck': update(gear['neck'], gem_id=f'240983/{gem}'),
                    'finger1': update(gear['finger1'], gem_id=gem),
                    'finger2': update(gear['finger2'], gem_id=gem)}
            result[f'{key}_gems_{family}'] = ({**changes, **gems}, {})
        sockets = {}
        for slot in ('head', 'wrist', 'waist'):
            bonuses = fields(gear[slot])['bonus_id'].split('/')
            if '13695' not in bonuses:
                bonuses.append('13695')
            sockets[slot] = update(gear[slot], bonus_id='/'.join(bonuses), gem_id=240900)
        result[f'{key}_three_sockets'] = ({**changes, **sockets}, {})
    for slot in ('back', 'wrist', 'waist', 'feet', 'finger2'):
        for kind in ('cm', 'hm'):
            result[f'craft_{slot}_{kind}'] = ({slot: crafted(base[slot], kind)}, {})
    for ident in (268249, 268252, 272150):
        result[f'core_keep_ring_{ident}'] = ({**core, 'finger2': ordinary('finger2', ident, socket=True)}, {})
    tuned_owned = {'hands': gloves, **{slot: crafted(base[slot], 'hm') for slot in ('back', 'wrist', 'feet')}}
    for family, gem in (('mc', 240898), ('mh', 240900)):
        gems = {'neck': update(base['neck'], gem_id=f'240983/{gem}'),
                'finger1': update(base['finger1'], gem_id=gem),
                'finger2': update(base['finger2'], gem_id=gem)}
        result[f'owned_tuned_{family}'] = ({**tuned_owned, **gems}, {})
        target = {**core, 'finger2': ordinary('finger2', 268249, socket=True)}
        target.update(neck=update(base['neck'], gem_id=f'240983/{gem}'),
                      finger1=update(base['finger1'], gem_id=gem),
                      finger2=update(target['finger2'], gem_id=gem))
        result[f'target_{family}'] = (target, {})
        full = dict(target)
        for slot in ('head', 'wrist', 'waist'):
            line = target.get(slot, base[slot])
            bonuses = fields(line)['bonus_id'].split('/') + ['13695']
            full[slot] = update(line, bonus_id='/'.join(bonuses), gem_id=gem)
        result[f'target_{family}_sockets'] = (full, {})
        result[f'target_{family}_keep_crafted_ring'] = ({**full, 'finger2': update(base['finger2'], gem_id=gem)}, {})
        result[f'target_{family}_h5_ring'] = ({**full, 'finger2': update(ordinary('finger2', 268252, socket=True), gem_id=gem)}, {})
    result['target_mc_hm_crafts'] = ({**result['target_mc_sockets'][0],
                                      **{slot: crafted(result['target_mc_sockets'][0].get(slot, base[slot]), 'hm') for slot in ('wrist', 'feet')}}, {})
    return result


def run(key, mode, iterations, seed, unbuffed):
    actor, gear = load()
    changes, options = candidates()[key]
    gear.update(changes)
    settings = {'flask': 'flask_of_the_magisters_2', 'food': 'harandar_celebration',
                'augmentation': 'void_touched', 'potion': 'potion_of_recklessness_2',
                'temporary_enchant': 'main_hand:thalassian_phoenix_oil_2'}
    settings.update(options)
    if unbuffed:
        settings = {key: 'disabled' for key in settings}
    style, length, targets = MODELS[mode]
    stem = f'live70783-{"stats" if unbuffed else mode}-{key}-{iterations}-{seed}'
    path = HERE / f'{stem}.simc'
    lines = ['# November 10 supplied talents, Omnium and retained Catalyst sources.',
             '# Candidate replacements are hypothetical, not acquisitions.',
             'ptr=0', 'item_db_source=local', *actor, *gear.values(),
             *[f'{key}={value}' for key, value in settings.items()],
             'optimal_raid=0', 'override.bloodlust=0', f'fight_style={style}',
             f'max_time={30 if unbuffed else length}', f'desired_targets={targets}',
             'vary_combat_length=0', 'fixed_time=1', 'threads=8',
             f'iterations={iterations}', f'seed={seed}', 'confidence=0.95']
    content = '\n'.join(lines) + '\n'
    if path.exists() and path.read_text(encoding='utf-8') != content:
        raise RuntimeError(f'Preserving different existing input: {path.name}')
    path.write_text(content, encoding='utf-8')
    summary_path = path.with_suffix('.validation.json')
    if summary_path.exists():
        previous = json.loads(summary_path.read_text(encoding='utf-8'))
        if previous.get('accepted'):
            print(json.dumps(previous, ensure_ascii=False), flush=True)
            return
    with path.with_suffix('.run.log').open('w', encoding='utf-8') as log:
        process = subprocess.run([str(ENGINE), str(path), f'json2={path.with_suffix(".json")}',
                                  f'output={path.with_suffix(".txt")}'], stdout=log, stderr=subprocess.STDOUT)
    if not path.with_suffix('.json').exists():
        raise RuntimeError(path.with_suffix('.run.log').read_text(encoding='utf-8'))
    data = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    player = data['sim']['players'][0]
    dps = player['collected_data']['dps']
    equipped = list(player['gear'].values())
    tier_count = sum(re.search(r',id=(271519|271517|271522|271520|271518)(?:,|$)', item['encoded_item']) is not None for item in equipped)
    lining_count = sum('12384' in re.search(r'bonus_id=([^,]+)', item['encoded_item']).group(1).split('/') for item in equipped if 'bonus_id=' in item['encoded_item'])
    severe = any('severe' in message.get('level', '').lower() for message in data.get('logs', []))
    result = {'candidate': key, 'model': 'stats' if unbuffed else mode, 'iterations_requested': iterations,
              'seed': seed, 'accepted': process.returncode == 0 and player.get('valid_fight_style') is True and not severe and tier_count >= 4 and lining_count == 2,
              'exit_code': process.returncode, 'valid_fight_style': player.get('valid_fight_style'),
              'tier_count': tier_count, 'lining_count': lining_count,
              'dps': dps['mean'], 'samples': dps['count'],
              'ci95': dps.get('mean_std_dev', 0) * data['sim']['options']['confidence_estimator'],
              'stats': player['collected_data']['buffed_stats'], 'logs': data.get('logs', [])}
    summary_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('candidate', 'model', 'accepted', 'dps', 'ci95', 'samples', 'tier_count', 'lining_count')}, ensure_ascii=False), flush=True)
    if not result['accepted']:
        raise RuntimeError(f'Rejected comparison: {stem}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', action='append', default=[])
    parser.add_argument('--model', action='append', choices=MODELS, default=[])
    parser.add_argument('--iterations', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=26111011)
    parser.add_argument('--unbuffed', action='store_true')
    args = parser.parse_args()
    manifest = {'recorded_at': datetime.now().astimezone().isoformat(),
                'source_commit': subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip(),
                'engine_sha256': hashlib.sha256(ENGINE.read_bytes()).hexdigest(),
                'raw_sha256': hashlib.sha256(RAW.read_bytes()).hexdigest(),
                'live_build': '12.1.5.70783', 'boundaries': 'Ordinary Myth334/Crafted331; no inaccessible 9/6 gear; supplied talents/Omnium held constant',
                'ring_assumption': 'Replacement rings modeled with one socket; an explicit no-socket Hex Ring control is included.',
                'models': MODELS, 'candidates': list(candidates())}
    (HERE / 'simc-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for model in args.model or ['slice']:
        for candidate in args.candidate or ['current']:
            run(candidate, model, args.iterations, args.seed, args.unbuffed)


if __name__ == '__main__':
    main()
