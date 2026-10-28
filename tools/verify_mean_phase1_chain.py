#!/usr/bin/env python3
"""Sequential original/native phase1 boundaries. Scheduler and exit reset adapters excluded."""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native');a=p.parse_args();r=Path(__file__).resolve().parents[1]
image=(r/'build/mean-prepared/pe-data.bin').read_bytes();dat=next((r/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
exe=Path(a.native) if a.native else r/'build/native/mean_phase1_chain_probe'
if not a.native:
 subprocess.run(['c++','-std=c++17','-Isrc','tests/mean_phase1_chain_probe.cpp','build/native/libslamassets.a','build/native/libmean_flipper_lift.a','build/native/libmean_minigame_lift.a','build/native/libmean_ball_pair_lift.a','-o',str(exe)],cwd=r,check=True)
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x100000);u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,dat.read_bytes())
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
def call(ad,skip=0):
 sp=0x10ff000;u.mem_write(sp,b'\0'*skip+struct.pack('<I',0x10ffff0));u.reg_write(UC_X86_REG_ESP,sp);u.emu_start(ad,0x10ffff0,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x10ffff0, "Original chain boundary did not return"
call(0x40af14);put(0x43e3e8,0x1000000);put(0x43efd8,0x1100000)
events={};kind=''
def hook(uc,ad,n,data):
 if ad in [0x1004000,0x1005000,0x1006000,0x1007000,0x1008000,0x4194e4,0x419f6c,0x40f754,0x416fe0]:
  if ad==0x416fe0 and kind=='entry':return # actual mode4 gate reset
  sp=uc.reg_read(UC_X86_REG_ESP);extra=0
  if ad==0x1004000:events['callback']=get(sp+12);uc.reg_write(UC_X86_REG_EAX,0);extra=12
  if ad==0x1005000:events['score']=uc.reg_read(UC_X86_REG_EAX)
  if ad==0x40f754:extra=8
  if ad==0x1006000:extra=4
  uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+extra)
u.hook_add(UC_HOOK_CODE,hook)
for off,target in [(0x34,0x1004000),(0x58,0x1005000),(0x3c,0x406680),(0x40,0x1006000),(0x84,0x1007000),(0x8c,0x1008000)]:put(0x1003000+off,target)
put(0x438be0,0x210000)
base=bytearray(0x3c0);struct.pack_into('<I',base,0x068,0x1002000);struct.pack_into('<I',base,0x0d0,0x1003000);struct.pack_into('<h',base,0x392,-1)
clock=lambda n:[dict(kind='clock') for _ in range(n)]
chains=[('cancel',[dict(kind='entry'),dict(kind='idle'),dict(kind='right')]),('late-release-two-rewards-exit',[dict(kind='entry'),dict(kind='idle')]+clock(481)+[dict(kind='right'),dict(kind='idle'),dict(kind='event',branch=0x41bf0c),dict(kind='idle'),dict(kind='event',branch=0x41bf0c),dict(kind='event',branch=0x41c0df)]),('countdown-expiry-exit',[dict(kind='entry'),dict(kind='idle')]+clock(500)+[dict(kind='idle'),dict(kind='event',branch=0x41c39e)])]
cases=[];expected=[]
for name,ops in chains:
 u.mem_write(0x43f000,bytes(base));put(0x1002030,2);put(0x1002040,13);u.mem_write(0x438a40,struct.pack('<h',77));rows=[]
 for op in ops:
  kind=op['kind'];events=dict(callback=0,score=0)
  u.reg_write(UC_X86_REG_EAX,0x1002000);u.reg_write(UC_X86_REG_ECX,0x1002000)
  if kind=='entry':call(0x41b010,24)
  elif kind=='idle':call(0x4141b8)
  elif kind=='clock':u.reg_write(UC_X86_REG_EAX,0x1003000);call(0x414d30,24)
  elif kind=='right':call(0x417849,24)
  else:call(op['branch'],24)
  mode=get(0x1002030);rows.append(dict(fields=list(u.mem_read(0x43f000,0x3c0)),a40=struct.unpack('<h',u.mem_read(0x438a40,2))[0],mode=mode,engine40=get(0x1002040),**events,exit=mode==2,clear_slots=False))
  if kind=='entry':rows[-1]['exit']=False
 cases.append(dict(name=name,fields=list(base),operations=ops));expected.append(rows)
actual=json.loads(subprocess.check_output([str(exe),str(dat)],input=json.dumps(cases).encode()))
assert len(actual)==len(expected)
for ci,(xs,ys) in enumerate(zip(actual,expected)):
 assert len(xs)==len(ys)
 for i,(x,y) in enumerate(zip(xs,ys)):
  if x!=y:raise AssertionError((chains[ci][0],i,cases[ci]['operations'][i],{k:(x[k],y[k]) for k in x if k!='fields' and x[k]!=y[k]},[(hex(k),aa,bb) for k,(aa,bb) in enumerate(zip(x['fields'],y['fields'])) if aa!=bb]))
assert expected[1][-1]['fields'][0x058:0x05c]==list(struct.pack('<I',60000000))
assert expected[2][-2]['mode']==4 and expected[2][-2]['fields'][0x3aa:0x3ac]==[2,0]
(r/'analysis/traces/mean-phase1-chain-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(dat.read_bytes()).hexdigest(),build_sha256=hashlib.sha256(next((r/'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE')).read_bytes()).hexdigest(),scope='Sequential entry41b010 -> actual idle4141b8/406680 -> clock414d30 -> right417849 -> events41bf0c/41c0df/41c39e. Original scheduler selection is explicit; exit4194e4/419f6c/416fe0 are excluded. Presentation/audio services are explicit return adapters; callbacks and score writes recorded at every boundary; service34 returns0. Timeout means countdown expiry, not mode exit.',chains=[dict(input=c,states=e) for c,e in zip(cases,expected)],differences=0),separators=(',',':'))+'\n')
print('PASS',len(cases),'sequential chains,',sum(map(len,expected)),'complete raw-state boundaries')
