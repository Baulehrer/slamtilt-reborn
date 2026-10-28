#!/usr/bin/env python3
"""Retained original Nudge fields -> actual Retail viewport clipping/Blt RECT.

Only isolated presentation-context inputs are written. No gameplay is executed or
changed; waveform fields originate in the pinned existing original game traces.
"""
import hashlib,json,sys
from pathlib import Path
from unicorn.x86_const import UC_X86_REG_EBP,UC_X86_REG_ESP
from pirate_adventure_oracle import Original,ROOT


def main():
    m=Original(ROOT/'build/oracle/pirate-full-tick')
    pairs={};sources=[]
    for case in ['left','right','up']:
        path=ROOT/'build/oracle/pirate-modes'/('nudge-'+case)/'trace.json'
        t=json.loads(path.read_text())
        public=ROOT/'analysis/traces'/('pirate-nudge-'+case+'.json')
        expected=json.loads(public.read_text())['nudge_sha256']
        assert hashlib.sha256(json.dumps(t['nudge'],separators=(',',':')).encode()).hexdigest()==expected
        sources.append(dict(case=case,nudge_sha256=expected,fixture=str(public.relative_to(ROOT))))
        for tick,state in enumerate(t['nudge']):
            def signed(v):return v-(1<<32)if v>=1<<31 else v
            pairs.setdefault((signed(state[9]),signed(state[7])),dict(case=case,tick=tick))
    rows=[]
    for (horizontal,vertical),source in pairs.items():
        for camera in [0,100,200]:
            # Actual x87 render origin, including original signed16.16 truncation.
            # Equal previous/current camera isolates Nudge from follow interpolation.
            m.put(0x46c72c,0x46b2a4)
            for address,value in [(0x46c744,0),(0x46c688,camera),(0x454a94,camera),
                                  (0x46c5f4,horizontal),(0x46c4a4,vertical)]:
                m.put(address,value)
            m.run(0x405486,until=0x4054e1)
            render_origin=[m.get(0x46b2a4),m.get(0x46b2ac)]
            m.put(0x46b2c0,400)
            m.u.reg_write(UC_X86_REG_EBP,0)
            m.run(0x4035af,edx=200,until=0x4035fa)
            # Fixed destination320x400, 1x scale; force the full-rectangle path.
            m.put(0x46b2a8,0x7fffffff);m.put(0x46b2b0,0x7fffffff)
            for address,value in [(0x454a1c,1),(0x454a10,320),(0x454a18,0),(0x454a14,400),
                                  (0x468434,0x100e000),(0x100e000,0x100e100)]:
                m.put(address,value)
            m.run(0x402e58,until=0x402f24)
            esp=m.u.reg_read(UC_X86_REG_ESP)
            rect=lambda pointer:[m.get(pointer+offset)for offset in range(0,16,4)]
            src=rect(m.get(esp+12));dst=rect(m.get(esp+4))
            assert dst==[0,0,320,400],dst
            assert src[2]-src[0]==320 and src[3]-src[1]==400
            # Original backing buffer places table X0 at column8.
            rows.append(dict(camera_scroll=camera,horizontal_pixels=horizontal,
                vertical_fixed=vertical,source=source,original_render_origin=render_origin,original_source_rect=src,
                original_destination_rect=dst,origin=[8-src[0],-src[1]]))
    fixture=dict(schema=1,build_sha256='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6',
        prepared_image_sha256=hashlib.sha256((ROOT/'build/oracle/pirate-full-tick/human-image.bin').read_bytes()).hexdigest(),
        method='Actual405486..4054e1 x87 render origin,4035af..4035fa clipping and402e58..402f24 source/destination RECT execution; original retained Nudge states; isolated renderer context',
        maximum_scroll=200,sources=sources,cases=rows,limits=['Native camera follow curve remains its existing policy; only original Nudge source offset and clipping transferred.',
        'No complete original raster equality or physical host acceptance claimed.'])
    path=ROOT/'analysis/traces/pirate-nudge-presentation-original.json'
    path.write_text(json.dumps(fixture,separators=(',',':'))+'\n')
    print(len(rows),'actual original viewport RECT cases;',path.relative_to(ROOT))

if __name__=='__main__':main()
