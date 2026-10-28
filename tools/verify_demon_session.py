#!/usr/bin/env python3
"""Shared presentation/audio/options on Demon, Original-record loading, private state."""
import json,os,subprocess,tempfile,hashlib
from pathlib import Path
from verify_space_session import compare
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
 work=ROOT/'build/demon-session';work.mkdir(exist_ok=True);game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
 with tempfile.TemporaryDirectory(prefix='private-',dir=work)as tmp:
  tmp=Path(tmp);env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',XDG_DATA_HOME=str(tmp/'prefs'))
  def run(label,*args):
   out=work/(label+'.json');subprocess.run([ROOT/'build/native/slamslice','demon',ROOT/'build/oracle/demon-full-game',game/'DAT/DEMON.DAT',*map(str,args),'--trace',out],check=True,env=env);return read(out)
  source=ROOT/'build/oracle/demon-full-tick/trace.json';actual=run('presentation','--presentation','--frames',300,'--replay',source,'--audio','--audio-trace',work/'launch-audio.json');compare(actual,read(source))
  assert read(work/'launch-audio.json')['events']==read(ROOT/'analysis/demon-audio-profile.json')['launch']['events']
  keys=['Escape','Down','Down','Down','Right','Tab','Right','Tab','Right','Tab','Left','Tab','Down','Down','Down','Down','Return']
  events=[dict(frame=i,type='key',key=k,down=True)for i,k in enumerate(keys)]+[dict(frame=17,type='focus_lost'),dict(frame=18,type='focus_gained')]
  path=work/'events.json';path.write_text(json.dumps(dict(events=events)))
  ui=run('menu','--presentation','--persist-options','--frames',20,'--ui-events',path,'--audio','--audio-trace',work/'menu-audio.json','--capture',work/'menu.bmp');f=ui['ui_frames']
  assert all(r['tick']==0 and r['menu']and r['audio_device_paused']for r in f[:16]);assert not f[16]['menu']and f[17]['tick']==f[16]['tick']and not f[17]['focused']and f[17]['audio_device_paused'];assert f[18]['focused']and f[18]['tick']>f[17]['tick']
  assert abs(f[-1]['zoom']-1.05)<1e-5 and f[-1]['dmd_position']==1
  again=run('options-reload','--presentation','--persist-options','--frames',1);assert abs(again['ui_frames'][0]['zoom']-1.05)<1e-5
  profile=tmp/'scores.json';source=ROOT/'build/oracle/demon-full-game/trace.json';first=run('natural','--frames',3000,'--replay',source,'--highscore-file',profile);compare(first,read(source));assert not profile.exists(),'Zero-score unqualified natural fixture must not save a new table'
  records=bytes.fromhex('000015000000')+b'ABC\0'+bytes(40);earned=read(ROOT/'build/oracle/demon-modes/base-rules-rewards.json');digest=hashlib.sha256(records).hexdigest();assert digest in earned['highscore_sha256']
  profile.write_text(json.dumps(dict(version=1,records=list(records))));stamp=profile.stat().st_mtime_ns;loaded=run('earned-record-load','--frames',1,'--highscore-file',profile);assert loaded['highscore_loaded']and loaded['highscore_sha256'][0]==digest and profile.stat().st_mtime_ns==stamp
  bad=tmp/'bad.json';bad.write_text('invalid profile');run('bad-profile','--frames',1,'--highscore-file',bad);assert bad.read_text()=='invalid profile'
 report=dict(status='VERIFIED',presentation_original_steps=1200,launch_audio_events_exact=5,menu_focus_audio_pause=True,options_fresh_reload=True,natural_game_original_steps=12000,zero_score_does_not_save=True,original_earned_15M_ABC_record_load_no_rewrite=True,corrupt_profile_preserved=True,scope='Private profiles. Qualified Demon score/initials are from diagnostic source case, not a newly proven legal-only scoring/save trajectory; no fabricated gameplay score or persistent diagnostic scores.')
 (ROOT/'analysis/traces/demon-session-acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
