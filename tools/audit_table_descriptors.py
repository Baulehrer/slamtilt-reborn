#!/usr/bin/env python3
"""Bounded Retail table initializer evidence; loader/allocation adapters only."""
import hashlib,json,struct
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
ROOT=Path(__file__).resolve().parents[1]
exe=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
raw=exe.read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert sha=='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
image=pefile.PE(data=raw).get_memory_mapped_image()
profiles=[('mean',0x41b9e0,0x46de14,0x46db7c,4),('pirate',0x42b390,0x46e4c4,0x46e2e0,3),('space',0x439ae0,0x46ed60,0x46eae8,4),('demon',0x40febc,0x46d6ec,0x46d610,3)]
results=[]
for name,init,cbbase,geometry,layer_count in profiles:
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 for a,n in [(0x400000,0x100000),(0x1000000,0x600000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(a,n)
 u.mem_write(0x400000,image)
 dat=(exe.parent/'DAT'/f'{name.upper()}.DAT').read_bytes();u.mem_write(0x1100000,dat)
 def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 alloc=[0x1400000];stores={}
 def service(uc,a,n,c):
  if a==0x40f7e0:value=0x1100000
  else:value=alloc[0];alloc[0]+=0x10000
  uc.reg_write(UC_X86_REG_EAX,value);sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,get(sp))
 def write(uc,access,a,size,value,c):
  if cbbase<=a<cbbase+0x54:stores[a]={'target':hex(value),'store_instruction':hex(uc.reg_read(UC_X86_REG_EIP))}
 for a in [0x40f7e0,0x40f740]:u.hook_add(UC_HOOK_CODE,service,begin=a,end=a)
 u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.mem_write(0x200f000,struct.pack('<I',0x2100000));u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1004000);u.reg_write(UC_X86_REG_EDX,0x1005000)
 try: u.emu_start(init,0x2100000,count=100000)
 except Exception:
  print(name, hex(u.reg_read(UC_X86_REG_EIP)),hex(u.reg_read(UC_X86_REG_ESP)));raise
 assert u.reg_read(UC_X86_REG_EIP)==0x2100000
 returned=u.reg_read(UC_X86_REG_EAX);graphics=get(returned);engine=get(returned+4);contactdir=get(engine);unknown_dir=get(engine+4)
 assert get(engine+8)==cbbase
 dirs=[]
 for j in range(layer_count):
  a=geometry+j*20
  dirs.append({'layer':j,'planes':int.from_bytes(u.mem_read(a,2),'little'),'stride':get(a+4),'normal_offset':get(a+8)-0x1100000,'hit_offset':get(a+12)-0x1100000,'render_offset':get(a+16)-0x1100000,'switch_callback':hex(get(contactdir+j*4))})
 motiondir=get(graphics+4)
 results.append({'table':name,'initializer':hex(init),'dat_sha256':hashlib.sha256(dat).hexdigest(),'returned_descriptor':hex(returned),'graphics_descriptor':hex(graphics),'engine_descriptor':hex(engine),'switch_callback_directory':hex(contactdir),'field_04_directory_unknown':hex(unknown_dir),'callback_directory':hex(cbbase),'callbacks':[dict(offset=hex(a-cbbase),slot=hex(a),**v) for a,v in sorted(stores.items())],'layers':dirs,'motion_directory_candidate':hex(motiondir),'motion_directory_first_three_raw_dwords_unknown':[hex(get(motiondir+j*4)) for j in range(3)]})
report={'schema':1,'build':str(exe.relative_to(ROOT)),'build_sha256':sha,'confidence':'VERIFIED initializer writes and static descriptor links; semantics bounded by consumer evidence','tables':results,'consumer_evidence':[{'address':'0x409823..0x40983e','claim':'Shared switch dispatcher selects layer using signed DWORD ball+0x46 >>16, obtains current descriptor+4 then engine descriptor+0, calls directory[layer] with EAX=ball.'},{'address':'0x409597..0x4095a4','claim':'Shared step calls engine callback+0x2c through current descriptor+4 / engine+8.'},{'address':'0x409679..0x409685','claim':'Shared step calls engine callback+0x0c through same chain; 4364c4 is this Pirate slot, not layer switch dispatch.'},{'address':'0x4096ca..0x4096d4','claim':'Shared state movement reads current descriptor+0 / graphics+4 then indexed motion entry using ball+0x32; full motion/flipper semantics remain PARTIAL.'}],'limits':['Only loader and allocation services adapted; no whole-game or whole-step equivalence claim.','Second engine directory and motion entry formats remain UNKNOWN/PARTIAL. Raw motion DWORDs are not uniformly pointers (Mean second/third, Demon all); do not parse them as a three-flipper array.','Layer counts established by initializer directories; no blind coordinate scan.'],'next_action':'Replace Mean hardcoded layer directory/profile with these descriptor-derived per-table records, then lift Pirate layer callbacks 437460/437bfc/438954 and decode graphics+4 motion entries before whole-step validation.'}
out=ROOT/'analysis/corpus-table-descriptor-levers.json';out.write_text(json.dumps(report,indent=2)+'\n')
print('PASS four complete initializer returns, callback slots and layer switch directories; '+str(out.relative_to(ROOT)))
