#!/usr/bin/env python3
"""Check the packaged real-time GPU run; raw traces remain private under build/."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from verify_demon_legal import KEYS
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--app',type=Path,default=ROOT/'build/compat/releases/slamtilt-demon-rc1');p.add_argument('--work',type=Path,default=ROOT/'build/demon-rc-host');p.add_argument('--run',action='store_true');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/demon-release-host.json');a=p.parse_args();app=a.app.resolve();work=a.work.resolve();
 if a.run:
  work.mkdir(parents=True,exist_ok=True);assert not (work/'game.json').exists()and not (work/'scores.json').exists(),'Use fresh --work directory'
  game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';data=work/'data'
  subprocess.run([app/'bin/slamdemon-import',game/'SLAMTILT.EXE',game/'DAT',data],check=True)
  (work/'focus.json').write_text(json.dumps(dict(events=[dict(frame=i,type='focus_gained')for i in range(10000)])))
  env=dict(os.environ,XDG_DATA_HOME=str(work/'profile'))
  subprocess.run([app/'slamdemon','--data',data,'--fullscreen','--realtime-steps','10512','--replay',ROOT/'build/oracle/demon-modes/legal-game-rewards.json','--replay-only','--ui-events',work/'focus.json','--trace',work/'game.json','--audio-trace',work/'audio.json','--capture',work/'game.bmp','--highscore-file',work/'scores.json'],check=True,env=env,timeout=90)
 t=read(work/'game.json');g=read(ROOT/'build/oracle/demon-modes/legal-game-rewards.json');audio=read(work/'audio.json')
 for k in KEYS:assert t[k]==g[k],k
 assert t['tick_count']==10512 and t['replay_only']and t['fullscreen']and t['renderer']=='gpu'and t['video_driver']=='wayland'
 assert t['clamped_frames']==0 and 52560<=t['real_wall_ms']<55560,(t['clamped_frames'],t['real_wall_ms'])
 assert audio['events']==g['audio_events']and audio['enabled']and audio['queued_bytes']>0
 records=bytes.fromhex(next(m for m in g['milestones']if m['label']=='game_over')['highscore_hex']);score=work/'scores.json';assert bytes(read(score)['records'])==records;stamp=score.stat().st_mtime_ns
 env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
 subprocess.run([app/'slamdemon','--data',work/'data','--frames','1','--trace',work/'reload.json','--highscore-file',score,'--no-audio'],check=True,env=env)
 r=read(work/'reload.json');assert r['highscore_loaded']and r['highscore_sha256'][0]==hashlib.sha256(records).hexdigest()and score.stat().st_mtime_ns==stamp
 report={k:t[k]for k in ['tick_count','fullscreen','renderer','video_driver','real_wall_ms','clamped_frames']}
 report.update(status='VERIFIED_BOUNDED_HOST',archive_sha256=sha(Path(str(app)+'.tar.gz')),twelve_vectors_exact=True,canonical_audio_events_exact=True,audio_requests=len(audio['events']),audio_driver=audio.get('driver',audio.get('audio_driver')),saved_score_fresh_reload_no_rewrite=True,screenshot=str((work/'game.bmp').relative_to(ROOT)),scope='Actual Debian-built package on current Wayland/GPU/audio host; frozen legal keys and controlled focus. No physical keyboard/listening/whole-raster/universal-driver claim.')
 a.report.write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
