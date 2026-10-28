#!/usr/bin/env python3
"""Actual upper dispatcher in table-mode4, with explicit release boundary."""
import json,random,struct,subprocess,sys,hashlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1];image=(R/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000)]:u.mem_map(a,n)
u.mem_write(0x400000,image)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def word(a,v):u.mem_write(a,struct.pack('<H',v&0xffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
def w(a):return struct.unpack('<h',u.mem_read(a,2))[0]
put(0x43f068,0x1001000);put(0x1001030,4);put(0x43f0d0,0x1002000)
put(0x1002010,0x1003000);put(0x1002058,0x200ff00)
event={}
def boundary(uc,a,n,data):
 if a==0x416be4:event['release']=True
 else:event['score']+=uc.reg_read(UC_X86_REG_EAX)
 sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp)&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,boundary,begin=0x416be4,end=0x416be4)
u.hook_add(UC_HOOK_CODE,boundary,begin=0x200ff00,end=0x200ff00)
cases=[];expected=[];rng=random.Random(0x415362)
def run(c):
 event.clear();event.update(score=0,release=False)
 for a,key in [(0x43f36a,'timer'),(0x43f364,'gate'),(0x43f394,'field394'),(0x43f1f2,'field1f2')]:word(a,c[key])
 for j,v in enumerate(c['slot']):put(0x438b5c+j*4,v)
 put(0x1003008,0);put(0x1001030,4)
 for a in [0x43f200,0x43f202,0x43f1fa]:word(a,0)
 b=bytearray(100);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b))
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
 u.emu_start(0x415330,0x200fff0,count=10000);assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
 assert bytes(u.mem_read(0x1000000,100))==b
 e=dict(timer=w(0x43f36a),gate=w(0x43f364),field394=w(0x43f394),field1f2=w(0x43f1f2),slot=[get(0x438b5c+j*4) for j in range(3)],mode=get(0x1001030),score=event['score'],bonus=get(0x1003008),release=event['release'],rule=False,transfer=False,mode6=False)
 cases.append(c);expected.append(e);return e
for i in range(768):run(dict(timer=rng.choice([50,1,0,-1,-2,-32768]),gate=rng.choice([0,-1,1]),field394=rng.choice([0,-1,1]),field1f2=rng.randrange(8),slot=[rng.choice([-1,0,10]),rng.choice([0,1,2,100]),rng.choice([0,1,2,300])]))
cycle=[];c=dict(timer=50,gate=0,field394=-1,field1f2=6,slot=[-1,100,0])
for tick in range(300):
 e=run(c);cycle.append(e)
 if e['release']:break
 c={k:e[k] for k in ['timer','gate','field394','field1f2','slot']}
 if tick%4==3 and c['slot'][0]>=0:c['slot'][0]-=1
assert cycle[-1]['release'] and sum(e['score'] for e in cycle)==500000
assert all(e['mode']==4 and e['field394']==-1 and e['field1f2']==6 for e in cycle)
a=json.loads(subprocess.run([sys.argv[1]],input=json.dumps(cases),capture_output=True,text=True,check=True).stdout)
assert len(a)==len(expected)
for i,(x,y) in enumerate(zip(a,expected)):assert x==y,(i,cases[i],x,y)
(R/'analysis/traces/mean-mode4-upper-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual415330 upper callback1 in table-mode4; score service stub, actual player bonus write;416be4 release is explicit separately-proven boundary; reward flags200/202/1fa zero; synthetic contexts',cases=cases,expected=expected,cycle=cycle),separators=(',',':'))+'\n')
print('PASS',len(cases),'original mode4 upper states;',len(cycle),'tick hold/award/release cycle')
