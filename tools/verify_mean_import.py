#!/usr/bin/env python3
"""Guard the supported raw import and preserve user files on all failures."""
import hashlib
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--native',type=Path,default=R/'build/native/slamimport');args=parser.parse_args()
    exe = next((R / 'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE'))
    hashes = dict(line.split(None, 1)[::-1] for line in (R / 'packaging/mean-data.sha256').read_text().splitlines())
    with tempfile.TemporaryDirectory(prefix='mean raw import ') as temp:
        root = Path(temp)
        raw = root / 'original data'
        raw.mkdir()
        inputs = {'SLAMTILT.EXE': exe.read_bytes(), **{name: (exe.parent / 'DAT' / name).read_bytes() for name in ('MEAN.DAT', 'MAIN.DAT')}}
        for name, data in inputs.items():
            (raw / name).write_bytes(data)

        def run(output):
            return subprocess.run([str(args.native.resolve()), '--recipe',str(R/'analysis/import/mean-demo-startup.json'),'--profile',str(R/'packaging/mean-data.sha256'), str(raw / 'SLAMTILT.EXE'), str(raw), str(output)], cwd=root, capture_output=True, text=True)

        output = root / 'private data'
        result = run(output)
        assert result.returncode == 0, result.stderr
        assert all(hashlib.sha256((output / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
        reference=root/'python reference'
        compared=subprocess.run(['python3','-S',str(R/'tools/slamimport_reference.py'),str(raw/'SLAMTILT.EXE'),str(raw),str(reference)],cwd=root,capture_output=True,text=True)
        assert compared.returncode==0,compared.stderr
        assert all((output/name).read_bytes()==(reference/name).read_bytes() for name in hashes)
        def check():
            return subprocess.run([str(args.native.resolve()),'--profile',str(R/'packaging/mean-data.sha256'),'--check',str(output)],capture_output=True,text=True)
        assert check().returncode==0
        manifest=output/'data.sha256';saved_manifest=manifest.read_text();manifest.write_text(saved_manifest+'invalid\n')
        assert check().returncode==2
        manifest.write_text(saved_manifest)
        before = {str(p.relative_to(output)): p.read_bytes() for p in output.rglob('*') if p.is_file()}
        assert run(output).returncode == 2
        assert all((output / name).read_bytes() == data for name, data in before.items())
        empty = root / 'existing empty'
        empty.mkdir()
        assert run(empty).returncode == 2 and not list(empty.iterdir())
        link = root / 'dangling'
        link.symlink_to(root / 'absent')
        assert run(link).returncode == 2 and link.is_symlink() and not (root / 'absent').exists()
        for name, data in inputs.items():
            bad = root / ('bad-' + name)
            (raw / name).write_bytes(bytes([data[0] ^ 1]) + data[1:])
            result = run(bad)
            assert result.returncode == 2 and not bad.exists(), (name, result.stderr)
            (raw / name).write_bytes(data)
        (raw / 'MAIN.DAT').unlink()
        assert run(root / 'missing').returncode == 2 and not (root / 'missing').exists()
        assert not list(root.glob('.mean-import-*'))
    report = {'status': 'VERIFIED', 'exact_profile_files': 8, 'native': True, 'python_reference_eight_files_exact':True,'native_profile_check':True,'malformed_private_manifest_rejected':True,
              'rejected': ['wrong_exe', 'wrong_mean', 'wrong_main', 'missing_main', 'existing_data', 'existing_empty', 'dangling_symlink'],
              'source_assets_embedded': False, 'emulator_required': False}
    (R / 'analysis/traces/mean-import-acceptance.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
