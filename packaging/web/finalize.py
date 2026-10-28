#!/usr/bin/env python3
"""Add embedded dependency notices without introducing companion runtime files."""
import argparse
import html
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('input', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
notices = [
    ('Emscripten', root / 'packaging/web/licenses/emscripten.txt'),
    ('ancient', root / 'LICENSES/ancient-BSD-2-Clause.txt'),
    ('SDL3', root / 'build/arm64-release/sources/SDL3-3.4.18/LICENSE.txt'),
    ('libxmp', root / 'build/libxmp/docs/COPYING'),
    ('Inter', root / 'assets/fonts/OFL.txt'),
    ('nlohmann/json', root / 'packaging/web/licenses/nlohmann-json.txt'),
    ('stb_truetype', root / 'build/compat/releases/slamtilt-reborn-linux-x86_64-rc6/LICENSES/stb_truetype.h'),
]
parts = ['<details style="margin:24px;color:#94a7c0"><summary>Open-source acknowledgements</summary>']
for name, path in notices:
    data = path.read_text()
    if name == 'stb_truetype':
        data = data[data.rfind('ALTERNATIVE A - MIT License'):]
    parts.append('<h3>' + html.escape(name) + '</h3><pre style="white-space:pre-wrap">' + html.escape(data) + '</pre>')
parts.append('</details>')
data = args.input.read_text()
assert '</body>' in data
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(data.replace('</body>', ''.join(parts) + '</body>'))
print(args.output)
