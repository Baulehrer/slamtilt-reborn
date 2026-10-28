#!/usr/bin/env python3
"""Bounded original Retail gain-LUT44b640 + one-shot resampler44cc00 PCM.

Explicit six-voice/full64/master65536/SFX10 fixture. Final stereo mixer/device,
tracker and the active machine's mixer settings are outside this proof.
"""
import hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
image=(ROOT/'build/oracle/pirate-full-tick/human-image.bin').read_bytes()
dat=(ROOT/'build/oracle/pirate-full-tick/human-dat.bin').read_bytes()
meta=json.loads((ROOT/'analysis/pirate-audio-static.json').read_text())
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
u.mem_map(0x3000000,0x60000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return int.from_bytes(u.mem_read(a,4),'little')
def run(start,eax=0,ebx=0,esi=0,edi=0):
    put(0x300f000,0x305fff0);u.reg_write(UC_X86_REG_ESP,0x300f000)
    for r,v in [(UC_X86_REG_EAX,eax),(UC_X86_REG_EBX,ebx),(UC_X86_REG_ESI,esi),(UC_X86_REG_EDI,edi)]:u.reg_write(r,v)
    u.emu_start(start,0x305fff0,count=2000000)
    assert u.reg_read(UC_X86_REG_EIP)==0x305fff0
put(0x46eeb8,0x3010000);run(0x44b640,0x20000//6)
put(0x3002000,0x3020000)
put(0x3003000,0x3010000);put(0x3003004,44100);put(0x3003008,65536)
def fnv(data):
    h=14695981039346656037
    for v in data:h=((h^v)*1099511628211)&0xffffffffffffffff
    return str(h)
cases=[]
for d in meta['sfx_descriptors']:
    start=int(d['pcm_offset'],16);length=d['length'];pcm=dat[start:start+length];u.mem_write(0x3020000,pcm)
    for frames in [1,221,2048,30000]:
        put(0x3002004,length)
        frequency=0x361f0f//d['period']
        for offset,value in [(0,0x3002000),(4,0),(8,0),(12,65536),(16,frequency),(20,0)]:put(0x3001000+offset,value)
        u.mem_write(0x3030000,bytes(frames*2));run(0x44cc00,frames,0x3030000,0x3001000,0x3003000)
        actual=bytes(u.mem_read(0x3030000,frames*2));step=((frequency<<32)//44100)&~15
        expected=bytearray()
        for f in range(frames):
            index=(f*step)>>32;v=pcm[index]if index<length else 0;signed=v if v<128 else v-256
            expected.extend(struct.pack('<h',(signed*(0x20000//6)*127)>>16))
        assert actual==expected,(d['address'],frames)
        cases.append(dict(descriptor=int(d['address'],16),frames=frames,pcm_fnv64=fnv(actual)))
result=dict(image_sha256=hashlib.sha256(image).hexdigest(),dat_sha256=hashlib.sha256(dat).hexdigest(),
    scope=__doc__,cases=cases)
(ROOT/'analysis/traces/pirate-audio-pcm.json').write_text(json.dumps(result,indent=2)+'\n')
print(len(cases),'original Pirate mono PCM cases exact')
