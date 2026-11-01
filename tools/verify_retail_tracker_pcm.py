#!/usr/bin/env python3
"""Run a bounded table tracker tick and mixer with SHA-pinned Retail code/data.

This initializes a synthetic mixer context and volume; it does not execute the
full game startup, DirectSound or SFX. 882 frames are an explicit comparison
window, not an assertion about original scheduler or hardware cadence. Private
PCM is written only to the selected build directory.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDX
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESP

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
EXE_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
TABLES = {
    'mean': ('1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f', 0x5c2d2, 4),
    'pirate': ('6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6', 0x51876, 34),
    'space': ('18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b', 0x53642, 32),
    'demon': ('0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d', 0x6ffb4, 25),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe', type=Path, default=GAME / 'SLAMTILT.EXE')
    p.add_argument('--table', choices=TABLES, default='pirate')
    p.add_argument('--dat', type=Path)
    p.add_argument('--order', type=int, help='Override the startup order in the selected bank')
    p.add_argument('--warm-order', type=int, help='Run one prior tracker tick before selecting the requested order')
    p.add_argument('--warm-ticks', type=int, default=1, help='Prior tracker/mixer ticks when --warm-order is set')
    p.add_argument('--warm-bank-offset', type=lambda v:int(v,0), help='Optional DAT bank for the warm tick')
    p.add_argument('--middle-order', type=int, help='Optional intermediate order after the warm tick')
    p.add_argument('--middle-bank-offset', type=lambda v:int(v,0), help='DAT bank for the intermediate order')
    p.add_argument('--middle-ticks', type=int, default=1, help='Tracker/mixer ticks in the intermediate order')
    p.add_argument('--scheduler-service', type=lambda v:int(v,0), choices=(0x84, 0x88),
                   help='Run Retail completion scheduler before each tracker tick after a base preemption')
    p.add_argument('--deferred-bank-offset', type=lambda v:int(v,0), help='Queue a lower-priority bank while service 88 is active')
    p.add_argument('--deferred-order', type=int, help='Order to queue for the lower-priority service')
    p.add_argument('--deferred-tick', type=int, default=1, help='Queue the lower service before this target tick')
    p.add_argument('--bank-offset', type=lambda v:int(v,0), help='Override the DAT bank offset')
    p.add_argument('--output', type=Path, default=ROOT / 'build/retail-tracker-pcm')
    p.add_argument('--ticks', type=int, default=1,
                   help='Adapted consecutive tracker/mixer windows; five is a bounded experiment')
    p.add_argument('--dynamic-voices', action='store_true', help='Update and link all four tracker voices on each manually clocked tick')
    p.add_argument('--allow-silent', action='store_true', help='Allow bounded cases with no active original samples')
    p.add_argument('--voice-mask', type=lambda v:int(v,0), default=15, help='Tracker channels to mix in the adapted oracle')
    p.add_argument('--voice-log', type=Path, help='Optional per-tick voice metadata; no sample data')
    p.add_argument('--tracker-log', type=Path, help='Optional per-tick tracker fields; no sample data')
    p.add_argument('--scheduler-log', type=Path, help='Optional per-tick scheduler and tracker control state')
    args = p.parse_args()
    assert 1 <= args.ticks <= 2048 and 0 <= args.voice_mask <= 15 and (args.dynamic_voices or args.ticks in (1, 5))
    assert args.warm_order is None or (0 <= args.warm_order < 128 and args.dynamic_voices)
    assert 1 <= args.warm_ticks <= 2048
    assert args.warm_bank_offset is None or args.warm_order is not None
    assert (args.middle_order is None and args.middle_bank_offset is None) or (
        args.warm_order is not None and args.middle_order is not None and
        args.middle_bank_offset is not None and 0 <= args.middle_order < 128 and 1 <= args.middle_ticks <= 64)
    assert args.scheduler_service is None or (args.warm_order is not None and args.middle_order is None)
    assert (args.deferred_bank_offset is None) == (args.deferred_order is None)
    assert args.deferred_order is None or (args.scheduler_service == 0x88 and 0 <= args.deferred_tick < args.ticks and 0 <= args.deferred_order < 128)
    dat_sha, bank_offset, order = TABLES[args.table]
    if args.order is not None: order = args.order
    if args.bank_offset is not None: bank_offset = args.bank_offset
    dat_path = args.dat or GAME / 'DAT' / (args.table.upper() + '.DAT')
    executable, dat = args.exe.read_bytes(), dat_path.read_bytes()
    assert sha(executable) == EXE_SHA and sha(dat) == dat_sha, 'unrecognized input'
    pe = pefile.PE(data=executable)
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    u.mem_map(0x400000, 0x100000)
    u.mem_write(0x400000, pe.get_memory_mapped_image())
    u.mem_map(0x1100000, 0x200000)
    u.mem_write(0x1100000, dat)
    u.mem_map(0x3000000, 0x60000)
    blocks = set()
    u.hook_add(UC_HOOK_BLOCK, lambda _u, address, size, _d: blocks.add((address, size)))

    def put(address, value):
        u.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def get(address):
        return struct.unpack('<I', u.mem_read(address, 4))[0]

    def run(address, eax=0, edx=0):
        put(0x3050000, 0x305fff0)
        for reg, value in ((UC_X86_REG_ESP, 0x3050000), (UC_X86_REG_EAX, eax),
                           (UC_X86_REG_EDX, edx), (UC_X86_REG_EBX, 0)):
            u.reg_write(reg, value)
        u.emu_start(address, 0x305fff0, count=10000000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x305fff0, hex(address)
        return u.reg_read(UC_X86_REG_EAX)

    # Reconstruct only the explicit state needed at the two routine boundaries.
    for address, size in ((0x467580, 4 * 0xac), (0x46b2d8, 6 * 32),
                          (0x46b060, 6 * 0x60)):
        u.mem_write(address, bytes(size))
    for i in range(4):
        put(0x467580 + i * 0xac, i)
    for address, value in ((0x467578, 0x1100000 + bank_offset), (0x46757c, 0x1100000),
                           (0x46c72c, 0x46b2a4), (0x46754c, 64), (0x467554, 1)):
        put(address, value)
    def link_voices(indices):
        for index, i in enumerate(indices):
            next_voice = 0x468858 + 0x24 * indices[index + 1] if index + 1 < len(indices) else 0
            put(0x468858 + 0x24 * i + 0x20, next_voice)
        put(0x468854, 0x468858 + 0x24 * indices[0] if indices else 0)

    def mixer_setup():
        run(0x44b5dc, 0x468854)
        for i in range(6):
            put(0x468858 + 0x24 * i, 0x46b060 + 0x60 * i)
            run(0x401838, i)
        indices = [i for i in range(4) if args.voice_mask & (1 << i) and get(0x468858 + 0x24 * i + 0x10)]
        link_voices(indices)
        for address, value in ((0x46eea4, 6), (0x46eeb8, 0x3010000), (0x46eebc, 44100),
                               (0x46ee98, 882), (0x46eeb0, 0x3002000), (0x46eeb4, 0x3004000),
                               (0x46eec8, 0x3006000), (0x46eea8, 16), (0x46eecc, 1),
                               (0x46ee9c, 1), (0x46eeac, 0), (0x46eec4, 0), (0x46ee90, 0)):
            put(address, value)
        run(0x44b640, 0x20000 // 6)

    def output_buffer():
        for address, value in ((0x3008000, 0x3009000), (0x3008004, 0),
                               (0x3008008, 882), (0x300800c, 0)):
            put(address, value)

    scheduler_warm_state = None
    if args.warm_order is not None:
        if args.warm_bank_offset is not None:
            put(0x467578, 0x1100000 + args.warm_bank_offset)
        run(0x44f138, args.warm_order)
        for warm_tick in range(args.warm_ticks):
            run(0x44eaf8)
            if warm_tick == 0:
                mixer_setup()
            else:
                for i in range(4): run(0x401838, i)
                link_voices([i for i in range(4) if args.voice_mask & (1 << i) and get(0x468858 + 0x24 * i + 0x10)])
            output_buffer()
            assert run(0x44b560, 0x3008000, 0x468854) == 1
        if args.scheduler_service is not None:
            # 40634c snapshots the prior tracker before installing an overlay.
            scheduler_warm_state = {'live_order': get(0x467568), 'live_row': get(0x467564),
                                    'saved_order': get(0x46ef40), 'saved_row': get(0x46ef3c),
                                    'saved_speed': get(0x46ef30)}
            run(0x44ddfc, 0x46b7e0)
        if args.middle_order is not None:
            put(0x467578, 0x1100000 + args.middle_bank_offset)
            run(0x44f138, args.middle_order)
            for _ in range(args.middle_ticks):
                run(0x44eaf8)
                for i in range(4): run(0x401838, i)
                link_voices([i for i in range(4) if args.voice_mask & (1 << i) and get(0x468858 + 0x24 * i + 0x10)])
                output_buffer()
                assert run(0x44b560, 0x3008000, 0x468854) == 1
    put(0x467578, 0x1100000 + bank_offset)
    run(0x44f138, order)
    if args.scheduler_service is not None:
        for address in (0x454a50, 0x454a54, 0x454a58, 0x454a5c, 0x454a60): put(address, 0)
        put(0x454a6c, 2 if args.scheduler_service == 0x88 else 1)
        if args.deferred_order is not None and args.deferred_tick == 0:
            put(0x46c644, 0x3003000)
            put(0x300300c, 0x3003100)
            put(0x3003100, get(0x46757c))
            put(0x3003104, 0x3003200)
            put(0x3003200, 0x1100000 + args.deferred_bank_offset)
            run(0x406240, args.deferred_order, 0)
        run(0x4062f0)
    run(0x44eaf8)
    channels = [list(struct.unpack('<8I', u.mem_read(0x46b2d8 + i * 32, 32)))
                for i in range(4)]
    active = [i for i, row in enumerate(channels) if row[0] == 1]
    assert (active or args.dynamic_voices) and all(row[0] in (0, 1) for row in channels)
    if args.table == 'pirate' and args.order is None and args.bank_offset is None and args.warm_order is None:
        assert active == [1, 2, 3]
        assert [(row[5], row[6]) for row in channels[1:]] == [(190, 64), (214, 64), (214, 64)]

    if args.warm_order is None:
        mixer_setup()
    else:
        for i in range(4):
            run(0x401838, i)
        link_voices([i for i in range(4) if args.voice_mask & (1 << i) and get(0x468858 + 0x24 * i + 0x10)])
    output_buffer()
    if args.deferred_order is not None:
        # Synthetic table descriptor: the real scheduler resolves the pending
        # bank through 46c644 -> descriptor+0xc -> bank pointer array.
        put(0x46c644, 0x3003000)
        put(0x300300c, 0x3003100)
        put(0x3003100, get(0x46757c))
        put(0x3003104, 0x3003200)
        put(0x3003200, 0x1100000 + args.deferred_bank_offset)
    pcm = bytearray(); voice_log = []; tracker_log = []; scheduler_log = []
    for tick in range(args.ticks):
        if tick:
            if args.deferred_order is not None and tick == args.deferred_tick:
                run(0x406240, args.deferred_order, 0)
            # Manually clock the sequencer at an assumed 50 Hz. The original
            # scheduler and changing voice-list setup are not reproduced here.
            if args.scheduler_service is not None:
                run(0x4062f0)
            run(0x44eaf8)
            if args.dynamic_voices:
                for i in range(4): run(0x401838, i)
                linked = [i for i in range(4) if args.voice_mask & (1 << i) and get(0x468858 + 0x24 * i + 0x10)]
                for index, i in enumerate(linked):
                    put(0x468858 + 0x24 * i + 0x20,
                        0x468858 + 0x24 * linked[index + 1] if index + 1 < len(linked) else 0)
                put(0x468854, 0x468858 + 0x24 * linked[0] if linked else 0)
            for address, value in ((0x3008000, 0x3009000), (0x3008004, 0),
                                   (0x3008008, 882), (0x300800c, 0)):
                put(address, value)
        if args.voice_log:
            voice_log.append([[get(0x468858 + 0x24 * i + off) for off in (0,4,8,12,16,20)] +
                              [get(0x46b060 + 0x60 * i + off) for off in (0,4,8,12)] for i in range(4)])
        if args.tracker_log:
            tracker_log.append([[get(0x467580 + 0xac * i + off) for off in
                                 (4, 8, 12, 16, 24, 28, 32, 36, 40, 0x9c, 0xa0, 0xa4, 0xa8)] for i in range(4)])
        if args.scheduler_log:
            scheduler_log.append({'tick': tick, 'speed': get(0x467558), 'tick_in_row': get(0x46755c),
                                  'row': get(0x467564), 'order': get(0x467568), 'services': get(0x454a6c),
                                  'pending_upper': get(0x454a58), 'end_marker': get(0x454a5c)})
        assert run(0x44b560, 0x3008000, 0x468854) == 1
        pcm.extend(u.mem_read(0x3009000, 882 * 4))
    pcm = bytes(pcm)
    samples = struct.unpack(f'<{1764 * args.ticks}h', pcm)
    assert samples[::2] == samples[1::2] and (args.allow_silent or any(samples))
    flags = [get(a) for a in (0x46eeac, 0x46eec4, 0x46ee90)]
    assert flags in ([0, 1, 1], [1, 1, 1]), flags
    # Match every executed block to the original authenticated PE, not just the
    # copied in-memory image. No external calls, patched instructions or hooks.
    for address, size in blocks:
        assert 0x401000 <= address and address + size <= 0x454000, hex(address)
        offset = pe.get_offset_from_rva(address - 0x400000)
        assert bytes(u.mem_read(address, size)) == executable[offset:offset + size]
    report = {'status': 'VERIFIED_BOUNDED', 'scope': __doc__,
              'exe_sha256': EXE_SHA, 'dat_sha256': dat_sha, 'table': args.table,
              'bank': 0 if args.bank_offset is None else None,
              'bank_offset': hex(bank_offset), 'order': order, 'warm_order': args.warm_order,
              'warm_ticks': args.warm_ticks if args.warm_order is not None else 0,
              'warm_bank_offset': hex(args.warm_bank_offset) if args.warm_bank_offset is not None else None,
              'middle_order': args.middle_order,
              'middle_bank_offset': hex(args.middle_bank_offset) if args.middle_bank_offset is not None else None,
              'middle_ticks': args.middle_ticks if args.middle_order is not None else 0,
              'scheduler_service': hex(args.scheduler_service) if args.scheduler_service is not None else None,
              'deferred_order': args.deferred_order, 'deferred_tick': args.deferred_tick if args.deferred_order is not None else None,
              'scheduler_warm_state': scheduler_warm_state,
              'tracker_ticks': args.ticks, 'voice_mask': args.voice_mask,
              'original_routines': ['0x44f138', '0x44eaf8', '0x401838',
                                    '0x44b5dc', '0x44b640', '0x44b560'],
              'executed_original_blocks': len(blocks), 'channels': channels,
              'sample_rate': 44100, 'frames': 882 * args.ticks, 'volume_setting': 64,
              'voice_gain_factor': 0x20000 // 6, 'master_gain': 65536,
              'mono_left_right_identical': True, 'buffer_flags_mono_left_right': flags,
              'min_sample': min(samples), 'max_sample': max(samples),
              'nonzero_samples': sum(v != 0 for v in samples), 'pcm_sha256': sha(pcm),
              'adaptations': ['manual tracker state and four channel indices',
                              'optional prior and intermediate tracker/mixer ticks',
                              'optional 4062f0 scheduler with synthetic service state',
                              'explicit DAT and bank pointers', 'music volume 64',
                              'manual voice descriptor pointers and active-voice links',
                              'six-voice LUT and master 65536',
                              f'signed 16-bit stereo output, 44100 Hz, {882 * args.ticks} frames',
                              'manual 50 Hz sequencer cadence and '+('four linked voices updated each tick' if args.dynamic_voices else 'fixed voice links'),
                              'silent SFX; no DirectSound or game startup']}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / f'{args.table}-first-tick.s16le').write_bytes(pcm)
    (args.output / f'{args.table}-report.json').write_text(json.dumps(report, indent=2) + '\n')
    if args.voice_log:
        args.voice_log.parent.mkdir(parents=True,exist_ok=True)
        args.voice_log.write_text(json.dumps(voice_log)+'\n')
    if args.tracker_log:
        args.tracker_log.parent.mkdir(parents=True,exist_ok=True)
        args.tracker_log.write_text(json.dumps(tracker_log)+'\n')
    if args.scheduler_log:
        args.scheduler_log.parent.mkdir(parents=True,exist_ok=True)
        args.scheduler_log.write_text(json.dumps(scheduler_log)+'\n')
    print(f"PASS: {args.table} first tracker tick, {len(blocks)} original blocks, "
          f"{report['min_sample']}..{report['max_sample']}; {report['pcm_sha256']}")


if __name__ == '__main__':
    main()
