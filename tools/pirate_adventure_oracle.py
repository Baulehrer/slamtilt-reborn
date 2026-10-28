#!/usr/bin/env python3
"""Original Pirate Adventure trajectories driven by diagnostic physical waypoints.

Waypoints change only free-ball position, velocity and validated layer bindings.
No rule, score, timer, capture-state or callback injection. Private assets below
build/. This is a directed collision integration proof, not a human-input run.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

import capstone
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_ESP, UC_X86_REG_EIP
import unicorn.x86_const as registers
from capstone.x86 import X86_OP_REG, X86_OP_MEM
from pirate_full_tick_oracle import ROOT, BUILD_SHA, DAT_SHA, OBJ, DAT, STACK, STOP
from verify_pirate_full_tick import TIMING


def digest(data):
    return hashlib.sha256(data).hexdigest()


def compact(value):
    return json.dumps(value, separators=(',', ':')).encode()


class Original:
    def __init__(self, prepared, track_edges=False, table="pirate"):
        self.u = Uc(UC_ARCH_X86, UC_MODE_32)
        for address, size in [(0x400000, 0x100000), (OBJ, 0x400000),
                              (0x2000000, 0x10000), (STOP, 0x1000)]:
            self.u.mem_map(address, size)
        self.table=table
        fixture = json.loads((ROOT/'analysis/traces/pirate-complete-game.json' if table=='pirate' else prepared/'summary.json').read_text())
        for address, name in [(0x400000, 'human-image.bin'), (OBJ, 'human-runtime.bin'), (DAT, 'human-dat.bin')]:
            data = (prepared/name).read_bytes()
            assert digest(data) == fixture['context_hashes'][name]
            self.u.mem_write(address, data)
        # The retained isolated context assigned46c66c after the service ABI
        # startup. Complete its original405b6a..405b78 sine-table binding now.
        # No clock/player/ball/rule state changes in these three instructions.
        if table=='pirate':self.run(0x405b6a,until=0x405b79)
        self.layers = json.loads((ROOT/'analysis/table-profiles.json').read_text())['tables'][table]['layers']
        self.lamp_descriptors = [self.get(self.get(0x46b74c)+i*4) for i in range(self.get(0x46c6a4))]
        self.calls = Counter()
        self.indirect = {}
        self.call_hooks = []
        self.tracking = False
        if track_edges:
            self.track_calls()

    def track_calls(self, exclude=(), extra_ranges=()):
        if self.tracking:
            return
        self.tracking = True
        image = bytes(self.u.mem_read(0x400000, 0x100000))
        cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        cs.detail = True
        table_range={'pirate':(0x42b390,0x439b00),'space':(0x439ae0,0x44f4c0),'demon':(0x40febc,0x41b9e0)}[self.table]
        for section_start, section_end in [(0x405234,0x4054f9),(0x405fac,0x4060f4),(0x406938,0x406aa0),(0x407b88,0x407c49),table_range,*([] if self.table=="pirate" else [(0x409154,0x40b600)]),*extra_ranges]:
            for instruction in cs.disasm(image[section_start-0x400000:section_end-0x400000], section_start):
                if any(lo <= instruction.address < hi for lo, hi in exclude):
                    continue
                if instruction.mnemonic == 'call' and not instruction.op_str.startswith('0x'):
                    self.indirect[instruction.address] = instruction
                    self.call_hooks.append(self.u.hook_add(UC_HOOK_CODE, self._indirect,
                                    begin=instruction.address, end=instruction.address))
        # Late hooks must also cover already translated clock/DMD blocks.
        # This invalidates Unicorn's translation cache, not game memory/state.
        self.u.ctl_remove_cache(0x400000,0x452000)

    def pause_calls(self):
        for hook in self.call_hooks:
            self.u.hook_del(hook)
        self.call_hooks.clear()
        self.tracking = False
        self.u.ctl_remove_cache(0x400000,0x452000)

    def _indirect(self, u, address, size, _):
        instruction = self.indirect[address]
        operand = instruction.operands[0]
        def reg(number):
            return u.reg_read(getattr(registers, 'UC_X86_REG_' + instruction.reg_name(number).upper())) if number else 0
        if operand.type == X86_OP_REG:
            target = reg(operand.reg)
        else:
            assert operand.type == X86_OP_MEM
            m = operand.mem
            target = self.get((reg(m.base) + reg(m.index)*m.scale + m.disp) & 0xffffffff)
        self.calls[(address, target)] += 1

    def get(self, address, n=4):
        return int.from_bytes(self.u.mem_read(address, n), 'little')

    def put(self, address, value, n=4):
        self.u.mem_write(address, (value & ((1 << (n*8))-1)).to_bytes(n, 'little'))

    def run(self, address, eax=0, edx=None, until=STOP):
        self.put(STACK, STOP)
        self.u.reg_write(UC_X86_REG_ESP, STACK)
        self.u.reg_write(UC_X86_REG_EAX, eax)
        if edx is not None:
            self.u.reg_write(UC_X86_REG_EDX, edx)
        self.u.emu_start(address, until, count=800000)
        assert self.u.reg_read(UC_X86_REG_EIP) == until, hex(self.u.reg_read(UC_X86_REG_EIP))
        if until == STOP:
            assert self.u.reg_read(UC_X86_REG_ESP) == STACK+4

    def shot(self, layer, x, y, ball_index=0):
        assert isinstance(ball_index,int) and 0 <= ball_index < min(8,self.get(0x46c67c)), 'Invalid active ball index'
        ball_address=0x46c15c+100*ball_index
        assert self.get(ball_address+0x58, 2) == 2, 'Only reposition a free ball'
        assert 0 <= layer < len(self.layers) and 0 <= x < 320 and 0 <= y < 600, 'Invalid diagnostic Pirate shot'
        profile = self.layers[layer]
        for offset, value, length in [(0, x << 16, 4), (4, y << 16, 4),
                (8, x << 16, 4), (12, y << 16, 4), (20, 0, 4), (24, 0, 4),
                (0x40, DAT+profile['hit_offset'], 4), (0x44, DAT+profile['normal_offset'], 4),
                (0x54, DAT+profile['render_offset'], 4), (0x4c, profile['stride'], 4),
                (0x50, profile['planes'], 4), (0x48, layer, 2), (0x38, 65535, 2), (0x3a, 65535, 2)]:
            self.put(ball_address+offset, value, length)

    def step(self, tick):
        self.run(0x405234, (tick+1)*5, until=0x405486)
        if (tick+1) % 4 == 0:
            self.run(0x408da8)
            # Actual render preparation40566f owns gameplay pool compaction.
            # Run its integer prefix, then its original balanced epilogue;
            # exclude only later interpolation/visibility/sprite sorting.
            self.run(0x408674,until=0x4086d5)
            self.u.emu_start(0x4089cb,STOP,count=100)
            assert self.u.reg_read(UC_X86_REG_EIP)==STOP
            assert self.u.reg_read(UC_X86_REG_ESP)==STACK+4

    def ball(self):
        return list(self.u.mem_read(0x46c15c, 100))

    def timing(self):
        return [self.get(a, n) for a, n in [(0x46c734,4),(0x46c744,4),(0x46c740,4),
            (0x46c704,4),(OBJ+0x900c,4),(0x46c6b4,4),(0x46c6b8,4),(0x46c6ac,4),
            (0x46c68c,4),(0x46e554,2),(0x46e53a,2)]]

    def sample(self):
        g = self.get
        record = g(0x46b758)
        lifecycle = [g(0x46c6ac),g(0x46c67c),g(0x46c680),g(0x46c684),g(record+14,2),
                     g(record+16,2),g(0x46c61c),g(0x46c620),*self.u.mem_read(record,6),g(0x46c60c)]
        lamps = b''.join(bytes(self.u.mem_read(descriptor+8,2))for descriptor in self.lamp_descriptors)
        return dict(timing=self.timing(), lifecycle=lifecycle,
            dmd_sha256=digest(bytes(self.u.mem_read(g(0x46c47c),1920))),
            highscore_sha256=digest(bytes(self.u.mem_read(0x46c542,50))), lamp_sha256=digest(lamps),
            rule_sha256=digest(bytes(self.u.mem_read(0x46e220,0x360))),
            ball_pool_sha256=digest(bytes(self.u.mem_read(0x46c15c,800))),
            video_sha256=digest(b''.join(bytes(self.u.mem_read(begin,end-begin))for begin,end in
                [(0x46e0b4,0x46e220),(0x465970,0x465a80),(0x46c67c,0x46c77c)])))

    def milestone(self, tick, label):
        g=self.get
        return dict(tick=tick,label=label,phase=g(0x46c6ac),adventure=g(0x46e2c0,2),
            timer=g(0x46e546,2),super_jackpot=g(0x46e556,2),
            played=list(self.u.mem_read(0x46e2c2,6)),targets=list(self.u.mem_read(0x46e564,5)),
            score_bcd=bytes(self.u.mem_read(g(0x46b758),6)).hex(),ball_state=g(0x46c1b4,2))


def generate(prepared, output, outcome):
    m=Original(prepared, track_edges=outcome=='success')
    states=[m.ball()];samples=[];inputs=[];shots=[];milestones=[]
    tick=0
    def step():
        nonlocal tick
        m.step(tick);states.append(m.ball());samples.append(m.sample());tick+=1
    def shot(label,layer,x,y):
        shots.append(dict(tick=tick,label=label,layer=layer,x=x,y=y))
        m.shot(layer,x,y);step()
        if label!='timeout_free_flight':milestones.append(m.milestone(tick,label))
    def free():
        start=tick
        while m.get(0x46c1b4,2)!=2:
            step()
            assert tick-start<4000,'Capture did not release'
    while tick<600:
        if tick in (200,201):
            m.run(0x40404c,0 if tick==200 else 1,0x1c)
            inputs.append(dict(tick=tick,action='enter',down=tick==200))
        step()
    shot('right_ramp_arm',1,225,45)
    shot('upper_left_entry',0,24,60)
    while m.get(0x46c6ac)!=5:
        step()
        assert tick<1000,'Adventure entry did not start'
    free()
    assert m.get(0x46c6ac)==5 and m.get(0x46e2c0,2)==0
    milestones.append(m.milestone(tick,'plank_started_and_released'))
    # Real return-lane switch resets a shared capture-release gate. Skipping
    # this transit with teleportation leaves later captures correctly waiting.
    shot('return_lane',2,70,340)
    if outcome=='success':
        for label,layer,x,y in [('rope_4',1,81,228),('duplicate_rope_4',1,81,228),
                ('rope_2',1,49,74),('rope_3',1,225,45),('clear_guide',0,160,400),
                ('skull_guide',0,41,162),('rope_1',2,91,44),('rope_0_trap',0,302,185)]:
            shot(label,layer,x,y);free()
        assert list(m.u.mem_read(0x46e564,5))==[0]*5 and m.get(0x46e556,2)==1
        milestones.append(m.milestone(tick,'five_ropes_super_jackpot_lit'))
        shot('super_jackpot_trap',0,86,10);free()
        assert m.get(0x46c6ac)==2 and m.get(0x46e2c0,2)==1
        milestones.append(m.milestone(tick,'super_jackpot_and_return'))
    else:
        while m.get(0x46c6ac)==5:
            if m.get(0x46e546,2)<=8:m.track_calls()
            if tick%40==0:shot('timeout_free_flight',0,160,400)
            else:step()
            assert tick<16000
        assert m.get(0x46c6ac)==2
        milestones.append(m.milestone(tick,'plank_timeout_return'))
    # Preserve observed mode-result frame for the SDL capture; then ordinary
    # physics resumes. Finite whole-game regression remains a separate proof.
    for _ in range(40):step()
    while tick%4:step()
    trace=dict(schema=1,build_sha256=BUILD_SHA,dat_sha256=DAT_SHA,tick_count=tick,
        outcome=outcome,inputs=inputs,diagnostic_shots=shots,milestones=milestones,states=states,
        **{k:[s[k]for s in samples]for k in samples[0]},timing_fields=TIMING,
        executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(m.calls.items())],
        gameplay_stubs=[],scope='Diagnostic free-ball waypoints, actual DAT triggers and full original clock; not legal-human-input trajectory')
    # Independent fresh original replay uses the frozen schedule, no outcome
    # policy or state-based target selection on this pass.
    replay=Original(prepared);shot_by_tick={s['tick']:s for s in shots};key_by_tick={e['tick']:e for e in inputs}
    for t in range(tick):
        if t in key_by_tick:replay.run(0x40404c,0 if key_by_tick[t]['down']else 1,0x1c)
        if t in shot_by_tick:
            s=shot_by_tick[t];replay.shot(s['layer'],s['x'],s['y'])
        replay.step(t)
        assert replay.ball()==states[t+1],('ball replay',t)
        assert replay.sample()==samples[t],('state replay',t)
    trace['deterministic_original_replay']=True
    output.mkdir(parents=True,exist_ok=True)
    (output/'trace.json').write_bytes(compact(trace)+b'\n')
    fixture={k:v for k,v in trace.items()if k not in ('states','timing','lifecycle','dmd_sha256','highscore_sha256','lamp_sha256','rule_sha256','video_sha256','ball_pool_sha256','executed_call_edges')}
    fixture.update(states_sha256=digest(bytes(v for s in states for v in s)),
        timing_sha256=digest(compact(trace['timing'])),lifecycle_sha256=digest(compact(trace['lifecycle'])))
    for key in ['dmd_sha256','highscore_sha256','lamp_sha256','rule_sha256','video_sha256','ball_pool_sha256']:
        fixture[key.replace('_sha256','_sequence_sha256')]=digest(''.join(trace[key]).encode())
    (ROOT/f'analysis/traces/pirate-plank-{outcome}.json').write_text(json.dumps(fixture,indent=2)+'\n')
    return trace


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared',type=Path,default=ROOT/'build/oracle/pirate-full-tick')
    p.add_argument('--output',type=Path,default=ROOT/'build/oracle/pirate-adventure')
    p.add_argument('--outcome',choices=['success','timeout','both'],default='both')
    args=p.parse_args()
    assert args.output.resolve().is_relative_to(ROOT/'build'),'Original outputs must remain below build/'
    names=['success','timeout']if args.outcome=='both'else[args.outcome]
    traces=[generate(args.prepared,args.output/name,name)for name in names]
    edges=Counter()
    for trace in traces:
        for edge in trace['executed_call_edges']:edges[(edge['callsite'],edge['target'])]+=edge['count']
    boundary=dict(build_sha256=BUILD_SHA,gameplay_stubs=[],
        executed_call_edges=[dict(callsite=a,target=b,count=n)for(a,b),n in sorted(edges.items())],
        scope='Observed indirect calls in original Plank success/timeout fixtures; diagnostic ball waypoints')
    (ROOT/'analysis/pirate-adventure-boundary.json').write_text(json.dumps(boundary,indent=2)+'\n')
    print(json.dumps({t['outcome']:dict(steps=t['tick_count'],milestones=t['milestones'][-2:])for t in traces}))


if __name__=='__main__':main()
