#!/usr/bin/env python3
"""Actual416fe0 gate and41b8d0 SPEED reward with actual40f754 admission coupling."""
import hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000)]:u.mem_map(a,n)
u.mem_write(0x400000,image)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
api=0x1002000;engine=0x1001000;put(api+0x58,0x1003000);put(api+0x34,0x1003010)
scores=[];callback=0;handle=0
slots=[0x438b64,0x438b70,0x438b7c,0x438b88,0x438b94]
def hook(uc,a,n,d):
 global callback
 if a not in [0x1003000,0x1003010]:return
 sp=uc.reg_read(UC_X86_REG_ESP);extra=0
 if a==0x1003000:scores.append(uc.reg_read(UC_X86_REG_EAX))
 else:callback=get(sp+12);extra=12;uc.reg_write(UC_X86_REG_EAX,handle)
 uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+extra)
u.hook_add(UC_HOOK_CODE,hook)
cases=[];expected=[]
def fields(timers):
 f=bytearray(0x3c0);struct.pack_into('<I',f,0x68,engine);struct.pack_into('<I',f,0xd0,api)
 for o,v in zip([0x38e,0x368,0x36c],timers):struct.pack_into('<h',f,o,v)
 f[0x250:0x254]=bytes([11,12,13,14]);return f
def run(a):
 put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(a,0x100fff0,count=3000)
for count,timers in itertools.product(range(1,9),itertools.product([-1,0,2000],repeat=3)):
 f=fields(timers);u.mem_write(0x43f000,bytes(f));put(engine, count);put(engine+0x30,6);put(0x438b2c,17);put(0x438b34,19)
 run(0x416fe0);cases.append(dict(kind='gate',fields=list(f),count=count));expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),b2c=get(0x438b2c),b34=struct.unpack('<i',u.mem_read(0x438b34,4))[0]))
for bits,id,gate,handle in itertools.product(range(8),[0,1,2],[-1,0],[0,0x12345678]):
 f=fields([0 if bits&(1<<i) else -1 for i in range(3)]);struct.pack_into('<h',f,0x35e,gate);struct.pack_into('<I',f,0x24,0x1234)
 u.mem_write(0x43f000,bytes(f));put(engine+0x30,6);delays=[101,102,103,104,105]
 for a,v in zip(slots,delays):put(a,v)
 scores.clear();callback=0;u.reg_write(UC_X86_REG_EAX,id);run(0x41b8d0)
 cases.append(dict(kind='reward',fields=list(f),id=id,handle=handle,delays=delays));expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),delays=[get(a) for a in slots],scores=list(scores),callback=callback))
a=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True));assert len(a)==len(expected)
for i,(x,y) in enumerate(zip(a,expected)):
 assert x==y,(i,{k:(x[k],y[k]) for k in x if k!='fields' and x[k]!=y[k]},[(hex(o),v,w)for o,(v,w)in enumerate(zip(x['fields'],y['fields']))if v!=w][:8])
(r/'analysis/traces/mean-speed-rules-original.json').write_text(json.dumps(dict(prepared_sha256=hashlib.sha256(image).hexdigest(),cases=len(cases),scope='Actual416fe0 right gate modes6/1..8balls/three signedtimer boundaries; actual41b8d0/40f754 SPEED scores, exclusions and accepted/rejected display with allfive delays. Presentation and score services adapted; no whole-table trajectory proof.',records=[dict(input=c,output=e)for c,e in zip(cases,expected)]),separators=(',',':'))+'\n')
print('PASS',len(cases),'original SPEED gate/reward/admission states')
