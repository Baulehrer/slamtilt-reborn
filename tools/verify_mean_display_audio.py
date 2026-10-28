#!/usr/bin/env python3
"""Exact405f98 admitted/rejected display request audio command effects."""
import hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
cases=[];expected=[]
for old,order,bank,flags,accepted in itertools.product([0,1,2,4,5],[-32768,-1,0,1,14,47,62,32767],[0,1,2],range(4),[False,True]):
 # Actualadmission gate plus priority; mode2 isactivegame,mode3rejects.
 put(0x43e7a0,2 if accepted else 3);put(0x43e780,old);put(0x43e788,1);put(0x43e7b0,1)
 put(0x4297cc,flags)
 for a,v in [(0x4297ac,0x12345678),(0x4297a8,0x23456789),(0x4297b8,0x3456789a),(0x4297bc,0x456789ab)]:put(a,v)
 sp=0x100f000;put(sp,0x100fff0);put(sp+4,order);put(sp+8,bank);put(sp+12,0x412d24)
 for reg,value in [(UC_X86_REG_ESP,sp),(UC_X86_REG_EAX,8),(UC_X86_REG_EDX,7),(UC_X86_REG_ECX,2),(UC_X86_REG_EBX,0)]:u.reg_write(reg,value)
 u.emu_start(0x405f98,0x100fff0,count=100)
 assert u.reg_read(UC_X86_REG_EIP)==0x100fff0
 admitted=u.reg_read(UC_X86_REG_EAX)!=0
 assert admitted==accepted
 if get(0x4297b8)==0xffffffff:
  assert get(0x4297bc)==0
  command=dict(service=0x88,bank=get(0x4297a8),order=get(0x4297ac))
 elif get(0x4297b8)==0 and get(0x4297bc)==0xffffffff:
  command=dict(service=0x8c,bank=0,order=0)
 else:
  assert [get(a) for a in [0x4297ac,0x4297a8,0x4297b8,0x4297bc]]==[0x12345678,0x23456789,0x3456789a,0x456789ab]
  command=dict(service=0,bank=0,order=0)
 cases.append(dict(old780=old,stack0=order,stack1=bank,admitted=admitted,flags=flags));expected.append(command)
probe=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/native/mean_display_audio_probe'
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(cases),text=True))
assert actual==expected,next(((i,a,b)for i,(a,b)in enumerate(zip(actual,expected))if a!=b),None)
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Original405f98 whole request; actual admission and directaudiofieldwrites; nativehelper modelscommands notPCM',cases=len(cases),matched=len(expected),request88=sum(x['service']==0x88 for x in expected),cancel8c=sum(x['service']==0x8c for x in expected),limitations=['Negative-stack cancellation requires actual4297cc flag2; simulation currently lacks foregroundaudiofeedback. Do not substitute displaystate for audioactiveflags.','Direct Originalwrites represented as service88/8c commands; sequencer field/effect boundaries tested elsewhere.'],inputs=cases,expected=expected)
(ROOT/'analysis/traces/mean-display-audio-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(len(cases),'Original display audio command effects exact')
