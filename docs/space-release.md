# Ace of Space — Linux RC1

Start the prepared local game:

```sh
build/compat/releases/space-private-053/play-space --fullscreen
```

The asset-free distributable is `build/compat/releases/slamtilt-space-rc1.tar.gz`.
Extract and run `./slamspace`; select your supported Windows Retail directory
containing SLAMTILT.EXE and DAT/SPACE.DAT plus DAT/MAIN.DAT. Import is native;
Python, Wine, emulators and this source checkout are unnecessary. Original assets
are not included. `--setup` changes the selection; `--data DIR` overrides it;
`--check` validates it. Only the SHA-pinned Retail revision is supported.

Shift controls flippers (left also the upper flipper), Enter launches. Left Ctrl
changes the spaceship-loop direction; Right Ctrl activates an earned Magnasaver.
Escape opens display/effects/audio/controls options; P pauses. After Game Over,
F1/R starts a new game. Settings and Space highscores persist separately from
other tables. Fill/Crop and zoom support a screen-filling ball-following view;
the colored DMD can stay above the table or dock elsewhere.

RC1 is Linux x86_64, built with Debian12/GCC12 and bundled SDL3/libxmp.
Maximum required symbols: GLIBC2.34, GLIBCXX3.4.29 and CXXABI1.3.9. Actual Debian12
userspace and current-host tests pass; arbitrary distributions/GPU drivers are
not claimed. [Compatibility](../analysis/traces/space-compat-acceptance.json).

[24 bounded handbook contracts](../analysis/space-completion-contract.json),
[isolated import/package/session](../analysis/traces/space-package-acceptance.json)
and [real-time fullscreen GPU/audio](../analysis/traces/space-release-host.json)
pass. Many rule fixtures use diagnostic free-ball contacts. This is a tested
single-player RC, not an exhaustive legal-key-only/full-raster, physical-listening,
multiplayer/nudge/Tilt acceptance claim. Details: [release island](../analysis/space-release-island.json).
