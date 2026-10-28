#!/usr/bin/env python3
"""Retail-only Mean import, four-table selection and native gameplay regression.

The sandbox hides Demo inputs/prepared data. Existing captured native traces are
comparison fixtures, not a claim of full Original Mean trajectory equivalence.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
HIDDEN = [ROOT / 'build/corpus/win95/demo-1997', ROOT / 'build/mean-prepared',
          ROOT / 'build/mean-minigame-prepared']


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def world_states(rows):
    return [{k: v for k, v in row.items() if k != 'camera_scroll'} for row in rows]


@contextmanager
def retained_on_failure(work):
    path = Path(tempfile.mkdtemp(dir=work, prefix='case-'))
    try:
        yield path
    except BaseException:
        print('Failure artifacts retained:', path, flush=True)
        raise
    else:
        shutil.rmtree(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', type=Path, default=ROOT / 'build/native')
    parser.add_argument('--app', type=Path)
    parser.add_argument('--replay-cases', nargs='*', choices=['primary', 'variant-1', 'variant-2'],
                        default=['primary', 'variant-1', 'variant-2'])
    parser.add_argument('--max-ticks', type=int)
    parser.add_argument('--skip-components', action='store_true')
    parser.add_argument('--report', type=Path, default=ROOT / 'analysis/traces/mean-retail-import.json')
    args = parser.parse_args()
    assert args.max_ticks is None or args.max_ticks > 0, '--max-ticks must be positive'
    build = args.build.resolve()
    importer, menu, view = (build / n for n in ['slamimport', 'slamtilt', 'slamview'])
    if args.app:
        app = args.app.resolve()
        importer, menu, view = app / 'slamimport', app / 'bin/slamtilt', app / 'bin/slamview'
    expected = dict((name.strip(), h) for h, name in
                    (line.split(maxsplit=1) for line in
                     (ROOT / 'packaging/mean-retail-data.sha256').read_text().splitlines()))
    assert len(expected) == 8
    assert shutil.which('bwrap'), 'bubblewrap required to prove Demo-independent import/play'
    work = ROOT / 'build/mean-retail-acceptance'
    work.mkdir(exist_ok=True)
    gameplay = []
    with retained_on_failure(work) as w:
        raw = w / 'Retail original'
        (raw / 'DAT').mkdir(parents=True)
        inputs = ['SLAMTILT.EXE', 'DAT/MAIN.DAT', 'DAT/MEAN.DAT', 'DAT/PIRATE.DAT',
                  'DAT/SPACE.DAT', 'DAT/DEMON.DAT', 'DAT/MENU.DAT']
        for name in inputs:
            shutil.copyfile(RETAIL / name, raw / name)
        input_hashes = {name: sha(raw / name) for name in inputs}
        (w / 'tmp').mkdir()
        env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
                   XDG_DATA_HOME=str(w / 'profile'), TMPDIR=str(w / 'tmp'))
        if args.app:
            env.update(LD_LIBRARY_PATH=str(app / 'lib'),
                       SLAM_TABLE_PROFILES=str(app / 'share/slamtilt/table-profiles.json'))
        sandbox = ['bwrap', '--ro-bind', '/', '/', '--bind', str(w), str(w),
                   '--proc', '/proc', '--dev', '/dev', '--unshare-net']
        for path in HIDDEN:
            assert path.is_dir(), path
            sandbox += ['--tmpfs', str(path)]

        def run(command, success=True, timeout=180):
            result = subprocess.run([*sandbox, *map(str, command)], cwd=w, env=env,
                                    capture_output=True, text=True, timeout=timeout)
            assert (result.returncode == 0) == success, (
                [str(x) for x in command[:3]], result.returncode,
                result.stdout[-700:], result.stderr[-1800:])
            return result

        for path in HIDDEN:
            assert not run(['/usr/bin/find', path, '-mindepth', '1', '-print', '-quit']).stdout
        private = w / 'Mean private'
        recipe = app / 'share/slamtilt/mean-demo-startup.json' if args.app else ROOT / 'analysis/import/mean-demo-startup.json'
        profile = app / 'share/slamtilt/mean-data.sha256' if args.app else ROOT / 'packaging/mean-data.sha256'

        def import_mean(destination):
            return [importer, '--recipe', recipe, '--profile', profile,
                    raw / 'SLAMTILT.EXE', raw / 'DAT', destination]

        run(import_mean(private))
        assert {name: sha(private / name) for name in expected} == expected
        run([importer, '--profile', profile, '--check', private])
        assert read(private / 'data.json')['build_sha256'] == input_hashes['SLAMTILT.EXE']
        manifest = private / 'data.sha256'
        saved_manifest = manifest.read_bytes()
        manifest.write_bytes(saved_manifest + b'invalid\n')
        run([importer, '--profile', profile, '--check', private], success=False)
        manifest.write_bytes(saved_manifest)
        original_files = {str(p.relative_to(private)): sha(p)
                          for p in private.rglob('*') if p.is_file()}
        run(import_mean(private), success=False)
        assert {str(p.relative_to(private)): sha(p)
                for p in private.rglob('*') if p.is_file()} == original_files
        empty = w / 'existing-empty'
        empty.mkdir()
        run(import_mean(empty), success=False)
        assert not list(empty.iterdir())
        link = w / 'dangling'
        link.symlink_to(w / 'absent')
        run(import_mean(link), success=False)
        assert link.is_symlink() and not (w / 'absent').exists()
        for name in ['SLAMTILT.EXE', 'DAT/MEAN.DAT', 'DAT/MAIN.DAT']:
            path = raw / name
            original = path.read_bytes()
            path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
            destination = w / ('bad-' + path.name)
            run(import_mean(destination), success=False)
            assert not destination.exists()
            path.write_bytes(original)
        missing = raw / 'DAT/MAIN.DAT'
        saved = missing.read_bytes()
        missing.unlink()
        destination = w / 'missing-main'
        run(import_mean(destination), success=False)
        assert not destination.exists()
        missing.write_bytes(saved)
        assert not list(w.glob('.mean-import-*'))

        config = w / 'menu.json'
        run([menu, '--config', config, '--import', raw, '--frames', '1'])
        selected = read(config)['tables']
        assert set(selected) == {'mean', 'pirate', 'space', 'demon'}
        assert {name: sha(Path(selected['mean']['data']) / name)
                for name in expected} == expected
        # Imported data contains everything required by the native sessions.
        # Mask both raw Retail copies without touching either original file.
        sandbox += ['--ro-bind', '/dev/null', str(raw / 'SLAMTILT.EXE'),
                    '--ro-bind', '/dev/null', str(RETAIL / 'SLAMTILT.EXE')]
        for original in [raw / 'SLAMTILT.EXE', RETAIL / 'SLAMTILT.EXE']:
            run(['/usr/bin/test', '-s', original], success=False)
        cycle = w / 'cycle.json'
        run([menu, '--config', config, '--exercise-all', '--child-frames', '40', '--trace', cycle])
        events = read(cycle)['events']
        assert events == [event for table in ['mean', 'pirate', 'space', 'demon'] for event in
                          [dict(event='launched', table=table),
                           dict(event='returned', table=table, exit_code=0)]]
        print('Retail-only import, protection cases, all four menu children PASS', flush=True)

        for case in args.replay_cases:
            schedule_path = ROOT / f'build/reborn-playtest/mean/{case}-input.json'
            schedule = read(schedule_path)
            ticks = min(schedule['tick_count'], args.max_ticks) if args.max_ticks else schedule['tick_count']
            trace = w / (case + '.json')
            run([view, private / 'MEAN.DAT', '--play', private / 'mean-prepared',
                 '--trace', ROOT / 'analysis/traces/mean-flight-100.json', '--retail-minigame',
                 '--replay', schedule_path, '--replay-only', '--realtime-steps', ticks,
                 '--frames', ticks // 4 + 1, '--trace-output', trace])
            actual = read(trace)
            baseline_path = ROOT / f'build/reborn-playtest/mean/{case}-native.json'
            baseline = read(baseline_path)
            assert actual['tick_count'] == ticks and not actual['failure']
            assert actual['inputs'] == [e for e in schedule['inputs'] if e['tick'] < ticks]
            aa, bb = world_states(actual['states']), world_states(baseline['states'][:ticks])
            if aa != bb:
                first = next((i for i, pair in enumerate(zip(aa, bb)) if pair[0] != pair[1]), min(len(aa), len(bb)))
                delta = {k: [aa[first].get(k), bb[first].get(k)] for k in set(aa[first]) | set(bb[first])
                         if aa[first].get(k) != bb[first].get(k)} if first < min(len(aa), len(bb)) else {}
                if 'balls' in delta:
                    left, right = delta['balls']
                    delta['balls'] = [(i, offset,
                                       int.from_bytes(bytes(a[offset:offset + 4]), 'little'),
                                       int.from_bytes(bytes(b[offset:offset + 4]), 'little'))
                                      for i, (a, b) in enumerate(zip(left, right))
                                      for offset in range(0, min(len(a), len(b)), 4)
                                      if a[offset:offset + 4] != b[offset:offset + 4]]
                raise AssertionError((case, first, delta))
            assert actual['audio_events'] == [e for e in baseline['audio_events'] if e[0] < ticks], case
            assert all(0 <= row['camera_scroll'] <= 200 for row in actual['states'])
            gameplay.append(dict(case=case, tick_count=ticks,
                                 input_sha256=sha(schedule_path), baseline_sha256=sha(baseline_path),
                                 gameplay_state_sha256=digest(world_states(actual['states'])),
                                 audio_event_sha256=digest(actual['audio_events']),
                                 active_steps=actual['active_steps'],
                                 game_over_wait_ticks=actual['game_over_wait_ticks']))
            del actual, baseline
            print('Retail Mean', case, ticks, 'native baseline/audio exact', flush=True)
        if not args.skip_components:
            lifecycle = w / 'lifecycle.json'
            run([build / 'mean_frontend_lifecycle', private / 'MEAN.DAT', private / 'mean-prepared',
                 ROOT / 'analysis/traces/mean-flight-100.json',
                 ROOT / 'analysis/traces/mean-skillshot-natural-input.json', lifecycle])
            assert lifecycle.is_file()
            fixtures = w / 'fixtures'
            fixtures.mkdir()
            names = set(re.findall(r'"([^"\n]+\.json)"',
                                   (ROOT / 'tests/mean_minigame_finite.cpp').read_text()))
            names.add('mean-minigame1-winning-input.json')
            for name in names:
                shutil.copyfile(ROOT / 'analysis/traces' / name, fixtures / name)
            run([build / 'mean_minigame_finite', private / 'MEAN.DAT', private / 'mean-prepared',
                 ROOT / 'analysis/traces/mean-flight-100.json', fixtures / 'mean-minigame1-winning-input.json'])
            print('Retail Mean 18 minigame finite win/abort cases PASS', flush=True)
            for helper, fixture, extra in [
                    ('mean_rally_finite', 'mean-rally-natural-input.json', ['win']),
                    ('mean_combined_modes_finite', 'mean-combined-modes-input.json', [])]:
                output = w / (helper + '.json')
                run([build / helper, private / 'MEAN.DAT', private / 'mean-prepared',
                     ROOT / 'analysis/traces/mean-flight-100.json', ROOT / 'analysis/traces' / fixture,
                     output, *extra])
                assert output.is_file()
                print('Retail Mean', helper, 'PASS', flush=True)
        assert {name: sha(raw / name) for name in inputs} == input_hashes
        report = dict(status='VERIFIED', supported_retail_exe_sha256=input_hashes['SLAMTILT.EXE'],
                      native_importer_sha256=sha(importer), runtime_sha256=sha(view),
                      recipe_sha256=sha(recipe.parent / 'mean-retail-startup.json'),
                      profile_sha256=sha(profile.parent / 'mean-retail-data.sha256'),
                      exact_profile_files=8, source_assets_embedded=False,
                      demo_source_and_prepared_hidden=True, network_disabled=True,
                      unchanged_original_inputs=True, malformed_manifest_rejected=True,
                      exe_not_required_after_import=True,
                      rejection_cases=['wrong_exe', 'wrong_mean', 'wrong_main', 'missing_main',
                                       'existing_data', 'existing_empty', 'dangling_symlink'],
                      retail_import_tables=['mean', 'pirate', 'space', 'demon'],
                      all_four_children_returned=True, child_frames=40,
                      gameplay_cases=gameplay, gameplay_ticks=sum(c['tick_count'] for c in gameplay),
                      finite_lifecycle_pass=not args.skip_components, whole_original_trajectory_equivalence=False,
                      minigame_finite_cases=0 if args.skip_components else 18,
                      rally_finite_pass=not args.skip_components, combined_modes_finite_pass=not args.skip_components,
                      helper_runtime_origin='local build; packaged runtime checked separately by menu/replay' if args.app else 'local build',
                      scope='Supported Retail-only native import/play with Demo source/prepared inputs '
                            'hidden. Selected existing native Mean regression traces compared exactly; '
                            + ('finite lifecycle/minigame/Rally/combined helpers included. ' if not args.skip_components else 'Finite component helpers omitted in this prefix check. ')
                            + 'Not full Original Retail startup/trajectory equivalence or physical-input/GPU/listening acceptance.')
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('Retail Mean importer/menu/gameplay acceptance PASS', report['gameplay_ticks'], 'ticks')


if __name__ == '__main__':
    main()
