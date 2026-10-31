#!/usr/bin/env python3
"""Original-exact legal game plus production highscore save/reload in private profile."""
from retail_audio_fixture import corrected_audio_events
import argparse,json,os,subprocess,tempfile
from pathlib import Path
from verify_space_asteroid import ROOT,read,sha,digest
KEYS=['states','globals','poses','lifecycle','highscore_sha256','lamp_sha256','raw_state_sha256','ball_pool_sha256','clock_state','mode_aux_sha256','video_state','variant_state']
def main():
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');a=p.parse_args();source=ROOT/'build/oracle/demon-modes/legal-game-rewards.json';t=read(source);m={r['label']:r for r in t['milestones']};n=t['tick_count']
 assert t['original_reset_exact']and t['diagnostic_shots']==[]and n%4==0
 assert m['first_natural_score']['tick']==3009 and int(m['first_natural_score']['score'])==25000
 over=m['game_over'];assert over['phase']==0 and int(over['score'])==125000
 records=bytes.fromhex(over['highscore_hex']);assert records[:6]==bytes.fromhex(over['score'])and records[6:9]==b'ABC'
 assert m['new_game']['phase']==1 and m['second_game_running']['phase']==2 and m['second_game_running']['state']==2
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';assert sha(game/'SLAMTILT.EXE')==t['build_sha256']and sha(game/'DAT/DEMON.DAT')==t['dat_sha256']
 f={k:t[k]for k in ['case','table','build_sha256','dat_sha256','tick_count','inputs','diagnostic_shots','milestones','payments','audio_events','original_reset_exact']};f.update(sequence_sha256={k:digest(t[k])for k in KEYS},scope='Actual Enter/Shift/ABC/F1 keys from reset; zero diagnostic contacts and no gameplay/rule/seed/timer writes. One natural scoring schedule and fresh empty highscore profile, not all modes via keys.')
 fixture=ROOT/'analysis/traces/demon-legal-game-rewards.json'
 if a.refresh:fixture.write_text(json.dumps(f,indent=2)+'\n')
 assert read(fixture)==f
 work=ROOT/'build/demon-legal-session';work.mkdir(exist_ok=True);env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
 with tempfile.TemporaryDirectory(dir=work)as tmp:
  profile=Path(tmp)/'scores.json';out=work/'native.json';audio=work/'audio.json';cmd=[ROOT/'build/native/slamslice','demon',ROOT/'build/oracle/demon-full-game',game/'DAT/DEMON.DAT','--frames',str(n//4),'--replay',source,'--replay-only','--trace',out,'--capture',work/'native.bmp','--audio','--audio-trace',audio,'--highscore-file',profile]
  subprocess.run(cmd,check=True,env=env);v=read(out)
  for k in KEYS:assert v[k]==t[k],k
  assert read(audio)['events']==corrected_audio_events(t['audio_events'], 'demon')and read(audio)['queued_bytes']>0
  saved=read(profile);assert saved['version']==1 and bytes(saved['records'])==records
  stamp=profile.stat().st_mtime_ns;reload=work/'reload.json'
  subprocess.run([ROOT/'build/native/slamslice','demon',ROOT/'build/oracle/demon-full-game',game/'DAT/DEMON.DAT','--frames','1','--highscore-file',profile,'--trace',reload,'--no-audio'],check=True,env=env)
  r=read(reload);import hashlib
  assert r['highscore_loaded']and r['highscore_sha256'][0]==hashlib.sha256(records).hexdigest()and profile.stat().st_mtime_ns==stamp
 result=dict(status='VERIFIED',cases=[dict(case='legal-game',steps=n,audio_requests=len(t['audio_events']),fixture_sha256=sha(fixture),first_score=25000,first_score_tick=3009,final_score=125000,initials='ABC',game_over=over['tick'],F1_and_relaunch=True)],twelve_vectors_exact=True,diagnostic_contacts=0,production_save_reload=True,profile_scope='Fresh initially empty private profile; no imported/edited records; no persistent writes from diagnostic games')
 (ROOT/'analysis/traces/demon-legal-acceptance.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
