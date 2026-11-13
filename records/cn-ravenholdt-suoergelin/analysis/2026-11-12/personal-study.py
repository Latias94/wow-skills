"""Bounded native70783 comparisons for the complete18:29 Arms import."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT / 'records/cn-ravenholdt-suoergelin/snapshots/2026-11-12-1829.simc'
ENGINE = ROOT / '.local/simc-build-70783/Release/simc.exe'
SOURCE = ROOT / '.local/simc-source-70783'
SLOTS = 'head neck shoulder back chest wrist hands waist legs feet finger1 finger2 trinket1 trinket2 main_hand'.split()
MODELS = {'slice': ('DungeonSlice', 360, 1), 'st': ('Patchwerk', 240, 1), 'aoe': ('Patchwerk', 90, 5)}
TIER_IDS = {271456, 271454, 271459, 271457, 271455}


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
    lines = [l for l in RAW.read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    gear = {l.split('=', 1)[0]: l for l in lines if l.split('=', 1)[0] in SLOTS}
    return [l for l in lines if l.split('=', 1)[0] not in SLOTS], gear


def bag(ident, slot):
    line = next(l[2:] for l in RAW.read_text(encoding='utf-8').splitlines()
                if l.startswith('# ') and ',id=' + str(ident) + ',' in l)
    return slot + line[line.index('='):]


def bonuses(line, add=(), replace=None):
    values = fields(line)['bonus_id'].split('/')
    values = [(replace or {}).get(x, x) for x in values]
    for value in add:
        if str(value) not in values:
            values.append(str(value))
    return update(line, bonus_id='/'.join(values))


def candidates():
    _, base = load()
    ring_filled = update(base['finger1'], gem_id=240890, enchant_id=7967)
    swarm334 = bonuses(base['finger1'], replace={'12849': '12854'})
    ready = {'finger1': update(swarm334, gem_id=240890, enchant_id=7967),
             'waist': update(bonuses(base['waist'], add=(13695,)), gem_id=240890),
             'feet': update(base['feet'], enchant_id=7963)}
    chest = update(base['chest'], bonus_id='13334/12854/13690/13698', ilevel=334, redirected_base_stats=268222)
    legs = f'legs=,id=271878,enchant_id=8163,bonus_id=13334/12854/13847,ilevel=334'
    ring_h5 = 'finger2=,id=268252,enchant_id=7967,gem_id=240890,bonus_id=13334/12854/13668,ilevel=334'
    ring_craft = 'finger2=,id=240949,enchant_id=7967,gem_id=240890,bonus_id=12214/13667/12497/13751/14001/8790/13836,content_tuning=3615,crafting_quality=5'
    craft_leg = 'legs=,id=237833,enchant_id=8163,bonus_id=12214/13667/12497/13751/14001/8790/13836,content_tuning=3615,crafting_quality=5'
    result = {
        'current': ({}, {}),
        'ring_fill': ({'finger1': ring_filled}, {}),
        'swarm334': ({'finger1': swarm334}, {}),
        'one_socket': ({'waist': ready['waist']}, {}),
        'ready': (ready, {}),
        'ready_h7': ({**ready, 'chest': chest}, {}),
        'ready_h8': ({**ready, 'legs': legs}, {}),
        'h7_chest': ({'chest': chest}, {}),
        'h8_legs': ({'legs': legs}, {}),
        'crafted_legs331': ({'legs': craft_leg}, {}),
        'bag_tier_legs': ({'legs': bag(271455, 'legs')}, {}),
        'bag_atroxus_ring2': ({'finger2': bag(252258, 'finger2')}, {}),
        'bag_atroxus_ring1': ({'finger1': bag(252258, 'finger1')}, {}),
        'bag_stolen_ring2': ({'finger2': bag(251148, 'finger2')}, {}),
        'ring_h5': ({'finger2': ring_h5}, {}),
        'ring_crafted331': ({'finger2': ring_craft}, {}),
        'ring_amani334': ({'finger2': update(base['finger2'], bonus_id='13334/12854/13668', ilevel=334, content_tuning=None)}, {}),
        'shoulder_ch': ({'shoulder': update(base['shoulder'], redirected_base_stats=239037)}, {}),
        'weapon_h10_341': ({'main_hand': 'main_hand=,id=280799,enchant_id=8689,bonus_id=13334/12856'}, {}),
        'flask_crit': ({}, {'flask': 'flask_of_the_shattered_sun_2'}),
        'flask_mastery': ({}, {'flask': 'flask_of_the_magisters_2'}),
        'core': ({**ready, 'chest': chest, 'legs': legs}, {}),
        'core_crafted_ring': ({**ready, 'chest': chest, 'legs': legs, 'finger2': ring_craft}, {}),
        'core_h5_ring': ({**ready, 'chest': chest, 'legs': legs, 'finger2': ring_h5}, {}),
        'core_keep_amani334': ({**ready, 'chest': chest, 'legs': legs, 'finger2': update(base['finger2'], bonus_id='13334/12854/13668', ilevel=334, content_tuning=None)}, {}),
        'core_owned_atroxus': ({**ready, 'chest': chest, 'legs': legs, 'finger2': bag(252258, 'finger2')}, {}),
        'core_owned_stolen': ({**ready, 'chest': chest, 'legs': legs, 'finger2': bag(251148, 'finger2')}, {}),
    }
    for level in (334, 341):
        for slot, label in (('trinket1', 'tendril'), ('trinket2', 'zuljin')):
            line = bag(270175, slot)
            if level == 341:
                line = bonuses(line, replace={'12854': '12856'})
            result[f'heart{level}_replace_{label}'] = ({slot: line}, {})
    for slot, label in (('trinket1', 'tendril'), ('trinket2', 'zuljin')):
        result[f'keeper341_replace_{label}'] = ({slot: f'{slot}=,id=270165,bonus_id=13334/12856'}, {})
    for family, gem in (('haste', 240890), ('crit', 240906)):
        target = {**ready, 'chest': chest, 'legs': legs, 'finger2': ring_craft}
        for slot in ('head', 'neck', 'finger1', 'finger2', 'waist'):
            line = target.get(slot, base[slot])
            target[slot] = update(line, gem_id=f'240983/{gem}' if slot == 'neck' else gem)
        result[f'target_{family}'] = (target, {})
        result[f'target_{family}_h5'] = ({**target, 'finger2': update(ring_h5, gem_id=gem)}, {})
        result[f'target_{family}_shoulder'] = ({**target, 'shoulder': update(base['shoulder'], redirected_base_stats=239037)}, {})
    result['target_haste_keep_owned_amani'] = ({**result['target_haste'][0], 'finger2': update(base['finger2'], gem_id=240890)}, {})
    result['target_crit_craft_cm'] = ({**result['target_crit'][0], 'finger2': bonuses(result['target_crit'][0]['finger2'], replace={'8790':'8791'})}, {})
    return result


def run(key, mode, iterations, seed, unbuffed):
    actor, gear = load()
    changes, options = candidates()[key]
    gear.update(changes)
    settings = {'flask': 'flask_of_the_blood_knights_2', 'food': 'harandar_celebration',
                'augmentation': 'void_touched', 'potion': 'potion_of_recklessness_2',
                'temporary_enchant': 'main_hand:thalassian_phoenix_oil_2'}
    settings.update(options)
    if unbuffed:
        settings = {k: 'disabled' for k in settings}
    style, length, targets = MODELS[mode]
    stem = f'full70783-{"stats" if unbuffed else mode}-{key}-{iterations}-{seed}'
    path = HERE / f'{stem}.simc'
    content = '\n'.join(['# Full user18:29 export;current talents,Omnium and retained sources.',
                         '# Replacement items are hypothetical except explicitly identified bag items.',
                         'ptr=0', 'item_db_source=local', *actor, *gear.values(),
                         *[f'{k}={v}' for k, v in settings.items()],
                         'optimal_raid=0', 'override.bloodlust=0', f'fight_style={style}',
                         f'max_time={30 if unbuffed else length}', f'desired_targets={targets}',
                         'vary_combat_length=0', 'fixed_time=1', 'threads=8', f'iterations={iterations}',
                         f'seed={seed}', 'confidence=0.95']) + '\n'
    if path.exists() and path.read_text(encoding='utf-8') != content:
        raise RuntimeError(f'Preserving a different existing input:{path.name}')
    path.write_text(content, encoding='utf-8')
    validation = path.with_suffix('.validation.json')
    if validation.exists() and json.loads(validation.read_text(encoding='utf-8')).get('accepted'):
        return
    with path.with_suffix('.run.log').open('w', encoding='utf-8') as log:
        process = subprocess.run([str(ENGINE), str(path), f'json2={path.with_suffix(".json")}',
                                  f'output={path.with_suffix(".txt")}'], stdout=log, stderr=subprocess.STDOUT)
    data = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    player = data['sim']['players'][0]
    tiers = sum(int(fields(gearline)['id']) in TIER_IDS for gearline in gear.values())
    linings = sum('12384' in fields(line).get('bonus_id', '').split('/') for line in gear.values())
    severe = any('severe' in x.get('level', '').lower() for x in data.get('logs', []))
    dps = player['collected_data']['dps']
    result = {'candidate': key, 'model': 'stats' if unbuffed else mode, 'iterations': iterations, 'seed': seed,
              'accepted': process.returncode == 0 and player.get('valid_fight_style') is True and not severe and tiers >= 4 and linings == 2,
              'exit_code': process.returncode, 'valid_fight_style': player.get('valid_fight_style'), 'tier_count': tiers, 'lining_count': linings,
              'dps': dps['mean'], 'samples': dps['count'], 'ci95': dps['mean_std_dev'] * data['sim']['options']['confidence_estimator'],
              'stats': player['collected_data']['buffed_stats'], 'gear': player['gear'], 'logs': data.get('logs', [])}
    validation.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('candidate', 'model', 'accepted', 'dps', 'ci95', 'samples')}, ensure_ascii=False), flush=True)
    if not result['accepted']:
        raise RuntimeError(f'Rejected:{stem}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', action='append', default=[])
    parser.add_argument('--model', action='append', choices=MODELS, default=[])
    parser.add_argument('--iterations', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=26111231)
    parser.add_argument('--unbuffed', action='store_true')
    args = parser.parse_args()
    manifest = {'recorded_at': datetime.now().astimezone().isoformat(),
                'source_commit': subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip(),
                'engine_sha256': hashlib.sha256(ENGINE.read_bytes()).hexdigest(), 'raw_sha256': hashlib.sha256(RAW.read_bytes()).hexdigest(),
                'live_build':'12.1.5.70783','models':MODELS,'candidates':list(candidates()),
                'boundaries':'OrdinaryMyth334/Crafted331/ascended341;one owned socket token;supplied talents andOmnium fixed;no M7/M8 9/6.',
                'ring_assumption':'New dropped rings one socket;crafted ring retains native socket. Existing empty Swarmcaller preparation measured separately.',
                'resources':'10 current-season sparks,10 ascendant venomstones,1 roll core;gold and crest purchase availability remain separate.'}
    (HERE/'full-simc-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for mode in args.model or ['slice']:
        for candidate in args.candidate or ['current']:
            run(candidate,mode,args.iterations,args.seed,args.unbuffed)


if __name__ == '__main__':
    main()
