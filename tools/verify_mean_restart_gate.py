#!/usr/bin/env python3
"""Replay bounded408915 branch/41b1f8 decrement; --oracle regenerates x86 evidence."""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'analysis/traces/mean-restart-gate-original.json'
def oracle():
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
 image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
 for a,v in [(0x43e740,0x1001000),(0x1001004,0x1001100),(0x1001108,0x1001200),(0x1001210,0x1000600),(0x100f000,0x100fff0)]:put(a,v)
 result={}
 def hook(uc,a,n,c):
  if a==0x1000600:
   result['decision']=1
   sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,struct.unpack('<I',uc.mem_read(sp,4))[0]);uc.reg_write(UC_X86_REG_ESP,sp+4)
  if a in [0x408949,0x408a0e,0x41b1fb]:
   if a==0x408a0e:result['decision']=2
   uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 cases=[]
 for op in [0,1]:
  for gate in [-2147483648,-2,-1,0,1,2,2147483647]:
   for state in [0,1,2,4,5,7,0xfffe,0xffff]:
    put(0x43e79c,gate);result.clear();result['decision']=0
    u.reg_write(UC_X86_REG_EDX,0x43e770 if op else 0x1001400);u.reg_write(UC_X86_REG_EAX,-1 if state==0xffff else state);u.reg_write(UC_X86_REG_ESP,0x100f000)
    u.emu_start(0x41b1f8 if op else 0x408915,0,count=40)
    cases.append(dict(op=op,gate=gate,state=state,decision=result['decision'],final_gate=get(0x43e79c)))
 PATH.write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual408915..408943 and41b1f8; initializer callback stubbed, exit continues outside bounded scope',cases=cases),indent=2)+'\n')
 return cases
p=argparse.ArgumentParser();p.add_argument('--oracle',action='store_true');p.add_argument('--native');a=p.parse_args()
cases=oracle() if a.oracle else json.loads(PATH.read_text())['cases']
if a.native:
 raw=''.join(f"{c['op']} {c['gate']} {c['state']}\n" for c in cases)
 lines=subprocess.check_output([a.native],input=raw,text=True).splitlines()
 assert len(lines)==len(cases)
 differences=[i for i,(c,line) in enumerate(zip(cases,lines)) if list(map(int,line.split()))!=[c['decision'],c['final_gate']]]
 assert not differences,differences
print(json.dumps(dict(cases=len(cases),differences=0)))
