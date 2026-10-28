#!/usr/bin/env python3
"""Bounded ADF-only import and four-table runtime regression (no Amiga parity claim)."""
import argparse,json,os,subprocess,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,default=ROOT/'build/native');p.add_argument('--ticks',type=int,default=100);p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/amiga-import-integration.json');a=p.parse_args();a.build=a.build.resolve()
 assert a.ticks>0 and a.ticks%4==0
 env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SLAM_ASSET_SOURCE='amiga')
 results=[]
 with tempfile.TemporaryDirectory(prefix='amiga-import-',dir=ROOT/'build') as temp:
  work=Path(temp);env['XDG_DATA_HOME']=str(work/'preferences');env['XDG_CONFIG_HOME']=str(work/'config')
  def run(args,ok=True):
   r=subprocess.run([str(x) for x in args],env=env,capture_output=True,text=True,timeout=180)
   assert (r.returncode==0)==ok,(args,r.returncode,r.stderr[-2000:],r.stdout[-1000:])
  out=work/'data';adfs=ROOT/'amiga/historical-mods/DLM'
  run([a.build/'slamimport','--adf',adfs,out])
  assert json.loads((out/'amiga-import.json').read_text())['windows_files_required'] is False
  before={str(q.relative_to(out)):hashlib.sha256(q.read_bytes()).hexdigest() for q in out.rglob('*') if q.is_file()}
  run([a.build/'slamimport','--adf',adfs,out],False)
  assert before=={str(q.relative_to(out)):hashlib.sha256(q.read_bytes()).hexdigest() for q in out.rglob('*') if q.is_file()}
  partial=work/'partial';partial.mkdir();disk=next(adfs.glob('*.adf'));(partial/disk.name).symlink_to(disk.resolve())
  run([a.build/'slamimport','--adf',partial,work/'reject'],False);assert not (work/'reject').exists()
  for table in ['mean','pirate','space','demon']:
   data=out/table;prepared=data/(table+'-prepared');trace=work/(table+'.json')
   source=json.loads((ROOT/f'build/reborn-playtest/{table}/primary-{"input" if table=="mean" else "oracle"}.json').read_text())
   replay=work/'replay.json';replay.write_text(json.dumps({'inputs':source['inputs']}))
   if table=='mean':
    command=[a.build/'slamview',data/'MEAN.DAT','--play',prepared,'--trace',ROOT/'packaging/mean-initial.json','--retail-minigame','--trace-output',trace,'--realtime-steps',str(a.ticks),'--frames',str(a.ticks//4+1)]
   elif table=='pirate':
    command=[a.build/'slamview',data/'PIRATE.DAT','--pirate-play',prepared,'--trace-output',trace,'--frames',str(a.ticks//4)]
   else:
    command=[a.build/'slamslice',table,prepared,data/(table.upper()+'.DAT'),'--trace',trace,'--frames',str(a.ticks//4),'--presentation']
   run(command+['--replay',replay,'--replay-only'])
   result=json.loads(trace.read_text());assert result['tick_count']==a.ticks,(table,result.get('tick_count'))
   results.append({'table':table,'tick_count':a.ticks,'status':'PASS'})
  for table,tool in [('mean','slamsetup'),('pirate','slampirate-setup'),('space','slamspace-setup'),('demon','slamdemon-setup')]:
   profile=ROOT/('packaging/mean-data.sha256' if table=='mean' else f'analysis/import/{table}-retail-startup.json')
   command=[a.build/tool,'--importer',a.build/'slamimport','--profile',profile]
   run(command+['--select',adfs]);run(command+['--saved'])
  results.append({'standalone':'all four ADF choosers and remembered selection','status':'PASS'})
  config=work/'menu.json';menu=[a.build/'slamtilt','--config',config]
  run(menu+['--import',adfs,'--frames','1'])
  settings=json.loads(config.read_text())
  assert all(row['source']=='amiga' for row in settings['tables'].values())
  run(menu+['--exercise-all','--child-frames','16','--trace',work/'cycle.json'])
  events=json.loads((work/'cycle.json').read_text())['events']
  assert len(events)==8 and all(e.get('exit_code',0)==0 for e in events),events
  results.append({'menu':'import, persist, reload, four child sessions','status':'PASS'})
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps({'status':'PASS','source':'DLM five-ADF set','scope':'Shared-native engine smoke; not original Amiga gameplay parity','cases':results},indent=2)+'\n');print(f'ADF import + four-table {a.ticks}-step smoke + menu reload PASS')
if __name__=='__main__':main()
