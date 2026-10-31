#!/usr/bin/env python3
"""Check Demon SFX descriptor period/volume in retained original x86 replays.

Uses actual Original service-entry observations on private Retail snapshots.
Mode scenarios include diagnostic contacts; this is not all-path proof.
Descriptor fields are sampled at request time, not at later queue consumption.
No original audio or game data is copied into the report.
"""
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_EBX
from pirate_adventure_oracle import Original, ROOT
from space_asteroid_oracle import Chain

GAME=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
BUILD_SHA='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_SHA='0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--native',type=Path,default=ROOT/'build/native/sfx_profiles_probe')
parser.add_argument('--output',type=Path,default=ROOT/'build/gameplay-verification/demon-sfx-descriptor-state.json')
args=parser.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def signed(n):return n if n<0x80000000 else n-0x100000000
assert sha(GAME/'SLAMTILT.EXE')==BUILD_SHA and sha(GAME/'DAT/DEMON.DAT')==DAT_SHA
profile_path=ROOT/'analysis/demon-audio-profile.json'
profiles=json.loads(profile_path.read_text())['sample_profiles']
expected={int(p['descriptor'],0):(p['period'],64) for p in profiles}
assert len(expected)==14
native=json.loads(subprocess.check_output([str(args.native.resolve())]))['demon']
assert len(native)==len(profiles)
for row in native:
 p=next(p for p in profiles if int(p['descriptor'],0)==row['descriptor'])
 assert (row['offset'],row['length'],row['period'])==(int(p['offset'],0),p['length'],p['period'])
cases=('legal-game','video-wolf-shoot','clock-award-4')
counts=Counter();rows=[]
for case in cases:
 path=ROOT/f'build/oracle/demon-modes/{case}-rewards.json'
 fixture=ROOT/f'analysis/traces/demon-{case}-rewards.json'
 source=json.loads(path.read_text());pin=json.loads(fixture.read_text())
 for k in ('inputs','diagnostic_shots','tick_count','audio_events','build_sha256','dat_sha256','original_reset_exact'):assert source[k]==pin[k],(case,k)
 assert source['original_reset_exact']
 recorded=source['audio_events']
 assert source['build_sha256']==BUILD_SHA and source['dat_sha256']==DAT_SHA
 m=Original(ROOT/'build/oracle/demon-full-game',table='demon')
 events=[]; local=Counter();tick=0
 def observe(u,_pc,_size,_):
  descriptor=u.reg_read(UC_X86_REG_EAX)
  event=[tick+1,0x5c,signed(u.reg_read(UC_X86_REG_EDX)),signed(u.reg_read(UC_X86_REG_EBX)),descriptor]
  events.append(event)
  fields=(m.get(descriptor+4),m.get(descriptor+8))
  assert descriptor in expected and fields==expected[descriptor],(case,tick,hex(descriptor),fields,expected.get(descriptor))
  local[(descriptor,*fields)]+=1
 m.u.hook_add(UC_HOOK_CODE,observe,begin=0x406600,end=0x406600)
 inputs={};shots={}
 for e in source['inputs']:inputs.setdefault(e['tick'],[]).append(e)
 for e in source.get('diagnostic_shots',[]):shots.setdefault(e['tick'],[]).append(e)
 assert m.ball()==source['states'][0]
 for tick in range(source['tick_count']):
  for e in inputs.get(tick,[]):Chain.apply(m,e)
  for e in shots.get(tick,[]):m.shot(e['layer'],e['x'],e['y'],e.get('ball',0))
  m.run(0x405234,(tick+1)*5,until=0x405486)
  if (tick+1)%4==0:m.run(0x408da8)
  assert m.ball()==source['states'][tick+1],(case,tick,'ball mismatch')
 assert events==[e for e in recorded if e[1]==0x5c],(case,'sound events')
 counts.update(local)
 rows.append({'case':case,'ticks':source['tick_count'],'diagnostic_contacts':len(source.get('diagnostic_shots',[])),'source_sha256':sha(path),'fixture_sha256':sha(fixture),'events':len(events),'fields':[{'descriptor':hex(d),'period':p,'volume':v,'events':n} for (d,p,v),n in sorted(local.items())]})
 print(case,len(events),'matching original SFX descriptor states',flush=True)
missing=sorted(set(expected)-{d for d,_,_ in counts})
report={'status':'VERIFIED_BOUNDED','original_exe_sha256':BUILD_SHA,'dat_sha256':DAT_SHA,'profile_sha256':sha(profile_path),'native_profile_probe_sha256':sha(args.native),'scope':__doc__,'cases':rows,'descriptor_count':len(expected),'observed_descriptors':len(expected)-len(missing),'unobserved_descriptors':[hex(d) for d in missing],'events':sum(counts.values()),'ticks':sum(r['ticks'] for r in rows),'unvisited_mutations':'UNKNOWN'}
out=args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print('PASS',report['events'],'events across',report['observed_descriptors'],'Demon descriptors;',report['ticks'],'original ticks')
