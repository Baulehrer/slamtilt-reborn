#!/usr/bin/env python3
"""Compare 65 synthetic STIM voice volumes with the Retail x86 resampler.

Uses one synthetic 8-bit sample and forward loop, fixed period 226 and a
manually initialized six-voice gain LUT. It does not prove whole-game audio.
"""
import argparse,hashlib,json,os,struct,subprocess
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_HOOK_BLOCK,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_EDI,UC_X86_REG_EIP,UC_X86_REG_ESI,UC_X86_REG_ESP
from verify_retail_tracker_pcm import EXE_SHA,GAME
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--native',type=Path,required=True);p.add_argument('--library',type=Path,required=True)
p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
exe=(GAME/'SLAMTILT.EXE').read_bytes();assert hashlib.sha256(exe).hexdigest()==EXE_SHA
pe=pefile.PE(data=exe);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,pe.get_memory_mapped_image());u.mem_map(0x3000000,0xc0000);blocks=set()
u.hook_add(UC_HOOK_BLOCK,lambda _u,addr,size,_d:blocks.add((addr,size)))
def put(addr,v):u.mem_write(addr,struct.pack('<I',v&0xffffffff))
def run(addr,eax,ebx=0,esi=0,edi=0):
 put(0x300f000,0x309fff0)
 for reg,val in ((UC_X86_REG_ESP,0x300f000),(UC_X86_REG_EAX,eax),(UC_X86_REG_EBX,ebx),(UC_X86_REG_ESI,esi),(UC_X86_REG_EDI,edi)):u.reg_write(reg,val)
 u.emu_start(addr,0x309fff0,count=2000000);assert u.reg_read(UC_X86_REG_EIP)==0x309fff0
sample=bytes((i*37+11)%256 for i in range(128));put(0x46eeb8,0x3010000);run(0x44b640,0x20000//6);u.mem_write(0x3020000,sample)
for off,val in ((0,0x3020000),(4,128),(8,8),(12,12)):put(0x3002000+off,val)
for off,val in ((0,0x3010000),(4,44100),(8,65536)):put(0x3003000+off,val)
library=a.library.absolute();env=dict(os.environ,LD_LIBRARY_PATH=str(library.parent));assert str(library) in subprocess.check_output(['ldd',str(a.native.resolve())],env=env,text=True)
cases=[]
for vol in range(65):
 for off,val in ((0,0x3002000),(4,0),(8,0),(12,vol*1024),(16,0x361f0f//226),(20,0xffffffff)):put(0x3001000+off,val)
 u.mem_write(0x3040000,bytes(882*2));run(0x44cc00,882,0x3040000,0x3001000,0x3003000)
 ref=struct.unpack('<882h',u.mem_read(0x3040000,882*2))
 stim=bytearray(406);stim[:4]=b'STIM';struct.pack_into('>HHH',stim,16,1,1,1);struct.pack_into('>I',stim,150,394)
 stim.extend(struct.pack('>4H',8,12,13,14)+bytes([1,25,0,0xbe,0xbf,0xbf,0xbf]));struct.pack_into('>I',stim,4,len(stim));stim.extend(bytes(4));stim.extend(struct.pack('>HBBHH',64,0,vol,4,6));stim.extend(sample)
 path=a.work/'synthetic.stim';path.write_bytes(stim)
 pcm=subprocess.check_output([str(a.native.resolve()),str(path),'882','137','restart','0','retail'],env=env);vals=struct.unpack('<1764h',pcm)
 assert vals[::2]==vals[1::2]
 differences=sum(x!=y for x,y in zip(ref,vals[::2]))
 cases.append({'volume':vol,'different_frames':differences,'original_sha256':hashlib.sha256(struct.pack('<882h',*ref)).hexdigest()})
for addr,size in blocks:
 assert 0x401000<=addr and addr+size<=0x454000
 off=pe.get_offset_from_rva(addr-0x400000);assert bytes(u.mem_read(addr,size))==exe[off:off+size]
assert not any(r['different_frames'] for r in cases),[(r['volume'],r['different_frames']) for r in cases if r['different_frames']]
report={'status':'VERIFIED_BOUNDED','scope':__doc__,'exe_sha256':EXE_SHA,'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'frames':882,'cases':cases,'original_blocks':len(blocks)}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
print('PASS: all 65 synthetic volumes match Original PCM exactly')
