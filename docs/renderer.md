# Native display island

Status: IMPLEMENTED and verified against source asset bytes; no original screenshot comparison yet.

`src/assets/windows_table.cpp` expands a tested 320×600 indexed DAT playfield into RGBA. `src/renderer/main.cpp` uploads it once to an SDL3 texture, renders a 320×400 viewport with nearest sampling and lets the user scroll over the 200-row range. Resizing letterboxes the logical viewport. Timing uses elapsed SDL milliseconds for manual camera input only; it is not a recovered game simulation tick.

Build and run:

```sh
cmake -S . -B build/native -DCMAKE_BUILD_TYPE=Debug
cmake --build build/native -j4
ctest --test-dir build/native --output-on-failure
tools/slamview 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT'
```

Replace MEAN with PIRATE, SPACE or DEMON. Original Amiga data also works after container extraction:

```sh
python tools/slamdecode.py ORIGINAL/Mean.Raw build/Mean.Raw
tools/slamview build/Mean.Raw --amiga
```

`src/assets/amiga_table.cpp` reads the decoded section directory and converts eight row-interleaved bitplanes and the original RGB palette into the same RGBA representation. The directory is produced by corpus extraction; any user DAT with a supported layout can be passed directly.

Verification: native palette/extent/rejection tests; four original DAT and four decoded Amiga RAW exports;1536000 RGB pixels independently compared with zero differences; malformed input cases; dummy-video smoke and actual desktop SDL window smoke. Independent full-pixel comparison is recorded in [verification.md](verification.md) when available. `build/{MEAN,PIRATE,SPACE,DEMON}.bmp` are generated local artifacts, excluded from source.

Milestones1 and2 are achieved. Milestone3 is partial: manual viewport scrolling works; original ball-follow camera behavior remains unknown. Sprites, lamp animation, DMD runtime, ball simulation, flippers and collision are not implemented. Stop low-level DirectDraw/blitter translation for this island and focus on object/physics data next.
