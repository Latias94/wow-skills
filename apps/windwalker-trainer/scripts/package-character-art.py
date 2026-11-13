"""Package visually reviewed single-pose Forge outputs for the trainer."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


APP = Path(__file__).resolve().parents[1]
ROOT = APP.parents[1]
SOURCE = ROOT / '.local/windwalker-art-v6'
DESTINATION = APP / 'dist/assets/sprites/v6'
POSES = ('idle', 'palm', 'blackout', 'sun', 'fists', 'crane', 'dragon', 'tiger', 'conduit', 'stomp')
ALIASES = {'wind': 'blackout', 'zenith': 'tiger'}


def main():
    entries = []
    preview = Image.new('RGB', (1200, 600), '#233b36')
    labels = ImageDraw.Draw(preview)
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for index, action in enumerate(POSES):
        folder = SOURCE / 'processed-v6' / action
        metadata = json.loads((folder / 'pipeline-meta.json').read_text(encoding='utf-8'))
        checks = metadata['qa']['checks']
        if any(check['status'] == 'fail' for check in checks):
            raise ValueError(f'{action}: failed Forge checks')
        image = Image.open(folder / 'clean.png').convert('RGBA')
        if image.size != (384, 384) or not image.getchannel('A').getbbox():
            raise ValueError(f'{action}: expected a nonempty 384px transparent pose')
        destination = DESTINATION / f'{action}.webp'
        image.save(destination, 'WEBP', quality=91, method=6)
        entries.append({
            'action': action,
            'src': destination.relative_to(APP / 'dist').as_posix(),
            'cols': 1, 'rows': 1, 'frames': 1, 'cellSize': 384,
            'duration': 1.6 if action == 'idle' else .9 if action == 'dragon' else .72,
            'anchor': [192, 365],
            'alphaBboxes': [list(image.getchannel('A').getbbox())],
            'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'sourceSha256': metadata['provenance']['input_sha256'],
            'forgeQa': metadata['qa']['status'],
            'warnings': [check for check in checks if check['status'] == 'warn'],
        })
        thumb = image.copy()
        thumb.thumbnail((230, 265), Image.Resampling.LANCZOS)
        x, y = index % 5 * 240, index // 5 * 300
        preview.paste(thumb, (x + (240 - thumb.width) // 2, y), thumb)
        labels.text((x + 12, y + 272), action, fill='#f1ddb0')
    for action, source in ALIASES.items():
        original = next(item for item in entries if item['action'] == source)
        entries.append({**original, 'action': action, 'sharedPose': source})
    manifest = {
        'version': 6,
        'style': 'Friendly round red-and-gold panda monk based on the user-supplied screenshot',
        'source': 'Host image generation reference edits; Agent Sprite Forge single-pose alpha and registration processing',
        'notice': 'Generated practice artwork; not extracted game models or full character animation',
        'motion': 'Single key pose per action with independently animated spell effects',
        'actions': entries,
        'limits': ['Wind shares the Blackout body pose; Zenith shares the invocation body pose.', 'Character bodies are held key poses, not video-derived animation.'],
    }
    (DESTINATION / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    preview.save(SOURCE / 'character-lineup.jpg', quality=95)
    print(json.dumps({'poses': len(POSES), 'actions': len(entries), 'preview': str(SOURCE / 'character-lineup.jpg')}))


if __name__ == '__main__':
    main()
