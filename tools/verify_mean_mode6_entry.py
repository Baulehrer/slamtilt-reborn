#!/usr/bin/env python3
"""Bounded original upper-capture entry after all five modes; no native claims."""
import hashlib,itertools,json,struct
from pathlib import Path
exec((Path(__file__).parent/'trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0])
image=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000))
fields=[0x382,0x37e,0x376,0x38e,0x368,0x36c,0x36e,0x35e]
def setw(address,value):u.mem_write(address,struct.pack('<H',value&65535))
def snapshot():
 return dict(ball=list(u.mem_read(0x1000000,100)),timer=word(0x43f36a),gate=word(0x43f364),field394=word(0x43f394),field1f2=word(0x43f1f2),mode=get(0x1001030),selected=word(0x43f1e6),fields={hex(f):word(0x43f000+f) for f in fields},data=list(u.mem_read(0x43f23c,24)),sum058=get(0x43f058)&0xffffffff,slot_upper=[get(0x438b5c+i*4) for i in range(3)],lamp=list(u.mem_read(0x43f1e0,5)))
cases=[]
for count,field394,selected in itertools.product([5,6,32767],[0,-1],range(5)):
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime)
 for f in fields:setw(0x43f000+f,0x1200+f)
 u.mem_write(0x43f23c,bytes(range(24)));put(0x43f058,0x12345678)
 setw(0x43f36a,-1);setw(0x43f364,0);setw(0x43f1f2,count);setw(0x43f394,field394);setw(0x43f1e6,selected)
 u.mem_write(0x43f1e0,bytes([1,1,1,1,1]))
 b=bytearray(100);struct.pack_into('<ii',b,0,14*65536,14*65536);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b))
 initial=snapshot();put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
 u.emu_start(0x415330,0x200fff0,count=20000)
 assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
 final=snapshot();assert final['mode']==6,(count,field394,selected,final)
 cases.append(dict(input=dict(field1f2=count,field394=field394,selected=selected),initial=initial,final=final))
fixture=dict(scope='Actual415330 upper timer -1 to -2; original mode6 initialization after field1f2>=5; presentation services bounded by shared upper-capture oracle',entry='0x415330',image_sha256=hashlib.sha256(image).hexdigest(),cases=cases)
out=ROOT/'analysis/traces/mean-mode6-entry-original.json';out.write_text(json.dumps(fixture,separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),mode6_cases=sum(c['final']['mode']==6 for c in cases),sample=cases[0]['final'])))
