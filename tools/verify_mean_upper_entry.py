#!/usr/bin/env python3
"""Original upper capture branch including real41db1c object gate."""
exec(open(__file__.replace('verify_mean_upper_entry.py','verify_mean_upper_release.py')).read().split('rng=random.Random')[0])
# One listed ball; blocked flag maps exactly to state3/callback1.
put(0x43f068,0x1001000);put(0x1001000,1);put(0x1002014,0x1004000);put(0x1004000,0x1006000)
def exit_branch(uc,a,n,c):uc.reg_write(UC_X86_REG_EIP,0x41db15)
u.hook_add(UC_HOOK_CODE,exit_branch,begin=0x41d9e3,end=0x41d9e3)
u.hook_add(UC_HOOK_CODE,exit_branch,begin=0x41da51,end=0x41da51)
rng=random.Random(0x41d983);cases=[];expected=[]
for i in range(512):
 b=bytearray(rng.randbytes(100));struct.pack_into('<ii',b,0,rng.choice([60*65536,60*65536+1,rng.randrange(-65536,61*65536)]),rng.choice([170*65536,170*65536-1,rng.randrange(-65536,171*65536)]))
 c=dict(ball=list(b),slot=[rng.choice([-1,0,1]),rng.randrange(200),rng.randrange(500)],timer=rng.randrange(-32768,32768),services=rng.choice([0,0,1]),blocked=bool(rng.randrange(2)));cases.append(c)
 u.mem_write(0x1000000,bytes(b));put(0x100201c,c['services']);put(0x1006058,0x10003 if c['blocked'] else 2)
 for j,v in enumerate(c['slot']):put(0x438b5c+j*4,v)
 u.mem_write(0x43f36a,struct.pack('<h',c['timer']));run(0x41d94c)
 accepted=c['services']==0 and struct.unpack_from('<i',b,0)[0]<=60*65536 and struct.unpack_from('<i',b,4)[0]<170*65536 and c['slot'][0]<0 and not c['blocked']
 expected.append(dict(ball=list(u.mem_read(0x1000000,100)),slot=[struct.unpack('<i',u.mem_read(0x438b5c+j*4,4))[0] for j in range(3)],timer=struct.unpack('<h',u.mem_read(0x43f36a,2))[0],accepted=accepted))
probe=ROOT/'build/oracle/mean_upper_entry_probe'
subprocess.run(['c++','-std=c++17','-Isrc','-Ibuild/native/_deps/json-src/include','tests/mean_upper_entry_probe.cpp','src/physics/mean_upper_entry.cpp','src/physics/mean_step.cpp','src/physics/mean_material_bundle.cpp','-o',str(probe)],cwd=ROOT,check=True)
actual=json.loads(subprocess.check_output([str(probe)],input=json.dumps(cases),text=True));diff=[i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b]
report=dict(cases=len(cases),differences=diff,accepted=sum(c['accepted'] for c in expected),scope='Original41d94c upper branch and actual41db1c gate; unrelatedXY branches exit; sound stub; all100ballbytes+slot+timer')
(ROOT/'analysis/traces/mean-upper-entry-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert not diff
