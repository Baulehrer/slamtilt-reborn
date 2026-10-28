#!/usr/bin/env python3
"""Bounded40a0e8 original oracle; supplied synthetic lookup separates arithmetic."""
import hashlib,json,random,struct,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x20000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
lookup=list(struct.unpack('<10000H',image[0x32ecc:0x37cec]))
u.mem_write(0x1000000,struct.pack('<10000H',*lookup));put(0x43e76c,0x1000000)
rng=random.Random(40);cases=[];expected=[]
patterns=[[],[[0,10,10,0]],[[-1,100,200,0]],[[1,100,200,0]],[[2,100,200,0]],[[1,-1000,-1000,0],[2,100,200,0]],[[0,0,0,0],[-1,100,200,0],[1,105,205,1],[2,98,198,-1]]]
for nodes in patterns:
 for suppressed in [False,True]:
  for i in range(15):
   b=bytearray(rng.randbytes(100));x=100+rng.randrange(-30,31);y=200+rng.randrange(-30,31)
   struct.pack_into('<ii',b,0,x*65536+rng.randrange(65536),y*65536+rng.randrange(65536))
   struct.pack_into('<ii',b,0x14,rng.randrange(-500000,500001),rng.randrange(-500000,500001))
   # Original1a DWORD overlaps18 velocity highword and1c WORD; control signed highword.
   struct.pack_into('<H',b,0x1c,rng.choice([0,1,65535,120]))
   u.mem_write(0x1008000,bytes(b));put(0x43d864,int(suppressed));put(0x43d860,0x1009000 if nodes else 0)
   for j,n in enumerate(nodes):u.mem_write(0x1009000+j*12,struct.pack('<Ihhhh',0x1009000+(j+1)*12 if j+1<len(nodes) else 0,*n))
   put(0x101f000,0x101fff0);u.reg_write(UC_X86_REG_ESP,0x101f000);u.reg_write(UC_X86_REG_EAX,0x1008000);u.emu_start(0x40a0e8,0x101fff0,count=10000)
   cases.append(dict(ball=list(b),nodes=nodes,suppressed=suppressed,lookup=lookup));expected.append(dict(ball=list(u.mem_read(0x1008000,100)),ok=True))
# Deterministic active original-node arithmetic trace; this is point-force-only,
# not a claim of100full gameplay steps.
b=bytearray(100);struct.pack_into('<ii',b,0,264*65536+32768+10000,181*65536+32768-7000)
struct.pack_into('<ii',b,0x14,35000,-22000);struct.pack_into('<H',b,0x1c,32)
nodes=[[-1,264,181,32]];trace=[list(b)]
for tick in range(100):
 u.mem_write(0x1008000,bytes(b));put(0x43d864,0);put(0x43d860,0x1009000)
 u.mem_write(0x1009000,struct.pack('<Ihhhh',0,*nodes[0]))
 put(0x101f000,0x101fff0);u.reg_write(UC_X86_REG_ESP,0x101f000);u.reg_write(UC_X86_REG_EAX,0x1008000);u.emu_start(0x40a0e8,0x101fff0,count=10000)
 cases.append(dict(ball=list(b),nodes=nodes,suppressed=False,lookup=lookup))
 b=bytearray(u.mem_read(0x1008000,100));expected.append(dict(ball=list(b),ok=True));trace.append(list(b))
(r/'analysis/traces/mean-point-force-100.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),routine='40a0e8',lookup='432ecc',scope='100point-force calls only; positions unchanged, nointegrator/collision/gameplay',nodes=nodes,tick_count=100,initial_state=trace[0],final_state=trace[-1],states=trace),separators=(',',':'))+'\n')
if len(sys.argv)>1:exe=sys.argv[1]
else:
 exe=str(r/'build/oracle/mean-point-force-probe')
 subprocess.run(['c++','-std=c++17','-O2','-ffunction-sections','-Wl,--gc-sections','-Isrc','tests/mean_point_force_probe.cpp','src/physics/mean_point_force.cpp','src/physics/mean_step.cpp','-o',exe],cwd=r,check=True)
actual=json.loads(subprocess.check_output([exe],input=json.dumps(cases),text=True))
assert actual==expected,next((i,[(hex(j),x,y) for j,(x,y) in enumerate(zip(a['ball'],b['ball'])) if x!=y]) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b)
for c in cases:del c['lookup']
(r/'analysis/traces/mean-point-force-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='40a0e8..40a35b; original LUT432ecc; full100objectbytes; EARLY EXIT original retained;1aDWORD overlap retained',lookup_source="user PE VA0x432ecc",lookup_sha256=hashlib.sha256(image[0x32ecc:0x37cec]).hexdigest(),cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'original point-force states exact')
