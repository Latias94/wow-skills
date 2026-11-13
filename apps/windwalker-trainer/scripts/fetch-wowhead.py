"""Snapshot official spell names, icon identities and plain-text tooltips from Wowhead."""
import datetime
import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

SPELLS = {
    'palm': 100780, 'blackout': 100784, 'sun': 107428, 'fists': 113656,
    'crane': 101546, 'dragon': 152175, 'tiger': 123904, 'zenith': 1249625,
    'conduit': 443028, 'stomp': 1272696, 'wind': 467307,
}
root = Path(__file__).resolve().parents[1] / 'dist'
assets = root / 'assets/icons'
assets.mkdir(parents=True, exist_ok=True)


class PlainTooltip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {'br', 'tr', 'div', 'table'}:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in {'td', 'th'}:
            self.parts.append(' ')

    def handle_data(self, data):
        self.parts.append(data)


data = {}
for key, spell_id in SPELLS.items():
    endpoint = f'https://nether.wowhead.com/tooltip/spell/{spell_id}?dataEnv=1&locale=4'
    with urllib.request.urlopen(endpoint, timeout=25) as response:
        spell = json.load(response)
    icon = spell['icon']
    if not re.fullmatch(r'[a-zA-Z0-9_]+', icon):
        raise ValueError('Unexpected icon identity')
    icon_url = f'https://wow.zamimg.com/images/wow/icons/large/{icon}.jpg'
    with urllib.request.urlopen(icon_url, timeout=25) as response:
        image = response.read()
    if not image.startswith(b'\xff\xd8'):
        raise ValueError('Expected JPEG icon')
    (assets / f'{key}.jpg').write_bytes(image)
    parser = PlainTooltip()
    parser.feed(spell['tooltip'])
    text = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
    data[key] = {
        'id': spell_id, 'name': spell['name'], 'icon': icon, 'iconPath': f'assets/icons/{key}.jpg',
        'source': f'https://www.wowhead.com/cn/spell={spell_id}', 'endpoint': endpoint,
        'tooltip': html.unescape(text),
        'fetchedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'environment': 'Live, dataEnv=1, locale=4; upstream may change independently of pinned training model',
    }
    print(f'{key}: {spell_id} / {icon}')
(root / 'skill-data.js').write_text('export const SPELL_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
