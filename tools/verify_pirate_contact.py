#!/usr/bin/env python3
"""Retail Pirate engine+4 material callback and shared wall transform, no separation."""
import hashlib,json,random,struct,subprocess
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
OBJ,DAT,STOP,STACK=0x1000000,0x1100000,0x2100000,0x200f000

def main():
 exe=ROOT/json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds'][0]['path'];raw=exe.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
 image=pefile.PE(data=raw).get_memory_mapped_image();dat=(exe.parent/'DAT/PIRATE.DAT').read_bytes();lut=(ROOT/'build/mean-prepared/lookup.bin').read_bytes();report=json.loads((ROOT/'analysis/pirate-engine-validation.json').read_text());layers=report['layers'];l0=layers[0];state=[DAT+l0['hit_offset'],DAT+l0['normal_offset'],DAT+l0['render_offset'],l0['stride'],l0['planes']]
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 for a,n in [(0x400000,0x100000),(OBJ,0x400000),(0x2000000,0x10000),(STOP,0x1000)]:u.mem_map(a,n)
 u.mem_write(0x400000,image);u.mem_write(DAT,dat);u.mem_write(OBJ+0x10000,lut)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def skip(uc,a,n,c):
  sp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,ret)
 u.hook_add(UC_HOOK_CODE,skip,begin=0x40aa10,end=0x40aa10)
 for a,v in [(0x454b68,OBJ),(0x46c66c,OBJ+0x10000),(0x46c648,OBJ+0x10800),(0x46c644,0x465958),(0x46e2b4,OBJ+0x5000),(0x46e2ec,state[0]),(0x46e2e8,state[1]),(0x46e2f0,state[2]),(0x46e2e4,state[3]),(0x46e2de,state[4]<<16)]:put(a,v)
 rng=random.Random(1996);cases=[];expected=[];samples=report['normal_samples'];real=0
 for i in range(1400):
  layer=i%3;material=(i//3)%9;mode=(i//27)%2
  b=bytearray(rng.randbytes(100));struct.pack_into('<ii',b,0,rng.randrange(320)<<16,rng.randrange(616)<<16);struct.pack_into('<ii',b,0x14,rng.randrange(-8*65536,8*65536),rng.randrange(-8*65536,8*65536));angle=rng.randrange(4096)
  if i<540:
   sample=samples[i];layer=sample['layer'];x,y=sample['xy'];struct.pack_into('<ii',b,0,x<<16,y<<16)
   if sample['angle']>=0:angle=sample['angle'];real+=1
  struct.pack_into('<H',b,0x1e,angle);struct.pack_into('<H',b,0x48,layer);struct.pack_into('<H',b,0x3c,material)
  ox,oy=rng.randrange(-65536,65536),rng.randrange(-65536,65536)
  c=dict(bytes=list(b),layer0=state,services_1c=mode,offset_x=ox,offset_y=oy);cases.append(c)
  supported=not(layer==0 and (material in (5,6) or material in (3,4) and mode==0) or layer==1 and material==1)
  if not supported:expected.append(dict(supported=False,bytes=list(b)));continue
  for a,v in [(OBJ+0x501c,mode),(0x46c604,ox),(0x46c5f8,oy)]:put(a,v)
  u.mem_write(OBJ,bytes(b));put(STACK,STOP);u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_EAX,0);u.emu_start(0x40a884,STOP,count=100000);assert u.reg_read(UC_X86_REG_EIP)==STOP
  expected.append(dict(supported=True,bytes=list(u.mem_read(OBJ,100))))
 outdir=ROOT/'build/oracle/pirate';outdir.mkdir(parents=True,exist_ok=True);cf=outdir/'contact-cases.json';cf.write_text(json.dumps(cases));probe=outdir/'pirate_contact_probe'
 subprocess.run(['c++','-std=c++17','-I'+str(ROOT/'src'),'-I'+str(ROOT/'build/native/_deps/json-src/include'),str(ROOT/'tests/pirate_contact_probe.cpp'),str(ROOT/'src/physics/pirate_contact.cpp'),str(ROOT/'build/native/libslamassets.a'),'-o',str(probe)],check=True)
 actual=json.loads(subprocess.check_output([str(probe),str(cf),str(ROOT/'build/mean-prepared/lookup.bin')],text=True));assert len(actual)==len(expected);diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
 if diff:
  i=diff[0];print('first mismatch',i,[(n,x,y)for n,(x,y)in enumerate(zip(actual[i]['bytes'],expected[i]['bytes']))if x!=y])
 fixture=dict(build_sha256=sha,dat_sha256=hashlib.sha256(dat).hexdigest(),addresses={'wall':'0x40a884','directory':'0x465778','callbacks':['0x438ea0','0x4397d0','0x439994']},scope='All 100 ball bytes; original shared wall transform and supported actual Pirate layer callbacks. Separation explicitly excluded. Unsupported cases return false unchanged. Real Pirate sampled coordinates/normal angles, synthetic velocity/pose fields.',cases=len(cases),supported_cases=sum(e['supported'] for e in expected),real_geometry_normal_cases=real,differences=diff,inputs=cases,expected=expected)
 (ROOT/'analysis/traces/pirate-contact-original.json').write_text(json.dumps(fixture,separators=(',',':'))+'\n');print(json.dumps({k:fixture[k] for k in ['cases','supported_cases','real_geometry_normal_cases','differences']}));assert not diff
if __name__=='__main__':main()
