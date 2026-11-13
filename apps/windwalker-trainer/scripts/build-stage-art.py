"""Package reviewed Forge scene, character and effect manifests."""

import hashlib
import json
from pathlib import Path

from PIL import Image


APP = Path(__file__).resolve().parents[1]
SOURCE = APP.parents[1] / '.local' / 'windwalker-art-v5'
DIST = APP / 'dist'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def webp(source, destination, *, max_size=None):
    image = Image.open(source).convert('RGBA')
    if max_size:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, 'WEBP', quality=90, method=6)
    return {
        'src': destination.relative_to(DIST).as_posix(),
        'size': list(image.size),
        'bytes': destination.stat().st_size,
        'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    }


def main():
    original = read_json(DIST / 'assets/sprites/manifest.json')
    character_manifest = DIST / 'assets/sprites/v6/manifest.json'
    if character_manifest.exists():
        original = read_json(character_manifest)
    channel_actions = {'fists', 'crane', 'conduit'}
    character = {
        item['action']: {
            'src': item.get('src', f"assets/sprites/{item['action']}.webp"),
            'cols': item['cols'], 'rows': item['rows'],
            'frames': item['frames'],
            'duration': item.get('duration', 1.6 if item['action'] == 'idle' else .72),
            'loop': item['action'] == 'idle' or item['action'] in channel_actions,
        }
        for item in original['actions']
    }
    effects, provenance = {}, []
    for action, duration, loop in [
        ('sun', .56, False), ('fists', .6, True),
        ('crane', .6, True), ('conduit', .8, True),
        ('tiger', .9, True), ('blackout', .56, False),
        ('wind', .6, False),
    ]:
        folder = SOURCE / ('fx' if action in ('sun', 'fists') else 'fx-v5') / action
        metadata = read_json(folder / 'pipeline-meta.json')
        failures = [check for check in metadata['qa']['checks'] if check['status'] == 'fail']
        if failures:
            raise ValueError(f'{action} has failed Forge checks: {failures}')
        frames = sorted(folder.glob('fx-*.png'), key=lambda path: int(path.stem.split('-')[-1]))
        expected = 6 if action == 'fists' else 4
        if len(frames) != expected:
            raise ValueError(f'{action}: expected {expected} frames, found {len(frames)}')
        record = webp(folder / 'sheet-transparent.png', DIST / f'assets/fx/v5/{action}.webp')
        record.update(action=action, forgeQa=metadata['qa']['status'])
        provenance.append(record)
        cols = 3 if action == 'fists' else 2
        effects[action] = {
            'src': record['src'], 'cols': cols, 'rows': 2,
            'frames': len(frames), 'duration': duration, 'loop': loop,
            'posterFrame': 2,
        }
    # Reuse a reviewed energy family where a dedicated source was rejected.
    for action, source, duration, loop in [
        ('palm', 'fists', .3, False),
        ('dragon', 'conduit', .75, False),
        ('stomp', 'crane', .5, False),
        ('zenith', 'conduit', .8, True),
        ('jade', 'conduit', .8, True),
        ('greaterJade', 'conduit', .8, True),
    ]:
        effects[action] = {**effects[source], 'duration': duration, 'loop': loop}
    scene = {}
    for name in ('dojo', 'dummy'):
        record = webp(SOURCE / f'scene-sources/{name}.png', DIST / f'assets/scenes/v5/{name}.webp', max_size=(1280, 1600))
        provenance.append({**record, 'action': name})
        scene['background' if name == 'dojo' else name] = record['src']
    version = 6 if character_manifest.exists() else 5
    data = {'version': version, 'character': character, 'effects': effects, 'scene': scene}
    (DIST / 'sprite-data.js').write_text(
        '// Generated from reviewed character and Forge effect manifests.\n'
        + 'export const SPRITE_ART = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n',
        encoding='utf-8',
    )
    report = {
        'version': version,
        'source': 'Historical host image generation; Agent Sprite Forge geometry/alpha processing',
        'characterStatus': original.get('style', 'Existing light-robed character; replacement pending'),
        'assets': provenance,
        'limits': [
            'The dedicated dragon source failed cross-cell spill QC and is not shipped.',
            'Dragon, Jade and Zenith share the reviewed conduit energy sheet.',
            'Palm shares the golden fist sheet; Stomp shares the jade ground ring.',
            'No new character video generation succeeded after the two historical pilot clips.',
        ],
    }
    (DIST / 'assets/fx/v5/manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'assets': len(provenance), 'fxFamilies': 7, 'version': version}, ensure_ascii=False))


if __name__ == '__main__':
    main()
