#!/usr/bin/env python3
"""Composed Pirate contact+separation against actual Retail40a884, real DAT geometry."""
import hashlib,json,random,struct,subprocess,sys
from pathlib import Path
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_MEM_INVALID
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1];report=json.loads((R/'analysis/pirate-engine-validation.json').read_text())
exe=R/report['build'];raw=exe.read_bytes();assert hashlib.sha256(raw).hexdigest()==report['build_sha256']
datpath=exe.parent/'DAT/PIRATE.DAT';dat=datpath.read_bytes();lut=(R/'build/mean-prepared/lookup.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32)
for a,n in [(0x400000,0x100000),(0x1000000,0x400000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(a,n)
u.mem_write(0x400000,pefile.PE(data=raw).get_memory_mapped_image());u.mem_write(0x1100000,dat);u.mem_write(0x1010000,lut)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
layers=json.loads((R/'analysis/table-profiles.json').read_text())['tables']['pirate']['layers'];g=layers[0]
for a,v in [(0x454b68,0x1000000),(0x46c66c,0x1010000),(0x46c648,0x1010800),(0x46c644,0x465958),(0x46e2b4,0x1005000),(0x46e2ec,0x1100000+g['hit_offset']),(0x46e2e8,0x1100000+g['normal_offset']),(0x46e2f0,0x1100000+g['render_offset']),(0x46e2e4,g['stride']),(0x46e2de,g['planes']<<16),(0x46c604,0),(0x46c5f8,0),(0x46c600,0),(0x46c4a4,0)]:put(a,v)
def fault(uc,access,address,size,value,user):
 print("oracle fault",hex(uc.reg_read(UC_X86_REG_EIP)),hex(address));return False
u.hook_add(UC_HOOK_MEM_INVALID,fault)
rng=random.Random(1996);cases=[];expected=[]
for sample in report['normal_samples']:
 if sample['angle']<0:continue
 layer=sample['layer'];l=layers[layer];x,y=sample['xy']
 material=sum(1<<p for p in range(l['planes']) if dat[l['hit_offset']+l['stride']*(p+1)+y*40+x//8]&(128>>(x&7)))
 supported=not(layer==0 and material in [3,4,5,6] or layer==1 and material==1)
 b=bytearray(100);struct.pack_into('<iiii',b,0,x<<16,y<<16,x<<16,y<<16)
 struct.pack_into('<ii',b,0x14,rng.randrange(-8*65536,8*65536),rng.randrange(-8*65536,8*65536))
 struct.pack_into('<H',b,0x1e,sample['angle']);struct.pack_into('<H',b,0x48,layer);struct.pack_into('<H',b,0x3c,material)
 for o,v in [(0x40,0x1100000+l['hit_offset']),(0x44,0x1100000+l['normal_offset']),(0x54,0x1100000+l['render_offset']),(0x4c,l['stride']),(0x50,l['planes'])]:struct.pack_into('<I',b,o,v)
 cases.append(dict(bytes=list(b),layer=layer,xy=[x,y],material=material))
 if not supported:expected.append(dict(supported=False,bytes=list(b)));continue
 put(0x46c670,sample["angle"]);u.mem_write(0x1000000,bytes(b));put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0)
 u.emu_start(0x40a884,0x2100000,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x2100000
 expected.append(dict(supported=True,bytes=list(u.mem_read(0x1000000,100))))
outdir=R/'build/oracle/pirate';outdir.mkdir(parents=True,exist_ok=True);casefile=outdir/'wall-cases.json';casefile.write_text(json.dumps(cases))
a=json.loads(subprocess.check_output([sys.argv[1],str(casefile),str(datpath),str(R/'build/mean-prepared/lookup.bin')],text=True));assert len(a)==len(expected)
for i,(a,b) in enumerate(zip(a,expected)):
 assert a==b,(i,cases[i]['layer'],cases[i]['xy'],cases[i]['material'],[(hex(o),x,y) for o,(x,y) in enumerate(zip(a['bytes'],b['bytes'])) if x!=y])
(R/'analysis/traces/pirate-wall-original.json').write_text(json.dumps(dict(scope='Actual Retail40a884 includes actual40aa10 separation; actual Pirate bitmap materials/normals and synthetic velocities; moving-surface offsets0;unsupported rules explicitfalse unchanged;no full gameplay wrapper',build_sha256=report['build_sha256'],cases=cases,expected=expected),separators=(',',':'))+'\n')
print('PASS',len(cases),'Pirate bitmap contact cases;',sum(x['supported'] for x in expected),'actual composed contacts+separations')
