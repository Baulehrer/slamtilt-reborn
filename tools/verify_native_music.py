#!/usr/bin/env python3
"""Compare native chunked PCM against the existing independent libxmp fixture."""
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);a=p.parse_args()
records=json.loads((ROOT/'analysis/audio-load-results.json').read_text())
results=[]
for record in records:
    if record['path'] not in ['build/decoded/Music.Bin','build/decoded/IntroMusic.Bin']:continue
    path=ROOT/record['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
    for chunk in [1024,777,220500]:
        pcm=subprocess.check_output([str(a.native),str(path),'220500',str(chunk),'restart'])
        assert len(pcm)==record['pcm_bytes'] and hashlib.sha256(pcm).hexdigest()==record['pcm_sha256'], (record['path'],chunk)
    results.append(dict(path=record['path'],pcm_sha256=record['pcm_sha256'],chunks=[1024,777,220500],restart_identical=True))
assert len(results)==2
bad=subprocess.run([str(a.native),str(ROOT/'build/decoded/Music.Bin'),'1024','1024','restart','999'],capture_output=True)
assert bad.returncode!=0, 'Out-of-range music order accepted'
(ROOT/'analysis/traces/native-music-validation.json').write_text(json.dumps(dict(sample_rate=44100,channels=2,bits=16,cases=results,invalid_order_rejected=True),indent=2)+'\n')
print('Two original STIM modules: chunked PCM/restart match existing five-second hashes')
