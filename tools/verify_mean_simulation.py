#!/usr/bin/env python3
"""Compare the supported native prefix to a live original flight fixture."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', type=Path, default=ROOT / 'analysis/traces/mean-flight-100.json')
    parser.add_argument('--probe', type=Path, default=ROOT / 'build/native/mean_sim_probe')
    args = parser.parse_args()
    trace_path = args.trace
    original = json.loads(trace_path.read_text())
    prepared = ROOT / 'build/mean-prepared'
    dat = ROOT / 'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT'
    ticks = original['tick_count']
    command = [str(args.probe), str(dat), str(prepared), str(trace_path), str(ticks)]
    native = json.loads(subprocess.check_output(command, text=True))
    repeat = json.loads(subprocess.check_output(command, text=True))
    keys = ('x', 'y', 'vx', 'vy')
    first_difference = next((a['step'] for a, b in zip(original['samples'], native['samples'])
                             if any(a[k] != b[k] for k in keys)), None)
    report = dict(build_sha256=original['build_sha256'], compared_fields=list(keys),
                  first_difference=first_difference, deterministic=native == repeat,
                  native_samples=len(native['samples']), contacts=native['collisions'],
                  status=native['status'],
                  limitation=('Per-step original contact context replayed; table rules/point forces still bounded'
                              if all('oracle_context' in s for s in original['samples']) else
                              'Captured static flipper poses; live fixture has no per-step flipper/input states.'),
                  prepared_sha256={name: hashlib.sha256((prepared / name).read_bytes()).hexdigest()
                                   for name in ('flipper-state.bin', 'engine-globals.bin', 'normals.bin')})
    output_name = ('mean-native-validation.json' if trace_path.name == 'mean-flight-100.json'
                   else trace_path.stem + '-native-validation.json')
    (ROOT / 'analysis/traces' / output_name).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    assert native == repeat, 'Native steps are not deterministic'
    assert len(native['samples']) == ticks + 1 and native['active'], 'Supported slice stopped before 100 steps'
    if trace_path.name == 'mean-flight-100.json':
        assert first_difference is None or first_difference >= 64, 'Previously verified flight prefix regressed'
    elif all('oracle_context' in s for s in original['samples']):
        assert first_difference is None, 'Synchronized original contact trace diverged'


if __name__ == '__main__':
    main()
