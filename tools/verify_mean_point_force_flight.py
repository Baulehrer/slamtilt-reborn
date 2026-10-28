#!/usr/bin/env python3
"""Original active-point-force flight; synthetic starts, no live trajectory claim."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1]
ns={'__file__':str(ROOT/'tools/trace_mean_multiball_flight.py')};exec((ROOT/'tools/trace_mean_multiball_flight.py').read_text().split('u.mem_write(0x1000000,bytes(100));run')[0],ns)
u,put,run=ns['u'],ns['put'],ns['run'];prep=ROOT/'build/mean-prepared'
# Match native oracle mode: suppress table-switch/rules dispatch, retaining actual
# integration, bitmap contact, normal decoding, wall response and separation.
def ret(uc,a,n,c):
 sp=uc.reg_read(UC_X86_REG_ESP); target=struct.unpack('<I',uc.mem_read(sp,4))[0]
 uc.reg_write(UC_X86_REG_ESP,sp+4);uc.reg_write(UC_X86_REG_EIP,target)
u.hook_add(UC_HOOK_CODE,ret,begin=0x408b04,end=0x408b04)
force_calls=[0]
def force_seen(uc,a,n,c):force_calls[0]+=1
u.hook_add(UC_HOOK_CODE,force_seen,begin=0x40a0e8,end=0x40a0e8)
put(0x1001030,2)
poses=list(struct.unpack('<27I',(prep/'flipper-state.bin').read_bytes()))
globals_=list(struct.unpack('<40I',(prep/'engine-globals.bin').read_bytes()))
base=json.loads((ROOT/'analysis/traces/mean-flight-100.json').read_text())
outdir=ROOT/'build/oracle/point-force-flight';outdir.mkdir(exist_ok=True)
cases=[];expected=[];summary=[]
for index,(x,y,vx,vy) in enumerate([(264,180,32768,16384),(250,170,20000,30000),(280,190,-25000,-15000)]):
 b=bytearray(struct.pack('<25I',*base['initial_state']['raw_words']))
 for off,value in [(0,x<<16),(4,y<<16),(8,x<<16),(12,y<<16),(20,vx),(24,vy),(0x60,0xaa1),(0x40,0x1100000+0x9ba36),(0x44,0x1100000+0x959f6),(0x54,0x1100000+0xb3b36)]:struct.pack_into('<I',b,off,value&0xffffffff)
 for off,value in [(0x58,2),(0x5a,0),(0x5c,0),(0x1c,0),(0x22,0),(0x28,40),(0x2a,0),(0x38,65535),(0x3a,65535)]:struct.pack_into('<H',b,off,value)
 u.mem_write(0x1000000,bytes(b));u.mem_write(0x43e700,(prep/'engine-globals.bin').read_bytes());u.mem_write(0x43e850,(prep/'flipper-state.bin').read_bytes())
 # Overwrite globals reset above with explicit oracle engine pointers.
 for a,v in [(0x43e764,0x1006000),(0x43e744,0x1006800),(0x43e728,0x42c9fc),(0x43e740,0x1005000),(0x43d860,0x438a3c),(0x43d864,0),(0x43e76c,0x432ecc),(0x4298a4,0),(0x4298c8,0x1000000),(0x43e770,1)]:put(a,v)
 u.mem_write(0x438a3c,struct.pack('<Ihhhh',0,-1,264,181,32))
 trace=outdir/f'case-{index}.json';trace.write_text(json.dumps({'initial_state':{'raw_words':list(struct.unpack('<25I',b))}}))
 force_calls[0]=0
 rows=[list(b)];stop='100ticklimit'
 for tick in range(100):
  xx,yy=struct.unpack_from('<ii',bytes(rows[-1]))
  if not (8<=xx>>16<312 and 8<=yy>>16<616):stop='tableboundary';break
  run(0x4088f0,0);rows.append(list(u.mem_read(0x1000000,100)))
 cases.append({'trace':str(trace),'poses':poses,'globals':globals_,'steps':len(rows)-1,'point_force_type':-1,'point_force_suppressed':False});expected.append(rows)
 summary.append({'case':index,'initial_xy':[x,y],'initial_velocity':[vx,vy],'ticks':len(rows)-1,'point_force_calls':force_calls[0],'stop':stop,'final_xy':[struct.unpack_from('<i',bytes(rows[-1]),o)[0]/65536 for o in [0,4]]})
casefile=outdir/'cases.json';casefile.write_text(json.dumps(cases))
probe=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/native/mean_right_path_probe'
if len(sys.argv)==1:subprocess.run(['c++','-std=c++17','-g','-DSLAM_MEAN_FLIPPER_LIFT=1','-DSLAM_MEAN_MINIGAME_LIFT=1','-DSLAM_MEAN_BALL_PAIR_LIFT=1','-I'+str(ROOT/'src'),str(ROOT/'tests/mean_right_path_probe.cpp'),'-o',str(probe),*[str(ROOT/'build/native'/n) for n in ['libslamassets.a','libmean_flipper_lift.a','libmean_minigame_lift.a','libmean_ball_pair_lift.a']]],check=True)
native=json.loads(subprocess.check_output([str(probe),str(next((ROOT/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))),str(prep),str(ROOT/'analysis/traces/mean-flight-100.json'),str(casefile)],text=True))
diffs=[]
for ci,(a,b) in enumerate(zip(expected,native)):
 for tick,(aa,bb) in enumerate(zip(a,b)):
  if aa!=bb:diffs.append({'case':ci,'tick':tick,'offsets':[i for i in range(100) if aa[i]!=bb[i]],'original_xy':[struct.unpack_from('<i',bytes(aa),o)[0]/65536 for o in [0,4]],'native_xy':[struct.unpack_from('<i',bytes(bb),o)[0]/65536 for o in [0,4]]});break
 if len(a)!=len(b):diffs.append({'case':ci,'original_states':len(a),'native_states':len(b)})
report={'build_sha256':base['build_sha256'],'prepared_image_sha256':hashlib.sha256((prep/'pe-data.bin').read_bytes()).hexdigest(),'addresses':{'step':'0x4088f0','point_force':'0x40a0e8','node':'0x438a3c','lookup':'0x432ecc','suppressed_switch_dispatch':'0x408b04'},'scope':'Original4088f0 physical path, original cachedrestflippers; syntheticmarker0starts, activeoriginalnode-1 at26418132,408b04table-switch/rules dispatch suppressed in original/native.100ticksorboundary.','cases':summary,'states':expected,'differences':diffs}
(ROOT/'analysis/traces/mean-point-force-flight-original.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(json.dumps({'cases':summary,'compared_states':sum(map(len,expected)),'differences':diffs}))

assert not diffs, "Original/native physical trajectory mismatch"
assert all(c["ticks"] == 100 and c["point_force_calls"] == 100 for c in summary), "100tickfixture incomplete"
