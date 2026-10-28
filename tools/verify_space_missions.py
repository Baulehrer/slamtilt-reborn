#!/usr/bin/env python3
"""One bounded verifier for the three sibling Space missions and final guard."""
import argparse,json,os,subprocess
from pathlib import Path
from verify_space_asteroid import ROOT,read,sha,digest
from space_mission_contracts import contracts
CASES=['race','hack','blam','blam-guard']
def main():
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');p.add_argument('--cases',nargs='+',default=CASES);a=p.parse_args();rows=[]
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';keys=['states','globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256']
 for case in a.cases:
  source=ROOT/f'build/oracle/space-modes/{case}.json';t=read(source);summary=contracts(t);n=t['tick_count'];assert n%4==0
  assert sha(game/'SLAMTILT.EXE')==t['build_sha256']and sha(game/'DAT/SPACE.DAT')==t['dat_sha256']
  f={k:t[k]for k in ['mission','build_sha256','dat_sha256','tick_count','inputs','diagnostic_shots','milestones','payments','original_reset_exact']};f['sequence_sha256']={k:digest(t[k])for k in keys};f['scope']='Frozen actualstation/ramp admission anddiagnostic FREE-ball contacts; realtimers, no rule/target/score edits. Not key-only entiremission.'
  path=ROOT/f'analysis/traces/space-mission-{case}.json'
  if a.refresh:path.write_text(json.dumps(f,indent=2)+'\n')
  assert read(path)==f
  out=source.parent/f'{case}-native.json';capture=source.parent/f'{case}-native.bmp'
  subprocess.run([ROOT/'build/native/slamslice','space',ROOT/'build/oracle/space-full-game',game/'DAT/SPACE.DAT','--frames',str(n//4),'--replay',source,'--diagnostic-shots',source,'--trace',out,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy'))
  actual=read(out);assert actual['tick_count']==n
  for k in keys:assert actual[k]==t[k],(case,k)
  assert capture.read_bytes()[:2]==b'BM';rows.append(dict(case=case,steps=n,contract=summary,fixture_sha256=sha(path)));print(case,n,'Original/native/reset/SDL EXACT',flush=True)
 (ROOT/'analysis/traces/space-mission-family-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',cases=rows),indent=2)+'\n')
if __name__=='__main__':main()
