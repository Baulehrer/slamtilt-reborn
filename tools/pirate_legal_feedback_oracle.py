#!/usr/bin/env python3
"""Freeze naturally reached unsupported original callbacks; legal keys only."""
import argparse,json
from collections import Counter
import capstone
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX
from pirate_adventure_oracle import ROOT, BUILD_SHA, DAT_SHA, compact, digest
from pirate_multiball_oracle import Multiball

INDICES=[5,8,12,23,29,32,83]
TARGETS=[0x406650,0x42c514,0x42dbb4,0x42e2f8,0x42cf8c,0x42f44c,0x42dd00,0x42e478,0x42e718,0x42d640]

def callsite(m,ret):
    cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    for length in range(2,7):
        decoded=list(cs.disasm(bytes(m.u.mem_read(ret-length,length)),ret-length))
        if len(decoded)==1 and decoded[0].mnemonic=='call' and decoded[0].size==length:
            ins=decoded[0]
            return dict(callsite=hex(ins.address),bytes=ins.bytes.hex(),instruction=ins.mnemonic+' '+ins.op_str)
    raise AssertionError(('No bounded call instruction',hex(ret)))

def generate(policy,tail_steps=600):
    index=policy['index'];target=int(policy['error'].split()[-1],16)
    case=f'legal-feedback-{target:x}';r=Multiball(0);m=r.m;g=m.get
    failure=policy['steps'];end=(failure+tail_steps+3)//4*4
    records=[];edges=Counter();entry_counter=Counter();first_last={};draws={}
    service=g(0x46e2b4)
    draw_targets={g(service+offset):offset for offset in [0x3c,0x40,0x44,0x48,0x4c]}
    watched=set(TARGETS)|set(draw_targets)
    def entered(u,address,size,_):
        ret=g(u.reg_read(UC_X86_REG_ESP));site=callsite(m,ret)
        edges[(int(site['callsite'],16),address)]+=1
        if address in TARGETS:
            entry_counter[address]+=1
            value=dict(tick=r.tick,target=hex(address),return_address=hex(ret),**site,
                phase=g(0x46c6ac),field_46c690=g(0x46c690),field_46c698=g(0x46c698),
                engine_context_counter=g(g(0x46e2b0)+0x1c),registers=dict(eax=u.reg_read(UC_X86_REG_EAX),ebx=u.reg_read(UC_X86_REG_EBX),ecx=u.reg_read(UC_X86_REG_ECX),edx=u.reg_read(UC_X86_REG_EDX)))
            records.append(value);first_last.setdefault(address,[r.tick,r.tick])[1]=r.tick
        elif failure-8<=r.tick<=end:
            eax=u.reg_read(UC_X86_REG_EAX)
            key=(address,int(site['callsite'],16),eax)
            row=draws.setdefault(key,dict(target=hex(address),service_offset=hex(draw_targets[address]),**site,
                eax=eax,first_tick=r.tick,last_tick=r.tick,count=0))
            row['count']+=1;row['last_tick']=r.tick
    def dmd_dispatch(u,address,size,_):
        edges[(address,g(0x46c69c))]+=1
    hooks=[m.u.hook_add(UC_HOOK_CODE,entered,begin=a,end=a)for a in watched]
    hooks.append(m.u.hook_add(UC_HOOK_CODE,dmd_dispatch,begin=0x407c09,end=0x407c09))
    m.u.ctl_remove_cache(0x400000,0x452000)
    left=right=False
    while r.tick<end:
        tick=r.tick
        if tick==max(0,failure-8):m.track_calls()
        if tick==failure+88:m.pause_calls()
        if g(0x46c6ac)==1 and (tick==0 or tick%200==0):
            r.key('enter',True);r.key('enter',False)
        mask=policy['b']if ((tick+policy.get('offset',0))//policy['period'])%2 else policy['a']
        nl,nr=bool(mask&1),bool(mask&2)
        if nl!=left:r.key('left',nl)
        if nr!=right:r.key('right',nr)
        left,right=nl,nr
        if tick==failure:r.mark('native_missing_call_boundary')
        r.step()
    m.pause_calls()
    r.mark('original_continuation')
    # Recorder.finish adds80steps and independently replays every frozen action.
    trace=r.finish(case)
    for hook in hooks:m.u.hook_del(hook)
    assert entry_counter[target]>0,(case,'target not reached')
    for edge,count in edges.items():m.calls[edge]=max(m.calls[edge],count)
    scope='Original Retail from canonical reset with only actual Enter/Shift edges; no diagnostic shots or gameplay-state injection. Native missing-call policy extended600steps; original replay independently verifies all normal state vectors. Post-prefix x87 raster excluded as existing integer oracle.'
    trace.update(scope=scope,source_policy=policy,missing_target=hex(target),target_entries=records,
        target_entry_counts={hex(a):v for a,v in sorted(entry_counter.items())},draw_service_entries=list(draws.values()),
        executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(m.calls.items())])
    (ROOT/'build/oracle/pirate-modes'/case/'trace.json').write_bytes(compact(trace)+b'\n')
    path=ROOT/f'analysis/traces/pirate-{case}.json';fixture=json.loads(path.read_text())
    for key in ['scope','source_policy','missing_target','target_entry_counts','draw_service_entries']:fixture[key]=trace[key]
    fixture['target_entries_sha256']=digest(compact(records))
    fixture['target_entry_samples']=[rows[i]for target in sorted(entry_counter)for rows in [[v for v in records if v['target']==hex(target)]]for i in sorted({0,len(rows)-1})]
    path.write_text(json.dumps(fixture,indent=2)+'\n')
    print('VERIFIED',case,'entries',dict(trace['target_entry_counts']),'draws',len(draws),flush=True)
    return trace

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--search',type=lambda s:ROOT/s)
    p.add_argument('--boundary',default='pirate-natural-feedback-boundary.json')
    p.add_argument('--tail-steps',type=int,default=600)
    args=p.parse_args()
    if args.search:
        search=json.loads(args.search.read_text());selected=[];seen=set()
        for policy in search['policies']:
            if not policy['error']:continue
            target=int(policy['error'].split()[-1],16)
            if target in seen:continue
            seen.add(target);selected.append(policy)
            if target not in TARGETS:TARGETS.append(target)
    else:
        selected=None
    search=json.loads((ROOT/'build/oracle/pirate-legal-key-search/search.json').read_text())
    edges=Counter();cases=[];entries=[]
    post=json.loads((ROOT/'build/oracle/pirate-legal-key-search-after-feedback/search.json').read_text())
    if selected is None:selected=[search['policies'][i]for i in INDICES]+[post['policies'][i]for i in [11,18,29]]
    for policy in selected:
        index=policy['index'];trace=generate(policy,args.tail_steps);cases.append(trace['case'])
        entries.append(dict(case=trace['case'],steps=trace['tick_count'],target=trace['missing_target'],
            counts=trace['target_entry_counts'],source_policy=index))
        for edge in trace['executed_call_edges']:edges[(edge['callsite'],edge['target'])]+=edge['count']
    boundary=dict(schema=1,build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,cases=cases,fixtures=entries,gameplay_stubs=[],
        scope='Legal-key-only original continuations from frozen missing-call native policies. Indirect call hooks limited to96steps around failure; concrete callback/draw entries tracked separately. Counts are bounded observations, not exhaustive engine callgraph.',
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())])
    name=args.boundary if args.search else 'pirate-legal-feedback-boundary.json'
    (ROOT/'analysis'/name).write_text(json.dumps(boundary,indent=2)+'\n')

if __name__=='__main__':main()
