#!/usr/bin/env python3
"""Repeat an explicit deterministic replay command; keep logs and raw metrics."""
import argparse
import hashlib
import json
import platform
import os
import time
import statistics
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runs', type=int, default=5)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command[:1] == ['--']:
        command = command[1:]
    if not command or args.runs < 1:
        parser.error('Provide a command and at least one repetition')
    args.output.mkdir(parents=True, exist_ok=True)
    executable = Path(command[0]).resolve()
    report = dict(command=command, platform=platform.platform(),
                  executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
                  executable_bytes=executable.stat().st_size, runs=[])
    cache = executable.parent / 'CMakeCache.txt'
    if cache.exists():
        selected = ('CMAKE_BUILD_TYPE:', 'CMAKE_CXX_COMPILER:',
                    'CMAKE_CXX_FLAGS_RELEASE:', 'SLAM_RELEASE_COMPACT:', 'SLAM_RELEASE_LTO:')
        report['build_configuration'] = [line for line in cache.read_text().splitlines()
                                         if line.startswith(selected)]
    report['input_sha256'] = {str(Path(arg)): hashlib.sha256(Path(arg).read_bytes()).hexdigest()
                              for arg in command[1:] if Path(arg).is_file()}
    report['load_average_before'] = os.getloadavg()
    for index in range(args.runs):
        with (args.output / f'{index}.log').open('w') as log:
            started = time.perf_counter()
            process = subprocess.Popen(command, stdout=log, stderr=log)
            _, status, usage = os.wait4(process.pid, 0)
            process.returncode = os.waitstatus_to_exitcode(status)
            wall = time.perf_counter() - started
        if process.returncode:
            raise SystemExit(f'Replay failed ({process.returncode}); inspect run {index} log')
        user, system, rss = usage.ru_utime, usage.ru_stime, usage.ru_maxrss
        report['runs'].append(dict(wall_seconds=wall, user_seconds=user,
                                   system_seconds=system, max_rss_kib=rss))
    report['median'] = {key: statistics.median(run[key] for run in report['runs'])
                        for key in report['runs'][0]}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['median']))


if __name__ == '__main__':
    main()
