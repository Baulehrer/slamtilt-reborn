#!/usr/bin/env python3
"""Development-only independent ADF extraction/SLAM byte proof; no runtime Python."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/amiga_disk_test')
    parser.add_argument('--report', type=Path, default=ROOT / 'analysis/traces/amiga-adf-reader.json')
    a = parser.parse_args()
    spec = importlib.util.spec_from_file_location('slamdecode', ROOT / 'tools/slamdecode.py')
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    work = ROOT / 'build/amiga-adf-reader'
    work.mkdir(exist_ok=True)
    sets = []
    subprocess.run([a.native], check=True, capture_output=True, text=True)
    for group in ['DLM', 'HD-Ninja']:
        source = ROOT / 'amiga/historical-mods' / group
        report = work / (group + '.json')
        subprocess.run([a.native, source, ROOT / 'build/decoded/full', report], check=True)
        actual = json.loads(report.read_text())
        by_name = {r['name']: r for r in actual['files']}
        count = decoded_count = 0
        with tempfile.TemporaryDirectory(dir=work) as tmp:
            tmp = Path(tmp)
            for disk in source.glob('*.adf'):
                raw = disk.read_bytes()
                volume = raw[880 * 512 + 433:880 * 512 + 433 + raw[880 * 512 + 432]].decode('latin1')
                slot = int(volume[-1])
                out = tmp / str(slot)
                out.mkdir()
                subprocess.run([ROOT / 'build/venv/bin/xdftool', disk, 'unpack', out], check=True, capture_output=True, text=True)
                volume_dir = out / volume
                for p in volume_dir.rglob('*'):
                    if not p.is_file():
                        continue
                    name = 'slam' + str(slot) + '/' + p.relative_to(volume_dir).as_posix().lower()
                    data = p.read_bytes()
                    assert by_name[name]['sha256'] == hashlib.sha256(data).hexdigest(), name
                    count += 1
                    if data.startswith(b'SLAM'):
                        decoded = decoder.decode(data)
                        assert by_name[name]['decoded_sha256'] == hashlib.sha256(decoded).hexdigest(), name
                        decoded_count += 1
            negative = tmp / 'negative'
            negative.mkdir()
            images = sorted(source.glob('*.adf'))
            for i, disk in enumerate(images):
                shutil.copyfile(disk, negative / (str(i) + '.ADF'))
            def reject():
                r = subprocess.run([a.native, negative, '/absent'], capture_output=True, text=True)
                assert r.returncode == 2, (r.returncode, r.stdout[-300:], r.stderr)
            q = negative / '0.ADF'
            original = q.read_bytes()
            q.write_bytes(original[:-1]); reject(); q.write_bytes(original)
            bad = bytearray(original); bad[880 * 512 + 24] ^= 1
            q.write_bytes(bad); reject(); q.write_bytes(original)
            # A checksum-correct directory chain cycle must fail independently.
            bad = bytearray(original)
            root = 880 * 512
            entry = next(struct.unpack_from('>I', bad, root + i * 4)[0] for i in range(6, 78) if struct.unpack_from('>I', bad, root + i * 4)[0])
            struct.pack_into('>I', bad, entry * 512 + 124 * 4, entry)
            struct.pack_into('>I', bad, entry * 512 + 5 * 4, 0)
            values = struct.unpack_from('>128I', bad, entry * 512)
            struct.pack_into('>I', bad, entry * 512 + 5 * 4, (-sum(values)) & 0xffffffff)
            q.write_bytes(bad); reject(); q.write_bytes(original)
            shutil.copyfile(q, negative / 'duplicate.adf'); reject(); (negative / 'duplicate.adf').unlink()
            q.unlink(); reject()
        sets.append(dict(name=group, native_files=count, independent_decoder_matches=decoded_count,
                         existing_decoded_reference_matches=actual['reference_decoded_matches']))
    # Independent synthetic OFS data disks exercise 488-byte payload framing,
    # sequence/header links and checksums without any original binary fixture.
    with tempfile.TemporaryDirectory(dir=work) as directory:
        folder = Path(directory)
        for slot in range(1, 6):
            image = bytearray(901120)
            image[:4] = b'DOS\0'
            struct.pack_into('>I', image, 8, 880)
            def word(block, index, value):
                struct.pack_into('>I', image, block * 512 + index * 4, value)
            def checksum(block):
                word(block, 5, 0)
                word(block, 5, (-sum(struct.unpack_from('>128I', image, block * 512))) & 0xffffffff)
            def name(block, text):
                value = text.encode()
                image[block * 512 + 432:block * 512 + 433 + len(value)] = bytes([len(value)]) + value
            word(880, 0, 2); word(880, 3, 72); word(880, 6, 882); word(880, 127, 1)
            name(880, 'Slam' + str(slot)); checksum(880)
            word(882, 0, 2); word(882, 1, 882); word(882, 2, 2); word(882, 4, 884)
            word(882, 77, 884); word(882, 76, 885); word(882, 81, 600)
            word(882, 125, 880); word(882, 127, 0xfffffffd)
            name(882, 'ofs' + str(slot) + '.dat'); checksum(882)
            payload = bytes(i % 251 for i in range(600))
            for sequence, block, chunk, next_block in [(1, 884, payload[:488], 885), (2, 885, payload[488:], 0)]:
                word(block, 0, 8); word(block, 1, 882); word(block, 2, sequence)
                word(block, 3, len(chunk)); word(block, 4, next_block)
                image[block * 512 + 24:block * 512 + 24 + len(chunk)] = chunk
                checksum(block)
            (folder / (str(slot) + '.adf')).write_bytes(image)
        report = folder / 'ofs.json'
        subprocess.run([a.native, folder, '/absent', report], check=True)
        rows = json.loads(report.read_text())['files']
        assert len(rows) == 10 and all(row['size'] == 600 and row['sha256'] == hashlib.sha256(payload).hexdigest() for row in rows)
    result = dict(status='VERIFIED', sets=sets, readonly_sources=True, native_runtime=True,
                  synthetic_OFS_files=5,
                  checks=['size', 'metadata_checksum', 'checksum_correct_cycle', 'duplicate_disk', 'missing_disk', 'SLAM_bounds'],
                  scope='Standard DD AmigaDOS OFS/FFS parser; complete five-disk DLM/HD-Ninja sets independently byte-compared with amitools extraction and Python SLAM reference. No executable loading or emulation.')
    a.report.write_text(json.dumps(result, indent=2) + '\n')
    print('Native ADF/SLAM:', sets, 'negative cases PASS')


if __name__ == '__main__':
    main()
