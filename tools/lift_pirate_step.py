#!/usr/bin/env python3
"""Bounded reachable-CFG Retail gameplay intermediate; output stays under build/."""
import argparse,hashlib,json,sys,re
from pathlib import Path
import capstone,pefile
from capstone.x86 import X86_OP_IMM,X86_OP_MEM
import lift_mean_flippers as g
ROOT=Path(__file__).resolve().parents[1]
SHA='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--extra',type=lambda x:int(x,0),nargs='*',default=[]);a=p.parse_args()
 if (ROOT/'analysis/space-full-tick-boundary.json').exists():a.extra.append(0x40404c)
 for table in ('space','demon'):
  if (ROOT/f'analysis/{table}-full-tick-boundary.json').exists():
   profile=json.loads((ROOT/'analysis/table-profiles.json').read_text())['tables'][table]
   a.extra.extend(int(layer['switch_callback'],0) for layer in profile['layers'])
 a.extra=list(set(a.extra)|{0x406600,0x406938,0x437460,0x40950c,0x437bfc,0x43636c,0x434160,0x434268,0x434340,
                          0x405eec,0x405234,0x4071e0,0x4070bc,0x407b88,0x44f4d0,0x44f4c6,0x45021e,0x40bbac,
                          0x405d54,0x405de8,0x408ae0,0x407778,0x408da8,0x408674,0x40b0b4,0x40b2ec,0x405bb4,0x40bbec})
 for name in ('reborn-gameplay-boundary.json','demon-legal-boundary.json','demon-variants-boundary.json','demon-banks-boundary.json','demon-video-boundary.json','demon-final-boundary.json','demon-modes-boundary.json','demon-clock-boundary.json','demon-base-boundary.json','space-variants-boundary.json','space-mission-campaign-boundary.json','space-lane-kickback-boundary.json','space-mission-family-boundary.json','space-multiball-boundary.json','space-multiball-rewards-boundary.json','space-mode-family-boundary.json','space-planet-success-boundary.json','space-bigblam-boundary.json','space-base-rules-boundary.json','space-weapons-boundary.json','space-modes-boundary.json','demon-full-tick-boundary.json','space-full-tick-boundary.json','pirate-full-tick-boundary.json','pirate-lifecycle-boundary.json','pirate-full-input-boundary.json','pirate-complete-game-boundary.json','pirate-adventure-boundary.json','pirate-modes-boundary.json','pirate-knife-boundary.json','pirate-multiball-boundary.json','pirate-multiball-campaign-boundary.json','pirate-magna-boundary.json','pirate-final-boundary.json','pirate-surplus-boundary.json','pirate-magna-eligibility-boundary.json','pirate-magna-keys-boundary.json','pirate-nudge-boundary.json','pirate-lock-matrix-boundary.json','pirate-legal-feedback-boundary.json','pirate-natural-croc-boundary.json','pirate-natural-plank-boundary.json','pirate-natural-feedback-boundary.json','pirate-plank-rope-boundary.json','pirate-plank-two-ropes-boundary.json','pirate-plank-nudge-boundary.json','pirate-mode-feedback-boundary.json','pirate-final-feedback-a-boundary.json','pirate-final-feedback-b-boundary.json','pirate-magnasaver-boundary.json','pirate-magna-capture-boundary.json','pirate-campaign-finite-boundary.json','pirate-campaign-magnets-boundary.json','pirate-plank-super-feedback-boundary.json'):
  boundary=ROOT/'analysis'/name
  if boundary.exists():
   evidence=json.loads(boundary.read_text());assert evidence['build_sha256']==SHA
   a.extra=list(set(a.extra)|{int(edge['target'],16) for edge in evidence['executed_call_edges']})
   a.extra.extend(int(address,16)for address in evidence.get('static_roots',[]))
 exe=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
 raw=exe.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA
 pe=pefile.PE(data=raw);image=pe.get_memory_mapped_image();cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
 # Explicit native gameplay scope. Outside calls are not silently discarded.
 def allowed(x):return 0x407c6c<=x<0x40b600 or 0x40f0d0<=x<0x40f740 or 0x42b390<=x<0x439b00 or (0x439ae0<=x<0x44f4c0 and (ROOT/'analysis/space-full-tick-boundary.json').exists()) or (0x40febc<=x<0x41b9e0 and (ROOT/'analysis/demon-full-tick-boundary.json').exists()) or x in a.extra
 roots={0x409588,0x409154,0x43163c,0x431a44,0x436428,0x4364c4,0x438ea0,0x4397d0,0x439994,*a.extra}
 definitions={};outside=set();dynamic=[]
 while roots-set(definitions):
  root=min(roots-set(definitions));todo=[root];instructions={}
  while todo:
   address=todo.pop()
   if address in instructions:continue
   if not allowed(address) and not (root in a.extra):raise ValueError(f'Unbounded block {address:x}')
   i=next(cs.disasm(image[address-0x400000:address-0x400000+16],address),None)
   if i is None:raise ValueError(f'No instruction {address:x}')
   instructions[address]=i
   if root==0x405234 and address==0x405486:
    todo.append(0x4054e1);continue # Original epilogue; renderer owns interpolation.
   if root==0x408674 and address==0x4086d5:
    todo.append(0x4089cb);continue # Preserve pool compaction before SDL interpolation.
   if i.mnemonic.startswith('ret'):continue
   if i.mnemonic=='call':
    op=i.operands[0]
    if op.type==X86_OP_IMM:
     if allowed(op.imm):roots.add(op.imm)
     else:outside.add(op.imm)
    else:dynamic.append(hex(address))
   if i.mnemonic.startswith('j'):
    op=i.operands[0]
    if op.type==X86_OP_IMM:
     if allowed(op.imm) or root in a.extra:todo.append(op.imm)
     else:outside.add(op.imm)
    elif op.type==X86_OP_MEM and not op.mem.base and op.mem.disp:
     # Only the directly referenced jump directory, never a whole-file scan.
     targets=[]
     for n in range(128):
      offset=op.mem.disp-0x400000+n*4
      value=int.from_bytes(image[offset:offset+4],'little')
      if not allowed(value):break
      roots.add(value);targets.append(hex(value))
     dynamic.append({'instruction':hex(address),'targets':targets})
    else:dynamic.append(hex(address))
    if i.mnemonic=='jmp':continue
   todo.append(address+i.size)
  definitions[root]=[instructions[x] for x in sorted(instructions)]
  if sum(map(len,definitions.values()))>80000:raise ValueError('Gameplay island exceeded instruction budget')
 g.RANGES=[(root,max(i.address+i.size for i in instructions)) for root,instructions in sorted(definitions.items())]
 g.INSTRUCTION_LISTS=definitions
 def custom(i,read,write,start,end):
  mn=i.mnemonic;ops=i.operands
  if start==0x405234 and i.address==0x405486:return 'goto L4054e1;'
  if start==0x408674 and i.address==0x4086d5:return 'goto L4089cb;'
  # CALL reads ESP-relative operands before pushing its return address (video44551a).
  if mn=='call':return '{const auto target='+read(ops[0])+f';m.push({i.address+i.size}u);m.call(target);'+'}'
  if mn=='jmp' or mn.startswith('j'):
   target=ops[0]
   action=f'goto L{target.imm:x};' if target.type==X86_OP_IMM and any(x.address==target.imm for x in definitions[start]) else f'm.call({read(target)});return;'
   if mn=='jmp':return action
   condition={'je':'m.z','jne':'!m.z','jl':'m.s!=m.o','jge':'m.s==m.o','jle':'m.z||(m.s!=m.o)','jg':'!m.z&&(m.s==m.o)','jb':'m.c','ja':'!m.c&&!m.z','jae':'!m.c','jbe':'m.c||m.z','js':'m.s','jns':'!m.s','jo':'m.o','jno':'!m.o'}[mn]
   return f'if({condition}){{{action}}}'
  if mn in ('inc','dec'):
   op=ops[0];method='add' if mn=='inc' else 'sub'
   return '{const auto carry=m.c;'+write(op,f'm.{method}({read(op)},1,{op.size})')+'m.c=carry;}'
  if mn=='adc':return write(ops[0],f'm.adc({read(ops[0])},{read(ops[1])},{ops[0].size})')
  if mn=='sete':return write(ops[0],'(m.z?1u:0u)')
  if mn=='ror':
   bits=ops[0].size*8
   # x86 masks counts to five bits; a full-width rotate still updates CF.
   return ('{const auto count=('+read(ops[1])+')&31u;if(count){const auto value='+read(ops[0])+
       ';const auto shift=count%'+str(bits)+'u;const auto result=shift?((value>>shift)|(value<<('+str(bits)+
       'u-shift)))&'+hex((1<<bits)-1)+'u:value;'+write(ops[0],'result')+
       'm.c=((result>>'+str(bits-1)+')&1u)!=0;if(count==1)m.o=(((result>>'+str(bits-1)+
       ')^(result>>'+str(bits-2)+'))&1u)!=0;}}')
  if mn in ('cld','std'):return 'm.direction='+('true;' if mn=='std' else 'false;')
  if mn in ('rep stosd','rep stosw','rep stosb','rep movsd','rep movsw','rep movsb','stosd','stosw','stosb','movsb','movsw','movsd'):
   length=4 if mn.endswith('d') else 2 if mn.endswith('w') else 1;repeat=mn.startswith('rep ');move='movs' in mn
   body=(f'm.wr(m.r[7],m.rd(m.r[6],{length}),{length});m.r[6]+=m.direction?-{length}u:{length}u;' if move else f'm.wr(m.r[7],m.r[0],{length});')+f'm.r[7]+=m.direction?-{length}u:{length}u;'
   return 'while(m.r[1]){'+body+'--m.r[1];}' if repeat else body
  if mn=='xchg':return '{const auto temp='+read(ops[0])+';'+write(ops[0],read(ops[1]))+write(ops[1],'temp')+'}'
  if mn=='leave':return 'm.r[4]=m.r[5];m.r[5]=m.pop();'
  return None
 g.INSTRUCTION_HANDLER=custom
 code,_=g.generate(exe,SHA)
 code=code.replace('physics/flipper_lift.h','physics/pirate_step_lift.h').replace('FlipperLift','PirateStepLift').replace('flipper_','pirate_')
 code=re.sub(r'L([0-9a-f]+): ',lambda x:f'L{x[1]}: if(m.instruction_observer)m.instruction_observer(m,0x{x[1]}); ',code)
 code+='namespace slam {void PirateStepLift::call(std::uint32_t address){last_entry=address;if(call_observer)call_observer(*this,address);switch(address){\n'
 for root in sorted(definitions):code+=f'case {root}u:pirate_{root:x}(*this);return;\n'
 code+='default:external(address);return;}}}\n'
 output=ROOT/'build/generated/pirate_step.cpp';output.parent.mkdir(parents=True,exist_ok=True);output.write_text(code)
 report={'build_sha256':SHA,'method':'Reachable CFG static C++ intermediate, fixed compiled instructions, no runtime decoder','roots':[hex(x) for x in sorted(definitions)],'instructions':sum(map(len,definitions.values())),'outside_calls':[hex(x) for x in sorted(outside)],'dynamic_sites':dynamic,'runtime_unsupported':'throws; no silent stubs'}
 (ROOT/'build/generated/pirate_step-map.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k in ('instructions','outside_calls')}))
if __name__=='__main__':main()
