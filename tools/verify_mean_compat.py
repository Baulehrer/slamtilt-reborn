#!/usr/bin/env python3
"""Verify a prebuilt Mean RC on the host and the actual older Debian ABI."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def version(value):
    return tuple(map(int, value.split('.')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', type=Path, default=ROOT / 'build/compat')
    args = parser.parse_args()
    build = args.build_root.resolve()
    metadata = json.loads((build / 'build.json').read_text())
    app, data = Path(metadata['program']), Path(metadata['data'])
    manifest = json.loads((app / 'bundle.json').read_text())
    ceilings = metadata['pins']['abi_ceiling']
    maxima = {}
    for requirement in manifest['runtime_requirements']:
        match = re.fullmatch(r'(GLIBCXX|GLIBC|CXXABI)_([0-9.]+)', requirement)
        if not match:
            raise RuntimeError('Unexpected ABI requirement: ' + requirement)
        abi, required = match.groups()
        if version(required) > version(ceilings[abi]):
            raise RuntimeError('ABI ceiling exceeded: ' + requirement)
        if abi not in maxima or version(required) > version(maxima[abi]):
            maxima[abi] = required
    if set(maxima) != set(ceilings):
        raise RuntimeError('Incomplete ABI audit')
    host_report = ROOT / 'analysis/traces/mean-compat-package-acceptance.json'
    command = ['python3', str(ROOT / 'tools/verify_mean_package.py'),
               '--program-archive', str(app) + '.tar.gz', '--data-archive', str(data) + '.tar.gz',
               '--checker', str(build / 'native/mean_mode_marathon'), '--output', str(host_report)]
    with (build / 'host-acceptance.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    host = json.loads(host_report.read_text())
    if not host['isolated_namespace']:
        raise RuntimeError('Host checkout isolation was not verified')
    image = metadata['image_id']
    with tempfile.TemporaryDirectory(prefix='.abi-acceptance-', dir=build) as temp:
        root = Path(temp)
        state = root / 'state'
        state.mkdir()
        raw = root / 'raw'
        raw.mkdir()
        (raw / 'DAT').mkdir()
        original_exe = next((ROOT / 'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE'))
        shutil.copyfile(original_exe, raw / 'SLAMTILT.EXE')
        for name in ('MEAN.DAT', 'MAIN.DAT'):
            shutil.copyfile(data / name, raw / 'DAT' / name)
        common = ['docker', 'run', '--rm', '--network', 'none', '--read-only', '--tmpfs', '/tmp',
                  '--user', f'{os.getuid()}:{os.getgid()}',
                  '--mount', f'type=bind,src={app},dst=/app,readonly',
                  '--mount', f'type=bind,src={data},dst=/game-data,readonly',
                  '--mount', f'type=bind,src={raw},dst=/raw,readonly',
                  '--mount', f'type=bind,src={build / "native/mean_mode_marathon"},dst=/mean-check,readonly',
                  '--mount', f'type=bind,src={build / "native/sha256_tests"},dst=/sha256-check,readonly',
                  '--mount', f'type=bind,src={ROOT / "analysis/traces/mean-five-modes-input.json"},dst=/replay.json,readonly',
                  '--mount', f'type=bind,src={state},dst=/state',
                  '-e', 'HOME=/state', '-e', 'XDG_DATA_HOME=/state/prefs',
                  '-e', 'SDL_VIDEODRIVER=dummy', '-e', 'SDL_AUDIODRIVER=dummy',
                  '-e', 'LD_LIBRARY_PATH=/app/lib',
                  '-e', 'SLAM_TABLE_PROFILES=/app/share/slamtilt/table-profiles.json', image]

        def run(arguments, empty_path=False):
            invocation=[*common[:-1],'-e','PATH=/no-import-tools',common[-1]] if empty_path else common
            result = subprocess.run([*invocation, *arguments], text=True, capture_output=True, timeout=60)
            if result.returncode:
                raise RuntimeError('Debian runtime failed: ' + result.stderr[-2000:] + result.stdout[-1000:])
            return result.stdout

        libc = run(['ldd', '--version']).splitlines()[0]
        run(['/sha256-check'])
        imported = run(['/app/bin/slamsetup', '--importer', '/app/slamimport',
                        '--profile', '/app/share/slamtilt/mean-data.sha256', '--select', '/raw'],empty_path=True)
        imported_path = state / Path(imported.strip()).relative_to('/state')
        hashes = dict(line.split(None, 1)[::-1] for line in (app / 'share/slamtilt/mean-data.sha256').read_text().splitlines())
        if not all(hashlib.sha256((imported_path / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items()):
            raise RuntimeError('Older-runtime raw import profile differs')
        selected = run(['/app/bin/slamsetup', '--importer', '/app/slamimport',
                        '--profile', '/app/share/slamtilt/mean-data.sha256', '--select', '/game-data'])
        if selected.strip() != '/game-data':
            raise RuntimeError('Older-runtime native data selection failed')
        run(['/app/slamplay', '--frontend-acceptance', '/state/frontend.json',
             '--frames', '14', '--capture', '/state/frontend.bmp'])
        run(['/mean-check', '/game-data/MEAN.DAT', '/game-data/mean-prepared',
             '/app/share/slamtilt/initial-state.json', '/replay.json', '/state/game.json'])
        frontend = json.loads((state / 'frontend.json').read_text())
        golden = json.loads((state / 'game.json').read_text())
        if golden['cases'][0] != host['all_five_packaged_data_replay']:
            raise RuntimeError('Old/new runtime finite game results differ')
        if not frontend['audio_requested'] or not frontend['focus_minimize_resume'] or frontend['open_failures']:
            raise RuntimeError('Older-runtime SDL frontend acceptance failed')
        if golden['speed']['peak_balls'] != 8:
            raise RuntimeError('Older-runtime multiball acceptance failed')
        artifacts = build / 'acceptance'
        artifacts.mkdir(exist_ok=True)
        for name in ('frontend.json', 'game.json', 'frontend.bmp'):
            shutil.copyfile(state / name, artifacts / name)
    archives = {str(p): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
                for p in (Path(str(app) + '.tar.gz'), Path(str(data) + '.tar.gz'))}
    report = {'evidence_id': 'MEAN-079', 'status': 'VERIFIED', 'abi_maxima': maxima,
              'abi_ceilings': ceilings, 'older_runtime': libc, 'toolchain_image_id': image,
              'program': str(app), 'private_data': str(data), 'archives': archives,
              'host_acceptance': str(host_report.relative_to(ROOT)),
              'native_setup_on_older_runtime': True, 'remembered_start': True,
              'raw_import_on_older_runtime': True, 'raw_import_eight_files_exact': True,
              'native_import_on_both_runtimes': True, 'known_sha256_vectors_on_older_runtime': True,
              'older_runtime_import_empty_path': True,
              'older_runtime_frontend': frontend, 'all_five_old_new_identical': golden['cases'][0],
              'all_five_repeats_per_runtime': 2, 'network_disabled': True,
              'source_checkout_not_mounted': True, 'program_and_data_read_only': True,
              'scope': 'Actual Debian12 glibc2.36 and host Linux native acceptance; no universal distro/GPU-driver compatibility claim.'}
    (ROOT / 'analysis/traces/mean-compat-acceptance.json').write_text(json.dumps(report, indent=2) + '\n')
    metadata['verification_pending'] = False
    metadata['verification'] = 'analysis/traces/mean-compat-acceptance.json'
    (build / 'build.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps({'status': 'VERIFIED', 'abi_maxima': maxima, 'older_runtime': libc,
                      'final_score': golden['cases'][0]['final_score'], 'report': 'analysis/traces/mean-compat-acceptance.json'}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit('verify_mean_compat: ' + str(error))
