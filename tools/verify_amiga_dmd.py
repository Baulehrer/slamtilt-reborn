#!/usr/bin/env python3
"""Execute the original bounded 68k DMD routine against every mapped native bank.
Development-only Unicorn oracle; never used by the port/importer.
"""
import argparse,hashlib,json,struct,time
from pathlib import Path
import unicorn as uc
from unicorn import m68k_const as reg
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--normalized',type=Path,default=ROOT/'build/amiga-normalized-final');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/amiga-dmd-original.json');a=p.parse_args()
 code=(ROOT/'build/amiga-main-investigation/hunk0.bin').read_bytes();index=json.loads((ROOT/'analysis/traces/amiga-dmd-banks.json').read_text())
 machine=uc.Uc(uc.UC_ARCH_M68K,uc.UC_MODE_BIG_ENDIAN);machine.ctl_set_cpu_model(reg.UC_CPU_M68K_M68020);machine.mem_map(0,0x400000);machine.mem_write(0,code);machine.mem_write(0x1041a,struct.pack('>I',0x100000));machine.mem_write(0x2f0000,struct.pack('>I',0x300000))
 machine.reg_write(reg.UC_M68K_REG_A7,0x2f0000)
 machine.emu_start(0x4f1a,0x300000,count=100000)
 lut_bytes=bytes(machine.mem_read(0x4f4a,512))
 lut=[lut_bytes[i*2:i*2+2]for i in range(256)];assert len(set(lut))==256
 cases=[]
 for table,row in index['tables'].items():
  source=(ROOT/f'build/decoded/full/{table.capitalize()}.Bin').read_bytes();native=(a.normalized/(table.upper()+'.DAT')).read_bytes();assert sha(source)==row['source_sha256']
  tested=0;combined=hashlib.sha256()
  for bank in row['banks']:
   offsets=struct.unpack_from('>'+str(bank['count'])+'I',source,bank['directory'])
   for i,offset in enumerate(offsets):
    start=bank['directory']+offset;data=source[start:start+961]
    machine.mem_write(0x200000,data);machine.reg_write(reg.UC_M68K_REG_A0,0x200000);machine.reg_write(reg.UC_M68K_REG_A7,0x2f0000)
    machine.emu_start(0x3d8e,0x300000,count=100000)
    assert machine.reg_read(reg.UC_M68K_REG_PC)==0x300000
    count=machine.reg_read(reg.UC_M68K_REG_A0)-0x200000
    if i+1<len(offsets):assert start+count<=bank['directory']+offsets[i+1]
    pixels=native[bank['target']+i*480:bank['target']+(i+1)*480]
    for plane in range(2):
     for y in range(20):
      expected=b''.join(lut[x]for x in pixels[plane*240+y*12:plane*240+(y+1)*12])
      actual=bytes(machine.mem_read(0x100000+0xd0+plane*2000+y*80,24))
      assert actual==expected,(table,hex(bank['directory']),i,plane,y)
      combined.update(actual)
    tested+=1
  if table=='mean':
   contact=json.loads((ROOT/'analysis/traces/amiga-contact-frames.json').read_text())
   for item in contact['records']:
    at=int(item['native'],0);width,height=item['dimensions'];size=width*height*item['frames']
    assert sha(native[at:at+size])==item['amiga_indexed_sha256'],item['native']
  cases.append({'table':table,'frames':tested,'native_sha256':sha(native),'physical_output_sha256':combined.hexdigest(),'status':'PASS' if tested else 'NOT_APPLICABLE_UNCOMPRESSED'})
  print(table,tested,'original 68k frames verified',flush=True)
 a.report.write_text(json.dumps({'status':'PASS','oracle':'Unicorn M68020 executes original Game.exe hunk0:3d8e..3e22, original LUT initialized by4f1a..4f48','code_hunk_sha256':sha(code),'routine_sha256':sha(code[0x3d8e:0x3e26]),'cases':cases,'limitations':['Bounded display routine, not full Amiga execution','Uncompressed Demon frames use separate existing copy mappings']},indent=2)+'\n')
if __name__=='__main__':main()
