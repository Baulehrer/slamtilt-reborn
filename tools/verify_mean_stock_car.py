#!/usr/bin/env python3
"""Actual bounded Mean bumper rule island, including original419da4 and40f754."""
import hashlib
import itertools
import json
import struct
import subprocess
import sys
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *
root = Path(__file__).resolve().parents[1]
image = (root / 'build/mean-prepared/pe-data.bin').read_bytes()
u = Uc(UC_ARCH_X86, UC_MODE_32)
for address, size in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000)]: u.mem_map(address,size)
u.mem_write(0x400000,image)
def put(address,value): u.mem_write(address,struct.pack('<I',value & 0xffffffff))
def get(address): return struct.unpack('<I',u.mem_read(address,4))[0]
points=[]; callback=0; handle=0
api=0x1002000; engine=0x1001000
put(api+0x58,0x1003000); put(api+0x5c,0x1003010); put(api+0x34,0x1003020)
def hook(uc,address,size,data):
    global callback
    if address not in [0x1003000,0x1003010,0x1003020]: return
    sp=uc.reg_read(UC_X86_REG_ESP); extra=0
    if address==0x1003000: points.append(uc.reg_read(UC_X86_REG_EAX))
    elif address==0x1003020:
        callback=get(sp+12); extra=12
        uc.reg_write(UC_X86_REG_EAX,handle)
    uc.reg_write(UC_X86_REG_EIP,get(sp)); uc.reg_write(UC_X86_REG_ESP,sp+4+extra)
u.hook_add(UC_HOOK_CODE,hook)
cases=[]; expected=[]
for i,(mode,material,remaining,played,locked,handle) in enumerate(itertools.product(
        [2,4,5,6],[3,4],[-1,0,1,15,30],[0,15,31],[0,1],[0,0x10203040])):
    fields=bytearray(0x3c0)
    fields[0x208:0x304]=bytes([0xa5])*(0x304-0x208)
    def word(offset,value): struct.pack_into('<H',fields,offset,value & 0xffff)
    selected=i % 5; suppressed=i % 7==0
    word(0x38a,remaining); word(0x384,locked); word(0x1e6,selected); word(0x366,42)
    for j in range(5): fields[0x1e0+j]=bool(played & (1<<j))
    struct.pack_into('<I',fields,0x068,engine); struct.pack_into('<I',fields,0x0d0,api)
    struct.pack_into('<I',fields,0x024,0x12345678)
    u.mem_write(0x43f000,bytes(fields)); put(engine+0x30,mode); put(api+0x1c,int(suppressed))
    put(0x1004000,0); put(0x1004004,0); put(0x1005000,128); put(0x1005004,0)
    points.clear(); callback=0
    sp=0x200f000; put(sp,0x100fff0)
    u.reg_write(UC_X86_REG_ESP,sp); u.reg_write(UC_X86_REG_EAX,0x1004000)
    u.reg_write(UC_X86_REG_EDX,material); u.reg_write(UC_X86_REG_ECX,0x1005000)
    u.reg_write(UC_X86_REG_EBX,0x1005004)
    u.emu_start(0x41e00c,0x100fff0,count=3000)
    cases.append(dict(fields=list(fields),mode=mode,material=material,suppressed=suppressed,handle=handle))
    expected.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),mode=get(engine+0x30),
                         score=sum(points)-(6830 if points else 0),callback=callback))
actual=json.loads(subprocess.check_output([sys.argv[1]],input=json.dumps(cases),text=True))
assert len(actual)==len(expected)
for i,(a,b) in enumerate(zip(actual,expected)):
    assert a==b,(i,{k:(a[k],b[k]) for k in a if k!='fields' and a[k]!=b[k]},
                  [(hex(o),x,y) for o,(x,y) in enumerate(zip(a['fields'],b['fields'])) if x!=y][:12])
(root/'analysis/traces/mean-stock-car-original.json').write_text(json.dumps({
    'prepared_sha256':hashlib.sha256(image).hexdigest(),'cases':len(cases),'differences':0,
    'scope':'Actual41e00c materials3/4 with real419da4 selection and40f754; sound/scoring/display services adapted, physical base6830 excluded from rule score. Modes2/4/5/6, played masks, locked selection, remaining counts and admitted/rejected displays. No whole-table trajectory claim.',
    'records':[{'input':c,'output':e} for c,e in zip(cases,expected)]},separators=(',',':'))+'\n')
print('PASS',len(cases),'actual StockCar bumper/selector/admission states')
