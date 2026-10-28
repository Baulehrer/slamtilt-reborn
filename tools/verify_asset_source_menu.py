#!/usr/bin/env python3
"""Verify source selection/persistence UI with paths only; no Amiga-gameplay claim."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--native', type=Path, default=ROOT / 'build/native/slamtilt')
    p.add_argument('--report', type=Path, default=ROOT / 'analysis/traces/asset-source-menu.json')
    a = p.parse_args()
    with tempfile.TemporaryDirectory(prefix='source-menu-', dir=ROOT / 'build') as directory:
        work = Path(directory)
        config = work / 'frontend.json'
        data = ROOT / 'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT'
        prepared = ROOT / 'build/mean-prepared'
        old = dict(version=1, selected=0, tables=dict(mean=dict(data=str(data), prepared=str(prepared))))
        config.write_text(json.dumps(old))
        env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', XDG_DATA_HOME=str(work / 'prefs'))

        def run(events=None):
            trace = work / 'trace.json'
            args = [a.native, '--config', config, '--preview-size', '1280x800', '--frames', '2', '--trace', trace]
            if events:
                keys = work / 'keys.json'
                keys.write_text(json.dumps(dict(events=events)))
                args += ['--ui-events', keys]
            r = subprocess.run(args, env=env, text=True, capture_output=True, timeout=60)
            assert r.returncode == 0, r.stderr
            return json.loads(trace.read_text()), json.loads(config.read_text())

        trace, migrated = run()
        assert trace['asset_source'] == 'windows'
        windows = migrated['tables']['mean']['sources']['windows']
        assert windows == old['tables']['mean']
        trace, missing = run([dict(frame=0, key='F3')])
        assert trace['asset_source'] == 'windows' and missing['tables']['mean']['source'] == 'windows'
        # Duplicate paths are deliberate UI fixtures, not actual Amiga inputs.
        missing['tables']['mean']['sources']['amiga'] = dict(data=str(data), prepared=str(prepared))
        config.write_text(json.dumps(missing))
        trace, switched = run([dict(frame=0, key='F3')])
        assert trace['asset_source'] == 'amiga' and switched['tables']['mean']['source'] == 'amiga'
        assert switched['tables']['mean']['sources']['windows'] == windows
        trace, restored = run()
        assert trace['asset_source'] == 'amiga' and restored['tables']['mean']['source'] == 'amiga'
        trace, _ = run([dict(frame=0, key='F3')])
        assert trace['asset_source'] == 'windows'
        trace, _ = run([dict(frame=0, type='click', x=180, y=718)])
        assert trace['asset_source'] == 'amiga'
        trace, final = run([dict(frame=0, type='click', x=90, y=718)])
        assert trace['asset_source'] == 'windows' and final['tables']['mean']['sources']['windows'] == windows
    a.report.write_text(json.dumps(dict(status='VERIFIED_SOURCE_UI', legacy_windows_migration=True,
                       both_sources_retained=True, keyboard_F3=True, mouse_chips=True,
                       selected_source_persisted=True, unavailable_source_not_selected=True,
                       scope='Source-selection UI and typed configuration only; duplicate PC paths serve as UI fixtures. Actual ADF gameplay and source assets require separate integration proof.'), indent=2) + '\n')
    print('PC/Amiga source UI migration/F3/mouse/persistence PASS')


if __name__ == '__main__':
    main()
