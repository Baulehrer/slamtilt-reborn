#!/usr/bin/env python3
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
from extract_mean_stim import extract
p=argparse.ArgumentParser();p.add_argument('--native',required=True);p.add_argument('--dat',type=Path,required=True);a=p.parse_args()
data=a.dat.read_bytes();records=[]
with tempfile.TemporaryDirectory() as temp:
    prefix=str(Path(temp)/'bank')
    subprocess.run([a.native,str(a.dat),prefix],check=True)
    for bank in range(2):
        actual=Path(prefix+str(bank)+'.stim').read_bytes();expected,_=extract(data,bank)
        assert actual==expected
        records.append(dict(bank=bank,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest()))
    broken=Path(temp)/'broken.dat';broken.write_bytes(data[:100])
    assert subprocess.run([a.native,str(broken),prefix],capture_output=True).returncode!=0
Path('analysis/traces/native-mean-banks-validation.json').write_text(json.dumps(records,indent=2)+'\n')
print('Two native banks byteidentical; truncated DAT rejected')
