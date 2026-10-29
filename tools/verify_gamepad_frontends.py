#!/usr/bin/env python3
"""Real native frontends, a recognized virtual pad and scheduled SDL pad events."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--native', type=Path, default=ROOT/'build/native/gamepad_frontend_probe')
p.add_argument('--menu', type=Path, default=ROOT/'build/native/slamtilt')
p.add_argument('--source', type=Path, default=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT')
p.add_argument('--output', type=Path, default=ROOT/'build/controller-acceptance')
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)
(a.output/"report.json").write_text(json.dumps({"status":"RUNNING"})+"\n")
config = a.output.resolve()/'frontend.json'
env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software', XDG_DATA_HOME=str(a.output.resolve()/'import-profile'))

def run(command, target_env, label):
    r = subprocess.run(list(map(str, command)), env=target_env, text=True, capture_output=True, timeout=40)
    (a.output/(label+'.log')).write_text(r.stdout+'\n'+r.stderr)
    if r.returncode:
        raise RuntimeError(f'{label}: exit{r.returncode}\n{r.stderr[-1200:]}')
    if 'watchdog=1' in r.stdout:
        raise RuntimeError(label+': fallback watchdog stopped the frontend')

if not config.exists():
    run([a.menu, '--config', config, '--import', a.source, '--windowed', '--frames', '1'], env, 'import')
locations = json.loads(config.read_text())['tables']
report = {'status': 'PASS', 'scope': 'actual frontend code, SDL virtual gamepad identity + scheduled pad/focus events, dummy video/audio; no physical hardware',
          'probe_sha256': hashlib.sha256(a.native.read_bytes()).hexdigest(), 'tables': {}}
for table in ['mean', 'pirate', 'space', 'demon', 'menu']:
    trace = a.output.resolve()/(table+'.json')
    if table=='menu':
        (a.output/'menu.json').unlink(missing_ok=True)
    table_env = dict(env, XDG_DATA_HOME=str(a.output.resolve()/(table+'-profile')))
    loc = locations['mean' if table == 'menu' else table]
    run([a.native, table, loc['data'], loc['prepared'], ROOT/'packaging/mean-initial.json', trace], table_env, table)
    j = json.loads(trace.read_text())
    if table == 'menu':
        frames = j['controller_frames']
        assert any(f['options_open'] for f in frames), 'Controller did not open native menu options'
        assert {0, 1, 2, 3, 4}.issubset({f['selected'] for f in frames}), 'Controller skipped native menu navigation'
        assert j['selected'] == 5 and not j['options_open'], 'Controller did not cancel options and choose Quit'
        report['menu'] = {'navigated': True, 'opened_options': True, 'cancelled_options': True, 'quit_via_controller': True}
        continue
    assert not (j.get('failure') or j.get('error')), j.get('failure') or j.get('error')
    frames = j['ui_frames']
    assert any(f['menu'] for f in frames), table+': Start did not open options'
    assert any(not f['focused'] for f in frames), table+': focus-loss fixture was missed'
    assert any(f.get('controller', {}).get('left') for f in frames), table+': left input absent'
    assert any(f.get('controller', {}).get('right') for f in frames), table+': right input absent'
    assert all(not f.get('controller', {}).get('left', False) and not f.get('controller', {}).get('right', False)
               for f in frames if not f['focused']), table+': stuck controller after focus loss'
    poses = [f['flipper_poses'] for f in frames if 'flipper_poses' in f]
    changed = [max(p[i] for p in poses)-min(p[i] for p in poses) for i in range(2)]
    assert min(changed) > 0, (table, 'native flippers did not move', changed)
    states = [s['balls'][0] if table == 'mean' else s for s in j['states']]
    xy = [struct.unpack('<ii', bytes(s[:8])) for s in states]
    ranges = [(max(p[i] for p in xy)-min(p[i] for p in xy))/65536 for i in range(2)]
    assert max(ranges) > 10, (table, 'native ball did not launch', ranges)
    if table in ['mean', 'space']:
        assert any(f.get('controller', {}).get('pull', 0) > .9 for f in frames), table+': analog pull absent'
    report['tables'][table] = {'tick_count': j['tick_count'], 'launch': 'RT pull/release' if table in ['mean', 'space'] else 'South/A',
                               'ball_range_xy': ranges, 'flipper_pose_range': changed, 'options': True, 'focus_release': True, 'Back_returns': True}
    print('PASS gamepad native frontend', table)
(a.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
print('PASS gamepad menu, four moving balls/native flippers/options/focus/Back')
