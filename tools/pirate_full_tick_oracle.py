#!/usr/bin/env python3
"""Original Retail table 200-Hz physics + 50-Hz rule/display trajectory.

Executes original405234 through405486 with elapsed milliseconds in EAX.
Only the final FPU display interpolation is excluded. No gameplay/output
services are replaced. Original artifacts remain below build/.
"""
import argparse
from collections import Counter
import hashlib
import json
import struct
from pathlib import Path

import pefile
import capstone
from unicorn import (Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE,
                     UC_HOOK_MEM_INVALID, UC_HOOK_MEM_WRITE)
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EDX,
                               UC_X86_REG_ESP, UC_X86_REG_EIP)

ROOT = Path(__file__).resolve().parents[1]
BUILD_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_SHA = '6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6'
EXE = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
OBJ, DAT, STACK, STOP = 0x1000000, 0x1100000, 0x200f000, 0x2100000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, separators=(',', ':')) + '\n')


def fields(state):
    data = bytes(state)
    return dict(x=struct.unpack_from('<i', data, 0)[0],
                y=struct.unpack_from('<i', data, 4)[0],
                vx=struct.unpack_from('<i', data, 20)[0],
                vy=struct.unpack_from('<i', data, 24)[0],
                state_58=struct.unpack_from('<H', data, 88)[0],
                field_5c=struct.unpack_from('<H', data, 92)[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--table',choices=['pirate','space','demon'],default='pirate')
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--display-lut',action='store_true',default=True,help='Execute original nibble expansion initialization at40bbac (enabled)')
    parser.add_argument('--flippers',action='store_true',help='Original left edges400/440 and right edges600/640')
    parser.add_argument('--auto-launch',action='store_true',help='Press original Enter for each ready launch-phase ball, at most once per200steps')
    parser.add_argument('--complete-game',action='store_true',help='Legal three-ball Enter route, ABC initials, then F1 after GameOver')
    parser.add_argument('--lamps',action='store_true',help='Run original lamp command consumer and raster routines every20ms')
    parser.add_argument('--launch-step', type=int, default=200,
                        help='Zero-based Enter-down tick; release follows one tick later')
    parser.add_argument('--exe', type=Path, default=EXE)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.complete_game:args.auto_launch=True
    if args.steps < 1 or args.launch_step < 0:
        parser.error('--steps must be positive; --launch-step must be nonnegative')
    output = (args.output or ROOT/'build/oracle'/f'{args.table}-full-tick').resolve()
    if not output.is_relative_to(ROOT / 'build'):
        parser.error('--output must be under build/: it contains original binary data')
    raw = args.exe.read_bytes()
    assert digest(raw) == BUILD_SHA, 'Unsupported Retail executable'
    profile=json.loads((ROOT/'analysis/table-profiles.json').read_text())['tables'][args.table]
    dat_sha=profile['dat_sha256'];initializer=int(profile['initializer'],0);descriptor=int(profile['returned_descriptor'],0)
    dat = (args.exe.parent / ('DAT/'+args.table.upper()+'.DAT')).read_bytes()
    assert digest(dat) == dat_sha, 'Unsupported table data'
    pe = pefile.PE(data=raw)
    image = bytearray(pe.get_memory_mapped_image())
    image.extend(bytes(0x100000 - len(image)))
    for section in pe.sections:
        if section.Name.rstrip(b'\0') == b'.bss':
            size = max(section.Misc_VirtualSize, section.SizeOfRawData)
            image[section.VirtualAddress:section.VirtualAddress + size] = bytes(size)
    machine = Uc(UC_ARCH_X86, UC_MODE_32)
    for address, size in [(0x400000, 0x100000), (OBJ, 0x400000),
                          (0x2000000, 0x10000), (STOP, 0x1000)]:
        machine.mem_map(address, size)
    machine.mem_write(0x400000, bytes(image))
    machine.mem_write(DAT, dat)
    machine.mem_write(0x4d0000,(args.exe.parent/'DAT/MAIN.DAT').read_bytes())
    tick, initializing = -1, True
    heap = 0x4e0000
    mode_writes, service_calls = [], []

    def put(address, value):
        machine.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def get(address):
        return struct.unpack('<I', machine.mem_read(address, 4))[0]

    def service(uc, address, size, data):
        # These two adapters are permitted only inside bounded initialization.
        assert initializing, f'Unexpected gameplay service {address:#x}, tick {tick}'
        nonlocal heap
        service_calls.append(hex(address))
        if address == 0x40f7e0:
            result = DAT
        else:
            result=heap;heap += (uc.reg_read(UC_X86_REG_EDX)+15)&~15
            assert heap<0x500000
        uc.reg_write(UC_X86_REG_EAX,result)
        sp = uc.reg_read(UC_X86_REG_ESP)
        uc.reg_write(UC_X86_REG_ESP, sp + 4)
        uc.reg_write(UC_X86_REG_EIP, get(sp))

    def mode_write(uc, access, address, size, value, data):
        mode_writes.append(dict(tick=tick, address=hex(address),
                                pc=hex(uc.reg_read(UC_X86_REG_EIP)), value=value))

    def invalid(uc, access, address, size, value, data):
        raise RuntimeError(f'Unmapped {address:#x}, pc {uc.reg_read(UC_X86_REG_EIP):#x}, tick {tick}')

    for address in (0x40f7e0, 0x40f740):
        machine.hook_add(UC_HOOK_CODE, service, begin=address, end=address)
    machine.hook_add(UC_HOOK_MEM_WRITE, mode_write, begin=0x46c6ac, end=0x46c6af)
    machine.hook_add(UC_HOOK_MEM_INVALID, invalid)

    def run(address, eax=0, edx=None, until=STOP):
        put(STACK, STOP)
        machine.reg_write(UC_X86_REG_ESP, STACK)
        machine.reg_write(UC_X86_REG_EAX, eax)
        if edx is not None:
            machine.reg_write(UC_X86_REG_EDX, edx)
        try:
            machine.emu_start(address, until, count=500000)
        except Exception:
            print('FAILED',tick,hex(machine.reg_read(UC_X86_REG_EIP)),list(machine.mem_read(machine.reg_read(UC_X86_REG_ESP),40)),flush=True)
            raise
        assert machine.reg_read(UC_X86_REG_EIP) == until, f'Instruction limit at {address:#x}'
        if until == STOP:
            assert machine.reg_read(UC_X86_REG_ESP) == STACK + 4, f'Unbalanced call {address:#x}'

    run(0x405a3a, until=0x405b90)  # Original shared service ABI.
    if args.display_lut:
        run(0x40bbac)  # Original 16-entry foreground/DMD nibble expansion.
    run(initializer, 0x46c67c, 0x46b748)  # Complete original Pirate initializer.
    put(0x46c644, descriptor)
    put(0x46c718,dict(demon=4,pirate=2,space=3)[args.table]) # Original menu40e7dc/loader405ce0, 1-based table IDs.
    run(0x404f09,until=0x404f62) # Original table-data/lamp/palette bindings.
    run(0x404ebf,1,until=0x404ee6) # Original selected-table highscore pointer.
    run(0x405057, until=0x405153)  # Original flipper parameters.
    for address, value in [(0x46c66c, 0x455780), (0x46c648, 0x455f80),
                           (0x46c638, 0x457f84), (0x46c640, 0x45d188),
                           (0x46c65c, 0x458788), (0x46c678, 0x45e454),
                           (0x46c67c, 0), (0x46c6ac, 0), (0x46c72c, OBJ + 0x7000),
                           (0x46c47c, OBJ + 0xa000), (0x46c488, OBJ + 0xa800), (0x46c730,0x4d0000)]:
        put(address, value)
    # Keep the original PE's canonical pool. Single-ball drain408d78 writes
    # 46c1b4 directly; relocating only this pointer table breaks later balls.
    assert [get(0x454b68+i*4) for i in range(8)] == [0x46c15c+i*100 for i in range(8)]
    put(0x46b760, get(get(descriptor)))  # This table's actual point-force list.
    for address in (0x46b764, 0x454b44, 0x46c600, 0x46c4a4, 0x46c604, 0x46c5f8):
        put(address, 0)
    put(0x46f214,OBJ+0x9000)
    # Headless original raster output: native SDL composites the decoded assets.
    put(0x46c724,0x4a0000);put(0x46c708,320);put(0x46c484,OBJ+0xc000)
    playfield_offset=get(0x46c48c)-DAT+1024
    assert 0<=playfield_offset<=len(dat)-320*600
    machine.mem_write(0x4a0000,dat[playfield_offset:playfield_offset+320*600])
    machine.mem_write(OBJ+0xc000,struct.pack('<HH',320,0)*600)
    run(0x451cbe,OBJ+0x9000,until=0x451cec) # originalCRTseedinit stopsbeforeGetCurrentThreadId
    if args.table!='pirate':run(0x40df1e,until=0x40df5f) # Original default-keymap branch.
    initializing = False
    for address, value in [(0x46c728,1),(0x46c734,0),(0x46c740,0),(0x46c744,0)]:
        put(address,value)
    run(0x40404c, 0, 0x3b)  # Original F1 down -> new one-player game.
    assert (get(0x46c67c), get(0x46c6ac), get(0x46c680), get(0x46c684)) == (1, 1, 1, 1)
    snapshots = {'human-image.bin': bytes(machine.mem_read(0x400000, 0x100000)),
                 'human-runtime.bin': bytes(machine.mem_read(OBJ, 0x10000)),
                 'human-dat.bin': bytes(machine.mem_read(DAT, len(dat)))}
    output.mkdir(parents=True, exist_ok=True)
    for name, data in snapshots.items():
        (output / name).write_bytes(data)

    input_events=[];last_launch=-10000;release_tick=-1
    text_index=0;next_text=0;restart_at=-1;restarted=False
    def ball_bytes():
        return bytes(machine.mem_read(get(0x454b68),100))
    def input_at_tick():
        nonlocal last_launch,release_tick,text_index,next_text,restart_at,restarted
        if args.complete_game:
            if get(0x46c6ac)==3 and get(0x46c61c)==6 and tick>=next_text and text_index<4:
                scan=(0x1e,0x30,0x2e,0x1c)[text_index]
                run(0x40404c,0,scan);run(0x40404c,1,scan)
                input_events.append(dict(tick=tick,action='key',scan=scan,down=True))
                text_index+=1;next_text=tick+20
            if get(0x46c6ac)==0 and not restarted:
                if restart_at<0:restart_at=tick+100
                if tick==restart_at:
                    run(0x40404c,0,0x3b);run(0x40404c,1,0x3b)
                    input_events.append(dict(tick=tick,action='new_game',down=True));restarted=True
        if args.flippers:
            # Original configurable scan codes; native SDL uses the proven action adapter.
            put(0x46c5dc,0x2a);put(0x46c5e0,0x36)
            if tick in (400,440,600,640):
                run(0x40404c,0 if tick in (400,600) else 1,0x2a if tick<600 else 0x36)
                if args.table!='pirate':input_events.append(dict(tick=tick,action='left'if tick<600 else'right',down=tick in (400,600)))
        launch=(tick==args.launch_step)
        if args.auto_launch:
            launch=tick>=args.launch_step and tick-last_launch>=200 and get(0x46c6ac)==1 and int.from_bytes(ball_bytes()[88:90],'little')==1
        if launch:
            run(0x40404c, 0, 0x1c)
            assert get(0x46c5fc) == 0xffffffff
            input_events.append(dict(tick=tick,action='enter',down=True));last_launch=tick;release_tick=tick+1
        if tick == release_tick:
            run(0x40404c, 1, 0x1c)
            input_events.append(dict(tick=tick,action='enter',down=False))

    watched={0x4071e0:'rng_update',0x44f4d0:'crt_rand',0x409154:'flipper_step',
             0x40950c:'scheduler',0x409588:'per_ball',0x43163c:'pirate200hz',
             0x435414:'pirate50hz_timers',0x407b88:'display50hz_dispatch',
             0x4308f0:'pirate_idle_display',0x4070bc:'nudge',0x409350:'camera'}
    if args.table!='pirate':
        callbacks=get(get(descriptor+4)+8)
        watched={a:n for a,n in watched.items() if not n.startswith('pirate')}
        watched[get(callbacks+0x30)]='table200hz'
        watched[get(callbacks+0x2c)]='table_per_ball'
        watched[get(callbacks+0x3c)]='pirate50hz_timers' # historical counter key; actual table callback
    counts=Counter()
    eligibility=Counter()
    def eligible_call(uc,address,size,data):
        if address==0x405311 and not get(0x46c6c0) and get(0x46c6ac)!=3:
            eligibility['scheduler']+=1
        if address==0x4053f8 and get(0x46c6ac) not in (0,3) and not get(0x46c6c0):
            eligibility['pirate50hz_timers']+=1
    for address in (0x405311,0x4053f8):
        machine.hook_add(UC_HOOK_CODE,eligible_call,begin=address,end=address)
    call_edges=Counter();pending_call=None;call_instructions={}
    disassembler=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    def call_edge(uc,address,size,data):
        nonlocal pending_call
        if pending_call is not None:
            call_edges[(pending_call,address)]+=1
        if address not in call_instructions:
            instruction=next(disassembler.disasm(bytes(uc.mem_read(address,size)),address),None)
            call_instructions[address]=instruction is not None and instruction.mnemonic=='call'
        pending_call=address if call_instructions[address] else None
    machine.hook_add(UC_HOOK_CODE,call_edge)
    def count_call(uc,address,size,data):
        counts[watched[address]]+=1
    for address in watched:
        machine.hook_add(UC_HOOK_CODE,count_call,begin=address,end=address)
    states = [list(ball_bytes())]
    globals_trace=[];lifecycle_trace=[];highscore_hashes=[];lamp_hashes=[]
    lamp_descriptors=[get(get(0x46b74c)+i*4) for i in range(get(0x46c6a4))]
    def lamps_sample():
        return digest(b''.join(bytes(machine.mem_read(address+8,2)) for address in lamp_descriptors))
    def lifecycle_sample():
        record=get(0x46b758)
        return [get(0x46c6ac),get(0x46c67c),get(0x46c680),get(0x46c684),
                int.from_bytes(machine.mem_read(record+14,2),'little'),
                int.from_bytes(machine.mem_read(record+16,2),'little'),
                get(0x46c61c),get(0x46c620),*machine.mem_read(record,6),get(0x46c60c)]
    def globals_sample():
        snapshot=dict(previous_ms=get(0x46c734),physics_accumulator=get(0x46c744),
                    frame_accumulator=get(0x46c740),frame_count=get(0x46c704),
                    crt_seed=get(OBJ+0x900c),rng_b4=get(0x46c6b4),rng_b8=get(0x46c6b8),
                    phase=get(0x46c6ac),dmd_state=get(0x46c68c),
                    field_46e554=int.from_bytes(machine.mem_read(0x46e554,2),'little'),
                    field_46e53a=int.from_bytes(machine.mem_read(0x46e53a,2),'little'),
                    dmd_sha256=digest(bytes(machine.mem_read(get(0x46c47c),1920))))
        if args.table!='pirate':snapshot['poses']=[get(a)&65535 for a in [0x46c786,0x46c76c,0x46c752]]
        return snapshot
    changes, previous_mode = [], get(0x46c6ac)
    for tick in range(args.steps):
        input_at_tick()
        run(0x405234, (tick + 1) * 5, until=0x405486)
        if args.lamps and (tick+1)%4==0:run(0x408da8)
        states.append(list(ball_bytes()))
        globals_trace.append(globals_sample())
        lifecycle_trace.append(lifecycle_sample());highscore_hashes.append(digest(bytes(machine.mem_read(get(0x46c498),50))))
        lamp_hashes.append(lamps_sample())
        mode = get(0x46c6ac)
        if mode != previous_mode:
            changes.append(dict(tick=tick + 1, before=previous_mode, after=mode))
            if args.auto_launch:print('phase',changes[-1],flush=True)
            previous_mode = mode
    first_counts=dict(counts);counts.clear()
    first_eligibility=dict(eligibility);eligibility.clear()
    first_edges=dict(call_edges);call_edges.clear()
    first_mode_writes = list(mode_writes)
    first_final_mode = get(0x46c6ac)
    first_inputs=list(input_events);input_events.clear();last_launch=-10000;release_tick=-1
    text_index=0;next_text=0;restart_at=-1;restarted=False
    machine.mem_write(0x400000, snapshots['human-image.bin'])
    machine.mem_write(OBJ, snapshots['human-runtime.bin'])
    machine.mem_write(DAT, snapshots['human-dat.bin'])
    machine.mem_write(0x2000000, bytes(0x10000))
    for tick in range(args.steps):
        input_at_tick()
        run(0x405234, (tick + 1) * 5, until=0x405486)
        if args.lamps and (tick+1)%4==0:run(0x408da8)
        assert list(ball_bytes()) == states[tick + 1], f'Replay differs at {tick}'
        assert globals_sample()==globals_trace[tick],f'Globals differ at {tick}'
        assert lifecycle_sample()==lifecycle_trace[tick],f'Lifecycle differs at {tick}'
        assert digest(bytes(machine.mem_read(get(0x46c498),50)))==highscore_hashes[tick],f'Highscore differs at {tick}'
        assert lamps_sample()==lamp_hashes[tick],f'Lamps differ at {tick}'
    assert get(0x46c6ac) == first_final_mode
    assert input_events==first_inputs
    assert dict(counts)==first_counts
    assert dict(call_edges)==first_edges
    assert dict(eligibility)==first_eligibility
    assert first_counts.get('scheduler',0)==first_eligibility.get('scheduler',0)
    assert first_counts.get('flipper_step',0)==args.steps
    assert first_counts.get('crt_rand',0)==args.steps*8
    assert first_counts.get('pirate50hz_timers',0)==first_eligibility.get('pirate50hz_timers',0)
    assert globals_trace[-1]['frame_count']==args.steps//4
    context_hashes = {name: digest(data) for name, data in snapshots.items()}
    report = dict(schema=1, build_sha256=BUILD_SHA, dat_sha256=dat_sha,
                  tick_count=args.steps, launch_step=args.launch_step,
                  initial_state=states[0], final_state=states[-1], states=states,
                  mode_changes=changes, mode_writes=first_mode_writes,
                  calls=first_counts,globals=globals_trace,
                  inputs=first_inputs,lifecycle=lifecycle_trace,highscore_sha256=highscore_hashes,lamp_sha256=lamp_hashes,
                  executed_call_edges=[dict(callsite=hex(a),target=hex(b),count=n)for(a,b),n in sorted(first_edges.items())],
                  deterministic_replay_globals=True,
                  rng=dict(thread_context='0x1009000',seed_offset=12,initial_seed=1,
                           formula='state=state*1103515245+12345 modulo2^32; return(state>>16)&32767',
                           function='0x44f4d0',initialization='0x451cbe..0x451cec'),
                  context_hashes=context_hashes, final_game_mode=first_final_mode,
                  deterministic_replay_all_ball_bytes=True, gameplay_stubs=[], errors=[])
    write_json(output / 'trace.json', report)
    metadata = {key: value for key, value in report.items()
                if key not in ('states', 'initial_state', 'final_state','globals','lifecycle','highscore_sha256','lamp_sha256')}
    metadata.update(initial_state=fields(states[0]), final_state=fields(states[-1]),
                    trace_sha256=digest((output / 'trace.json').read_bytes()),
                    initializer='40404c(EAX0,EDX3b)->408ae0',
                    input='Enter down/up via40404c(EAX0/1,EDX1c)',
                    original_step='405234(EAX=5*(tick+1)) stop405486: full200Hz+50Hz loops',
                    final_globals=globals_trace[-1],
                    flipper_inputs=args.flippers,
                    lamp_consumer=args.lamps,
                    display_lut='original40bbac; 16nibbles expanded to4preservationbytes',
                    wrapper_abi=dict(entry='0x405234',stop='0x405486',input='EAX absolute elapsed milliseconds',
                                     excluded_tail='405486..4054f8 FPU display interpolation and epilogue'),
                    initialization_service_adapters=service_calls,
                    limits=['Synthetic isolated frontend context; original code runs under Unicorn.',
                            'Final FPU display interpolation and actual hostdevice output excluded.',
                            'CRTdefaultseed1 and synthetic5ms clock; gameplay RNG executes originalinstructions.',
                            'DMDoutputbuffers isolated; native host scaling/monitor output not covered by original instruction execution.',
                            'No live desktop capture, multiball or full-rule coverage.'])
    write_json(output / 'summary.json', metadata)
    case='pirate-full-input' if args.flippers else 'pirate-full-tick'
    if args.steps == 1000 and args.launch_step == 200 and output == ROOT/'build/oracle'/case:
        write_json(ROOT / f'analysis/{case}-boundary.json', metadata)
    print(json.dumps(dict(status='PASS', steps=args.steps, mode_changes=changes,
                          deterministic=True, gameplay_stubs=0, output=str(output))))


if __name__ == '__main__':
    main()
