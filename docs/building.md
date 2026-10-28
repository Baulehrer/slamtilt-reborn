# Building the public source

Install a C++17 compiler, CMake, Python3, SDL3 (3.4+ recommended), nlohmann/json and libxmp development files. `glslc` is optional for advanced GPU effects.

```sh
cmake -S . -B out/native -DCMAKE_BUILD_TYPE=Release
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
