#!/usr/bin/env python3
"""Test STIM period rounding against Retail over 2,000 manual tracker ticks.

Uses an isolated private libxmp copy. Different ticks are measured in Q12;
this does not establish scheduler, PCM, event, or whole-song equivalence.
The baseline library supplied to this test remains unchanged.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--native',type=Path,required=True)
p.add_argument('--source',type=Path,default=ROOT/'build/libxmp')
p.add_argument('--baseline',type=Path,required=True)
p.add_argument('--base-patch',type=Path,help='Historical libxmp patch to use as experiment baseline')
p.add_argument('--work',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--targeted',action='store_true',help='Round only STIM pitch slides without vibrato or arpeggio')
p.add_argument('--survey',action='store_true',help='Also compare selected orders in each startup bank')
p.add_argument('--vibrato-hold',action='store_true',help='Test retaining the previous period at a vibrato row start')
p.add_argument('--vibrato-direct',action='store_true',help='Test direct period plus vibrato for STIM')
a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='period-round-',dir=a.work) as tmp:
 root=Path(tmp); source=root/'source';build=root/'build'
 prepare=[sys.executable,str(ROOT/'tools/prepare_stim_libxmp.py'),'--source',str(a.source),'--output',str(source)]
 if a.base_patch:prepare+=['--patch',str(a.base_patch.resolve())]
 subprocess.run(prepare,check=True,stdout=subprocess.DEVNULL)
 player=source/'src/player.c';s=player.read_text();anchor='\t\tfinal_period = xc->period;';assert s.count(anchor)==1
 # Periods are positive in this branch; integer cast implements nearest rounding.
 condition='strcmp(m->mod.type, "Slamtilt") == 0 && final_period > 0'
 if a.vibrato_direct:
  addition='\n\tif ('+condition+' && TEST(VIBRATO) && arp == 0 && xc->finetune == 0)\n\t\tfinal_period = period + vibrato;'
 elif a.vibrato_hold:
  addition='\n\tif ('+condition+' && TEST(VIBRATO) && !TEST(NEW_NOTE) && p->frame == 0 && xc->info_period > 0)\n\t\tfinal_period = xc->info_period / 4096.0;'
 else:
  if a.targeted:
   condition+=' && TEST(PITCHBEND) && xc->freq.slide > 0 && !TEST(VIBRATO) && arp == 0 && xc->finetune == 0'
  addition='\n\tif ('+condition+')\n\t\tfinal_period = (int)(final_period + 0.5);'
 s=s.replace(anchor,anchor+addition)
 player.write_text(s)
 subprocess.run(['cmake','-S',str(source),'-B',str(build),'-DBUILD_SHARED=ON','-DBUILD_STATIC=OFF','-DCMAKE_BUILD_TYPE=Release'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 subprocess.run(['cmake','--build',str(build),'-j','4'],check=True,stdout=subprocess.DEVNULL)
 library=build/'libxmp.so.4';reports=[];diffs=[]
 for label,lib in (('production',a.baseline.absolute()),('rounded',library)):
  out=root/f'{label}.json';diff=root/f'{label}-diffs.json'
  subprocess.run([sys.executable,str(ROOT/'tools/verify_stim_sequence_periods.py'),'--native',str(a.native.resolve()),'--library',str(lib),'--work',str(root/label),'--output',str(out),'--differences',str(diff),'--ticks','2000'],check=True,stdout=subprocess.DEVNULL)
  reports.append(json.loads(out.read_text()));diffs.append(json.loads(diff.read_text()))
 rows=[]
 for before,after in zip(reports[0]['tables'],reports[1]['tables']):
  table=before['table'];assert table==after['table'] and before['compared_channel_ticks']==after['compared_channel_ticks']
  d0={(x['tick'],x['channel']):abs(x['delta_q12']) for x in diffs[0][table]};d1={(x['tick'],x['channel']):abs(x['delta_q12']) for x in diffs[1][table]};keys=set(d0)|set(d1)
  improved=sum(d1.get(k,0)<d0.get(k,0) for k in keys);worse=sum(d1.get(k,0)>d0.get(k,0) for k in keys)
  rows.append({'table':table,'channel_ticks':before['compared_channel_ticks'],'original_exact':before['exact_period_ticks'],'rounded_exact':after['exact_period_ticks'],'improved':improved,'worse':worse,'max_worse_q12':max([0]+[d1.get(k,0)-d0.get(k,0) for k in keys])})
 survey=[]
 if a.survey:
  for table in ('mean','pirate','space','demon'):
   for order in (0,4,16,25,32,34,48,60):
    pair=[]
    for label,lib in (('production',a.baseline.absolute()),('rounded',library)):
     out=root/f'survey-{table}-{order}-{label}.json';diff=root/f'survey-{table}-{order}-{label}-diffs.json'
     subprocess.run([sys.executable,str(ROOT/'tools/verify_stim_sequence_periods.py'),'--native',str(a.native.resolve()),'--library',str(lib),'--work',str(root/f'survey-{label}'),'--output',str(out),'--differences',str(diff),'--ticks','256','--table',table,'--order',str(order)],check=True,stdout=subprocess.DEVNULL)
     pair.append(json.loads(diff.read_text())[table])
    d0={(x['tick'],x['channel']):abs(x['delta_q12']) for x in pair[0]};d1={(x['tick'],x['channel']):abs(x['delta_q12']) for x in pair[1]};keys=set(d0)|set(d1)
    survey.append({'table':table,'order':order,'ticks':256,'improved':sum(d1.get(k,0)<d0.get(k,0) for k in keys),'worse':sum(d1.get(k,0)>d0.get(k,0) for k in keys),'max_worse_q12':max([0]+[d1.get(k,0)-d0.get(k,0) for k in keys])})
 if not a.targeted and not a.vibrato_hold and not a.vibrato_direct:
  assert any(r['worse'] for r in rows) and all(r['rounded_exact']>=r['original_exact'] for r in rows)
 elif a.targeted or a.vibrato_hold or a.vibrato_direct:
  assert all(r['worse']==0 for r in rows+survey), 'targeted rounding regressed observed periods'
 report={'status':'EXPERIMENT_ONLY','scope':__doc__,'targeted':a.targeted,'vibrato_hold':a.vibrato_hold,'vibrato_direct':a.vibrato_direct,'baseline_library_sha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'candidate_library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'tables':rows,'survey':survey,'decision':'not enabled pending broader PCM/effect validation'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: isolated rounding comparison recorded')
