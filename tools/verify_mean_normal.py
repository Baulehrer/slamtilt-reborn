#!/usr/bin/env python3
"""Compare bounded native normal evaluator against original 0x40e1d0."""
import argparse, hashlib, json, random, struct, subprocess
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('native', type=Path)
    p.add_argument('--output', type=Path, default=Path('analysis/traces/mean-normal-original.json'))
    p.add_argument('--boundary-extension', action='store_true', help='Compare fractional, outside-playfield and drain boundaries without claiming natural reachability')
    a=p.parse_args()
    exe=next(Path('build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE'))
    dat_path=next(exe.parent.rglob('MEAN.DAT')); raw=exe.read_bytes();dat=dat_path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    assert sha=='31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00'
    image=pefile.PE(data=raw).get_memory_mapped_image()
    image_path=Path('build/mean-normal-pe.bin');image_path.write_bytes(image)
    u=Uc(UC_ARCH_X86, UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image)
    u.mem_map(0x1000000,0x400000);u.mem_write(0x1100000,dat)
    u.mem_map(0x2000000,0x10000);u.mem_map(0x2100000,0x1000)
    rng=random.Random(0x40e1d0); cases=[]
    offsets=[0x959f6,0xb98f6,0xd1956,0xde796,0xd20d6]
    for layer, base in enumerate(offsets):
        xs=[-8,-1,0,1,7,8,311,312,319,320,321,328] if a.boundary_extension else [5,7,8,9,310,311,312,314]
        ys=[-8,-1,0,1,7,8,607,608,615,616,617,624] if a.boundary_extension else [7,8,607,608,615,616,618,619]
        fractions=[0,32768,65535] if a.boundary_extension else [0]
        for x in xs:
            for y in ys:
                for shift in [0,7]:
                    for ox,oy in [(-196096,261376),(196096,261376),(0,0)]:
                        for fraction in fractions:
                            cases.append(((x<<16)+fraction,(y<<16)+fraction,base+shift,ox,oy))
        for _ in range(1000):
            cases.append((rng.randrange(8<<16,312<<16),rng.randrange(8<<16,616<<16),base+rng.randrange(8),rng.randrange(-196096,196097),rng.randrange(261377)))
    expected=[]
    for x,y,base,ox,oy in cases:
        u.mem_write(0x1000000,struct.pack('<ii',x,y));u.mem_write(0x1000044,struct.pack('<I',0x1100000+base))
        u.mem_write(0x43e71c,struct.pack('<i',ox));u.mem_write(0x43e410,struct.pack('<i',oy))
        u.mem_write(0x200f000,struct.pack('<I',0x2100000));u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000)
        u.emu_start(0x40e1d0,0x2100000,count=10000)
        assert u.reg_read(UC_X86_REG_ESP)==0x200f004
        expected.append(u.reg_read(UC_X86_REG_EAX))
    packed=b''.join(struct.pack('<IIIII',*(v&0xffffffff for v in c)) for c in cases)
    result=subprocess.run([str(a.native),str(image_path),str(dat_path)],input=packed,stdout=subprocess.PIPE,check=True).stdout
    actual=list(struct.unpack('<'+'I'*len(expected),result))
    for i,(left,right) in enumerate(zip(expected,actual)):
        if left!=right:raise AssertionError((i,cases[i],left,right))
    fixture=dict(build_sha256=sha,dat_sha256=hashlib.sha256(dat).hexdigest(),routine='0x40e1d0..0x40e83e',cases=len(cases),edge_cases=len(cases)-5000,random_cases=5000,pointer_shifts=list(range(8)),nudge_offsets=True,input_sha256=hashlib.sha256(packed).hexdigest(),output_sha256=hashlib.sha256(result).hexdigest(),status='VERIFIED',scope='Original normal evaluator only; DAT linear addressing preserved without geometric clamping')
    if a.boundary_extension:
        signed=[v if v<0x80000000 else v-0x100000000 for v in actual]
        invalid=[v for v in signed if v < -1 or v > 4095]
        assert not invalid, ('Original return outside native guard domain',invalid[:10])
        fixture.update(boundary_extension=True,x_integer=xs,y_integer=ys,fractional_low_words=fractions,natural_reachability_claimed=False,return_min=min(signed),return_max=max(signed),no_normal_returns=signed.count(-1),invalid_native_guard_returns=len(invalid))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(fixture,indent=2)+'\n'); print(json.dumps(fixture))
if __name__=='__main__':main()
