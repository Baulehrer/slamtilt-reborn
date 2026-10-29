#!/usr/bin/env python3
"""Add embedded dependency notices without introducing companion runtime files."""
import argparse
import html
import base64
import gzip
import re
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
# Compress the generated engine, including embedded Wasm, inside the same HTML.
# The bootstrap uses browser APIs only; no CDN, server, or companion file.
pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.S)
scripts = list(pattern.finditer(data))
engine = max(scripts, key=lambda m: len(m.group(1)))
if len(engine.group(1)) < 100000:
    raise SystemExit('Generated engine script missing; refusing to package')
packed = base64.b64encode(gzip.compress(engine.group(1).encode(), compresslevel=9, mtime=0)).decode()
loader = """<script>(async()=>{try{
if(typeof DecompressionStream!=='function')throw Error('This browser needs gzip decompression support.');
const b=Uint8Array.from(atob('PAYLOAD'),c=>c.charCodeAt(0));
const source=await new Response(new Blob([b]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
const script=document.createElement('script');script.id='mainScript';script.textContent=source;document.body.appendChild(script);
}catch(e){status('Engine could not load: '+e.message,true)}})();</script>""".replace('PAYLOAD', packed)
data = data[:engine.start()] + loader + data[engine.end():]
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(data.replace('</body>', ''.join(parts) + '</body>'))
print(args.output)
