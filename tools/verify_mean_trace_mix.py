#!/usr/bin/env python3
"""Compare Mean Retail display-table SFX requests plus synthetic startup music.

Original x86 table callbacks yield descriptor, period, volume and request slot.
Each resulting request is mixed with synthetic startup music into an empty
mixer. This is not an observed simultaneous gameplay recording, natural timing,
previous-voice arbitration, output-device or Amiga parity test.
"""
import argparse, hashlib, json, os, struct, subprocess, sys
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_BLOCK
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_ESP, UC_X86_REG_EIP
from extract_mean_stim import extract
from verify_mean_sample_pcm_original import PROFILES
from verify_retail_final_mix import original_mix
from verify_retail_tracker_pcm import ROOT, GAME, TABLES, EXE_SHA

def sha(data):return hashlib.sha256(data).hexdigest()

def original_effect(exe, dat, spec, frames):
 offset,length,period,volume=spec
 pe=pefile.PE(data=exe);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,pe.get_memory_mapped_image());u.mem_map(0x3000000,0x90000);blocks=set()
 u.hook_add(UC_HOOK_BLOCK,lambda _u,addr,size,_:blocks.add((addr,size)))
 def put(a,v):u.mem_write(a,struct.pack('<I',v & 0xffffffff))
 def run(addr,eax=0,ebx=0,esi=0,edi=0):
  put(0x300f000,0x308fff0)
  for reg,val in ((UC_X86_REG_ESP,0x300f000),(UC_X86_REG_EAX,eax),(UC_X86_REG_EBX,ebx),(UC_X86_REG_ESI,esi),(UC_X86_REG_EDI,edi)):u.reg_write(reg,val)
  u.emu_start(addr,0x308fff0,count=2000000);assert u.reg_read(UC_X86_REG_EIP)==0x308fff0
 assert 0<length<=0x1f000 and offset+length<=len(dat)
 put(0x46eeb8,0x3010000);run(0x44b640,0x20000//6)
 for off,val in ((0,0x3010000),(4,44100),(8,65536)):put(0x3003000+off,val)
 u.mem_write(0x3040000,dat[offset:offset+length]);put(0x3002000,0x3040000);put(0x3002004,length)
 for off,val in ((0,0x3002000),(4,0),(8,0),(12,volume<<10),(16,0x361f0f//period),(20,0)):put(0x3001000+off,val)
 u.mem_write(0x3030000,bytes(frames*2));run(0x44cc00,frames,0x3030000,0x3001000,0x3003000)
 for addr,size in blocks:
  fileoff=pe.get_offset_from_rva(addr-0x400000);assert bytes(u.mem_read(addr,size))==exe[fileoff:fileoff+size]
 return struct.unpack(f'<{frames}h',u.mem_read(0x3030000,frames*2))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
 exe=(GAME/'SLAMTILT.EXE').read_bytes();dat_path=GAME/'DAT/MEAN.DAT';dat=dat_path.read_bytes();assert sha(exe)==EXE_SHA and sha(dat)==TABLES['mean'][0]
 env=dict(os.environ,LD_LIBRARY_PATH=str(a.library.absolute().parent));assert str(a.library.absolute()) in subprocess.check_output(['ldd',str(a.native.resolve())],env=env,text=True)
 native_sha,library_sha=sha(a.native.read_bytes()),sha(a.library.read_bytes())
 eventsfile=a.work/'sequences.json';subprocess.run([sys.executable,str(ROOT/'tools/verify_mean_retail_sfx_sequences.py'),'--output',str(eventsfile)],check=True,stdout=subprocess.DEVNULL);source=json.loads(eventsfile.read_text());assert source['exe_sha256']==EXE_SHA
 profiles={addr:(off,length) for addr,off,length,_ in PROFILES};image=pefile.PE(data=exe).get_memory_mapped_image();cases={}
 for group in source['cases']:
  for event in group['events']:
   desc=int(event['descriptor'],16);demo=desc-0x2c0b4;assert demo in profiles
   off,length=profiles[demo];words=struct.unpack_from('<9I',image,desc-0x400000);assert words[3]==length
   if words[0]:assert struct.unpack_from('>I',dat,(words[0]-1)*4)[0]+8+words[4]==off
   key=(desc,event['period'],event['volume']);cases.setdefault(key,(group['table'],event['tick'],off,length))
 assert len(cases)==13,len(cases)
 subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),'--table','mean','--ticks','3','--dynamic-voices','--output',str(a.work/'music')],check=True,stdout=subprocess.DEVNULL)
 frames=2646;raw=(a.work/'music/mean-first-tick.s16le').read_bytes();music=struct.unpack(f'<{frames*2}h',raw);assert music[::2]==music[1::2]
 stim,_=extract(dat,0,(TABLES['mean'][1],));stimfile=a.work/'mean.stim';stimfile.write_bytes(stim);rows=[]
 for (desc,period,volume),(table,tick,off,length) in cases.items():
  sfx=original_effect(exe,dat,(off,length,period,volume),frames);inputs=[(s,m,m) for s,m in zip(sfx,music[::2])];assert all(-32768<=s+m<=32767 for s,m,_ in inputs)
  mixed,_=original_mix(exe,inputs);original=struct.pack(f'<{frames*2}h',*(v for pair in mixed for v in pair));cmd=[str(a.native.resolve()),str(stimfile.resolve()),str(dat_path),str(TABLES['mean'][2]),str(off),str(length),str(period),str(volume),str(frames)]
  same=[subprocess.check_output(cmd+[str(chunk)],env=env)==original for chunk in (137,882,2646)]
  row={'table':table,'tick':tick,'descriptor':hex(desc),'period':period,'volume':volume,'chunks':[137,882,2646],'status':'EXACT' if all(same) else 'DIFFERENT','pcm_sha256':sha(original)};rows.append(row);print(table,tick,hex(desc),row['status'],flush=True)
 assert sha(a.native.read_bytes())==native_sha and sha(a.library.read_bytes())==library_sha, 'Binary changed during comparison'
 report={'status':'MEASURED_BOUNDED','scope':__doc__,'exe_sha256':sha(exe),'dat_sha256':sha(dat),'native_sha256':sha(a.native.read_bytes()),'library_sha256':sha(a.library.read_bytes()),'frames':frames,'cases':rows};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
 if any(r['status']!='EXACT' for r in rows):raise SystemExit('Mismatch; see report')
 print('PASS: all unique Mean display-table requests')
if __name__=='__main__':main()
