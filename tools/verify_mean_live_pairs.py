#!/usr/bin/env python3
"""Actual408bfc on natural pairs, plus Original408874 pair visitation order.

All pair mutations in the legal all-five game are retained. Scheduler physics
and phase1 are adapters: per-row live pool counts are supplied, not proven.
"""
import argparse,collections,hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--probe',type=Path,default=R/'build/native/mean_pair_context_probe');p.add_argument('--output',type=Path,default=R/'analysis/traces/mean-live-pairs-original.json');a=p.parse_args()
 prep=R/'build/mean-prepared';route=R/'analysis/traces/mean-five-modes-input.json';image=(prep/'pe-data.bin').read_bytes();lut=(prep/'lookup.bin').read_bytes();fixture=json.loads(route.read_text());dat=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
 assert hashlib.sha256(image).hexdigest()==fixture['image_sha256'] and hashlib.sha256(dat.read_bytes()).hexdigest()==fixture['dat_sha256']
 path=R/'build/oracle/mean-live-pairs.json';path.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run([str(a.probe),str(dat),str(prep),str(R/'analysis/traces/mean-flight-100.json'),str(route),str(path)],check=True);contexts=json.loads(path.read_text())
 u=Uc(UC_ARCH_X86,UC_MODE_32)
 for addr,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x2000000,0x10000),(0x2100000,0x1000)]:u.mem_map(addr,n)
 u.mem_write(0x400000,image);u.mem_write(0x1006000,lut)
 def put(addr,v):u.mem_write(addr,struct.pack('<I',v&0xffffffff))
 def get(addr):return struct.unpack('<I',u.mem_read(addr,4))[0]
 def ret():
  sp=u.reg_read(UC_X86_REG_ESP);target=get(sp);u.reg_write(UC_X86_REG_ESP,sp+4);u.reg_write(UC_X86_REG_EIP,target)
 phase='schedule';rows={};visits=[]
 def hook(uc,addr,size,data):
  if phase!='schedule':return
  if addr==0x4088f0:
   row=uc.reg_read(UC_X86_REG_EAX)
   if row in rows:put(0x43e770,rows[row])
  elif addr==0x408bfc:visits.append([uc.reg_read(UC_X86_REG_EAX),uc.reg_read(UC_X86_REG_EDX),get(0x43e770)])
  ret()
 for addr in (0x4088f0,0x408bfc,0x2100100):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
 def run(entry,first=0,second=0):
  put(0x200f000,0x2100000);u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,first);u.reg_write(UC_X86_REG_EDX,second);u.emu_start(entry,0x2100000,count=10000)
  assert u.reg_read(UC_X86_REG_EIP)==0x2100000,('Original did not return',hex(entry))
 def schedule(n,changes):
  nonlocal phase,rows,visits
  phase='schedule';rows=changes;visits=[]
  for addr,value in [(0x43e740,0x1005000),(0x1005004,0x1005100),(0x1005108,0x1005200),(0x1005230,0x2100100),(0x43e770,n),(0x43e6f8,0)]:put(addr,value)
  run(0x408874);return visits
 references={n:schedule(n,{}) for n in range(9)}
 for n,actual in references.items():assert actual==[[i,j,n] for i in range(n) for j in range(i+1,n)],('Original static order',n)
 scheduled_batches=0;dynamic_patterns=0;schedule_differences=[]
 for c in contexts['schedules']:
  expected=c['visits'];changes={}
  for i,j,n in expected:
   assert i<j<n<=8
   assert i not in changes or changes[i]==n
   changes[i]=n
  actual=schedule(expected[0][2],changes)
  if actual!=expected:schedule_differences.append(c);break
  scheduled_batches+=c['batches'];dynamic_patterns+=len(set(changes.values()))>1
 phase='pair';coverage=collections.Counter();mutations_by_mode=collections.Counter();diff=[];changed=0;physical=0
 slots=[bytes([0xa5+i])*100 for i in range(8)]
 for index,c in enumerate(contexts['cases']):
  i,j=c['first'],c['second']
  for k,ball in enumerate(slots):put(0x4298c8+k*4,0x1000000+k*128);u.mem_write(0x1000000+k*128,ball)
  for k,n in enumerate((i,j)):u.mem_write(0x1000000+n*128,bytes(c['before'][k]))
  put(0x43e728,c['globals'][0]);put(0x43e764,c['globals'][1]);put(0x43e75c,c['globals'][2])
  run(0x408bfc,i,j)
  actual=[list(u.mem_read(0x1000000+n*128,100)) for n in (i,j)]
  other_ok=all(bytes(u.mem_read(0x1000000+k*128,100))==slots[k] for k in range(8) if k not in (i,j))
  coverage['count_'+str(c['count'])]+=1;coverage['pair_'+str(i)+'_'+str(j)]+=1
  for ball in c['before']:coverage['state_'+str(struct.unpack_from('<H',bytes(ball),0x58)[0])]+=1
  if c['changed']:
   changed+=1;mutations_by_mode[str(c['mode'])]+=1
   if all(struct.unpack_from('<H',bytes(b),0x58)[0]==2 for b in c['before']) and any(x[20:28]!=y[20:28] for x,y in zip(c['before'],c['after'])):physical+=1
  if actual!=c['after'] or not other_ok:diff.append(dict(index=index,tick=c['tick'],unselected_slots_unchanged=other_ok,byte_offsets=[[o for o in range(100) if actual[k][o]!=c['after'][k][o]] for k in range(2)],context=c,actual=actual));break
 missing=[]
 if changed!=contexts['changed'] or not changed:missing.append('all actual pair mutations')
 if len([k for k in coverage if k.startswith('pair_')])!=28:missing.append('all28pairindices')
 if not coverage['count_8']:missing.append('eightballpool')
 if not scheduled_batches:missing.append('natural schedule batches')
 if sum(len(c['visits'])*c['batches'] for c in contexts['schedules'])!=contexts['observed']:missing.append('all native pair visits accounted for')
 if not physical:missing.append('actual active-ball velocity response')
 report=dict(status='VERIFIED' if not(diff or schedule_differences or missing) else 'DIFFERENCE',pair_entry='0x408bfc',scheduler_entry='0x408874',observed_pair_calls=contexts['observed'],retained_pair_calls=contexts['retained'],changed_pair_calls=changed,active_ball_velocity_responses=physical,mutations_by_mode=dict(mutations_by_mode),compared_ball_bytes_per_case=200,coverage=dict(coverage),coverage_missing=missing,scheduler=dict(static_counts=list(references),native_patterns=len(contexts['schedules']),verified_batches=scheduled_batches,dynamic_count_patterns=dynamic_patterns,differences=schedule_differences),differences=diff,image_sha256=hashlib.sha256(image).hexdigest(),lookup_sha256=hashlib.sha256(lut).hexdigest(),route_sha256=hashlib.sha256(route.read_bytes()).hexdigest(),contexts_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),scope='Fresh legal all-five native game; every actual pair mutation and stratified no-ops. Both100-byte records exact under Original actual i/j indices vs native0/1 adapter; unused slots poisoned and unchanged. Original scheduler visitation tested with adapted physics/phase1 and native per-row pool counts. No Original full-tick/clock/spawn/removal equivalence claim.')
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','observed_pair_calls','retained_pair_calls','changed_pair_calls','coverage_missing','scheduler')}))
 assert report['status']=='VERIFIED',('pair/scheduler mismatch',diff[:1],missing)
if __name__=='__main__':main()
