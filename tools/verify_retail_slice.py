#!/usr/bin/env python3
"""Original/native/reset/SDL acceptance for Space and Demon vertical slices."""
import argparse,hashlib,json,os,subprocess,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jsha(v):return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--table',choices=['space','demon']);p.add_argument('--refresh',action='store_true');p.add_argument('--viewer',type=Path,default=ROOT/'build/native/slamslice');a=p.parse_args();rows=[]
 game=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';profiles=read(ROOT/'analysis/table-profiles.json')
 for table in ([a.table]if a.table else ['space','demon']):
  for suffix in ['full-tick','full-game']:
   prepared=ROOT/f'build/oracle/{table}-{suffix}';source=prepared/'trace.json';o=read(source);meta=read(prepared/'summary.json');dat=game/f'DAT/{table.upper()}.DAT';n=o['tick_count']
   assert sha(game/'SLAMTILT.EXE')==o['build_sha256']==profiles['build_sha256']
   assert sha(dat)==o['dat_sha256']==profiles['tables'][table]['dat_sha256']
   assert o['deterministic_replay_globals']and o['gameplay_stubs']==[],(table,suffix)
   assert n==(1200 if suffix=='full-tick'else 12000)and len(o['states'])==n+1
   fixture=ROOT/f'analysis/traces/{table}-{suffix}.json'
   f=dict(table=table,build_sha256=o['build_sha256'],dat_sha256=o['dat_sha256'],tick_count=n,context_hashes=meta['context_hashes'],inputs=o['inputs'],mode_changes=o['mode_changes'],states_sha256=jsha(o['states']),globals_sha256=jsha(o['globals']),lifecycle_sha256=jsha(o['lifecycle']),highscore_sha256=jsha(o['highscore_sha256']),lamp_sha256=jsha(o['lamp_sha256']),initial_state=o['states'][0],final_state=o['states'][-1],original_reset_exact=True,scope='Original keyboard events only after isolated post-F1 initialization. No diagnostic ball/state writes; native static C++ and independent reset. Not all-table-rules/full-raster/platform equivalence.')
   if a.refresh:fixture.write_text(json.dumps(f,indent=2)+'\n')
   assert read(fixture)==f,'Pinned fixture differs'
   for name,digest in f['context_hashes'].items():assert sha(prepared/name)==digest,name
   out=prepared/'native-verified.json';capture=prepared/'native-verified.bmp'
   subprocess.run([a.viewer,table,prepared,dat,'--frames',str(n//4),'--replay',source,'--trace',out,'--capture',capture],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy'))
   native=read(out);assert native['tick_count']==n and native['states']==o['states'],(table,suffix,'ball')
   for i,(x,y)in enumerate(zip(o['globals'],native['globals'])):
    for k,v in y.items():assert x[k]==v,(table,suffix,i,k)
    assert x['poses']==native['poses'][i],(table,suffix,i,'poses')
   for key in ['lifecycle','highscore_sha256','lamp_sha256']:assert o[key]==native[key],(table,suffix,key)
   assert capture.read_bytes()[:2]==b'BM'
   changes=o['mode_changes'];assert any(e['after']==2 for e in changes)
   assert any(e['action']=='left'for e in f['inputs'])and any(e['action']=='right'for e in f['inputs'])
   if suffix=='full-game':
    assert sum(e['before']==2 and e['after']==3 for e in changes)>=3
    over=next(e['tick']for e in changes if e['after']==0);restart=next(e['tick']for e in changes if e['before']==0 and e['after']==1);assert restart>over
    assert any(e['action']=='new_game'for e in o['inputs'])
    keys=[e for e in o['inputs']if e['action']=='key']
    if table=='space':
     assert [e['scan']for e in keys]==[0x1e,0x30,0x2e,0x1c]
     assert len(set(o['highscore_sha256']))>1
    else:
     # Actual retained Demon route scores zero and does not qualify for initials.
     assert not keys and len(set(o['highscore_sha256']))==1
     assert all(r[8:14]==[0]*6 for r in o['lifecycle'][:over])
   rows.append(dict(table=table,case=suffix,steps=n,original_native_reset_sdl=True,full100_ballbytes=True,clock_phase_fields=9,flipper_poses=3,dmd_lifecycle_highscore_lamps=True));print(table,suffix,n,'EXACT',flush=True)
  if a.refresh:
   o=read(ROOT/f'build/oracle/{table}-full-game/trace.json');start=200;end=start+100
   fields=lambda s:dict(x=struct.unpack_from('<i',bytes(s),0)[0],y=struct.unpack_from('<i',bytes(s),4)[0],vx=struct.unpack_from('<i',bytes(s),20)[0],vy=struct.unpack_from('<i',bytes(s),24)[0],state_58=int.from_bytes(bytes(s)[88:90],'little'))
   proof=dict(build_sha256=o['build_sha256'],dat_sha256=o['dat_sha256'],source_case=table+'-full-game',start_tick=start,tick_count=100,inputs=[dict(e,tick=e['tick']-start)for e in o['inputs']if start<=e['tick']<end],initial_state=fields(o['states'][start]),final_state=fields(o['states'][end]),all100_ballbytes_sequence_sha256=jsha(o['states'][start:end+1]),clock='200Hz; absolute milliseconds retained from original timeline',verified_by=f'analysis/traces/{table}-full-game.json')
   (ROOT/f'analysis/traces/{table}-ball-100.json').write_text(json.dumps(proof,indent=2)+'\n')
 (ROOT/f'analysis/traces/retail-slice-{a.table or "all"}-acceptance.json').write_text(json.dumps(dict(status='VERIFIED',cases=rows),indent=2)+'\n')
if __name__=='__main__':main()
