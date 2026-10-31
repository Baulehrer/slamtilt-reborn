#!/usr/bin/env python3
"""Compare two consecutively earned Demon video modes with the original x86 game.

Fixtures require the user's private Windows Retail DAT/EXE. The bank/trap
contacts are diagnostic; Brain choices are programmatic, not human tracking.
"""
from retail_audio_fixture import corrected_audio_events
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
SOURCE = ROOT / 'build/oracle/demon-modes/video-consecutive-rewards.json'
PIN = ROOT / 'analysis/traces/demon-video-consecutive-rewards.json'
KEYS = ('states', 'globals', 'poses', 'lifecycle', 'highscore_sha256',
        'lamp_sha256', 'raw_state_sha256', 'ball_pool_sha256',
        'clock_state', 'mode_aux_sha256', 'video_state')


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_json(value):
    return digest_bytes(json.dumps(value, separators=(',', ':')).encode())


def require(condition, description):
    if not condition:
        raise AssertionError(description)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, default=ROOT / 'build/native/slamslice')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/demon-video-consecutive')
    parser.add_argument('--report', type=Path,
                        default=ROOT / 'analysis/traces/demon-video-consecutive-acceptance.json')
    parser.add_argument('--freeze', action='store_true', help='Create a new original fixture; never overwrite one')
    args = parser.parse_args()
    source = json.loads(SOURCE.read_text())
    require(source['case'] == 'video-consecutive' and source['table'] == 'demon', 'Original case identity')
    require(source['original_reset_exact'], 'Original independent reset not verified')
    require(digest_bytes((GAME / 'SLAMTILT.EXE').read_bytes()) == source['build_sha256'], 'Original EXE hash')
    require(digest_bytes((GAME / 'DAT/DEMON.DAT').read_bytes()) == source['dat_sha256'], 'Original DAT hash')
    marks = {m['label']: m for m in source['milestones']}
    require(len(marks) == len(source['milestones']), 'Duplicate milestone label')
    first, first_end = marks['video_started'], marks['video_returned']
    second, second_end = marks['second_video_started'], marks['second_video_returned']
    require(first['field_46d6e4'] == 0 and second['field_46d6e4'] == 1, 'Werewolf then Brain order')
    require(first['video_state'][-1] == second['video_state'][-1] == 1, 'Video entry')
    require(marks['video_ended']['video_state'][-1] == marks['second_video_ended']['video_state'][-1] == 0,
            'Video termination')
    require(first_end['state'] == second_end['state'] == 2 and first_end['phase'] == second_end['phase'] == 2,
            'Return to free-ball normal phase')
    require(first['ball_number'] == second['ball_number'] == second_end['ball_number'], 'Same ball')
    require(first_end['tick'] < marks['second_video_armed']['tick'] < second['tick'], 'Second bank rearmed after return')
    require(marks['second_video_armed']['video_armed'] == 1 and second['video_armed'] == 0, 'Second admission flag')
    choice = marks['second_choice_selected']
    require(choice['cups'][choice['selected']] != 0, 'Chosen Brain location')
    awards = [p for p in source['payments'] if p['return_address'] == '0x4169c7']
    require(len(awards) == 1 and awards[0]['amount'] == 50000000 and
            choice['tick'] < awards[0]['tick'] <= second_end['tick'], '50M correct Brain payout')
    require(not any(e['action'] == 'new_game' for e in source['inputs']), 'New game between video modes')

    keys = ('case', 'audio_events', 'table', 'build_sha256', 'dat_sha256', 'tick_count',
            'inputs', 'diagnostic_shots', 'milestones', 'payments', 'original_reset_exact')
    frozen = {key: source[key] for key in keys}
    frozen['sequence_sha256'] = {key: digest_json(source[key]) for key in KEYS}
    frozen['scope'] = 'One original game; diagnostic physical moon/trap contacts; no rule/score/timer edits; Brain solution obtained from observed state, not visual tracking.'
    if args.freeze:
        PIN.parent.mkdir(parents=True, exist_ok=True)
        with PIN.open('x') as f:
            json.dump(frozen, f, indent=2)
            f.write('\n')
    require(json.loads(PIN.read_text()) == frozen, 'Pinned Original fixture differs')

    count, cut = source['tick_count'], second['tick']
    require(count % 4 == 0, 'Frame-aligned tick count')
    args.output.mkdir(parents=True, exist_ok=True)
    replay, ui = args.output / 'sdl-replay.json', args.output / 'sdl-events.json'
    replay.write_text(json.dumps({'inputs': [e for e in source['inputs'] if e['tick'] < cut]}))
    controls = [e for e in source['inputs'] if e['tick'] >= cut]
    require(all(e['tick'] % 4 == 0 for e in controls), 'SDL control alignment')
    events = [dict(frame=i, type='focus_gained') for i in range(count // 4)]
    for e in controls:
        events.append(dict(frame=e['tick'] // 4, type='key',
                           key={'left':'Left Shift', 'right':'Right Shift', 'enter':'Return'}[e['action']], down=e['down']))
    events.sort(key=lambda e: e['frame'])
    ui.write_text(json.dumps({'events': events}))
    out, audio = args.output / 'sdl-trace.json', args.output / 'sdl-audio.json'
    binary = args.native.resolve()
    binary_hash = digest_bytes(binary.read_bytes())
    cmd = [str(binary), 'demon', str(ROOT / 'build/oracle/demon-full-game'), str(GAME / 'DAT/DEMON.DAT'),
           '--presentation', '--windowed', '--frames', str(count // 4), '--replay', str(replay),
           '--diagnostic-shots', str(SOURCE), '--ui-events', str(ui), '--trace', str(out),
           '--audio', '--audio-trace', str(audio)]
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software',
               XDG_DATA_HOME=str(args.output.resolve() / 'profile'),
               SLAM_TABLE_PROFILES=str(ROOT / 'analysis/table-profiles.json'))
    subprocess.run(cmd, env=env, check=True)
    require(digest_bytes(binary.read_bytes()) == binary_hash, 'Native binary changed during replay')
    native, sound = json.loads(out.read_text()), json.loads(audio.read_text())
    require(native['tick_count'] == count, 'Native tick count')
    for key in KEYS:
        require(native[key] == source[key], 'Original/native vector differs: ' + key)
    require(sound['enabled'] and sound['queued_bytes'] > 0 and sound['events'] == corrected_audio_events(source['audio_events'], 'demon'),
            'Native audio requests or queue')
    journal = [dict(tick=int(tick), **e) for tick, items in native['physical_inputs'] for e in items]
    require(all(e['tick'] == 0 and not e['down'] for e in journal if e['tick'] < cut), 'Unexpected startup input')
    require([e for e in journal if e['tick'] >= cut] == controls, 'SDL control journal differs')
    result = {'status':'VERIFIED_BOUNDED', 'table':'demon', 'case':source['case'],
              'original_build_sha256':source['build_sha256'], 'dat_sha256':source['dat_sha256'],
              'original_trace_sha256':digest_bytes(SOURCE.read_bytes()), 'pinned_fixture_sha256':digest_bytes(PIN.read_bytes()),
              'native_sha256':binary_hash, 'tick_count':count, 'ball_number':first['ball_number'],
              'first_video_start':first['tick'], 'first_return':first_end['tick'],
              'second_bank_armed':marks['second_video_armed']['tick'], 'second_video_start':cut,
              'second_confirm':marks['second_choice_confirmed']['tick'], 'second_return':second_end['tick'],
              'brain_award':awards[0], 'SDL_control_events':len(controls),
              'audio_requests':len(source['audio_events']), 'compared_vectors':list(KEYS),
              'scope':'One original/reset and current native/reset game. Video modes earned by diagnostic physical contacts; second mode controlled by injected SDL events chosen from observed brain position, not human visual tracking. Original mixed PCM and other seeds/outcomes remain open.'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS Demon: Werewolf return, second earned bank, Brain 50M and return; SDL keys / 11 vectors / audio requests exact')


if __name__ == '__main__':
    main()
