#!/usr/bin/env python3
"""New importer/frontends accept unchanged RC4 private datasets, without reimport."""
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,default=ROOT/'build/native');p.add_argument('--legacy',type=Path,default=ROOT/'build/amiga-v1-legacy-fixture');p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/amiga-v2-legacy.json');a=p.parse_args();build=a.build.resolve();legacy=a.legacy.resolve();assert legacy.is_dir()
 def hashes():return{str(p.relative_to(legacy)):hashlib.sha256(p.read_bytes()).hexdigest()for p in legacy.rglob('*')if p.is_file()}
 before=hashes();cases=[]
 with tempfile.TemporaryDirectory(dir=ROOT/'build',prefix='adf-legacy-')as temp:
  env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',XDG_DATA_HOME=temp,SLAM_ASSET_SOURCE='amiga')
  for table in ['mean','pirate','space','demon']:
   data=legacy/table;prepared=data/(table+'-prepared');trace=Path(temp)/(table+'.json');tool=build/('slamimport'if table=='mean'else'slam'+table+'-import')
   result=subprocess.run([tool,'--check',data],env=env,capture_output=True,text=True);assert result.returncode==0,result.stderr
   if table=='mean':cmd=[build/'slamview',data/'MEAN.DAT','--play',prepared,'--trace',ROOT/'packaging/mean-initial.json','--retail-minigame','--trace-output',trace,'--realtime-steps','100','--frames','26']
   elif table=='pirate':cmd=[build/'slamview',data/'PIRATE.DAT','--pirate-play',prepared,'--trace-output',trace,'--frames','25']
   else:cmd=[build/'slamslice',table,prepared,data/(table.upper()+'.DAT'),'--trace',trace,'--frames','25','--presentation']
   replay=ROOT/f'build/reborn-playtest/{table}/primary-{"input"if table=="mean"else"oracle"}.json';result=subprocess.run([*cmd,'--replay',replay,'--replay-only'],env=env,capture_output=True,text=True,timeout=60);assert result.returncode==0,(table,result.stderr[-1000:]);assert json.loads(trace.read_text())['tick_count']==100
   cases.append({'table':table,'verified_legacy_files':True,'tick_count':100,'status':'PASS'})
 assert before==hashes()
 a.report.write_text(json.dumps({'status':'PASS','scope':'Unmodified RC4 private import remains readable/playable by v2-aware native frontends','files_sha256':before,'cases':cases},indent=2)+'\n');print('Four unchanged RC4 imports verify and run100steps PASS')
if __name__=='__main__':main()
