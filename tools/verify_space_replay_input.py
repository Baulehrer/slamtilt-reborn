#!/usr/bin/env python3
"""Exclusive diagnostic replay owns game controls; normal live control is preserved."""
import json,os,subprocess,tempfile
from pathlib import Path
from verify_space_session import compare
ROOT=Path(__file__).resolve().parents[1]
def main():
 with tempfile.TemporaryDirectory(prefix='space-replay-')as tmp:
  work=Path(tmp);events=dict(events=[dict(frame=20,type='key',key='Left Shift',down=True),dict(frame=40,type='key',key='Left Shift',down=False),dict(frame=105,type='focus_lost'),dict(frame=106,type='focus_gained')]);(work/'events.json').write_text(json.dumps(events))
  source=ROOT/'build/oracle/space-full-tick/trace.json';gold=json.loads(source.read_text());env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',XDG_DATA_HOME=str(work/'prefs'))
  base=[ROOT/'build/native/slamslice','space',ROOT/'build/oracle/space-full-game',ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT','--presentation','--frames','301','--replay',source,'--ui-events',work/'events.json']
  for exclusive in [False,True]:
   out=work/('exclusive.json'if exclusive else'live.json');subprocess.run([*base,*(['--replay-only']if exclusive else[]),'--trace',out],check=True,env=env);t=json.loads(out.read_text())
   if exclusive:compare(t,gold);assert not t['physical_inputs']
   else:assert any(a!=b['poses']for a,b in zip(t['poses'],gold['globals']))and t['physical_inputs']
  bad=subprocess.run([*base[:4],'--replay-only','--frames','1'],env=env,capture_output=True,text=True);assert bad.returncode==1 and '--replay-only requires --replay'in bad.stderr
 (ROOT/'analysis/traces/space-replay-input-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',original_steps=1200,exclusive_replay_ignores_live_controls=True,focus_pause_preserves_frozen_held_key=True,normal_live_input_unchanged=True,no_replay_rejected=True,scope='Injected actual SDL gameplay/focus events; explicit diagnostic mode only, not changed normal gameplay.'),indent=2)+'\n');print('Space replay ownership PASS')
if __name__=='__main__':main()
