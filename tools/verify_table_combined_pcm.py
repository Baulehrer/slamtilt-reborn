#!/usr/bin/env python3
"""Compare four Retail music starts plus two original-data SFX, synthetically.

The tracker is manually clocked and two one-shot voices start simultaneously;
this is not a recorded event, full-game scheduling, or device-output proof.
No original sample or PCM bytes are included in the report.
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_BLOCK
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_ESP, UC_X86_REG_EIP
from extract_mean_stim import extract
from verify_retail_final_mix import original_mix
from verify_retail_tracker_pcm import ROOT, GAME, TABLES, EXE_SHA


def digest(data): return hashlib.sha256(data).hexdigest()


def original_effects(exe, dat, specs, frames):
    pe = pefile.PE(data=exe)
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    u.mem_map(0x400000, 0x100000); u.mem_write(0x400000, pe.get_memory_mapped_image())
    u.mem_map(0x3000000, 0x90000)
    blocks = set()
    u.hook_add(UC_HOOK_BLOCK, lambda _u, addr, size, _: blocks.add((addr, size)))
    def put(addr, value): u.mem_write(addr, struct.pack('<I', value & 0xffffffff))
    def run(addr, eax=0, ebx=0, esi=0, edi=0):
        put(0x300f000, 0x308fff0)
        for reg, value in ((UC_X86_REG_ESP, 0x300f000), (UC_X86_REG_EAX, eax),
                           (UC_X86_REG_EBX, ebx), (UC_X86_REG_ESI, esi), (UC_X86_REG_EDI, edi)):
            u.reg_write(reg, value)
        u.emu_start(addr, 0x308fff0, count=2000000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x308fff0
    put(0x46eeb8, 0x3010000); run(0x44b640, 0x20000//6)
    for off, value in ((0, 0x3010000), (4, 44100), (8, 65536)): put(0x3003000+off, value)
    for i, (offset, length) in enumerate(specs):
        assert 0 < length <= 0x1f000 and offset + length <= len(dat)
        sample, voice, entry = 0x3040000+i*0x20000, 0x3001000+i*0x20, 0x3002000+i*8
        u.mem_write(sample, dat[offset:offset+length]); put(entry, sample); put(entry+4, length)
        for delta, value in ((0, entry), (4, 0), (8, 0), (12, 64<<10), (16, 0x361f0f//226), (20, 0)):
            put(voice+delta, value)
    u.mem_write(0x3030000, bytes(frames*2))
    for i in range(2): run(0x44cc00, frames, 0x3030000, 0x3001000+i*0x20, 0x3003000)
    for addr, size in blocks:
        off = pe.get_offset_from_rva(addr-0x400000)
        assert bytes(u.mem_read(addr, size)) == exe[off:off+size]
    return struct.unpack(f'<{frames}h', u.mem_read(0x3030000, frames*2)), len(blocks)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True); p.add_argument('--library', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); a.work.mkdir(parents=True, exist_ok=True)
    exe = (GAME/'SLAMTILT.EXE').read_bytes(); assert digest(exe) == EXE_SHA
    env = dict(os.environ, LD_LIBRARY_PATH=str(a.library.absolute().parent))
    assert str(a.library.absolute()) in subprocess.check_output(['ldd', str(a.native.resolve())], env=env, text=True)
    frames = 2646; rows = []
    for table, (dat_sha, offset, order) in TABLES.items():
        dat_path = GAME/'DAT'/f'{table.upper()}.DAT'; dat = dat_path.read_bytes(); assert digest(dat) == dat_sha
        specs = []
        for sample in range(2):
            header = struct.unpack_from('>I', dat, 4*sample)[0]
            length = struct.unpack_from('>H', dat, header)[0] * 2
            specs.append((header+8, length))
        music_work = a.work/table
        subprocess.run([sys.executable, str(ROOT/'tools/verify_retail_tracker_pcm.py'), '--table', table,
                        '--ticks', '3', '--dynamic-voices', '--output', str(music_work)], check=True, stdout=subprocess.DEVNULL)
        music_raw = (music_work/f'{table}-first-tick.s16le').read_bytes()
        music = struct.unpack(f'<{frames*2}h', music_raw); assert music[::2] == music[1::2]
        sfx, sfx_blocks = original_effects(exe, dat, specs, frames)
        inputs = [(sample, m, m) for sample, m in zip(sfx, music[::2])]
        assert all(-32768 <= s+m <= 32767 for s, m, _ in inputs), 'synthetic case overflows'
        mixed, mix_blocks = original_mix(exe, inputs)
        original = struct.pack(f'<{frames*2}h', *(v for pair in mixed for v in pair))
        stim, _ = extract(dat, 0, (offset,)); stim_path = music_work/f'{table}.stim'; stim_path.write_bytes(stim)
        base = [str(a.native.resolve()), str(stim_path), str(dat_path), str(order),
                *(str(x) for spec in specs for x in spec), str(frames)]
        for chunk in (137, 882, 2646):
            native = subprocess.check_output(base+[str(chunk)], env=env)
            assert native == original, (table, chunk, 'original/native combined PCM differs')
        rows.append({'table': table, 'bank_offset': hex(offset), 'order': order, 'frames': frames,
                     'sfx_samples': [{'index': i+1, 'data_offset': spec[0], 'length': spec[1]} for i, spec in enumerate(specs)],
                     'chunks': [137, 882, 2646], 'pcm_sha256': digest(original),
                     'original_sfx_blocks': sfx_blocks, 'original_final_mix_blocks': mix_blocks})
        print(table, 'EXACT', flush=True)
    report = {'status': 'VERIFIED_BOUNDED', 'scope': __doc__, 'exe_sha256': EXE_SHA,
              'dat_sha256': {table: data[0] for table, data in TABLES.items()},
              'native_sha256': digest(a.native.read_bytes()), 'library_sha256': digest(a.library.read_bytes()), 'cases': rows}
    a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: four tables, tracker plus two SFX, three chunk sizes')


if __name__ == '__main__': main()
