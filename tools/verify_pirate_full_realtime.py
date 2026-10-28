#!/usr/bin/env python3
"""Complete real-clock natural Crocodile game vs fresh original; no waypoints."""
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--case',choices=['natural-crocodile-game','acceptance-multiball'],default='natural-crocodile-game');p.add_argument('--launcher',type=Path,default=ROOT/'build/compat/releases/slamtilt-pirate-fullgame/slampirate');p.add_argument('--output',type=Path);a=p.parse_args()
    case=a.case;fixture=ROOT/f'analysis/traces/pirate-{case}.json';f=read(fixture);n=f['tick_count'];work=ROOT/'build/oracle/pirate-full-realtime';work=work if case=='natural-crocodile-game'else work/case;work.mkdir(parents=True,exist_ok=True)
    if a.run:
        subprocess.run([a.launcher,'--data',ROOT/'build/imported/pirate-retail','--fullscreen','--realtime-steps',str(n),'--replay',fixture,
            '--full-state-trace','--trace-output',work/'game.json','--audio-trace',work/'audio.json','--timing-output',work/'timing.json','--capture',work/'final.bmp'],check=True,timeout=n/200+40)
    t=read(work/'game.json');g=read(ROOT/f'build/oracle/pirate-modes/{case}/trace.json');o=read(ROOT/'analysis/traces/pirate-full-realtime-original.json')
    from verify_pirate_multiball_campaign import integrity
    assert integrity(g,f,f['build_sha256'],f['dat_sha256'])==n
    assert not f['diagnostic_shots']
    if case=='natural-crocodile-game':assert o['source_fixture_sha256']==sha(fixture)
    assert not t['error']and t['tick_count']==n
    from verify_pirate_multiball import KEYS
    for key in KEYS:assert t[key]==g[key],key
    ms=read(work/'original-magnasaver.json')if case=='natural-crocodile-game'else g['magnasaver_state'];assert t['magnasaver_state']==ms
    assert hashlib.sha256(json.dumps(ms,separators=(',',':')).encode()).hexdigest()==(o if case=='natural-crocodile-game'else f)['magnasaver_state_sha256']
    events=read(work/'audio.json');expected=next(r for r in read(ROOT/'analysis/traces/pirate-audio-events.json')['cases']if r['case']==case)
    assert events['events']==expected['events']and events['queued_bytes']>0 and not events['error']
    timing=read(work/'timing.json');assert timing['fullscreen']and timing['video']!='dummy'and timing['renderer']=='gpu'
    frames=timing['frames'];assert frames[-1][5]==n and all(len(r)==11 for r in frames)
    active_ns=sum(r[9]for r in frames if r[7]);clamped=sum(r[10]>100000000 for r in frames)
    assert 0<=active_ns-n*5000000<frames[-1][9]+5000000
    # Persist same complete natural game in a private profile, then reload in a
    # fresh process; no user profile is read/written in either acceptance path.
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    with tempfile.TemporaryDirectory(prefix='pirate highscore ',dir=work)as temp:
        temp=Path(temp);profile=temp/'profile.json';fixed=temp/'fixed.json';reload=temp/'reload.json'
        subprocess.run([a.launcher,'--data',ROOT/'build/imported/pirate-retail','--frames',str(n//4),'--no-audio','--replay',fixture,
            '--highscore-file',profile,'--trace-output',fixed],env=env,check=True)
        fixed_state=read(fixed)
        for key in KEYS[:6]:assert fixed_state[key]==g[key],key
        saved=profile.read_bytes();records=read(profile)['records'];assert bytes(records[:10])==bytes.fromhex('00001583000041424300')
        assert hashlib.sha256(bytes(records)).hexdigest()==g['highscore_sha256'][-1]
        before=profile.stat()
        subprocess.run([a.launcher,'--data',ROOT/'build/imported/pirate-retail','--frames','1','--no-audio','--highscore-file',profile,'--trace-output',reload],env=env,check=True)
        r=read(reload);assert r['highscore_sha256']==[g['highscore_sha256'][-1]]*4
        after=profile.stat();assert saved==profile.read_bytes()and(before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
    report=dict(status='VERIFIED',source_case=case,source_fixture_sha256=sha(fixture),steps=n,original_vectors=10,
        real_wall_ms=(frames[-1][0]+frames[-1][1])/1e6,active_ms=active_ns/1e6,clamped_frames=clamped,frames=len(frames),video=timing['video'],renderer=timing['renderer'],
        milestones=[dict(tick=m['tick'],label=m['label'])for m in f['milestones']],audio_requests=len(events['events']),
        score=15830000,initials='ABC',private_profile_reload_exact=True,profile_not_rewritten=True,
        screenshot_sha256=sha(work/'final.bmp'),scope='Real-clock input replay,actualGPU/audio; 200Hz original simulation,full10vectors andrequest stream exact. No physical keyboard/audio listening or whole original raster parity claim.')
    (a.output or ROOT/('analysis/traces/pirate-full-realtime.json'if case=='natural-crocodile-game'else f'analysis/traces/pirate-full-realtime-{case}.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(n,'real-clock steps/10original vectors/',len(events['events']),'audio requests/ABC/F1/persistent score PASS;',report['real_wall_ms'],'ms')
if __name__=='__main__':main()
