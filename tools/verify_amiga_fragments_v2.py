#!/usr/bin/env python3
"""Bounded original-68k execution for overlapping streams and whole-object assets."""
import argparse,hashlib,json,struct
from pathlib import Path
import unicorn as uc
from unicorn import m68k_const as reg
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--normalized',type=Path,default=ROOT/'build/amiga-normalized-v2-final');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/amiga-fragments-v2.json');a=p.parse_args()
 code=(ROOT/'build/amiga-main-investigation/hunk0.bin').read_bytes();machine=uc.Uc(uc.UC_ARCH_M68K,uc.UC_MODE_BIG_ENDIAN);machine.ctl_set_cpu_model(reg.UC_CPU_M68K_M68020);machine.mem_map(0,0x400000);machine.mem_write(0,code);machine.mem_write(0x1041a,struct.pack('>I',0x100000));machine.mem_write(0x2f0000,struct.pack('>I',0x300000));machine.reg_write(reg.UC_M68K_REG_A7,0x2f0000);machine.emu_start(0x4f1a,0x300000,count=100000)
 interface=0x103e2
 assert code[0x2d2:0x2d4]==bytes.fromhex('49f9')and struct.unpack_from('>I',code,0x2d4)[0]==interface
 vector=struct.unpack_from('>I',code,interface+0x44)[0];entry=vector-0x24
 assert vector==0x3d8a and entry==0x3d66
 lut=bytes(machine.mem_read(0x4f4a,512));assert len({lut[i:i+2]for i in range(0,512,2)})==256
 source=(ROOT/'build/decoded/full/Pirate.Bin').read_bytes();native=(a.normalized/'PIRATE.DAT').read_bytes();evidence=json.loads((ROOT/'analysis/traces/pirate-amiga-fragments-v2.json').read_text());assert sha(source)==evidence['source']['sha256'];frames=[]
 for frame in evidence['records'][0]['frames']:
  start=int(frame['source'],0);target=int(frame['dest'],0);machine.mem_write(0x200000,source[start:start+961]);machine.reg_write(reg.UC_M68K_REG_A0,0x200000);machine.reg_write(reg.UC_M68K_REG_A7,0x2f0000);machine.emu_start(entry,0x300000,count=100000);assert machine.reg_read(reg.UC_M68K_REG_PC)==0x300000
  end=start+machine.reg_read(reg.UC_M68K_REG_A0)-0x200000;assert end==int(frame['consumed_end'],0)
  pixels=native[target:target+480];assert sha(pixels)==frame['sha256']
  for plane in range(2):
   for y in range(20):
    expected=b''.join(lut[v*2:v*2+2]for v in pixels[plane*240+y*12:plane*240+(y+1)*12])
    assert bytes(machine.mem_read(0x100000+0xd0+plane*2000+y*80,24))==expected
  frames.append({'index':frame['index'],'source':hex(start),'target':hex(target),'consumed_end':hex(end),'sha256':sha(pixels),'status':'PASS'})
 assert frames[0]['consumed_end']=='0x6b8c4'and frames[1]['source']=='0x6b8c3'
 raw=[];pc=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT'
 for table,objects in {'mean':[(0xaaa59,0x1516c4,480),(0xa2453,0x1525c4,480)],'demon':[(0x70ff6,0x10d8f0,480),(0x867b6,0x10e070,480)],'pirate':[(0xa5ce7,0x140ddc,960),(0xa6417,0x14173c,400),(0xa6287,0x1418cc,400)]}.items():
  source=(ROOT/f'build/decoded/full/{table.capitalize()}.Bin').read_bytes();native=(a.normalized/(table.upper()+'.DAT')).read_bytes();oracle=(pc/(table.upper()+'.DAT')).read_bytes()
  for start,target,size in objects:
   actual=native[target:target+size];assert actual==source[start:start+size]==oracle[target:target+size]
   raw.append({'table':table,'source':hex(start),'target':hex(target),'bytes':size,'sha256':sha(actual),'status':'PASS'})
 report={'status':'PASS','oracle':'Original Game hunk0:3d8e..3e22 with executed4f1a LUT initialization','code_hunk_sha256':sha(code),'interface_binding':{'a4_base':'0x103e2','setup_lea':'0x2d2','field_44':'0x3d8a','service_offset':'-0x24','entry':'0x3d66','decoder':'0x3d8e'},'overlap_bytes':1,'compressed_frames':frames,'whole_raw_objects':raw,'limits':['Original source objects only; no full Amiga gameplay parity','All-FF candidate holes remain unmapped without caller evidence']}
 a.report.write_text(json.dumps(report,indent=2)+'\n');print('13 original-68k frames, one-byte overlap, seven whole source objects PASS')
if __name__=='__main__':main()
