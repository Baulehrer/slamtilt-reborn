#!/usr/bin/env python3
"""Assert all four adapted Original first-tick PCM comparisons improve.

Only the first 882 frames are compared; this is not complete audio parity.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--native', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_native.py'),
                '--native',str(a.native.resolve()),'--output',str(a.output)],check=True)
report=json.loads((a.output/'comparison.json').read_text())
for row in report['cases']:
    assert row['uncentered_correlation'] > 0.99, (row['table'],row['uncentered_correlation'])
print('PASS: four table startup correlations above 0.99')
