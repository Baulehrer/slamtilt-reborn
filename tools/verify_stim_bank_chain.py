#!/usr/bin/env python3
"""Check two successive same-table bank switches against Retail PCM.

The source tracker is primed for one tick, then the intermediate bank plays
four ticks before the target bank. Game scheduler, SFX and device output are
not modeled. Original data and PCM remain in the private work directory.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from extract_mean_stim import extract
from verify_retail_tracker_pcm import ROOT, GAME, TABLES, EXE_SHA
from verify_stim_crossbank_pcm import BANKS

CASES = {'mean': (0,1,0,5,46,16), 'pirate': (0,1,0,34,27,34),
         'space': (0,1,2,32,20,28), 'demon': (0,1,2,25,15,18)}

def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,required=True); p.add_argument('--library',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    p.add_argument('--ticks',type=int,default=32); a=p.parse_args(); assert 1<=a.ticks<=2048
    a.work.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,LD_LIBRARY_PATH=str(a.library.absolute().parent))
    assert str(a.library.absolute()) in subprocess.check_output(['ldd',str(a.native.resolve())],env=env,text=True)
    rows=[]
    for table,(source,middle,target,warm,mid_order,order) in CASES.items():
        dat=(GAME/'DAT'/f'{table.upper()}.DAT').read_bytes(); assert sha(dat)==TABLES[table][0]
        modules=[]
        for bank in (source,middle,target):
            path=a.work/f'{table}-{bank}.stim';path.write_bytes(extract(dat,0,(BANKS[table][bank],))[0]);modules.append(path.resolve())
        work=a.work/table
        cmd=[sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),'--table',table,
             '--warm-order',str(warm),'--warm-bank-offset',hex(BANKS[table][source]),
             '--middle-order',str(mid_order),'--middle-bank-offset',hex(BANKS[table][middle]),'--middle-ticks','4',
             '--bank-offset',hex(BANKS[table][target]),'--order',str(order),'--ticks',str(a.ticks),
             '--dynamic-voices','--allow-silent','--output',str(work)]
        subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
        original=(work/f'{table}-first-tick.s16le').read_bytes()
        native=subprocess.check_output([str(a.native.resolve()),*(str(x) for x in modules),str(warm),str(mid_order),str(order),'4',str(a.ticks)],env=env)
        assert len(original)==len(native)==a.ticks*882*4
        assert original==native, (table,'bank-chain PCM differs')
        rows.append({'table':table,'banks':[source,middle,target],'orders':[warm,mid_order,order],
                     'intermediate_ticks':4,'ticks':a.ticks,'frames':a.ticks*882,'pcm_sha256':sha(original)})
        print(table,'EXACT',flush=True)
    report={'status':'VERIFIED_BOUNDED','scope':__doc__,'exe_sha256':EXE_SHA,
            'library_sha256':sha(a.library.read_bytes()),'native_sha256':sha(a.native.read_bytes()),'cases':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: four consecutive-bank sequences exact')

if __name__=='__main__': main()
