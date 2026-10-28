#!/usr/bin/env python3
"""Compare bounded initial upper capture timers against original execution."""
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
subprocess.run([str(ROOT/'build/venv/bin/python'), 'tools/trace_mean_upper_capture.py'], cwd=ROOT, check=True)
probe = ROOT/'build/oracle/mean_upper_capture_probe'
subprocess.run(['c++', '-std=c++17', '-Isrc', '-Ibuild/native/_deps/json-src/include', 'tests/mean_upper_capture_probe.cpp', 'src/physics/mean_upper_capture.cpp','src/physics/mean_upper_release.cpp','src/assets/table_profile.cpp','-DSLAM_TABLE_PROFILES_PATH="analysis/table-profiles.json"', 'src/physics/mean_step.cpp', 'src/physics/mean_material_bundle.cpp', '-o', str(probe)], cwd=ROOT, check=True)
actual = json.loads(subprocess.check_output([str(probe)], text=True))
raw = json.loads((ROOT/'analysis/traces/mean-upper-original-cycle.json').read_text())
expected = [{**{k:s[k] for k in ['timer','field394','slot1','score','mode','field1f2']}, 'release':s['ball'][88] == 2, 'transfer':s['ball'][90] == 3} for s in raw]
diff = [i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report = {'steps':len(expected), 'native_steps':len(actual), 'differences':diff, 'scope':'Original callback1 initial mode2; timer and slot complete through release request. Release ball/random mutations verified independently. Original service34 returns nonzero handle, actual40f754 executes; slot0 display every4steps; no DMD completion synthesized.'}
(ROOT/'analysis/traces/mean-upper-capture-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
if diff:
 i=diff[0];print(i,actual[i],expected[i])
assert not diff and len(actual)==len(expected)
subprocess.run([str(ROOT/'build/venv/bin/python'), 'tools/trace_mean_upper_second.py'],cwd=ROOT,check=True)
actual=json.loads(subprocess.check_output([str(probe),'second'],text=True))
raw=json.loads((ROOT/'analysis/traces/mean-upper-second-original-cycle.json').read_text())[:452]
expected=[{**{k:s[k] for k in ['timer','field394','slot1','score','mode','field1f2']},'release':False,'transfer':s['ball'][90]==3} for s in raw]
diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report={'steps':len(expected),'native_steps':len(actual),'differences':diff,'scope':'Second initial-mode upper callback1 through original417068 transfer request. Local rule394/1f2/mode and slot exact; full rule/lamp sideeffects and callback3 completion separately bounded.'}
(ROOT/'analysis/traces/mean-upper-second-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
if diff:
 i=diff[0];print(i,actual[i],expected[i])
assert not diff and len(actual)==len(expected)

subprocess.run([str(ROOT/'build/venv/bin/python'), 'tools/trace_mean_upper_third.py'],cwd=ROOT,check=True)
actual=json.loads(subprocess.check_output([str(probe),'third','mode5'],text=True))
raw=json.loads((ROOT/'analysis/traces/mean-upper-third-original-cycle.json').read_text())[:152]
expected=[{**{k:s[k] for k in ['timer','field394','slot1','score','mode','field1f2']},'release':False,'transfer':s['ball'][90]==3} for s in raw]
diff=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
report={'steps':len(expected),'native_steps':len(actual),'differences':diff,'scope':'Third upper capture mode5/field1e6=0 through original417068 request;415dc7 returnswithout secondaryslotdelay. Originalfullcycle252stepsincludingcallback3.'}
(ROOT/'analysis/traces/mean-upper-third-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
if diff:
 i=diff[0];print(i,actual[i],expected[i])
assert not diff and len(actual)==len(expected)
