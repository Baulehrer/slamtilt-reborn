from pathlib import Path
import pefile,struct,json,math,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ESP
ROOT=Path(__file__).resolve().parents[1]
p=next((ROOT/'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE'));
assert hashlib.sha256(p.read_bytes()).hexdigest()=='31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00'
image=pefile.PE(str(p)).get_memory_mapped_image(); results=[]
for x,y,px,py,rest in [(287,571,287,571,5),(287.75,571.25,286,570,5),(287.75,571.25,286,570,0),(100.75,230.25,99.25,228.75,2),(6.75,6.25,6,6,5),(0,0,0,0,5),(-1.25,-3.75,-1,-3,5)]:
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000);u.mem_map(0x2000000,0x10000);u.mem_write(0x4298c8,struct.pack('<I',0x1000000));u.mem_write(0x1000000,struct.pack('<4i',*[int(a*65536) for a in (x,y,px,py)]));u.mem_write(0x43e848,struct.pack('<i',rest));u.reg_write(UC_X86_REG_EBX,0);u.reg_write(UC_X86_REG_ESP,0x2008000);u.emu_start(0x407a84,0x407b05,count=1000);got=struct.unpack('<2h',u.mem_read(0x1000010,4));expected=(math.trunc(px*(1-rest/5)+x*rest/5-7),math.trunc(py*(1-rest/5)+y*rest/5-7));assert got==expected,(got,expected);results.append(dict(current=[x,y],previous=[px,py],residual_ms=rest,original_render_xy=list(got),expected=list(expected)))
out={'build_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'VERIFIED','routine':'0x407a84..0x407b01','oracle':'original demo x86 including x87 interpolation and trunc helper under Unicorn','cases':results,'mismatches':0};(ROOT/'analysis/traces/mean-ball-render-anchor-validation.json').write_text(json.dumps(out,indent=2)+'\n');print('7 original x87 render-position cases pass, including interpolation and truncation')
