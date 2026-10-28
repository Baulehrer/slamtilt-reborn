Slam Tilt Native - Mean Machines RC (Linux)

1. Extract this program folder anywhere.
2. Run ./slamplay. On first start, choose your supported Windows DAT folder
   (MEAN.DAT and MAIN.DAT) or a prepared native data folder. No EXE is needed.
   The game remembers the selected data.
   Import, validation and play are native: no Python, Wine or emulator needed.
3. To choose another folder later, run ./slamplay --setup.
   Or: ./slamplay --data-dir /path/to/private-mean-data

No Python, Wine or source checkout is needed to run the prepared game.
SDL3 and libxmp are included. A compatible Linux architecture, glibc/C++ runtime,
video/audio drivers and desktop session are required; this is not a universal
Linux binary. See bundle.json for build ABI requirements and file hashes.

Shift: flippers. Enter: launch/Mode Lock. Alt/Space: nudge. R: new game.
Escape opens options; P pauses. Options include fullscreen, aspect ratio,
zoom, shaders, DMD position/colors and audio levels.
Options and highscores use the normal per-user SDL preference directory,
not this folder. Data and the program folder can remain read-only.

This is a Mean release candidate. Automated native acceptance covers all five
main modes in a finite game, 2072-game endurance and bounded Original physics
comparisons. Full Original timeline equivalence and human feel remain unproven.

Original game data belongs to its respective owners and is not supplied here.
Third-party license texts are in LICENSES/. No new license for the native port
or original game content is granted by this development package.
