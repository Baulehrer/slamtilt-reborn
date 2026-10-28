# Pirate native preview

`tools/slampirate` starts the original Retail table with native compiled gameplay,
ball/foreground masks, three flippers, camera and original colored DMD. Enter
launches, Shift controls flippers (right also controls upper), P pauses, M mutes, Escape
opens presentation options. After Game Over, R/F1 calls the original new-game
routine while preserving the clock and RNG. R during play is a diagnostic
fresh reset. Type up to three initials, Backspace to correct, Enter to submit
when the original highscore prompt is active. The basic finite game and lamps
are verified, as are six individual Adventures. Original STIM music/SFX now play through the shared libxmp/SDL backend;
Audio options control master/music/SFX separately. Focus loss, minimization,
pause and options suspend audio and gameplay; M mutes audio only.
`--no-audio` disables playback. Complete table/physical-host acceptance remain pending. Crocodile Multiball is individually verified;
Storm/Battle/Mutiny core chains are now verified in one diagnostic campaign. In Knife Throwing, Shift moves the player,
crossing an active opponent automatically throws, and Enter throws manually.

Developer preparation, using the existing private Retail corpus and Python RE
environment:

```sh
build/venv/bin/python tools/pirate_full_tick_oracle.py
build/venv/bin/python tools/lift_pirate_step.py
cmake -S . -B build/native
cmake --build build/native -j 3
tools/slampirate
```

Original EXE/DAT hashes and prepared context hashes are checked. No original
assets, memory snapshots or generated original instruction bodies belong in
the repository. Runtime playback requires neither Wine nor Python/Unicorn.
`SLAM_PIRATE_DATA_DIR` and `SLAM_PIRATE_PREPARED` select matching private inputs.

The original full clock405234 uses absolute milliseconds, consumes5ms physics
and20ms rules/display loops, calls the original CRT RNG, and stops at405486
before x87 display interpolation. Native closure runs the original epilogue.
Interpolation is separately checked against7original x87 ball-display cases.
Bounded code generation follows reachable basic blocks and proven indirect
targets; unresolved calls stop with their original address. The compiler must
jump to each function's real entry even when its CFG contains earlier blocks
(the step653 regression found and now covers this case).

Original F1 creates the player state; phase1 is the launch/skillshot phase.
Enter calls434160 then sets46c5fc. Left/right callbacks434268/434340 receive
±1; press guards, control flags, key timers and upper-flipper routing are
preserved. Original keyboard/adapters were compared in24bounded contexts;
native behavior is additionally checked on legal original input timelines.

DMD: original40bbac initializes the16-entry nibble lookup. The full50Hz path
fills96×20 intensity bytes through46c47c. Startup404f09..404f15 chooses table
descriptor+20;406137..406190 maps those levels through four table-palette
indices. Pirate uses22/28/e0/ef. Native output is compared to original pixel
hashes each step, including score and bonus displays; UI scaling/shaders are
presentation only.

Verification:

```sh
python tools/verify_pirate_session.py
python tools/verify_pirate_full_tick.py
python tools/verify_pirate_full_tick.py --flippers
python tools/verify_pirate_full_tick.py --steps 10000
python tools/verify_pirate_complete_game.py
build/venv/bin/python tools/verify_flipper_lamp_composite.py --native build/native/table_flipper_composite_probe
build/venv/bin/python tools/validate_table_sprites_original.py
```

The latter full traces require the retained private outputs, reproducible with
`pirate_full_tick_oracle.py --flippers --output build/oracle/pirate-full-input`
and `--steps 10000 --output build/oracle/pirate-full-10000` respectively. Full
traces stay under `build/oracle/`; compact pinned fixtures live in
`analysis/traces/pirate-full-*.json`.

The10000step proof includes phase1→2 at312, physical drain→bonus at2188,
next ball at2976,100ballbytes and11time/RNGfields per step,2500DMDupdates,
native reset/replay and SDL output. It does not establish a complete game or
coverage of all Adventures, MagnaTable, four multiballs or Treasure Island.
The original RNG seed1 and synthetic isolated frontend/clock are explicit
fixture conditions. Space/Demon reuse the verified assets and parameter
interfaces; they are not advertised as playable.


Finite-game fixture preparation (same pinned context as the default launcher):

```sh
build/venv/bin/python tools/pirate_full_tick_oracle.py --steps 12000 --complete-game --lamps --output build/oracle/pirate-complete-game-lamps-ready
```

The complete fixture reaches natural three-ball bonuses, original ABC initials
and a4.5M highscore, Game Over at step9480, original F1 at9581 and a second
launch at9911. Original/native/reset/SDL match ball, timing/RNG, lifecycle,
DMD, highscore and53lamp-state hashes every step. The test uses a fresh
private profile, then loads it in a separate SDL process without rewriting it.
This is one basic legal-input game, not all Adventure/multiball coverage.

Canonical balls at46c15c+i*100 are essential: original408d78 directly writes
first-ball state46c1b4. Earlier relocated fixtures matched a split context,
so their phase3→1 transition alone did not prove next-ball reinitialization.
Those compact fixtures are archived as superseded; current baseline fixtures
use canonical state and original table/lamp/highscore startup bindings.

Lamps run the actual original408da8 command consumer and40b0b4/40b2ec raster
routines every20ms. Native lamp frames use the validated table palette/mask;
three flippers also consume their original parent lamp masks. The four-table
decoder covers216lamps/432frames, with303296original local pixels compared;
Pirate flipper masks add24actual-blit comparisons/72192pixels. Neither shared
decoding nor Pirate coverage enables unverified Space/Demon gameplay.

Interactive highscores use SDL's private preference path
`SlamTiltNative/SlamTilt/pirate-highscores.json`, independent of Mean and the
original CFG. Five validated10-byte records contain6packed-BCD score bytes,
3initials andNUL. Writes use a private temporary file and atomic replacement.
Malformed profiles are preserved and saving is disabled for that session.
Finite diagnostic runs leave profiles alone unless `--highscore-file FILE`
is explicit. `--replay FILE` accepts only recorded input actions; it never
injects ball/rule state. `--no-lamps` isolates older clock-only fixtures.


Walk the Plank now has bounded success and timeout acceptance. The directed
success route arms via the right ramp, starts at the upper-left ramp, hits five
different rope targets, rejects a repeated jackpot, collects30M, releases the
ball and returns to normal play. Total fixture score is83M including base
awards. Timeout returns without the jackpot. Original/native/reset/SDL agree
for1812/13524steps:100ball bytes,864rule bytes,11clock/RNG and15lifecycle
fields, plus DMD/lamp/highscore hashes every step.

```sh
build/venv/bin/python tools/pirate_adventure_oracle.py
build/venv/bin/python tools/lift_pirate_step.py
cmake --build build/native -j3
python tools/verify_pirate_adventure.py
tools/slampirate --replay build/oracle/pirate-adventure/success/trace.json --diagnostic-shots build/oracle/pirate-adventure/success/trace.json
```

`--diagnostic-shots` repositions only a free ball, using actual DAT switch
points and validated layer bindings. The original physics and callbacks cause
all progress and awards. Previous switch caches are invalidated when rebinding
a layer. No rule state, timers, capture state or scores are injected. This is a
directed collision/engine integration proof, not a legal-key-only trajectory.
A shared return-lane gate must be cleared by its actual switch before later
captures can release; the fixture includes that transit. Diagnostic mode is
visibly labeled and cannot save highscore profiles. Frozen shot schedules and
hashes: `analysis/traces/pirate-plank-{success,timeout}.json`. Four further Adventures now reuse these entry/trigger boundaries, as verified below.
Knife Throwing remains the next Adventure.


Swordfight, Treasure Dive, Monkey Business and Shark Attack now have seven
additional directed integration fixtures (47256steps). Swordfight tests5M
repeatable jackpots,250k bumper/target and500k upper-trap growth, then timeout.
Dive tests rate10→11, depth11..99→100 clamping, duplicate hit and30M collection;
Monkey tests a wrong target, five pieces in order1,2,3,4,0 and terminal30M;
Shark tests ramp/bumper/target speed gains and50M escape at the original raw
threshold6970. Dive/Monkey/Shark also have independent no-award timeout cases.
All match original/native/reset/SDL ball,full864-byte rule state,timing,
lifecycle,DMD,lamps andhighscores each step. Cases are independent diagnostic
trajectories; a legal-key-only all-Adventures finite game remains unverified.

```sh
build/venv/bin/python tools/pirate_modes_oracle.py
build/venv/bin/python tools/lift_pirate_step.py
cmake --build build/native -j3
python tools/verify_pirate_modes.py
```

Preview any case using the existing `--replay` and `--diagnostic-shots` flags
with `build/oracle/pirate-modes/CASE/trace.json`. Cases: `sword`,
`dive-success`, `dive-timeout`, `monkey-success`, `monkey-timeout`,
`shark-success`, `shark-timeout`. Diagnostic profiles remain nonpersistent.
The only generator extension is byte SETE for a reached DMD helper; original
callbacks are registered from actual traced dispatches. Next: first Pirate multiball.


Knife Throwing now has success/failure fixtures (11436/4212 steps). Table entry
uses the actual bumper selector/ramp/capture; throughout the video mode only
original legal keys act. All25 kills pay3M, accelerating the spawn period from
100 to25 frames. Original win/lose DMD sequences return to normal play. Success
arms Extra Ball; the upper trap does not collect it, while the right trap does,
converting the pending award into one player extra-ball credit. This does not
prove subsequent credit redemption or an all-six legal-key-only campaign.

```sh
build/venv/bin/python tools/pirate_knife_oracle.py
build/venv/bin/python tools/lift_pirate_step.py
cmake --build build/native -j3
python tools/verify_pirate_knife.py
```

Cases `knife-success`/`knife-failure` use the same replay flags and directory
as the other modes. Per-step proof adds892 video-state bytes (three exact
ranges in `analysis/pirate-knife-island.json`), alongside864 rule bytes, ball,
clock/RNG, lifecycle, coloredDMD, lamps andhighscores. CTest
`pirate_knife_native_sdl` executes the same native/reset/SDL verifier.
Original-derived graphics/code/full traces remain private under `build/`.


Crocodile Multiball now runs through two Cave locks, original cannon aiming and
physical flight, two balls,5M jackpot, Cave+1M growth,6M jackpot, ball rescue,
drain/compaction and normal-play return. A separate cannon-miss fixture proves
one lost lock and no multiball. Wrong jackpots and early firing are guarded.
SDL camera follows the lower eligible ball, keeping its existing offset/clamp.

```sh
build/venv/bin/python tools/pirate_multiball_oracle.py
build/venv/bin/python tools/lift_pirate_step.py
cmake --build build/native -j3
python tools/verify_pirate_multiball.py
```

Cases `crocodile`/`cannon-miss` use the same replay flags/directories. Optional
diagnostic `ball` index0..7 requires that selected canonical ball to be active
and free; absent index retains ball0 behavior. No waypoints occur during cannon
aiming/flight.8908 integer-oracle/native/reset/SDL steps match, including800
ball-pool bytes per step. The oracle now executes the original render-owned
integer compaction prefix408674..4086d4 and original balanced epilogue4089cb;
x87 display XY/visibility/sorting are excluded and handled by SDL. It also
completes the exact original405b6a sine-service pointer assignment after loading
the unchanged pinned snapshots. These are explicit boundary corrections, not
new physics or invented rule behavior. Full original raster equivalence and
legal-key-only/all-mode acceptance remain separate. Evidence:
`analysis/pirate-multiball-island.json`. Next: Storm3-ball chain.


Four multiballs now compose in one25780-step diagnostic campaign. It first
replays the exact6400-step frozen Crocodile prefix, then earns Storm/Battle/Mutiny
through original Cave/cannon events. Runtime Windows Retail releases3/4/5 FREE
balls (handbook lists3/3/4); the native port follows the measured binary.
Jackpots10/15/20M grow by1M at the Cave; duplicate/unlit guards and a complete
clockwise target wrap pass. Unlit hits still light the next target. Nine real
slot0 replacements compact each pool down to one, followed by normal return.

```sh
build/venv/bin/python tools/pirate_multiball_campaign_oracle.py
build/venv/bin/python tools/lift_pirate_step.py
cmake --build build/native -j3
python tools/verify_pirate_multiball_campaign.py
```

Replay case `multiball-campaign` uses the existing flags/path convention.
All800 poolbytes plus timing/lifecycle/DMD/rule/video/lamps/highscores match
original integer-oracle/native/reset/SDL each step. Original x87 render XY,
visibility and sorting remain outside that boundary; no legal-key-only/full
raster equivalence claimed. Battle upper-trap triple-JP admission remains
UNKNOWN after two bounded writer searches; no enabling flag was injected.
Surplus-lock variants and all-six-Adventures-plus-four-multiballs composition
remain separate. Evidence:`analysis/pirate-multiball-campaign-island.json`.
MagnaTable coverage follows below.


## MagnaTable

20 bounded fixtures cover all12 nominal rewards, original integer magnet
forces, all3 slots, no-lock/window-expiry guards, full intro/both-key skip,
no-award exit and normal returns.40876 original/native/reset/SDL steps exact,
including800 ball-pool bytes. Two1800-step intervals use only held keys after
entry; reward captures remain explicit diagnostic shots. Already-lit fallback
variants and key-only award completion remain unproved. Evidence:
`analysis/pirate-magna-island.json`, static byte witnesses and20 compact traces.

```sh
build/venv/bin/python tools/pirate_magna_oracle.py
build/venv/bin/python tools/lift_pirate_step.py
cmake --build build/native -j3
ctest --test-dir build/native --output-on-failure -R '^pirate_magna_native_sdl$'
```

The lightweight `pirate_magna_cases.py` shares schedules without requiring
Unicorn/Capstone for the native verifier. Full generation uses the retained
private canonical context. Treasure Island composition follows below.


## Treasure Island / composed core campaign

Treasure Island campaign: frozen25780-step four-multiball prefix→six actual Adventures→final→new Plank cycle,54760 integer-oracle/native/reset/SDL steps exact. Eight actual free balls (handbook4),15M→16M JP, duplicate/unarmed guards, target sweep and15/47/80M Super Jackpots;284M beforedrain,300M afterone further16M. Seven slot0 compactions8→1, progression reset, actualreturn-lane gate andnextPlank entry/release/completion verified. Only149 compiled instructions added; no productionphysics/render/input changes. [Evidence](../analysis/pirate-final-island.json).

```sh
build/venv/bin/python tools/pirate_final_oracle.py
build/venv/bin/python tools/lift_pirate_step.py
cmake --build build/native -j3
ctest --test-dir build/native --output-on-failure -R '^pirate_final_campaign_native_sdl$'
```

`--resume-entry` / `--resume-return` replay retained private checkpoints;
no state injection. Final return requires the real return-lane switch before
nextPlank release. Scope remains integer-only diagnostic composition, not a
legal-key-only finite game. All six flags are deliberately earned; the Retail
initializer's first-five-only predicate is separate from six-flag readiness.
Next primary: Pirate music/SFX through the existing STIM/libxmp and SDL mixer.

Pirate audio island (cached original service events; original mixer PCM excluded):

```sh
build/venv/bin/python tools/verify_pirate_audio.py --refresh
build/venv/bin/python tools/pirate_audio_pcm_oracle.py
ctest --test-dir build/native --output-on-failure -R '^pirate_audio_original_native_sdl$'
```

The fixture observes actual original service-entry registers in the existing
finite game, four-multiball/six-Adventure/final campaign and12Magna rewards.
A retained base0/0 request is explicitly delivered before step one.
Native PCM repeats exactly at44100/200 cadence; original equivalence is
bounded to60 mono resampler cases, not the full tracker/stereo mix.

Five-lock campaign: `build/venv/bin/python tools/pirate_surplus_oracle.py`,
then `build/venv/bin/python tools/lift_pirate_step.py` and rebuild.
`ctest --test-dir build/native --output-on-failure -R '^pirate_multiball_surplus_native_sdl$'`
checks all four original five-ball releases, sixth-lock guards, surplus
jackpots,16pool compactions and normal returns. Diagnostic physical waypoints;
Battle triple-JP activation remains unproved.

MagnaTable reward/eligibility reproduction:

```sh
build/venv/bin/python tools/pirate_magna_eligibility_oracle.py
build/venv/bin/python tools/pirate_magna_keys_oracle.py
ctest --test-dir build/native --output-on-failure -R '^pirate_magna_(eligibility|keys)_native_sdl$'
```

The frozen reward flight uses only actual Shift transitions after entry:
both off1352/on1472/off1592/on1712, capture5M1820, return1970.120steps=600ms;
this is a demonstrated fixture policy, not a guarantee for arbitrary entries.
Diagnostic admission remains explicitly labeled. Four earned-state fallback
chains cover already-lit mode/all6played/HoldBonus/Kickback. Search is optional:
`build/native/pirate_magna_key_search PREPARED PIRATE.DAT analysis/traces/pirate-magna-natural-both.json build/oracle/pirate-magna-key-search 300`.
Shared Nudge option bindings are currently unhandled by the Pirate frontend;
that is the next gameplay island.
