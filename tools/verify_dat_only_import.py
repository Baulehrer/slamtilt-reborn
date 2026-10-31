#!/usr/bin/env python3
"""Prove isolated first import/play with DAT files only and no checkout or caches."""
import argparse
from retail_audio_fixture import corrected_audio_events
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT'
TABLES = ['mean', 'pirate', 'space', 'demon']


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def world_states(rows):
    return [{k: v for k, v in row.items() if k != 'camera_scroll'} for row in rows]


def exact_prefix(actual, expected, table, vector):
    if actual != expected[:len(actual)]:
        at = next((i for i, (a, b) in enumerate(zip(actual, expected)) if a != b),
                  min(len(actual), len(expected)))
        raise AssertionError((table, vector, at, actual[at:at + 1], expected[at:at + 1]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--build', type=Path, default=ROOT / 'build/native')
    p.add_argument('--app', type=Path)
    p.add_argument('--ticks', type=int, default=4000)
    p.add_argument('--legacy-audio-fixture', action='store_true', help='Expect historical 0/0 startup from an unchanged older package')
    p.add_argument('--report', type=Path, default=ROOT / 'analysis/traces/dat-only-import.json')
    a = p.parse_args()
    assert a.ticks > 0 and a.ticks % 4 == 0
    assert shutil.which('bwrap'), 'bubblewrap required for checkout/cache isolation'
    work = Path(tempfile.mkdtemp(prefix='slam-dat-only-'))
    success = False
    try:
        app = work / 'app'
        if a.app:
            shutil.copytree(a.app.resolve(), app)
        else:
            subprocess.run([sys.executable, str(ROOT / 'tools/slamtilt-pack'), '--build',
                            str(a.build.resolve()), '--output', str(app)], check=True,
                           capture_output=True, text=True)
        manifest = read(app / 'frontend-bundle.json')
        assert not manifest['original_assets_included']
        for name, h in manifest['files'].items():
            assert sha(app / name) == h, name
        assert not any(q.suffix.lower() in ['.exe', '.dat', '.bin'] for q in app.rglob('*') if q.is_file())
        raw, state, fixtures = (work / n for n in ['raw', 'state', 'fixtures'])
        (raw / 'DAT').mkdir(parents=True)
        state.mkdir()
        fixtures.mkdir()
        for name in ['MEAN.DAT', 'PIRATE.DAT', 'SPACE.DAT', 'DEMON.DAT', 'MAIN.DAT', 'MENU.DAT']:
            shutil.copyfile(RETAIL / name, raw / 'DAT' / name)
        raw_hashes = {q.name: sha(q) for q in (raw / 'DAT').iterdir()}
        assert not list(raw.rglob('*.EXE'))

        # No user home, project tree, corpus, oracle, or pre-existing prepared data
        # is mounted into the sandbox. Only relocated program, DATs and fresh state.
        base = ['bwrap', '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib',
                '--ro-bind', '/lib64', '/lib64', '--ro-bind', '/etc', '/etc',
                '--dir', '/home', '--dir', '/tmp', '--dir', '/run',
                '--ro-bind', str(app), '/app', '--ro-bind', str(raw), '/raw',
                '--bind', str(state), '/state', '--ro-bind', str(fixtures), '/fixtures',
                '--unshare-net', '--unshare-pid', '--proc', '/proc', '--dev', '/dev', '--chdir', '/state',
                '--setenv', 'HOME', '/state', '--setenv', 'XDG_DATA_HOME', '/state',
                '--setenv', 'LD_LIBRARY_PATH', '/app/lib', '--setenv', 'PATH', '/no-tools',
                '--setenv', 'SDL_VIDEODRIVER', 'dummy', '--setenv', 'SDL_AUDIODRIVER', 'dummy',
                '--setenv', 'SLAM_TABLE_PROFILES', '/app/share/slamtilt/table-profiles.json']

        def run(command, ok=True, timeout=180):
            r = subprocess.run([*base, *map(str, command)], capture_output=True,
                               text=True, timeout=timeout)
            assert (r.returncode == 0) == ok, (list(map(str, command)), r.returncode,
                                              r.stdout[-600:], r.stderr[-1800:])
            return r

        run(['/usr/bin/test', '!', '-e', str(ROOT)])
        run(['/usr/bin/test', '!', '-e', '/raw/SLAMTILT.EXE'])
        private = state / 'mean-direct'
        run(['/app/slamimport', '/raw/DAT', '/state/mean-direct'])
        run(['/app/slamimport', '--check', '/state/mean-direct'])
        assert not read(private / 'data.json').get('input_executable_provided', True)
        before = {str(q.relative_to(private)): sha(q) for q in private.rglob('*') if q.is_file()}
        run(['/app/slamimport', '/raw/DAT', '/state/mean-direct'], ok=False)
        assert before == {str(q.relative_to(private)): sha(q) for q in private.rglob('*') if q.is_file()}
        (state / 'empty').mkdir()
        run(['/app/slamimport', '/raw/DAT', '/state/empty'], ok=False)
        assert not list((state / 'empty').iterdir())
        (state / 'dangling').symlink_to('absent')
        run(['/app/slamimport', '/raw/DAT', '/state/dangling'], ok=False)
        assert (state / 'dangling').is_symlink() and not (state / 'absent').exists()

        menu = ['/app/bin/slamtilt', '--config', '/state/menu.json']
        run([*menu, '--import', '/raw/DAT', '--frames', '1'])
        config = read(state / 'menu.json')
        assert set(config['tables']) == set(TABLES)
        snapshot = (state / 'menu.json').read_bytes()
        initial_dirs = {str(q) for q in state.rglob('*-menu-data-*')}
        for name in ['MEAN.DAT', 'PIRATE.DAT', 'SPACE.DAT', 'DEMON.DAT', 'MAIN.DAT']:
            q = raw / 'DAT' / name
            original = q.read_bytes()
            q.write_bytes(bytes([original[0] ^ 1]) + original[1:])
            run([*menu, '--import', '/raw', '--frames', '1'], ok=False)
            assert (state / 'menu.json').read_bytes() == snapshot
            assert {str(q) for q in state.rglob('*-menu-data-*')} == initial_dirs
            q.write_bytes(original)
        main_dat = raw / 'DAT/MAIN.DAT'
        original = main_dat.read_bytes()
        main_dat.unlink()
        run([*menu, '--import', '/raw', '--frames', '1'], ok=False)
        assert (state / 'menu.json').read_bytes() == snapshot
        main_dat.write_bytes(original)
        for repeat in range(2):
            run([*menu, '--exercise-all', '--child-frames', '16', '--trace', f'/state/cycle{repeat}.json'])
            events = read(state / f'cycle{repeat}.json')['events']
            assert events == [e for table in TABLES for e in
                              [dict(event='launched', table=table),
                               dict(event='returned', table=table, exit_code=0)]]
        print('DAT-only isolated import, corruption rollback and four-child reload PASS', flush=True)

        cases = []
        for table in TABLES:
            source_path = ROOT / f'build/reborn-playtest/{table}/primary-{"input" if table == "mean" else "oracle"}.json'
            source = read(source_path)
            (fixtures / 'replay.json').write_text(json.dumps(dict(inputs=source['inputs'])))
            data, prepared = (config['tables'][table][k] for k in ['data', 'prepared'])
            if table == 'mean':
                command = ['/app/bin/slamview', data + '/MEAN.DAT', '--play', prepared,
                           '--trace', '/app/share/slamtilt/initial-state.json', '--retail-minigame',
                           '--trace-output', '/state/game.json', '--realtime-steps', a.ticks,
                           '--frames', a.ticks // 4 + 1, '--replay-only']
            elif table == 'pirate':
                command = ['/app/bin/slamview', data + '/PIRATE.DAT', '--pirate-play', prepared,
                           '--full-state-trace', '--trace-output', '/state/game.json',
                           '--audio-trace', '/state/audio.json', '--frames', a.ticks // 4, '--replay-only']
            else:
                command = ['/app/bin/slamslice', table, prepared, data + '/' + table.upper() + '.DAT',
                           '--trace', '/state/game.json', '--audio', '--audio-trace', '/state/audio.json',
                           '--frames', a.ticks // 4, '--presentation', '--replay-only']
            run([*command, '--replay', '/fixtures/replay.json'])
            actual = read(state / 'game.json')
            assert actual['tick_count'] == a.ticks
            if table == 'mean':
                reference_path = ROOT / 'build/reborn-playtest/mean/primary-native.json'
                reference = read(reference_path)
                assert not actual['failure']
                assert len(actual['states']) == a.ticks
                exact_prefix(world_states(actual['states']), world_states(reference['states']), table, 'states')
                audio = actual['audio_events']
                expected_audio = [e for e in reference['audio_events'] if e[0] < a.ticks]
                vectors = ['states excluding camera_scroll', 'audio_events']
            else:
                reference_path, reference = source_path, source
                vectors = ['states', 'lifecycle', 'highscore_sha256', 'lamp_sha256', 'ball_pool_sha256']
                vectors += ['timing', 'dmd_sha256', 'rule_sha256', 'video_sha256'] if table == 'pirate' else ['poses', 'globals']
                if table == 'demon':
                    vectors.append('raw_state_sha256')
                for vector in vectors:
                    extra = len(reference[vector]) - reference['tick_count']
                    assert extra in [0, 1], (table, vector, 'unexpected reference cadence', extra)
                    assert len(actual[vector]) == a.ticks + extra, (table, vector, 'truncated trace')
                    exact_prefix(actual[vector], reference[vector], table, vector)
                audio = read(state / 'audio.json')['events']
                expected_audio = [e for e in reference['audio_events'] if e[0] < a.ticks]
            if table != 'mean' and not a.legacy_audio_fixture:
                expected_audio = corrected_audio_events(expected_audio, table)
            assert audio == expected_audio, (table, 'audio prefix', audio[:4], expected_audio[:4])
            cases.append(dict(table=table, ticks=a.ticks, exact_vectors=vectors,
                              audio_requests=len(audio), audio_sha256=digest(audio),
                              reference_sha256=sha(reference_path), runtime_sha256=sha(app / ('bin/slamview' if table in ['mean', 'pirate'] else 'bin/slamslice'))))
            print('DAT-only', table, a.ticks, 'state/audio exact PASS', flush=True)
            del source, reference, actual
        assert {q.name: sha(q) for q in (raw / 'DAT').iterdir()} == raw_hashes
        report = dict(status='VERIFIED', legacy_audio_fixture=a.legacy_audio_fixture, source_inputs='Windows DAT files only',
                      source_dat_sha256=raw_hashes, checkout_hidden=True, corpus_hidden=True,
                      existing_prepared_caches_hidden=True, original_exe_present=False,
                      native_importer_sha256=sha(app / 'slamimport'), original_assets_bundled=False,
                      program_and_originals_readonly=True, empty_PATH=True, network_disabled=True,
                      all_four_children_returned=True, reload_cycles=2,
                      rejection_cases=['wrong_mean', 'wrong_pirate', 'wrong_space', 'wrong_demon',
                                       'wrong_main', 'missing_main', 'existing_data', 'existing_empty', 'dangling_symlink'],
                      original_inputs_unchanged=True, cases=cases,
                      total_ticks=sum(c['ticks'] for c in cases),
                      whole_original_mean_trajectory_equivalence=False,
                      scope='Relocated asset-free program, fresh private state, DAT-only first import, actual native child reload and bounded legal replay. Checkout/home/corpus/caches hidden; no EXE copied or mounted. Mean compared to prior native regression, other tables to configured Original vectors/audio. No GPU/physical-input/listening/whole-table claim.')
        if a.app:
            archive = Path(str(a.app.resolve()) + '.tar.gz')
            if archive.exists():
                report['archive_sha256'] = sha(archive)
        a.report.write_text(json.dumps(report, indent=2) + '\n')
        success = True
        print('DAT-only import and all-four gameplay acceptance PASS', report['total_ticks'], flush=True)
    finally:
        if success:
            shutil.rmtree(work)
        else:
            print('Failure artifacts retained:', work, flush=True)


if __name__ == '__main__':
    main()
