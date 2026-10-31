#!/usr/bin/env python3
"""Compare one synthetic looping STIM voice to the executed Retail resampler.

The actual x86 resampler runs at 44.1 kHz with 137-frame chunks and explicit
full volume. One normal-tuning sample, period 226 and a 12-byte forward loop
are repeated for five seconds. This isolates sample-position drift; it does
not exercise the game scheduler, note effects or physical audio output.
"""
import argparse
import hashlib
import json
import math
import os
import struct
import subprocess
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDI
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESI, UC_X86_REG_ESP
from verify_retail_tracker_pcm import EXE_SHA, GAME


def sha(b): return hashlib.sha256(b).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,required=True)
    p.add_argument('--library',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--expect-stable',action='store_true',help='Require stable correlation across the five-second loop')
    p.add_argument('--note',type=int,choices=(13,24,25,28),default=25)
    a=p.parse_args(); a.work.mkdir(parents=True,exist_ok=True)
    exe=(GAME/'SLAMTILT.EXE').read_bytes(); assert sha(exe)==EXE_SHA
    pe=pefile.PE(data=exe); image=pe.get_memory_mapped_image()
    u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
    u.mem_map(0x3000000,0xc0000);blocks=set()
    u.hook_add(UC_HOOK_BLOCK,lambda _u,addr,size,_d:blocks.add((addr,size)))
    def put(addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
    def run(address,eax,ebx=0,esi=0,edi=0):
        put(0x300f000,0x309fff0)
        for reg,value in ((UC_X86_REG_ESP,0x300f000),(UC_X86_REG_EAX,eax),
                          (UC_X86_REG_EBX,ebx),(UC_X86_REG_ESI,esi),(UC_X86_REG_EDI,edi)):
            u.reg_write(reg,value)
        u.emu_start(address,0x309fff0,count=2000000)
        assert u.reg_read(UC_X86_REG_EIP)==0x309fff0
    period={13:453,24:240,25:226,28:190}[a.note]
    sample=bytes((i*37+11)%256 for i in range(128)); freq=0x361f0f//period
    put(0x46eeb8,0x3010000);run(0x44b640,0x20000//6);u.mem_write(0x3020000,sample)
    for off,value in ((0,0x3020000),(4,128),(8,8),(12,12)):put(0x3002000+off,value)
    for off,value in ((0,0x3002000),(4,0),(8,0),(12,65536),(16,freq),(20,0xffffffff)):put(0x3001000+off,value)
    for off,value in ((0,0x3010000),(4,44100),(8,65536)):put(0x3003000+off,value)
    frames=44100*5
    for i in range(0,frames,137):run(0x44cc00,min(137,frames-i),0x3040000+2*i,0x3001000,0x3003000)
    reference=struct.unpack(f'<{frames}h',u.mem_read(0x3040000,frames*2))
    for addr,size in blocks:
        assert 0x401000<=addr and addr+size<=0x454000
        off=pe.get_offset_from_rva(addr-0x400000)
        assert bytes(u.mem_read(addr,size))==exe[off:off+size]
    # Minimal STIM with one note and a synthetic looping sample; no game data.
    stim=bytearray(406);stim[:4]=b'STIM';struct.pack_into('>HHH',stim,16,1,1,1)
    struct.pack_into('>I',stim,150,394)
    stim.extend(struct.pack('>4H',8,12,13,14)+bytes([1,a.note,0,0xbe,0xbf,0xbf,0xbf]))
    struct.pack_into('>I',stim,4,len(stim));stim.extend(bytes(4))
    stim.extend(struct.pack('>HBBHH',64,0,64,4,6));stim.extend(sample)
    bank=a.work/'synthetic-loop.stim';bank.write_bytes(stim)
    lib=a.library.absolute(); env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None)
    variants={}
    for name, venv in (('baseline',env),('experiment',dict(env,LD_LIBRARY_PATH=str(lib.parent)))):
        if name=='experiment':
            linkage=subprocess.check_output(['ldd',str(a.native.resolve())],env=venv,text=True)
            assert str(lib) in linkage
        data=subprocess.check_output([str(a.native.resolve()),str(bank),str(frames),'137','restart','0','retail'],env=venv)
        stereo=struct.unpack(f'<{frames*2}h',data);assert stereo[::2]==stereo[1::2]
        native=stereo[::2];seconds=[]
        for k in range(5):
            x=reference[k*44100:(k+1)*44100];y=native[k*44100:(k+1)*44100]
            xx=sum(v*v for v in x);yy=sum(v*v for v in y);assert xx and yy
            seconds.append({'second':k+1,'correlation':round(sum(v*w for v,w in zip(x,y))/math.sqrt(xx*yy),6),
                            'rms_ratio':round(math.sqrt(yy/xx),6),'exact_frames':sum(v==w for v,w in zip(x,y))})
        variants[name]=seconds
    # These checks preserve the measured drift; production parity is not claimed.
    assert variants['experiment'][0]['correlation']>0.98
    if a.expect_stable:
        assert min(x['correlation'] for x in variants['experiment']) > 0.99
    else:
        assert variants['experiment'][4]['correlation']<0.90
    report={'status':'EXPERIMENT_ONLY_STABLE_BOUNDED' if a.expect_stable else 'EXPERIMENT_ONLY_DRIFT_OBSERVED','scope':__doc__,'exe_sha256':EXE_SHA,
            'library_sha256':sha(lib.read_bytes()),'native_sha256':sha(a.native.read_bytes()),
            'synthetic_stim_sha256':sha(stim),'period':period,'frequency':freq,
            'loop_start':8,'loop_length':12,'frames':frames,'original_blocks':len(blocks),
            'original_pcm_sha256':sha(struct.pack(f'<{frames}h',*reference)),'variants':variants}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: 5-second synthetic loop; Original/native comparison recorded')

if __name__=='__main__':main()
