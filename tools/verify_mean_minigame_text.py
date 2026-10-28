#!/usr/bin/env python3
from pathlib import Path
prefix=Path(__file__).with_name('verify_mean_material5_display.py').read_text().split('specs=')[0]
exec(compile(prefix,'verify_mean_material5_display.py','exec'))
cases=[]
for value in [0,1,8000,7600,123456,4294967295]:
 for align,x in [(0,0),(1,12),(2,24)]:
  for mask in range(4):
   cases.append(dict(target=0x40617c,registers=[align,mask,7,value,0x10ff000,0,0,0],x=x))
for value in [0,8000,123456789012,999999999999]:
 digits=f'{value:012d}';bcd=[int(digits[i:i+2],16) for i in range(0,12,2)]
 for align,x in [(0,0),(1,12),(2,24)]:cases.append(dict(target=0x40617c,registers=[align,3,7,4294967295,0x10ff000,0,0,0],x=x,bcd=bcd))
# UINT32max is the original BCD sentinel; use explicit mapped zero record there.
for c in cases:
 if c['registers'][3]==0xffffffff and 'bcd' not in c:c['bcd']=[0]*6
for text in ['READY','S','PRESS SHIFT','BONUS','8000']:
 cases.append(dict(target=0x4060f8,registers=[0,0,4,0x1004000,0x10ff000,0,0,0],text=text))
for value in [0,8000,30500000,4294967294]:cases.append(dict(target=0x406280,registers=[1,12,4,value,0x10ff000,0,0,0]))
for level in [4294967295,0,1,2,3,4,5,6,7,2147483647]:cases.append(dict(target=0x4060a4,registers=[level,0,0,0,0x10ff000,0,0,0]))
expected=[]
for c in cases:
 u.mem_write(0x1000000,bytes(i%4 for i in range(1920)));u.mem_write(0x1004000,c.get('text','').encode()+b'\0');u.mem_write(0x1005000,bytes(c.get('bcd',[0]*6)))
 for reg,value in zip([UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_EBX],c['registers'][:4]):u.reg_write(reg,value)
 put(0x10ff004,c.get('x',0));put(0x10ff008,0x1005000)
 call(c['target']);result=u.reg_read(UC_X86_REG_EAX) if c['target']==0x40617c else c['registers'][0]
 expected.append(dict(fnv=fnv(bytes(u.mem_read(0x1000000,1920))),result=result))
actual=json.loads(subprocess.run([a.native,str(directory/'MAIN.DAT')],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout)
assert len(actual)==len(expected)
for i,(x,y) in enumerate(zip(expected,actual)):assert x==y,(i,cases[i],x,y)
(root/'analysis/traces/mean-minigame-text-original.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),main_dat_sha256=hashlib.sha256(main).hexdigest(),scope='Actual4060f8/40617c/406280 pixels; small numeric return width, binary/6byteBCD, alignment/color andcommadots; screen-contained input positions; primaryscore returnregister not compared',cases=cases,expected=expected),separators=(',',':'))+'\n')
print(len(cases),'original/native text numeric pixels and widths exact')
