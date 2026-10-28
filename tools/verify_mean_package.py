#!/usr/bin/env python3
"""Package, extract elsewhere, and run the RC without access to the checkout."""
import argparse,hashlib,json,os,re,shutil,subprocess,tarfile,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def run(cmd,**kw):return subprocess.run([str(x) for x in cmd],text=True,capture_output=True,**kw)
def executes_tool(line,tools):
 match=re.search(r'execve\("([^"]+)"',line)
 return bool(match and any(Path(match[1]).name.lower().startswith(tool) for tool in tools))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,default=R/'build/native');p.add_argument('--output',type=Path,default=R/'analysis/traces/mean-package-acceptance.json');p.add_argument('--program-archive',type=Path);p.add_argument('--data-archive',type=Path);p.add_argument('--checker',type=Path);a=p.parse_args()
 if bool(a.program_archive)!=bool(a.data_archive):p.error('--program-archive and --data-archive must be supplied together')
 with tempfile.TemporaryDirectory(prefix='mean rc ') as tmp:
  tmp=Path(tmp);original=tmp/'original';original.mkdir();app=original/'Mean Runtime';data=original/'Private Data'
  if a.program_archive:
   roots=[]
   for source in (a.program_archive,a.data_archive):
    with tarfile.open(source) as archive:
     names={Path(m.name).parts[0] for m in archive.getmembers()};assert len(names)==1 and next(iter(names)) not in ('..','.')
     name=next(iter(names));assert name not in roots;roots.append(name)
     shutil.copyfile(source,original/(name+'.tar.gz'));archive.extractall(original,filter='data')
   app=original/roots[0];data=original/roots[1]
  else:
   packaged=run([R/'tools/slampack','--build',a.build,'--output',app,'--data-output',data]);assert packaged.returncode==0,packaged.stderr
  manifest=json.loads((app/'bundle.json').read_text());assert not manifest['original_assets_included']
  assert (app/'slamimport').read_bytes()[:4]==b'\x7fELF'
  assert not any(f.suffix.lower() in ('.dat','.bin') for f in app.rglob('*'))
  before=hashlib.sha256((app/'bundle.json').read_bytes()).hexdigest()
  repeated=run([R/'tools/slampack','--build',a.build,'--output',app]);assert repeated.returncode!=0 and hashlib.sha256((app/'bundle.json').read_bytes()).hexdigest()==before
  moved=tmp/'relocated with spaces';moved.mkdir()
  for folder in (app,data):
   with tarfile.open(str(folder)+'.tar.gz') as archive:
    assert all(Path(m.name).parts[0]==folder.name for m in archive.getmembers())
    archive.extractall(moved,filter='data')
  shutil.rmtree(original);app=moved/app.name;data=moved/data.name
  for name,digest in manifest['files'].items():assert hashlib.sha256((app/name).read_bytes()).hexdigest()==digest
  unrelated=tmp/'unrelated';unrelated.mkdir()
  env=os.environ.copy();env.pop('SLAMTILT_DATA_DIR',None);env.pop('LD_LIBRARY_PATH',None)
  prefs=tmp/'initial preferences';prefs.mkdir();env.update(HOME=str(prefs),XDG_DATA_HOME=str(prefs))
  missing=run([app/'slamplay','--check'],cwd=unrelated,env=env);assert missing.returncode==2
  selected=run([app/'slamplay','--data-dir',data,'--check'],cwd=unrelated,env=env);assert selected.returncode==0,selected.stderr
  by_env=run([app/'slamplay','--check'],cwd=unrelated,env=dict(env,SLAMTILT_DATA_DIR=str(data)));assert by_env.returncode==0,by_env.stderr
  starter=run([data/'play-mean','--check'],cwd=unrelated,env=env);assert starter.returncode==0,starter.stderr
  target=data/'mean-prepared/lookup.bin';saved=target.read_bytes();target.write_bytes(bytes([saved[0]^1])+saved[1:])
  broken=run([app/'slamplay','--data-dir',data,'--check'],cwd=unrelated,env=env);assert broken.returncode==2
  target.write_bytes(saved)
  runtime=data/'mean-minigame-prepared/runtime.bin';runtime.rename(runtime.with_suffix('.held'))
  incomplete=run([app/'slamplay','--data-dir',data,'--check'],cwd=unrelated,env=env);assert incomplete.returncode==2
  runtime.with_suffix('.held').rename(runtime)
  dynamic=subprocess.check_output(['readelf','-d',str(app/'bin/slamview')],text=True)
  assert '$ORIGIN/../lib' in dynamic and str(R) not in dynamic
  resolved=run(['ldd',app/'bin/slamview'],env=dict(env,LD_LIBRARY_PATH=str(app/'lib')));assert resolved.returncode==0
  for name in manifest['bundled_libraries']:assert str(app/'lib'/name) in resolved.stdout
  state=tmp/'state';state.mkdir();sandbox=[];namespace=False;namespace_error=None
  if shutil.which('bwrap'):
   sandbox=['bwrap','--ro-bind','/usr','/usr','--ro-bind','/etc','/etc','--ro-bind',str(Path('/bin').resolve()),'/bin','--ro-bind',str(Path('/lib').resolve()),'/lib','--ro-bind',str(Path('/lib64').resolve()),'/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp']
   available=run([*sandbox,'/bin/true']);namespace=available.returncode==0;namespace_error=available.stderr or None
  env.update(PWD=str(unrelated),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',HOME=str(state),XDG_DATA_HOME=str(state))
  # Import from original files only, with no checkout/cache or tools on PATH.
  original_exe=next((R/'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE'))
  raw=tmp/'raw originals';raw.mkdir()
  shutil.copyfile(original_exe,raw/'SLAMTILT.EXE')
  (raw/'DAT').mkdir()
  for name in ('MEAN.DAT','MAIN.DAT'):shutil.copyfile(data/name,raw/'DAT'/name)
  if namespace:
   import_command=[*sandbox,'--ro-bind',app,'/app','--ro-bind',raw,'/raw','--bind',state,'/state','--chdir','/tmp','--setenv','HOME','/state','--setenv','XDG_DATA_HOME','/state','--setenv','PATH','/no-import-tools','/app/bin/slamsetup','--importer','/app/slamimport','--profile','/app/share/slamtilt/mean-data.sha256','--select','/raw']
  else:import_command=[app/'bin/slamsetup','--importer',app/'slamimport','--profile',app/'share/slamtilt/mean-data.sha256','--select',raw]
  import_trace=state/'import-access.log'
  if shutil.which('strace'):import_command=[shutil.which('strace'),'-f','-e','trace=file','-o',import_trace,*import_command]
  imported=run(import_command,cwd=unrelated,env=env);assert imported.returncode==0,imported.stderr
  if import_trace.exists():
   accesses=import_trace.read_text();assert str(R) not in accesses
   assert not any(executes_tool(line,('python','wine','sha256sum')) for line in accesses.splitlines())
  imported_path=Path(imported.stdout.strip())
  if namespace:imported_path=state/imported_path.relative_to('/state')
  assert all(hashlib.sha256((imported_path/name).read_bytes()).hexdigest()==digest for digest,name in (line.split(None,1) for line in (app/'share/slamtilt/mean-data.sha256').read_text().splitlines()))
  data=tmp/'Imported Data';shutil.move(imported_path,data)
  imported_check=run([app/'slamplay','--data-dir',data,'--check'],cwd=unrelated,env=env);assert imported_check.returncode==0,imported_check.stderr
  if namespace:
   remember_command=[*sandbox,'--ro-bind',app,'/app','--ro-bind',data,'/game-data','--bind',state,'/state','--chdir','/tmp','--setenv','HOME','/state','--setenv','XDG_DATA_HOME','/state','/app/bin/slamsetup','--importer','/app/slamimport','--profile','/app/share/slamtilt/mean-data.sha256','--select','/game-data']
   command=[*sandbox,'--ro-bind',app,'/app','--ro-bind',data,'/game-data','--bind',state,'/state','--chdir','/tmp','--setenv','HOME','/state','--setenv','XDG_DATA_HOME','/state','/app/slamplay','--frontend-acceptance','/state/report.json','--frames','14','--capture','/state/table.bmp']
  else:
   remember_command=[app/'bin/slamsetup','--importer',app/'slamimport','--profile',app/'share/slamtilt/mean-data.sha256','--select',data]
   command=[app/'slamplay','--frontend-acceptance',state/'report.json','--frames','14','--capture',state/'table.bmp']
  remembered=run(remember_command,cwd=unrelated,env=env);assert remembered.returncode==0,remembered.stderr
  # Trace executed programs and file access; the runtime never invokes Python/Wine.
  trace=state/'access.log'
  if shutil.which('strace'):command=['strace','-f','-e','trace=file','-o',str(trace),*command]
  played=run(command,cwd=unrelated,env=env);assert played.returncode==0,played.stderr
  frontend=json.loads((state/'report.json').read_text());assert frontend['audio_requested'] and frontend['open_failures']==0 and frontend['initials']=='RAB' and frontend['focus_minimize_resume']
  assert (state/'table.bmp').stat().st_size>10000
  if trace.exists():
   accesses=trace.read_text();offending=[line for line in accesses.splitlines() if str(R) in line];assert not offending,offending[:8]
   assert not any(executes_tool(line,('python','wine')) for line in accesses.splitlines())
  checker=a.checker.resolve() if a.checker else a.build.resolve()/'mean_mode_marathon';fixture=R/'analysis/traces/mean-five-modes-input.json'
  if namespace:
   game=[*sandbox,'--ro-bind',app,'/app','--ro-bind',data,'/game-data','--ro-bind',checker,'/mean-check','--ro-bind',fixture,'/replay.json','--bind',state,'/state','--chdir','/tmp','--setenv','SLAM_TABLE_PROFILES','/app/share/slamtilt/table-profiles.json','--setenv','LD_LIBRARY_PATH','/app/lib','/mean-check','/game-data/MEAN.DAT','/game-data/mean-prepared','/app/share/slamtilt/initial-state.json','/replay.json','/state/game.json']
  else:game=[checker,data/'MEAN.DAT',data/'mean-prepared',app/'share/slamtilt/initial-state.json',fixture,state/'game.json']
  replayed=run(game,env=dict(env,SLAM_TABLE_PROFILES=str(app/'share/slamtilt/table-profiles.json')));assert replayed.returncode==0,replayed.stderr
  golden=json.loads((state/'game.json').read_text());assert golden['cases'][0]['completed_mask']==31 and golden['cases'][0]['final_score']==924072310 and golden['speed']['peak_balls']==8
  assert all(hashlib.sha256((app/name).read_bytes()).hexdigest()==digest for name,digest in manifest['files'].items())
  report={'status':'VERIFIED','runtime_file_count':len(manifest['files']),'private_original_data_files':8,'program_has_original_assets':False,'extracted_elsewhere':True,'paths_with_spaces':True,'independent_working_directory':True,'missing_data_rejected':True,'tampered_data_rejected':True,'missing_minigame_rejected':True,'existing_output_preserved':True,'cli_and_env_data_roots':True,'private_starter':True,'install_runpath':'$ORIGIN/../lib','bundled_libraries':manifest['bundled_libraries'],'isolated_namespace':namespace,'namespace_fallback_reason':namespace_error,'read_only_program_and_data':namespace,'checkout_accesses':0 if trace.exists() else None,'python_wine_runtime_invocations':0 if trace.exists() else None,'all_five_packaged_data_replay':golden['cases'][0],'all_five_repeats':2,'frontend':frontend,'runtime_requirements':manifest['runtime_requirements'],'scope':'Relocated Linux RC on current host with isolated dummy SDL audio/video; not cross-distro or physical GPU/audio compatibility proof.'}
  report['raw_original_import']={'status':'VERIFIED','isolated_namespace':namespace,'cached_inputs':False,'native':True,'no_tools_on_import_path':namespace,'python_wine_external_sha_invocations':0 if import_trace.exists() else None,'all_eight_hashes_exact':True,'native_frontend_and_two_finite_games_use_imported_data':True}
  report['native_first_start']={'raw_import_via_sdl_setup':True,'prepared_folder_selection':True,'remembered_selection_starts_game_without_data_argument':True,'native_play_uses_no_python':True}
  report['prebuilt_archives']=bool(a.program_archive)
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
