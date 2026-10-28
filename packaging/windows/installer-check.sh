#!/bin/sh
set -eu
cd /workspace
export WINEPREFIX="${SLAM_WINDOWS_INSTALLER_PREFIX:-/workspace/build/windows-release/wineprefix-installer}"
export WINEDEBUG=-all WINEARCH=win64
mkdir -p "$WINEPREFIX"
wine=/usr/lib/wine/wine64
installer="${SLAM_WINDOWS_INSTALLER:-/workspace/build/windows-release/artifacts/Slamtilt-Reborn-windows-x86_64-setup.exe}"
"$wine" "$installer" /S
/usr/lib/wine/wineserver -w
installed="$WINEPREFIX/drive_c/users/root/AppData/Local/Programs/Slamtilt Reborn"
menu="$WINEPREFIX/drive_c/users/root/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Slamtilt Reborn"
test -f "$installed/bin/slamtilt.exe"
test -f "$installed/Uninstall.exe"
test -f "$installed/LICENSES/nlohmann-json-MIT.txt"
test -f "$installed/LICENSES/ancient-BSD-2-Clause.txt"
test -f "$menu/Slamtilt Reborn.lnk"
"$wine" reg query 'HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\SlamtiltReborn' /v UninstallString
mkdir -p "$WINEPREFIX/drive_c/users/root/AppData/Roaming/SlamTiltNative/SlamTilt"
printf 'retained user data\n' > "$WINEPREFIX/drive_c/users/root/AppData/Roaming/SlamTiltNative/SlamTilt/installer-retention-probe.txt"
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy SDL_RENDER_DRIVER=software
"$wine" "$installed/bin/slamtilt.exe" --windowed --frames 3
"$wine" "$installed/Uninstall.exe" /S '_?=C:\users\root\AppData\Local\Programs\Slamtilt Reborn'
/usr/lib/wine/wineserver -w
test ! -e "$installed/bin/slamtilt.exe"
test ! -e "$menu/Slamtilt Reborn.lnk"
test -f "$WINEPREFIX/drive_c/users/root/AppData/Roaming/SlamTiltNative/SlamTilt/installer-retention-probe.txt"
if "$wine" reg query 'HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\SlamtiltReborn'; then
 echo 'Uninstaller left registry entry' >&2;exit 1
fi
echo 'PASS silent per-user unsigned install, shortcut and uninstall registry, installed launcher, silent uninstall, retained user profile'
