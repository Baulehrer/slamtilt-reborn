#!/usr/bin/env python3
"""Exercise four real STIM startup banks for ten deterministic seconds each.

This checks actual native output, not long-run equality with the Original.
The original bank bytes remain in the private work directory.
"""
import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from extract_mean_stim import extract
from verify_retail_tracker_pcm import GAME, TABLES

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--probe', type=Path, required=True)
p.add_argument('--work', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.work.mkdir(parents=True, exist_ok=True)
rows=[]
for table, (expected, offset, order) in TABLES.items():
    dat=(GAME/'DAT'/f'{table.upper()}.DAT').read_bytes()
    assert hashlib.sha256(dat).hexdigest() == expected
    bank,_=extract(dat,0,(offset,))
    path=a.work/f'{table}.stim'; path.write_bytes(bank)
    def run(chunk):
        return subprocess.check_output([str(a.probe.resolve()),str(path),'441000',str(chunk),'restart',str(order),'retail'])
    pcm=run(137); assert pcm == run(4096) and len(pcm) == 441000*4
    values=struct.unpack('<882000h',pcm)
    assert values[::2] == values[1::2] and any(values)
    rows.append({'table':table,'dat_sha256':expected,'order':order,'frames':441000,
                 'pcm_sha256':hashlib.sha256(pcm).hexdigest(),'peak':max(abs(x) for x in values)})
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps({'status':'VERIFIED_BOUNDED','scope':__doc__,'cases':rows},indent=2)+'\n')
print('PASS: four STIM banks, ten deterministic seconds each')
