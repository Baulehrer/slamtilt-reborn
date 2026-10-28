#!/usr/bin/env python3
"""Retail engine against Pirate data; bounded services, no table-rules claim."""
import hashlib,json,struct,subprocess
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
OBJ,DAT,STOP,STACK=0x1000000,0x1100000,0x2100000,0x200f000

def main():
 meta=json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds'][0]
 exe=ROOT/meta['path'];raw=exe.read_bytes();image=pefile.PE(data=raw).get_memory_mapped_image()
 assert hashlib.sha256(raw).hexdigest()=='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
 datpath=exe.parent/'DAT/PIRATE.DAT';dat=datpath.read_bytes()
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 for a,n in [(0x400000,0x100000),(OBJ,0x400000),(0x2000000,0x10000),(STOP,0x1000)]:u.mem_map(a,n)
 u.mem_write(0x400000,image);u.mem_write(DAT,dat)
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def run(a,eax=OBJ,until=STOP):
  put(STACK,STOP);u.reg_write(UC_X86_REG_ESP,STACK);u.reg_write(UC_X86_REG_EAX,eax);u.emu_start(a,until,count=100000)
  if until==STOP:assert u.reg_read(UC_X86_REG_ESP)==STACK+4,hex(a)
 def service(uc,a,n,c):
  # File loader returns already loaded DAT; allocation returns isolated scratch.
  uc.reg_write(UC_X86_REG_EAX,DAT if a==0x40f7e0 else OBJ+0x8000)
  sp=uc.reg_read(UC_X86_REG_ESP);target=get(sp);uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,target)
 for a in [0x40f7e0,0x40f740]:u.hook_add(UC_HOOK_CODE,service,begin=a,end=a)
 # Execute real initializer through all geometry writes. Scratch allocations
 # and file IO are intentionally replaced; instruction/global writes are real.
 u.reg_write(UC_X86_REG_EDX,OBJ+0x5000);run(0x42b390,OBJ+0x4000,0x42b675)
 layers=[]
 for i in range(3):
  addr=0x46e2e0+i*20
  layers.append(dict(layer=i,directory=hex(addr),planes=struct.unpack('<H',u.mem_read(addr,2))[0],stride=get(addr+4),normal_offset=get(addr+8)-DAT,hit_offset=get(addr+12)-DAT,render_offset=get(addr+16)-DAT))
 run(0x436428);reset=list(u.mem_read(OBJ,100))
 assert get(OBJ+0x40)==DAT+layers[0]['hit_offset'];assert get(OBJ+0x44)==DAT+layers[0]['normal_offset']
 # Evaluate the same original normal function against Pirate data in both
 # Retail and the already supported Demo engine. No guessed normals.
 demo=Uc(UC_ARCH_X86,UC_MODE_32)
 for a,n in [(0x400000,0x100000),(OBJ,0x400000),(0x2000000,0x10000),(STOP,0x1000)]:demo.mem_map(a,n)
 demo.mem_write(0x400000,(ROOT/'build/mean-prepared/pe-data.bin').read_bytes());demo.mem_write(DAT,dat)
 normals=[];cases=[];expected=[];lut=(ROOT/'build/mean-prepared/lookup.bin').read_bytes()
 u.mem_write(OBJ+0x10000,lut)
 for a,v in [(0x46c600,0),(0x46c4a4,0),(0x46c66c,OBJ+0x10000),(0x46c648,OBJ+0x10800),(0x454b68,OBJ),(0x46b760,0),(0x46b764,0),(0x454b44,0)]:put(a,v)
 for layer in layers:
  b=bytearray(reset)
  for o,v in [(0x40,DAT+layer['hit_offset']),(0x44,DAT+layer['normal_offset']),(0x54,DAT+layer['render_offset']),(0x4c,layer['stride']),(0x50,layer['planes'])]:struct.pack_into('<I',b,o,v)
  points=[]
  for y in range(16,min(600,layer['stride']//40)-16,7):
   for x in range(16,304,7):
    if dat[layer['hit_offset']+y*40+x//8] & (128>>(x&7)):points.append((x,y))
  # Cover occupied pixels across the table, bounded 180 samples per layer.
  points=points[::max(1,len(points)//180)][:180]
  for x,y in points:
   struct.pack_into('<ii',b,0,x<<16,y<<16);u.mem_write(OBJ,bytes(b));run(0x40f0d0);angle=u.reg_read(UC_X86_REG_EAX);angle=angle if angle<0x80000000 else angle-0x100000000
   demo.mem_write(OBJ,bytes(b));demo.mem_write(STACK,struct.pack('<I',STOP));demo.reg_write(UC_X86_REG_ESP,STACK);demo.reg_write(UC_X86_REG_EAX,OBJ);demo.emu_start(0x40e1d0,STOP,count=100000);other=demo.reg_read(UC_X86_REG_EAX);other=other if other<0x80000000 else other-0x100000000
   assert angle==other,(layer['layer'],x,y,angle,other)
   normals.append(dict(layer=layer['layer'],xy=[x,y],angle=angle))
   if angle<0:continue
   dx,dy=struct.unpack_from('<h',lut,0x800+angle*2)[0],struct.unpack_from('<h',lut,angle*2)[0]
   cases.append(dict(bytes=list(b),hit_offset=layer['hit_offset'],stride=layer['stride'],planes=layer['planes'],direction_x=dx,direction_y=dy))
   u.mem_write(OBJ,bytes(b));put(0x46c670,angle);run(0x40aa10,0);expected.append(list(u.mem_read(OBJ,100)))
 outdir=ROOT/'build/oracle/pirate';outdir.mkdir(parents=True,exist_ok=True)
 casefile=outdir/'separation-cases.json';casefile.write_text(json.dumps(cases))
 probe=outdir/'pirate_engine_probe';subprocess.run(['c++','-std=c++17','-I'+str(ROOT/'src'),str(ROOT/'tests/pirate_engine_probe.cpp'),str(ROOT/'build/native/libslamassets.a'),'-o',str(probe)],check=True)
 actual=json.loads(subprocess.check_output([str(probe),str(casefile),str(datpath)],text=True));assert expected==actual,'Pirate separation mismatch'
 # 100 physics-component steps from a synthetic free pixel. Actual Pirate
 # reset metadata retained; callbacks, contact response and flippers excluded.
 start=next((x,y) for y in range(100,300) for x in range(140,181) if all(not(dat[layers[0]['hit_offset']+(y+k)*40+x//8]&(128>>(x&7))) for k in range(60)))
 b=bytearray(reset);struct.pack_into('<iiii',b,0,start[0]<<16,start[1]<<16,start[0]<<16,start[1]<<16);struct.pack_into('<H',b,0x58,2)
 states=[list(b)];component_cases=[];component_expected=[]
 u.mem_write(OBJ,bytes(b))
 for tick in range(100):
  component_cases.append(dict(operation='integrate',bytes=list(u.mem_read(OBJ,100))));run(0x40aca8,0);component_expected.append(list(u.mem_read(OBJ,100)))
  component_cases.append(dict(operation='free',bytes=list(u.mem_read(OBJ,100))));run(0x40aab0);component_expected.append(list(u.mem_read(OBJ,100)));states.append(list(u.mem_read(OBJ,100)))
  x,y=struct.unpack_from('<ii',bytes(states[-1]));x>>=16;y>>=16
  assert not(dat[layers[0]['hit_offset']+y*40+x//8]&(128>>(x&7))), 'Free-flight fixture hit geometry'
 cf=outdir/'flight-cases.json';cf.write_text(json.dumps(component_cases));native=json.loads(subprocess.check_output([str(ROOT/'build/native/mean_probe'),str(cf),str(ROOT/'build/mean-prepared/lookup.bin')],text=True));assert native==component_expected,'Retail/native integration mismatch'
 trace={'build_sha256':hashlib.sha256(raw).hexdigest(),'dat_sha256':hashlib.sha256(dat).hexdigest(),'initial_state':states[0],'tick_count':100,'final_state':states[-1],'states':states,'scope':'Original Retail40aca8 integration +40aab0 free velocity; synthetic free start on actual Pirate reset metadata; no gameplay wrapper, flippers, contact response, table callbacks.'}
 (ROOT/'analysis/traces/pirate-ball-100.json').write_text(json.dumps(trace,separators=(',',':'))+'\n')
 report={'schema':1,'status':'VERIFIED bounded shared engine components; NOT playable Pirate','build':str(exe.relative_to(ROOT)),'build_sha256':trace['build_sha256'],'dat_sha256':trace['dat_sha256'],'addresses':{'initializer':'0x42b390','directory_boundary':'0x42b675','ball_reset':'0x436428','normal_full':'0x40f0d0','normal_demo':'0x40e1d0','separation_full':'0x40aa10','integration_full':'0x40aca8','free_velocity_full':'0x40aab0'},'layers':layers,'normal_samples':normals,'compared_normals':len(normals),'native_separation_cases':len(cases),'native_flight_component_states':len(component_expected),'fixture':'analysis/traces/pirate-ball-100.json','original_reset_state':reset,'differences':[],'limits':['File loader and allocation services stubbed; initializer directory and reset are actual original writes.','Synthetic coordinate start, not captured live gameplay.','Pirate collision response callback and flipper descriptors not yet adapted. MeanSimulation still hardcodes Mean directories/normal caches; do not feed Pirate DAT to it.'],'next_action':'Resolve Pirate contact callback via runtime engine descriptor (4364c4 is launch/frame, not contact); adapt flipper descriptors and replace MeanSimulation hardcoded geometry with validated table profile before whole-step replay.'}
 (ROOT/'analysis/pirate-engine-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['layers','compared_normals','native_separation_cases','native_flight_component_states','differences']}))
if __name__=='__main__':main()
