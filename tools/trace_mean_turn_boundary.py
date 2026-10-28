#!/usr/bin/env python3
"""Observe actual engine drain/save and next-ball reset/mode-write ordering."""
import hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1];image=(ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
calls=[]
def hook(uc,a,n,c):
 if a in [0x1000600,0x1000610,0x1000620]:
  calls.append(dict(callback={0x1000600:'table+18 save',0x1000610:'table+1c reset',0x1000620:'table+14'}[a],eax=uc.reg_read(UC_X86_REG_EAX),mode=get(0x43e7a0)))
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
 elif a in [0x100fff0,0x4078a6]:uc.emu_stop()
u.hook_add(UC_HOOK_CODE,hook)
for a,v in [(0x43e740,0x1001000),(0x1001004,0x1001100),(0x1001108,0x1001200),(0x1001218,0x1000600),(0x100121c,0x1000610),(0x1001214,0x1000620),(0x100100c,0x1001300),(0x1001308,123),(0x100130c,456)]:put(a,v)
cases=[]
for mode in [1,2,4,5,6]:
 for count in [1,2,4,8]:
  calls.clear();put(0x43e7a0,mode);put(0x43e770,count);put(0x43e774,1);put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.reg_write(UC_X86_REG_EAX,0x1001400);u.emu_start(0x408084,0x100fff0,count=100)
  cases.append(dict(operation='drain',input_mode=mode,ball_count=count,calls=calls.copy(),final_mode=get(0x43e7a0),phase=get(0x43e73c),timer=get(0x43e7e4),engine40=get(0x43e780),ball_state=struct.unpack('<H',u.mem_read(0x1001458,2))[0]))
for mode in [3,5,6]:
 calls.clear();put(0x43e7a0,mode);put(0x43e774,1);u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x407808,0,count=100)
 cases.append(dict(operation='next_ball',input_mode=mode,calls=calls.copy(),final_mode=get(0x43e7a0),engine40=get(0x43e780)))
p=ROOT/'analysis/traces/mean-turn-boundary-original.json';p.write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual408084 and407808; callback bodies observed/stubbed, proves caller ordering and mode values',cases=cases),indent=2)+'\n');print(json.dumps(dict(cases=len(cases),path=str(p))))
