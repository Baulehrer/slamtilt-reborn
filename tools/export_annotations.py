#!/usr/bin/env python3
"""Export source-supported Amiga patch comments for radare2; no guessed image base."""
import argparse
import json
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--hunk0-base',type=lambda s:int(s,0),required=True,help='Actual imported hunk0 address')
p.add_argument('--patches',type=Path,default=Path('analysis/patches.json'))
a=p.parse_args()
print('# Apply only to unpacked retail Game.exe SHA256 22b894d3667887a0822e63999598ae80813e4a5fccf7881228a97189ebaa3a84')
seen=set()
for patch in json.loads(a.patches.read_text())['patches']:
    if patch.get('coordinate')!='hunk0-relative':continue
    offset=int(patch['address'],0)
    text=f"WHDLoad {patch['version']}: {patch['operation']} {patch['replacement']}; {patch['description']}"
    text=text.replace('\n',' ').replace(';',' / ')
    if (offset,text) in seen:continue
    seen.add((offset,text))
    print(f'CC {text} @ 0x{a.hunk0_base+offset:x}')
