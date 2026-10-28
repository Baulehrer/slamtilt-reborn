#!/usr/bin/env python3
"""One real-minute packaged Space GPU/audio session, exclusive diagnostic input."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from PIL import Image
from verify_space_session import compare
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=ROOT/'build/space-rc1-host');a=p.parse_args();w=a.work.resolve();w.mkdir(parents=True,exist_ok=False)
 app=ROOT/'build/compat/releases/slamtilt-space-rc1';data=ROOT/'build/compat/releases/space-private-053';source=ROOT/'build/oracle/space-full-game/trace.json'
 (w/'focus.json').write_text(json.dumps(dict(events=[dict(frame=i,type='focus_gained')for i in range(20000)])))
 env=dict(os.environ,XDG_DATA_HOME=str(w/'prefs'));env.pop('SDL_VIDEODRIVER',None);env.pop('SDL_AUDIODRIVER',None)
 subprocess.run([app/'slamspace','--data',data,'--presentation','--fullscreen','--realtime-steps','12000','--replay-only','--replay',source,'--ui-events',w/'focus.json','--trace',w/'game.json','--audio','--audio-trace',w/'audio.json','--highscore-file',w/'score.json','--capture',w/'game.bmp'],env=env,check=True,timeout=100,cwd='/tmp')
 t=read(w/'game.json');compare(t,read(source));s=read(w/'audio.json');ref=read(ROOT/'build/oracle/space-import/audio.json')
 assert s['events']==ref['events']and s['queued_bytes']>0
 assert t['tick_count']==12000 and t['fullscreen']and t['renderer']=='gpu'and t['clamped_frames']==0 and abs(t['real_wall_ms']-60000)<250 and not t['physical_inputs']
 assert s['driver']=='pipewire';score=w/'score.json';stamp=score.stat().st_mtime_ns
 subprocess.run([app/'slamspace','--data',data,'--frames','1','--highscore-file',score,'--trace',w/'reload.json'],check=True,env=dict(env,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
 assert read(w/'reload.json')['highscore_loaded']and score.stat().st_mtime_ns==stamp
 Image.open(w/'game.bmp').save(w/'game.png')
 d={k:t[k]for k in ['tick_count','fullscreen','renderer','video_driver','real_wall_ms','clamped_frames']};d.update(status='VERIFIED',archive_sha256=hashlib.sha256(Path(str(app)+'.tar.gz').read_bytes()).hexdigest(),original_game_vectors_exact=True,canonical_audio_events_exact=True,replay_only=True,audio_driver=s['driver'],audio_requests=len(s['events']),saved_score_fresh_reload_no_rewrite=True,screenshot=str((w/'game.png').relative_to(ROOT)),scope='Actual packaged Debian-built RC1 on current Wayland/GPU/PipeWire; frozen natural input and controlled focus. Unrestricted replay earlier diverged after unscheduled left-flipper activation; exclusive replay is separate from normal live controls. No physical keyboard/listening/full-raster/universal-driver acceptance claim.')
 (ROOT/'analysis/traces/space-release-host.json').write_text(json.dumps(d,indent=2)+'\n');print('Space packaged realtime GPU/audio/highscores PASS',t['real_wall_ms'])
if __name__=='__main__':main()
