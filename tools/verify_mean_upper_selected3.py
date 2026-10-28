#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([str(ROOT/'build/venv/bin/python'),'tools/trace_mean_upper_selected3.py'],cwd=ROOT,check=True)
p=ROOT/'build/oracle/mean_upper_selected3_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_upper_selected3_probe.cpp','src/physics/mean_upper_capture.cpp','src/physics/mean_upper_release.cpp','src/assets/table_profile.cpp','-DSLAM_TABLE_PROFILES_PATH="analysis/table-profiles.json"','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(p)],cwd=ROOT,check=True)
a=json.loads(subprocess.check_output([str(p)]));r=json.loads((ROOT/'analysis/traces/mean-upper-selected3-original.json').read_text())
b=[{**{k:s[k] for k in ['timer','gate','field394','field1f2','mode','slot1','score']},'release':s['ball'][88]==2,'start':i==51} for i,s in enumerate(r['states'])]
diff=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
report={'steps':len(b),'native_steps':len(a),'differences':diff,'scope':'Uppercallback-only selected3 timers/slots/score/release/startrequest; separate minigame dispatcher excluded from this bounded test.'}
(ROOT/'analysis/traces/mean-upper-selected3-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert not diff and len(a)==len(b)
