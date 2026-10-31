#!/usr/bin/env python3
"""Verify Retail startup/reset music fields using bounded original x86 execution.

Requires private prepared original contexts and a SHA-pinned Windows Retail EXE.
This proves configuration and request fields, not audible playback or sequencing.
"""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_EIP

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
BUILD_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
TABLES = {
    'pirate': ('pirate-full-tick', '6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6', 34),
    'space': ('space-full-game', '18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b', 32),
    'demon': ('demon-full-game', '0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d', 25),
}


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'build/gameplay-verification/retail-original-music-start.json')
    parser.add_argument('--frontend', action='store_true', help='Compare actual SDL startup requests for Retail, DAT-only, and available Amiga imports')
    parser.add_argument('--native-dir', type=Path, default=ROOT/'build/native')
    args = parser.parse_args()
    exe = EXE.read_bytes()
    if digest(exe) != BUILD_SHA:
        raise ValueError('Unsupported original executable')
    pe = pefile.PE(data=exe).get_memory_mapped_image()
    rows = []
    for table, (context_name, dat_sha, expected_order) in TABLES.items():
        context = ROOT/'build/oracle'/context_name
        summary = json.loads((context/'summary.json').read_text())
        image = (context/'human-image.bin').read_bytes()
        runtime = (context/'human-runtime.bin').read_bytes()
        dat = (context/'human-dat.bin').read_bytes()
        assert summary['build_sha256'] == BUILD_SHA
        assert digest(dat) == summary['dat_sha256'] == dat_sha
        assert digest(image) == summary['context_hashes']['human-image.bin']
        assert digest(runtime) == summary['context_hashes']['human-runtime.bin']
        case = {'table': table, 'image_sha256': digest(image), 'runtime_sha256': digest(runtime),
                'dat_sha256': dat_sha, 'runs': []}
        for start, end in ((0x404f56, 0x404f82), (0x40841c, 0x408455)):
            offset, size = start - 0x400000, end - start
            assert image[offset:offset+size] == pe[offset:offset+size], hex(start)
            u = Uc(UC_ARCH_X86, UC_MODE_32)
            u.mem_map(0x400000, 0x100000)
            u.mem_write(0x400000, image)
            u.mem_map(0x1000000, 0x10000)
            u.mem_write(0x1000000, runtime)
            get = lambda address: int.from_bytes(u.mem_read(address, 4), 'little')
            descriptor = get(0x46c644)
            config = get(descriptor+0xc)
            assert (get(config+8), get(config+0xc)) == (0, expected_order)
            # Set a sentinel so the check demonstrates writes rather than retained state.
            for addr in (0x454a64, 0x454a68, 0x454a3c, 0x454a38):
                u.mem_write(addr, (0xdeadbeef).to_bytes(4, 'little'))
            u.reg_write(UC_X86_REG_EAX, descriptor)
            u.reg_write(UC_X86_REG_EDX, descriptor)
            u.emu_start(start, end, count=100)
            assert u.reg_read(UC_X86_REG_EIP) == end
            assert (get(0x454a68), get(0x454a64)) == (0, expected_order)
            if start == 0x40841c:
                assert (get(0x454a38), get(0x454a3c)) == (0, expected_order)
            case['runs'].append({'start': hex(start), 'end_exclusive': hex(end),
                'descriptor': hex(descriptor), 'config': hex(config),
                'bank': get(0x454a68), 'order': get(0x454a64),
                'verified_exe_code_sha256': digest(image[offset:offset+size])})
        rows.append(case)
    frontend = []
    if args.frontend:
        game_dat = EXE.parent/'DAT'
        env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        with tempfile.TemporaryDirectory(prefix='slam-music-start-') as temp:
            temp = Path(temp)
            env['XDG_DATA_HOME'] = str(temp/'xdg')
            for table, (context_name, dat_sha, expected_order) in TABLES.items():
                importer = args.native_dir/f'slam{table}-import'
                imported = temp/f'{table}-dat-only'
                subprocess.run([str(importer), str(game_dat), str(imported)], env=env,
                               capture_output=True, text=True, check=True, timeout=90)
                amiga = ROOT/f'build/amiga-read-verified-data/{table}'
                paths = [('retail-context', ROOT/'build/oracle'/context_name, game_dat),
                         ('dat-only', imported/f'{table}-prepared', imported)]
                if (amiga/f'{table}-prepared/human-image.bin').is_file() and (amiga/f'{table.upper()}.DAT').is_file():
                    paths.append(('amiga-adapter', amiga/f'{table}-prepared', amiga))
                for profile, prepared, data in paths:
                    audio = temp/f'{table}-{profile}-audio.json'
                    exe = args.native_dir/('slamview' if table == 'pirate' else 'slamslice')
                    dat_path = data/f'{table.upper()}.DAT'
                    if table == 'pirate':
                        cmd = [str(exe), str(dat_path), '--pirate-play', str(prepared), '--frames', '1', '--audio-trace', str(audio)]
                    else:
                        cmd = [str(exe), table, str(prepared), str(dat_path), '--frames', '1', '--presentation', '--audio', '--audio-trace', str(audio)]
                    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=90)
                    assert result.returncode == 0, (table, profile, result.stdout, result.stderr)
                    actual = json.loads(audio.read_text())
                    expected = [0, 0x90, 0, expected_order, 0]
                    assert actual['enabled'] and actual['queued_bytes'] > 0
                    assert actual['events'] and actual['events'][0] == expected, (table, profile, actual.get('events'), expected)
                    frontend.append({'table': table, 'profile': profile, 'startup_event': actual['events'][0],
                                     'native_sha256': digest(exe.read_bytes()), 'dat_sha256': digest(dat_path.read_bytes()),
                                     'image_sha256': digest((prepared/'human-image.bin').read_bytes())})
    report = {'status': 'VERIFIED_BOUNDED', 'original_build_sha256': BUILD_SHA,
              'scope': 'Actual Retail initialization/reset x86 on retained table contexts, checked against original EXE bytes; does not prove tracker PCM or whole original startup.',
              'tables': rows, 'frontend': frontend,
              'frontend_scope': 'SDL dummy audio/video actual startup request; Amiga uses the shared native adapter, not original Amiga music logic.' if args.frontend else 'not run'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('Retail original initial/reset music configuration:',
          ', '.join(f"{row['table']} bank {row['runs'][0]['bank']} order {row['runs'][0]['order']}" for row in rows))


if __name__ == '__main__':
    main()
