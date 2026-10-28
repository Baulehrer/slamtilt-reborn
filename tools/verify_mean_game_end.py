#!/usr/bin/env python3
"""Full finite-game predicate, actual branch + bounded game-over writes."""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--oracle',action='store_true');a=p.parse_args()
f=ROOT/'analysis/traces/mean-game-end-original.json'
if a.oracle:
 import pefile
 from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
 from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_ESI
 path=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE';exe=path.read_bytes();image=pefile.PE(data=exe).get_memory_mapped_image();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
 def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
 def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
 boundary=[]; checking=[True]
 def hook(uc,ad,n,c):
  if checking[0] and ad in (0x4083d1,0x408465):boundary.append(ad);uc.emu_stop()
  elif not checking[0] and ad==0x4084db:uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);cases=[];expected=[];effects=[]
 for flag in (0,1,2,0xffffffff):
  for ball in list(range(10))+[0x7fff,0x8000,0xffff]:
   c=dict(field_player_0e=ball,field_454aa4=flag);cases.append(c);put(0x454aa4,flag);u.mem_write(0x100000e,struct.pack('<H',ball));u.reg_write(UC_X86_REG_EDX,0x1000000);u.reg_write(UC_X86_REG_ESI,flag);checking[0]=True;boundary.clear();u.emu_start(0x4083a9,0,count=30);ended=boundary==[0x408465];expected.append(ended)
   if ended:
    checking[0]=False;u.reg_write(UC_X86_REG_ESP,0x100f000);put(0x46c684,1);u.emu_start(0x408465,0x4084db,count=100)
    effects.append(dict(case=len(cases)-1,table_mode=get(0x46c6ac),player_count=get(0x46c684),ball_count=get(0x46c67c),engine40=get(0x46c68c),field_46c608=get(0x46c608),field_454a8c=get(0x454a8c)))
 data=dict(build_sha256=hashlib.sha256(exe).hexdigest(),addresses=['0x4083a9','0x4083cb','0x408465','0x4084db'],scope='Windows Full selected-next-player signed WORD boundary; game-over initialization writes observed to4084db. Demo407808 has no corresponding limit. Highscore entry and later display phases excluded.',cases=cases,expected=expected,game_over_effects=effects);f.write_text(json.dumps(data,separators=(',',':'))+'\n')
else:data=json.loads(f.read_text())
actual=json.loads(subprocess.check_output([str(a.native)],input=json.dumps(dict(cases=data['cases'])),text=True));assert actual==data['expected'];print(json.dumps(dict(cases=len(actual),differences=0)))
