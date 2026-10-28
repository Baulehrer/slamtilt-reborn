#!/usr/bin/env python3
"""Original/native/reset/SDL whole Asteroid chain; explicit diagnostic contacts."""
import argparse,json,hashlib,os,subprocess
from pathlib import Path
from space_asteroid_contracts import contracts
from space_asteroid_traps_contracts import contracts as trap_contracts
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['chain','traps'],default='chain');p.add_argument('--refresh',action='store_true');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamslice');a=p.parse_args()
 source=ROOT/f'build/oracle/space-modes/asteroid-{a.case}.json';t=read(source);summary=(contracts if a.case=='chain'else trap_contracts)(t);n=t['tick_count'];assert n%4==0
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';dat=game/'DAT/SPACE.DAT'
 assert sha(game/'SLAMTILT.EXE')==t['build_sha256']and sha(dat)==t['dat_sha256']
 keys=['states','globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']
 f={k:t[k]for k in ['build_sha256','dat_sha256','tick_count','inputs','diagnostic_shots','milestones','payments','original_reset_exact']}
 f.update(sequence_sha256={k:digest(t[k])for k in keys},scope=('Original station/ramp/parking/drain FREE-ball DAT contacts; no rule/score/timer edits. Actual clock/expiry/ABC/F1. Not a legal-key-only whole mission.' if a.case=='chain' else 'Frozen earned station/ramp admission and four actual FREE-ball capture contacts; natural capture timers. No rule/score/timer edits; not legal-key-only trajectory.'))
 path=ROOT/f'analysis/traces/space-asteroid-{a.case}.json'
 if a.refresh:path.write_text(json.dumps(f,indent=2)+'\n')
 assert read(path)==f
 out=source.parent/f'asteroid-{a.case}-native.json';capture=source.parent/f'asteroid-{a.case}-native.bmp'
 subprocess.run([a.viewer,'space',ROOT/'build/oracle/space-full-game',dat,'--frames',str(n//4),'--replay',source,'--diagnostic-shots',source,'--trace',out,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy'))
 actual=read(out);assert actual['tick_count']==n
 for k in keys:assert actual[k]==t[k],k
 assert capture.read_bytes()[:2]==b'BM'
 report=dict(status='VERIFIED',steps=n,contract=summary,original_native_reset_sdl=True,verified_vectors=keys,fixture_sha256=sha(path),scope=f['scope'])
 (ROOT/f'analysis/traces/space-asteroid-{a.case}-acceptance.json').write_text(json.dumps(report,indent=2)+'\n')
 print(n,'Original/native/reset/SDL Asteroid',a.case,'EXACT',summary)
if __name__=='__main__':main()
