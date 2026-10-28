#!/usr/bin/env python3
"""Original4086b8 gameplay camera incl. cached render position/state6 selection."""
import json,struct,subprocess,sys,random,hashlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP
R=Path(__file__).resolve().parents[1];image=(R/'build/mean-prepared/pe-data.bin').read_bytes();u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
def run(c):
 for a,v in [(0x43e7a0,2),(0x43e828,0x1001000),(0x1001010,c['max_scroll']),(0x100101c,c['viewport']),(0x429aec,c['center']),(0x429af0,c['velocity']),(0x43e77c,c['scroll']),(0x43e770,len(c['balls']))]:put(a,v)
 for i,(y,state) in enumerate(c['balls']):
  a=0x1002000+i*128;put(0x4298c8+i*4,a);u.mem_write(a+0x10,struct.pack('<hh',13,y));u.mem_write(a+0x58,struct.pack('<H',state))
 put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000);u.emu_start(0x4086b8,0x100fff0,count=1000)
 return [get(a) for a in [0x429aec,0x429af0,0x43e77c,0x4297f4]]
rng=random.Random(4086);cases=[];expected=[]
for n in range(512):
 c=dict(center=rng.randrange(-100,701)*65536+rng.randrange(65536),velocity=rng.randrange(-20,21)*65536,scroll=rng.randrange(201),viewport=rng.choice([240,400,720,-3]),max_scroll=rng.choice([0,200,400]),balls=[[rng.choice([-32768,-1,0,14,300,571,608,32767]),rng.choice([0,2,3,6,65535])] for _ in range(n%9)])
 cases.append(c);expected.append(run(c))
for profile in range(5):
 center=300*65536;velocity=0;scroll=200
 for tick in range(600):
  # Render positions change only every4ticks, like a supplied50Hz render oracle.
  t=tick//4;y=[571,14+(t*7)%558,571-(t*7)%558,300+(t%20)*4,100][profile]
  balls=[[y,2]] if profile<4 else [[100,6],[500,6]]
  c=dict(center=center,velocity=velocity,scroll=scroll,viewport=400,max_scroll=200,balls=balls);out=run(c);cases.append(c);expected.append(out);center,velocity,scroll=out[:3]
a=json.loads(subprocess.run([sys.argv[1]],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout);assert a==expected,next((i,x,y) for i,(x,y) in enumerate(zip(a,expected)) if x!=y)
(R/'analysis/traces/mean-camera-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='Actual4086b8 gameplay branch, supplied cached renderY/state and viewport;512 boundarycontexts+5x600steps. Attract/menu branch excluded; viewport400/maxscroll200 selected from native logical view, original startup camera initialization not claimed.',cases=cases,expected=expected),separators=(',',':'))+'\n');print('PASS',len(cases),'original camera states')
