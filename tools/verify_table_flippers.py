#!/usr/bin/env python3
"""Actual Retail graphics flipper records against reused Demo bounded lift."""
import argparse,hashlib,json,random,struct,subprocess
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native',type=Path);ap.add_argument('--contacts',action='store_true',help='Diagnostic only: contact normal/scratch mismatch remains unresolved');args=ap.parse_args()
 exe=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE';raw=exe.read_bytes()
 sha=hashlib.sha256(raw).hexdigest();assert sha=='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
 pe=pefile.PE(data=raw);image=bytearray(pe.get_memory_mapped_image());image.extend(bytes(0x100000-len(image)))
 for section in pe.sections:
  if section.Name.rstrip(b'\0')==b'.bss':
   a=section.VirtualAddress;n=max(section.Misc_VirtualSize,section.SizeOfRawData);image[a:a+n]=bytes(n)
 work=ROOT/'build/oracle/table-flippers';work.mkdir(parents=True,exist_ok=True);mapped=work/'retail-image.bin';mapped.write_bytes(image)
 probe=args.native or work/'table_flipper_probe'
 if not args.native:subprocess.run(['c++','-std=c++17','-O2','-I'+str(ROOT/'src'),str(ROOT/'tests/table_flipper_probe.cpp'),str(ROOT/'src/assets/table_flippers.cpp'),str(ROOT/'build/native/libmean_flipper_lift.a'),'-o',str(probe)],check=True)
 report={'schema':1,'build_sha256':sha,'addresses':{'parameter_copy':'0x405057..0x405153','pose_full':'0x409154','pose_demo':'0x4084bc','contact_full':'0x409ce8','contact_demo':'0x409050','response_full':'0x40a380','response_demo':'0x4096e8'},'tables':[],'scope':'VERIFIED parameter copy and 240 input-to-pose steps per table, complete 78 runtime bytes. Original zero-initialized BSS default rest, synthetic edge schedule. Contact normal/scratch comparison remains unresolved and is excluded; no response, gameplay or sprite proof.'}
 for table in json.loads((ROOT/'analysis/corpus-table-descriptor-levers.json').read_text())['tables']:
  u=Uc(UC_ARCH_X86,UC_MODE_32)
  for a,n in [(0x400000,0x100000),(0x1000000,0x1000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(a,n)
  u.mem_write(0x400000,bytes(image))
  def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def run(a,stop=0x2100000):
   put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.emu_start(a,stop,count=100000);assert u.reg_read(UC_X86_REG_EIP)==stop
  graphics=int(table['graphics_descriptor'],16);put(0x46c644,int(table['returned_descriptor'],16));run(0x405057,0x405153)
  poses=bytes(u.mem_read(0x46c748,78));rng=random.Random(1996);inputs=[];expected=[]
  for tick in range(240):
   left=1 if tick in (5,70,180) else 0xffffffff if tick in (30,150,220) else 0
   right=1 if tick in (10,100,170) else 0xffffffff if tick in (60,140,230) else 0
   inputs.append([left,right])
   for a,v in [(0x454b58,left),(0x454b5c,right),(0x454b60,right)]:put(a,v)
   run(0x409154);expected.append(list(u.mem_read(0x46c748,78)))
  cases=[dict(operation='pose',inputs=inputs)];outputs=[expected];hits=0
  # Restore actual copied default poses. The lookup values are shared assets;
  # original Full uses its own static atan table, demo lift uses original Demo.
  u.mem_write(0x46c748,poses)
  globals_=(ROOT/'build/mean-prepared/engine-globals.bin').read_bytes()
  # Sine table pointer is read by the contact/response routines.
  lut=(ROOT/'build/mean-prepared/lookup.bin').read_bytes();u.mem_map(0x1100000,0x10000);u.mem_write(0x1100000,lut)
  put(0x46c648,0x1100800);put(0x46c66c,0x1100000)
  demoimage=bytearray((ROOT/'build/mean-prepared/pe-data.bin').read_bytes());demoimage.extend(bytes(0x100000-len(demoimage)));demoimage[0x3e700:0x3e7a0]=globals_
  import capstone
  from capstone.x86 import X86_OP_MEM
  cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
  aa=list(cs.disasm(demoimage[0x9050:0x9bb4],0x409050));bb=list(cs.disasm(image[0x9ce8:0xa84c],0x409ce8));assert len(aa)==len(bb)
  mappings={}
  for a,b in zip(aa,bb):
   assert a.mnemonic==b.mnemonic
   for x,y in zip(a.operands,b.operands):
    if x.type==X86_OP_MEM and not x.mem.base and not x.mem.index and x.mem.disp>=0x400000:
     mappings[x.mem.disp]=y.mem.disp
  for a,b in mappings.items():
   if a in (0x43e744,0x43e764,0x43e728,0x43e730):continue
   put(b,struct.unpack_from('<I',demoimage,a-0x400000)[0])
  aux=struct.unpack_from('<I',demoimage,0x3e730)[0];u.mem_write(0x1104000,bytes(demoimage[aux-0x400000:aux-0x400000+8192]));put(0x46c640,0x1104000)
  atan=struct.unpack_from('<I',demoimage,0x3e728)[0];u.mem_write(0x1103000,bytes(demoimage[atan-0x400000:atan-0x400000+2050]));put(0x46c638,0x1103000)
  third=struct.unpack_from('<H',image,graphics-0x400000+0x1c)[0]
  for i in range(600 if args.contacts else 0):
   u.mem_write(0x46c748,poses)
   for a,b_ in mappings.items():
    if a not in (0x43e744,0x43e764,0x43e728,0x43e730):put(b_,struct.unpack_from('<I',demoimage,a-0x400000)[0])
   index=i%(3 if third else 2);desc=0x46c77c-index*26;px,py=struct.unpack('<hh',u.mem_read(desc,4))
   b=bytearray(100);struct.pack_into('<ii',b,0,(px+rng.randrange(-65,66))<<16,(py+rng.randrange(-20,21))<<16)
   struct.pack_into('<ii',b,0x14,rng.randrange(-393216,393216),rng.randrange(-393216,393216));struct.pack_into('<H',b,0x28,40)
   cases.append(dict(bytes=list(b),index=index,response=False))
   u.mem_write(0x1000000,bytes(b));u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,desc);run(0x409ce8);result=u.reg_read(UC_X86_REG_EAX)
   if result==0:
    hits+=1
    if False:u.reg_write(UC_X86_REG_EAX,0x1000000);u.reg_write(UC_X86_REG_EDX,desc);run(0x40a380)
   outputs.append(dict(result=result,bytes=list(u.mem_read(0x1000000,100)),scratch=struct.unpack('<I',u.mem_read(0x46c660,4))[0]))
  path=work/(table['table']+'-cases.json');path.write_text(json.dumps(cases));actual=json.loads(subprocess.check_output([str(probe),str(ROOT/'build/mean-prepared'),str(mapped),hex(graphics),str(path)],text=True))
  diffs=[i for i,(a,b) in enumerate(zip(outputs,actual)) if a!=b]
  if diffs:
   n=diffs[0];print(table['table'],'firstdiff',n,'expected',outputs[n] if n else outputs[n][0],'actual',actual[n] if n else actual[n][0]);raise SystemExit(1)
  assert len(outputs)==len(actual)
  record={'table':table['table'],'graphics_descriptor':hex(graphics),'parameter_addresses':[hex(struct.unpack_from('<I',image,graphics-0x400000+0xc+j*4)[0]) for j in range(3 if third else 2)],'field_1c':third,'pose_steps':240,'distinct_poses':len({bytes(x) for x in expected}),'initial_runtime_bytes':list(poses),'state_after_100_steps':expected[99],'final_runtime_bytes':expected[-1],'trace_sha256':hashlib.sha256(bytes(v for state in expected for v in state)).hexdigest(),'contact_cases':600 if args.contacts else 0,'contact_hits':hits,'differences':[]};report['tables'].append(record);print('PASS',table['table'],record['pose_steps'],'full runtime states;',record['distinct_poses'],'distinct poses')
 (ROOT/'analysis/traces/table-flippers-original.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
