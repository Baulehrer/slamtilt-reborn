#!/usr/bin/env python3
import itertools,subprocess,json
exec(open('tools/verify_mean_minigame.py').read().split('fixtures=[]')[0])
cases=[list(c) for c in itertools.product(range(4),[0,5,6,7],[0,130,150],[158,180,184],[0,32767])];expected=[]
for c in cases:
 u.mem_write(0x400000,image);u.mem_write(0x1000000,runtime);points[0]=0
 for a,v in zip([0x43f00c,0x43efdc,0x43efe0,0x43efe4,0x43f1fa],c):u.mem_write(a,struct.pack('<H' if a==0x43f1fa else '<I',v))
 put(0x43f010,c[0]);run(0x4192d0)
 expected.append([get(a)&0xffffffff for a in [0x43f00c,0x43f010,0x43efdc,0x1001044,0x1001030]]+[e['word'](0x43f1e6)&65535,e['word'](0x43f1fa)&65535]+[get(a)&0xffffffff for a in [0x438b64,0x438b70,0x438b7c]]+[points[0]])
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_minigame_terminal_probe.cpp','src/physics/mean_minigame_lift.cpp','build/generated/mean_minigame.cpp','-o','build/mean_minigame_terminal_probe'],check=True)
actual=json.loads(subprocess.check_output(['build/mean_minigame_terminal_probe',str(prepared/'image.bin'),str(prepared/'runtime.bin'),str(next((ROOT/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')))],input=json.dumps(cases),text=True))
assert actual==expected
assert any(x[-1]==120000000 for x in expected), "Winning branch not exercised"
(ROOT/'analysis/traces/mean-minigame-terminal-fixture.json').write_text(json.dumps(dict(cases=cases,expected=expected,scope='Original4192d0 progress/120Mcompletion/extra-ballflag/slot1100 includingWORDwrap; presentation bounded'),separators=(',',':'))+'\n')
print(json.dumps(dict(cases=len(cases),winning_cases=sum(x[-1]==120000000 for x in expected),differences=0)))
