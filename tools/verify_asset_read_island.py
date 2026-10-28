#!/usr/bin/env python3
"""Reproduce the bounded asset-read gate without instrumenting release binaries."""
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,default=ROOT/'build/native');p.add_argument('--ticks',type=int,default=60000);p.add_argument('--report',type=Path,default=ROOT/'analysis/traces/asset-read-coverage.json');a=p.parse_args();a.build=a.build.resolve();assert 0<a.ticks<=60000
 before={n:sha(a.build/n)for n in ['slamtilt','slamview','slamslice','slamimport']}
 subprocess.run(['cmake','--build',a.build,'--target','asset_read_audit','-j2'],check=True,capture_output=True)
 assert before=={n:sha(a.build/n)for n in before}
 with tempfile.TemporaryDirectory(dir=ROOT/'build',prefix='asset-gate-')as tmp:
  tmp=Path(tmp);data=tmp/'data';reads=tmp/'reads';reads.mkdir();subprocess.run([a.build/'slamimport','--adf',ROOT/'amiga/historical-mods/DLM',data],check=True,capture_output=True)
  references={};jobs=[]
  for table in ['pirate','space','demon']:
   fixture=ROOT/f'build/reborn-playtest/{table}/primary-oracle.json';references[table]=sha(fixture)
   pc=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT'/(table.upper()+'.DAT')
   jobs.append((table,subprocess.Popen([a.build/'asset_read_audit',table,data/table/(table+'-prepared'),data/table/(table.upper()+'.DAT'),pc,fixture,str(a.ticks),reads/(table+'.json')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)))
  for table,job in jobs:
   out,err=job.communicate(timeout=180);assert job.returncode==0,(table,err);print(out.strip(),flush=True)
  subprocess.run([a.build/'slamnative-data',ROOT/'build/asset-read-audit/native.bin'],check=True,capture_output=True)
  subprocess.run(['python3',ROOT/'tools/classify_asset_read_audit.py','--data',data,'--reads',reads,'--report',a.report],check=True)
  report=json.loads(a.report.read_text());report.update(production_binaries_unchanged_by_audit_build=before,reference_sha256=references,instrumentation=json.loads((a.build/'asset-audit/instrumentation.json').read_text()))
  report['reader_evidence']={t:json.loads((reads/(t+'.json')).read_text())for t,_ in jobs}
  source=(ROOT/'build/decoded/full/Demon.Bin').read_bytes();old=(ROOT/'build/amiga-normalized-v2-final/DEMON.DAT').read_bytes();new=(data/'demon/DEMON.DAT').read_bytes();repairs=[]
  for source_offset,target,caller in [(0x65296,0x134b30,0x410dae),(0x9bcba,0x1402f0,0x413927)]:
   expected=source[source_offset:source_offset+480];assert new[target:target+480]==expected
   repairs.append({'source_offset':source_offset,'target':target,'bytes':480,'caller_return':caller,'fixed_bytes':sum(x!=y for x,y in zip(old[target:target+480],expected)),'sha256':hashlib.sha256(expected).hexdigest()})
  report['demon_whole_frame_repairs']=repairs;a.report.write_text(json.dumps(report,indent=2)+'\n')
 assert before=={n:sha(a.build/n)for n in before}
if __name__=='__main__':main()
