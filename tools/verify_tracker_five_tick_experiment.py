#!/usr/bin/env python3
"""Compare five manually clocked Original/native tracker/mixer windows.

Retains synthetic startup, 50 Hz cadence and fixed original voice links. It
is not a complete scheduler, effect/finetune/loop or audible-output proof.
The experimental library must be built separately and is not installed.
"""
import argparse
import hashlib
import json
import math
import os
import struct
import subprocess
import sys
from pathlib import Path
from extract_mean_stim import extract
from verify_retail_tracker_pcm import ROOT, GAME, TABLES


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--baseline-library', type=Path, help='Historical baseline library for this experiment')
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    lib = a.library.absolute()
    baseline = dict(os.environ); baseline.pop('LD_LIBRARY_PATH',None)
    if a.baseline_library:
        baseline_lib = a.baseline_library.absolute()
        baseline['LD_LIBRARY_PATH'] = str(baseline_lib.parent)
        baseline_linkage = subprocess.check_output(['ldd',str(a.native.resolve())],env=baseline,text=True)
        assert str(baseline_lib) in baseline_linkage
    modified = dict(baseline,LD_LIBRARY_PATH=str(lib.parent))
    linkage = subprocess.check_output(['ldd',str(a.native.resolve())],env=modified,text=True)
    assert str(lib) in linkage
    rows = []
    for table, (dat_sha, offset, order) in TABLES.items():
        dat = (GAME/'DAT'/f'{table.upper()}.DAT').read_bytes()
        assert hashlib.sha256(dat).hexdigest() == dat_sha
        subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),
                        '--table',table,'--ticks','5','--output',str(a.work)],check=True)
        original = (a.work/f'{table}-first-tick.s16le').read_bytes()
        reference = struct.unpack('<8820h',original)[::2]
        stim, _ = extract(dat,0,(offset,))
        bank = a.work/f'{table}.stim'; bank.write_bytes(stim)
        variants = {}
        for name, env in (('baseline',baseline),('experiment',modified)):
            pcm = subprocess.check_output([str(a.native.resolve()),str(bank),'4410','137','restart',str(order),'retail'],env=env)
            native = struct.unpack('<8820h',pcm)[::2]
            windows=[]
            for i in range(5):
                x,y=reference[i*882:(i+1)*882],native[i*882:(i+1)*882]
                xx=sum(v*v for v in x); yy=sum(v*v for v in y)
                assert xx and yy
                windows.append({'correlation':round(sum(v*w for v,w in zip(x,y))/math.sqrt(xx*yy),6),
                                'rms_ratio':round(math.sqrt(yy/xx),6),
                                'exact_frames':sum(v==w for v,w in zip(x,y))})
            variants[name]=windows
        assert all(w['correlation'] > 0.99 for w in variants['experiment']), (table, variants)
        assert all(w['correlation'] >= base['correlation'] for w, base in
                   zip(variants['experiment'], variants['baseline'])), (table, variants)
        rows.append({'table':table,'original_pcm_sha256':hashlib.sha256(original).hexdigest(),
                     'original_report_sha256':digest(a.work/f'{table}-report.json'), 'variants':variants})
    result={'status':'EXPERIMENT_ONLY','scope':__doc__,'native_sha256':digest(a.native),
            'library_sha256':digest(lib),'frames_per_window':882,'windows':5,'cases':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: four tables, five manually clocked Original/native windows each')


if __name__ == '__main__': main()
