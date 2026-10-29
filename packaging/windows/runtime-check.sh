#!/bin/sh
set -eu
cd /workspace
export WINEDEBUG=-all WINEPREFIX="${SLAM_WINDOWS_RUNTIME_PREFIX:-/workspace/build/windows-release/wineprefix}"
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
wine=/usr/lib/wine/wine64
app="${SLAM_WINDOWS_APP:-build/windows-release/artifacts/Slamtilt-Reborn-windows-x86_64/bin/slamtilt.exe}"
runtime_out="${SLAM_WINDOWS_RUNTIME_OUT:-build/windows-release}"
export SLAM_WINDOWS_RUNTIME_OUT="$runtime_out"
mkdir -p "$runtime_out"
state=$(python3 -c 'from pathlib import Path; import sys; print("Z:"+str(Path(sys.argv[1]).resolve()).replace("/",chr(92)))' "$runtime_out")
dat='Z:\workspace\build\corpus\win95\_dokumente\Slam_Tilt_Win_RIP_EN\Game Files\SLAMTILT\DAT'
"$wine" "$app" --windowed --config "$state\preferences.json" --import "$dat" --frames 3 --trace "$state\first-import.json"
"$wine" "$app" --windowed --config "$state\preferences.json" --exercise-all --child-frames 16 --frames 1000 --trace "$state\table-cycle.json"
python3 - <<'PY'
import json,os
from pathlib import Path
p=Path(os.environ['SLAM_WINDOWS_RUNTIME_OUT'])
a=json.loads((p/'first-import.json').read_text());b=json.loads((p/'table-cycle.json').read_text())
print(json.dumps({'import_events':a['events'],'cycle_events':b['events']},indent=2))
assert sum(e.get('event')=='launched' for e in b['events'])==4
assert sum(e.get('event')=='returned' and e.get('exit_code')==0 for e in b['events'])==4,b['events']
PY
