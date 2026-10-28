#!/usr/bin/env python3
"""Original Retail Pirate F1/Enter trajectory; no gameplay service substitutions.

Requires the developer pefile/Unicorn environment. Original data and complete
memory snapshots stay under build/. This is a bounded 5-ms physics oracle;
outer 20-ms rules/display ticks, RNG, nudge and camera remain excluded.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile
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
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--launch-step', type=int, default=200,
                        help='Zero-based Enter-down tick; release follows one tick later')
    parser.add_argument('--exe', type=Path, default=EXE)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/oracle/pirate-human')
    args = parser.parse_args()
    if args.steps < 1 or args.launch_step < 0:
        parser.error('--steps must be positive; --launch-step must be nonnegative')
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'build'):
        parser.error('--output must be under build/: it contains original binary data')
    raw = args.exe.read_bytes()
    assert digest(raw) == BUILD_SHA, 'Unsupported Retail executable'
    dat = (args.exe.parent / 'DAT/PIRATE.DAT').read_bytes()
    assert digest(dat) == DAT_SHA, 'Unsupported Pirate data'
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
    tick, initializing = -1, True
    mode_writes, service_calls = [], []

    def put(address, value):
        machine.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def get(address):
        return struct.unpack('<I', machine.mem_read(address, 4))[0]

    def service(uc, address, size, data):
        # These two adapters are permitted only inside bounded initialization.
        assert initializing, f'Unexpected gameplay service {address:#x}, tick {tick}'
        service_calls.append(hex(address))
        uc.reg_write(UC_X86_REG_EAX, DAT if address == 0x40f7e0 else OBJ + 0x8000)
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
        machine.emu_start(address, until, count=500000)
        assert machine.reg_read(UC_X86_REG_EIP) == until, f'Instruction limit at {address:#x}'
        if until == STOP:
            assert machine.reg_read(UC_X86_REG_ESP) == STACK + 4, f'Unbalanced call {address:#x}'

    run(0x405a3a, until=0x405b90)  # Original shared service ABI.
    run(0x42b390, 0x46c67c, 0x46b748, 0x42b675)  # Pirate geometry/callbacks.
    put(0x46c644, 0x465958)
    run(0x405057, until=0x405153)  # Original flipper parameters.
    for address, value in [(0x46c66c, 0x455780), (0x46c648, 0x455f80),
                           (0x46c638, 0x457f84), (0x46c640, 0x45d188),
                           (0x46c65c, 0x458788), (0x46c678, 0x45e454),
                           (0x46c67c, 0), (0x46c6ac, 0), (0x46c72c, OBJ + 0x7000)]:
        put(address, value)
    for index in range(8):
        put(0x454b68 + index * 4, OBJ + index * 100)
    put(0x46b760, get(get(0x465958)))  # This table's actual point-force list.
    for address in (0x46b764, 0x454b44, 0x46c600, 0x46c4a4, 0x46c604, 0x46c5f8):
        put(address, 0)
    initializing = False
    run(0x40404c, 0, 0x3b)  # Original F1 down -> new one-player game.
    assert (get(0x46c67c), get(0x46c6ac), get(0x46c680), get(0x46c684)) == (1, 1, 1, 1)
    snapshots = {'human-image.bin': bytes(machine.mem_read(0x400000, 0x100000)),
                 'human-runtime.bin': bytes(machine.mem_read(OBJ, 0x10000)),
                 'human-dat.bin': bytes(machine.mem_read(DAT, len(dat)))}
    output.mkdir(parents=True, exist_ok=True)
    for name, data in snapshots.items():
        (output / name).write_bytes(data)

    def input_at_tick():
        if tick == args.launch_step:
            run(0x40404c, 0, 0x1c)
            assert get(0x46c5fc) == 0xffffffff
        if tick == args.launch_step + 1:
            run(0x40404c, 1, 0x1c)

    states = [list(machine.mem_read(OBJ, 100))]
    changes, previous_mode = [], get(0x46c6ac)
    for tick in range(args.steps):
        input_at_tick()
        run(0x409154)
        run(0x40950c)
        states.append(list(machine.mem_read(OBJ, 100)))
        mode = get(0x46c6ac)
        if mode != previous_mode:
            changes.append(dict(tick=tick + 1, before=previous_mode, after=mode))
            previous_mode = mode
    first_mode_writes = list(mode_writes)
    first_final_mode = get(0x46c6ac)
    machine.mem_write(0x400000, snapshots['human-image.bin'])
    machine.mem_write(OBJ, snapshots['human-runtime.bin'])
    machine.mem_write(DAT, snapshots['human-dat.bin'])
    machine.mem_write(0x2000000, bytes(0x10000))
    for tick in range(args.steps):
        input_at_tick()
        run(0x409154)
        run(0x40950c)
        assert list(machine.mem_read(OBJ, 100)) == states[tick + 1], f'Replay differs at {tick}'
    assert get(0x46c6ac) == first_final_mode
    context_hashes = {name: digest(data) for name, data in snapshots.items()}
    report = dict(schema=1, build_sha256=BUILD_SHA, dat_sha256=DAT_SHA,
                  tick_count=args.steps, launch_step=args.launch_step,
                  initial_state=states[0], final_state=states[-1], states=states,
                  mode_changes=changes, mode_writes=first_mode_writes,
                  context_hashes=context_hashes, final_game_mode=first_final_mode,
                  deterministic_replay_all_ball_bytes=True, gameplay_stubs=[], errors=[])
    write_json(output / 'trace.json', report)
    metadata = {key: value for key, value in report.items()
                if key not in ('states', 'initial_state', 'final_state')}
    metadata.update(initial_state=fields(states[0]), final_state=fields(states[-1]),
                    trace_sha256=digest((output / 'trace.json').read_bytes()),
                    initializer='40404c(EAX0,EDX3b)->408ae0',
                    input='Enter down/up via40404c(EAX0/1,EDX1c)',
                    original_step='409154 poses ->40950c scheduler/43163c/409588',
                    initialization_service_adapters=service_calls,
                    limits=['Synthetic isolated frontend context; original code runs under Unicorn.',
                            'Outer20ms rule/display ticks, RNG, nudge, camera excluded.',
                            'No live desktop capture, multiball or full-rule coverage.'])
    write_json(output / 'summary.json', metadata)
    if args.steps == 1000 and args.launch_step == 200:
        write_json(ROOT / 'analysis/traces/pirate-human-1000.json', metadata)
    print(json.dumps(dict(status='PASS', steps=args.steps, mode_changes=changes,
                          deterministic=True, gameplay_stubs=0, output=str(output))))


if __name__ == '__main__':
    main()
