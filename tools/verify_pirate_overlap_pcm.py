#!/usr/bin/env python3
"""Bounded real Pirate simultaneous SFX: Retail resampler versus native mixer.

The selected recorded requests use initial idle voices and simultaneous start;
actual device cadence, previous voices, tracker and final stereo mix are not tested.
"""
import argparse
import collections
import hashlib
import json
import struct
import subprocess
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_BLOCK
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_ESP, UC_X86_REG_EIP

ROOT = Path(__file__).resolve().parents[1]
BUILD_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_SHA = '6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6'
def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    fixture_path = ROOT/'analysis/traces/pirate-audio-events.json'
    fixture = json.loads(fixture_path.read_text())
    assert fixture['build_sha256'] == BUILD_SHA and fixture['dat_sha256'] == DAT_SHA
    case = next(c for c in fixture['cases'] if c['case'] == 'acceptance-nudge')
    groups = collections.defaultdict(list)
    for e in case['events']:
        if e[1] == 0x5c: groups[e[0]].append(e)
    group = next(v for v in groups.values() if len(v) == 2 and all(x[2:4] == [2,1] for x in v) and v[0][4] != v[1][4])
    meta = json.loads((ROOT/'analysis/pirate-audio-static.json').read_text())
    profiles = {int(x['address'],0):x for x in meta['sfx_descriptors']}
    assert all(e[4] in profiles for e in group)
    game = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    exe = (game/'SLAMTILT.EXE').read_bytes(); dat_path = game/'DAT/PIRATE.DAT'; dat = dat_path.read_bytes()
    assert sha(exe)==BUILD_SHA and sha(dat)==DAT_SHA
    pe=pefile.PE(data=exe); image=pe.get_memory_mapped_image()
    u=Uc(UC_ARCH_X86,UC_MODE_32); u.mem_map(0x400000,0x100000); u.mem_write(0x400000,image)
    u.mem_map(0x3000000,0x90000); blocks=set()
    u.hook_add(UC_HOOK_BLOCK, lambda _u, addr, size, _: blocks.add((addr,size)))
    def put(addr,v): u.mem_write(addr,struct.pack('<I',v & 0xffffffff))
    def run(addr,eax=0,ebx=0,esi=0,edi=0):
        put(0x300f000,0x308fff0)
        for reg,v in ((UC_X86_REG_ESP,0x300f000),(UC_X86_REG_EAX,eax),(UC_X86_REG_EBX,ebx),(UC_X86_REG_ESI,esi),(UC_X86_REG_EDI,edi)): u.reg_write(reg,v)
        u.emu_start(addr,0x308fff0,count=2000000)
        assert u.reg_read(UC_X86_REG_EIP)==0x308fff0
    put(0x46eeb8,0x3010000);run(0x44b640,0x20000//6)
    for off,val in ((0,0x3010000),(4,44100),(8,65536)): put(0x3003000+off,val)
    specs=[]
    for i,event in enumerate(group):
        d=profiles[event[4]]; off=int(d['pcm_offset'],0); length=d['length']; period=d['period']; volume=64
        assert sha(dat[off:off+length])==d['pcm_sha256']
        words=struct.unpack_from('<9I',image,event[4]-0x400000)
        assert words[1:4] == (period,volume,length)
        sample_addr=0x3040000+i*0x20000; voice=0x3001000+i*0x20; entry=0x3002000+i*8
        u.mem_write(sample_addr,dat[off:off+length]);put(entry,sample_addr);put(entry+4,length)
        for delta,val in ((0,entry),(4,0),(8,0),(12,volume<<10),(16,0x361f0f//period),(20,0)):put(voice+delta,val)
        specs.append((off,length,period,volume))
    cases=[]
    for frames in (1,221,2048,30000):
        # Restart both voices so the selected traces are deterministic per length.
        for i in range(2):
            put(0x3001000+i*0x20+4,0);put(0x3001000+i*0x20+8,0)
        u.mem_write(0x3030000,bytes(frames*2))
        for i in range(2):run(0x44cc00,frames,0x3030000,0x3001000+i*0x20,0x3003000)
        original=bytes(u.mem_read(0x3030000,frames*2))
        native=subprocess.check_output([str(a.native.resolve()),str(dat_path),*[str(x) for spec in specs for x in spec],str(frames)])
        assert native==original, frames
        cases.append({'frames':frames,'pcm_sha256':sha(original)})
    for addr,size in blocks:
        off=pe.get_offset_from_rva(addr-0x400000)
        assert bytes(u.mem_read(addr,size))==exe[off:off+size]
    report={'status':'VERIFIED_BOUNDED','scope':__doc__,'exe_sha256':BUILD_SHA,'dat_sha256':DAT_SHA,
            'fixture_sha256':sha(fixture_path.read_bytes()),'native_sha256':sha(a.native.read_bytes()),
            'case':case['case'],'tick':group[0][0],'events':group,'cases':cases,'executed_original_blocks':len(blocks)}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: Pirate simultaneous two-voice Original/native PCM, four lengths')
if __name__=='__main__': main()
