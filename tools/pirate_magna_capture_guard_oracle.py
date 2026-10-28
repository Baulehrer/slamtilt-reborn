#!/usr/bin/env python3
"""42bae4 admission leaf against five genuine, independently replayed contexts.

Only the existing fixture's keyboard events and free-ball waypoints are replayed.
No ball/state/cooldown injection; snapshots containing original bytes stay build/.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from pirate_magna_capture_oracle import Capture
from pirate_adventure_oracle import ROOT, BUILD_SHA, DAT_SHA
from verify_pirate_multiball import KEYS
from verify_pirate_multiball_campaign import integrity

CASES = [(1355, 1, 'ready'), (1356, 0, 'genuine_occupied_capture'),
         (1506, 0, 'cooldown_ten'), (1544, 0, 'cooldown_zero'),
         (1548, 1, 'cooldown_negative_ready')]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path)
    args = parser.parse_args()
    game = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
    source = ROOT/'analysis/traces/pirate-magna-capture-cooldown.json'
    fixture = json.loads(source.read_text())
    trace = json.loads((ROOT/'build/oracle/pirate-modes/magna-capture-cooldown/trace.json').read_text())
    assert sha((game/'SLAMTILT.EXE').read_bytes()) == BUILD_SHA
    assert sha((game/'DAT/PIRATE.DAT').read_bytes()) == DAT_SHA
    integrity(trace, fixture, BUILD_SHA, DAT_SHA)
    folder = ROOT/'build/oracle/pirate-capture-guard'
    folder.mkdir(parents=True, exist_ok=True)
    inputs = {}
    for event in fixture['inputs']:
        inputs.setdefault(event['tick'], []).append(event)
    shots = {event['tick']: event for event in fixture['diagnostic_shots']}
    rows = []
    for end, expected, label in CASES:
        # Each leaf context starts from the independently reset original context.
        m = Capture.fresh_original()
        for tick in range(end):
            for event in inputs.get(tick, []):
                Capture.apply_input(m, event)
            if tick in shots:
                event = shots[tick]
                m.shot(event['layer'], event['x'], event['y'], event.get('ball', 0))
            m.step(tick)
        sample = dict(states=m.ball(), **m.sample())
        for key in KEYS:
            actual = sample[key]
            recorded = trace[key][end if key == 'states' else end-1]
            assert actual == recorded, (end, key)
        image = bytes(m.u.mem_read(0x400000, 0x100000))
        runtime = bytes(m.u.mem_read(0x1000000, 0x10000))
        mapped_game = bytes(m.u.mem_read(0x1000000, 0x400000))
        m.run(0x42bae4, 6, 0x465a68)
        from unicorn.x86_const import UC_X86_REG_EAX
        result = m.u.reg_read(UC_X86_REG_EAX)
        assert result == expected, (end, expected, result)
        assert bytes(m.u.mem_read(0x400000, 0x100000)) == image
        assert bytes(m.u.mem_read(0x1000000, 0x400000)) == mapped_game
        image_name = f'tick-{end}-image.bin'
        runtime_name = f'tick-{end}-runtime.bin'
        (folder/image_name).write_bytes(image)
        (folder/runtime_name).write_bytes(runtime)
        row = dict(tick=end, label=label, expected_eax=expected,
                   ball_state=m.get(0x46c1b4, 2), ball_substate=m.get(0x46c1b6, 2),
                   cooldown=m.get(0x465a68), hold=m.get(0x465a6c),
                   original_game_memory_unchanged=True,
                   image_file=image_name, image_sha256=sha(image),
                   runtime_file=runtime_name, runtime_sha256=sha(runtime),
                   original_mapped_game_sha256=sha(mapped_game))
        rows.append(row)
        print(end, label, 'original EAX', result, 'game memory unchanged', flush=True)
    manifest = ROOT/'analysis/traces/pirate-magna-capture-guard.json'
    manifest.write_text(json.dumps(dict(schema=1, status='ORIGINAL VERIFIED',
        build_sha256=BUILD_SHA, dat_sha256=DAT_SHA,
        source_fixture='analysis/traces/pirate-magna-capture-cooldown.json',
        source_fixture_sha256=sha(source.read_bytes()),
        entry='0x42bae4', eax=6, edx='0x465a68', cases=rows,
        scope='Actual Original+independent reset gameplay contexts, all nine source trace vectors checked at each checkpoint. Direct read-only leaf invocation; not a second simultaneous ball trajectory. No synthetic occupied ball or state/cooldown writes. Native reads the exact private snapshots.'), indent=2)+'\n')
    if args.native:
        subprocess.run([args.native, manifest, folder, game/'DAT/PIRATE.DAT', source,
                        game/'SLAMTILT.EXE'], check=True)


if __name__ == '__main__':
    main()
