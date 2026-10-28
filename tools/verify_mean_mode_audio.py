#!/usr/bin/env python3
"""Bounded Original Mean mode-start/terminal audio request evidence, no PCM claim."""
import hashlib,json,struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
prefix=(ROOT/'tools/trace_mean_upper_second.py').read_text().split('b=bytearray(100)')[0]
CALLS={0x415969:0x84,0x415ac6:0x84,0x415b83:0x84,0x415dba:0x84,0x415710:0x84,0x4194fd:0x84,0x41950b:0x80}
results=[]
def setup():
 ns={'__file__':str(ROOT/'tools/trace_mean_upper_second.py')};exec(compile(prefix,'upper-audio-harness','exec'),ns)
 u=ns['u'];events=[]
 def log(uc,a,n,d):
  if a in CALLS:
   service=CALLS[a];events.append(dict(address=hex(a),service=hex(service),bank=uc.reg_read(UC_X86_REG_EDX) if service==0x84 else 0,order=uc.reg_read(UC_X86_REG_EAX) if service==0x84 else 0))
 u.hook_add(UC_HOOK_CODE,log)
 ns['put'](0x1002080,0x200ff00)
 return ns,events
for selected,order,addr in [(0,51,0x415969),(1,46,0x415ac6),(2,40,0x415b83),(4,2,0x415dba),(5,29,0x415710)]:
 ns,events=setup();u,put,get=ns['u'],ns['put'],ns['get']
 for a,v in [(0x43f1e6,selected if selected<5 else 0),(0x43f394,-1),(0x43f36a,-1),(0x43f1f2,5 if selected==5 else 0)]:u.mem_write(a,struct.pack('<h',v))
 b=bytearray(100);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b));put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=5000)
 assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
 assert events==[dict(address=hex(addr),service='0x84',bank=0,order=order)],events
 results.append(dict(case='speed-start' if selected==5 else 'selection-'+str(selected),final_mode=get(0x1001030),requests=events))
for value in [-32768,-1,0,1,32767]:
 ns,events=setup();u,put=ns['u'],ns['put'];u.mem_write(0x43f37a,struct.pack('<h',value));put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(0x4194e4,0x200fff0,count=100)
 assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
 assert events==[dict(address=hex(0x41950b if value<0 else 0x4194fd),service='0x80' if value<0 else '0x84',bank=0,order=0 if value<0 else 62)]
 results.append(dict(case='terminal-audio',field_37a=value,requests=events))
# Successful Chicken capture resets through41635f then4194e4.
for value in [-1,0]:
 ns,events=setup();u,put,get=ns['u'],ns['put'],ns['get']
 put(0x1001030,5);put(0x43f05c,75000000)
 for a,v in [(0x43f1e6,0),(0x43f380,-1),(0x43f37a,value)]:u.mem_write(a,struct.pack('<h',v))
 b=bytearray(100);struct.pack_into('<HH',b,0x58,3,2);u.mem_write(0x1000000,bytes(b));put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=5000)
 assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
 assert get(0x1001030)==2
 assert events==[dict(address=hex(0x41950b if value<0 else 0x4194fd),service='0x80' if value<0 else '0x84',bank=0,order=0 if value<0 else 62)],events
 results.append(dict(case='chicken-complete',field_37a=value,requests=events))
report=dict(confidence='VERIFIED',scope='Original415330 whole bounded upper-init callback for selections0/1/2/4 andSPEED; actual40f754, externalservice34/84; Original4194e4 terminal helper; exact requests only, no PCM equivalence',image_sha256=hashlib.sha256((ROOT/'build/mean-prepared/pe-data.bin').read_bytes()).hexdigest(),cases=results)
(ROOT/'analysis/traces/mean-mode-audio-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(len(results),'Original mode audio request cases exact')
