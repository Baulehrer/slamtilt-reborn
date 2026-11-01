#!/usr/bin/env python3
"""Compare unique recorded Pirate same-step SFX pairs plus synthetic startup music.

Pairs come from pinned original request traces, but this reconstructed mix
starts all voices together in an empty mixer. Original in-game voice arbitration,
actual tracker state, event cadence and physical playback are not modeled.
"""
import argparse, collections, hashlib, json, os, struct, subprocess, sys
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_BLOCK
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_ESP, UC_X86_REG_EIP
from extract_mean_stim import extract
from verify_retail_final_mix import original_mix
from verify_retail_tracker_pcm import ROOT, GAME, TABLES, EXE_SHA

def sha(data): return hashlib.sha256(data).hexdigest()

def original_effects(exe, dat, specs, frames):
 pe=pefile.PE(data=exe);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,pe.get_memory_mapped_image());u.mem_map(0x3000000,0x90000);blocks=set()
 u.hook_add(UC_HOOK_BLOCK,lambda _u,addr,size,_:blocks.add((addr,size)))
 def put(a,v):u.mem_write(a,struct.pack('<I',v & 0xffffffff))
 def run(addr,eax=0,ebx=0,esi=0,edi=0):
  put(0x300f000,0x308fff0)
  for reg,val in ((UC_X86_REG_ESP,0x300f000),(UC_X86_REG_EAX,eax),(UC_X86_REG_EBX,ebx),(UC_X86_REG_ESI,esi),(UC_X86_REG_EDI,edi)):u.reg_write(reg,val)
  u.emu_start(addr,0x308fff0,count=2000000);assert u.reg_read(UC_X86_REG_EIP)==0x308fff0
 put(0x46eeb8,0x3010000);run(0x44b640,0x20000//6)
 for off,val in ((0,0x3010000),(4,44100),(8,65536)):put(0x3003000+off,val)
 for i,(off,length,period,_,_) in enumerate(specs):
  assert 0<length<=0x1f000 and off+length<=len(dat)
  sample,voice,entry=0x3040000+i*0x20000,0x3001000+i*0x20,0x3002000+i*8
  u.mem_write(sample,dat[off:off+length]);put(entry,sample);put(entry+4,length)
  for delta,val in ((0,entry),(4,0),(8,0),(12,64<<10),(16,0x361f0f//period),(20,0)):put(voice+delta,val)
 u.mem_write(0x3030000,bytes(frames*2))
 for i in range(2):run(0x44cc00,frames,0x3030000,0x3001000+i*0x20,0x3003000)
 for addr,size in blocks:
  off=pe.get_offset_from_rva(addr-0x400000);assert bytes(u.mem_read(addr,size))==exe[off:off+size]
 return struct.unpack(f'<{frames}h',u.mem_read(0x3030000,frames*2))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
 fixture=ROOT/'analysis/traces/pirate-audio-events.json'; trace=json.loads(fixture.read_text());assert trace['build_sha256']==EXE_SHA and trace['dat_sha256']==TABLES['pirate'][0]
 exe=(GAME/'SLAMTILT.EXE').read_bytes();dat_path=GAME/'DAT/PIRATE.DAT';dat=dat_path.read_bytes();assert sha(exe)==EXE_SHA and sha(dat)==TABLES['pirate'][0]
 profiles={int(x['address'],0):x for x in json.loads((ROOT/'analysis/pirate-audio-static.json').read_text())['sfx_descriptors']}; env=dict(os.environ,LD_LIBRARY_PATH=str(a.library.absolute().parent)); assert str(a.library.absolute()) in subprocess.check_output(['ldd',str(a.native.resolve())],env=env,text=True)
 native_sha,library_sha=sha(a.native.read_bytes()),sha(a.library.read_bytes())
 groups={}
 for case in trace['cases']:
  ticks=collections.defaultdict(list)
  for e in case['events']:
   if e[1]==0x5c:ticks[e[0]].append(e)
  for tick,events in ticks.items():
   if len(events)==2:
    key=tuple((e[2],e[3],e[4]) for e in events);groups.setdefault(key,(case['case'],tick))
 assert len(groups)==7,len(groups)
 subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),'--table','pirate','--ticks','3','--dynamic-voices','--output',str(a.work/'music')],check=True,stdout=subprocess.DEVNULL)
 frames=2646;raw=(a.work/'music/pirate-first-tick.s16le').read_bytes();music=struct.unpack(f'<{frames*2}h',raw);assert music[::2]==music[1::2]
 stim,_=extract(dat,0,(TABLES['pirate'][1],));stimfile=a.work/'pirate.stim';stimfile.write_bytes(stim); pe=pefile.PE(data=exe).get_memory_mapped_image();cases=[]
 for group,(case,tick) in groups.items():
  specs=[]
  for field1,field2,address in group:
   desc=profiles[address];off=int(desc['pcm_offset'],0);length=desc['length'];period=desc['period'];assert sha(dat[off:off+length])==desc['pcm_sha256'];words=struct.unpack_from('<9I',pe,address-0x400000);assert words[1:4]==(period,64,length);specs.append((off,length,period,field1,field2))
  sfx=original_effects(exe,dat,specs,frames);samples=[(s,m,m) for s,m in zip(sfx,music[::2])];assert all(-32768<=s+m<=32767 for s,m,_ in samples)
  mixed,_=original_mix(exe,samples);original=struct.pack(f'<{frames*2}h',*(v for pair in mixed for v in pair));cmd=[str(a.native.resolve()),str(stimfile.resolve()),str(dat_path),str(TABLES['pirate'][2]),*(str(v) for spec in specs for v in spec),str(frames)]
  same=[]
  for chunk in (137,882,2646):same.append(subprocess.check_output(cmd+[str(chunk)],env=env)==original)
  row={'case':case,'tick':tick,'events':[[x[0],x[1],hex(x[2])] for x in group],'chunks':[137,882,2646],'status':'EXACT' if all(same) else 'DIFFERENT','pcm_sha256':sha(original)};cases.append(row);print(case,tick,row['status'],flush=True)
 assert sha(a.native.read_bytes())==native_sha and sha(a.library.read_bytes())==library_sha, 'Binary changed during comparison'
 report={'status':'MEASURED_BOUNDED','scope':__doc__,'exe_sha256':sha(exe),'dat_sha256':sha(dat),'fixture_sha256':sha(fixture.read_bytes()),'native_sha256':sha(a.native.read_bytes()),'library_sha256':sha(a.library.read_bytes()),'frames':frames,'cases':cases};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
 if any(x['status']!='EXACT' for x in cases):raise SystemExit('Mismatch; see report')
 print('PASS: all unique same-tick SFX pairs')
if __name__=='__main__':main()
