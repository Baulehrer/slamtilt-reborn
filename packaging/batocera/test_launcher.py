#!/usr/bin/env python3
"""Exercise launcher argv/environment and transactional first import with real shell execution."""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

LAUNCHER = Path(__file__).with_name('Slamtilt-Reborn.sh').resolve()
STUB = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
with open(os.environ['STUB_LOG'],'a') as f:
 f.write(json.dumps({'args':sys.argv[1:],'mapping':os.environ.get('SDL_GAMECONTROLLERCONFIG_FILE'),'inline':os.environ.get('SDL_GAMECONTROLLERCONFIG'),'xdg':os.environ.get('XDG_DATA_HOME')})+'\\n')
if '--import' in sys.argv:
 if os.environ.get('STUB_IMPORT_FAIL'):sys.exit(7)
 p=Path(sys.argv[sys.argv.index('--config')+1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{"tables":{"mean":{"data":"private"}}}')
else:sys.exit(int(os.environ.get('STUB_GAME_EXIT','0')))
'''


def main():
    checks = []
    with tempfile.TemporaryDirectory(prefix='reborn-batocera-') as tmp:
        base = Path(tmp)
        home = base / 'runtime with spaces'
        home.mkdir()
        app = home / 'slamtilt-reborn'
        app.write_text(STUB)
        app.chmod(0o755)
        data = base / 'original data with spaces'
        data.mkdir()
        config = base / 'profile with spaces/frontend.json'
        marker = Path(str(config) + '.batocera-imported')
        log = base / 'calls.jsonl'
        env = dict(os.environ, SLAMTILT_HOME=str(home), SLAMTILT_DATA=str(data),
                   SLAMTILT_CONFIG=str(config), XDG_DATA_HOME=str(base / 'saves'),
                   XDG_CONFIG_HOME=str(base / 'configs'), XDG_CACHE_HOME=str(base / 'cache'),
                   STUB_LOG=str(log))
        for key in ['SDL_GAMECONTROLLERCONFIG_FILE', 'SDL_GAMECONTROLLERCONFIG',
                    'SLAMTILT_GAMEPAD_DB', 'SLAMTILT_REIMPORT', 'STUB_IMPORT_FAIL', 'STUB_GAME_EXIT']:
            env.pop(key, None)

        def run(extra=None, args=(), expected=0):
            log.write_text('')
            result = subprocess.run(['bash', str(LAUNCHER), *args], env=dict(env, **(extra or {})),
                                    text=True, capture_output=True, timeout=15)
            assert result.returncode == expected, (result.returncode, result.stderr)
            return [json.loads(line) for line in log.read_text().splitlines()]

        calls = run(args=('--windowed', '--frames', '3'))
        assert len(calls) == 2
        assert calls[0]['args'] == ['--config', str(config), '--import', str(data), '--windowed', '--frames', '1']
        assert calls[1]['args'] == ['--config', str(config), '--windowed', '--frames', '3']
        assert marker.read_text() == str(data) + '\n'
        checks.append('first import uses native CLI, preserves quoted paths and forwards user argv')
        assert len(run()) == 1
        checks.append('successful import is not repeated')
        marker.unlink()
        original = config.read_bytes()
        assert len(run()) == 1 and config.read_bytes() == original and not marker.exists()
        checks.append('existing partial configuration is preserved without marker')
        assert len(run({'SLAMTILT_REIMPORT': '1'})) == 2
        checks.append('explicit refresh imports again')
        config.unlink()
        marker.unlink()
        assert len(run({'STUB_IMPORT_FAIL': '1'}, expected=7)) == 1
        assert not marker.exists() and not config.exists()
        assert len(run()) == 2
        checks.append('failed import stops launch, writes no marker and retries next time')
        config.unlink()
        assert len(run()) == 2
        checks.append('missing configuration restores import despite existing marker')
        config.write_text('')
        assert len(run()) == 2
        checks.append('empty configuration restores import')
        assert len(run({'SLAMTILT_DATA': ''})) == 1
        assert len(run({'SLAMTILT_DATA': str(base / 'absent')})) == 1
        checks.append('disabled or absent source opens menu without attempting import')
        changed = base / 'other original set'
        changed.mkdir()
        assert len(run({'SLAMTILT_DATA': str(changed)})) == 2
        checks.append('changed source with launcher marker refreshes import')
        db = home / 'gamecontrollerdb.txt'
        db.write_text('test mapping\n')
        assert run({'SDL_GAMECONTROLLERCONFIG': 'inline mapping'})[-1]['mapping'] == str(db)
        assert run({'SDL_GAMECONTROLLERCONFIG': 'inline mapping'})[-1]['inline'] == 'inline mapping'
        configured = base / 'configs/slamtilt/gamecontrollerdb.txt'
        configured.parent.mkdir(parents=True)
        configured.write_text('configured mapping\n')
        assert run()[-1]['mapping'] == str(configured)
        assert run({'SDL_GAMECONTROLLERCONFIG_FILE': 'inherited mapping'})[-1]['mapping'] == 'inherited mapping'
        explicit = base / 'explicit mapping.txt'
        explicit.write_text('explicit\n')
        assert run({'SLAMTILT_GAMEPAD_DB': str(explicit)})[-1]['mapping'] == str(explicit)
        assert run({'SLAMTILT_GAMEPAD_DB': str(base / 'missing')}, expected=2) == []
        checks.append('SDL mapping precedence and unreadable explicit mapping are handled')
        alternate = base / 'alternate frontend.json'
        calls = run(args=('--config', str(alternate)))
        assert len(calls) == 2 and calls[0]['args'][1] == str(alternate)
        assert alternate.exists() and Path(str(alternate) + '.batocera-imported').exists()
        assert run(args=('--config',), expected=2) == []
        checks.append('native --config override controls both first import and interactive launch')
        explicit_source = base / 'explicit source'
        explicit_source.mkdir()
        assert len(run(args=('--import', str(explicit_source)))) == 1
        checks.append('explicit native --import bypasses automatic preflight')
        assert len(run({'STUB_GAME_EXIT': '9'}, expected=9)) == 1
        checks.append('interactive game exit code propagates')
        app.unlink()
        assert run(expected=2) == []
        checks.append('missing executable fails clearly')
    print(json.dumps({'status': 'PASS', 'launcher_sha256': hashlib.sha256(LAUNCHER.read_bytes()).hexdigest(), 'checks': checks, 'physical_hardware_verified': False}, indent=2))


if __name__ == '__main__':
    main()
