"""Export a bounded, inspectable damage reference from the personal SimC report."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, default=Path(__file__).resolve().parents[3] / 'records/cn-barrens-shaseng/analysis/2026-10-26/gear-compat341-raid-current.json')
args = parser.parse_args()
raw = args.report.read_bytes()
report = json.loads(raw)
player = report['sim']['players'][0]


def flatten(items):
    for item in items:
        yield item
        yield from flatten(item.get('children', []))


stats = {item['name']: item for item in flatten(player['stats'])}
names = {
    'palm': 'tiger_palm', 'blackout': 'blackout_kick',
    'sun': 'rising_sun_kick_damage', 'dawn': 'glory_of_the_dawn_rising_sun_kick_damage',
    'wind': 'rushing_wind_kick_damage', 'fists': 'fists_of_fury',
    'fistsTier': 'fists_of_fury_damage_mid2_2pc', 'crane': 'spinning_crane_kick_tick',
    'dragonAoe': 'whirling_dragon_punch_aoe', 'dragonSingle': 'whirling_dragon_punch_singletarget',
    'conduit': 'celestial_conduit',
    'stomp': 'zenith_stomp_cast', 'stompAuto': 'zenith_stomp_trigger',
}
damage = {}
for key, name in names.items():
    item = stats[name]
    result = next(item[k]['hit']['actual_amount'] for k in ['direct_results', 'tick_results'] if 'hit' in item.get(k, {}))
    damage[key] = {'reference': result['min'], 'observedMean': result['mean'], 'statName': name}

data = {
    'character': player['name'], 'talents': player['talents'],
    'simcRevision': report.get('git_revision'), 'report': args.report.name,
    'sha256': hashlib.sha256(raw).hexdigest(),
    'stats': player['collected_data']['buffed_stats']['stats'],
    'energyRegen': player['base_energy_regen_per_second'], 'damage': damage,
    'method': 'Observed minimum non-critical hit per named SimC statistic. Not an isolated coefficient fit; residual buffs can remain. Core-damage training estimate only, not full character DPS.',
}
out = Path(__file__).resolve().parents[1] / 'dist/calibration.js'
out.write_text('export const CALIBRATION = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'Exported {len(damage)} observed references to {out}')
