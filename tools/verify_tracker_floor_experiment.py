#!/usr/bin/env python3
"""Compare an isolated, globally modified libxmp with the unmodified build.

This is an experiment, not a runtime dependency or a production patch. It
changes nearest interpolation globally in a private source copy, including
reverse/stereo samples. It does not establish loop or long-run correctness.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'build/libxmp')
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/stim_audio_probe')
    parser.add_argument('--work', type=Path, default=ROOT / 'build/tracker-floor-experiment')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    work = args.work.resolve()
    assert source != work and source not in work.parents, 'work directory must not alter source'
    work.mkdir(parents=True, exist_ok=True)
    copied = work / 'generated-libxmp-source'
    if copied.exists():
        if not (copied / '.slamtilt-floor-experiment').is_file():
            raise RuntimeError(f'Refusing to replace unmarked directory: {copied}')
        shutil.rmtree(copied)
    shutil.copytree(source, copied, ignore=shutil.ignore_patterns('.git'))
    (copied / '.slamtilt-floor-experiment').write_text('Generated experiment; safe to replace.\n')
    mixer = copied / 'src/mix_all.c'
    text = mixer.read_text()
    start = text.index('#define NEAREST_ROUND()')
    end = text.index('\n\n#define VAR_NORM', start)
    original_macro = text[start:end]
    assert 'frac += (1 << (SMIX_SHIFT - 1))' in original_macro
    mixer.write_text(text[:start] + '#define NEAREST_ROUND() do { } while (0)' + text[end:])
    build = work / 'generated-libxmp-build'
    subprocess.run(['cmake', '-S', str(copied), '-B', str(build), '-DBUILD_SHARED=ON',
                    '-DBUILD_STATIC=OFF', '-DCMAKE_BUILD_TYPE=Release'], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run(['cmake', '--build', str(build), '-j', '4'], check=True,
                   stdout=subprocess.DEVNULL)
    library = build / 'libxmp.so.4'
    assert library.exists()
    command = [sys.executable, str(ROOT / 'tools/verify_retail_tracker_native.py'),
               '--native', str(args.native.resolve())]
    baseline_env = dict(os.environ)
    baseline_env.pop('LD_LIBRARY_PATH', None)
    modified_env = dict(baseline_env, LD_LIBRARY_PATH=str(build))
    linkage = subprocess.check_output(['ldd', str(args.native.resolve())], env=modified_env, text=True)
    assert str(build / 'libxmp.so.4') in linkage, 'experimental library was not selected'
    for label, env in (('baseline', baseline_env), ('floor', modified_env)):
        subprocess.run(command + ['--output', str(work / label)], env=env, check=True)
    baseline = json.loads((work / 'baseline/comparison.json').read_text())
    floor = json.loads((work / 'floor/comparison.json').read_text())
    cases = []
    for old, new in zip(baseline['cases'], floor['cases']):
        assert old['table'] == new['table']
        cases.append({'table': old['table'], 'baseline_correlation': old['uncentered_correlation'],
                      'floor_correlation': new['uncentered_correlation'],
                      'baseline_best_aligned_correlation': old['best_correlation_within_8_frames'],
                      'floor_best_aligned_correlation': new['best_correlation_within_8_frames'],
                      'floor_best_alignment_frames': new['original_relative_frame_offset'],
                      'floor_rms_ratio': new['native_rms_over_original']})
    report = {'status': 'EXPERIMENT_ONLY', 'scope': __doc__,
              'original_mixer_source_sha256': hashlib.sha256((source / 'src/mix_all.c').read_bytes()).hexdigest(),
              'experimental_library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(),
              'frames_per_table': baseline['frames_per_table'], 'cases': cases}
    destination = args.report or work / 'report.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['cases']))


if __name__ == '__main__':
    main()
