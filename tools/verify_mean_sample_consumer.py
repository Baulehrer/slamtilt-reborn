#!/usr/bin/env python3
"""Original service5c queue, two-slot allocation and sample resolution fixture."""
from pathlib import Path
import hashlib,json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_EBX
root=Path(__file__).resolve().parents[1];image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x10000)
def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def run(start,eax=0,edx=0,ebx=0):
 put(0x100f000,0x100fff0);u.reg_write(UC_X86_REG_ESP,0x100f000)
 for r,v in [(UC_X86_REG_EAX,eax),(UC_X86_REG_EDX,edx),(UC_X86_REG_EBX,ebx)]:u.reg_write(r,v&0xffffffff)
 u.emu_start(start,0x100fff0,count=500)
put(0x43e828,0x43d2a4);put(0x437d04,0x1005000);put(0x43d3a0,10)
requests=[]
for a,b in [(9,8),(4,3),(99,99)]:
 run(0x405c60,0x437cf0,a,b)
 requests.append([get(0x437cf0+0x1c),get(0x437cf0+0x20)])
assert requests==[[9,8]]*3
run(0x401760)
voice=[get(0x43d2d8+4*32+i*4) for i in range(8)]
assert voice==[1,0x1005000,0x1941,0,0,0xa0,64,8],voice
assert get(0x43d2d4)==0
allocator=[]
for p0,p1,a,b in [(0,0,9,8),(8,0,4,3),(8,3,4,3),(8,3,2,1),(8,3,9,8),(8,3,-1,6),(8,3,-2,7)]:
 put(0x43d374,p0);put(0x43d394,p1);run(0x4016dc,a,b)
 slot=u.reg_read(UC_X86_REG_EAX);expected=4 if a==-1 or (a!=-2 and (p0==0 or (p1!=0 and a>=p0))) else 5 if a==-2 or p1==0 or a>=p1 else 0
 assert slot==expected,(a,b,slot,expected)
 allocator.append(dict(before=[p0,p1],arguments=[a,b],slot=slot,after=[get(0x43d374),get(0x43d394)]))
# Original second direct descriptor437d14 +period226/length4078.
put(0x437d28,0x1006000);put(0x43d374,0);put(0x43d394,0)
run(0x405c60,0x437d14,6,5);run(0x401760)
second=[get(0x43d2d8+4*32+i*4) for i in range(8)]
assert second==[1,0x1006000,0xfee,0,0,0xe2,64,5],second
put(0x437db8,0x1007000);put(0x43d374,0);put(0x43d394,0)
run(0x405c60,0x437da4,3,3);run(0x401760)
third=[get(0x43d2d8+4*32+i*4) for i in range(8)]
assert third==[1,0x1007000,0xbd2,0,0,0xe2,64,3],third
flippers=[]
for descriptor,length,pointer in [(0x437d38,0x118a,0x1008000),(0x437d5c,0xfac,0x1009000)]:
 put(descriptor+0x14,pointer);put(0x43d374,0);put(0x43d394,0)
 run(0x405c60,descriptor,2,1);run(0x401760)
 state=[get(0x43d2d8+4*32+i*4) for i in range(8)]
 assert state==[1,pointer,length,0,0,226,64,1],state
 flippers.append(dict(descriptor=hex(descriptor),arguments=[2,1],voice=state))
put(0x437e00,0x100a000);put(0x43d374,0);put(0x43d394,0)
run(0x405c60,0x437dec,6,5);run(0x401760)
release=[get(0x43d2d8+4*32+i*4) for i in range(8)]
assert release==[1,0x100a000,0x16b0,0,0,226,64,5],release
# Bank-relative minigame samples: actual401760 resolves DAT sample18 slices.
dat_path=next((root/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
dat=dat_path.read_bytes();u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,dat)
put(0x43941c,0x1100000);minigame=[]
for descriptor,offset,length in [(0x437fe4,0x27b66,2747),(0x438008,0x286ea,2882),(0x43802c,0x292f5,3395),(0x438050,0x2a100,4536)]:
 put(0x43d374,0);put(0x43d394,0)
 run(0x405c60,descriptor,255,245);run(0x401760)
 state=[get(0x43d2d8+4*32+i*4) for i in range(8)]
 assert state==[1,0x1100000+offset,length,0,0,428,64,245],state
 minigame.append(dict(descriptor=hex(descriptor),dat_offset=hex(offset),arguments=[255,245],voice=state,pcm_sha256=hashlib.sha256(dat[offset:offset+length]).hexdigest()))
report=dict(minigame_samples=minigame,dat_sha256=hashlib.sha256(dat).hexdigest(),mode4_release=release,flippers=flippers,third_consumer_voice=third,second_consumer_voice=second,image_sha256=hashlib.sha256(image).hexdigest(),descriptor='0x437cf0',dat_offset='0x63a1d',length=6465,period=160,volume=64,frequency=0x361f0f//160,queue_duplicate_first_arguments=requests,consumer_voice=voice,allocator=allocator)
(root/'analysis/traces/mean-sample-consumer-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('Original sample queue/consumer and7 allocator cases PASS')
