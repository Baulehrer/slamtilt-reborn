#!/bin/sh
set -eu
cd /workspace
prefix=/opt/windows/SDL3-3.4.18/x86_64-w64-mingw32
x86_64-w64-mingw32-g++ -std=c++17 -O2 -Isrc -I"$prefix/include" -I/opt/windows/prefix/include packaging/windows/smoke.cpp src/frontend/pirate_highscores.cpp -L"$prefix/lib" -lSDL3 -static-libstdc++ -static-libgcc -o build/windows-release/native/windows_smoke.exe
cp "$prefix/bin/SDL3.dll" build/windows-release/native/
cp /opt/windows/prefix/bin/libxmp.dll build/windows-release/native/
cp /usr/x86_64-w64-mingw32/lib/libwinpthread-1.dll build/windows-release/native/
export WINEDEBUG=-all
export WINEPREFIX=/workspace/build/windows-release/wineprefix
mkdir -p "$WINEPREFIX"
/usr/lib/wine/wine64 build/windows-release/native/windows_smoke.exe
python3 tools/slamtilt-windows-pack --output build/windows-release/artifacts
