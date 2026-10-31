#!/usr/bin/env python3
"""Execute bounded original Retail audio requests and scheduler for an active upper cue.

The original music tracker is not executed here: synthetic flag 2 represents an
active upper cue. The test proves request/scheduler flag semantics only.
"""
import argparse, hashlib, json, struct
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_EIP, UC_X86_REG_ESP

ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
BUILD_SHA='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--output',type=Path,default=ROOT/'build/music-transitions/original-deferred.json')
 a=p.parse_args();raw=EXE.read_bytes();assert hashlib.sha256(raw).hexdigest()==BUILD_SHA
 image=pefile.PE(data=raw).get_memory_mapped_image()
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
 def put(address,value):u.mem_write(address,struct.pack('<I',value&0xffffffff))
 def get(address):return int.from_bytes(u.mem_read(address,4),'little')
 starts=[]
 def record(_u,address,_size,_user):starts.append(hex(address))
 u.hook_add(UC_HOOK_CODE,record,begin=0x44f138,end=0x44f138)
 def run(entry,eax=0,edx=0):
  put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000)
  u.reg_write(UC_X86_REG_EAX,eax);u.reg_write(UC_X86_REG_EDX,edx)
  u.emu_start(entry,0x100fff0,count=10000)
  assert u.reg_read(UC_X86_REG_EIP)==0x100fff0 and u.reg_read(UC_X86_REG_ESP)==0x100f004
 for address,value in [(0x454a58,0),(0x454a5c,0),(0x454a50,0),(0x454a54,0),
                       (0x454a60,0),(0x454a6c,2),(0x46756c,0x12345678)]:put(address,value)
 run(0x406240,50,1);assert (get(0x454a40),get(0x454a44),get(0x454a54),get(0x454a6c))==(1,50,0xffffffff,2)
 run(0x40634c);assert (get(0x454a54),get(0x454a6c),get(0x46756c))==(0xffffffff,2,0x12345678)
 deferred={'service':'0x84','bank':1,'order':50,'pending':'0xffffffff','active_flags':2,'tracker_start_calls':len(starts)}
 run(0x406268);run(0x40634c)
 assert (get(0x454a54),get(0x454a60),get(0x454a6c),get(0x46756c))==(0,0xffffffff,2,0x12345678)
 assert not starts,starts
 canceled={'service':'0x80','pending':0,'stop_lower':'0xffffffff','active_flags':2,'tracker_start_calls':len(starts)}
 report={'status':'VERIFIED_BOUNDED','original_build_sha256':BUILD_SHA,
         'addresses':['0x406240','0x406268','0x40634c'], 'deferred':deferred,'canceled':canceled,
         'scope':'Actual Retail x86 service entry and scheduler with synthetic active-88 flag; no tracker output or scheduler cadence.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
 print('Retail deferred 84 and lower 80 leave active 88 unchanged')
if __name__=='__main__':main()
