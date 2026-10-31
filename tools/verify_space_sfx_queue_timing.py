#!/usr/bin/env python3
"""Execute Retail Space SFX queue/consumer with controlled descriptor mutation.

The state and mutation are synthetic; this does not establish that a live
Space event mutates a queued descriptor or prove complete playback parity.
"""
import argparse, hashlib, json, struct
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_BLOCK
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_EBX, UC_X86_REG_EIP, UC_X86_REG_ESP
ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
CONTEXT=ROOT/'build/oracle/space-full-game'
EXE_SHA='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_SHA='18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b'
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 exe=(GAME/'SLAMTILT.EXE').read_bytes();image=(CONTEXT/'human-image.bin').read_bytes();dat=(CONTEXT/'human-dat.bin').read_bytes();summary=json.loads((CONTEXT/'summary.json').read_text())
 assert sha(exe)==EXE_SHA==summary['build_sha256'] and sha(dat)==DAT_SHA==summary['dat_sha256'] and sha(image)==summary['context_hashes']['human-image.bin']
 profiles=json.loads((ROOT/'analysis/space-audio-reuse.json').read_text())['sample_profiles'];assert len(profiles)==10
 pe=pefile.PE(data=exe);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,dat);u.mem_map(0x3000000,0x10000);blocks=set()
 u.hook_add(UC_HOOK_BLOCK,lambda uc,addr,size,d: blocks.add((addr,size)))
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def run(a,eax=0,edx=0,ebx=0):
  put(0x300f000,0x300fff0)
  for reg,val in ((UC_X86_REG_ESP,0x300f000),(UC_X86_REG_EAX,eax),(UC_X86_REG_EDX,edx),(UC_X86_REG_EBX,ebx)):u.reg_write(reg,val)
  u.emu_start(a,0x300fff0,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x300fff0
 rows=[]
 for profile in profiles:
  descriptor=int(profile['descriptor'],0);period=profile['period'];offset=int(profile['offset'],0);length=profile['length']
  assert sha(dat[offset:offset+length])==profile['pcm_sha256']
  for mutated in (False,True):
   u.mem_write(0x400000,image)
   for addr,val in ((0x46c72c,0x46b2a4),(0x46b2d4,0),(0x46b374,0),(0x46b394,0),(0x46b3a0,10),(0x46757c,0x1100000)):put(addr,val)
   assert (get(descriptor+4),get(descriptor+8))==(period,64)
   run(0x406600,descriptor,9,8);assert get(0x46b2d4)==descriptor
   if mutated:put(descriptor+4,period+1);put(descriptor+8,32)
   run(0x401760);state=[get(0x46b358+4*i) for i in range(8)]
   expected=[1,0x1100000+offset,length,0,0,period+int(mutated),32 if mutated else 64,8]
   assert state==expected,(hex(descriptor),state,expected)
   assert get(0x46b2d4)==0
   rows.append({'descriptor':hex(descriptor),'synthetic_mutation':mutated,'period_consumed':state[5],'volume_consumed':state[6],'pcm_sha256':profile['pcm_sha256']})
 for addr,size in blocks:
  assert 0x401000<=addr and addr+size<=0x454000
  off=pe.get_offset_from_rva(addr-0x400000);assert image[addr-0x400000:addr-0x400000+size]==exe[off:off+size],hex(addr)
 report={'status':'VERIFIED_BOUNDED','scope':__doc__,'exe_sha256':EXE_SHA,'dat_sha256':DAT_SHA,'image_sha256':sha(image),'entries':['0x406600','0x401760'],'executed_original_blocks':len(blocks),'cases':rows,'conclusion':'consumer reads descriptor period and volume at consumption; live mutation remains unverified'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS: 10 Space descriptors, 20 queue/consumer cases; late mutation consumed')
if __name__=='__main__':main()
