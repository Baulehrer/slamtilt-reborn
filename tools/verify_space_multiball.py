#!/usr/bin/env python3
"""SHA-bound Original/native/reset/SDL ball-pool verification for Space."""
import argparse,json,os,subprocess
from verify_space_asteroid import ROOT,read,sha,digest
KEYS=['states','globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256','ball_pool_sha256']
def main():
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');a=p.parse_args();rows=[]
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
 for case,phase in [('multiball',4),('alien',6)]:
  source=ROOT/f'build/oracle/space-modes/{case}.json';t=read(source);n=t['tick_count'];assert n%4==0 and t['original_reset_exact']
  assert sha(game/'SLAMTILT.EXE')==t['build_sha256'] and sha(game/'DAT/SPACE.DAT')==t['dat_sha256']
  counts=[r[1] for r in t['lifecycle']];assert max(counts)==3,(case,'not three balls')
  assert any(r[0]==phase and r[1]==3 for r in t['lifecycle']),(case,'admission phase')
  f={k:t[k] for k in ['table','build_sha256','dat_sha256','tick_count','inputs','diagnostic_shots','milestones','payments','original_reset_exact']}
  f.update(sequence_sha256={k:digest(t[k])for k in KEYS},scope='Actual FREE-ball DAT contacts, original spawn timers and integer pool compaction; no rule/score/timer edits. Not complete legal-key-only mode acceptance.')
  path=ROOT/f'analysis/traces/space-{case}.json'
  if a.refresh:path.write_text(json.dumps(f,indent=2)+'\n')
  assert read(path)==f
  out=source.parent/f'{case}-native.json';capture=source.parent/f'{case}-native.bmp'
  cmd=[ROOT/'build/native/slamslice','space',ROOT/'build/oracle/space-full-game',game/'DAT/SPACE.DAT','--frames',str(n//4),'--replay',source,'--diagnostic-shots',source,'--trace',out,'--capture',capture]
  subprocess.run(cmd,check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy'))
  actual=read(out)
  for k in KEYS:assert actual[k]==t[k],(case,k)
  assert capture.read_bytes()[:2]==b'BM';rows.append(dict(case=case,steps=n,max_balls=max(counts),phase=phase,fixture_sha256=sha(path)));print(case,n,'eight vectors exact',flush=True)
 (ROOT/'analysis/traces/space-multiball-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',cases=rows),indent=2)+'\n')
if __name__=='__main__':main()
