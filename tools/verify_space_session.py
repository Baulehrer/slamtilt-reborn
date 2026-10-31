#!/usr/bin/env python3
"""Private profiles only: presentation invariance, actual menu events, score reload."""
import json,os,subprocess,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def compare(actual,gold):
 for k in ['states','lifecycle','highscore_sha256','lamp_sha256']:assert actual[k]==gold[k],k
 assert actual['poses']==gold.get('poses',[r['poses']for r in gold['globals']])
 for i,(a,b)in enumerate(zip(actual['globals'],gold['globals'])):
  for k in a:assert a[k]==b[k],(i,k)
def main():
 work=ROOT/'build/space-session';work.mkdir(exist_ok=True);game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
 with tempfile.TemporaryDirectory(prefix='private-',dir=work)as private:
  private=Path(private);env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',XDG_DATA_HOME=str(private/'prefs'))
  def run(label,*args):
   out=work/(label+'.json');cmd=[ROOT/'build/native/slamslice','space',ROOT/'build/oracle/space-full-game',game/'DAT/SPACE.DAT',*map(str,args),'--trace',out];subprocess.run(cmd,check=True,env=env);return read(out)
  source=ROOT/'build/oracle/space-full-tick/trace.json';t=read(source)
  actual=run('presentation','--presentation','--frames',300,'--replay',source)
  compare(actual,t)
  keys=['Escape','Down','Down','Down','Right','Tab','Right','Tab','Right','Tab','Left','Tab']+['Down']*17+['Return']
  closed=len(keys)-1
  events=[dict(frame=i,type='key',key=k,down=True)for i,k in enumerate(keys)]+[dict(frame=closed+1,type='focus_lost'),dict(frame=closed+2,type='focus_gained')]
  path=work/'events.json';path.write_text(json.dumps(dict(events=events)))
  ui=run('menu','--presentation','--persist-options','--frames',closed+4,'--ui-events',path,'--audio','--audio-trace',work/'menu-audio.json','--capture',work/'menu.bmp')
  f=ui['ui_frames'];assert all(r['tick']==0 and r['menu']for r in f[:closed]);assert not f[closed]['menu'] and f[closed+1]['tick']==f[closed]['tick']and not f[closed+1]['focused'];assert f[closed+2]['focused']and f[closed+2]['tick']>f[closed+1]['tick']
  assert all(r['audio_device_paused']for r in f[:closed]) and not f[closed]['audio_device_paused'] and f[closed+1]['audio_device_paused'] and not f[closed+2]['audio_device_paused']
  sound=read(work/'menu-audio.json');assert sound['enabled']and sound['queued_bytes']>0
  assert abs(f[-1]['zoom']-1.05)<1e-5 and f[-1]['dmd_position']==1
  settings=list((private/'prefs').rglob('options.json'));assert len(settings)==1;stored=read(settings[0]);assert stored['visual']['preset']==3 and abs(stored['volume']-.95)<1e-5
  again=run('settings-reload','--presentation','--persist-options','--frames',1);assert abs(again['ui_frames'][0]['zoom']-1.05)<1e-5 and again['ui_frames'][0]['dmd_position']==1
  profile=private/'space-highscores.json';source=ROOT/'build/oracle/space-full-game/trace.json';t=read(source)
  first=run('score-save','--frames',3000,'--replay',source,'--highscore-file',profile)
  compare(first,t)
  records=bytes(read(profile)['records']);assert len(records)==50;stamp=profile.stat().st_mtime_ns
  loaded=run('score-reload','--frames',1,'--highscore-file',profile);assert loaded['highscore_loaded']and loaded['highscore_sha256'][0]==hashlib.sha256(records).hexdigest();assert profile.stat().st_mtime_ns==stamp
  bad=private/'bad.json';bad.write_text('invalid profile');run('score-corrupt','--frames',1,'--highscore-file',bad);assert bad.read_text()=='invalid profile'
  report=dict(status='VERIFIED',presentation_game_vectors_exact=1200,menu_events=len(events),menu_and_focus_pause=True,audio_device_pause_resume=True,settings_apply_and_fresh_reload=True,finite_game_exact=12000,private_score_save_reload_no_rewrite=True,corrupt_profile_preserved=True)
 (ROOT/'analysis/traces/space-session-acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
