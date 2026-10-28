#!/usr/bin/env python3
"""Compact accelerated-gameplay evidence; preserve the explicit Mean Original boundary."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 reports=[]
 for table in ['mean','pirate','space','demon']:
  for case in ['primary','variant-1','variant-2']:
   name=f'analysis/traces/reborn-{table}-{case}.json';x=read(name);assert x['status']==('VERIFIED_NATIVE_REGRESSION'if table=='mean'else'VERIFIED')and x['diagnostic_contacts']==0
   assert x['tick_count']==(60000 if case=='primary' else 4000)
   reports.append(dict(table=table,case=case,path=name,sha256=sha(name),steps=x['tick_count'],original_scope='COMPONENT_ONLY'if table=='mean'else'EXACT_RECORDED_TRAJECTORY'))
 components=read('analysis/traces/reborn-mean-components.json');assert components['status']=='VERIFIED'and components['cases']==22 and not components['differences']
 index=dict(status='VERIFIED_ACCELERATED_BOUNDED',reports=reports,total_native_steps=sum(r['steps']for r in reports),original_retail_trajectory_steps=sum(r['steps']for r in reports if r['table']!='mean'),mean_original_components=dict(path='analysis/traces/reborn-mean-components.json',sha256=sha('analysis/traces/reborn-mean-components.json'),cases=22,skipped=14),whole_original_mean_trajectory='PARTIAL_NOT_CLAIMED',realtime_acceptance='SEPARATE_REPORTS_REQUIRED',input_configuration_gap=dict(path='analysis/traces/reborn-pirate-input-binding-gap.json',sha256=sha('analysis/traces/reborn-pirate-input-binding-gap.json')),callback_gap=dict(path='analysis/traces/reborn-demon-dmd-gap.json',sha256=sha('analysis/traces/reborn-demon-dmd-gap.json')),scope='Legal keyboard actions only, no diagnostic contacts; exact Retail trajectories and Mean deterministic native sessions plus bounded actual Original integration. Real keyboard/hearing/raster equivalence not claimed.')
 (ROOT/'analysis/traces/reborn-gameplay-acceptance.json').write_text(json.dumps(index,indent=2)+'\n');print(index['status'],index['total_native_steps'])
if __name__=='__main__':main()
