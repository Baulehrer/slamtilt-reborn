#!/usr/bin/env python3
"""SHA-bound Original/native/reset/SDL ball-pool verification for Demon."""
from retail_audio_fixture import corrected_audio_events
import argparse,json,os,subprocess
from verify_space_asteroid import ROOT,read,sha,digest
from demon_video_contracts import contracts,CASES
KEYS=['states','globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256','ball_pool_sha256','clock_state','mode_aux_sha256','video_state']
def verify_input(case):
 source=ROOT/f'build/oracle/demon-modes/{case}-rewards.json';t=read(source);work=source.parent;n=t['tick_count'];cut=next(m['tick']for m in t['milestones']if m['label']=='video_started')
 replay=work/f'{case}-sdl-replay.json';replay.write_text(json.dumps(dict(inputs=[e for e in t['inputs']if e['tick']<cut])))
 events=[dict(frame=i,type='focus_gained')for i in range(n//4)]
 controls=[e for e in t['inputs']if e['tick']>=cut]
 for e in controls:
  assert e['tick']%4==0
  events.append(dict(frame=e['tick']//4,type='key',key={'left':'Left Shift','right':'Right Shift','enter':'Return'}[e['action']],down=e['down']))
 events.sort(key=lambda e:e['frame']);ui=work/f'{case}-sdl-events.json';ui.write_text(json.dumps(dict(events=events)))
 out=work/f'{case}-sdl.json';audio=work/f'{case}-sdl-audio.json';game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
 subprocess.run([ROOT/'build/native/slamslice','demon',ROOT/'build/oracle/demon-full-game',game/'DAT/DEMON.DAT','--presentation','--frames',str(n//4),'--replay',replay,'--diagnostic-shots',source,'--ui-events',ui,'--trace',out,'--audio','--audio-trace',audio],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
 actual=read(out)
 for k in KEYS:assert actual[k]==t[k],(case,'SDL keys',k)
 journal=[dict(tick=int(tick),**e)for tick,es in actual['physical_inputs']for e in es]
 startup=[e for e in journal if e['tick']<cut];assert all(e['tick']==0 and not e['down']for e in startup)
 assert [e for e in journal if e['tick']>=cut]==controls,(case,'SDL input journal')
 assert read(audio)['events']==corrected_audio_events(t['audio_events'], 'demon')
 print(case,'actual SDL key events / eleven vectors / audio exact',flush=True)
 return dict(case=case,steps=n,key_events=len(controls),eleven_vectors_exact=True,audio_exact=True,scope='Programmatically injected SDL events; not physical keyboard or human visualtracking')
def main():
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');p.add_argument('--cases',nargs='+',choices=CASES);a=p.parse_args();rows=[]
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
 for case,phase in [(c,2)for c in CASES]:
  if a.cases and case not in a.cases:continue
  source=ROOT/f'build/oracle/demon-modes/{case}-rewards.json';t=read(source);contract=contracts(t);n=t['tick_count'];assert n%4==0 and t['original_reset_exact']
  assert sha(game/'SLAMTILT.EXE')==t['build_sha256'] and sha(game/'DAT/DEMON.DAT')==t['dat_sha256']
  counts=[r[1]for r in t['lifecycle']];assert any(r[0]==phase for r in t['lifecycle'])
  f={k:t[k] for k in ['case','audio_events','table','build_sha256','dat_sha256','tick_count','inputs','diagnostic_shots','milestones','payments','original_reset_exact']}
  f.update(sequence_sha256={k:digest(t[k])for k in KEYS},scope='Actual FREE-ball DAT contacts, original spawn timers and integer pool compaction; no rule/score/timer edits. Not complete legal-key-only mode acceptance.')
  path=ROOT/f'analysis/traces/demon-{case}-rewards.json'
  if a.refresh:path.write_text(json.dumps(f,indent=2)+'\n')
  assert read(path)==f
  out=source.parent/f'{case}-rewards-native.json';capture=source.parent/f'{case}-rewards-native.bmp'
  cmd=[ROOT/'build/native/slamslice','demon',ROOT/'build/oracle/demon-full-game',game/'DAT/DEMON.DAT','--frames',str(n//4),'--replay',source,'--diagnostic-shots',source,'--trace',out,'--capture',capture]
  audio=source.parent/f'{case}-rewards-native-audio.json';cmd+=['--audio','--audio-trace',audio]
  subprocess.run(cmd,check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
  actual=read(out)
  for k in KEYS:assert actual[k]==t[k],(case,k)
  sound=read(audio);assert sound['events']==corrected_audio_events(t['audio_events'], 'demon') and sound['enabled'] and sound['queued_bytes']>0
  assert capture.read_bytes()[:2]==b'BM';rows.append(dict(case=case,steps=n,max_balls=max(counts),phase=phase,contract=contract,audio_requests=len(t['audio_events']),fixture_sha256=sha(path)));print(case,n,'eleven vectors and audio exact',flush=True)
 input_rows=[verify_input(c)for c in ['video-brain-win','video-wolf-shoot']]
 (ROOT/'analysis/traces/demon-video-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',cases=rows,actual_sdl_keys=input_rows),indent=2)+'\n')
if __name__=='__main__':main()
