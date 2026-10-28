#!/usr/bin/env python3
"""Read-only, SHA-bound Demon RC gate. Bounded coverage never means all variants."""
import argparse,copy,hashlib,json,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RETAIL_SHA='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
def read(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def require(condition,message):
 if not condition:raise AssertionError(message)
def verify(index_path):
 index=read(index_path);archive=index['archive'];digest=sha(archive)
 require(digest==index['archive_sha256'],'RC archive SHA mismatch')
 evidence={}
 for ref in index['evidence']:
  path=ref['path'];require(path not in evidence,'Duplicate evidence: '+path)
  require(sha(path)==ref['sha256'],'Evidence SHA mismatch: '+path);evidence[path]=read(path)
 def report(name,status='VERIFIED'):
  path='analysis/traces/'+name+'.json';require(path in evidence,'Missing pinned report: '+path)
  value=evidence[path];require(value['status']==status,'Unverified report: '+path)
  require(value['archive_sha256']==digest,'Different tested archive: '+path);return value
 package=report('demon-rc-package');compat=report('demon-rc-compat')
 host=report('demon-rc-host','VERIFIED_BOUNDED_HOST');fixtures=report('demon-rc-fixtures')
 for key in ['archive_relocated','checkout_hidden','program_and_originals_readonly','network_disabled','native_import_empty_PATH','saved_selection','separate_preferences','original_game_vectors_exact','highscore_save_reload_no_rewrite','options_reload','menu_focus_audio_pause']:
  require(package[key] is True,'Package condition: '+key)
 require(not package['original_assets_included']and package['checkout_accesses']==0 and package['python_wine_checksum_execs']==0,'Package isolation')
 for key in ['native_import_empty_PATH','five_files_exact','checkout_not_mounted','network_disabled','program_originals_readonly']:
  require(compat[key]is True,'Compatibility condition: '+key)
 version=lambda text:tuple(map(int,text.split('.')))
 for abi,limit in [('GLIBC','2.34'),('GLIBCXX','3.4.29'),('CXXABI','1.3.9')]:require(version(compat['abi_maxima'][abi])<=version(limit),'ABI ceiling: '+abi)
 require('Debian' in compat['older_runtime'],'No actual Debian runtime evidence')
 require(host['fullscreen']and host['renderer']=='gpu'and host['tick_count']==10512 and host['clamped_frames']==0,'Realtime GPU condition')
 require(52560<=host['real_wall_ms']<55560,'Realtime wall duration')
 for key in ['twelve_vectors_exact','canonical_audio_events_exact','saved_score_fresh_reload_no_rewrite']:require(host[key]is True,'Host condition: '+key)
 require(host['audio_requests']==31,'Host audio delivery count')
 completion=read('analysis/demon-completion-contract.json')
 require(completion['manual_rules_complete']and len(completion['rules'])==20 and completion['counts']=={'VERIFIED':20},'Manual contract coverage')
 require(sha(completion['manual']['path'])==completion['manual']['sha256'],'Manual SHA')
 accepted={}
 for path in completion['native_acceptance_indices']:
  a=read(path);require(a['status']=='VERIFIED','Unverified native index: '+path)
  for row in a['cases']:accepted[row['case']]=row['fixture_sha256']
 expected=completion['fixtures'];require(len(expected)==36,'Expected 36 bounded fixtures')
 for case,f in expected.items():
  require(sha(f['path'])==f['sha256']==accepted[case],'Fixture SHA: '+case)
  fdata=read(f['path']);require(fdata['original_reset_exact']and fdata['table']=='demon'and fdata['build_sha256']==RETAIL_SHA,'Fixture origin: '+case)
 for rule in completion['rules']:require(rule['status']=='VERIFIED'and rule['fixtures']and all(f in expected for f in rule['fixtures']),'Unverified manual rule: '+rule['id'])
 rows=fixtures['cases'];require(len(rows)==36 and len({r['case']for r in rows})==36 and {r['case']for r in rows}==set(expected),'Incomplete packaged fixture set')
 for row in rows:
  f=expected[row['case']];source=read(f['path'])
  require(row['fixture_sha256']==f['sha256']and row['steps']==source['tick_count'],'Packaged fixture identity: '+row['case'])
  require(row['vectors_exact']is True and row['audio_exact']is True,'Packaged fixture mismatch: '+row['case'])
 legal=read(completion['legal_game']['evidence']);require(legal['production_save_reload']and legal['diagnostic_contacts']==0,'Legal production storage')
 # Check the actual archived bytes, not merely the extracted test directory.
 with tarfile.open(ROOT/archive)as tar:
  members=tar.getmembers();names={m.name:m for m in members};manifests=[m for m in members if m.name.endswith('/bundle.json')]
  require(len(manifests)==1,'Missing/ambiguous bundle manifest')
  manifest_member=manifests[0];prefix=manifest_member.name[:-len('bundle.json')];manifest=json.load(tar.extractfile(manifest_member))
  require(manifest['table']=='Night of the Demon'and not manifest['original_assets_included'],'Bundle table/assets')
  for name,h in manifest['files'].items():
   require(not name.startswith('/')and '..'not in Path(name).parts,'Unsafe bundle path')
   member=names[prefix+name];require(member.isfile(),'Non-file bundle member: '+name)
   require(hashlib.sha256(tar.extractfile(member).read()).hexdigest()==h,'Archive member SHA: '+name)
  require(not any(Path(m.name).suffix.lower()in {'.dat','.exe','.bin'}for m in members if m.isfile()),'Original asset in archive')
 metadata=evidence.get('analysis/traces/demon-rc-metadata.json')
 require(metadata is not None,'Missing RC metadata proof')
 if metadata:
  require(metadata['status']=='VERIFIED'and metadata['archive_sha256']==digest,'Metadata identity')
  require(metadata['table']=='demon'and metadata['gameplay']=='Playable'and metadata['build_sha256']==RETAIL_SHA,'Metadata readiness mismatch')
  require(metadata['runtime_sha256']==manifest['files']['bin/slamslice'],'Metadata runtime mismatch')
 return dict(status='VERIFIED',archive=archive,archive_sha256=digest,pinned_evidence=len(evidence),bounded_manual_rules=20,packaged_fixtures=36,packaged_steps=sum(r['steps']for r in rows),metadata_verified=metadata is not None,scope='Bounded supported Retail RC; no all-seed/physical-input/listening/whole-raster/universal-driver claim')
def main():
 p=argparse.ArgumentParser();p.add_argument('--index',default='analysis/demon-rc-island.json');p.add_argument('--output',type=Path);p.add_argument('--negative-tests',action='store_true');a=p.parse_args();result=verify(a.index)
 if a.negative_tests:
  index=read(a.index);rejected=[]
  with tempfile.TemporaryDirectory()as tmp:
   candidate=Path(tmp)/'bad-index.json'
   for case in ['archive_hash','missing_report','evidence_hash']:
    bad=copy.deepcopy(index)
    if case=='archive_hash':bad['archive_sha256']='0'*64
    elif case=='missing_report':bad['evidence']=[r for r in bad['evidence']if not r['path'].endswith('demon-rc-fixtures.json')]
    else:bad['evidence'][0]['sha256']='0'*64
    candidate.write_text(json.dumps(bad))
    try:verify(candidate)
    except AssertionError:rejected.append(case)
    else:raise AssertionError('Accepted invalid release index: '+case)
  result['rejected_invalid_indices']=rejected
 if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
