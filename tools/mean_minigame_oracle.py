"""Bounded original selected3 runtime setup, presentation services isolated."""
import struct,json
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
ROOT=Path.cwd();e={'__file__':str(ROOT/'tools/trace_mean_upper_capture.py')};exec((ROOT/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0],e)
u=e['u'];put=e['put'];get=e['get']
for off in [0x38,0x3c,0x40,0x44,0x48,0x4c,0x50,0x60,0x64,0x68,0x6c,0x70,0x74,0x78,0x80,0x88,0x90,0x94]:put(0x1002000+off,0x200ff00)
u.hook_add(UC_HOOK_CODE,e['stub'],begin=0x40f91c,end=0x40f91c)
u.hook_add(UC_HOOK_CODE,e['stub'],begin=0x419f6c,end=0x419f6c)
u.hook_add(UC_HOOK_CODE,e['stub'],begin=0x416fe0,end=0x416fe0)
u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,next((ROOT/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')).read_bytes());put(0x43efd8,0x1100000)
u.mem_write(0x1006000,(ROOT/'build/mean-prepared/lookup.bin').read_bytes());put(0x1002030,0x1006000)
put(0x1002040,0x200ff20)
def svc40(uc,a,n,c):
 sp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(UC_X86_REG_ESP,sp+8);uc.reg_write(UC_X86_REG_EIP,ret)
u.hook_add(UC_HOOK_CODE,svc40,begin=0x200ff20,end=0x200ff20)
# Initialize through actual upper callback.
u.mem_write(0x43f1e6,struct.pack('<h',3));u.mem_write(0x43f394,struct.pack('<h',-1))
b=bytearray(100);struct.pack_into('<iiHH',b,0,14*65536,14*65536,0,0);struct.pack_into('<HH',b,88,3,1);u.mem_write(0x1000000,bytes(b))
def run(a):
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(a,0x200fff0,count=100000)
for i in range(52):run(0x415330)
