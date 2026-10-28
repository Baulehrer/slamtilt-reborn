#!/usr/bin/env python3
"""Native first-run UI, import, remembered data, rejection and restart checks."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', type=Path, required=True)
    args = parser.parse_args()
    hashes = dict(line.split(None, 1)[::-1] for line in (R / 'packaging/mean-data.sha256').read_text().splitlines())
    with tempfile.TemporaryDirectory(prefix='mean first start ') as temp:
        root = Path(temp)
        state = root / 'preferences'
        state.mkdir()
        env = dict(os.environ, HOME=str(state), XDG_DATA_HOME=str(state), SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        command = [str(args.setup.resolve()), '--importer', str(R / 'tools/slamimport'), '--profile', str(R / 'packaging/mean-data.sha256')]

        def run(*options):
            return subprocess.run([*command, *map(str, options)], env=env, cwd=root, capture_output=True, text=True, timeout=30)

        initial = run('--frames', 2, '--capture', root / 'welcome.bmp')
        assert initial.returncode == 1 and not initial.stdout
        assert (root / 'welcome.bmp').stat().st_size > 10000
        assert run('--saved').returncode == 2
        bad = run('--select', root)
        assert bad.returncode == 2 and not bad.stdout and run('--saved').returncode == 2
        raw = root / "Original Demo $(touch SHOULD_NOT_EXIST) `false`"
        raw.mkdir()
        exe = next((R / 'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE'))
        shutil.copyfile(exe, raw / 'SLAMTILT.EXE')
        (raw / 'DAT').mkdir()
        for name in ('MEAN.DAT', 'MAIN.DAT'):
            shutil.copyfile(exe.parent / 'DAT' / name, raw / 'DAT' / name)
        imported = run('--select', raw, '--capture', root / 'ready.bmp')
        assert imported.returncode == 0, imported.stderr
        data = Path(imported.stdout.strip())
        assert data.is_relative_to(state) and data.is_dir()
        assert all(hashlib.sha256((data / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
        assert run('--saved').stdout.strip() == str(data)
        # Correct folder structure with an unsupported EXE must fail during
        # import, rather than replacing the prior working data selection.
        original_exe = (raw / 'SLAMTILT.EXE').read_bytes()
        (raw / 'SLAMTILT.EXE').write_bytes(bytes([original_exe[0] ^ 1]) + original_exe[1:])
        assert run('--select', raw).returncode == 2
        assert run('--saved').stdout.strip() == str(data)
        (raw / 'SLAMTILT.EXE').write_bytes(original_exe)
        # A rejected new selection must keep the prior valid preference.
        assert run('--select', root).returncode == 2
        assert run('--saved').stdout.strip() == str(data)
        prepared = root / 'prepared with spaces'
        shutil.copytree(data, prepared)
        picked = run('--select', prepared)
        assert picked.returncode == 0 and picked.stdout.strip() == str(prepared)
        assert run('--saved').stdout.strip() == str(prepared)
        target = prepared / 'mean-prepared/lookup.bin'
        target.write_bytes(b'corrupt')
        assert run('--saved').returncode == 2
        restored = run('--select', data)
        assert restored.returncode == 0 and run('--saved').stdout.strip() == str(data)
        assert not list(root.rglob('SHOULD_NOT_EXIST'))
        assert all((raw / 'DAT' / name).read_bytes() == (exe.parent / 'DAT' / name).read_bytes() for name in ('MEAN.DAT', 'MAIN.DAT'))
    report = {'status': 'VERIFIED', 'native_welcome_screen': True, 'cancel_without_selection': True,
              'raw_demo_import': True, 'eight_files_exact': True, 'prepared_data_selection': True,
              'saved_selection_restart': True, 'corrupt_saved_data_rejected': True,
              'failed_selection_preserves_previous': True, 'shell_metacharacter_paths': True,
              'originals_unchanged': True, 'scope': 'SDL dummy UI with --select using same selection/import/persistence path; desktop portal folder click not automated.'}
    (R / 'analysis/traces/mean-setup-acceptance.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
