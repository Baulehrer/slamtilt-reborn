#!/usr/bin/env python3
"""Actual415330 upper announcements + actual40f754 admission effects."""
import hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_EBX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1]
base=(R/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0]
cases=[];expected=[]
for mode,timer,gate,unlocked,count,selected,handle in itertools.product([2,3,4],[50,1,0,-1],[0,-1],[0,-1],[0,5],[0,1,2,4],[0,1]):
 c=dict(mode=mode,timer=timer,gate=gate,field394=unlocked,field1f2=count,selected=selected,handle=handle,delays=[17,23,31,43,59],field024=97)
 env={'__file__':str(R/'tools/trace_mean_upper_capture.py')};exec(base.replace('UC_X86_REG_EAX,1)','UC_X86_REG_EAX,'+str(handle)+')'),env)
 u=env['u'];put=env['put'];get=env['get'];word=env['word'];calls=[]
 for a,v in [(0x43f36a,timer),(0x43f394,unlocked),(0x43f1f2,count),(0x43f1e6,selected),(0x43f364,gate),(0x43f200,0),(0x43f202,0),(0x43f1fa,0)]:u.mem_write(a,struct.pack('<h',v))
 put(0x1001030,mode);put(0x43f024,c['field024'])
 for a,v in zip([0x438b64,0x438b70,0x438b7c,0x438b88,0x438b94],c['delays']):put(a,v)
 def helper(uc,a,n,data):
  sp=uc.reg_read(UC_X86_REG_ESP)
  calls.append(dict(delay=get(sp+8),selectors=[get(sp+4)]+[uc.reg_read(r) for r in [UC_X86_REG_ECX,UC_X86_REG_EBX,UC_X86_REG_EDX,UC_X86_REG_EAX]]))
 u.hook_add(UC_HOOK_CODE,helper,begin=0x40f754,end=0x40f754)
 b=bytearray(100);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b))
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=10000)
 assert u.reg_read(UC_X86_REG_EIP)==0x200fff0
 expected.append(dict(ok=True,timer=word(0x43f36a),mode=get(0x1001030),field394=word(0x43f394),field1f2=word(0x43f1f2),delays=[get(a) for a in [0x438b64,0x438b70,0x438b7c,0x438b88,0x438b94]],field024=get(0x43f024),request=bool(calls),delay=calls[0]['delay'] if calls else 0,selectors=calls[0]['selectors'] if calls else [0,1,1,1,1]));cases.append(c)
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True))
for i,(a,b) in enumerate(zip(actual,expected)):assert a==b,(i,cases[i],a,b)
(R/'analysis/traces/mean-upper-delay-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256((R/'build/mean-prepared/pe-data.bin').read_bytes()).hexdigest(),scope='Actual415330 timer50/1/0/-1 gate0/-1 upper first-unlock/mode5 selections0,1,2,4/mode6 start and mode4 no-op. Service34 handle0/1 synthetic admission; actual40f754 all5 secondary delays and field024. Rule/lamp helper boundaries retained from existing upper oracle; no full table trajectory.',cases=cases,expected=expected),separators=(',',':'))+'\n')
print('PASS',len(cases),'original upper admission/delay contexts')
