#!/usr/bin/env python3
"""Bounded original camera math, sequential frame inputs and x87 interpolation."""
import json
from pirate_adventure_oracle import ROOT,Original,BUILD_SHA

def main():
    m=Original(ROOT/'build/oracle/pirate-full-tick');context=0x1007000
    m.put(0x46c72c,context);m.put(context+0x10,200);m.put(context+0x1c,400)
    for a,v in [(0x46c688,0),(0x454a94,0),(0x454d8c,0),(0x454d90,0),(0x454a98,0),(0x454a9c,1)]:m.put(a,v)
    rows=[]
    # Reuse real natural multiball positions. Original camera input is the last
    # rendered projected WORD Y; freeze each group of four simulation steps.
    t=json.loads((ROOT/'build/oracle/pirate-modes/acceptance-multiball/trace.json').read_text())
    for tick in range(9000):
        s=t['states'][tick//4*4];y=int.from_bytes(bytes(s[12:16]),'little',signed=True)//65536-7
        phase=t['lifecycle'][max(0,tick-1)][0]
        balls=[dict(y=y,state=int.from_bytes(bytes(s[88:90]),'little'))]
        # Explicit camera-context branches; these are synthetic presentation
        # inputs, not claims of earned gameplay or physical multiball states.
        if 7000<=tick<7200:balls=[dict(y=580,state=6),dict(y=120,state=2)]
        if 7200<=tick<7400:balls=[dict(y=580,state=6),dict(y=120,state=6)]
        if 7400<=tick<7600:balls=[]
        if tick>=7600:phase=0
        m.put(0x46c6ac,phase);m.put(0x46c67c,len(balls))
        for i,b in enumerate(balls):
            address=0x46c15c+100*i;m.put(0x454b68+4*i,address)
            m.put(address+0x10,(b['y']&65535)<<16);m.put(address+0x58,b['state'],2)
        m.run(0x409350)
        state=[m.get(a)for a in [0x46c688,0x454a94,0x454d8c,0x454d90,0x454a98,0x454a9c]]
        state=[v if v<0x80000000 else v-0x100000000 for v in state]
        scroll=[]
        for residual in range(5):
            m.put(0x46c744,residual);m.put(0x46c4a4,0);m.put(0x46c5f4,0)
            m.run(0x405486,until=0x4054e1);scroll.append(m.get(context+8))
        rows.append(dict(phase=phase,balls=balls,state=state,scroll=scroll))
    path=ROOT/'analysis/traces/pirate-camera-original.json'
    path.write_text(json.dumps(dict(schema=1,build_sha256=BUILD_SHA,original_addresses=['0x409350','0x405486'],
        scope='Actual original sequential camera and x87 interpolation; real natural-ball-derived projected input plus explicit synthetic state6/empty/GameOver presentation cases. No whole original raster/gameplay-coupling claim.',cases=rows),separators=(',',':'))+'\n')
    print(len(rows),'sequential original camera cases /',len(rows)*5,'x87 interpolation observations')
if __name__=='__main__':main()
