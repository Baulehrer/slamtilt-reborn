# The Pirate — Linux RC1

Start with:

```sh
build/compat/releases/slamtilt-pirate-rc1/slampirate
```

The native chooser imports your supported Windows Retail EXE, PIRATE.DAT and
MAIN.DAT. Use `--setup` to choose another directory. Existing private prepared
data can be selected with `--data /path/to/data`.

Shift controls the three flippers; Enter launches; Left Ctrl activates an earned
Magnasaver. Alt/Space nudge. Escape opens display, shaders, DMD, audio and controls.
After Game Over, F1/R starts another game. Scores and settings persist separately
from Mean Machines.

The program directory and `.tar.gz` archive are relocatable and contain no
original assets. They bundle SDL3/libxmp and were built with Debian12/GCC12.
Actual Debian12 userspace and current-host tests are
recorded in [compatibility acceptance](../analysis/traces/pirate-rc1-compat.json).

All handbook rule groups have bounded Original/native evidence, including
left/right-only automatic Knife victory, four multiballs, six Adventures and
Treasure Island. [Acceptance map](../analysis/pirate-completion-contract.json).
Many feature tests use explicit diagnostic free-ball contacts; they do not claim
an all-features keyboard-only playthrough or universal original-raster equivalence.

RC1 also passes the [real-time fullscreen game](../analysis/traces/pirate-rc1-realtime.json):
15,600 steps, original state/audio agreement, Game Over, initials and persistent
score reload. Twelve current-host window/fullscreen input/audio event tests pass.
