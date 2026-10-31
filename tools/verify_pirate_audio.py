#!/usr/bin/env python3
"""Pirate audio: original service-entry events vs native/reset/SDL, cached evidence.

--refresh replays retained diagnostic/finite trajectories in original x86 code.
No sound-state writes, no audio-device emulation; original mixer PCM is excluded.
"""
from retail_audio_fixture import corrected_audio_events
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'analysis/traces/pirate-audio-events.json'
DAT=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT'
SERVICES={0x406600:0x5c,0x406268:0x80,0x406240:0x84,0x40621c:0x88,0x4061f8:0x8c,0x4061c4:0x90}
CASES=['plank-super-feedback','piranha-chain','bonus-multiplier-ladder','acceptance-nudge','acceptance-tilt','acceptance-multiball','complete-game','final-campaign','campaign-finite','campaign-magnets','magna-award-0','magna-award-1','magna-award-2',
       'magna-award-3','magna-award-4','magna-award-5','magna-award-6',
       'magna-award-7','magna-award-8','magna-award-9','magna-award-10','magna-award-11','multiball-surplus','magna-mode-lit','magna-bonus-held','magna-kickback-lit','magna-all-played','magna-key-reward','locks-crocodile-3','locks-crocodile-4','locks-storm-4','legal-cave-game','natural-crocodile-game','natural-plank-game','natural-plank-rope','natural-plank-two-ropes','natural-plank-nudge','feedback-sword','feedback-dive','feedback-monkey','legal-feedback-42e140',
       *['legal-feedback-'+target for target in ['406650','42c514','42cf8c','42dbb4','42dd00','42e2f8','42f44c','42e478','42e718','42d640']],
       *['final-feedback-'+case for case in ['threshold','left-feature','multiplier','kickback']],
       *['magnasaver-'+case for case in ['force-off','force-on','retrigger','rearm','tilt-armed','tilt-active','save-return']],
       *['magna-capture-'+case for case in ['trigger-edge','exit-edge','cooldown','tilt-free','tilt-held','admit-last','admit-late']],
       *['nudge-'+c for c in ['left','right','up','warning','decay','prelaunch','tilt-game','tilt-knife','tilt-magna','tilt-crocodile','tilt-held-magna','tilt-held-crocodile']]]

def read(path):return json.loads(path.read_text())
def sha(data):return hashlib.sha256(data).hexdigest()
def signed(v):return v if v<0x80000000 else v-0x100000000

def refresh(extend=False):
    from pirate_adventure_oracle import Original,BUILD_SHA,DAT_SHA
    from unicorn import UC_HOOK_CODE
    from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_EBX
    previous=read(FIXTURE)if FIXTURE.exists()else None
    rows=[]
    cached={r['case']:r for r in previous['cases']}if previous and extend else{}
    if cached:assert previous['build_sha256']==BUILD_SHA and previous['dat_sha256']==DAT_SHA
    for case in CASES:
        path=ROOT/'analysis/traces'/('pirate-'+case+'.json');f=read(path)
        if case in cached and cached[case]['replay_sha256']==sha(path.read_bytes()):
            row=cached[case];assert row['tick_count']==f['tick_count']
            rows.append(row);continue
        m=Original(ROOT/'build/oracle/pirate-full-tick');tick=0
        if any(e['action']=='special_left' for e in f['inputs']):
            # Same executed Retail default-key prefix as the source fixture.
            m.run(0x40df1e,until=0x40df5f)
        # Existing diagnostic fixture adapters bind the original Shift scan codes.
        if case!='complete-game':m.put(0x46c5dc,0x2a);m.put(0x46c5e0,0x36)
        if any(e['action'].startswith('nudge_')for e in f['inputs']):m.put(0x46c5ec,0x38);m.put(0x46c5f0,0xb8)
        events=[[0,0x90,m.get(0x454a68),m.get(0x454a64),0]]
        def capture(u,pc,size,_):
            service=SERVICES[pc];a=u.reg_read(UC_X86_REG_EAX);d=u.reg_read(UC_X86_REG_EDX);b=u.reg_read(UC_X86_REG_EBX)
            if service==0x5c:events.append([tick,service,signed(d),signed(b),a])
            elif service in (0x80,0x8c):events.append([tick,service,0,0,0])
            else:events.append([tick,service,signed(d),signed(a),0])
        for pc in SERVICES:m.u.hook_add(UC_HOOK_CODE,capture,begin=pc,end=pc)
        inputs={};shots={}
        for e in f['inputs']:inputs.setdefault(e['tick'],[]).append(e)
        for e in f.get('diagnostic_shots',[]):shots.setdefault(e['tick'],[]).append(e)
        for tick in range(f['tick_count']):
            for e in inputs.get(tick,[]):
                if e['action'] in ('left','right','enter','nudge_left','nudge_right','nudge_up','special_left'):
                    m.run(0x40404c,0 if e['down']else 1,{'left':0x2a,'right':0x36,'enter':0x1c,'nudge_left':0x38,'nudge_right':0xb8,'nudge_up':0x39,'special_left':0x1d}[e['action']])
                elif e['down']:
                    if e['action']=='key':m.run(0x405d54,e['scan'])
                    elif e['action']=='new_game':m.run(0x408ae0,1)
                    else:raise AssertionError(e)
            for e in shots.get(tick,[]):
                assert m.get(0x46c15c+100*e.get('ball',0)+0x58,2)==2,(case,tick,e)
                m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
            m.step(tick)
        if case=='complete-game':
            old=read(ROOT/'build/oracle/pirate-complete-game-lamps-ready/trace.json')
        else:old=read(ROOT/'build/oracle/pirate-modes'/case/'trace.json')
        assert m.ball()==old['states'][-1],(case,'ball state')
        if 'timing' in old:assert m.timing()==old['timing'][-1],case
        assert m.sample()['lifecycle']==old['lifecycle'][-1],case
        rows.append(dict(case=case,tick_count=f['tick_count'],replay=str(path.relative_to(ROOT)),
            replay_sha256=sha(path.read_bytes()),events=events,
            final_ball_pool_sha256=m.sample()['ball_pool_sha256'],
            final_rule_sha256=m.sample()['rule_sha256']))
        print(case,len(events),'original events',flush=True)
    data=dict(schema=1,build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,
      services={hex(k):hex(v)for k,v in SERVICES.items()},
      startup='Synthetic delivery of retained original base request454a64/68 (0/0); not a new original service call.',
      scope='Original service-entry register observations; retained finite/diagnostic trajectories; excludes original audio device/mixer PCM and wall-clock synchronization.',cases=rows)
    if previous:
        by_case={row['case']:row for row in rows}
        for row in previous['cases']:
            if by_case[row['case']]['replay_sha256']==row['replay_sha256']:
                assert by_case[row['case']]==row,(row['case'],'retained audio evidence changed')
    FIXTURE.write_text(json.dumps(data,separators=(',',':'))+'\n')
    return data

def main():
    global FIXTURE,CASES
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--all-sdl-cases',action='store_true');ap.add_argument('--fixture',type=Path);ap.add_argument('--cases',nargs='+');ap.add_argument('--work',type=Path);ap.add_argument('--refresh',action='store_true');ap.add_argument('--extend',action='store_true',help='Reuse SHA-pinned retained original event rows during refresh');ap.add_argument('--native',type=Path)
    ap.add_argument('--viewer',type=Path);a=ap.parse_args()
    if a.extend and not a.refresh:ap.error('--extend requires --refresh')
    if a.fixture:FIXTURE=a.fixture
    if a.cases:CASES=a.cases
    data=refresh(a.extend)if a.refresh else read(FIXTURE)
    assert sha(DAT.read_bytes())==data['dat_sha256']
    work=a.work or ROOT/'build/oracle/pirate-audio';work.mkdir(parents=True,exist_ok=True)
    if a.native:
        subprocess.run([a.native,ROOT/'build/oracle/pirate-full-tick',DAT,FIXTURE,work/'native.json'],check=True,cwd=ROOT,env=dict(os.environ,SDL_AUDIODRIVER='dummy'))
    if a.viewer:
        for row in [r for r in data['cases'] if a.all_sdl_cases or r['case'] in ('bonus-multiplier-payout','plank-super-feedback','piranha-chain','bonus-multiplier-ladder','acceptance-multiball','complete-game','final-campaign','nudge-tilt-game','nudge-tilt-held-magna','final-feedback-left-feature','magnasaver-tilt-active','magna-capture-tilt-held','magna-capture-cooldown','campaign-finite','campaign-magnets')]:
            path=ROOT/row['replay'];assert sha(path.read_bytes())==row['replay_sha256']
            output=work/(row['case']+'-sdl.json')
            cmd=[a.viewer,DAT,'--pirate-play',ROOT/'build/oracle/pirate-full-tick','--frames',str(row['tick_count']//4),
                 '--replay',path,'--audio-trace',output]
            if row['case']!='complete-game':cmd+=['--diagnostic-shots',path]
            subprocess.run(cmd,check=True,cwd=ROOT,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
            actual=read(output);assert actual['events']==corrected_audio_events(row['events'], 'pirate'),(row['case'],'SDL events')
            assert actual['enabled']and actual['queued_bytes']>0 and actual['error']=='',actual
        output=work/'frontend.json'
        subprocess.run([a.viewer,DAT,'--pirate-play',ROOT/'build/oracle/pirate-full-tick','--frames','14','--audio-acceptance',output],
            check=True,cwd=ROOT,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
        assert read(output)['passed']
    print(len(data['cases']),'Pirate original/native/reset/audio cases; SDL checked'if a.viewer else'Pirate audio evidence cases')
if __name__=='__main__':main()
