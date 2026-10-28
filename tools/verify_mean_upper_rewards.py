#!/usr/bin/env python3
"""Bounded original415330 rewards; actual40f754, DMD service returns handle1."""
import json,struct,subprocess,itertools
from pathlib import Path
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'build/oracle/mean_upper_reward_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_upper_reward_probe.cpp','src/physics/mean_upper_capture.cpp','src/physics/mean_upper_release.cpp','src/assets/table_profile.cpp','-DSLAM_TABLE_PROFILES_PATH="analysis/table-profiles.json"','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(p)],cwd=ROOT,check=True)
cases=list(itertools.product([0,-1,1],[0,-1,1],[0,-1,1,2,-32768]))
native=json.loads(subprocess.check_output([str(p)],input=json.dumps(cases),text=True))
expected=[]
for c in cases:
 env={'__file__':str(ROOT/'tools/trace_mean_upper_capture.py')};exec((ROOT/'tools/trace_mean_upper_capture.py').read_text().split('b=bytearray(100)')[0],env)
 u=env['u'];put=env['put'];get=env['get'];word=env['word'];scores=env['scores']
 b=bytearray(100);struct.pack_into('<HH',b,0x58,3,1);u.mem_write(0x1000000,bytes(b))
 for address,value in zip([0x43f36a,0x43f200,0x43f202,0x43f1fa,0x43f378,0x43f1fc],[0,*c,0,0]):u.mem_write(address,struct.pack('<h',value))
 for i,v in enumerate([7,19,23]):put(0x438b44+i*4,v)
 put(0x200f000,0x200fff0);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,0x1000000);u.emu_start(0x415330,0x200fff0,count=10000)
 expected.append(dict(ok=True,timer=word(0x43f36a),gate=word(0x43f364),field200=word(0x43f200),field202=word(0x43f202),field1fa=word(0x43f1fa),field378=word(0x43f378),field1fc=word(0x43f1fc),slot44=[get(0x438b44+i*4) for i in range(3)],score=sum(scores),player08=get(0x1003008),player10=word(0x1003010),ball=list(u.mem_read(0x1000000,100))))
diff=[i for i,(a,b) in enumerate(zip(native,expected)) if a!=b]
report={'scope':'Original415330 timer0 rewardpriority200/202/1fa; ball-local100bytes and gate/slot/playerfields. DMD completion not synthesized. Lampwrites omitted.','cases':cases,'expected':expected,'differences':diff}
(ROOT/'analysis/traces/mean-upper-rewards-fixture.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print(json.dumps({'cases':len(cases),'differences':diff}))
if diff:print(native[diff[0]],expected[diff[0]])
assert not diff
