#!/usr/bin/env python3
"""Frozen original score raster hashes; requires user's MAIN.DAT."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
probe=Path(sys.argv[1])
main=Path(sys.argv[2]) if len(sys.argv)>2 else next((ROOT/'build/corpus/win95/demo-1997').rglob('MAIN.DAT'))
f=json.loads((ROOT/'analysis/traces/mean-score-font-fixture.json').read_text())
assert hashlib.sha256(main.read_bytes()).hexdigest()==f['main_dat_sha256']
actual=json.loads(subprocess.check_output([str(probe),str(main)],input=json.dumps([c['input'] for c in f['cases']]).encode()))
assert len(actual)==len(f['cases'])
for pixels,c in zip(actual,f['cases']):assert hashlib.sha256(bytes(pixels)).hexdigest()==c['pixels_sha256'],c['input']
print(json.dumps(dict(cases=len(actual),pixels=len(actual)*1920,differences=0)))
