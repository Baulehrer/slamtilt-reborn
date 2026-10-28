#!/usr/bin/env python3
"""Natural three-Cave-lock finite game, initials and next game; no waypoints.

Frozen native policy candidate is independently executed in original Retail,
then replayed again from reset. Only Enter/Shift, admitted initials and F1.
"""
import json
from pirate_multiball_oracle import Multiball
from pirate_adventure_oracle import ROOT,BUILD_SHA,compact

CASE='legal-cave-game'
class Legal(Multiball):
    @staticmethod
    def apply_input(m,e):
        if e['action']in ('enter','left','right'):return Multiball.apply_input(m,e)
        if not e['down']:return
        if e['action']=='key':
            assert m.get(0x46c6ac)==3 and m.get(0x46c61c)==6;m.run(0x405d54,e['scan'])
        elif e['action']=='new_game':assert m.get(0x46c6ac)==0;m.run(0x408ae0,1)
        else:raise ValueError(e)
    def mark(self,label):
        v=super().mark(label);v.update(highscore_hex=bytes(self.m.u.mem_read(0x46c542,50)).hex());return v
    def event(self,action,down=True,**kw):
        e=dict(tick=self.tick,action=action,down=down,**kw);self.inputs.append(e);self.apply_input(self.m,e)

def main():
    source=json.loads((ROOT/'build/oracle/pirate-legal-cave/candidate.json').read_text());assert source['diagnostic_shots']==[] and source['tick_count']==8000
    r=Legal(0);keys={};g=r.m.get
    for e in source['inputs']:keys.setdefault(e['tick'],[]).append(e)
    native_marks={e['tick']:e for e in source['policy']['milestones']};old_locks=0;held={'left':False,'right':False}
    for tick in range(source['tick_count']):
        for e in keys.get(tick,[]):
            r.inputs.append(e);r.apply_input(r.m,e)
            if e['action']in held:held[e['action']]=e['down']
        r.step()
        if r.tick in native_marks:
            p=native_marks[r.tick];player=g(0x46b758)
            assert [g(0x46c6ac),g(0x46e2bc,2),g(0x46e2be,2),g(player+14,2),g(0x46c67c)]==[p[k]for k in ['phase','locks','played','ball_number','ball_count']],('native candidate milestone',r.tick)
        locks=g(0x46e2bc,2)
        if locks!=old_locks:r.mark('natural_lock_'+str(locks));old_locks=locks
    assert g(0x46e2bc,2)==3
    for side,down in held.items():
        if down:r.event(side,False)
    r.mark('policy_end');entered=False;letters=[0x1e,0x30,0x2e,0x1c]
    while g(0x46c6ac)!=0:
        if g(0x46c6ac)==3 and g(0x46c61c)==6:
            if not entered:r.mark('initials_admitted');entered=True
            if r.tick%4==0 and letters:r.event('key',scan=letters.pop(0))
        r.step();assert r.tick<16000,'finite game did not end'
    assert entered and not letters;r.mark('game_over')
    frozen=r.m.ball();records=bytes(r.m.u.mem_read(0x46c542,50))
    for _ in range(64):r.step();assert g(0x46c6ac)==0 and r.m.ball()==frozen
    r.mark('game_over_stable');r.event('new_game');r.mark('new_game')
    assert g(0x46e2bc,2)==0 and bytes(r.m.u.mem_read(0x46c542,50))==records
    for _ in range(1200):
        if g(0x46c6ac)==1 and r.tick%200==0:r.event('enter');r.event('enter',False)
        r.step()
    while g(0x46c1b4,2)!=2:
        r.step();assert r.tick<16000,'second game free ball missing'
    r.mark('second_game_running');assert g(0x46c6ac)==2 and g(0x46c1b4,2)==2
    t=r.finish(CASE);t.update(scope=__doc__,source_policy=source['policy'],diagnostic_shots=[],key_only=True,
        call_edge_coverage='Existing compiled context plus original full steps; no broad call hooks in waits.')
    (ROOT/f'build/oracle/pirate-modes/{CASE}/trace.json').write_bytes(compact(t)+b'\n')
    p=ROOT/f'analysis/traces/pirate-{CASE}.json';f=json.loads(p.read_text())
    for k in ['scope','source_policy','key_only','call_edge_coverage']:f[k]=t[k]
    p.write_text(json.dumps(f,indent=2)+'\n')
if __name__=='__main__':main()
