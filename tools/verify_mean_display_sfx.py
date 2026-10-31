#!/usr/bin/env python3
"""Compare Mean's two display-callback sound sequences against both binaries.

The original table consumer is executed by verify_mean_retail_sfx_sequences.
Callback code/table bindings and Demo/Retail descriptor equivalence are checked
in the pinned executables. This does not establish a natural gameplay route or
device timing; queue service is observed at the boundary.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EIP, UC_X86_REG_ESP
from verify_mean_sample_pcm_original import DEMO_SHA
from verify_retail_tracker_pcm import EXE_SHA, GAME

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    builds = json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds']
    demo = (ROOT / next(x['path'] for x in builds if x['sha256'] == DEMO_SHA)).read_bytes()
    retail = (GAME/'SLAMTILT.EXE').read_bytes()
    assert digest(demo) == DEMO_SHA and digest(retail) == EXE_SHA
    images = [pefile.PE(data=x).get_memory_mapped_image() for x in (demo, retail)]
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    pairs = ((0x4133d4, 0x41fe14, 0), (0x413518, 0x41ff58, 0),
             (0x4131cc, 0x41fc0c, 1), (0x4132d4, 0x41fd14, 1),
             (0x412fa8, 0x41f9e8, 2), (0x411824, 0x41e264, 3),
             (0x41041c, 0x41ce5c, 4), (0x410158, 0x41cb98, 5))
    demo_tables = (0x438074, 0x4380a8, 0x4380dc, 0x438110, 0x438144, 0x438158)
    retail_tables = (0x464128, 0x46415c, 0x464190, 0x4641c4, 0x4641f8, 0x46420c)
    for old, new, group in pairs:
        for image, entry, table, consumer in ((images[0], old, demo_tables[group], 0x40f834),
                                               (images[1], new, retail_tables[group], 0x41c274)):
            code = list(decoder.disasm(image[entry-0x400000:entry-0x400000+65], entry))
            assert any(i.mnemonic == 'mov' and i.op_str == f'eax, {hex(table)}' for i in code)
            assert any(i.mnemonic == 'call' and i.op_str == hex(consumer) for i in code)
    for demo_table, retail_table in zip(demo_tables, retail_tables):
        for i in range(4):
            demo_row = struct.unpack_from('<I', images[0], demo_table-0x400000+16*i)[0]
            retail_row = struct.unpack_from('<I', images[1], retail_table-0x400000+16*i)[0]
            if demo_row == 0xffff or retail_row == 0xffff:
                assert demo_row == retail_row == 0xffff
                break
            demo_row = struct.unpack_from('<4I', images[0], demo_table-0x400000+16*i)
            retail_row = struct.unpack_from('<4I', images[1], retail_table-0x400000+16*i)
            assert demo_row[0] == retail_row[0] and demo_row[2:] == retail_row[2:]
            assert demo_row[1] + 0x2c0b4 == retail_row[1]
            assert struct.unpack_from('<5I', images[0], demo_row[1]-0x400000) == \
                   struct.unpack_from('<5I', images[1], retail_row[1]-0x400000)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    seq_path = args.output.parent/'mean-display-sfx-original-sequences.json'
    subprocess.run([sys.executable, str(ROOT/'tools/verify_mean_retail_sfx_sequences.py'),
                    '--output', str(seq_path)], check=True)
    original = json.loads(seq_path.read_text())
    sequences = original['cases']
    actual = json.loads(subprocess.check_output([str(args.native.resolve())]))
    expected = []
    for callback, _, group in pairs:
        for row in sequences[group]['events']:
            expected.append({'callback':callback, 'tick':row['tick'], 'service':0x5c,
                'field_1c':-1, 'field_20':256,
                'descriptor':int(row['descriptor'],16)-0x2c0b4,
                'period':row['period'], 'volume':row['volume']})
    assert actual == expected
    interrupted = json.loads(subprocess.check_output([str(args.native.resolve()), '--interrupt']))
    expected_interrupted = [{'tick':e['tick'], 'descriptor':int(e['descriptor'],16)-0x2c0b4,
                             'period':e['period'], 'volume':e['volume']}
                            for e in original['interleaved_cursor_events']]
    assert interrupted == expected_interrupted
    # The table mutates an already queued descriptor on its second request.
    # Run the actual Demo queue and consumer rather than assuming copy semantics.
    dat = (GAME/'DAT/MEAN.DAT').read_bytes()
    assert digest(dat) == '1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f'
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    for address, size in ((0x400000,0x100000),(0x1100000,0x200000),(0x3000000,0x10000)):
        u.mem_map(address, size)
    u.mem_write(0x400000, images[0])
    u.mem_write(0x1100000, dat)
    blocks = set()
    u.hook_add(UC_HOOK_BLOCK, lambda _u, address, size, _d: blocks.add((address,size)))
    def put(address, value):
        u.mem_write(address, struct.pack('<I', value & 0xffffffff))
    def get(address):
        return struct.unpack('<I', u.mem_read(address, 4))[0]
    def run(address, eax=0):
        put(0x300f000, 0x300fff0)
        u.reg_write(UC_X86_REG_ESP, 0x300f000)
        u.reg_write(UC_X86_REG_EAX, eax)
        u.emu_start(address, 0x300fff0, count=20000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x300fff0
    for address, value in ((0x43e828,0x43d2a4), (0x43d3a0,10),
                           (0x43941c,0x1100000), (0x43f0d0,0x3001000),
                           (0x300105c,0x405c60), (0x43d2d4,0),
                           (0x43d374,0), (0x43d394,0)):
        put(address, value)
    for tick in (0, 16, 20):
        put(0x43f02c, tick)
        run(0x40f834, 0x438074)
    assert get(0x43d2d4) == 0x437e10
    run(0x401760)
    voice = [get(0x43d2d8 + 4*32 + i*4) for i in range(8)]
    assert voice == [1,0x1100000+0x38ef0,8948,0,0,428,64,256]
    pe = pefile.PE(data=demo)
    for address, size in blocks:
        offset = pe.get_offset_from_rva(address-0x400000)
        assert bytes(u.mem_read(address,size)) == demo[offset:offset+size]
    report = {'status':'VERIFIED_BOUNDED', 'scope':__doc__, 'demo_sha256':DEMO_SHA,
              'retail_sha256':EXE_SHA, 'native_probe_sha256':digest(args.native.read_bytes()),
              'events':actual, 'interleaved_cursor_events':interrupted,
              'queued_duplicate_final_voice':voice,
              'demo_callbacks':[hex(x[0]) for x in pairs],
              'retail_callbacks':[hex(x[1]) for x in pairs]}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: eight Demo/Retail callbacks, six original sound tables and native requests')


if __name__ == '__main__':
    main()
