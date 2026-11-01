# Building the public source

Install a C++17 compiler, CMake, Python3, SDL3 (3.4+ recommended), nlohmann/json and libxmp development files. `glslc` is optional for advanced GPU effects.

For the corrected Slam Tilt STIM music timing, use the pinned libxmp source checkout at `build/libxmp` and build a private patched copy before configuring the port:

```sh
python3 tools/prepare_stim_libxmp.py --source build/libxmp --output build/libxmp-stim-v11
cmake -S build/libxmp-stim-v11 -B build/libxmp-stim-v11-build -DBUILD_SHARED=ON -DBUILD_STATIC=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build build/libxmp-stim-v11-build -j2
```

Set `SLAM_STIM_CHANNEL_HISTORY=ON` only when linking the pinned patch; unpatched libraries retain the safe restart behavior. The patch is limited to STIM. A system libxmp without it still plays music but does not have the timing correction. For an existing CMake build, explicitly set `-DXMP_INCLUDE_DIR=$PWD/build/libxmp-stim-v11/include -DXMP_LIBRARY=$PWD/build/libxmp-stim-v11-build/libxmp.so` when reconfiguring; otherwise a cached older library may remain selected.

```sh
cmake -S . -B out/native -DCMAKE_BUILD_TYPE=Release -DSLAM_STIM_CHANNEL_HISTORY=ON
cmake --build out/native --target slamtilt slamview slamslice -j2
out/native/slamtilt
```

Six generated static C++ engine islands are intentionally checked in under `build/generated`. They are source files, not game assets; preserve that directory and use `out/` for compiler output.

The runtime imports your own Windows DATs or supported five-ADF set. No original game executable or emulator is needed for Windows DAT import.

Public tests without original game data:

```sh
cmake --build out/native --target port_options_test frontend_runtime_test pirate_highscores_test -j2
ctest --test-dir out/native -R '^(port_options|frontend_runtime_safety|pirate_highscore_storage)$' --output-on-failure
```

Most other RE/oracle tests require private original data and traces, intentionally excluded from this repository. Platform distribution recipes are in [packaging](../packaging/README.md).
