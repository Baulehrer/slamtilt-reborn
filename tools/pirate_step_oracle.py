#!/usr/bin/env python3
"""Bounded original Retail Pirate step: all gameplay instructions real, service calls logged."""
import hashlib,json,struct,collections,argparse
from pathlib import Path
import pefile,capstone
from unicorn import *
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1]
EXE=R/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
raw=EXE.read_bytes();pe=pefile.PE(data=raw);im=bytearray(pe.get_memory_mapped_image());im.extend(bytes(0x100000-len(im)))
for s in pe.sections:
 if s.Name.rstrip(b'\0')==b'.bss':im[s.VirtualAddress:s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData)]=bytes(max(s.Misc_VirtualSize,s.SizeOfRawData))
assert hashlib.sha256(raw).hexdigest()=='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
parser=argparse.ArgumentParser();parser.add_argument('--steps',type=int,default=100);args=parser.parse_args();
OUT=R/'build/oracle/pirate-step';OUT.mkdir(parents=True,exist_ok=True)
OBJ,DAT,ST,STOP=0x1000000,0x1100000,0x200f000,0x2100000
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(OBJ,0x400000),(0x2000000,0x10000),(STOP,0x1000)]:u.mem_map(a,n)
u.mem_write(0x400000,bytes(im));dat=(EXE.parent/'DAT/PIRATE.DAT').read_bytes();u.mem_write(DAT,dat)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def ret(uc):
 sp=uc.reg_read(UC_X86_REG_ESP);ra=get(sp);uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ra)
services=collections.Counter();calls=collections.Counter();tick=-1;event=[]
def hook(uc,a,n,c):
 calls[a]+=1
 if a in (0x40f7e0,0x40f740):
  uc.reg_write(UC_X86_REG_EAX,DAT if a==0x40f7e0 else OBJ+0x8000);ret(uc)
def invalid(uc,access,a,size,value,c):
 print('INVALID',tick,hex(uc.reg_read(UC_X86_REG_EIP)),hex(a),hex(uc.reg_read(UC_X86_REG_ESP)),flush=True);return False
u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
def run(a,eax=0,edx=None,until=STOP):
 put(ST,STOP);u.reg_write(UC_X86_REG_ESP,ST);u.reg_write(UC_X86_REG_EAX,eax)
 if edx is not None:u.reg_write(UC_X86_REG_EDX,edx)
 u.emu_start(a,until,count=500000)
 assert u.reg_read(UC_X86_REG_EIP)==until,(hex(a),hex(u.reg_read(UC_X86_REG_EIP)))
 if until==STOP:assert u.reg_read(UC_X86_REG_ESP)==ST+4,hex(a)
# Original startup populates shared service ABI pointer table.
run(0x405a3a,until=0x405b90)
# Actual table initializer: real shared engine context and real service ABI.
run(0x42b390,0x46c67c,0x46b748,0x42b675)
put(0x46c644,0x465958);run(0x405057,until=0x405153)
for a,v in [(0x46c66c,0x455780),(0x46c648,0x455f80),(0x46c638,0x457f84),(0x46c640,0x45d188),(0x46c65c,0x458788),(0x46c678,0x45e454),(0x46c67c,1),(0x46c6ac,1),(0x454b68,OBJ)]:put(a,v)
for i in range(1,8):put(0x454b68+i*4,OBJ+i*100)
# Point-force list supplied directly by this table's graphics descriptor.
put(0x46b760,get(get(0x465958)))
put(0x46c72c,OBJ+0x7000)
# No active nudge/debug injected input.
for a in (0x46b764,0x454b44,0x46c600,0x46c4a4,0x46c604,0x46c5f8):put(a,0)
run(0x436428,OBJ)
# state0 is original scheduler's reset transition; zero state before reset is synthetic cold engine.
# Launch latch asserted on every step so actual callback can launch when state1 is reached.
initial=list(u.mem_read(OBJ,100));states=[initial];errors=[]
initial_image=bytes(u.mem_read(0x400000,0x100000));initial_runtime=bytes(u.mem_read(OBJ,0x10000))
(OUT/'image.bin').write_bytes(initial_image)
(OUT/'runtime.bin').write_bytes(initial_runtime)
try:
 for tick in range(args.steps):
  put(0x46c5fc,1)
  run(0x409154);run(0x40950c)
  b=bytes(u.mem_read(OBJ,100));states.append(list(b))
  if tick%1000==0:print(tick,struct.unpack_from('<ii',b),struct.unpack_from('<ii',b,20),struct.unpack_from('<H',b,88)[0],flush=True)
except Exception as e:errors.append(str(e))
first_calls=dict(calls)
# A second fresh memory snapshot must reproduce every byte through the per-ball boundary.
u.mem_write(0x400000,initial_image);u.mem_write(OBJ,initial_runtime)
replay=[]
for tick in range(len(states)-1):
 put(0x46c5fc,1);run(0x409154);run(0x409588,0)
 replay.append(list(u.mem_read(OBJ,100)))
assert replay==states[1:], 'per-ball/scheduler trajectory differs'
result=dict(per_ball_scheduler_states_equal=True,build_sha256=hashlib.sha256(raw).hexdigest(),dat_sha256=hashlib.sha256(dat).hexdigest(),tick_count=len(states)-1,initial_state=initial,final_state=states[-1],states=states,executed_calls={hex(a):n for a,n in first_calls.items() if a in [0x409154,0x40950c,0x409588,0x43163c,0x431a44,0x4364c4,0x409b08,0x40979c,0x40aca8,0x40f0d0,0x40a884,0x40aa10,0x409ce8,0x40a380]},service_stubs={hex(a):n for a,n in services.items()},errors=errors)
(OUT/'trace.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print({k:v for k,v in result.items() if k not in ('states','initial_state','final_state')})
