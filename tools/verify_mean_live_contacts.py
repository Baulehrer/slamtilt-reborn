#!/usr/bin/env python3
"""Original408e70 vs native contacts reached by the all-five legal-input game.

Compares all100 ball bytes at material dispatch, then complete response and
separation including Original material callbacks, with explicit external service adapters.
This is a component differential from natural states, not paired trajectories.
"""
import argparse, collections, hashlib, json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP, UC_X86_REG_EIP
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--probe',type=Path,default=R/'build/native/mean_contact_context_probe')
 p.add_argument('--contexts',type=Path,default=R/'build/oracle/mean-live-contacts.json')
 p.add_argument('--output',type=Path,default=R/'analysis/traces/mean-live-contacts-original.json')
 a=p.parse_args();prep=R/'build/mean-prepared';route=R/'analysis/traces/mean-five-modes-input.json'
 route_fixture=json.loads(route.read_text())
 dat_path=next((R/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'));dat=dat_path.read_bytes();image=(prep/'pe-data.bin').read_bytes()
 assert route_fixture['dat_sha256']==hashlib.sha256(dat).hexdigest()
 assert route_fixture['image_sha256']==hashlib.sha256(image).hexdigest()
 a.contexts.parent.mkdir(parents=True,exist_ok=True)
 routes=(route,R/'analysis/traces/mean-live-goal-input.json')
 contexts=dict(observed=0,retained=0,selection='First six per mode/layer/contact-kind/material/nudge/multiball/mutable-geometry bucket in each fresh route',cases=[])
 route_hashes={}
 for route_index,route_path in enumerate(routes):
  output=a.contexts.with_name(a.contexts.stem+'-'+str(route_index)+'.json')
  subprocess.run([str(a.probe),str(dat_path),str(prep),str(R/'analysis/traces/mean-flight-100.json'),str(route_path),str(output)],check=True)
  part=json.loads(output.read_text());contexts['observed']+=part['observed'];contexts['retained']+=part['retained']
  route_hashes[str(route_path.relative_to(R))]=hashlib.sha256(route_path.read_bytes()).hexdigest()
  for c in part['cases']:c['route']=route_index;contexts['cases'].append(c)
 a.contexts.write_text(json.dumps(contexts,separators=(',',':')))

 u=Uc(UC_ARCH_X86,UC_MODE_32)
 for addr,n in [(0x400000,0x100000),(0x1000000,0x10000),(0x1100000,(len(dat)+4095)//4096*4096),(0x2000000,0x10000),(0x2100000,0x2000)]:u.mem_map(addr,n)
 u.mem_write(0x400000,image);u.mem_write(0x1100000,dat);u.mem_write(0x1006000,(prep/'lookup.bin').read_bytes())
 def put(addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
 def word(addr,value):u.mem_write(addr,struct.pack('<H',value&0xffff))
 def relocated(ball,base):
  b=bytearray(ball)
  for o in (0x40,0x44,0x54):
   v=struct.unpack_from('<I',b,o)[0]
   if base<=v<base+len(dat):struct.pack_into('<I',b,o,0x1100000+v-base)
  return bytes(b)
 # Original indirection interfaces; only data/dispatch pointers are relocated.
 for addr,value in [(0x43e740,0x1005000),(0x1005000,0x1005600),(0x1005004,0x1005100),(0x1005104,0x1005300),(0x43f0d0,0x1002000)]:put(addr,value)
 descriptor=struct.unpack_from('<I',(prep/'engine-globals.bin').read_bytes(),0x40)[0]
 graphics=struct.unpack_from('<I',image,descriptor-0x400000)[0]
 third_flipper=struct.unpack_from('<H',image,graphics-0x400000+0x1c)[0]
 assert third_flipper==1,('Mean native third-flipper contract',hex(graphics),third_flipper)
 word(0x100561c,third_flipper)
 for k,callback in enumerate((0x41e00c,0x41e800,0x41e8b8,0x41e828,0x41e828)):put(0x1005300+k*4,callback)
 profiles=json.loads((R/'analysis/table-profiles.json').read_text())['tables']['mean']['layers']

 services=collections.Counter();handle=0
 for offset,target in ((0x58,0x2101000),(0x5c,0x2101010),(0x34,0x2101020),(0x80,0x2101030)):put(0x1002000+offset,target)
 def service(uc,addr,size,data):
  services[hex(addr)]+=1
  sp=uc.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',uc.mem_read(sp,4))[0]
  if addr==0x2101020:uc.reg_write(UC_X86_REG_EAX,handle)
  uc.reg_write(UC_X86_REG_ESP,sp+4+(12 if addr==0x2101020 else 0));uc.reg_write(UC_X86_REG_EIP,ret)
 for addr in (0x2101000,0x2101010,0x2101020,0x2101030):u.hook_add(UC_HOOK_CODE,service,begin=addr,end=addr)
 phase='dispatch';wall=False
 def boundary(uc,addr,size,data):
  nonlocal wall
  wall=True
  if phase=='dispatch':uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,boundary,begin=0x409bec,end=0x409bec)
 differences=[];coverage=collections.Counter();full=collections.Counter();excluded=collections.Counter()
 for index,c in enumerate(contexts['cases']):
  ball=0x1000000+c['ball_index']*128
  for y in range(30):u.mem_write(0x1100000+profiles[0]['normal_offset']+0x49e1+y*40,bytes(c['lane_saver_normal'][y*4:y*4+4]))
  for plane in range(4):
   for y in range(32):u.mem_write(0x1100000+profiles[0]['hit_offset']+0x49e1+plane*0x6040+y*40,bytes(c['lane_saver_hit'][plane*128+y*4:plane*128+y*4+4]))
  u.mem_write(0x43f000,bytes(c['cached_fields']));u.mem_write(0x43ee1c,bytes(c['fields_ee1c']))
  put(0x43f0d0,0x1002000);put(0x43f068,0x1001000);put(0x1001030,c['mode'])
  for k,l in enumerate(profiles):
   for j,v in enumerate((l['planes'],l['stride'],0x1100000+l['normal_offset'],0x1100000+l['hit_offset'],0x1100000+l['render_offset'])):put(0x43f06c+k*20+j*4,v)
  for addr,words in [(0x43e700,c['engine_words']),(0x43e850,c['flipper_words'])]:u.mem_write(addr,struct.pack('<'+'I'*len(words),*words))
  for addr,value in [(0x43e740,0x1005000),(0x43e764,0x1006000),(0x43e744,0x1006800),(0x43e728,0x42c9fc),(0x43e71c,c['nudge'][0]),(0x43e410,c['nudge'][1]),(0x43e724,c['nudge'][2]),(0x43e564,c['nudge'][3]),(0x4298c8+c['ball_index']*4,ball),(0x100201c,c['material_context']['services_1c'])]:put(addr,value)
  word(0x43f1da,c['material_context']['field_1da']);word(0x43f390,c['material_context']['field_390'])
  u.mem_write(ball,relocated(c['before'],c['dat_base']));put(0x200f000,0x2100000)
  u.reg_write(UC_X86_REG_ESP,0x200f000);u.reg_write(UC_X86_REG_EAX,c['ball_index'])
  phase='dispatch';wall=False
  u.emu_start(0x408e70,0x2100000,count=30000)
  pc=u.reg_read(UC_X86_REG_EIP)
  assert pc in (0x409bec,0x2100000),('instruction limit',index,hex(pc))
  actual=bytes(u.mem_read(ball,100));expected=relocated(c['dispatch'],c['dat_base'])
  coverage[c['kind']]+=1;coverage['mode_'+str(c['mode'])]+=1;coverage['layer_'+str(struct.unpack_from('<H',bytes(c['before']),0x48)[0])]+=1
  if any(c['nudge']):coverage['active_nudge']+=1
  if c['ball_count']>1:coverage['multiball']+=1
  coverage['geometry_'+str(c['geometry_hash'])]+=1
  if wall!=c['wall'] or actual!=expected:
   differences.append(dict(index=index,tick=c['tick'],stage='dispatch',wall=[wall,c['wall']],byte_offsets=[i for i in range(100) if actual[i]!=expected[i]],context=c,actual=list(actual)))
   break
  if not wall:continue # Complete free/flipper response already compared.
  layer=struct.unpack_from('<H',actual,0x48)[0];material=struct.unpack_from('<H',actual,0x3c)[0]
  # Replay both display-admission answers. Actual419da4/41e724/40f754 run;
  # service adapters only collect score/audio or return a display handle.
  machine=u.context_save();memory=bytes(u.mem_read(0x400000,0x100000));runtime=bytes(u.mem_read(0x1000000,0x10000));stack=bytes(u.mem_read(0x2000000,0x10000))
  for handle in (0,1):
   u.context_restore(machine);u.mem_write(0x400000,memory);u.mem_write(0x1000000,runtime);u.mem_write(0x2000000,stack)
   phase='full'
   try:u.emu_start(0x409bec,0x2100000,count=30000)
   except Exception as exc:raise RuntimeError(('full',index,c['tick'],layer,material,handle,hex(u.reg_read(UC_X86_REG_EIP)))) from exc
   assert u.reg_read(UC_X86_REG_EIP)==0x2100000,('full contact did not return',index)
   actual=bytes(u.mem_read(ball,100));expected=relocated(c['after'],c['dat_base']);full['layer'+str(layer)+'_material'+str(material)+'_admit'+str(handle)]+=1
   if actual!=expected:
    differences.append(dict(index=index,tick=c['tick'],stage='full',admitted=handle,byte_offsets=[i for i in range(100) if actual[i]!=expected[i]],context=c,actual=list(actual)));break
  if differences:break

 required=('free','flipper','wall','active_nudge','multiball','mode_1','mode_2','mode_5','mode_6',*(f'layer_{i}' for i in range(5)))
 missing=[key for key in required if not coverage[key]]
 if len([key for key in coverage if key.startswith('geometry_')])<2:missing.append('both mutable LaneSaver states')
 if sum(full.values())!=2*coverage['wall']:missing.append('all wall responses under both admission answers')
 report=dict(status='DIFFERENCE' if differences or missing else 'VERIFIED',routes=list(route_hashes),original_entry='0x408e70',dispatch_boundary='0x409bec',observed=contexts['observed'],retained=contexts['retained'],coverage_missing=missing,selection=contexts['selection'],coverage=dict(coverage),full_response_separation=dict(full),excluded_full_material_callbacks=dict(excluded),differences=differences,dat_sha256=hashlib.sha256(dat).hexdigest(),image_sha256=hashlib.sha256(image).hexdigest(),route_sha256=route_hashes,contexts_sha256=hashlib.sha256(a.contexts.read_bytes()).hexdigest(),third_flipper_source=dict(descriptor=hex(descriptor),graphics=hex(graphics),field_1c=third_flipper),services=dict(services),scope='All100 ball bytes, actual native live flipper poses/nudge/bitmap pointers and mutable LaneSaver geometry tiles; Original contact orchestration and complete free/flipper responses; complete wall response+separation including Original material callbacks, with score/audio/display services adapted. Both accepted/rejected display handles tested; Original419da4/41e724/40f754 execute. Raw rule cache copied, critical material gate/timer exported directly; global rule/service outcomes not compared. No point-force/integration/table switches/pair collisions or global score/audio/lamp comparison; not full Original trajectories.')
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ('status','observed','retained','coverage','full_response_separation','excluded_full_material_callbacks')}))
 if differences:print(json.dumps({k:v for k,v in differences[0].items() if k not in ('context','actual')}));raise SystemExit(1)
 assert not missing,('missing coverage',missing)

if __name__=='__main__':main()
