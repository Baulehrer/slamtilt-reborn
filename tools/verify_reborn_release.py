#!/usr/bin/env python3
"""SHA-bound release acceptance for the shared Reborn RC; scopes remain explicit."""
import argparse,copy,hashlib,json,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORTS={
 'distribution':'analysis/traces/reborn-distribution.json',
 'isolation':'analysis/traces/reborn-package-isolation.json',
 'focus':'analysis/traces/reborn-focus.json',
 'endurance':'analysis/traces/reborn-endurance.json',
 'accelerated':'analysis/traces/reborn-gameplay-acceptance.json',
 'visuals':'analysis/traces/reborn-visuals.json',
 'menu':'analysis/traces/reborn-menu-acceptance.json',
 'camera':'analysis/traces/reborn-mean-camera-original.json',
 'components':'analysis/traces/reborn-mean-components.json',
 'review':'analysis/traces/reborn-review-acceptance.json'}
def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def verify(index):
 x=read(index);archive=x['archive'];digest=sha(archive);assert digest==x['archive_sha256']
 refs={r['path']:r['sha256']for r in x['evidence']};assert len(refs)==len(x['evidence'])
 for path,value in refs.items():assert sha(path)==value,path
 for path in REPORTS.values():assert path in refs,path
 r={k:read(p)for k,p in REPORTS.items()}
 for key in ['distribution','isolation','focus','endurance']:assert r[key]['archive_sha256']==digest,key
 d=r['distribution'];assert d['status']=='VERIFIED'and 'Debian' in d['actual_runtime']and d['checkout_not_mounted']and d['all_imported_files_exact']
 assert d['total_steps']==240000 and len(d['accelerated_sessions'])==4
 assert r['isolation']['status']=='VERIFIED'and r['isolation']['checkout_hidden']and not r['isolation']['original_assets_included']
 f=r['focus'];assert f['status']=='VERIFIED_REAL_COMPOSITOR'and {c['table']for c in f['cases']}=={'mean','pirate','space','demon'}
 for c in f['cases']:
  for key in ['actual_alt_tab','manual_pause_preserved','simulation_suspended','audio_suspend_resume','F10_return']:assert c[key],(c['table'],key)
 e=r['endurance'];assert e['status']=='VERIFIED_BOUNDED_REALTIME'and e['total_logical_session_steps']==240000 and len(e['cases'])==4
 with tarfile.open(ROOT/archive)as tar:
  m=next(m for m in tar.getmembers()if m.name.endswith('/frontend-bundle.json'));prefix=m.name[:-len('frontend-bundle.json')];manifest=json.load(tar.extractfile(m));assert manifest['project']=='Slamtilt - Reborn'and not manifest['original_assets_included']
  for path,h in manifest['files'].items():
   assert not path.startswith('/')and '..'not in Path(path).parts
   member=tar.getmember(prefix+path);assert member.isfile()and hashlib.sha256(tar.extractfile(member).read()).hexdigest()==h,path
  assert not any(Path(m.name).suffix.lower()in['.exe','.dat','.bin']for m in tar.getmembers()if m.isfile())
 for case in e['cases']:
  assert case['path']in refs and sha(case['path'])==case['sha256'];t=read(case['path']);assert t['archive_sha256']==digest and t['tick_count']==60000 and t['clamped_frames']==0 and t['fullscreen']and t['renderer']=='gpu'
  binary='bin/slamview'if case['table']in['mean','pirate']else'bin/slamslice';assert t['runtime_sha256']==manifest['files'][binary]
  if case['table']in x['controlled_background_replay_tables']:assert t['focus_policy']=='CONTROLLED_TEST_EVENTS'
  if case['table']in x['qa_sdl_probe_tables']:assert len(t['sdl_stall_probe_sha256'])==64
  if case['table']=='mean':assert not t['whole_original_trajectory_equivalence']and t['active_simulation_steps']+t['game_over_wait_ticks']==60000
  else:assert t['status']=='VERIFIED'and not t['differences']
 assert r['components']['status']=='VERIFIED'and r['components']['cases']==22 and not r['components']['differences']and not r['components']['whole_trajectory_equivalence']
 assert len(r['accelerated']['reports'])==12
 for case in r['accelerated']['reports']:assert sha(case['path'])==case['sha256']
 assert r['accelerated']['status']=='VERIFIED_ACCELERATED_BOUNDED'and r['visuals']['status']=='VERIFIED_RENDERED_LAYOUTS'and r['menu']['status']=='VERIFIED'
 assert len(r['visuals']['cases'])==12 and r['menu']['partial_import_rolls_back']and r['menu']['classic_modern_theme_persistence']
 assert r['review']['status']=='VERIFIED_TARGETED_REVIEW'and r['review']['sanitizers_pass']
 assert sha(r['camera']['source_fixture'])==r['camera']['source_sha256']
 return dict(status='VERIFIED_BOUNDED_RC',project='Slamtilt - Reborn',archive=archive,archive_sha256=digest,review_complete=True,real_alt_tab_four_tables=True,older_runtime_verified=True,real_session_minutes=20,logical_session_steps=240000,controlled_background_replay_tables=x['controlled_background_replay_tables'],qa_sdl_probe_tables=x['qa_sdl_probe_tables'],mean_whole_original_trajectory_equivalence=False,scope='Supported build/profile/currenthostGPU plus actual Debian12. Demon timing uses explicitly controlled background focus and QA-only SDL call instrumentation; earlier timing failures retained, cause unknown. Mean Original components only; subjective feel/hearing, all seeds and universal drivers unclaimed.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--index',default='analysis/reborn-release-island.json');p.add_argument('--output',type=Path);p.add_argument('--negative-tests',action='store_true');a=p.parse_args();result=verify(a.index)
 if a.negative_tests:
  original=read(a.index);cases=[]
  broken=copy.deepcopy(original);broken['archive_sha256']='0'*64;cases.append(('archive identity',broken))
  broken=copy.deepcopy(original);broken['evidence'][0]['sha256']='0'*64;cases.append(('evidence identity',broken))
  broken=copy.deepcopy(original);broken['evidence']=[r for r in broken['evidence']if r['path']!=REPORTS['focus']];cases.append(('required focus proof',broken))
  with tempfile.TemporaryDirectory()as tmp:
   for name,index in cases:
    candidate=Path(tmp)/'index.json';candidate.write_text(json.dumps(index))
    try:verify(candidate)
    except AssertionError:continue
    raise AssertionError('Tampered release accepted: '+name)
  result['negative_cases_rejected']=[name for name,_ in cases]
 if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
