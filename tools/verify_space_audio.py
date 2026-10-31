#!/usr/bin/env python3
"""Original service stream -> existing native audio, both silent observer and SDL."""
from retail_audio_fixture import corrected_audio_events
import argparse,json,os,subprocess
from pathlib import Path
from verify_space_asteroid import ROOT,read

def main():
 p=argparse.ArgumentParser();p.add_argument('--cases',nargs='*');a=p.parse_args();f=read(ROOT/'analysis/traces/space-audio-events.json');rows=[];work=ROOT/'build/oracle/space-audio';work.mkdir(exist_ok=True,parents=True)
 for row in f['cases']:
  if a.cases and row['case']not in a.cases:continue
  case=row['case'];source=ROOT/row['source'];out=work/f'{case}.json';n=row['steps']
  game_trace=work/f'{case}-game.json'
  cmd=[ROOT/'build/native/slamslice','space',ROOT/'build/oracle/space-full-game',ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT','--frames',str(n//4),'--replay',source,'--audio','--audio-trace',out,'--trace',game_trace]
  if read(source).get('diagnostic_shots'):cmd+=['--diagnostic-shots',source]
  subprocess.run(cmd,check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
  state=read(game_trace);gold=read(source);assert state['states']==gold['states']
  for i,(x,y)in enumerate(zip(gold['globals'],state['globals'])):
   for k,v in y.items():assert x[k]==v,(case,i,k)
  for key in ['lifecycle','highscore_sha256','lamp_sha256']:assert state[key]==gold[key],(case,key)
  assert state['poses']==gold.get('poses',[r['poses']for r in gold['globals']]if 'poses'in gold['globals'][0]else None)
  if gold.get('diagnostic_shots'):assert state['raw_state_sha256']==gold['raw_state_sha256']
  actual=read(out);assert actual['events']==corrected_audio_events(row['events'], 'space'),(case,'events');assert actual['enabled']and actual['queued_bytes']>0
  rows.append(dict(case=case,steps=n,requests=len(row['events']),original_native_exact=True,queued_bytes=actual['queued_bytes']));print(case,len(row['events']),'original/native audio requests EXACT',flush=True)
 (ROOT/'analysis/traces/space-audio-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',cases=rows,scope='Original request ordering/registers plusSDLqueue; assets/PCM separatelyverified. Not Original mixed-device PCM or physical listening parity.'),indent=2)+'\n')
if __name__=='__main__':main()
