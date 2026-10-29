#!/usr/bin/env python3
"""Compare pre-cache and cached release frontends with private replay fixtures."""
import os,subprocess,json,hashlib,argparse
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--performance',action='store_true');p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,default=r/'build/lamp-cache-verification');p.add_argument('--frames',type=int,default=1000);args=p.parse_args();
if args.frames<1:p.error('frames must be positive')
w=args.output;w.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software')
rows=[]
for table in ['space','demon']:
 outputs=[]
 for label,binary in [('before',args.before),('after',args.after)]:
  out=w/f'{table}-{label}.json';bmp=w/f'{table}-{label}.bmp'
  cmd=[str(binary.resolve()),table,str(r/f'build/oracle/{table}-full-game'),str(r/f'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/{table.upper()}.DAT'),'--frames',str(args.frames),'--replay',str(r/f'build/reborn-playtest/{table}/primary-oracle.json'),'--replay-only','--trace',str(out),'--capture',str(bmp)]
  if args.performance and label=='after':cmd+=['--performance-output',str(w/f'{table}-performance.json')]
  profile=binary.resolve().parent.parent/'share/slamtilt/table-profiles.json'
  env['SLAM_TABLE_PROFILES']=str(profile if profile.exists() else r/'analysis/table-profiles.json')
  subprocess.run(cmd,env=env,check=True,stdout=subprocess.DEVNULL)
  outputs.append(json.loads(out.read_text()))
 if args.performance:
  profile=json.loads((w/f'{table}-performance.json').read_text())
  assert profile['ticks']==args.frames*4 and profile['frames']==args.frames
  assert 0<profile['frame_p50_ns']<=profile['frame_p95_ns']<=profile['frame_p99_ns']
  assert profile['simulation_ns']>0 and profile['render_prepare_ns']>0
  if profile.get('thread_cpu_supported'):
   assert 0<profile['simulation_thread_cpu_ns']<=profile['simulation_ns']
 a,b=outputs
 ignored={'real_wall_ms','ui_frames','lamp_texture_uploads'}
 diffs=[k for k in a if k not in ignored and a[k]!=b.get(k)]
 assert not diffs,(table,diffs)
 assert hashlib.sha256((w/f'{table}-before.bmp').read_bytes()).digest()==hashlib.sha256((w/f'{table}-after.bmp').read_bytes()).digest()
 image=(r/f'build/oracle/{table}-full-game/human-image.bin').read_bytes()
 count=int.from_bytes(image[0x6c6a4:0x6c6a8], 'little')
 assert 0<count<=256
 before_uploads=args.frames*count
 assert b['lamp_texture_uploads']<before_uploads
 rows.append({'uploads_before':before_uploads,'table':table,'ticks':b['tick_count'],'compared_keys':[k for k in a if k not in ignored],'bmp_exact':True,'uploads_after':b['lamp_texture_uploads']})
 print(rows[-1],flush=True)
(w/'report.json').write_text(json.dumps(rows,indent=2)+'\n')
