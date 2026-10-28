#!/usr/bin/env python3
"""Actual408915 gate and41ab94 initializer on retained full ball records."""
import json,struct,subprocess,sys,hashlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1];image=(R/'build/mean-prepared/pe-data.bin').read_bytes();source=json.loads((R/'analysis/traces/mean-capture-flight-original.json').read_text())
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000)]:u.mem_map(a,n)
u.mem_write(0x400000,image)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
for a,v in [(0x43e740,0x1001000),(0x1001004,0x1001100),(0x1001108,0x1001200),(0x1001210,0x41ab94)]:put(a,v)
for i,v in enumerate([3,0x6040,0x1100000+0x959f6,0x1100000+0x9ba36,0x1100000+0xb3b36]):put(0x43f06c+i*4,v)
def stop(uc,a,n,c):uc.emu_stop()
u.hook_add(UC_HOOK_CODE,stop,begin=0x408949,end=0x408949);u.hook_add(UC_HOOK_CODE,stop,begin=0x408a0e,end=0x408a0e)
records=[]
for capture,flight in zip(source['capture'],source['flights']):
 records.extend([capture[0]['ball'],capture[-1]['ball'],flight[len(flight)//2],flight[-1]])
cases=[];expected=[]
for record in records:
 for shifted in [False,True]:
  for state in [0,2,7,0xffff]:
   for gate in [-1,0,1]:
    b=bytearray(record);struct.pack_into('<H',b,0x58,state)
    if shifted:
     for o in [0x40,0x44,0x54]:struct.pack_into('<I',b,o,struct.unpack_from('<I',b,o)[0]+7)
     struct.pack_into('<I',b,0x4c,0x60e0);struct.pack_into('<I',b,0x50,1)
    c=dict(ball=list(b),gate=gate,shifted=shifted);cases.append(c)
    u.mem_write(0x1001400,bytes(b));put(0x43e79c,gate)
    u.reg_write(UC_X86_REG_EAX,0xffffffff if state==0xffff else state);u.reg_write(UC_X86_REG_EDX,0x1001400);u.reg_write(UC_X86_REG_ESP,0x100f000)
    u.emu_start(0x408915,0,count=1000);pc=u.reg_read(UC_X86_REG_EIP);assert pc in [0x408949,0x408a0e]
    decision=2 if pc==0x408a0e else 1 if state==0xffff else 0
    expected.append(dict(ball=list(u.mem_read(0x1001400,100)),gate=get(0x43e79c),decision=decision))
a=json.loads(subprocess.run([sys.argv[1]],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);assert len(a)==len(expected)
for i,(x,y) in enumerate(zip(a,expected)):assert x==y,(i,'offsets',[j for j in range(100) if x['ball'][j]!=y['ball'][j]],x['gate'],y['gate'])
(R/'analysis/traces/mean-restart-reuse-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual408915..408943 with real41ab94 callback; controlled baseline directory; retained capture/release/midflight/drain records plus explicitly shifted pointers; stop before integration, not full next-ball callback/scheduler proof',cases=cases,expected=expected),separators=(',',':'))+'\n')
print('PASS',len(cases),'complete100-byte restart/gate/real-initializer states')
