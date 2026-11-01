# Current status — 2026-10-29

## Trace-derived combined audio — 2026-11-01

- Four new original-mixer tests match over 2,646 stereo frames: 13 Mean
  display-table requests, all seven distinct same-step Pirate SFX pairs, the
  one same-step Demon SFX pair, and one Space plus one Demon trace-derived
  music/SFX pair. [Results](../analysis/audio-trace-mix-v1.4.json).
- The [trace inventory](../analysis/audio-trace-coverage-v1.4.json) records
  request coincidences, not audio overlap: Mean lacks a comparable complete
  original event stream. Mix tests use reconstructed voice/tracker states;
  true cadence, earlier voices, full-game and Amiga/device parity remain open.

## Deferred music after an upper cue — 2026-11-01

- A pending service 84 now inherits the live upper-cue voices when service 88
  finishes. Previously a controlled Mean transition differed in 356 stereo
  frames at the transition tick.
- Ten controlled comparisons across all four Windows Retail tables match
  bit-for-bit for 512 ticks each, including the previously failing Mean case
  and the 88/84 request pair observed together in Pirate's retained
  `nudge-tilt-knife` trace. [Results](../analysis/stim-pcm-deferred-scheduler.json).
- The Pirate requests come from a retained diagnostic game trace, but its
  playback context and tick timing are reconstructed; whole-game, physical
  audio output and Amiga equivalence remain unverified.

## Mean tracker effect 8 — 2026-11-01

- The previously discrepant bank transition used instrument 29 without a new
  note. Retail applies its new volume on the first tick; the native mixer kept
  the preceding volume. The pinned STIM patch corrects that row-specific case.
- All 14 targeted Mean transitions with effect-8 rows match the Windows Retail
  tracker/mixer for 128 ticks. All 54 selected scheduler cases now match for
  512 ticks; the previously disabled tests are restored. [Effect-8 results](../analysis/stim-pcm-v11-mean-effect8.json), [scheduler](../analysis/stim-pcm-v11-scheduler.json).
- Windows, ARM64 and WebAssembly libraries and the changed native audio sources
  cross-compile. This is not a device-playback or complete-game parity test.

## Historical STIM bank switching and scheduler — 2026-11-01

- The pinned v11 STIM patch carries compatible voices and channel history
  across banks. The sequencer also restores the saved tracker pattern after
  service 88 ends; service 84 remains active until an explicit stop.
- 600 synthetic 32-tick bank/service transitions are bit-exact against the
  authenticated Windows Retail routines across all four tables. Nine longer
  base transitions and four two-switch chains also match for 512 ticks.
- Scheduler comparison: 52/54 synthetic 512-tick cases match. Both differences
  are the same Mean bank 1 → 0 transition after 200 warm ticks: 866 of 451,584
  stereo frames differed at its first tick. The two strict tests were subsequently
  fixed and restored; see the current status above.
- Full playback, natural gameplay event reachability, device timing, and Amiga
  equivalence remain unverified. No release has been made from this work.

## Historical STIM v9 same-bank transitions — 2026-11-01

- A new four-table Original/native combined mixer fixture matches 2,646 stereo
  frames of tracker plus two simultaneous SFX at three chunk sizes. The
  simultaneous starts are synthetic, not a live gameplay trace.

- Pinned v9 STIM and the shared music sequencer preserve channel history for
  repeated same-bank services 90/84/88. Stock libxmp keeps the previous restart
  behavior when `SLAM_STIM_CHANNEL_HISTORY` is off.
- All eight previously unresolved Mean targets match for 32 and 512 ticks
  when primed with one verified tracker/mixer tick; 15 of 16 two-prime cases
  match, with the remaining adapted original fault explicitly retained.
  Same-order restarts and 48 sampled transitions on the other tables match
  for 32 ticks. [Evidence](../analysis/stim-pcm-v9-transitions.json).
- Cold-start regression: 555 of 563 positions match for 32 ticks; the eight
  original fresh-state faults remain unchanged. [Survey](../analysis/stim-pcm-v9-all-orders-survey.json).
- Validation: 24 targeted audio/game tests, three cross-table transition tests
  and all 42 sound/audio tests pass. Windows, ARM64 and WebAssembly library
  and changed audio sources cross-compile; device playback is not covered.
- Still open: real-game transition reachability and timing, cross-bank or
  overlapping services, complete-song/SFX/device and Amiga equivalence.

## STIM Retail PCM update — 2026-11-01

- At the v6 checkpoint, the 33 previously
  differing short samples now match; all 30 selected bank/order starts match
  Retail for 2,048 manually clocked ticks each. In the all-order 32-tick
  survey, 555 starts match and eight Mean starts fault in the original adapter
  without an earlier channel period. [Evidence](../analysis/stim-pcm-v6-all-orders-survey.json),
  [long survey](../analysis/stim-pcm-v6-long-survey.json).
- A synthetic Pirate music plus two-SFX case matches exactly; this does not
  establish complete live event scheduling, output-device or Amiga parity.
- Validation: 26 tracker/audio tests and 42 sound/audio tests passed; the v6
  library also cross-compiles for Windows, Linux ARM64 and WebAssembly. These
  are build and bounded-oracle checks, not physical-device acceptance.
- Next: recover preceding state for those eight starts and compare complete
  live game audio transitions with the original.

## Dynamic tracker/mixer PCM — 2026-11-01 (bounded)

- `0x401838` updates each voice's sample, period and volume; retaining the four live voices and rebuilding their list permits 512 manually clocked Retail tracker/mixer ticks per table, including voice changes. The first five windows match the earlier fixed-voice oracle exactly. Full-window Original/native PCM correlations: Mean 0.999512, Pirate 0.999641, Space 0.999703, Demon 0.999793. Individual samples still differ. [Evidence](verification/stim-dynamic-pcm-2026-11-01.json).
- Isolated 67% and 2/3 per-voice gain experiments increased overall RMS error for all four tested starts and gave mixed exact-sample results; 66% remains in use. [Evidence](verification/stim-volume-experiment-2026-11-01.json).
- These use adapted 50 Hz timing, manually linked voices and no SFX or real device; they do not prove full-song or Amiga PCM parity.

## STIM period-domain vibrato — 2026-11-01 (bounded)

- The local STIM-only libxmp patch keeps vibrato in the period domain instead of round-tripping through a pitch-bend conversion when finetune and arpeggio are absent. In four manually clocked 2,000-tick starts, all 29,598 compared nonzero period/volume channel fields now match the SHA-verified Retail tracker exactly. [Direct execution](verification/stim-vibrato-direct-original-2026-11-01.json).
- Against the previous local patch, 199 startup period fields and 221 fields in 32 selected 256-tick order samples improve, with no observed regressions. Eight relevant tests pass, plus four five-second synthetic loop tests; Windows, ARM64 and WebAssembly library cross-builds succeed. [Survey](verification/stim-vibrato-direct-survey-2026-11-01.json).
- The published v1.2 packages are unchanged. These are bounded period-field comparisons with an adapted clock, not full-song PCM, full Original scheduling or physical playback proof.

## STIM vibrato row boundary — 2026-10-31 (bounded)

- In the pinned Retail tracker, an existing vibrato without a new note retains the preceding period on the first tick of a continued row. The local STIM patch now reproduces this under those conditions. [Original comparison](verification/stim-vibrato-hold-original-2026-10-31.json).
- Four 2,000-tick startup comparisons improve three Mean and 15 Pirate channel periods with no observed regression; another 32 selected 256-tick order samples improve 12 values with no observed regression. Seven relevant tests pass. Windows, ARM64 and WebAssembly library cross-builds succeed. [Survey](verification/stim-vibrato-hold-survey-2026-10-31.json).
- The published v1.2 packages are unchanged. Full original timing, effects, audible PCM and all music paths remain unverified.

## STIM pitch-down correction — 2026-10-31 (bounded)

- Remaining nonzero period-field differences in the first 2,000 manually clocked ticks occur with effect 04/06 (vibrato) on Mean/Pirate and effect 02/01 (pitch down) on Demon. [Baseline](verification/stim-sequence-periods-2026-10-31.json).
- A STIM-only correction rounds the final period for pitch-down slides with zero finetune, no vibrato and no arpeggio. Original comparison improves Demon from 6,765 to 7,066 exact values out of 7,066; no observed regressions in those four startup sequences or 32 additional 256-tick order samples. [Original](verification/stim-pitch-slide-original-2026-10-31.json), [survey](verification/stim-pitch-slide-survey-2026-10-31.json).
- Native executables use the correction locally; Windows, ARM64 and WebAssembly libxmp cross-builds pass. Published v1.2 packages are unchanged. Full Original scheduling, physical output and all effect paths remain unverified.

## STIM periods beyond startup — 2026-10-31 (bounded)

- Executed 2,000 manually clocked original tracker ticks and compared channel fields with nonzero period and volume for each table. Exact Q12 matches: Mean 7,326/7,354; Pirate 7,072/7,245; Space 7,933/7,933; Demon 6,765/7,066. This observes tracker fields, not complete audio, original scheduling or audibility. [Evidence](verification/stim-sequence-periods-2026-10-31.json).
- An isolated integer-rounding experiment increases exact matches (Mean 7,351, Pirate 7,170, Demon 7,066) but makes 71 Pirate and one Mean individual periods less accurate. It is not enabled. [Comparison](verification/stim-period-rounding-2026-10-31.json).

## STIM timing integrated — 2026-10-31 (bounded)

- The port's local native build and four platform packaging paths now use the same pinned, privately patched libxmp source. The correction applies only to STIM. The pinned source files are checked before patching. [Patch](../patches/libxmp-stim-rate.patch), [preparation](../tools/prepare_stim_libxmp.py).
- Four Original startup comparisons exceed 0.99 correlation; ten-second native playback for all four tables is deterministic across chunk sizes. Pirate combined music/two-SFX correlation improves from 0.987281 to 0.999925 in the adapted first-tick comparison. A non-STIM MOD is bit-identical across 88,200 frames. [Startup](verification/stim-original-quality-2026-10-31.json), [long play](verification/stim-long-play-2026-10-31.json), [Pirate](verification/pirate-combined-stim-fixed-2026-10-31.json), [isolation](verification/stim-non-stim-isolation-2026-10-31.json).
- Synthetic five-second loops at four notes and five manually clocked startup windows per table pass. Effects, finetune, the full Original scheduler, exact samples and physical device playback remain unverified.

## Version 1.2 candidate and STIM timing — 2026-10-31

- The first STIM-only experiment drifted in a five-second Original resampler comparison. Preserving the Original's integer frequency division before the output-rate division removes that observed drift in four synthetic notes: each five-second window correlates above 0.99. Five manually clocked startup windows on each table also pass. [Startup](verification/tracker-stim-rate-five-tick-2026-10-31.json), [loop example](verification/tracker-stim-rate-loop-2026-10-31.json). This variant has since been integrated as described above; effects, finetune, full scheduling and actual device output are unverified.
- Local Linux, Windows, ARM64 and browser 1.2 candidate packages were built with the **unmodified** libxmp. They do not contain the experiment. Linux AppImage first import and all four child launches passed; browser offline acceptance passed 19 checks; Wine installer and QEMU smoke were exercised. Physical Windows and ARM64 remain unverified.
- Platform builds containing the correction supersede those initial candidates; effects and longer Original audio paths remain to be validated.

## Tracker period experiment — 2026-10-31 (experimental)

- A private libxmp variant combines floor sample indexing, normal-tuning ProTracker integer periods, and preservation of those periods for zero pitch bend. For the adapted 882-frame first tick, Pirate channel 1 reports the Original's period 190; mixed PCM correlation rises from 0.979677 to 0.999996 (32 exact frames). Mean 0.999935, Space 0.999876, Demon 0.999999. [Evidence](verification/tracker-period-experiment-2026-10-31.json).
- This experimental global MODRNG modification is not used by the port. Effects, finetune, loops, later music and device playback are not established; this is not complete PCM parity. CTest `tracker_period_experiment` reproduces the bounded comparison.

## Four-table combined audio and reachability — 2026-10-31 (bounded)

- Mean: 12 additional original mode callback scenarios access none of the three unresolved descriptors; synthetic state and adapted services prevent a reachability conclusion. [Evidence](verification/mean-sfx-mode-access-2026-10-31.json).
- Pirate: with identical original music, a synthetic two-SFX combination matches original PCM exactly. With the native tracker, 867/882 frames differ (correlation 0.987281); combined playback is therefore not bit-exact. [Evidence](verification/pirate-combined-audio-2026-10-31.json).
- Space: the original consumes descriptor period/volume at queue consumption, not request time; synthetic mutations affect all ten profiles. Seven original replays contain no watched writes across 70,176 ticks; these replays do not run the consumer. [Timing](verification/space-sfx-queue-timing-2026-10-31.json), [writes](verification/space-sfx-mutations-2026-10-31.json).
- Demon: three original scenarios cover 131 requests / 17,292 ticks; period and volume match native constants for ten of 14 descriptors at request time. [Evidence](verification/demon-sfx-descriptor-state-2026-10-31.json).
- Complete natural reachability, actual device playback and full original mixed PCM remain unproven. Pirate tracker mismatch is observed, not merely hypothetical.

## Four-table sound follow-up — 2026-10-31 (bounded)

- Mean: 1,036 original contact replays with 116 adapted sound calls show no access to the three unresolved descriptors; positive controls work. [Evidence](verification/mean-sfx-contact-access-2026-10-31.json).
- Pirate: two simultaneous Original-trace SFX match native mixed PCM for four output lengths, starting with free voices. [Evidence](verification/pirate-overlap-pcm-2026-10-31.json).
- Space: seven bounded Original replays cover all ten SFX descriptors and 124 requests; period and volume at the request boundary match native constants. Later queue-time mutations remain unknown. [Evidence](verification/space-sfx-descriptor-state-2026-10-31.json).
- Demon: all 12 retained Clock award scenarios match native audio requests over 40,048 steps; diagnostic contacts and the separately corrected historical startup are used. [Evidence](verification/demon-clock-audio-2026-10-31.json).
- These results do not establish complete gameplay reachability, physical playback, or final music-plus-SFX output.

## Remaining Mean SFX references — 2026-10-31 (bounded)

- Memory watchpoints on 16 original Demo display callbacks (1,902 frames) and eight bounded original/native minigame scenarios found no access to the three descriptors. Known descriptor accesses and four minigame sound requests provide positive controls. States are synthetic and services adapted; natural reachability remains unknown. [Display](verification/mean-sfx-access-2026-10-31.json), [minigame](verification/mean-sfx-minigame-access-2026-10-31.json).
- Scanned all 108 byte addresses inside the three remaining descriptors in pinned Demo, Retail and Fix PE images: no exact 32-bit address bytes. The Fix records are identical to Retail at new addresses `0x46506c/0x465090/0x4650b4`. Eight pinned Windows DAT files contain one coincidental candidate inside Mean sample 26 PCM. Computed pointers, runtime construction, compression and Amiga logic remain unknown; none of the three is proven unreachable. [Evidence](verification/mean-sfx-reference-surfaces-2026-10-31.json).

## Sound effect descriptor audit — 2026-10-31 (partial)

- All 15 Pirate, 10 Space and 14 Demon native profiles match the selected pinned Retail descriptors and resolved DAT slices. Their one-voice original/native PCM tests cover 156 cases. Mean adds 13 formerly unbound Demo-addressed sample profiles; all 24 now have 96 direct Demo/native PCM comparisons using real DAT samples, and the 17 selected Retail descriptors have byte-identical native aliases. [Audit](verification/sfx-descriptor-audit-2026-10-31.json), [Mean PCM](verification/mean-sample-pcm-2026-10-31.json).
- Six original Retail sound sequences execute 16 sound requests with dynamic period/volume. The mixer matches Original for all 16×2 PCM cases plus a synthetic sweep of 65 volume levels. These sequences now route through eight corresponding Mean display callbacks; bounded Demo/Retail callback, shared-cursor interruption and duplicate-queue mutation checks pass. One 40,380-step legal-input replay produced 42 dynamic requests across four descriptors; other paths remain unverified. [Sequences](verification/mean-retail-sfx-sequences-2026-10-31.json), [dynamic PCM](verification/mean-dynamic-sfx-pcm-2026-10-31.json), [callbacks](verification/mean-display-sfx-2026-10-31.json).
- Imported Amiga adapter Mean DAT has 23/24 identical native sample slices versus Retail; existing descriptor `0x437cf0` differs. All 13 newly bound shared-sample slices match in this adapter. This is not Amiga event/timing parity.
- Expanded SHA-identified retained Original event fixtures exercise all 15 selected Pirate and 10 Space descriptors, and 13/14 Demon descriptors. Six additional Original/SDL replays cover the newly located Space/Demon events; the Pirate knife replay covers the final two Pirate descriptors. The remaining Demon descriptor `0x463308` matches Original/native in 100 controlled callback states, including 30 emissions. This is bounded event coverage, not proof of natural reachability or every callsite. [Space/Demon replays](verification/retail-sfx-replays-2026-10-31.json), [Pirate replay](verification/pirate-sfx-replay-2026-10-31.json), [Demon callback](verification/demon-sfx-callback-2026-10-31.json).
- The complete retained 81-case Pirate event/audio regression also passed again (662,728 steps), along with seven additional Space audio cases (80,328 steps), the six targeted Space/Demon replays and the two Mean minigame sound sequences. For Mean, 14/17 Retail descriptors occur in the bounded display/minigame checks; the remaining three have no direct pointer bytes in either pinned PE, which does not rule out computed or indirect references. [Space acceptance](verification/space-sfx-acceptance-2026-10-31.json), [bounded search](verification/mean-remaining-sfx-static-2026-10-31.json).

## Pirate tracker periods and Retail loops — 2026-10-31

- Pirate startup: original channel 1 uses period 190; libxmp reports 780911/4096 ≈ 190.65. Two other channels use period 214 in both and correlate >0.99999 with the independent original-floor sample model using the experimental floor library. The period mismatch is a strong candidate for the remaining channel-1 difference, not proof of complete causality. [Evidence](verification/pirate-tracker-channels-2026-10-31.json).
- Original `0x44cc00` matches a Q32 floor/modulo model across four synthetic forward-loop configurations, 4,096 frames and three chunk sizes each. This does not test libxmp loop boundaries or real game cadence. [Loop evidence](verification/retail-loop-resampler-2026-10-31.json).

## Floor-mixer experiment — 2026-10-31

- A private libxmp build that floors nearest sample positions improved the bounded Mean startup PCM correlation from 0.641 to 0.9999, but Pirate fell from 0.9797 to 0.9678 at zero offset; aligning two frames raises Pirate to 0.9796. Space and Demon improved. These are 882-frame comparisons with adapted original startup, not whole-song listening tests. The global library modification is not enabled in the port. [Evidence](verification/tracker-floor-experiment-2026-10-31.json).

## Retail tracker mix — 2026-10-31 (bounded)

- The game sequencer now uses mono, nearest-sample interpolation and an approximate 66% libxmp level. The independent `StimPlayer` default remains unchanged. Retail `0x44b560` / `0x44c918` / `0x44cd4d` combine up to six voices in mono with nearest-sample reads; executable tests cover one, four and six synthetic voices. [Mixer evidence](verification/retail-game-mixer-2026-10-31.json).
- The first tracker tick of all four Retail tables was executed from original code and DATs with explicitly adapted startup, full volume and an 882-frame window. Native/original RMS ratio is 0.995–1.013; samples still differ, especially Mean. Original truncates fractional sample positions while libxmp nearest rounds them; native interpolation is therefore still approximate. This does not establish original startup, live cadence, complete music or Amiga playback parity. [Four-table comparison](verification/retail-tracker-native-2026-10-31.json).

## Retail final mixer — 2026-10-31 (bounded)

- Signed 16-bit stereo original `0x44b8bc` / `0x44bca9` wraps on overflow; the native gain helper and production SFX mixer clamp. Direct original/native tests cover 1,032 synthetic stereo frames and 768 single-voice frames, including all signed 8-bit sample values. [Evidence](verification/retail-final-mix-2026-10-31.json).
- At the explicitly tested six-voice/full-volume sample gain, six worst-case sample terms remain within signed 16-bit range. The later normal-game mixer test above uses the shared mono buffer, so the separate-buffer synthetic overflow case is not established as a real game path. Live input levels and device timing remain unverified.

## Music queue and Amiga source parity — 2026-10-30 (bounded)

- Fixed unnecessary SDL queue clearing for a deferred `0x84` under active `0x88`, and for `0x80` when the lower track is not foreground. Original service/scheduler flag behavior and actual SDL queue preservation are tested. A real foreground switch still clears queued data; exact original device timing remains unverified.
- All ten reconstructed tracker banks for the four tables are byte-identical between the pinned Windows Retail DATs and this decoded Amiga input set, including samples. The adapter's complete bank/sample bytes are traced to matching source-copy ranges; no Windows files are required for Amiga import. Original Amiga trigger order and playback/mix are not established.
- Seven unobserved stop functions: 55 original boundary records/4,448 call edges and initialized source contexts contain no observed target; three wrappers were executed in six controlled original states. This is not a proof of unreachability.
- Evidence: [queue](verification/retail-audio-deferred-2026-10-30.json), [Amiga banks](verification/amiga-windows-music-banks-2026-10-30.json), [stop pointers](verification/retail-music-stop-pointers-2026-10-30.json), [stop wrappers](verification/retail-music-stop-wrappers-2026-10-30.json).

## Retail music positions and transitions — 2026-10-30 (partial)

- All 563 raw DAT positions across ten banks select their original order/pattern in libxmp; the actual `StimPlayer` first 128 stereo frames agree with an independently positioned libxmp context. This is not original-player PCM proof.
- Mean: Retail base 0/4 plus 13 individual cue blocks executed; Mode4 phase1 omitted service 0x8c after 0x84/1/50, now corrected and covered by gameplay/original tests.
- Pirate: 81 retained scenarios/662,728 steps rerun twice; SHA-bound original event requests agree after the separately proven startup correction. Space/Demon: eight mode/minigame replays/155,060 steps, later service events exact.
- Original keyboard-driven Warning/Tilt now works for Space and Demon: missing native callbacks and warning DMD were restored, with 800-step original/SDL comparisons per table. Space requests 0x84/2/54; Demon sends 0x8c then 0x84/2/0. Seven other static stop sites remain unvisited. A raw-code survey found no direct external rel32 CALL/JMP into their bounded functions; indirect/computed reachability is unknown ([survey](verification/unobserved-music-stops-2026-10-30.json)). The known native Amiga data adapters pass the same bounded Tilt checks; original Amiga sequencing remains unverified. Original mixed PCM and actual listening remain unverified.
- [Space Tilt](verification/space-tilt-music-2026-10-30.json), [Demon Tilt](verification/demon-tilt-music-2026-10-30.json), [all positions](verification/music-order-positions-2026-10-30.json), [Mean transitions](verification/mean-retail-music-transitions-2026-10-30.json), [Space/Demon events](verification/space-demon-music-events-2026-10-30.json), [Space/Demon static coverage](verification/space-demon-music-coverage-2026-10-30.json), [Pirate coverage](verification/pirate-music-coverage-2026-10-30.json).

## Retail startup music correction — 2026-10-30

- Demon, Space and Pirate previously started bank 0/order 0 from incomplete cached globals. Actual Retail initialization/reset selects orders 25, 32 and 34 respectively. The native startup now binds both current and saved music fields from each table descriptor.
- Historical audio fixtures synthetically seeded the same wrong startup, so earlier comparisons did not validate it. They now adapt that first synthetic row only; later events remain strict. Original Amiga music sequencing and audible output are not established by this fix. [Evidence](verification/retail-music-start-2026-10-30.json).

## Windows Retail gameplay and audio verification — 2026-10-30 (partial)

- Pirate, Space and Demon: nine legal-input replays, 204,000 total steps, exact recorded state vectors and audio requests. All use saved original contexts with `original_reset_exact=false`; no complete-original-startup claim.
- Mean: 22 original Retail integration cases match all 100 ball bytes; 14 incompatible cases excluded. The initial states are native-derived, not an original trajectory. Retail minigame win and abort cases pass under adapted services.
- Space post-jackpot return and Demon consecutive video modes pass bounded original comparisons with diagnostic entry contacts. Pirate/Space/Demon single-voice PCM: 156 exact cases, explicit full-volume settings.
- Open: complete natural Mean game, unvisited branches/minigames, music sequencing and final mixed PCM, original display raster, physical listening and Amiga gameplay parity. [Verified inputs and scopes](verification/windows-retail-2026-10-30.json).

## Version 1.1 release

- Original-inspired menu/options screenshots, native controller support, smaller browser download and Vivaldi canvas fix. Standard downloads retain the static engine.
- New Linux AppImage/TAR.XZ, unsigned Windows installer/ZIP, single HTML and ARM64 preview built from 1.1.
- Release evidence and limitations: releases/v1.1/ACCEPTANCE.md. Previous v1.0 artifacts remain unchanged.


## Observed asset-read island / Demon revision3 — 071

- Separate developer audit observes original lifted RD/WR instructions without measurement code in release targets. Pirate reuses actual session/input routing; all180k observed ball-state steps match the existing references.
- Demon: two displayed480-byte source frames restored (22missingbytes), proved atnative callers410dae/413927 andoriginalBin65296/9bcba. Demonrevision3 adds one trustedprofile; other tables remainrevision2 andolder imports remain accepted.
- Afterfix:197758unique source bytes read inthree60k scenarios; zero unexplained read differences. Remaining observed differences exactlymatch original masks (Pirate500/Space627/Demon1bytes) orPirate sourceart2285bytes. Meanexplicitloaders have no newly missing asset; eight originalmaskvariants verified.
- Nine targetedCTests pass; asset-freeRC6 andisolatedDebian12/PCregression evidence indexed inasset-read-island.json. Unvisited paths, SDLreader coverage beyondexplicitchecks andoriginalAmiga physics/rules remain unclaimed.


## Amiga scene objects / compatible revision2 — 070

- Original Pirate caller proves an additional13-frame bank. Twelve source variants are preserved; frame0 legitimately reads one byte across the next directory entry. Original interface binding and all13frames executed/verified onM68020.
- Four missing whole frames restored forMean/Demon. Pirate192×20panorama andtwo5-tile16×20banks verified as complete objects. The nearby all-FF gap is outside these objects; it was not fabricated into a scene.
- Revision2 source profiles added alongsideRC4 profiles; allfour unchangedRC4imports verify andrun100steps. Native4×4000steps and8targetedCTests pass. RC5 asset-freeDebian12 package and source/PC acceptance indexed separately.
- Next: prioritize actually reached unmapped asset reads, not arbitrary file gaps. OriginalAmiga physics/rules parity remainsUNKNOWN.


## Amiga display island + RC4 — 069

- Shared inner-DMD RLE decoder implemented:1719 original bank frames acrossMean/Pirate/Space, verified by executing Original68k decoder plus OriginalLUT initialization.1712 matchPC; sevenMean repair frames retainAmiga art/TIRE wording versusPC TYRE. Demon retains its uncompressed path.
- TwelveMean contact-animation frames now use originalRaw descriptors/anchors/planar pixels, replacing static crops. Original palette indices retained; no assumed color aliases.
- Native four-table16k steps and7/7 targetedCTests pass; native andDebian12 builds warning-free. RC4 asset-free package built; isolated ADF-only Debian12 andPC DAT-only regression evidence linked inamiga-adf-island.json. Shared-native rules remain distinct from originalAmiga gameplay parity.
- Remaining: individual DMD fragments/source differences, fullAmiga mask/display-timing behavior, subjective GPU/audio acceptance. No fullAmiga physics/rules equivalence claimed.


## Amiga ADF runtime integration — 068 (partial)

- Native five-disk reader/SLAM decoder and original-asset bridge integrated into CLI, shared menu and standalone chooser. Per-table PC/Amiga source slots and separate highscores; no Windows-file fallback.
- DLM import, destination preservation/missing-set rejection, all four 100-step native sessions and menu reload/four children pass. Independent ADF/SLAM proof passes DLM and HD-Ninja; HD-Ninja full asset import rejects differing shared graphics revision.
- Shared native gameplay, not Amiga physics parity. DMD scenes partly unmapped; Mean contact animation uses original static crops. New distribution/older-Linux acceptance remains open; frozen RC1–3 preserved.
- [Usage/limits](amiga-adf-import.md), [integration proof](../analysis/traces/amiga-import-integration.json).


## DAT-only first import for all four tables — 067

- EXE dependency removed from first import and play. F2 accepts a DAT folder or its parent; standalone importers accept DAT_DIRECTORY OUTPUT. User DAT hashes remain strict; old EXE imports/private datasets remain supported.
- Native formulas reproduce56,232 math bytes exactly. Structured native captions, sample/lamp/table parameters and logical callback directories reproduce complete shared/table initialization454a00..466fec (75,244bytes), all sixMean source ranges and observed initialized-data reads. No original headers, instructions, IAT, pixels or PCM blobs bundled.
- Clean isolated package proof: no checkout/home/corpus/prepared caches, no gameEXE, freshprofile, readonlyprogram/DATs, networkoff/emptyPATH. Allfour import, reload twice,16k exact state/audio ticks; corrupt/missing DAT rollback anddestination preservation pass. Actual Debian12 DAT-only import+240k exact ticks/allfour pass; ABI ceilings unchanged. Final compiler warning fix yields bit-identical archive.
- RC3:build/compat/releases/slamtilt-reborn-linux-x86_64-rc3.tar.gz. RC1/RC2 archives/evidence retained. Full OriginalMean startup/trajectory, new subjective/GPU/audio-hearing acceptance remain unclaimed; this island replaces initialized data, not gameplay code.
- Final6/6 targeted CTests pass28.77s, including DAT-only isolation andpreservedRC1 integrity; final native/compat builds have0warnings. RC3 manifest/proof identities andall frozenRC1/RC2 references checked.

[Current data requirements](dat-only-import.md), [evidence](../analysis/dat-only-island.json).

## Mean Retail import / one Retail folder for four tables — 066

- Mean now imports supported Windows Retail as well as Demo; one Retail import sets up all four tables. Retail and Demo MEAN.DAT/MAIN.DAT are byte-identical. Legacy Demo eight-file hashes unchanged.
- Native importer extracts60,640 data bytes in six ranges, including full math lookup island and two inline mask arrays;124 explicit pointer fixups normalize existing native Mean data ABI. No original instructions executed, no original assets bundled. Standalone chooser/profile checks and shared menu support both inputs.
- Demo-hidden/Original-EXE-masked proof:68,000 legal Mean ticks/state+audio exact to prior native baselines; finite lifecycle,18 minigame cases,Rally andcombined modes pass. Packaged4000tick check passes. Actual Debian12 imports allfour fromRetail and runs240,000 exact steps; ABI ceilings unchanged. Four targeted CTests pass, including preserved RC1 integrity. New RC2 archive; old RC1 unchanged.
- EXE is needed only during import for lookup tables/descriptors, not afterward. DAT-only import remains unimplemented. Full Original Retail startup/trajectory equivalence remains unclaimed.

[Data requirements](data-import.md), [evidence](../analysis/mean-retail-island.json).

## Slamtilt - Reborn review / shared distribution — 065

- Neo-90s Premium main/options menus implemented; original Classic menu and reduced animation selectable. Original playfield previews, shared preferences/highscores preserved; 12 rendered layouts checked.
- Targeted launcher/import/lifetime refactor: transactional imports, configuration recovery, bounded child ownership, safe dialog lifetime, reliable F10 return. ASan/UBSan and 11 targeted CTests pass. Legal Demon replay exposed DMD callback 0x410ea0: +41 verified Original instructions, outside-call boundary unchanged.
- Shared asset-free Debian12/GCC12 RC built and tested in actual older userspace: native first import, all four children, 240,000 accelerated steps. Hidden-checkout/readonly-original/empty-PATH isolation passes. ABI maxima GLIBC2.34 / GLIBCXX3.4.29 / CXXABI1.3.9.
- New legal gameplay suite: 12 cases / 272,000 accelerated ticks. Retail source vectors/audio exact; Mean native determinism plus 22 Original component cases and 3,512 camera contexts; full Mean Original trajectory remains PARTIAL.
- Actual compositor Alt-Tab/fullscreen/pause/audio/F10 passes all four tables. Four five-minute GPU runs pass, 240,000 logical ticks/0 clamps. Demon uses explicitly controlled background focus and QA-only SDL-call instrumentation (300,008.67ms; no call over50ms). Earlier timing failures remain retained; their cause is UNKNOWN. SHA-bound release gate and three tamper-rejection cases pass.

[Release index](../analysis/reborn-release-island.json), [review](reborn-review.md), [release](reborn-release.md), [scope](reborn-playtest.md).

## Original-style four-table frontend — 064

- Shared SDL3 launcher usesactual Retail MENU.DAT pixels: chrome logo, fourgoldtablebuttons, Options/Quit. Keyboard/mouse selection, shared options, persistentdata/lasttable. F2imports3Retailtables together; Mean remains separatelyDemo-bound. Nativefallback beforeoriginalartavailable.
- Existing nativefrontends runaschildren; parenthides andreturns onexit. Session-only MainMenu footerbutton/F10 postsordinarySDLquit; standalonecontrols andphysics/rulesunchanged. Commonlauncher/package:tools/slamtilt andbuild/releases/slamtilt-four-tables-064.tar.gz. Nooriginalassetsbundled.
- OriginalRGBhash/unitproof, import/files, fouractualchildstarts/returns, options/failurepreservation, isolatedarchive/hiddencheckout/readonlyoriginals/networkoff/emptyPATH PASS. Nine targeted+fourtablegameplay CTestsPASS (5+4); build0warnings, actualdesktop screenshotinspected. Combinedpackage currenthostLinux; three/fourfrozenindividualRCs and062proofspreserved.

[Evidence](../analysis/frontend-island.json), [Frontend](frontend.md).

## Demon playable RC1 — 063

- All36 completion fixtures run against freshly native-imported packaged RC:222,852 steps and861audio requests, every pinned Original vector exact.20 bounded handbook contracts retained; no newphysics/rule code.
- RC package isolation/storage/options and actual Debian12/ABI checks pass. Realtime fullscreen GPU/Wayland/PipeWire:10,512steps/52.596s/0clamps, twelvevectors/31audio exact; actual125kABC storage/freshreload. Earlier attempt248clamps/63.035s is retained, causeUNKNOWN; no tolerances changed.
- Dedicated SHA-bound gate validates archive contents, all evidence identities,36fixtures andmetadata; rejects badarchivehash/missingfixtureproof/badevidencehash. Six affected CTests PASS0.93s, builds0warnings, screenshot inspected.
- Demon metadata is nowPlayable with supportedRetailEXESHA; completion release_ready=true. FrozenRC:build/compat/releases/slamtilt-demon-rc1.tar.gz. Mean/Pirate/Space and062 archives/evidence preserved. Bounded single-player acceptance; no all-seed/driver/physical-input/listening/raster claim.

[Evidence](../analysis/demon-rc-island.json), [Gate](../analysis/traces/demon-rc-gate.json).

## Demon standalone/import/ABI/realtime island — 062

- Native Retail importer and separate Demon selector reconstruct five files byte-exact (308 image DWORDs +1 runtime DWORD). No original assets bundled; Python/Wine/emulator/checkout unnecessary for import/play.
- Relocated readonly package passes hidden-checkout/network-off tests: native import with empty PATH, saved selection, legal game, production highscores, options/DMD persistence and focus/audio pause/resume.
- Actual Debian12 build/runtime: four cases/30,548 steps, twelve vectors/audio exact; ABI maxima GLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9. Packaged fullscreen Wayland/GPU/PipeWire:10,512 steps in52.577s,0clamps,31audio exact, actual ABC save/freshreload. Screenshot inspected.
- Four affected CTests + completion integrity pass; Space import regression12,000steps exact; builds0warnings. Demon remains standalone preview pending final RC metadata consistency/promotion. Three existing RC archives unchanged.

[Evidence](../analysis/demon-release-island.json).

## Demon legal game, real score storage and bounded manual audit — 061

- Position-feedback Enter/Shift keys score25k at3009, finish125k/ABC atGameOver10308, thenF1/newlaunch. **Zero diagnostic contacts**; Original/reset/native/reset/SDL10512steps/twelvevectors/31audio exact. Production storage writesactualrecord, freshprocess reload matches withno rewrite; initiallyempty privateprofile, no fabricated/imported records. GPU10340step legalgame/profilewrite exact, screenshot inspected.
-20/20 bounded handbook contracts mapped to36 SHA-pinned fixtures. Grave passivelydeclines5000/step beforetreasure (10M floorSTATIC); finalneedsplayedflags andpays35M whenalready4 onfifth. TheseRetail differences areexplicit; no universalvariant claim. Completion integrity and release gate areseparate.
- No newOriginal instructions (57,397total), outside5 unchanged. Demon rule tracing decoupled fromdiagnosticmode, enabling realstorage tests. Build0warnings;16/16CTestPASS314.25s, finalintegrity1/1PASS0.04s; dependencyorder and searchreproduction verified.
- Demon staysGameplayPreview pending nativeuser-data import/standalone package/olderABI/packagedrealtime acceptance. Next: thatreleasebundle using the existing threeRC pipelines; stop broadgameplayRE.

[Evidence](../analysis/demon-legal-audit-island.json).

## Demon Witch/Twice/Zombie variant bundle — 060

- Witch: same100ballbytes at(175,300)→20steps on(187.8369,295.2833) versus actual-rescued/off(175,301.8555). Both real sidelanes endmode, disableforce andretainBall1. This proves boundedforce response, not whole-context equality or fullfield coverage.
- Twice: twoheadpairs/4×15M, repeatedClock/Top guards, paircompletion rearmshead/double flags. Bonus2.25→4.5M then5.25→10.5M; realdrain pays11M andlaunchesBall2. Zombie Clock/Top/Wolf increases produce actual5/6/7/8M rampkills. Ordinary/bumper awards retained.
- **25,160 Original/reset/native/reset/SDL steps, twelve vectors and172audio exact**,5cases. Only30 Original instructions added (57,397total), outside5unchanged. New diagnostic vector coversforceenable/bonus/head/value fields. Build0warnings;14/14CTestPASS149.75s;9PEranges/allbytes checked. GPU Witch/Twice prefixes matchvectors/audio, screenshots inspected.
- Demon staysPreview. Next: bounded manual/fixture completion audit and highest playable/release blocker; positive legal-input-only scoring acceptance is still open.

[Evidence](../analysis/demon-variants-island.json).

## Demon kickback and all Clock awards — 059

- Skull bank earns kickback/600k. Identical100ballbytes prove armed upward rescue versus uncharged fall;250-counter grace, nonextending repeat, expiry and rearm verified. Right bank600k earns lottery; genuine elapsed delays select all12 outcomes, both flippers stop it.5M/10M/20M, video/Spirit/kickback charges, nonzero bonus collection/double, ExtraBall grant/physical consumption and actual BallSaver rescue verified. Field_0C +8/+5 remains neutrally named.
- **43,660 Original/reset/native/reset/SDL steps, eleven vectors and230 audio exact**,14cases.642 Original instructions added (57,367total), five outside calls unchanged. Build0warnings;13/13 affected CTests PASS208.39s. SixPEranges/allbytes/nineDATcontacts checked. GPU kickback/Clock prefixes matchvectors/audio; screenshots inspected.
- Demon remainsPreview. Alternative lottery availability/exclusion states are static-only. Next: Witchcraft/Twice-Pain/Zombie remaining outcome variants asonebundle, then completion/release audit.

[Evidence](../analysis/demon-banks-island.json).

## Demon moon bank and both video modes — 058

- Four physical Moon targets earn either Werewolf or No Brain No Pain. Brain correct choice50M/wrong0, early Enter guard and left/right bounds0..4 verified. Werewolf two kills5M/10M then failure; separate idle failure. Both return the captured ball to FREE play. Repeated moon flag does not complete bank; first/repeated-armed bank pays600k/15.1M.
- **17,052 Original/reset/native/reset/SDL steps, eleven vectors and197 audio exact**. Two additional SDL-event input cases cover8,108steps with exact vectors/audio/journal; physical keyboard/human visual tracking not claimed.
- Three missing shared-sample descriptors resolved through Original4017a8; existing mixer/libxmp reused (14sample profiles,3banks).951 Original instructions added (56,725total), five outside calls unchanged. Build0warnings;12/12 affected CTests PASS158.39s.12PEranges/allbytes/fourDATcontacts checked. GPU Werewolf award/Brain skull-shuffle screenshots inspected.
- Demon remainsPreview. Next: skull-bank kickback plus right-bank Clock awards. Mode variants and completion/release acceptance remain open.

[Evidence](../analysis/demon-video-island.json).

## Demon seven-mode campaign and final — 057

- One game earns all seven played flags, carries them through Witch ball loss, then starts Demon’s Night. Four original FREE balls;21 jackpots at7M/8.5M/10M. Every fifth restores a ball below4, or pays35M when already4 (twice observed). Mode Total257.5M.
- Last-ball compaction→normal play takes1step. Final clears played/selector flags; fresh Wolf selection works. **52,904 Original/reset/native/reset/SDL steps, ten vectors and64 audio exact**.
-373 Original instructions added (55,774total), five outside calls unchanged. Build0warnings,11/11 affected CTests PASS199.86s;11 PE ranges/all bytes checked. GPU/Wayland/PipeWire42,324step campaign prefix shows four balls;55audio/vectors exact, screenshot inspected.
- Demon staysGameplayPreview: diagnostic contacts, one campaign; alternative Top final admission is static-only. Next: moon bank→both video modes→controls/awards/return.

[Evidence](../analysis/demon-final-island.json).

## Demon seven Wolf/Spirit mode island — 056

- Shared ramp/trap consumers now drive all seven earned modes. Wolf trap0(266,153), Spirit arming trap0(91,14); ramps1(130,30),2(54,30),2(172,45),2(281,30). Actual selector/cycle/unarmed guards, played flags and mode returns verified.
- Bat25M hit, Meatball50M escape, observed Grave46.37M treasure; Zombie four5M kills; Witch four2M ramps/5M trap; Twice two balls/15M Clock head; Vampires four10M kills plus20M final. Ordinary/combo awards retained. Bat/Zombie/Witch/Twice return through real ball loss; other success outcomes proven.
- **42,412 Original/reset/native/reset/SDL steps, ten vectors and90 audio requests exact**.1,629 Original instructions added (55,401total), fiveoutsidecalls unchanged.19PEranges/allbytes andfourDATcontacts checked. Build0warnings;10/10 affected CTests PASS177.23s. GPU/Wayland/PipeWire4800step two-ball Twice prefix matchesvectors/14audio; screenshot inspected.
- Demon remainsGameplayPreview. Seven independent games, diagnostic contacts; not sequential campaign/allmode variants/legal-key-only/fullraster/listening acceptance. Next: seven played modes inonegame→Demon Night final multiball/rewards/return.

[Evidence](../analysis/demon-modes-island.json).

## Demon Clock Tower multiball / jackpots / bonus — 055

- Three actual Clock Tower captures at layer0(21,196) earn three balls. Layer1 ramp(130,30) arms locks; all-active-held guard pays 60M for three locks and later20M for the last ball. Required ramps advance1→4→5; unarmed/rearm captures eject without a jackpot. Ordinary awards remain intact.
- Real drain pays250k×8=2M and resets next-ball multiplier1. Separate last-ball-loss case returns after4001steps. **24,484 Original/reset/native/reset/SDL steps, nine vectors and58 audio requests exact** across three cases.
- Added743 compiled Original instructions (53,772total); five outside calls unchanged. Build0warnings;9/9 affected CTests PASS102.78s. Six PE ranges/instruction bytes and literal DAT ramp bit checked. GPU/Wayland/PipeWire5400step three-ball prefix matches vectors/14audio; screenshot inspected.
- Diagnostic physical contacts; no rule/score/timer/spawn edits. Not legal-key-only/full-raster/listening/full-table acceptance. Demon remainsGameplayPreview. Next: Wolf/Spirit selector→earned mode admission→one complete lifecycle.

[Evidence](../analysis/demon-clock-island.json).

## Demon first vertical rule/audio/presentation island — 054

- Demon is now priority; Mean/Pirate/Space RC references stay frozen. Existing shared physics/collision/renderer/score/pool reused. Six-lamp contacts(126,60),(148,60),(170,60) earn×2/4/6/8 then15M; actualLeftShift cyclesflags, duplicate guard, threephysicaldrains→ABC→GameOver/F1/launch verified. **6,668 Original/reset/native/reset/SDL steps/eightvectors/19audio exact**.
- Shared modern presentation now defaults forDemon: Escape options, P pause, zoom/fillcrop/shaders/DMD colors/placement, menu/focus pauses actualaudio andsimulation. Three STIM banks/11boundSFX useexisting libxmp/mixer, no newdecoder;463398 remainsunbound/unsupported. OriginalDemon launch1200steps/5requests andall assettests pass.
- Native qualified15M/ABC scoreboard isproven; session checks12000step zero-score naturalgame, no accidentalsave, actualOriginalrecord load/no-rewrite, corruptfile preservation andoptions reload. No newlyproven legal-input-only scoring/save route; twoflipperpatterns andlongEnterholds yieldedzero, duration hypothesisfalsified within4000steps.
-105 Original instructions added (53,029total), externalboundary unchanged. Build0warnings,9/9 affected CTests PASS89.22s, syntax andfivePErangechecks PASS. GPU/Wayland/PipeWire6668step vectors/audio exact, screenshot inspected; controlledfocus/diagnosticcontacts, notfullraster/listening/fulltable proof.
- Demon remainsGameplayPreview. Observed trapcontacts(91,14),(21,196),(266,153) havefield5a3/1/2; ruleidentities stillunlabelled. Next: ClockTower counter→earned3-ball admission→return asoneverticalchain.

[Evidence](../analysis/demon-base-island.json). [Demon](tables/night-of-the-demon.md).


## Space standalone Linux RC1 — 053

- **READY:** `build/compat/releases/space-private-053/play-space --fullscreen`. Public program: `build/compat/releases/slamtilt-space-rc1/slamspace`; first start imports supported original Windows Retail EXE/SPACE.DAT/MAIN.DAT withnative chooser. Asset-free relocatable archive; consumer needs no Python/Wine/emulator/checkout.
- Shared native Retail importer produces five exact-profile files from359 imageDWORDs +1 runtimeDWORD, original section/data copies and compact summary; unsupported/corrupt inputs/existing destinations preserved. Mean/Pirate import/setup regression passes. Standalone namespace hidescheckout; program/raws readonly, networkingoff, savedselection/options/highscores andmenu/focus/audio pass.
- Debian12/GCC12 binary: GLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9 ceilings;82,708 Original-exact rule steps inactualolderuserspace. Final packaged realGPU/Wayland/PipeWire game12,000steps in60.019s,fullscreentrue,0clampedframes,exactstate/canonicalaudio andsavedscore reload. Controlled focus/exclusive replay; no physicalkeyboard/listening/fullraster/universaldriver claim.
- Added explicit diagnostic `--replay-only`: extra live controls cannot contaminate acceptance, normal interactive controls unchanged. A parallel stress run clampedtime; isolated strict realtime check passed. Final provenance-only metadata repack left runtime bits/recipe semantics unchanged; archive/ABI retested.
- Modern/compat builds0warnings;13/13 affected CTests PASS136.32s; finalarchive2/2 PASS29.68s andgate1/1. **24/24 bounded manual contracts + RC release gate VERIFIED**. Space isPlayable; Demon remainsPreview. Next: transfer shared infrastructure toDemon, keepthreeRC baselines frozen.

[Release](space-release.md). [Evidence](../analysis/space-release-island.json).


## Space repeat / payout / damage / aim variants — 052

- Seven Original/reset/native/reset/SDL cases: **56,816 steps, ten vectors and121 audio requests exact**. Second Multiball requires4locks instead of3, then returns withthreshold4; cap9 is STATIC. Walker actualrecapture givessecond15M; aim70/88 miss,87hits, earlyEnter0 ignored. Misses ALSO spawn3balls inRetail.
- Race actual5/10/15/20/25M ladder, ten2.5M ordinary advances, cap5, passiveevent andten gated loop passes verified. Goals extendtimer100×counter. Retail starts/resets atfifth; belowfifth was not fabricated (guard STATIC, writer/alias limits retained).
- Sabre targets−1/2M; six accepted ramps−3/6M, excludedramp1, duplicate guard andremaining1→0 capped2M verified. Runtime DMD render440803 seesfield+1: internal0 displays1unit;30M finish follows.345 Original instructions added (52,924total), external boundary unchanged.
- Build0warnings; seven new comparisons PASS,6/6 regression CTests PASS25.47s plusaudit1/1. Sabre GPU/Wayland/PipeWire5664step prefix matchesvectors/audio; screenshot inspected. No physical-input/listening/full-raster claim.
- **24/24 bounded manual contracts VERIFIED**,39 pinned fixtures. Manual completion and release readiness are now distinct: existing unassessed import/ABI/relocation/packaged-session checks keepSpace GameplayPreview. Next: standaloneSpace raw-data import/package acceptance usingMean/Pirate infrastructure; stop detailRE.

[Evidence](../analysis/space-variants-island.json). [Coverage](../analysis/space-completion-contract.json).


## Space four-mission station SuperJackpot — 051

- One game earns all four missions → station → fresh mission → GameOver/ABC/F1/launch. **25,892 Original/reset/native/reset/SDL steps, ten vectors and53 audio requests exact**. Played is set at admission; two aborted missions retain partial flags across physical drains. Zero/three-played and duplicate collection guards pass.
- Station pays **75M** and clears all four played+armed flags. This run also earns ordinary500k and subsequent5M slot result (80.5M total); preserve source-specific rewards. Fresh Asteroid admission works after clearing. Five separate MODE-played flags remain zero: this is not BigBlam.
-206 Original instructions added (52,579 total), outside calls unchanged. Independent PE SHA/eight range hashes/all retained bytes checked; build0warnings, Python syntax and8/8 affected CTests PASS. Actual GPU/Wayland/PipeWire jackpot prefix matches ten vectors/audio; controlled focus, no physical-keyboard/listening/full-raster claim.
- Manual gate: **20 VERIFIED /4 PARTIAL /0 UNKNOWN**,32 pinned fixtures. Space remains GameplayPreview. Next: remaining higher-lock Multiball, repeated Walker, Race payout and Sabre damage variants as one acceptance bundle.

[Evidence](../analysis/space-mission-campaign-island.json). [Coverage](../analysis/space-completion-contract.json).


## Space grey bank / kickback / lanechanger — 050

- Seven Original/reset/native/reset/SDL cases: **7,352 steps, ten vectors, 34 audio requests exact**. Four grey contacts earn kickback; identical 100-byte ball states at620 separate armed/unarmed response. Saved ball returns free at933; uncharged grace repeat934 does not extend timer; natural expiry1624, expired guard and earned second save1630 pass.
- Actual Left Ctrl switches 46ed2c and ship lamps. Same loop entry selects Original ball field5c=11/13 at708; double toggle restores default, Left Shift does not switch. A real key during the loop at680 produces the selected trajectory; six actual SDL input cases pass.
-111 Original instructions added (52,373 total), outside calls unchanged; no invented physics/assets. GPU/Wayland/PipeWire scripted-key run matches ten vectors/audio; screenshot inspected. Host focus is controlled, fullscreen trace false; no listening/physical-keyboard/raster-equivalence claim.
- Manual gate: **19 VERIFIED / 4 PARTIAL / 1 UNKNOWN**,31 pinned fixtures. Space remains GameplayPreview. Next: four missions in one game → station SuperJackpot → clear/rearm.

[Evidence](../analysis/space-lane-kickback-island.json). [Coverage](../analysis/space-completion-contract.json).


## Space weapons / bonus / Magnasaver — 049

- Four Original/reset/native/reset/SDL cases: 5,548 steps, ten vectors and 16 audio requests match. Weapon lamps rotate with flippers; bank completion raises multiplier 1/2/4/6/8/10, then pays 10M. Real 250k bonus pays 2.5M at ×10; next ball resets multiplier to 1.
- Earned Magnasaver consumes its charge, pulls an identical paired ball state over 20 physics steps, expires after 201 fifty-Hz frames and can be recharged. Unarmed/repeated activation cannot extend it. This proves bounded force response, not a full natural outlane rescue.
- Fixed actual input gap: Right Ctrl activates Magnasaver; Right Shift rotates lamps. Left/Right Ctrl are configurable Space actions; six/seven-action settings migrate to eight. Three actual SDL key cases and independent physical-input reset pass. Left-special callback is verified; lane-changing trajectory remains open.
- 497 Original instructions added (52,262 total); five outside calls remain. Conditional DMD restore 40be98 is statically lifted, not executed by these cases. Build has zero warnings; 24/24 affected CTests PASS in 225.00s. GPU/Wayland/PipeWire scripted-key check matches ten vectors/audio under controlled focus; fullscreen trace was false.
- Manual gate: **17 VERIFIED / 4 PARTIAL / 3 UNKNOWN**, 24 pinned fixtures. Space stays GameplayPreview. Next: four-grey-lamp kickback and loop-direction/lanechanger as one trigger/input/trajectory island.

[Evidence](../analysis/space-weapons-island.json). [Coverage](../analysis/space-completion-contract.json).


## Space audit and base-rule island — 048

- Auditfound realmanual gaps; release staysblocked. Closed skillshot,Combos/ComboExtraBall andshipspeed withfour Original/reset/native/reset/SDL cases /24,472steps,nine vectors,69audio requests.21/21 affected CTests PASS206.29s; separateaudit-integrity1/1PASS, build0warnings.
- Skillshot10M→15M onnextnormalball,repeat/expired-first-arrival guards.40 realCombos→threshold20/40/80, twoearned/collectedcredits→Ball1 replayedtwice→Ball2. Armedcombo doesnotpay duringAlien. Retail directCombo isliteral1M plusbonusbase/count payout; observed40M countbonus onthree drains retained.
- Actual rightinlane(241,468)→event2 layer1(156,25) gives4/6/8/10M then20M/reset; unarmed/expired guards and751-frame grade decay pass.46ee4a ispassage counter, nottimer; earlierpaired-loop hypothesis disproven.
-997 Original instructions compiled (51,765total), outsidecallsunchanged. Actual GPU/Wayland/PipeWire fullskill/combo/credit chain13,296steps matchesninevectors and55audio requests. FullRetailPDF resolvescutBigBlam ending; noadditionalfinalrule found.
- Manualgate:15 VERIFIED /4 PARTIAL /5 UNKNOWN,20SHA-pinnedfixtures. Stillopen: weapons/bonus, kickback, Magnasaver, lanechanger andfourmissions→stationSJ; partialvariants remain. NoRC promotion/package claim.
- Next: weaponlamp bank→bonus multiplier/payout→earned Magnasaver asone bundle.

[Evidence](../analysis/space-base-audit-island.json). [Manualcoverage](../analysis/space-completion-contract.json).

## Space session / presentation — 047

- Space now defaults to shared options/presentation: Escape menu, P pause, fullscreen/resolutions, fit/stretch/fill-crop with ball following, zoom, filtering, GPU presets and DMD top/left/right/overlay/colors. Existing400-row consumers unchanged; Space uses600-row geometry. Supported controls remap left/right/plunger; initials retain Enter/Backspace.
- Shared options.json persists display/audio settings; private space-highscores.json loads selected table50bytes and atomically saves completed GameOver records. Missing/corrupt files preserved; diagnostic shots cannot use persistent profiles.
- Menu/focus pauses simulation AND actual SDL audio device, releases held inputs; resume drops catch-up time. Independent music/SFX/master levels connected. Settings fresh-process reload, finite12,000step game→ABC/save, score reload/no-rewrite and corruptfile protection pass in private test profiles.
-20/20 affected CTests PASS191.62s; final cosmetic-title smoke5/5 PASS12.89s, build0warnings. New1200step presentation path and12000step finite game remain Original-exact. Actual GPU/Wayland/PipeWire menu/focus event replay passes with Neon/DMDleft, and Fill/Crop/DMDtop covers laptop viewport; screenshots inspected.
- No new binary RE/physics code; existing options/UI/shaders/storage reused. Space remains GameplayPreview pending completion audit. Nudge/multiplayer/new release packaging not accepted here.
- Next: bounded Space completion audit and release acceptance using existing manual contracts/fixtures.

[Evidence](../analysis/space-session-island.json).

## Space BigBlam final campaign — 046

- Earned five-mode campaign→BigBlam→rewards→6→5→4→3→2→1→normal play:42,864 Original/reset/native/reset/SDL steps match nine vectors and87 audio requests.15/15 affected CTests PASS198.06s, build0warnings.
- Allfive played flags suffice; no mission wins or fresh arming required. Final entry clears allfive flags. Actual Retail code requests5 extra balls and reaches6FREE balls; manual says4-ball. Keep observed Retail behavior; reason for manual difference UNKNOWN.
- Unique eligible ramps pay10M each and grow bank15M.25M/100M bank collections and rearming verified; disabled loop, duplicate ramp, unearned/repeated top guards pass. Final special awards195M, player346,804,560. Last-ball return delay801steps.
-255 compiled Original instructions added (50,768total), outside boundary unchanged. Existing pool, renderer, inputs, assets and audio reused. Actual fullscreen Wayland/OpenGL/PipeWire campaign segment matches nine vectors/audio and shows six original balls.
- Scope: diagnostic physical contacts, genuine mode admission/input, no rule/played/score/timer/spawn edits. One campaign; not legal-key-only entiretable, all Tilt/seed/boundary cases or whole-raster/PCM parity. Space stays GameplayPreview.
- Next: shared playable frontend/session—reuse display/options and persistent highscore support, followed by bounded Space completion audit.

[Evidence](../analysis/space-bigblam-island.json).

## Death Planet success and Extra Ball — 045

- Final verification:14/14 affected CTests PASS158.96s; build0warnings, syntax and evidence/index/root-coverage checks PASS.

- Complete Original/reset/native/reset/SDL chain:19,392steps, nine vectors and15 audio requests exact. Frozen left/right-only steering clears allsix levels without losing any ofthree lives; six original15M awards total90M.
- Original completion earns pending Extra Ball46ed50; top capture2 collects it into playerWORD+10. A physical drain/bonus consumes the credit and Enter launches Ball1 again. Final score92,502,480. Actual fullscreen Wayland/OpenGL/PipeWire fullchain passes and screenshot inspected.
-234 additional compiled Original instructions (50,513total), six outside calls unchanged. Known video raster no longer retraced per-pixel during discovery; all state/DMD hashes and independent reset remain checked. Default trace behavior unchanged.
- Scope: diagnostic physical admission/collection/drain, actual steering keys during video; no rule/video/score/timer edits. One successful schedule, not all crash/seed/boundary cases or legal-key-only entiretable/full-raster/PCM parity.
- Next: BigBlam—sequential modes→earned final admission→four-ball finale/rewards/return. Other edge cases and Space options/persistence remain pending.

[Evidence](../analysis/space-planet-success-island.json).

## Space mode family — 044

- Final verification:13/13 affected CTests PASS154.45s; all four native/reset/SDL cases match nine vectors and90 audio events. Build0warnings; syntax and evidence/index references PASS.

- Four additional original mode outcomes: Light Sabre44×2M plus30M finish (unearned-top guard); Speed Bikes wrong-side guard,3×30M and12,921-step expiry; Walker aimed15M hit, ball-loss return; Death Planet no-input failure then physical ball release520steps later. Death Planet success/Extra Ball is NOT accepted.
- Four independent Original resets cover28,468steps. Native verification now compares nine vectors, including800-byte ball pool and256 opaque video/control bytes at466b6c;90 original audio requests retained.
- Fixed shared static CALL lowering: evaluate operand before pushing return. Original44551a `ff1424` CALL[ESP] exposed the bug atvideo tick1864. Original target probe retained; no CPU decoder/stub added. Static intermediate50,279instructions (+2702), six outside calls unchanged.
- Real fullscreen Wayland/OpenGL/PipeWire Death Planet segment shows original tunnel DMD;2,000steps match all nine vectors and audio. Fixed-step replay, not physical input/listening/full-raster parity.
- Walker manual mismatch is evidence-backed: Retail4436bc/443786 sets2 extra balls; observed pool reaches3 FREE balls. Keep Retail behavior; reason for manual difference UNKNOWN.
- Next: Death Planet success through six levels/PowerCore to earned Extra Ball. BigBlam/sequential campaign, other mode edge cases and preview options/persistence remain pending.

[Evidence](../analysis/space-mode-family-island.json).

## Space multiball rewards and return — 043

- Final verification:12/12 affected CTests PASS129.93s; build0warnings, Python syntax and JSON/evidence references PASS.

- Two complete reset→admission→rewards→3→2→1→normal-play chains cover17,676 Original/reset/native/reset/SDL steps. Eight vectors match, including the complete800-byte pool after deleting nonlast ball0. Both original return countdowns take801 steps after one ball remains.
- Standard Multiball: distinct ramps0/5/6 yield10M/20M/30M jackpots; every collection rearms eligible ramps. An unearned top capture pays only ordinary500k. Final score65.25M.
- Alien Attack: seven distinct events each pay10M; duplicate0 pays only ordinary250k. Earned top pays30M, repeated top only ordinary500k. Mode Total DMD100M; player score104M includes ordinary awards.
- Existing renderer/compaction/audio reused;526 additional compiled Original instructions,47,577 total, unchanged six outside calls. Original audio37 requests matches native with unchanged game vectors. Actual fullscreen Wayland/OpenGL/PipeWire full Alien chain passes; screenshot inspected.
- Scope: diagnostic FREE-ball contacts, original timers/rules/score; not legal-key-only whole-mode, all RNG/Tilt cases or full raster/PCM parity. Space remains GameplayPreview.
- Next: remaining four Space modes through the shared dispatcher—Light Sabre, Death Planet, Walker and Speed Bikes.

[Evidence](../analysis/space-multiball-rewards-island.json).

## Space multiball — 042

- Final verification: 11/11 affected CTests PASS117.91s, zero build warnings; Python syntax and JSON/evidence references pass.

- Standard Multiball and Alien Attack now spawn and display three original balls. Two independently reset Original/native/reset/SDL fixtures cover 15,472 steps and eight vectors, including the complete 800-byte ball pool.
- Shared original integer compaction408674 runs every fourth tick. Renderer draws every active ball with original masks, occlusion and shading in stable Y order; native reset checks the whole pool.
- Verified admission: third top capture then airlock starts phase4 at2118; balls2/3 appear3109/3201. Blam ramp then mode trap starts Alien phase6 at653; balls2/3 appear1657/1749.
- Corrected a disproven geometric hypothesis: capture3 (199,188) is airlock; capture5 (166,101) is mode trap. The original441ab4 dispatch table and runtime admissions establish the distinction. Previous capture IDs, score amounts and coordinates remain valid.
- Actual fullscreen Wayland/OpenGL/PipeWire replay matches all eight vectors; inspected screenshot shows three balls and Alien Attack DMD. This is fixed-step host verification, not real-time or physical input/listening acceptance.
- Next: prove3→2→1 loss/compaction, ramp jackpots and Alien Attack Super Jackpot. Current fixtures use diagnostic FREE-ball contacts; full multiball lifecycle is still pending.

[Evidence](../analysis/space-multiball-island.json).

## Space missions and audio — 041

- Race, Hack and Blam plus a negative Blam guard match Original/reset/native/reset/SDL over 47,412 steps. Race pays 25M at the goal and a separate 5M at expiry; Hack pays 75M only for the observed winning event; Blam pays six distinct 10M targets and the earned 30M final. Duplicate/wrong targets are checked.
- Space music/SFX now reuse libxmp and the existing mixer: three music banks, ten samples, 26 deterministic PCM checks. Seven Original audio cases cover 80,328 steps and 119 matching requests, with unchanged gameplay vectors.
- Verification: 10/10 affected CTests pass (109.45s), zero build warnings. Actual fullscreen Wayland/OpenGL/PipeWire replay: 1,200 steps in 6008.51ms, zero clamps; state and five audio requests match. This does not establish physical listening or Original mixed-PCM parity.
- Scope: diagnostic free-ball contacts, not complete key-only rule acceptance. Hack event-pair 1 remains static-only; runtime winner 2 is covered. Space remains GameplayPreview.
- Next: Space multiball as one island—original spawning, ball-pool compaction and rendering every ball; standard Multiball plus Alien Attack.

[Evidence](../analysis/space-mission-audio-island.json).

## Ace of Space priority — 040

- **Asteroid mission:** SPACE-ASTEROID-040: two Original/reset/native/reset/SDL fixtures /31,716steps. Allfour actual trapcaptures1/2/5/3 pay5/5.5/6/6.5M plus500k each; ramp no-Asteroid guard,exact12001-tick expiry,played flag acrossball2/3 andF1reset,46M/ABC/GameOver pass. All100ballbytes,clock/phase/DMD,poses,lifecycle/highscore/lamps and1536rawstatebytes match. AllSpace4/Demon3 layerhandlers seeded fromverified directories; +1041compiledinstructions,44802total,outsideboundary unchanged.7/7 affected CTests PASS35.73s;build0warnings. Extra20M return4413d5 preserved,meaning UNKNOWN. Diagnosticcontacts,notkey-only/allrules/fullraster. [Evidence](../analysis/space-asteroid-island.json).

- **Working:** `tools/slamspace [--fullscreen]` runs original Space playfield, ball, collisions, three flippers, lamps and colored DMD above the table. Shared `slamslice` also supports `tools/slamdemon`. Both are GameplayPreview; Mean/Pirate remain Playable.
- **Verified:** four Original/reset/native/reset/SDL cases /26,400 steps;100ballbytes,9clock/phasefields,3poses,DMD,lifecycle,selected-table highscores andlamps exact. Space natural three-ball→ABC/GameOver/F1→nextball; Demon natural zero-score three-ball→F1 (no initials qualification). Space actual Wayland/OpenGL fullscreen real-time1200steps/6014.73ms,0clamps matchesOriginal. [Evidence](../analysis/retail-gameplay-island.json).
- **Next:** Space multiball spawning/compaction/rendering. Space audio is connected; options, persistence and camera remain pending. Older Pirate work below is retained evidence.

## Pirate / remaining-table transfer — current

- **Playable RC / manual acceptance:** Pirate 038: PLAYABLE_RC. Manual audit links 24 rule contracts to 56 SHA-pinned Original fixtures / 372,660 retained steps; 48 semantic checks rerun. Closed the concrete auto-Knife gap: left/right only during video, 25 kills / 75M / collected Extra Ball, 13,076 Original/reset/native/reset/SDL steps, 74 audio events exact. Pirate capability now Playable with Retail SHA (Mean stays Demo; Space/Demon viewers); removed Preview captions. Asset-free GCC12 RC1 built and verified under actual Debian12: raw import/selection,25,792-step game plus90,340 rule steps/all10vectors; relocated archive and12 actual Wayland/PipeWire window/fullscreen event tests pass. [Evidence](../analysis/pirate-completion-island.json). Bounded diagnostic feature coverage is not all-feature key-only/full-raster equivalence; undocumented Battle3x admission remains UNKNOWN.

- **Mermaid / Hold Bonus / Tilt:** Pirate 037: Seven Original/fresh-reset/native/reset/SDL chains match all 10 vectors across 52,364 steps, also in the existing GCC12 package. Repeated Mermaid collection pays 1M/3M/4M; bank survives ball changes and F1 resets it to 1M. Hold Bonus preserves the base once, including under Tilt, but resets multiplier ×2→×1. Original quirk retained: Tilt suppresses base×multiplier, while Combo-count×1M still pays (2M proved). Seven audio cases / 217 Original requests match. Build: 0 warnings; 4/4 affected CTests PASS. Added fixtures/contracts/CTest; no production changes. Diagnostic free-ball trajectories, not legal-key-only all-feature acceptance. [Evidence](../analysis/pirate-mermaid-island.json).

- **Timing/earned Extra Balls:** Pirate 036: Nine Original/fresh-reset/native/reset/SDL chains match all 10 vectors across 29,076 steps. Skillshot: 10M once per ball, rearmed on next launch. Combo: 1M/2M/3M cap; timer 0 valid, −1 expired. Extra Ball: thresholds 25/50, next threshold 100; two earned credits replay Ball 1 twice before Ball 2. Player+0x0c counts successful Combos (historical ordinary_ramp_count keys retained). Existing native engine passed; added contracts, fixtures and CTest gates. Nine audio cases / 100 Original requests match. Diagnostic contacts; not legal-key-only all-feature acceptance. [Evidence](../analysis/pirate-window-island.json).

- **Rule fix/full chains:** Pirate rule035: fixedactualPlank30Mfeedback callback42eb6c,previouslymissedregisterpush432388/432390/4323c8. Oldreleasefailed4099;now271dispatches/51DMDframes exact. +211compiledOriginalinstructions,24118total/outsideboundary unchanged. Fourchains26008Original/freshreset/native/reset/SDL10vectorsteps:PlankSJ,Piranha10×2Madditions/11thnormal/rearm,1/2/4/6/8/10/12bonusladder/cap,20.7M×12payout/nextballreset. Allfour alsoGCC12/actualDebian12 pass.82uniqueaudio cases/6215requests exact acrossmain81+scoped1;retained78rows unchanged. Fullbuild0warnings;two4/4CTestbatchesPASS209.10/34.58s. Ready:`build/compat/releases/slamtilt-pirate-rules/slampirate`. Diagnosticphysicalwaypoints,notallkey-onlyall-featuregame. [Evidence](../analysis/pirate-rule-island.json).

- **Full real-time games:** Pirate fullreal-time034: nativeGPU/actualwallclock legalCrocodile replay15600steps/78.026s andtwofinitegames25792steps/128.986s matchall10original vectors;597audio requests exact,0timeclamps. Threecompletegames/3F1 continuations; firstnaturaltrajectory overlaps. Cave/Cannon/2ballJP/15.83M/ABC/GameOver/F1/freeball pass,plusactualprivatehighscore persistence andfreshprocess50byte reloadwithoutrewrite. Newexact-tickbound supportsnon4multiple37step test. Freshoriginal15600retains9vectors/addsMSstate; no newRE/physics.4/4CTestPASS14.43s,oldABIandmodernbuild0warnings,actualDebian12regression retained. Ready:`build/compat/releases/slamtilt-pirate-fullgame/slampirate`. Notwholeoriginal raster orphysicalinput/audio listening/all-mode acceptance. [Evidence](../analysis/pirate-full-realtime-island.json).

- **Real-time/render cost:** Pirate real-time/cache033: preload75ball shading groups once; conditionalLampstate/actualflipperRGBA/DMDcolor texture uploads. 1000fixedframes/4000steps preserve10vectors/camera/fullBMP byte-exact; uploads58000→2974,MAINopens1002→3,perballrenderfileIO0. All600Ypixels matchprior decoder. RealWayland/GPU4secondruns/window+fullscreen:799steps,acceptedclockresidual<5ms,0clamps;8queuedpresses permode reachposechange inlowmilliseconds. Rendercallwallp95~0.82–0.86→0.16ms; loopintervalnotphysicalrefresh,not CPU/GPUcounters orphysicalinputlatency.5/5CTestPASS17.58s,12finalpackagehostcases pass,olderABI fullgame unchanged. Newready:`build/compat/releases/slamtilt-pirate-realtime-final/slampirate`. [Evidence](../analysis/pirate-realtime-island.json).

- **Older Linux package:** Pirate older-Linux ABI032: same immutableMean Debian12/GCC12toolchain reused offline/sourceRO. MaxGLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9. ActualDebian12glibc2.36 imports4exactfiles withnativeUI/PATHempty; rememberedstart/SHA/audioNudgeSpecial pass.25792steps/10vectors/6448camera frames/364audio requests exact. No sourcecheckoutmount,program/raworiginalsRO,networknone. Relocatedarchive/currenthost and12Wayland/PipeWire actualwindow/fullscreen cases pass.4/4regressionCTestsPASS31.99s; ownbuild0warnings. Ready:`build/compat/releases/slamtilt-pirate-bookworm/slampirate`. Sharedhostkernel; otherdistros/drivers/physicalAltTab/listening unclaimed. [Evidence](../analysis/pirate-compat-island.json).

- **Host test resolved:** Pirate host031: observed actualfocusgain526/mainwindow4 after scriptedloss527/id0 explains frame2failure. Test-only SDL_PumpEvents beforeinjection fixes event order; no ignoredOS events/removedfreezechecks/audioorphysics changes.12source+12packaged realWayland/PipeWire runs and6dummy cases pass audio/Nudge/LeftCtrl focus/minimize/pause/options/mute/reset/repeat/remapping gates. New --fullscreen enablesgenuinefullscreenwithframes; earlier030attempts werebothwindowed.4/4CTestsPASS30.00s,fullbuild0warnings. Relocated25792steps/10vectors/6448camera frames/364audio requests unchanged. Ready:`build/releases/slamtilt-pirate-host/slampirate`. PhysicalAltTab/listening/otherdrivers/olderABI remainunclaimed. [Evidence](../analysis/pirate-host-island.json).

- **Native first start / package:** Pirate folder chooser/drop/raw import/prepared selection/persisted path and --setup/--data/--check now share Mean's native UI,with separate Pirate preferences. Asset-free stripped Linux bundle/archive ready:`build/releases/slamtilt-pirate-native`. Relocated archive imports originals and runs25792steps/10vectors/6448camera frames/364audio requests exact; strace0checkout/Python/Wine accesses/executions.4/4affectedtestsPASS34.73s,build0warnings. Historical hostfocus-test failure resolved031; earlierframe-limited attempts werebothwindowed. [Evidence](../analysis/pirate-firststart-island.json).

- **Native raw import:** `build/native/slampirate-import EXE DAT_DIRECTORY NEW_OUTPUT` creates all4supported Retail data/context files byte-exact without Python/Wine/emulator. Ready:`tools/slampirate --data build/imported/pirate-retail`. Importeddata run25792SDLsteps/all10gameplay vectors/6448camera frames/364audio requests exact.341image+1runtime startup scalars; code/graphics copied from user originals. Native package/chooser now verified by030. [Evidence](../analysis/pirate-import-island.json).
- **Composition audit:** all27Pirate flipperframes×4lamp patterns=108frames/321792pixels and4wholelamp canvases/768000pixels match originalblits with0RGB/alpha errors.53lamp masks have0opaque pairwise overlaps; no new renderer fix justified. Existing endpoint coverage expanded.

- **Original camera:** direct ballY−260 follow replaced by Retail409350 inertial camera, state6-aware multiball selection/fallback, empty-pool handling, GameOver pan and x87 residual interpolation.9000 sequential original states/45000interpolation values exact;6448actual SDL frames/25792steps agree with original consumers; all10gameplay vectors unchanged. Nudge retained,DMD fixed. Full original raster/scheduler equivalence remains unclaimed. [Evidence](../analysis/pirate-camera-island.json).

- **Repeated-game acceptance:**24 normal-input policies/520244native steps,48GameOvers/48F1 restarts,zero errors; original/reset/native/reset/SDL prove three representative Nudge/Tilt/Crocodile paths/62576steps/6finite games. No waypoints; clock/RNG/highscores retained across games. No earned Magnasaver in this sweep; prior magnet evidence retained. [Evidence](../analysis/pirate-acceptance-island.json).

- **Working:** `tools/slampirate`: original playfield/ball/occlusion, three Shift-controlled flippers, camera, Alt/Space Nudge with original Tilt and table motion, colored DMD,53 animated lamps including flipper masks, existing options/effects. Enter launches; LeftCtrl activates earned Magnasaver (configurable Left special); type initials when admitted; R/F1 after Game Over starts the original new game without resetting clock/RNG. Pirate scores persist in a separate private profile.
- **Verified:** complete legal three-ball→bonus→ABC initials→highscore→Game Over→F1→second game,12000steps, original/native/reset/SDL exact for100ballbytes,11clock/RNGfields,15 lifecycle fields,DMD/highscore/lamp hashes each step. Fresh process loads the exact saved50bytes without rewriting the profile.
- **Adventure added:** Walk the Plank entry, five distinct ropes, duplicate-hit guard,30M Super Jackpot, capture/release and normal-play return; timeout also verified. Original/native/reset/SDL match15336 steps including all864 rule bytes each step. Test shots reposition only a free ball at actual DAT switch points; these are diagnostic trajectories, not legal-key-only proof.
- **Four more Adventures:** Swordfight jackpot growth/repeated collection/timeout; Treasure Dive rate boost/depth100/clamp/30M/timeout; Monkey wrong-target guard/five-piece map/30M/timeout; Shark speed gains/50M escape/timeout. Seven original/native/reset/SDL diagnostic fixtures match47256 steps. These modes are verified individually, not as an all-five finite game.
- **Knife Throwing:** original50Hz video simulation, Shift movement/automatic throws/Enter,25kills×3M, success/failure DMD and normal-play return now verified. Extra Ball is first armed, then collected at the right trap; upper-trap noncollection guard passes. Original/native/reset/SDL match15648 steps, including864 rule+892 video-state bytes per step. Diagnostic table entry; keys only during the video mode. [Evidence](../analysis/pirate-knife-island.json).
- **Crocodile Multiball:** two Cave locks→cannon aim/hit→two balls→5M jackpot→Cave growth→6M jackpot→rescue/drain→single-ball return verified; cannon miss loses one lock.8908 original integer-oracle/native/reset/SDL steps match all800 ball-pool bytes plus rule/video/clock/display state. Fixed original sine-service binding and render-owned pool compaction; SDL camera follows the lower ball. [Evidence](../analysis/pirate-multiball-island.json).
- **Four-multiball campaign:** frozen Crocodile prefix→Storm→Battle→Mutiny runs25780 original integer-oracle/native/reset/SDL steps exactly, including all800 poolbytes. Actual Windows Retail gives3/4/5 free balls in the new modes; handbook says3/3/4. JP10/15/20M→Cave+1M→11/16/21M, duplicate/unlit guards, target wrap, nine slot0 compactions and each normal return pass. Only701 compiled instructions added; no physics changes. [Evidence](../analysis/pirate-multiball-campaign-island.json).
- **Five-lock campaign:** all four multiballs now run with actual five-Cave-locks and a sixth-lock guard,29844 original/native/reset/SDL steps exact. Five actual free balls each; startJP12.5/15/17.5/20M, Cave+1M,16slot0 compactions and four normal returns. No additional original routines needed. Battle unarmed upper-trap gives500k without JP collection; actual write watchpoint found only clears, so triple-JP admission remains UNKNOWN. [Evidence](../analysis/pirate-surplus-island.json).
- **MagnaTable:** one actual Cave lock plus left lane34,468 arms400-frame window; upper trap initializes431d95 without phase change. Shift callbacks434268/434340 set original type2 force descriptors465864/465858;40ad80 applies original integer LUT force. All12 reward targets4380dc verified through actual layer1switch2 captures, including direct/pending Extra Ball, mode light,5/10/20M, Hold Bonus, Ball Saver,5 Cave locks, Mermaid growth and Kickback. All three slots, no-lock/expiry guards, full intro/skip, no-award exit and two1800-step key-only flights pass.20 fixtures/40876 integer-oracle/native/reset/SDL steps exact; only289 compiled instructions added. Follow-up below closes one key-only reward and four earned-state eligibility/fallback cases. [Evidence](../analysis/pirate-magna-island.json).
- **Magna completion:** four actual fallback chains: mode already lit→20M; all6Adventures played→20M; earned HoldBonus→Crocodile→Magna reentry→10M; earned Kickback→same reentry→5M.64560 original/native/reset/SDL steps exact. First key-only Magna flight/reward: both magnets alternate OFF/ON every120steps;468free steps→actual5M capture1820→return1970,2052steps exact. Only entry uses diagnostic waypoints (last1209);25Magna fixtures/107488steps now covered. No extra original instructions needed. [Evidence](../analysis/pirate-magna-completion-island.json).
- **Treasure Island:** frozen25780-step four-multiball prefix→six actual Adventures→final→new Plank cycle,54760 integer-oracle/native/reset/SDL steps exact. Eight actual free balls (handbook4),15M→16M JP, duplicate/unarmed guards, target sweep and15/47/80M Super Jackpots;284M beforedrain,300M afterone further16M. Seven slot0 compactions8→1, progression reset, actualreturn-lane gate andnextPlank entry/release/completion verified. Only149 compiled instructions added; no productionphysics/render/input changes. [Evidence](../analysis/pirate-final-island.json).
- **Audio added:** two original Pirate STIM banks (68/55 orders),15 direct/shared PCM descriptors; existing libxmp/sequencer/two-voice SDL mixer reused.6215 delivered requests (82base +6133actual service entries) across82unique fixtures/672732steps (main81+scopedpayout1) match native/reset; legal basic game and final campaign match SDL requests too.60 original Retail mono-LUT/resampler cases are byte-exact. Focus/minimize/pause/options/mute/reset SDL acceptance passes. Original final mixed-output equivalence and physical host listening remain unverified. [Evidence](../analysis/pirate-audio-island.json).
- **Corrected:** original single-ball drain writes canonical46c1b4 directly. Earlier relocated oracle matched an invalid split context; its phase3→1 did not prove next-ball initialization. Canonical pool46c15c+i*100 now preserved; superseded compact fixtures archived under `analysis/traces/superseded-pirate-relocated-context/`.
- **Transferred:** all four tables:103 original flipper frames and216 lamps/432 on-off frames. Actual original lamp blits:303296pixels,zero differences; Pirate native parent-mask composition:24frames/72192pixels,zero RGB/alpha differences. Space/Demon remain viewers; Mean gameplay unchanged.
- **Not complete:** physical Pirate audio/host acceptance, combined legal all-mode acceptance, arbitrary dynamic-object presentation, extended attract and import/package/user-host acceptance. A bounded complete basic game is not complete table coverage.
- **Nudge/Tilt:** default LeftAlt/RightAlt/Space, configurable; original forces, warning/DMD/audio, flipper release, finite drain and next-ball reset.12 original/native/reset/SDL fixtures/45844steps exact, including Knife/Magna/Crocodile and held captures. Real SDL repeat/focus/pause/options/minimize/remapping gates pass. Only295 original instructions added. [Evidence](../analysis/pirate-nudge-island.json).
- **Lock matrix:** all10 legal lock/ball-count combinations covered;3new Crocodile3/4 and Storm4 fixtures/26876steps exact, eight slot0compactions. [Evidence](../analysis/pirate-lock-matrix-island.json).
- **Natural gameplay:**11key-only fixtures/65068steps exact;3naturalCave locks→5.145M→ABC→GameOver→F1→free second-game ball.10original DMD callbacks plus one bonus-control routine added (+917instructions), including ShootMagnaTable/MermaidBonus; actual ordinary key policies previously stopped here. No waypoints in these11fixtures.46audio fixtures/3567deliveries now exact; all new/affected checks pass, build0warnings. [Evidence](../analysis/pirate-legal-gameplay-island.json).
- **Battle3×:** no handbook rule; direct nonzero gate setters belong to TreasureIsland/Plank/Dive.8770 observed Battle steps stay unarmed. Reachability elsewhere remainsUNKNOWN; no synthetic arming.
- **Natural Crocodile:** two earned Cave locks→joint40ms flipper pulse→cannon→two balls→actual5M jackpot→single-ball return→15.83M/ABC/GameOver/F1/free second-game ball.15600original/native/reset/SDL steps exact, no waypoints or new gameplay instructions. Offline679candidate search/30.71s only proposes keys; proof replays fresh from reset.47audio fixtures pass. [Evidence](../analysis/pirate-natural-croc-island.json).
- **Natural Plank:** right-ramp arm1750→upper capture/phase5 at4104→free ball4932→natural drain6093→6.08415M/ABC/GameOver/F1/free second-game ball.11600original/native/reset/SDL steps exact, no waypoints. Also fixed ordinary DMD42e140 (+142original instructions), full201-call cycle/10344steps exact. Five affected CTestsPASS120.72s;49audio fixtures green at that stage. Initial fixture stops at drain; rope follow-up below. [Evidence](../analysis/pirate-natural-plank-island.json).
- **Natural Plank ropes:** actual flipper pulses earn rope4at6763 and rope3at7298, each10M+250k/400timer ticks. Two new finite games17.53415M/28.18415M→ABC/GameOver/F1/free next ball;26200original/native/reset/SDL steps exact. Missing bonus-DMD42ee48 now compiled(+106instructions);51audio fixtures green. [Evidence](../analysis/pirate-plank-natural-ropes-island.json).
- **Display/feedback bundle:** original Nudge motion now moves table/lamps/flippers/balls together;63original viewport contexts and all12Nudge/Tilt SDL trajectories pass. Six actual Swordfight/Dive/Monkey DMD messages added(+695instructions);12124new diagnostic steps exact. Natural two-rope+Nudge finite game adds13400legal steps and96×18wavefield samples.5/5affected checks pass;55audio fixtures green. [Evidence](../analysis/pirate-feedback-display-island.json).
- **Final direct DMD bundle:** Extra-Ball threshold, earned Magnasaver, bonus multiplier and right-outlane Kickback:4fixtures/9104steps original/reset/native/reset/SDL exact;43/43bounded direct targets compiled(+580instructions). LeftCtrl is configurable, six-key profiles migrate without losing mappings; realSDL gates/remapping pass.7/7affected tests PASS106.47s. [Evidence](../analysis/pirate-final-feedback-island.json).
- **Magnasaver physical save:** paired inactive/active left-outlane entry; real force lifts ball, expiry then LeftShift2200..2320 returns it aboveY400/free through2800. Repeat-without-charge, reearned reload, Tilt force inhibition/frozen timer and actual next-ball reset:7fixtures/21904steps original/reset/native/reset/SDL10vectors exact; no additional original instructions.5/5affected checks PASS115.80s;66audio fixtures green. [Evidence](../analysis/pirate-magnasaver-island.json).
- **MagnaTable capture boundaries:** true DAT edge/exit,150step hold/cooldown10→0→−1,Tilt rejection/early held release,and last trap admission2760vs2761:7fixtures/13940steps exact.5real-context occupied/cooldown leaf cases exact/unchangedmemory;previous20Magnafixtures preserved.5/5affected testsPASS118.40s;73audiofixtures. [Evidence](../analysis/pirate-magna-capture-island.json).
- **Composed finite campaign:** unchanged54760step4multiball/6Adventure/TreasureIsland prefix→13legalactions/no furtherwaypoints→ABC/1.486839210B/GameOver62640/freeze64/F162704/free nextgame62910.62992totalsteps original/reset/native/reset/SDL9vectors exact; no new engineinstructions.3/3finalchecksPASS148.15s;74audiofixtures green. Both Magna systems are integrated by the follow-up below. [Evidence](../analysis/pirate-campaign-finite-island.json).
- **Same-game magnet campaign:** retained4MB/6Adventure/final prefix→earnedMagnaTable/Mermaid+3Mbank→earnedMagnasaver/802forceapplications/actualflipperreturn→ABC/1.498782380B/GameOver65040/F165104/freeball65310.65392steps original/reset/native/reset/SDL10vectors exact;11postprefixwaypoints,last55486,then9905keys-onlysteps.4/4affectedchecksPASS182.02s;75audiofixtures. No engineinstructions added. [Evidence](../analysis/pirate-campaign-magnets-island.json).
- **Next:** Verify Pirate Skillshot/Combo timing windows and earned Extra Ball thresholds through actual original events. Third natural Plank rope remains unproved after bounded searches.

Historical Mean findings below remain applicable; older Pirate-only-contacts/unknown-tick entries are superseded by this workpack.

- Native Mean: original playfield/ball/flippers, deterministic collision/physics, finite three-ball lifecycle, bonus, rules/captures, DMD and audio are implemented with bounded original fixtures.
- Natural finite Cliff success/timeout, Kickstart60M PitStop65M, StockCar75M full SPEED Monster Car and Liquid Rally success/timeout Offroad90M and ChickenRace three-race/max/expiry now replay from reset through bonus/GameOver/new-game; original bounded rules/pixels remain the reference. Gear1→5/earned extra collection/×5 bonus/credit redemption now verified twice through finite GameOver/reset. KICK→physical rescue→grace expiry→finite GameOver/reset now verified twice. LaneSaver fence geometry/rendering and natural GOAL-bonus collection/open/GameOver/reset now pass. Full goal ladder/credits and ordinary lap timing now pass; MillionSkull timed repeat/expiry/restart now verified; Skillshot selection/lock/20M→30M/finite lifecycle now verified; both-ramp progression now verified; mapped audio-event chain now integrated; next primary: Mean laptop/input/layout/highscore/audio acceptance.
- Launcher now selects verified Retail first-minigame rules: three laps /120M; explicit `--demo-minigame` retains six-lap Demo behavior.
- Remaining-rule comparison: 26 ranges /7463 instructions per Retail/Fix build and153 table DWORDs unchanged; reuse existing consumers (`analysis/mean-rule-reuse.json`).
- Coverage limits: no complete original-table trajectory equivalence; first- and second-minigame natural finite entry/win/return/GameOver are now verified natively with SDL-equivalent diagnostic inputs. Complete Mean finish is not claimed.
- Both minigame win/failure → return → bonus → finite GameOver → new-game reset chains now pass18 deterministic integration cases:12 diagnostic captures plus6 natural finite entries (Formula1 win/abort and second-minigame win, each repeated).
- Persistent Tilt dispatcher now passes ten finite release/bonus/next-ball/reset chains with a nonzero test bank. Original Nudge waveform/collision/query/SDL coupling is now implemented; bounded special-mode Tilt composition now passes original fixtures and seven finite native chains; remaining award/presentation boundaries are partial.

All five main-mode contracts now compose in one ordinary finite native game, including an intervening eight-ball SPEED multiball. Two fresh runs: all five at78512 onball2; GameOver83056/924072310/fourbonuses/freeze64/reset. Replays: `analysis/traces/mean-five-modes-{input,finite}.json` (MEAN-073). Full Original trajectory equivalence remains unproved.

The entries below are chronological evidence; earlier blockers may be superseded by later verified changes.

# Working

- Baseline material3/4 active responses now include6830base points and original contact flashframes; material5 response adds50000base points.1000original-x86 cases match ball bytes/score/effect selection; original418030 animation matches240steps. Native6000steps pass3starts/2drains/275000points; longer run stops8409states atlayer3/switch1 near85.75,141.33.

- Lower baseline switch4/y>=450 now awards its original25000-point base value. Native HUD shows ball/score; score persists across drains and resets withR.640original-x86 score/event cases pass;2500step run yields3score events/75000points. Mode bonuses and other score events remain unported.

- Native continuous single-player slice now prepares the next ball after baseline y>=608 drain.256original counter cases match;2500native steps include1drain and2launches. Bonus/DMD skipped; finite game-over rules and ball-save mode remain unported.

- Step64 isolated: original integration+collision with saved static context equals native result. Synchronized per-step flipper/engine-context capture and native replay implemented; fresh live comparison completed. Evidence: mean-contact64-static-context.json.
- Synchronized original lower-flipper fixture:100steps,13contacts, all101XY/VX/VY states match native exactly. Conditional CTest mean_contact_oracle added. External contact context replayed; autonomous input timing/full table rules remain unverified.

- Upper ramp transitions implemented: deterministic scripted launch now1852states/90contacts, reaches original BALL_DRAIN boundary instead of unsupported callback. Directed acceleration:64original-x86 fixtures match all100ball bytes. Full trajectory equivalence remains unverified.

- Mean demo ballstate and per-ball step identified; live flight fixture: `analysis/traces/mean-flight-100.json`.
- Native `--simulate build/mean-prepared --trace analysis/traces/mean-flight-100.json` renders original ball/playfield, follows ball and runs deterministic native integration/bitmap contacts/flipper collision. Shift keys drive original flipper pose step; original flipper sprites render.
- Native flight matches X/Y/VX/VY for steps0–63; first divergence64 at flipper contact. Per-step original flipper/input state was not captured. This does not prove its cause.
- Original x86 comparisons:900 component cases,1500 flipper cases including275 contacts,240 sequential input/pose steps: zero differences.

- Native C++17/SDL3/CMake `slamview` displays all four original Windows playfields in color, with manual viewport scrolling and BMP export.
- 1536000 Windows/Amiga base-image RGB pixels independently compared: zero differences.
- `slaminfo` recognizes known table assets, SLAM, STTF/STTL, RNC and executables; reports sample/score structures.
- Bounded SLAM decoder; original Amiga music extracted and rendered to PCM through libxmp.
- Amiga planar playfield layout recovered; native `--amiga` loads decoded RAWs.
- Corpus manifests, structural comparisons,30 source WHDLoad patch records, Amiga hardware anchors and Windows import/callback maps.
- Packed-BCD highscore reader, cross-checked against two supplied independent tool sources.

- Launch initializer/action/layer1–3 material responses:900 original-x86 comparisons, zero differences. Screenshot: `build/mean-native-ready.png`.
- Corrected baseline normals from wrong0x95af6 to verified0x959f6; caches regenerated.

- User-reported rail offset fixed: original render anchor is(-7,-7), with previous/current interpolation;7original x87 fixtures match native. Lower switch4 now continues;300original cases confirm unchanged ball state in initial mode.

# Strong hypotheses

- Shared engine plus per-table hardcoded callbacks/data is the productive native boundary.
- Decoded Amiga table overlays are the highest-value physics/rules target; executable code in them is confirmed, exact physics island is not.
- Ball coordinates are signed16.16 at object+0/+4; velocity at+0x14/+0x18, dynamically captured.

# Unknown

- Original camera behavior; complete forces/ramp/rule behavior. Demo timing is statically verified at200Hz.
- Remaining ramp/rule branches and special switch capture/release lifecycle.
- Meaning of individual table callbacks; full rule/mode state machines.
- Sprite/lamp/DMD dynamic descriptors and audio event sequencing.
- Complete compiled WHDLoad3.6 patch map and semantic mapping of every historical patch.

# Biggest current blockers

1. Full table rules, ball save, score/lamp event effects and finite game-over lifecycle remain unported.
2. Some special materials/ramp branches and point forces remain unsupported; foreground occlusion incomplete.
3. Full autonomous-input trajectory equivalence is unverified. Synchronized100step contact fixture passes; older flight trace lacks contact context.

# Highest-value next actions

1. Port upper capture afterallfive modes: field43f1f2>=5.
2. Extend coverage only where actual gameplay hits an unsupported branch.
3. Capture longer synchronized launch/contact traces when needed.

Native gameplay slice is visible; no fully playable table is claimed. `tools/slamplay` starts ready; Enter launches, Shift controls flippers, R resets. Original demo5ms accumulator is used. Single-ball regression has1852states/90contacts; continuous mode advances to the next ball; this is a deterministic native regression, not a live-original trajectory match.


## Bundled gameplay continuation — 2026-10-08

Implemented bounded ramp/layer4/material6–7 and baseline switches1/3/4, including right return lane. Ramp1600 + materials512 + baseline-one480 + baseline-three480 + switches512 =3584 original comparisons, zero differences. Three synthetic input schedules complete12000 steps (7/7/6 launches); fourth stops11377 steps at left capture near32,279. Repeated coverage is byte-identical; these are native regressions, not full original trajectory matches. Build,3CTest cases and existing component/contact/scoring/lifecycle checks pass. Next: prove438b68 slot state and captured-ball tick/release for41d9e3..41da47; preserve explicit stop until supported.


## Capture/release vertical bundle — 2026-10-08

Implemented left baseline switch3 capture(callback2), original253-step callback2→3→active sequence and500000 base award. Integration preserves original held-ball wrapper and same-step release physics. Slot first-word updates run50Hz; capture timers200Hz. No injected DMD completion: initial-mode original branch clears its gate. Player+8 bonus updates remain separate from score; full rules/notifications excluded. Layer2 target/transfer41c00c..41c09f and capture exit pointer+7 now honored.

Verification:512capture-entry cases,253original callback states (all100ball bytes plus slots/gates/score),512shifted-normal cases,768switch cases pass. FiveCTest cases pass, including frozen capture oracle and four12000-step native gameplay schedules; seed0 completes capture/release. Repeated60000-step sweep is deterministic: seed0 completes2captures/2releases and18starts before upper capture; seed1/3 reach31/24starts before same upper capture; seed2 completes60000steps/36starts. Native coverage is not autonomous original trajectory equivalence.

Next primary target: actual upper capture(callback1) runtime→release trace. `analysis/mean-upper-capture.json` records unresolved mode transitions; no partial capture is enabled there.


## Upper capture / mode continuation bundle — 2026-10-09

Upper capture now enters, scores and releases natively through first352-step, second552-step and repeated-mode5 252-step sequences. All1156 original callback states (100ball bytes, slots, timers, gates and base scores) replay exactly. Original slot delays300/400 come from actual40f754 execution; no fabricated DMD completion. Original406840/422f40 RNG drives direct release; native deterministic reset seed1 is a deliberate seed policy, not the unknown original time seed. Entry512cases and RNG/release/transfer1024cases match.

Mode5 left capture also continues:500000 then initial10000000 award,153step transfer; first two awards bounded, third/full reset remains unsupported. Actual second-cycle memory confirms05c=10000000,058=0,1e6=0,3b4=0. Layer2 Y<60 velocity reduction added; switch comparison now896cases.

All four native schedules complete120000steps/ten simulated minutes with44/73/68/66 launches and32 total captures/releases. Repeated sweep identical; sixCTest cases pass, including full upper oracle and120000-step gameplay bundle. This is native coverage, not live-original autonomous trajectory equivalence. Next: original mode5 third-award/reset flow, before further rule expansion.


## Mode5 timer/reset island — 2026-10-09

Implemented200Hz award timer, terminal award/timeout reset, cyclic next-mode selection and preserved capture/release. Native constant10000000 was only initialization: next originalframe computes20600000 at timer8400; award follows65000000-(timer-1000)*6000, jumps75000000 below1000. Negative post-decrement timer ends mode. Third award resets after counter increment;75000000 resets without increment. Reset selects next unlit mode, preserves ball/slots/award sums and sets43f366=-1.

1499original-x86/native comparisons pass:1009timer/wrap cases,480selection cases,8terminal awards,2full253step reset/release cycles. New frozen CTestmean_mode_island_oracle passes; five existing component/oracle tests pass. Existing mean_gameplay_bundle remains FAILED: realreset now selects43f1e6=1, whose upper rule phase is unported. No test weakened or hidden. Three native schedules stop there after60140/112778/107700successfulsteps; fourth completes120000. Previous all-active run used incomplete mode timing.

Next: selected43f1e6=1 upper-capture rule phase, keeping genuine mode transitions. Full lamps/DMD/audio effects remain excluded.


## Follow modes + sixth capture island — 2026-10-09

Implemented bounded selected modes1/2 entry, signed200Hz timers9400/6400, timeout reset, and upper/left hold→transfer→release. Initialization preserves existing award/counter for1/2; selected2 field38c uses original engine38 lookup{4,5,4}; unknown fields retain address names. Sixth left capture requests25500000points, actual740-step extra delay and reward/counter writes; five893-step original cycles match.

Verification:3523mode-clock/reset/left cases +2260upper states +18initialization sentinel/all-lit cases +4465sixth-capture states =10266original comparisons, zero differences. Build and8/9CTest pass. Existing120000-step all-active regression remains failed: three schedules complete, seed0 advances from60140 to116726successful steps/52launches before upper reward service415e3f. Native explicitly stops before consuming sixth-capture reward flags; DMD-dependent gate completion is unproven. No autonomous original trajectory equivalence claimed.

Next: prove upper reward415e3f→gate43f364 clear→ball release, especially field200 generated by the sixth left capture. Do not fabricate DMD completion or skip the reward flags.


## Upper rewards through actual display completion — 2026-10-09

Implemented rewardpriority200→202→1fa, field378/1fc mutations, extra-ballWORD increment, original finite display clocks and realidle-gate release. Service405f98 directly installsstate4/active2; tabledisplay419890 precedes50Hzscheduler4071e8. Reward410a34/410910/410d34 finish at171/162/200displayticks. Gate413b60 runs only when idle, not unconditionally. Reward3 lamp-service requests/slot438afc are preserved; lamp visuals remain omitted.

Proof:45rewardentry cases,533original display states,2030complete reward1/2 capture→display→release states, zero differences. Fullcycles1033/997steps compareall100ballbytes plus timers/slots/gates/score. Reward3display additionally executes actual lampservices405da8/405e48. Selected3entry also located: shared+44=1 starts a separate minigame and leaves tablemode2; native explicitly stops at this event instead of inventingmode5.

Build and14/14CTest pass. Gameplayregression now additionally requires an actualreward completion. Four120000-step runs finish; repeatedcoverage identical. Extended240000-step run: seeds0/1/2 stop at160417/174316/233331successfulsteps on mini-game dispatch;seed3 completes240000. Coverage uses synthetic nativeinputs, not fulloriginaltrajectory equivalence. FullDMDgraphics/queue/preemption and other modeevent rules remain outside this bound.

Next primary target: shared+44 minigame dispatcher entered415b9a, through genuine completion/resumption.


## Mean car minigame island — 2026-10-09

Native selected3 capture now runs the original bounded minigame dispatcher at50Hz, with Shift steering, original96x20 two-plane DMD data and genuine completion/resumption. The200Hz loop preserves RNG/flipper stepping while physics and ordinary table-display slots pause. Generated static C++ remains local underbuild; presentation/audio adapters are bounded, not a runtime x86 interpreter. Winning completion requests120000000points, increments the original extra-ballWORD flag and installs1100display-tick secondary slots; failure paths also return to the captured-ball lifecycle.

Proof:2672original dispatcher states (four input schedules),1024input cases,288terminal cases including4wins andWORD wrap,32DMD cases/61440pixels, zero differences. Build and19/19CTest pass. Four native200000-step schedules finish; two complete the minigame and resume the table. Repeated sweep is deterministic. This is native coverage, not live-original autonomous trajectory equivalence. DMD font/announcement services, audio and lamp presentation remain bounded/omitted; minigame pixels use grayscale.

Fixtures/index: `analysis/mean-minigame-island.json`, `analysis/traces/mean-minigame{,-input,-terminal}-fixture.json`, `analysis/traces/mean-minigame-gameplay-validation.json`. Rebuild local island with `build/venv/bin/python tools/lift_mean_minigame.py` and `build/venv/bin/python tools/verify_mean_minigame.py`, then CMake build. Preview: `tools/slamplay --minigame-preview`; Shift steers.

Next primary target: selected4 upper-capture rule phase, reached at205917/231979steps in extended native coverage.


## Mode4 entry / transfer / timeout — 2026-10-09

Implemented selected4 initializer415c86, verified stage1 clock414e79, and original416b28 transfer to(13,306), capturedstate3/callback5. Upper ready-slot stage1 becomes2 and writes438b90=200,3ae=750,43f260={4,3,1,0}; this is a multiball-spawn boundary, not ordinary417068 transfer. Native stops explicitly before unimplemented4151e4 allocation. Stage3 keeps the ordinary transfer; mode4 lamp descriptors retain original address names.

Proof:802original entry/timeout states and128transfer cases compareall100ballbytes plus stage/slots/descriptor effects, zero differences;21/21CTest pass. Four200000-step regressions still finish. Extended240000 coverage now reaches206318/232380successfulsteps for seeds0/1,402steps past previous boundary, stopping at real stage2; seeds2/3 complete240000. No whole mode4/multiball or original autonomous trajectory equivalence claim. Fixtures: `analysis/traces/mean-mode4{,-transfer}-fixture.json`; RE index: `analysis/mean-mode4-consumers.json`.

Next: engine+20 allocation →4151e4 spawn sequence → native ball pool with shared table rules.


## Native multiball / eject lane island — 2026-10-09

Implemented8-object pool, original4151e4 sequential extra-ball spawn, callback5 held→active release,417238 eject-lane guide,200Hz per-ball stepping and exact bounded408bfc ball-pair response. Shared RNG/flippers/table clock run once perstep; original order is step(i)→pair(i,j>i). Renderer draws every ball with its own original anchor/interpolation; HUD shows active count. Drain marksstate5; sweep copies last100bytes into removedslot and incrementsi without rechecking replacement. Native removal uses deterministic50Hz presentation cadence; original caller404d6f is render preparation with variable timing unverified. Spare native pool objects begin zeroed; exact original startup spare context was not captured.

Fixed real eject-lane blocker: oldnormalcache excluded rows608..615 and nativeguard stopped at608. Layer1 now includes812additional actual40e1d0 queries and bounds616. `prepare_mean.py --extend-bottom --layers 1` updates an existing cache; default preparation also includes layer1 bottom rows.121original release-flight states now matchall100bytes after relocation ofthreeDATpointers, with cachedrestflippers andpointforcesdisabled.

Proof:1757original componentcases (432pool/spawn/removal,1024pairs,49held-release cases,252guide);24/24CTest pass. Four225000-step schedules finish; repeatedcoverage identical. Seed0 spawns3additional balls,max4,returnsingleball andmode2/selected0. Extended300000 sweep: allfour schedules exercisefour-ball spawn andreturn;seed3 finishes,others reach nextupperrule boundary at232172/252413/273912successfulsteps. This is nativecoverage, not fulloriginalautonomousplay equivalence; mode4 rule/score/lamp/DMD completeness remains unclaimed.

Preview: `tools/slamplay --multiball-preview`; screenshot `build/mean-multiball-four.png` visibly shows twooriginalballs. Generated original-derived pair code remains local underbuild (`tools/lift_mean_ball_pair.py`). Evidence/index: `analysis/mean-multiball-island.json`.

Next primary target: upper415330 branch withfield43f1f2>=5 afterallfive modes.


## Mean eight-ball / mode6 island — 2026-10-09

Implemented post-five-mode upper entry415567, uninterrupted410b00 announcement gate (43f382 clears on50Hz tick268), seven-extra-ball4151e4 spawn, state6 capture-count gates, callback2/4 side clocks, and414e79 expiry back to mode2. Reuses verified ball pool, pair collision, sprites and eject-lane guide. Upper stage1 uses3ae=1000 (mode4 uses750). Side capture requires captured_count-active_count<-1; upper requires<0. Transfer respects sharedslot74 occupancy.

Proof:4798 original boundary cases (30entry+480capture+192clock+4096side),270 exact displayticks; four400000-step native schedules finish, each reaches8balls andreturnsingleball. Seed0 repeat is identical. Final build passes27/27CTest. Native coverage is not full original trajectory equivalence. Announcement rendering, lamp reset presentation, player08 bonus and full mode6 scoring remain pending; callback4 entering context is not gameplay-validated.

Preview: `tools/slamplay --mode6-preview` enters the actual post-five-modes capture path; no substitute physics. Fixtures/index: `analysis/mean-mode6-island.json`.

Next: original lamp/score feedback tied to already-proven gameplay events.


## Original lamp/score display island — 2026-10-10

Implemented63 original lamp masks (4387ac/43f208), all408110 command states0..6, and original MAIN.DAT score glyphs including12-digit BCD formatting. On clears indexedpalette bit7, off sets it in the bounded parentptr0 path; dynamic occlusion path differs and is not claimed reproduced. Native renderer overlays sparse masked pixels below contact/flipper/ball sprites. Original reset starts descriptoron=false/commands2; proven mode arrays23c (lamp13..18) and260 (lamp22) drive current gameplay lighting. Other rule/selection writers remain unmapped. Lamp consumption uses native deterministic50Hz presentation; original variable render-preparation cadence unverified.

Proof:630clockcases/5040states,126on/off full-canvas patches,36scorecases/69120pixels exact. `cmake --build build/native -j4` and30/30CTest pass; four400000-step gameplay checks complete. Screenshot `build/mean-lamps-score.png` from native SDL mode6 preview. Fixtures/index `analysis/mean-lamp-score-island.json`; assets remain user-provided.

Next: switch/selection rule writers → remaining original lamp commands.


## Mean lamp-rule / target-reward island — 2026-10-10

Implemented original419f6c/41a54c63-command rebuild with explicitfield inputs; mode reset, minigame exit and new-ball callback boundaries integrated. Native first-ball uses same callback andexplicitdefault inputpolicy. Top targets41c974→41d0fc drive lamps30..32/flags1e8; completedgroup continues41d153 through438e44 lookup, player+12 progression, extra-ballavailability1fa/lamp59 and10M scoring branch. Player+12 reset1 is proven4077bf; native startup1 uses same resetpolicy. Remaining rebuildinputwriters, targetDMD services andfull419b00/bonus lifecycle unported.

Proof:1848originalcases (1024sentinel rebuild,504target,320reward) exact. Build `cmake --build build/native -j4` and `ctest --test-dir build/native --output-on-failure -j4` pass34/34. Four400000-step native schedules complete,98targethits/14groups; native coverage is not originalwholetrajectory equivalence. Screenshot `build/mean-lamp-rules.png`; index `analysis/mean-lamp-rules-island.json`.

Next: original419b00 ball reset plus bonus/turn lifecycle.


## Mean ball-reset / bonus / save / turn island — 2026-10-10

Implemented419ad8 persistent52-byte record,419b00 reset/419da4 mode selection,40735b low32 bonus multiplication and407794 turn/extra-ball arithmetic. Native game starts with an explicit empty player record, applies original reset, enters mode1; actual layer3/switch1/Y90..116 route41b184→41b210 entersmode2,3ae400,35a200 andlamp21/23commands.41aaac ball-save retains pool count; singleball consumes save, multiball retains timer.4199a6..419a97 common timers run50Hz beforelamp consumption, not200Hz.

Proof:3040 original bounded cases (512reset/save,1024bonus/turn,480entry/save,1024clock), plus23actualengine caller ordering cases. Build and39/39CTest pass. Four400000-step ordinary schedules finish:509bonus/turn completions,303saves; repeatseed0 identical includingall100finalballbytes. Controlled original capture entries now isolate multiball/mode6/minigame/award coverage; assertions remain, held spawnedballs count toward capture/release diagnostics. Screenshotbuild/mean-turn-lifecycle.png.

Limits: native immediately completes bonus DMD phase and directly reinitializes saved balls; original43e79c initializer gate/presentation scheduling is not reproduced. Runtime service1c andbonus-suppression43d864 currently use nativezero policy. Multiplayer helper arithmetic verified but native frontend remains singleplayer. Finitegameover limit, completebonusbank writers andDMD still pending. No whole-original trajectory claim.

Next: original43e79c saved-ball initializer gate plus finite turn/game-over boundary.


## Saved-ball queue / complete native game island — 2026-10-10

Implemented shared43e79c gate:408915 stateFFFF/gate<=0 initializes andsets1; gate>0 waits. Every original41b1f8 layer3/switch1/Y90..116 exit decrements gate, independentlyof tablemode. New-ball turn nowleavesstateFFFF (4080e0), preservinggate through407808; nextphysics initializes, ratherthan directreset. Diagnostic captureentries setgate0 becausefixturestartsafterlaunchlane.

Full4083a9..4083cb providesfinite boundary absentfromDemo: selectednextplayer signedballWORD>=4 if454aa4=0, otherwise>=6. Nativefrontend explicitlyadopts Fullzero-fieldpolicy (threeballs); no inventedmeaning for454aa4. Gameoverclearstablemode/playercount/ballcount, engine40=3; score remainsvisible, simulation stops, R resetsnewgame. Endlesspolicy isexplicit onlyin probes; gameplaychecks retaincoverageassertions.

Proof:112originalgatecases,8drain/turncases,52Fullpredicatecases exact. Build+42/42CTest pass;fourfinitegamesfinishat6047/11275/9398/8076states, allfreezeandresetchecks pass;seed0repeat identical. Existing four400000-step eightball sweeps remainactiveandreturntosingleball;2008queuedwaitsteps exercised. `tools/slamplay --game-over-preview` usesactualnativeinputs toreachgameover; screenshotbuild/mean-game-over.png.

Limits: physicsremainsDemobased, Fullcontributesboundedendpredicate only. OriginalbonusDMD/qualifyinghighscoreentry presentation stillskipped; no originalwholetrajectory equivalence. Fiveballflagmeaning, multiplayerfrontend andremainingbonusbankwriters unknown/unported.
Next primary target: originalbonus/DMD dispatch → visiblebonusphase beforeturnadvance.


## Original bonus DMD / deferred turn island — 2026-10-10

Implemented4072cc bonusdispatcher andactual419554 tablecallback:phase0 booksbonusonce,65callbackticksfinishintro,bank/multiplierdisplaythenTOTAL SCORE,turncompletiononlyafteroriginalphase5timer. StandardMean186ticks;positivebankwithmultiplier!=1 uses248ticksat50Hz. Uses24originalMEAN.DAT framesat11cc4e,originalMAIN.DAT textglyphs91b4 andexistingverifiedscorefont. Physics/tableclocks suspendinmode3; RNG/flipperupdatescontinue200Hz (404a12..404a52). SharedDMDpanelshowsbonuswithoutcoveringnativeheader.

Proof:1200actualdispatcher cases+172originalpixel/callback cases (42text/background,64introframes,66clockstates), all exact. Build+44/44CTestpass. Fourfinitegamesfinish10384/11172/10380/11016states;each3bonuscompletions/558displayticks,ballbytesandballnumberfrozenbetweenboundaries,bookings=starts=completions;seed0repeatidentical. Existing400000-stepregressionspass. Previewtools/slamplay --bonus-preview; screenshotbuild/mean-bonus.png.

Limits: nativeplayer+0c remainsunknown/default0 althoughstage0score1M*signedWORD isisolatedandverified;bonus-bankwritersincomplete. Fastskipfield43e734 remainsnative0;clockhelperstep4 verifiedbutinputmappingunported. BONUS HELD/per-playerretentionwritersandFullhighscoreentryunported. No originalwholetrajectory equivalence.
Next: connectexistinglibxmp musicandfirstgameplay-triggeredsounds;avoidnewdecoderRE.


## Native Mean audio island — 2026-10-11
Implemented optional libxmp→SDL3 stereo44100 output, device conversion, bounded100ms queue, SPACE pause/M mute/R restart. Native Mean loads two original Windows STIM banks directly from user MEAN.DAT; no extracted assets committed. Selected3 initializer415c54/415c67 queues88(bank1,order53),84(bank0,order23). Original4059ac/405af3 priority: one foreground,88 pauses84, resumes savedPCM or deferred replacement84; no simultaneous mixing. Explicit --music MODULE/--music-order N remains available; --no-audio disables playback.
Proof: independent extraction/native byte equality for both banks; six Windows orders render nonzeroPCM; native Amiga Music/Intro PCM hash matches existing oracle at three chunk sizes; restart, SDL dummy queue/pause, sequencer preemption/resume/pending/chunk invariance tested.
Limits: ordinary startup music request UNKNOWN (native starts silent until proved cue or explicit --music). Common-contact SFX unlocated. Order56/73 belongs to unported callback4 sidecapture table_mode<4+field43f3a2 path, not selected4 multiball; deliberately unconnected. F00/first-loop termination is bounded native policy, original exact completion timing unverified. M pauses output; no listening comparison claimed.
Next: original startup/background music request + common-contact cue writers.

Validation: cmake --build build/native -j4 PASS; ctest --test-dir build/native --output-on-failure -j4 PASS48/48; SDLdummy tools/slamplay --minigame-preview --frames120 PASS. No Git metadata available for diff.


## Base music + bonus audio — 2026-10-11
FOUND: Original419d88..419d95 ends419b00 reset with service90(order4,bank0).405824 storesbase request429798/42979c and clears84pending, requests88stop.405a2e resolvesbank andstarts422658; base snapshot43dca0 under84, snapshot43df78 under88.419554 stage0 requests88(order49,bank1).
IMPLEMENTED: native90 replacesbase andclearsbothhigherlevels;84/88 pausebasewithoutadvancingPCM;stop84 restoresbase. Initialgameandnewball resetemit90/0/4;bonusstage0emits88/1/49once. Defaulttools/slamplay nowhasoriginalbase music without --music;R restartsit. Baseuseslibxmpcontinuousloop;highercueF00/firstloopcompletion remainsnativepolicy,exactoriginaltimingunverified.
PROOF: analysis/traces/mean-audio-base-original.json:7boundedoriginalcaller/requestcases. SequencerPCMtestcoversbasepause/resume+replacement;8actualWindowsordersload/rendernonzeroPCM. Buildand48existingtestsPASS,newmean_audio_base_oraclePASS;SDLdummy120normalframesPASS. Listeningcomparisonnotclaimed.
NEXT: common-contact descriptor consumer/service5c versusactualsoundwriters;do notattachunknownsampleIDs.


## Original direct-SFX island — 2026-10-11
Implemented MEAN.DAT direct PCM437cf0(offset63a1d,length6465,period160,volume64): launch41ac6c arguments9/8,acceptedmaterial7 41e717 arguments4/3. Also437d14(offset6535e,length4078,period226,volume64):material3/4 callbacks41e0b5/41e184 arguments6/5. MeanContactEvent forwardsprovenrequests;SDL mixes2SFXvoicesoverexistingmusic.
Evidence:405c60 FIFOdeduplicatesdescriptor,retainsfirstarguments;401760 resolvesdirectpointer+14,length+0c,period+4,volume+8;4016dc slots4/5 allocation exact.40f053/40f065 DATrelocations;401838 integerfrequency3546895/period. Fixtureanalysis/traces/mean-sample-consumer-original.json;indexanalysis/mean-sample-island.json. No originalassetscommitted.
Limits: signed8/nearest-neighbor44100Hz/centerstereo/fullvolume/saturatinggainareexplicitnativeoutputpolicy;originalfinalmixer/resamplingequivalenceandlisteningunverified. Native completionclearsprioritymarker;exactoriginalmarkerclockunverified.437da4/material5rulebranchesremainunported. Queueconsumedatnativeaudiofillcadence,up to100msqueuedlatency.
Next: originalsharedSFXmixer/timingcomparison beforeadditionalrule-specificsoundmapping.

Validation: cmake --build build/native -j4 PASS(no warnings);ctest --test-dir build/native --output-on-failure -j4 PASS52/52;SDLdummy tools/slamplay --frames120 PASS.


## Original mono SFX timing/gain — 2026-10-11
Implemented420120 integerfrequencyQ32step (low4fractionbitscleared),41eb60 lookupgain (sixvoiceconfig401551/4015af,master65536,fullvolume64→row127),signedarithmeticfloor andexactsampletermination. Replacesnative256amplitude/exactrationalphasepolicy. TenoriginalPCMcases (bothperiods,1/100/1000/2048/20000frames) provefullmonoPCMhash+Q32phase/endfrequencyzero;nativehashesmatch,tailssilent. NativeoutputstillcentersSFXinstereoandadds/clampsagainstlibxmpmusic;notwholeoriginalstereomixerequivalence. Originaldeviceclock/9-blockconversioncadence unported.
Evidence:analysis/traces/mean-sample-resampler-original.json;tools/verify_mean_sample_resampler.py;tests/mean_sample_resampler_probe.cpp. Largefinal41eddcdeviceformatmixer intentionallynotlifted;bounded420120/LUT sufficient.
Next: material5contactrules→originalsample437da4/lamp300,usingexistingprovenrule/scoreinterfaces.


## Material5 contact/group island — 2026-10-11
Implemented41e269..41e7fe: x<=80/x<=160/y<=270 targetselection, signedpositive43ee1c..22cooldowngate→5 (existing50Hzclock),63lampcommands25..28/62, persistentflags43f1dc..1df. Fourflagcompletion resetsflags,commands25..28={6,2,index1..4,50},sets43f1da=1andlamp24byte0=1;nextacceptedmaterial7 consumesflag,starts250clockandoriginal268blinkcommand. Base50000contactscorepreserved.
Original437da4 SFX(offset6aaa4,length3026,period226,volume64) nowthirdprofileinexistingtwoSFXslots;args3/3. Originalqueue/consumerthirdprofileverified;15monoPCM/LUT/phasecasesexact. y>350 branchalwayssamples/lamp62;mode<4+37a>=0 sets37a=-1,addsfield054,stops84. Nativefield054remains0policy;nonzeroinputhelperverified.
Proof:1344original/nativecases covercoordinateboundaries,16flagpatterns,cooldowns-1/0/1,modes2/4,37a-1/0. Four400000-stepnativeordinaryschedules reach374acceptedmaterial5events/25groups (83/9,88/9,144/2,59/5),remainactiveandretainturn/savecoverage. Nativecountsarecoverage,notoriginalwholetrajectoryequivalence.
Limits:413a2c/413958/41062cDMDcallbacks recorded/returnedbutpresentationunported. Original43f050displaycopy/field054writersnotintegrated;highermodebonuswritersunmapped. FinalSFXstereomix/devicecadenceremainnativepolicy.
Next: originalfield054awardwriters andmaterial5DMD callback presentation.

Validation: buildPASS(no warnings),55/55CTestPASS;strengthenedmaterial5gameplaycoveragePASS;SDLdummy120framesPASS.


## Material5 original DMD callbacks — 2026-10-11
Implemented413a2c target50-tickdisplay (DAT144d8e +480*(activeflags-blink)),413958 group105-tickdisplay (invertpriorpixels,4holdticks,100alternatingblank/frame150e2c),41062c award155-tickdisplay (10frames1483ee repeated4ticks,invertat50,100score/blankticks). Originalservice50 ispixelinvert40607c,notclear;firstawardscoreoverlayretainspreviousbackground. Parserloads17original480-byteframes (includesvalidframe-1),existingverifiedMAINscorefont reused.
Nativecontactcallbacksstartdisplay;deterministic50Hzpresentationclockupdatesitwhileballphysicscontinues. Bonus/minigameoverridepanel;bonus/newturnclearpendingmaterial5callback. Previewtools/slamplay --material5-preview usesactualnativephysics/flipperinputs,endlessonlywhilefindinggroup,thenrestoresfinitepolicyandpausesatvisibleframe;capturebuild/mean-material5-dmd.bmp.
Proof:1390actualcallbackpixel/statecases (16flagmasks,completegroupcycle,3awardscores),allnativeFNVpixelhash/counter/endstatesequaloriginalservices. BuildPASS(no warnings),56/56CTestPASS,SDLdummygroup-preview1framecapturePASS. Whole-screenshotvisualinspectionnotperformed(BMPviewerunsupported).
Limits:originalsharedschedulerpriority/delay/cadenceunported;nativeimmediatecallbackreplacement+50Hzpolicy. Awardcounter45services70/68and438afc..b04sideeffectsexcludedfrompixeloracle/unported. Field054reset0known,writer415148/41d32b/41d4aeLOCATEDbutcallerconditionsunported;nativeawardbankremains0. No wholeoriginalDMDschedulingequivalence.
Next: field054writers→realnonzeroawardandoriginalbanktimer.


Award-bank island: IMPLEMENTED bounded41ce03..41d0fa/41d294/4150b8. Five lower switch targets activate37a=6000/054=60M;200Hz timer decays to10M, Material5→score/41062c consumes once. Lamps33..37/62 and84 order62/80 wired.1550original/native cases plus activation→100ticks→59M collection/expiry chain pass;57/57CTest,SDLdummy120frames. Native-only4×800000steps:15activations,0collections (collection integration not reached in sweep). Activation4107c8/midpoint41086c/expiry410504 DMD and41d220 secondaryreward,41d46f alternative writer remain unported. Next: activation/timer DMD callbacks as one display island.


Award-bank DMD island: IMPLEMENTED4107c8/41086c/410504. Activation/midpoint48animation+100message ticks;expiry24animation+5hold+12checkerboardfade ticks. DAT1496ae/150a6c/150c4c/1474ee assets read fromuser files. Existing6callback oracle now1730exactpixel/countercases;sharedschedulerand70/68setup remainexcluded/native50Hz immediate replacement. SDL --award-bank-preview reachesrealnativeactivation,capturebuild/mean-award-bank-dmd.bmp. Next:41d220 side-target reward chain,currentlyomitted lower-switch effect.


Side-extra-ball island: IMPLEMENTED41ce2b/41d084→41d220→player10/lamp23,60,61→existingbonus extra-ball lifecycle;field1fc clearedonce.150original/native gate/state cases pluscollection→bonus consumption/ball-number chain. Native-only4×800000steps:2sideextras(seed0),allactive. Complete410e4c DMD(122ticks+termination),frame13b00e and16maskedtailframesfdd4e.1976exactpixel/countercases across7callbacks;58/58CTest. SDL --extra-ball-preview reachesrealnativeevent,capturebuild/mean-extra-ball-dmd.bmp. Original43efd0 allocatorzero proven;indirectwritersnotdynamicallyexcluded,nativerestoredefaultzero explicit. Next:alternative60M writer41d46f anditslivecallbackboundary.


Switch-reward island: IMPLEMENTED41d3e4..41d8af cashplus7selectors inclalternative60M.216original/native fulltable-statecases; common40fdecDMD now16856exactpixel/countercases across8callbacks. Live41de3d writer3b6=100→50Hz419903decay→41cb1dgate consumes3b6/35a→dispatcher;41cad4 adds500k deferredbonus.4×800000native-onlysteps:22rewards,allactive;59/59CTest,SDL --switch-reward-preview reachesactualreward/counter56,capturebuild/mean-switch-reward-dmd.bmp. Sevenselectorbranches boundedverified;live358toggleinputunlocated,normalnativeusescashbranch3580. Following41cb28combo/progression and40f754delay/DMDscheduler stillunported. Next:prove358toggleinputboundary inWindowsFull andwireverifiedaction.


## Flipper input / reward selection island (2026-10-11)
- Registered callbacks417374/41766c now run on native Shift rising edges: rotate target groups, swap extra-ball side, right-flipper reward selection in mode1, original437d38/437d5c PCM. Engine dispatch40436c/4043d2 uses edges+1/-1; registration43f348/43f34c. Earlier417984 dead-stub blocker superseded.
- Exact bounded checks:960original input cases,25PCM resampler cases. Fixtures:analysis/traces/mean-flipper-actions-original.json and mean-sample-resampler-original.json. Long native stress:mean-flipper-actions-gameplay-validation.json; synthetic input, no original trajectory equivalence.
- Selector3 sets392=-1, which original416246..4162b7 activates as mode4; next release416440 calls416ca4 and creates ballstate7. This gameplay island remains unported. Native keeps original reward lamps/DMD but explicitly defers392 activation (pending_mode4_rewards), avoiding unsupported capture/freeze. Other reward variants remain enabled.
- Next primary island: original mode4/state7 release, gameplay tick and input as one bounded vertical slice.


## Table-mode4 phase0 / state7 island — 2026-10-12

Implemented original callback2 activation → sinus-guided state7 → callback5 hold → flipper-selected release → switch reward or350-step return clock. Selector3 activation is enabled; prior392 deferral removed. Common flipper rotations/SFX now include Mode4. UserDAT provides original DMD announcement, speed bar, looping launch frames and437dec eject PCM. `tools/slamplay --mode4-preview` shows guided motion; screenshot `build/mean-mode4-state7.png`.

Evidence/index: `analysis/mean-mode4-phase0-island.json`;5159 bounded original comparisons across capture/math/input/clock/pixels/switches; mono PCM coverage30cases. Four seeded native mode4 runs each complete entry/18guidedsteps/return and continue800000steps; four ordinary runs also finish. Four12000-step cycles plus exact deterministic repeat are the new gameplay regression. These are native composition checks, not autonomous original trajectory equivalence.

Limits: native immediate DMD replacement/50Hz idle policy remains; shared original queue/preemption is unverified. Winning41249c/end4126ec panels omitted. Right ramp sets3a6=1, right capture sets3a6=2: their entry/gameplay chain remains partial despite bounded input/clock helpers. Next primary island: both right entries through events/scoring and return.

Validation: `cmake --build build/native -j4` PASS (no warnings); `ctest --test-dir build/native --output-on-failure`68/68 PASS. Native SDL dummy120frames PASS; exported PNG inspected. Common flipper input1152originalcases now includesMode4; audio30PCMcases plus actual437dec queue consumer verified.


## Mode4 right-entry / second-minigame island — 2026-10-12

Implemented phase1 right-ramp entry,4141b8 idle-driven3aa=-1→0/countdown/Shift action,25M-first/10M-repeat reward and mode2 exits. Phase2 callback4 now holds→starts original second minigame→Shift accelerates→score/timeout/failure→held ball resumes/release. Original integer code remains a bounded local static intermediate; userDAT supplies graphics. Right-capture sample437dc8 (40f0ba offset6b676,length7576,period226,volume64) added to mixer. Preview: `tools/slamplay --minigame2-preview`; screenshot `build/mean-minigame2-native.png` inspected.

Evidence/index: `analysis/mean-mode4-right-island.json`.360entry+288events+180idle pixel/state+336input comparisons;10minigame cycles/10112states exact across timeout/failure/success. Eight native12000-step right-entry/return cycles continue, deterministic repeats pass. Native scenarios explicitly inject verified entry setup; they do not prove natural marker20 activation or original whole-table trajectories.

Remaining: complete416fe0 armed-right gate plus marker20 writers41cdd6/41ded1 are not integrated; normal autonomous right-capture activation unverified. Phase1 intro/exit panels and original DMD queue omitted; native immediate50Hz idle policy. Minigame2 intro text/numbers/countdown SFX438050 omitted. Initial player1f6 challenge threshold unverified; original success branch fixture uses explicit synthetic20000. Next primary island: armed gate→marker20→natural right capture.

Validation: build PASS without warnings; full74/74CTest PASS before final sample extension;10/10 affected checks PASS after it, including35original/native mono PCM cases. SDLdummy120-frame second-minigame preview PASS, PNG visually inspected.


## Right route / natural arming island — 2026-10-12

Implemented41cb28 lower timed switch combo/progression→3bc2→3a2=-1→416fe0 armed gate→bothmarker20 writers→original right-guided collisionpointer→callback4→existing second-minigame/release. Corrected newly ported extra-ball progress lamp to AFTER increment index, proved by oracle. Reset initializes native raw layer directory from known original descriptors; no stale emulated pointer copied. Index: `analysis/mean-right-route-island.json`.

Proof:648originalprogress states+384gate/marker states exact. Twelve12000step native cycles, including4realbitmap-switch→marker20→right-capture cycles, deterministic repeats pass. Fourordinary800000step native sweeps allactive;2naturallyarmed gates,0rightcaptures. Thusnaturalarming is exercised, autonomous right-capture traversal remains unverified. SDL --minigame2-preview now uses actualbitmap marker route;120framesPASS,build/mean-right-route-native.png inspected.

Limits:targetedroute fixture seeds verifiedprogress andballatactualswitch;notwhole-originaltrajectoryequivalence.41b8d0andprogressionpanelsunported. Minigame2thresholdprovenance `analysis/mean-minigame2-threshold.json`:record+22 copied419b8c, cached0;originalinitialvalueUNKNOWN after2targeted attempts. Nextprimary:originalright-directed marker20 traversal vsnative runtime trace.

Validation:finalbuildPASS(no warnings),76/76CTestPASS;12targetedcyclesand4×800000ordinarynative stepsPASS.


## Ball preservation / correct capture boundary — 2026-10-12

FOUND correction: object54 is the original ball/table preservation bitmap read40abf4, not collision geometry. Marker20 doesnot force movement to the rightcapture.1007full100-byte states from6synthetic original4088f0 trajectories match native integration/contact/normal/response/separation;pointforcesdisabled andswitchdispatchsuppressed. Originalnormal44/hit40alreadycorrect. Therefore no artificialrailforce introduced.

Implemented original16x15 outline OR tablemask at40abc8 for every displayed nativeball, includingcbb96-14 specialmask;2074original240-byte comparisons/guardflags exact. Native recomputesalpha atoriginalinterpolateddrawingcoordinates; SDL --ball-occlusion-preview exposes partialballbehindoriginalrail. Original41c93d dispatch/41c966 provesrightcapture belongs layer0/switch3;removed prematurepre-physics x>=260capture.12positivecycles+negative x>=260/marker20withoutswitch3 pass.

Evidence/index:`analysis/mean-ball-preservation-island.json`;physicaltrace `analysis/traces/mean-right-path-original.json`;dispatch `analysis/traces/mean-right-capture-dispatch-original.json`.78/78CTestPASS; SDL120-frame occlusion andcorrect-switchminigame previewsPASS. Limits:naturalrightcapturestillunexercisedinordinarysweep;physicaltraceissyntheticbounded,notwholeliveoracle. Nextprimary:naturalmarker20entryvelocity/eventtrace;originalphysicsalreadyagrees.

Final verification:buildno warnings;78/78fullsuite plus4/4affectedchecks afterpreviewintegrationPASS;bothSDL120framepreviewsPASS;occlusionPNG inspected.

## Armed right-route return island — 2026-10-12

Implemented original41c611..41c6d9 at layer1/mask1/y<60: clears armed3a2/progress3bc, sets364=-1, adds15 to WORD38a, updates exact lamps and416fe0 gate. 180original raw-state cases byteexact; native actual-bitmap targeted return cancels once and returns layer0. DMD413490/scheduler remains external with explicit native return0; service1c==0 gameplay branch only.

Verified408b04 switch boundary in160original cases: solid pixel suppresses dispatch; only changed free-pixel mask dispatches. Corrected marker_a bound to Y (EBX loaded41c98b, retained via41cabd into41cd50);384gate/marker cases pass. Native caller already boundedY, so no invented steering or gameplay force added.

Compact ordinary-input event fixture `analysis/traces/mean-right-natural-events.json`:2×800000steps active, two natural arms, cleared on new-ball reset before right-entry;0markers/0captures. This does not prove a traversal bug. Pointforce provenance recorded separately; runtime list/right-route effect unknown. Index `analysis/mean-right-route-return-island.json`.

Validation:80/80CTestPASS, buildno warnings; existing right-minigame SDL120frame previewPASS. Nextprimary:live-original armed-route entry state/velocity plus startup force-list dump.

## Original Mean phase1 point-force island — 2026-10-12

FOUND retained live snapshot resolves43e740=438ae4→438ac4→438a3c. Original node has264/181/32, type0 by default; existing41b010 phase1 entry sets438a40=-1, clock414e65/right-input417896/exits/reset clear it. Original LUT432ecc is static20000bytes. Previouscachedzero-pointer blocker resolved; no new live game required. This is phase1 magnet, not proof of marker20/right-capture steering.

IMPLEMENTED bounded user-PE data parser and exact40a0e8 force before native integration. Existing native field438a40 gates it automatically; no invented force/lookup.310original100-byte component cases exact. Three100-step original4088f0 flights with active force compare303completeballstates exactly, switchrules suppressed. Separate force-only100-call trace explicitly labeled.

Native1000-step synthetic actual-free-layer2 phase1 cycle:484velocity updates,25contacts,1completion, finaltype0, deterministic repeat. SDL --point-force-preview renders original ball/table after100native steps;120frame capturePASS andPNGinspected.83/83CTestPASS; buildno warnings. Index `analysis/mean-point-force-island.json`; fixtures `analysis/traces/mean-point-force-*`. Original LUT loaded from user PE, not bundled. Nextprimary:phase1 input→magnetrelease→rampreward original/native event chain.

## Phase1 release/reward gameplay island — 2026-10-12

VERIFIED3sequential original chains/996fullraw-state boundaries: earlyrightcancel;481clocks→rightrelease→25Mtop→10Mtop→25Mexit=60M;500clocks→countdownexpiry→exitswitch. Countdownalone leavesmode4/3aa2. Originalexit41c3ce calls416fe0; nativefinish_mode4 now invokes verifiedgatehelper, preserving separatelyarmed3a2 ratherthanunconditionallyclosingroute.

IMPLEMENTEDphase1 numeric composition through existingoriginalfont:180full1920pixel frames match actual4141b8+406280. Fontcodeunchanged; originaloracleinstructioncap was insufficient for longnumbers, now100000+assertreturn. SDLpoint-force-preview now showscountdown5;120framesPASS,PNGinspected.

Nativechain:originalclockreleasewindowtick485,484forceupdates,rightinput→3aa3,actualbitmaptop/top/exitswitches→25M/35M/60M cumulative,mode2,armedrouteopen. Fixture explicitlyseedsball/switchpositions;noautonomouswholetrajectoryclaim.86/86CTestPASS,buildnowarnings, strengthenedchainreturncheckPASS. Index `analysis/mean-phase1-gameplay-island.json`. Nextprimary:shared41b8d0 mode5/mode6 event reward dispatcher, reusingknowncapture/rampcallers.

## Gameplay corpus accelerators — 2026-10-12

Audit found complete USAoriginalrulebook for allfourtables (different from9-pageWindowsPDF), exactnormalizedDemo/Retail/Fix boundedphysics/magnet/progression matches, sixidenticalWindowsMEAN.DAT hashes, andSTRONGfour-tableAmigaABIentrycandidates. Important exception:4390byteDragRace blockhasoneactualscalechange Demo418848×2→Retail425288/Fix425658×4, effectunknown. Noportbehavior changed. Full404e60 four-entrytable isnot a verifiedinitializerlist; olderfirst-pass interpretation mustnot guide newinitialization work.

Index `analysis/corpus-accelerators.json`, report `docs/corpus-accelerators.md`, ruleoracles `analysis/table-rule-oracles.json`; reproduciblecheckedaudit `tools/audit_windows_corpus_levers.py` (fiveanchors/tenranges/sixDAThashes). STRONGMeanbehaviornames:phase1Kickstart,phase2DragRace; manualmode numbering differs frominternalengine. Nextprimary:manual-guidedshared41b8d0event/reward dispatcher andretailadapters; thennexttabledata/callbacks,notanotherphysicsRE.


## Mean manual-guided shared rules + Pirate engine validation — 2026-10-12

IMPLEMENTED shared41b8d0 + Rally4169e4 at all six actual native switch/capture consumers. Monster Car distinct shots5/10/15/20/25/50M→125M and mode2; Rally correct turns15M+2000ticks, sixth turn adds remaining-time reward; Offroad different target15M, immediate repeat0. Mode6 uses original active38e/368/36c timer signs and id2/35e exclusion. Original PE supplies Rally tables438ddc/438df4. Rightprogress41cbc4 hook preserves original ordering: combo writes → commonreward → new-mode gate/progression test.

VERIFIED576 complete shared raw states +288 Rally target states; three handbooksuggested helper chains18events; three native chains17steps at actual bitmap switch pixels/capture timer. Native Rally total211.5M uses original6400tick initial timer, unlike helper fixture's explicit2000ticks (180M). Test ball/mode seeds are synthetic, not a natural playthrough. Scores/lamps/mode changes are native; reward DMD callbacks and scheduler/control services remain presentation adapters.

Pirate actual Full42b390 initializer directory +436428 reset confirmed: three original bitmap/normal/render layers.540 normals Retail↔Demo,506 separations Retail↔native,100 free-flight steps/200 component states Retail↔native: zero differences. This validates reusable engine components, not playable Pirate; MeanSimulation still has Mean-specific directories and normal caches. Index `analysis/mean-shared-rules-and-pirate-island.json`, detailed Pirate proof `analysis/pirate-engine-validation.json`.

NEXT: Pirate contact callback + flipper descriptor consumers → data-driven table profile → contact-inclusive replay. Do not re-analyze shared integration or graphics.

Additional combined proof:72 full raw states match actual41cb28→41b8d0→rightprogression, including Monster/Rally completion changingmode before the gate test. Full91-test regression passed; one subsequent combined-oracle test added. SDL120-frame point-force preview still renders correctly; screenshot `build/mean-shared-regression.png`.

Final verification: build without warnings;91-test full suite PASS, added test92 PASS; strengthened shared/target/combined exit assertions PASS.


## Corpus second pass — 2026-10-12

VERIFIED all four Retail initializer returns and shared descriptor→engine→layercallback consumer. Profile records `analysis/table-profiles.json` expose original Mean4/Pirate3/Space4/Demon3 initialized layers and switch callbacks; callback-created special layers remain outside base profile. Pirate switch callbacks437460/437bfc/438954;4364c4 is engine+0c. Demon init40febc.

VERIFIED24 extracted DAT copies have one hashfamily per basename; USA gameEXE=RIP, UK=ROM. GermanEXE is installercontainer.120 original arithmetic microtraces +2 dispatcher traces correct prior scaler association:×2/×4 difference lies in shared car variant1, not Drag Race variant2. Port behavior unchanged; audit scripts all pass. Index `analysis/corpus-accelerators-v2.json`, report `docs/corpus-accelerators.md`.

NEXT: adopt descriptor-driven table geometry and adapt Pirate contact/flipper consumers; compare contact-inclusive traces before additional table rules. Reuse existing engine math and identical DAT profiles.


## Shared table profiles / Pirate contact island — 2026-10-12

IMPLEMENTED `src/assets/table_profile.*`: allfour original initialized directories, DATbounds guards, shared layer assignment/bitmapconfiguration; Mean nowdelegateslayer writes andnormalcache bases. Separatelyverified Mean transientlayer4 remains explicit; shiftedcapture bitmap pointers arepreserved.56complete original40f8a0 helper states acrossallfour tables match. SDL`--collision` nowloadsprofile byoriginal DATbasename forMean/Pirate/Space/Demon; allfour capturesPASS, visuallyinspected `build/four-table-profile-overlays.png`.

IMPLEMENTED Piratecontact`src/physics/pirate_contact.*`: exactsharedtransform+threeactual materialcallbacks438ea0/4397d0/439994.1188supported fullball states match;212 unsupported cases false+unchanged. VerifiedPirate clamp−512 differsfromMean−256. `pirate_wall_contact` joins response→profile bitmapconfiguration→originalshared separation:506realbitmap cases,494supported complete Retail40a884+40aa10 outputs exact,12unsupported unchanged. Moving-surface offsets explicitlyzero; verifiednormal inputs andsyntheticvelocities, notliveplaythrough.

IMPLEMENTED`src/assets/table_flippers.*`: actualgraphics+0c/+10/+14 parameterparser, startupcopy layout andoriginalinputedges(+1press/−1release/0idle) intoexistingcompiledlift. Allfour tables×240 complete78byte input→pose states matchRetail. Graphics+04 isguidedmotiondirectory, notflippers. Pirateball/flipper normal/scratch comparison unresolved; no contact/response proof fromposes. Diagnostic`--contacts` intentionallyexcludedfrompassing oracle.

VERIFICATION: CMakebuild no warnings;96/96CTestPASS (`build/table-profile-ctest-final.log`); newCppfiles clang-formatted, PythonchecksPASS. Updated legacyrightgateoracle tohonor supplied CMakeprobe ratherthan recompiling mean_step.cpp withoutitsnew profiledependency; original384cases unchanged. WorkspacehasnoGitrepository, soGitdiff unavailable. Index `analysis/table-profile-contact-island.json`.

NEXT: resolvefirstPirate flippercontact mismatch via targetedcallee/LUT/contextwrite trace, thenjoin provencontact/separation into contact-inclusive gameplay. Mean remainspriority; table rules andfullPirate gameplayunverified.

## Retail flipper contact island — 2026-10-12

IMPLEMENTED: bounded actual Retail C++ lift (generated only under `build/generated`), exposed as `retail_table_flipper_contact` in `src/assets/table_flippers.*`. Original contact `0x409ce8` and response `0x40a380`: 2,400 complete ball/result/scratch comparisons across four tables; 965 hits. Prepared original startup poses with explicit supplied Demo-derived shared globals/LUTs; no live-context or Demo/Retail-equality claim. Existing Mean backend unchanged. The older Demo/Retail mismatch no longer blocks this separate Retail path.

NEXT: verify original caller ordering/offsets and compose Retail flipper contacts with the proven Pirate wall pipeline.

VERIFICATION: native build without warnings; **97/97 CTest PASS**, including production Retail adapter oracle (`build/retail-flipper-ctest.log`). Python syntax checks PASS.

## Mean priority restored / shared reward feedback — 2026-10-12

This supersedes the preceding Pirate NEXT entries: finish Mean first; defer Pirate gameplay composition. Existing Mean wall/flipper composition was already verified and remains unchanged.

IMPLEMENTED: original Monster Car `412fa8`, Offroad `41041c`, mode6 award `410158` DMD animations, score phases and finite completion. User MEAN.DAT supplies 20/14/12 original frames and score page. `apply_shared_reward` starts these after mode reset, preserving the final Monster Car award display. Existing immediate native display policy remains explicit; original queue/preemption and these callbacks' lamp/audio service bodies are not claimed.

VERIFIED: 1,448 complete pixel-hash/counter/active comparisons vs actual Demo callbacks, including score boundaries; Monster/Offroad native switch chains additionally assert callback selection. Native SDL original-event preview inspected: `tools/slamplay --shared-reward-preview`; `build/mean-shared-reward.png`.

NEXT: finish Mean Rally reward/exit feedback via original `411c60`/`411db4`/`411824` callbacks, reusing the same verified pixel services.

VERIFICATION: `cmake --build build/native -j4` PASS without warnings; `ctest --test-dir build/native -j4 --output-on-failure` **98/98 PASS**, log `build/mean-shared-display-ctest.log`. New C++ display files/probe formatted; Python syntax checks PASS. SDL dummy original-event preview renders successfully and PNG visually inspected. Git diff unavailable: workspace has no Git repository.

## Mean Rally feedback island — 2026-10-12

IMPLEMENTED all remaining shared-reward callback presentations: Rally correct turn `411c60` (30+20+50 ticks), final turn `411db4` (50+75+100), wrong turn `411824` (28+35+16). Original DAT frames/masks and score font; restore and score inversion preserved. All six shared reward callbacks now have native display consumers. Original display queue/preemption and callback lamp/audio bodies remain excluded.

VERIFIED: 14 isolated series / 2,372 original complete-frame hash, counter and active/end comparisons. Native bitmap-switch chain adds wrong turn (0 award, unchanged target) then six correct turns (211.5M total, final mode2 and final callback). Native chain now18steps; synthetic placements, not autonomous whole-table equivalence. SDL `tools/slamplay --rally-reward-preview` inspected (`build/mean-rally-reward.png`).

NEXT: exercise complete finite Mean games for reachable unsupported branches before extending presentation or other tables.

VERIFICATION: native build PASS without warnings; full **99/99 CTest PASS** (`build/mean-rally-ctest.log`), including extended pixel oracle and native wrong/correct/final chain. Python syntax checks PASS; SDL dummy preview capture PASS and PNG inspected. New display C++/probe clang-formatted. No Git repository is available for git diff.

## Mean full-game coverage / mode4 upper continuation — 2026-10-12

FIXED real unsupported helper branch: upper callback1 in internal table-mode4. Actual415545/415dc7 returns without ordinary mode-selection work on timer−2; slot expiry at415473 requests existing416be4 release. Native now preserves mode4/selection flags instead of stopping.920original local state/event comparisons plus152tick hold→500000award→release cycle exact; reward flags200/202/1fa explicitlyzero and release routine is separately-proven boundary. Native actualbitmap targeted entry holds152steps and four12000step continuations pass. Natural mode4-upper traversal not proven. Preview: `tools/slamplay --mode4-upper-preview`; capture inspected.

VERIFIED96 complete finite games /905632steps:32periodic,32deterministic varying holds,8held,8passive,16alternating. Each reaches original-policy GameOver, frozen ball/score, bonus completion and new-game restoration; five seed0 repeats exact.46captures/releases and222saves; no minigames reached. Four additional800000step random runs remain active (3200000steps), one mode4 start; no minigames/multiball reached, so those rely on existing targeted coverage. Native regressions, not original whole-table trajectory equivalence.

Validation: nativebuild no warnings;22/22 affected CTestPASS (`build/mean-coverage-ctest.log`), including new original oracle and inputcoverage; previous full99suite retained, now101registered tests. NewCppprobes formatted, PythonsyntaxPASS; SDLdummy2frame release previewPASS, PNGinspected. NoGitworkspace.

NEXT: longer synchronized original/native Mean gameplay across capture, drain and next-ball boundaries; retain Mean priority and defer other tables.

## Mean capture → flight → restart — 2026-10-12

FIXED: production reset/restart used only scalar41ab94 writes, leaving retained geometry/render descriptors. `mean_initialize_ball` restores layer0 descriptors and scalar state; restart refreshes collision bit views. Unknown retained fields are preserved.
VERIFIED:456 capture/RNG/release states +3951 complete100-byte flight states across three seeds, ending at original40898b drain callback boundary. Controlled context: cached rest flippers, no point forces, suppressed switches; not live whole-table or table drain/next-ball scheduler equivalence.
Restart regression: actual408915 gate +real41ab94, retained capture/release/flight/drain records and shifted descriptors,288 contexts. Pre-fix failed on geometry/render offsets40/44/54.

Validation:103/103 CTest PASS (`build/mean-restart-ctest.log`); native build without warnings; Python syntax and SDLdummy mode4-upper preview PASS. NEXT: table drain callback→next-ball scheduler context, retaining Mean priority.

## Mean drain/bonus/restart composition — 2026-10-12

VERIFIED controlled original composition:24 expired-save drain→bonus→persistent save/reset→initializer chains +24 direct ball-save→initializer contexts;4100 full snapshots (100-byte ball,960-byte table fields,52-byte player record, bonus/display/player counters). Includes zero/nonzero/wrapping bonus, multipliers1..3, bonus held, extra ball, suppression and one/two-ball saves. No new production mismatch. Rendering/audio/lamp rebuild and save scheduling service34/40f754 excluded; no live cadence,Full game-over or whole-table proof.

Validation:11/11 affected CTests PASS (`build/mean-drain-ctest.log`), native probe build without warnings and Python syntax PASS;104 registered tests. Previous full103 suite retained.

## Mean timing + playable bonus acceleration — 2026-10-12

IMPLEMENTED original two-flipper bonus fast-forward: SDL Shift edges set/clear734 bits1/2; both pressed after bonus entry select step4. Holding across drain creates no fresh press (original4080dc clears734). One flipper alone retains normal speed. Fixed phase1 adapter dispatch: original4072de skips intro callback before fast phase2; native previously called it once extra.
VERIFIED1032 original bit-write contexts and56 actual4049e0/4071e8 budget/dispatch contexts:5ms RNG/flippers/physics (physics suppressed in bonus/overlay),20ms table/bonus/overlay dispatch. Original catches up all physics before all display; native interleaves at fixed5ms. Catch-up batching/live jitter remains unverified, no scheduler equivalence claim.
Expanded lifecycle proof:72 contexts/5076 full snapshots, including24 accelerated bonus chains with nonzero/overflow bonus,held bonus and extra ball. Native natural-drain comparison:185 remaining displayticks normal/one flipper vs41 both, same score/ball number; ball frozen. Route tests use explicit periodic-no-bonus profile to isolate contacts/targets; finite input-diversity tests retain acceleration. Lifecycle minimum now42 proven full fast ticks instead of186 normal ticks.

Validation:107/107 full CTests PASS (`build/mean-fast-final-ctest.log`); native build without warnings, Python syntax and SDLdummy bonus preview PASS. All route assertions retained with bonus-neutral targeted input profile; broader finite profiles exercise normal acceleration.

## Mean original camera +runtime transition — 2026-10-12

IMPLEMENTED gameplay camera4086b8 in native SDL view: signed16.16 response, acceleration delta±2pixels/5ms, viewport clamping, greatest renderY with state6 excluded unless all candidates excluded. Camera reads last-render interpolated anchorY and fresh per-ball state after simulation, including bonus; physics/ball100bytes unchanged. Native view supplies400height/200scroll range and explicit reset focus; original startup camera/menu branch not recovered.3512 original state comparisons:512 boundarycases +five600step sequences.
VERIFIED28 original bonus-end frame batches with actual4049e0/4071e8/4072cc/407794/419ad8/419b00:all simulation budget consumed while bonus freezes physics, then first displaytick finishes bonus; remaining displayticks run new-mode table display/idle. BallFFFF retained for next simulation frame. Tick/renderer/audio/lamp boundaries adapted; controlled terminal bonus, not live jitter or native batching equivalence. Native fixed-step interleaving retained.

Validation:109/109 full CTests PASS (`build/mean-camera-final-ctest.log`); native build without warnings, Python syntax and SDLdummy upper-preview PASS; capturePNG inspected. Fixture-consuming tests depend on capture oracle to avoid concurrent reads during regeneration. NEXT: natural Mean advanced-mode entry coverage with existing verified helpers.

## Mean unforced advanced-mode island — 2026-10-12

VERIFIED native ordinary-reset trajectories, no debug_start/ball/table-field injection:seed13 minigame starts247020 at ball88, completes249704, releases250304;seed16 minigame starts365474 at ball138. Seeds27/29 spawn three extra balls/max4 and return to one ball/mode2 (firstspawn161125 at ball59 /317265 at ball129). Four400000step runs; repeats13/27 full summaries/event chains exact. These are endless diagnostic keys, not finite3-ball achievements or captured original/live whole-table equivalence.
IMPLEMENTED shared diagnostic key generator (uint32 xorshift seed+1,10..200tick holds), compact advanced event journal and natural SDL previews: `tools/slamplay --natural-mode-preview minigame` / `multiball`. Ordinary reset→normal native physics/rules only; continue same keys through400/64steps for initial display/release, pause for inspection; Space resumes with user input. Explicit endless diagnostic policy. Both captures inspected, original Formula1 introduction and Active4 visible.
Validation:110/110 full CTests PASS (`build/mean-natural-ctest.log`); builds without warnings, Python syntax and both SDLdummy previewcaptures PASS. Read-only side audit found no proven selected3/4 entry blocker; unconsumed rule_service_request remains an unverified service boundary, not claimed cause. NEXT: ordinary upper-capture rule/service-request effects against original.

## Upper first-capture announcement — 2026-10-13

IMPLEMENTED ignored first ordinary upper rule request415727→service34(callback411fdc): lamp29 command{4,6,1,0}, native50Hz animation/hold/masked restore. Frames11904e/119b8e decoded from user MEAN.DAT; callback stops at oldcounter155. Ball hold/release unchanged; selected-mode/service queue/handle038/field024 and438b20 sideeffects remain separate boundaries. Uses existing immediate native display policy and saved native page, not complete original queue equivalence.
VERIFIED312 actual411fdc pixel/counter/active cases:two156tick series with blank/patterned restore, real bitmap+mask services. Natural seed13 ordinary-reset SDL entry available as `tools/slamplay --natural-mode-preview upper`;32step same-input continuation, captures inspected (ball2). Explicit endless preview, no injected ball/rules. Full111/111 CTest PASS plus2/2 final announcement tests PASS (112registered); builds without warnings.
NEXT: selected-mode upper announcement requests, using same proven DMD pipeline.

## Upper selected-mode announcement island — 2026-10-13

IMPLEMENTED selections0/1/2/4 service34 requests→412d24/411f10/412af8/412c58: original MEAN.DAT frames10a7ce/11a6ce/11f94e/13380e, exact animation/hold/16mask restore and termination. Selection3 retains existing minigame. Native immediate display/saved-page policy retained; original queue/handles not claimed equivalent. VERIFIED1298 original/native pixel/counter/active states (eight complete blank/patterned restore series), fixture `analysis/traces/mean-upper-modes-original.json`. Natural SDL preview `--natural-mode-preview upper-mode` uses ordinary reset and diagnostic keys, no injected state.
NEXT: shared display request arbitration when gameplay events overlap.

Natural upper-mode preview:seed13 reaches original car animation at ball489 within2000000step budget,32same-input continuation and inspected SDLcapture `build/mean-upper-mode.png`. Initial400000step budget insufficient; endless diagnostic only, not normal3-ball entry coverage.

Validation:114/114 full CTests PASS (`build/mean-upper-modes-final-ctest.log`), warning-free native build, Python syntax PASS, SDL upper-mode capture inspected.

## Shared DMD admission/retirement island — 2026-10-13

FOUND405f98 has no suspended queue: reject unless requestEAX>43e7b0 and (inactive orEAX>43e788), then storeEDX as43e788, callback/active/counter; successful return−1. Same-class request can replace becauseEAX/EDX intentionally differ. IMPLEMENTED original admission and4071e8 retirement/idle transition for21 native pixel callbacks. Upper8/7 blocks bank6/5, ordinary7/6;413a2c special5/2. Rejected requests leave active animation/counter/saved page intact. Bonus/newturn/mode4 finish retain explicit native display reset.
VERIFIED1516 original/native admission/scheduler contexts incl signed comparisons, raw stack sideeffects, branch/idle/restart actions; real callback pixels across7 overlap sequences in `analysis/traces/mean-display-overlap-original.json`. Request metadata22sites/21callbacks in `analysis/display-request-args.json`. Callback bodies/bitmap executed; alternate/idle/restart/control services adapted. Native50Hz interleaving unchanged; bonus/minigame/reward/mode6 overlay arbitration, global floor writers, sound consumption, complete shared score/page equivalence remain separate boundaries.
NEXT: merge reward/mode6 display ownership with the proven admission component.

Validation:116/116 full CTests PASS (`build/mean-display-scheduler-ctest.log`), final2/2 scheduler/overlap checks PASS after formatting; builds without warnings, Python syntax PASS. Natural Upper-mode SDL capture inspected again; native physics/event trajectories unchanged by presentation admission.1516 raw contexts +1773 actual overlap/pixel steps exact.

## Reward/Mode6 visible shared-owner island — 2026-10-13

IMPLEMENTED original410a34/410910/410d34 reward pixels and410b00 full multiball announcement (clear25,19frames×4,hold100,mask16,READY50+invert cadence). Reads user MEAN.DAT frames14352e/14244e/137f4e/13bf0e and reuses MAIN.DAT text font. Replaces independent reward/mode6 clocks with shared405f98 admission and4071e8 retirement. Rewards8/7;Mode6 10/9. Reward364 releases only on idle;Mode6 382 at oldcounter267;reward3 438afc={1,0,0} at75 only if callback runs. Native shared display now follows table-display tick; bonus/minigame remain explicit separate owners.
VERIFIED1590 callback pixel/counter/active states and2945 admission/scheduler/pixel/gate states across9 composed sequences, including blocked low request, preemption, before/after75 reward3 effect and synthetic11/10 interruption. Actual413b04 reward gate executed with enginefield1c=0; post-gate idle rendering and lamps/audio adapted. Native original normal-frame batching/global floor/438afc downstream scheduling remain unproved.118/118 full CTests PASS (`build/mean-reward-owner-ctest.log`); additional Mode6 SDL119th test PASS, capture inspected. Existing --mode6-preview uses explicit seeded capture then native event/200step animation; not natural finite3-ball proof.
NEXT: shared display ownership at minigame/bonus entry and return.

## Bonus/minigame display ownership island — 2026-10-13

IMPLEMENTED first/second native minigame entry discards prior callback/priority rather than pausing it; shares retained engine1c counter with the existing original-code lift, imports raw engine10/14/18/1c/20/44 on return. Bonus entry state6/mode3 preserves raw active/priority/callback/counter; return state3/mode1/field44=0, not arbitrary all-field reset. Admission reads current native table/engine30 mode. Existing normal turn reset/pending policy retained.
VERIFIED324 raw contexts:actual415bf7..415c32 takeover,408084 bonus entry (table-save adapter),407870..4078a6 return writes. All old active/priority/counter contexts preserved or cleared exactly. Actual first minigame takeover validated; second minigame reuses already-cached initializer field contract, original second-entry caller not newly recovered. Natural seeds13/16 entry display{callback0,counter156,state0,active0,priority−1,storedcallback0,field44=1}; exit same raw fields andcounter156,field44=0. No old callback restored. Native ordinary-reset/endless diagnostic; no original/live entire trajectory or finite3-ball achievement claim.
NEXT: validate remaining Mean gameplay/rule gaps in a finite three-ball run.

Validation:120/120 full CTests PASS (`build/mean-display-owners-ctest.log`), final owner oracle PASS after scope metadata update; native build warning-free, Python syntax PASS. Natural minigame/finite-input regressions and existing SDL previews PASS.

## Upper return-pass gameplay/rule island — 2026-10-13

FOUND layer2/mask1/Y<60 native ball-local slice stopped at41be5d, omitting entire mode-selection/repeat-score/timer chain. IMPLEMENTED literal419da4 guards (3840/mode<=4/not-all-complete), next unfinished selection+lamps without terminal-mode reset;374=150,21flash; repeat37c++ with signedupdated37c*5M modulo32-bit. DWORD37a highWORDaliases37c.50Hz419944 expiry clears37c/lamp21; mode4/3a6==1 restoresflash. Score050/41163c request5/4 and originalflashpixels integrated; accepted40f754 request resets five capture secondarytimers, opaque038/024 remain excluded.
VERIFIED1536 actual rule/expiry raw-state contexts,324 actual41163c pixels/counter/active states. Native original-bitmap targeted chain rotates2→3→4 andscores0→5→15M, repeated exact (`analysis/traces/mean-return-pass-gameplay.json`); explicit ball/mode fixture, not natural trajectory.96ordinary finite games observe2first-pass entries/no repeat awards, allcomplete; existing natural advanced tests retaincoverage. SDL `--return-pass-preview` seeds3passages, then separate verified ramp beforedisplay continuation; originalscoreflash/lamp visible, explicit fixture.
NEXT: synchronize a complete return-pass/expiry sequence with original gameplay and audit the next missing gameplay consumer.

Validation:124/124 full CTests PASS (`build/mean-return-pass-ctest.log`), warning-free native build and Python syntax PASS. SDL return-pass capture inspected:15M total/10M final award, original table and lamps. Source-asset files remain user-owned; no original assets added.

## Complete return-pass cycle/dispatch island — 2026-10-13

IMPLEMENTED shared return-pass presentation adapter: actual405f98 result−1/0 stored asraw038, accepted40f754 clearsraw024 andfive secondary capture timers; rejection preserves both resetfield/timers. Score050 written even when display admission fails. Replaces inline production timer wiring with reusable verified dispatch.
VERIFIED2053 composed original/native operation states and pixels across6cycles: hit→repeat→expiry→new chain;150tick boundary permits repeat,151tick expires; higher8/7 advertisement rejects5/4 repeat notice while score continues; later admission resumes normally. Actual419da4/405f98/40f754/419944/4071e8/41163c and bitmap/font routines executed. Binary score accumulation and idle rendering adapted; no full ball physics, capture timer countdown, live frame batching or whole-table equivalence claim. Evidence `analysis/traces/mean-return-pass-cycle-original.json`.
NEXT: audit the next unconsumed Mean gameplay callback, prioritizing a complete rule chain.

Validation:125/125 full CTests PASS (`build/mean-return-cycle-ctest.log`), native build warning-free and Python syntax PASS. Parallel bounded audit41cd50..41d0fa found native Marker20/noop/lower-target consumers already wired; no missing mechanic or redundant RE warranted. Remaining testlever is composed dispatch across exact Y/X gates.

## Original player defaults / second-minigame progression island — 2026-10-13

FOUND real NewGame407f21→registered40f00b/43f324→419e68, then407f31→419b00. Old native all-zero record incorrectly started selection1 andsecond-mini target0. IMPLEMENTED full52byte initializer: WORDrecord04/12hex=4,22hex=8000; byteholes11/17/1dhex preserved. Eight originalrecords/256sentinel+random comparisons exact; nativefrontend remains singleplayer/freshrecordzeroBSS policy. Newgame selectionnow0 after originalresetrotation. FullUSA4268a8,UK/ROM426c78 initializer instruction/defaultpattern agrees (relocated addresses), no Amiga assumption.
VERIFIED15 original minigame2 cycles/15168states, five nowuse actual initialized8000 instead of onlysynthetic0/20000. Native actual-bitmap seeded rightcapture +flipper edges: periods5/10 win30M (+500k entry),8000→7600/count1; periods20/40 fail with8000/count0; save→next-ball reset retains target, newgame restores8000. Repeat exact; not naturalrightentry/fulloriginaltrajectory proof. Fixtures `analysis/traces/mean-player-record-original.json`, `mean-minigame2-original.json`, `mean-minigame2-player-gameplay.json`.
Updated unforced regression after correcteddefaults:400000step seeds27/29 minigame enter/complete,13/16 negativecontrols; seed27 at1800000steps enters Mode6,spawns7extras/max8,returns oneball/mode2 (firstspawn1650985,eight1651825,return1656149), exactrepeat. Endless many-ball diagnostics, not finite3-ball achievement. Natural preview uses27 forminigame/multiball, latterbudget1800000.127/127fullCTestsPASS (`build/mean-player-init-ctest.log`), warning-free build/Python syntaxPASS.
NEXT: show original second-minigame goal and terminal feedback using existing fonts/services.

Final visiblecheck:127/127fullsuite PASS plusnew128th `mean_natural_mode6_eight_visible` PASS after diagnosticpreview update. Natural seed27 mode6 previewnow waits eightballs,64same-input continuation; `build/mean-natural-eight.png` inspected (Active8). Still endless diagnostic/no finite3-ball claim; no state injection. Finalbuild warning-free.

## Second-minigame original text/result feedback island — 2026-10-13

IMPLEMENTED original text4060f8,smallnumeric40617c (binary/6byteBCD,width return,alignment,inkmask,group dots) andlarge406280 through optional native lift presentation hook andexisting MAIN.DAT fonts. Lift externalcalls omit hardware returnaddress; fontbridge supplies virtualESP−4 while preserving argument cleanup. Actual smallBCD zero formatting retains2digits aftermax10leading-zero shifts. Legacy gameplay oracle remains explicit no-text adapter; liveSDL nowrenders originalgoalcaption/8000/S.
IMPLEMENTED41210c failure239ticks and4122cc success214ticks: DAT11670e animation, raw43efcc numeric/S caption, failure14fbee maskedpage, successaward/invert andsavedpage restoration. Captures requested callback from liftedservice34 stack+8 (nohardware return), original8/7 admission onreturn; initialized raw43efcc andaward050 carried intoexisting sharedDMD owner. Native winner/failure testchecks actualterminalcallback.
VERIFIED93actual text/numeric pixel+width contexts through liftbridge,5436actual terminalpixel/counter/active states (24series).132/132fullCTestsPASS (`build/mean-minigame-feedback-ctest.log`) plusnew133goalSDLandfinalfont checksPASS; warning-free build/Python syntaxPASS. Goal/success/failure PNGscapturedandinspected; new `--minigame2-result-preview success|failure`, existing`--minigame2-preview` stopsatactualgoalfontcall. Previews seedoriginalrightcapture/route anddiagnosticflipperinputs; no naturalfinite3-ball/originalwholeframe equivalence claim. Other scene scaler405f0c/audio bodies remain explicit boundaries.
NEXT: reuse existing audio pipeline for missing minigame countdown/event samples.

## Minigame sample island — 2026-10-13

IMPLEMENTED both minigames' service405c60 requests and second-minigame417570 early-start input forwarded into existing native SDL sample mixer. Four original sample18 slices437fe4/438008/43802c/438050: DAT27b66/286ea/292f5/2a100, lengths2747/2882/3395/4536, period428, volume64, arguments255/245. Resolver4017a8 uses BE DAT sample index plus8 plus descriptor10; no new decoder. Early flipper press legitimately skips countdown; native four input profiles each emit exactly one start sample.
VERIFIED four original/native countdown request traces (both variants, two input schedules), exact ticks/descriptors/arguments; actual401760 resolves four PCM addresses/voice records; 55 original/native mono PCM cases across all11 samples. Evidence MEAN-MINI-AUDIO-022. Final stereo saturation remains native policy; no listening test or complete original music/display-frame equivalence claim.
NEXT: close remaining minigame scene-scaling405f0c presentation boundary using original data and a bounded pixel oracle.

Final verification:134/134 full CTests PASS (`build/mean-minigame-audio-ctest.log`); final build plus7/7 targeted sample/gameplay/SDL dummy checks PASS (`build/mean-minigame-audio-final-checks.log`). Build warning-free, Python syntax PASS.

## Composed minigame presentation/audio — 2026-10-13

FOUND prior405f0c scene-scaler attribution was wrong: routine expands32pixel two-plane strips to96stride canvas, unused by generated4180d0..4194e4 consumers. Existing406680/406574/40f91c implementations match original unpack/mask pixels. No additional scaler needed.
IMPLEMENTED ordered minigame audio queue for40587c/4058a0/4058c8 → existing sequencer88/84/80. Original wrappers take EAXorder/EDXbank; preserve queue order with service5c sample events. Both native second-minigame success/failure input profiles require exactly one terminal84 bank0/order62 or80stop event selectedby signed37a.
VERIFIED3461 composed full1920pixel DMD frames across both variants and four seeded scenarios, executing actual original render/text/mask routines. Oracle framebuffer must be separate from original runtime1008000 scratch (43efd0); isolated1500000 canvas, reset betweencases. External scoring/audio/display-admission/lamp effects remain bounded adapters; no full original tick/physics equivalence claim. Eight original/native tick-aligned sample/music traces include raw37a0→84 order62 vs37a−1→80 stop. See MEAN-MINI-COMPOSED-023.
NEXT: carry first-minigame terminal callback40f994 into the existing shared DMD owner (native completion bridge currently only accepts41210c/4122cc).

Final verification:135/135 CTests PASS (`build/mean-minigame-composed-final-ctest.log`), including8audio traces/3461composedframes/native completion audio branch. Build warning-free; Python syntax PASS.

## First-minigame terminal island — 2026-10-13
IMPLEMENTED40f994/40fb78 result animation/text/score/fade, raw43efdc transfer, original8/7 admission slots55/54. Completion now imports original tablemode before admission (debug entrypreviouslyretainedmode1andrejectedresult). Shared4060a4 now reproduces all7brightness pairs, signedclamp0..6.
VERIFIED2814actual callback pixel/counter/active states;103font/clear contexts;3461composedminigame frames stillmatch. Four native minigame→40f994→displayretirement chains compare originalpixels andownerrelease. SDLNO SCORE screenshot inspected (`build/mean-minigame1-result.png`, `--minigame-result-preview`). Success40fb78 verified boundedpixels/requestsource; no naturalfirst-minigame120Msuccess claim.
NEXT: reproduce first-minigame120M success using actual steering inputs andcheck return to table.

Natural-regression delta: prior completion assertion expected missingterminalDMD/retainedcounter; now requires original40f994 request[callback,0,4,2,7,callback,0]. Diagnostic trace records first-minigame result-owner transitions. Natural ballrelease happens atresultcounter150; callbackretires167 independently, so no before-release requirement. Entry counterretention remainschecked; completioncounterreset isoriginalacceptedrequest behavior.

Final verification:138/138 CTests PASS (`build/mean-minigame1-result-final-ctest.log`), including natural minigame27/29 result-ownerretirement and1800000step mode6 eightballreturn. Final build warning-free/Python syntaxPASS. Natural traces nowcapture resultretirement; four debug-entry profilescompareoriginalresultpixels; screenshotinspected.

## First-minigame steering-only120M island — 2026-10-13
FOUND actual DAT1565c4 collisionmask256×256; raster(-field014>>17)&255,((28f5c2−field018)>>16&510)/2; originalheading0/1024/2048/3072→down/left/up/right. Real keypairs produce sixcompletedlaps(raw43efdc7),120M,40fb78 in4520×20ms ticks. No originalstatewrites aftercachedcaptureinitialization.
VERIFIED4520original/native ticks:24DWORDblock43efd8..43f034,active/mode/field1fa/points/callback and480bytepacked-framehash exact. Native two diagnosticentries plus two unforced endlessseed27 entries allwin withsameinput;120M once,ballreleased,resultownerretired,301uniqueDMDtickpixels match original. Natural score78,336,860→198,336,860 onwin;25,000legitimatepointsafterballrelease whiledisplaycontinues, exactrepeat.141/141CTestsPASS (`build/mean-minigame1-win-ctest.log`), warning-freebuild/Python syntaxPASS. SDL`--minigame-win-preview` shows6LAPS/120000000; screenshotinspected.
NEXT: cross-check first-minigame winning lifecycle againstRetail/Fix, resolving knowncontact-counterdecrement2×Demo vs4×Retail. Still nofinite3-ball/originalwhole-tabletrajectory claim.

## Retail/Fix first-minigame island — 2026-10-13
FOUND entire codefamily differs by3gameplayconstants:418848contactscale2→4,419220partial-lappoints20M→40M,4193c6rawcompletion7→4. Both terminalDMD bodiesalso20M→40M (40fb4f/40fd77). Initializer415bce..415d00 has65unchangedinstructions/constants. Demo/RetailMEAN.DAT byteidentical (SHA1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f).
IMPLEMENTED explicitnativeRetailrevision via`--retail-minigame`; three completedlaps→120M, onecompletedlapthenabort→40M; matchingDMD3LAPS/120M andpartial40M. Demo remainsdefaultreference; noother-table/runtimeversionequivalence implied. Generatorparametrizesonlythreeprovedinstructions; DMDlapamounttransferredwithterminalrawstate.
VERIFIED actualunmodifiedRetail/Fix executables, translatedcachedDemoentrycontext/compatibleDAT/LUT: win2455ticks andone-lap-abort1189ticks perbuild,24DWORDrawstate/flags/points/callback/packedframehash exactagainstnativeprofile. Four productionrunsperresult (two diagnostic,two unforcedendlessseed27) matchpixels,awardonce,ballrelease/DMDownerretirement.1407normalizedRetailDMDpixel/countercases useproven20M→40M changes+originalDemofont/render services; notactualRetailwholeframeoracle. SDL3LAPS/120M screenshotinspected.146/146fullCTestsPASS (`build/mean-minigame-retail-ctest.log`), warning-freebuild/PythonsyntaxPASS.
NEXT: boundedDemo/Retail comparison of remainingMeanrule/capturecallbacks, prioritizing realconstantchanges overrelocation.

Final initializercheck: expandedactualRetail/Fix mapper includes65unchangedinitializationinstructions; final142oraclePASS (`build/mean-minigame-retail-final-oracle.log`) after146/146fullsuite. Fullnormalizedbundle2609instructions/build; only5provedconstants differ.

## Mean rule reuse / Retail launcher — 2026-10-13
FOUND: 14 bounded Mean code ranges (5860 instructions per Retail/Fix build) match Demo after verified address relocation; numeric constants and instruction bytes are unchanged. Three consumed tables (153 DWORDs) also match byte-for-byte. Evidence: `analysis/mean-rule-reuse.json`; reproducible checker `tools/verify_mean_rule_reuse.py`.
IMPLEMENTED: `tools/slamplay` defaults to the verified Retail first-minigame profile (3 laps / 120M); `--demo-minigame` selects Demo (6 laps). Historical Demo SDL fixtures explicitly select their profile. This is not a claim of complete Retail runtime equivalence.
NEXT: validate the remaining Mean completion gaps in the finite three-ball lifecycle, rather than reimplement identical rules.

Final verification:148/148 CTests PASS (`build/mean-rule-reuse-ctest.log`,117.31s); build warning-free, Python syntax PASS. Default Retail screenshot inspected (3LAPS/120M); historical Demo preview remains6LAPS.

## Both minigames → finite GameOver island — 2026-10-13
VERIFIED: twelve native integration runs (six outcomes × exact repeat): first-minigame Demo/Retail win/abort, second-minigame win/failure; real key inputs after explicitly diagnostic capture setup, result callback, ball release, three bonus completions/awards, stationary ball during bonus, GameOver ball/score freeze for40steps and new-game restoration. First awards120M/20M/40M; second30.5M/0.5M. No simulation change needed. Fixture: `analysis/traces/mean-minigame-finite.json`.
IMPLEMENTED: `tests/mean_minigame_finite.cpp`, CTest149. Warning-free build; newintegrationtestPASS22.07s (`build/mean-finite-island-ctest.log`). Previous148-test suite remains last fullrun; no full149-suite claim.
FOUND: bounded natural finite random-input search seeds0..127 yields128GameOvers andzero minigame entries (`analysis/traces/mean-finite-entry-search.json`). This is a negative diagnostic coverage result, not evidence of impossible entry. Existing seed27naturalentry isendless.
NEXT: target player-controlled shot/selection progression to reach a minigame within a finite game; stop broad random-seed searches.

## Natural finite second-minigame island — 2026-10-13
FOUND: bounded ball-position/phase-based key timing reaches second minigame during ball1 ofnormalfinitegame: Y>=470, alternateleft/right every16gameplaysteps,phase4; launchheld; no ball/rule state injection. Entry after12185steps insearch,score5906830. Phase12alsoenters. First-minigame selection stillrequires additionalprogress; no naturalfinite first-minigame claim.
IMPLEMENTED: shared diagnostic keyhelper `mean_finite_shot_input`, optionalSDL`tools/slamplay --natural-mode-preview minigame2` (finitepolicy), expandedfiniteintegrationtest to14cases includingtwoentireunforcedentries. Preview showsoriginalBEAT8000/Shiftaccelerates onball1, screenshotinspected (`build/mean-natural-finite-minigame2.png`). No gameplayphysics/rules changed.
VERIFIED: naturalentry → realkeyminiwin(+30M afterentry, earlier500k capturealreadyincluded) → result4122cc → release →3bonuscompletions/awards →GameOver/frozenballscore40steps →reset; exactrepeat,finalscore117640980. Fixture`analysis/traces/mean-minigame-finite.json`; search`analysis/traces/mean-targeted-shot-search.json`. Newintegration+SDLtests2/2PASS (`build/mean-route-island-targeted.log`).
NEXT: validate this same finite shot sequence against original runtime around rightcapture/minigameentry; retainnativewhole-table/originalequivalence distinction.

Final verification:150/150 CTests PASS (`build/mean-route-island-ctest.log`,128.72s); warning-freebuild;14finiteintegrationcases includingtwo naturalball1entries. SDLnaturalfinitepreview screenshotinspected.

## Natural-entry original mini-game execution — 2026-10-13
IMPLEMENTED: readonly diagnostic minigame accessor, `mean_natural_minigame_oracle_probe`, `tools/verify_mean_natural_minigame.py`, CTest151. Probe reachesball1entryviaexistingrealkeysequence, exportsbinarysnapshot onlyunderbuild, records2119native5msinputsteps. Actualoriginal417374/41766c inputcallbacks and4180d0 execute530mini20msticks; actual416fe0 executes, notstubbed.
VERIFIED: everytick24DWORD43efd8..43f034+960rawbytes43f000..43f3c0,flags/mode/30M/4122cc/480packedbytehash match; orderedtwoaudioevents andargumentsmatch acrossallinputsteps. Originalcore/input/resetcodebytes comparedtocachedoriginalimage; snapshot/DAT SHAs recorded. Actualresetobservedmode2/field3a2=0. Nativealltablephysics/startup BEFOREentry remainsnotanoriginalruntimecapture; renderer/font/audio-device services remainboundedadapters. Fixture`analysis/traces/mean-natural-minigame-original.json`.
NEXT: reach the first minigame in finite play via targeted Return-Pass/upper-capture shots; preserve the verified second-minigame route.

Verification:7/7 relevantoriginal/native/integration/SDLtestsPASS (`build/mean-natural-oracle-regression.log`,20.75s); warning-freebuild, Python syntaxPASS. Prior150/150fullsuite islastfullrun; no151/151fullsuiteclaim.

## Nudge waveform / common tilt island — 2026-10-13
FOUND: originalControl.txt mapsLeftAlt/rightward,RightAlt/leftward,Space/upward.40407c inputs queue42980c/429858;40554c adds40to43e7d4 inmode>1,mode!=3,nottilted; signed>41requests callback0,>81sets43d864/engineflippers/ballstatus2 andcallback1.20ms404b43decayspositivecounter.40671c waveformadvancesafter5msphysics;404b48pendingacceptedafter20msloop. Existingcollisionfunctions support43e724/564 velocity and43e71c/410 queryoffsets; nativecalls currentlyzero.
IMPLEMENTED: `src/input/mean_nudge.{h,cpp}` and `mean_nudge_tilt.{h,cpp}`; userPEcache supplies17DWORDLUTs at429814/429860.900Original/nativewaveform/acceptcases include6complete40stepbursts/retriggercadence;528commonTiltcases include0/1/8balls andintegeroverflow. TwoCTesttargetsPASS0.62s (`build/mean-nudge-island-ctest.log`), warning-freebuild/PythonsyntaxPASS. No newSDLkeysorphysicscouplingyet: tablecallback+4 consequences andcaptured-ball/newballTilt lifecycle remainunverified. This supersedes intermediate intent to wire a diagnostic preview.
REA: connectedserver openedSHA31192e... DemoPE, butnativeanalysisproviderunavailable (Ghidra notconfigured; noavailablealternative); sessionclosed, noinstallation/configchanges. ExistingCapstone/Unicorn usedforactualcodeproofs.
NEXT: locate/verify tablecallback+4 warning/Tilt/reset effects, thencompose Nudge with existingnativecollision andSDLcontrols.

## Mean Tilt callback / warning / audio — 2026-10-13
FOUND: callback+4=417ae0 via43e740→438ae4,+4→4388d4,+8→43f304,+4→43f308; initializer40f0af/40f10c installs417ae0. Warningservice34 requests40f93c(6,1,2,0;−1/−1), recordsadmission43f038 andcalls40f754(1,1,1,1;1/0). Tiltcalls8c then84(order52,bank1), clearsengine+14; no directcaptured-ballwrites.
IMPLEMENTED: nativecallbackrequestmodule `src/input/mean_nudge_table.*` (108originalcontexts), warningDMD40f93c/page14ecee (51originalpixel/counter/retirementstates), realsharedadmissionmetadata andSDL`--nudge-warning-preview`. SDLsoundservice8c nowusesexistingstop88sequencer;actualMeanbank1/order52 queuesPCM inDummydevice. Sixnudge/table/warning/audio testsPASS (`build/mean-tilt-table-targeted.log`); screenshotWARNINGinspected.
FOUND:20original415330writeobservations showimmediateTiltrelease followedbyordinarycallbacklogic. cb2 releases416d08 then decrements43f380;cb4 transfers417068 thenwrites43f370/438b38;cb1maycall416be4twice. Generic'eject-and-return' isincorrect. NativecaptureTilt dispatch isnotimplemented; Alt/Space remainunbound. Observationfixture`analysis/traces/mean-tilt-capture-observation.json` explicitlynotnativeequivalence.
NEXT: nativeTiltCapture dispatch preservingrelease-before-continuation, beginning416d08/callback2; thenwaveform/collisionquery+flippercoupling andSDLinput.

Finalverification:157/157CTestsPASS (`build/mean-tilt-table-ctest.log`,96.10s),warning-freebuild/PythonsyntaxPASS. SDLWARNINGscreenshotinspected;TiltmusicPCMqueuedonDummydevice. Capturerelease-before-continuation observationsrerunvia`tools/observe_mean_tilt_capture.py`,seed/stubboundariesretained.

## Five bounded Tilt capture paths — 2026-10-13
IMPLEMENTED: cb2/3optionalservices1c inmean_capture_tick;416d08releasebeforetimercontinuation;cb3immediatereleasepluspossiblesecondrelease. cb4optionalflag afterentryguard,shared417068proxy beforecontinuedtimer/award logic; blockedsecondtransferpreserveschangedcallback3. cb5unconditional416f24beforetimer,normalreadyrelease mayrepeat; originalsamplecountrecorded. cb1newboundedhumanwrapper executes416be4beforeconstsaved-entrytick,early_release_count1 leavesnormalrelease/transfercaller-owned. DefaultnonTiltAPIs unchanged.
VERIFIED:288actual415330cb2/3contexts (mode2;positive/<=−3timers,slotready/busy,fullball/slots/timer/sample437decargs6/5);384actual4164e1cb4contexts (human1..4,armed/blocked/timers);70actual415330cb5cases/135states (modes2/5/6);216actual415330uppercases (human1..3,gate/expired/positive/RNG), total958cases. Fixturesmean-capture-tilt-original /mean-tilt-right-capture-original /mean-tilt-multiball-original /mean-tilt-upper-capture-original. Existing360right/1757multiballcases passedagentisolatedchecks; legacyselected3timers152stepsstillmatchafterdependencyupdates.
VISIBLE: `tools/slamplay --tilt-release-preview` setsdiagnosticcallback2entry,executesoriginalTiltrelease+timer50→49/sample once,then32ordinarynativephysicssteps; screenshotinspected. No persistentgameTiltstateornudgeforces areinjected; notgeneralkeyboardTilt/gameendproof. Alt/Space stillunbound.
NEXT: compose verified capture entrypoints into the sharedTilt dispatcher, retaining uncoveredmode5/6/rule-boundary guards, thenconnectwaveform/queryoffsets andSDLkeys.

Finalverification:162/162CTestsPASS (`build/mean-capture-tilt-ctest.log`,195.90s), warning-freebuild. Python syntaxPASS;cb2/3sampleargstrengtheningfinal158PASS;legacyselected3152stepregressionPASS. SDLdiagnosticrelease screenshotinspected. No full keyboardNudge/Tiltcompositionclaim.

## Persistent Tilt dispatcher / finite lifecycle — 2026-10-14
IMPLEMENTED: singlefield43d864 signal feeds captured-ball dispatcher, flipperaction release, capture-entryguards, originalpoint-force/ball-save suppression andMeanBonusDisplayInput.suppressed. Usesverified417ae0requestmodule for8c→84bank1/order52/displayretirement. Clearsaftertableturncallbacks atoriginal40786a;newgameresetsflag. Score-service calls remainunconditional per40560c, no blanketscorefreeze.
VERIFIED native10chains (fivehumanmode2diagnosticcaptures×exactrepeat): release/continuedtimer/sampleordering,nonzero10Mdiagnosticbanknotawarded,stationarybonusball,flagheldthroughbonus,clearednextball,finiteGameOver/newgame. Casecontinuations5660/6600/6352/6352/10036steps; fixture`analysis/traces/mean-tilt-gameplay.json`. Targetedlifecycle+SDL2/2PASS (`build/mean-tilt-dispatch-targeted.log`). Nooriginalwhole-tabletrajectoryproof; specializedmode5/6captures/scoreboundarycomposition remainoutsidecoverage.
VISIBLE: `--tilt-release-preview` nowusespersistentTiltcapture2dispatcher andcontinuesnativephysics;Space resumes untilnextball. Alt/SpaceNudgecontrols stillunbound pendingoriginalwaveform/queryoffsetcoupling.
NEXT: connectNudgewaveform tocollisionquery/normal/separation/flipperresponse, verifyoriginalcomposedcases, thenbindAlt/Space.

Finalverification:163/163CTestsPASS (`build/mean-tilt-dispatch-ctest.log`,211.54s),warning-freebuild. TenpersistentTiltfinitechainswithnonzero10Mbank,sample/musicorder,bonusfreeze,nextballclear/newgamerestore;SDLpreviewPASS. Nudgekeysandfullspecializedmode5/6Tiltremainunclaimed.

## Nudge integration — 2026-10-14
Original waveform now drives native collision/query/wall/separation/flippers; Alt/Space input and warning/Tilt connected. P pauses; Space resumes paused previews. Static original wiring evidence: `analysis/traces/mean-nudge-wiring-original.json`. Bounded waveform/Tilt oracles remain valid; complete specialized mode5/6Tilt and edge-cache coverage remain partial.

Verification:163/163 existing CTestsPASS (`build/mean-nudge-live-ctest.log`,215.32s), plus new100-step nudge integration testPASS. All three directions change ball state at launcher warmup48 with deterministic repeats; three rapid inputs Tilt/resetPASS. Build warning-free. Next: specialized mode5/6Tilt capture continuations.

## Special capture Tilt island — 2026-10-14
Mode4/5left + mode6side Tiltrelease/continuation implemented, mode6releasedballs nowresumephysics.2792boundedOriginal/nativecomparisonsPASS;7specialnativecapturepairs→100steps→bonus/nextball/finiteGameOverPASS. See MEAN-SPECIAL-TILT-036 / `analysis/traces/mean-special-tilt-gameplay.json`. Next: unify original40f754 capture-delay sideeffects at mode5 award boundaries. No fullMean completionclaim.

Finalverification:168/168CTestsPASS (`build/mean-special-tilt-ctest.log`,220.04s); warning-freebuild. Final strengthened seven-pair finite integrationPASS (`build/mean-special-tilt-finite.log`), Originaloracle length checksPASS; Python syntax/map/fixture validationPASS.

## Capture-delay / mode5 award island — 2026-10-14
Shared40f754 gate/selector helper + mode5left award412908 graphics/native dispatch implemented.384helper+224mode5admission+1304pixel casesPASS;4award integrationchainsPASS. Corrected stale rawmode in special Tilt fixture;7assertedmode4/5/6 finitepairsPASS, previous mislabeledintegrationclaim superseded (direct originaloracles valid). See MEAN-CAPTURE-DELAY-AWARD-037. Next: route remaining upper/mode-transition40f754 callers through the shared admission helper.

Finalverification:171/171 fullregressionPASS (`build/mean-award-delay-ctest.log`,100.88s) + newSDLvisibleTest172PASS (`build/mean-award-delay-visible.log`). Warning-freebuild. Screenshot `build/mean-mode5-award.png` inspected: original65Maward on originalplayfield; preview `tools/slamplay --mode5-award-preview` uses synthetic diagnosticentry. Syntax/mapPASS.

## Mean completion island — 2026-10-14

- Implemented persistent SDL options: fullscreen desktop/exclusive, window resolution, aspect/zoom/filter, DMD top/left/right/draggable overlay, original amber/custom colors, rebinding, separate music/SFX levels. Esc opens options; simulation pauses. Native highscores use a separate preferences file.
- Original collision normal40e1d0 executes directly from user DAT; cached-normal and coordinate-border restrictions removed. Linear bitmap addressing follows original408e70, including edge/Nudge queries.
- Mode Lock4172a8 and upper415330 use actual display admission and five-delay40f754 helper. Mode4 flipper input now uses actual admission, all five delays, and preserves4114cc exit feedback.
- Mean remains incomplete: natural finite first-minigame win, named handbook chains and laptop manual acceptance remain. See `analysis/mean-completion.json`; prioritize first-minigame finite chain next.

Final verification: warning-free build;186/186 CTest PASS in101.64s (`build/mean-options-normal-final-ctest.log`), including100 finite games, original normal/bitmap/Mode Lock/upper admission and4114cc pixel oracles. Options screenshot inspected. Hardware laptop acceptance remains pending.

## Formula 1 finite island — 2026-10-14

- Native finite entry from reset after19717steps on ball3; no placement, field injection or endless mode. Prefix alternating flippers every81ticks until11612, then lower-table16tick shots phase2. Return released forone tick then pressed once locks selected3.
- Retail three-lap win120M and abort40M each return totable, release capture, complete bonus/GameOver and restore new game. Second run replays recorded264 input runs from fixture instead of recomputing feedback. Eighteen combined minigame integration cases pass.
- Formula1 identification STRONG: handbook winding-track flipper steering,3laps×40M,curb energy match original Retail minigame. Original result DMD verified1200 native observations forwin and668 forabort during finite return.
- Fixtures: `analysis/traces/mean-first-minigame-natural-finite-{win,abort}.json`; existing original Retail/DMD oracles reused. Does not prove full original-table trajectory equivalence or natural collection of the extra-ball prize.
- Next: named Stock Car/Pit Stop/Overheat/SPEED-lock chains; keep Mean first.

## Formula1 extra-ball collection — 2026-10-14

VERIFIED: Win arms WORD1fa0→1; no immediate ball credit. Real upper-trap reward3 consumes pending prize and grants playercredit. Bonus consumes credit without advancing ball3. Existing production adapters already do this; only observation getters and a regression were added. Two natural finite continuations (shot phases2/10), exact repeats, GameOver/reset, and phase0 uncollected-prize control pass. Positive cases have4bonuscompletions, negative3. Original Retail/Fix win/abort,45 upperreward cases and1024 bonus cases support the transitions. Fixture `analysis/traces/mean-formula1-extra-ball-gameplay.json`; proof `analysis/mean-formula1-extra-ball-proof.json`.

Verification: warning-free full build;6/6 affected CTests PASS45.53s (`build/mean-extra-ball-final-tests.log`); Python syntax PASS. Total suite now187tests, not a claim of187full rerun. Whole original trajectory and manual gameplay equivalence remain unverified. Next: remaining named Mean chains (Stock Car/Pit Stop/Overheat/SPEED-lock multipliers).

## Stock Car / Pit Stop / Overheat island — 2026-10-14

- IMPLEMENTED StockCar15cars/restart+15,5Mperactivebumper/countdown/terminalguard and actual419da4 bumper mode selection/Return-lock gate. Start/hit originalDMD413490/413770. Missing gameplay code is now wired, not merely named.
- IMPLEMENTED PitStop41b61c:4punctures/4repairs/jackpot,4actualramp consumers,50Hz1500timer/expiry,concurrentmainmode2/4/5/6. Real per-request admission and fivecapture-delay helper;4new originalDMD callbacks. Combined shared-mode shots now explicitly include2.5M per first puncture, preserving exact Monster/Rally/Offroad awards.
- VERIFIED Overheat combined lane/rotation/60Mactivation/decay/bluecollection/expiry fixture. Original Demo/Retail60M differs fromhandbook75M; no fabricated correction.
- VERIFIED480Stockrule +186PitStoprule/timer states;849Stock+867PitStopDMDstates, including30cars and actual fifthDATframe whenremainingpunctures4. No coordinate/frame clamp. Demo/Retail/Fix reuse now17ranges/6248instructions perbuild and153DWORDs.
- Full195/195 CTestPASS110.61s (`build/mean-short-modes-final-ctest.log`),100finitegames;warning-freebuild. Visible captures inspected: `build/mean-stock-car.png`,`build/mean-pit-jackpot.png`. Diagnostic previews: `tools/slamplay --short-mode-preview stock-car|pit-stop|pit-jackpot`; these explicitly seed known states, not natural play.
- Regression correction: firstmini diagnosticReturn locks only afterknownthird-ball prefix11612; storedkeyreplay/fullfinitewin/abort assertions retained. Natural endless positive29 no longer enters; independent34 replaces29 with allstrictassertions unchanged; negatives13/16 and seed27eightball/repeats retained.
- Limits: Stock/Pit naturally reached finite fullcompletion and callback-specific audio remain unverified. CompleteMean not claimed. NEXT: SPEED four-ball timed locks/jackpot multipliers and namedCliffJumper. Machine summary: `analysis/mean-short-modes.json`.

## SPEED lock/jackpot island — 2026-10-14

IMPLEMENTED: actual416fe0 mode6 right-lock gate/lamp18 now uses activepoolcount and three signedlocktimers. Timed held release and side capture consume reset events. Main righttrap now accepts mode6; actual41da51 closes gate immediately aftercapture, fixing a5356step unsupported-switch stop. Original41b8d0 SPEED jackpot now applies real DMDadmission to40f754 allfive delays; rejection preserves them.

VERIFIED:312actualgate/reward/admission states;888actualstart/jackpotpixelstates; upper/rightentryoracle extended to mode6; three2000ticklocks nominal10seconds and10/20/30/40M awards, exact expiry/last-free protections. Native eight multiplier/admission/priority contexts; four400000step mode6 continuations now pass. DiagnosticSDL preview `tools/slamplay --short-mode-preview speed-jackpot` shows original40Mbrightblink frame; syntheticentry, not naturalgameplay.

Corpus finding: handbook says4balls; originalDemo init7remaining, Retail408ce8/Fix408f48 allocators bothcap8 and staticAPI+20 assignments. Existingeight preserved ratherthan inventing4. Machineproof: `analysis/mean-speed-island.json`. CompleteMean/naturalfiniteSPEEDfullmode still unclaimed; next namedCliffJumper chain.

Final SPEED verification: full200/200CTestPASS290.18s (`build/mean-speed-final-ctest.log`), including100finitegames andfour400000step SPEEDcontinuations; warning-freebuild. Bright40M screenshot `build/mean-speed-jackpot.png` inspected. Prior199/200 run exposedmissingmode6rightentry; fixed viaOriginal41da51, extendedentryoracle and reranfullsuite. No tests weakened.


## Cliff Jumper result island —2026-10-14

Cliff phase0 now runs original instruction/rev-input → success30M+15M per prior jump or350tick timeout → original result display → mode2.24 native diagnostic admission/slot/control contexts pass;2278 original pixel/counter states exact. Entry and physical trajectory remain bounded/injected, not natural finite completion. Preview: `tools/slamplay --short-mode-preview cliff-jumper`.

Cliff final verification: warning-free CMake build;202/202CTestPASS295.17s, including original pixels, nativeCliff24contexts, visible preview and existing mode4/mode6 gameplay bundles. Log:`build/mean-cliff-full-ctest.log`.


## Left ramp / natural Cliff island —2026-10-15

Missing left ramp41b31f progress now implemented:0→1→2 arms392, wrap→SPEEDletter. Original216raw/API +1896letterpixel/counterstates exact;90 nativeadmission/lamps contextsPASS. Natural finite Cliff seed7:yellow783/green1474/entry2169/success2697; maxrevReturn2452 vs earlyReturn2388→timeout2941. Fourchains end3bonuses/GameOver/frozen/reset at8568/8592ticks; scores40.7M/7.725M. No injected physics/rule fields or captured full Original trajectory claim. Preview:`tools/slamplay --natural-mode-preview cliff`.

Shared animation/capture delta: real438b38/3c/40 triplet is now coupled toexisting418030 renderer (Original417da7/417dac). This fixes rightcapture wait exposed byleft-ramp4-repeat initialization; unchanged DragRacefiniteentry/visible/originalminigameoracle pass again.360Originalanimationstatesexact. Extra-ballroute10positive/0negative stillpass; secondpositive inputroute beingupdated. Initialfull207run203PASS/4FAIL; threeDragfailuresfixed, no assertionsweakened.

Finalleft-ramp/animation verification supersedes initial failures: warning-free nativebuild;206/206fullCTestPASS352.38s +separateextra-ball187PASS(twopositive18/10exactrepeats,negative0),207/207finaltests green.360Originalanimationstatesexact. NaturalCliff46-input-run success/timeout→3bonuses/GameOver/reset unchanged. Nextprimary:naturalfiniteKickstart25M+10M+25M→bonus/GameOver. Index:`analysis/mean-left-progress-island.json`.


## Natural Kickstart60M island —2026-10-15

NaturalKickstart60M implemented:Ball2entry25647, Originalintro blocks628gameplayticks,25M26917/35M27133/60M27256; GameOver30912/89,877,710points andcleannewgame, two freshkeyboard-only repeats. Originalintro4130cc+end4102c0 pixels2168exact. Livephase1idle nowhonorssharedidle; accepted8/7 requests clearsfive slots, rejectedpreserves; enddisplay retainedacrossmode2. Preview:`tools/slamplay --natural-mode-preview kickstart`.

Kickstart finalverification: warning-freebuild;210/210CTestPASS191.01s (`build/mean-kickstart-full-ctest.log`); finalclear25Mpreview aftercounter40polish recheckedPASS1.41s andPNGinspected. Natural60Mgame→GameOver/reset repeatedexactly; Originalpixel2168 andcrossRetail/Fix26ranges7463instructions confirmed. Nextprimary:naturalPitStop65Mfinitechain.


## Natural PitStop65M island —2026-10-15

NaturalPitStop65M complete:existingKickstartprefixcollectsallfourtyres by27256; repairs0/3/1/2 at29617/30852/31293/33243,13gameplayticks beforeexpiry33256. TwofreshSDL-keyboard replayswithrightnudges27456/31437, noTilt orstateinjections; GameOver36912/157,091,370points, freeze/resetPASS. Read-onlypittelemetry+naturalpreviewadded:`tools/slamplay --natural-mode-preview pit-stop`.

PitStop finalverification: warning-freebuild;212/212CTestPASS301.84s (`build/mean-pit-full-ctest.log`). Bothfreshnatural65M/deadline/bonus/GameOver/resetreplays andOriginal25MvisiblepreviewPASS. Nextprimary:naturalfiniteStockCar15hits/75M→bonus/GameOver.

StockCar island verification: warning-free build,214/214 CTest PASS (266.48s), `build/mean-stock-full-ctest.log`; original NO CARS LEFT preview inspected.

Natural SPEED verification: warning-free build;216/216 CTest PASS160.82s (`build/mean-speed-natural-full-ctest.log`), including strengthened exact Formula1completion/fourbonus/GameOver40380/507716240 checks. Original40M native preview inspected.

MonsterCar final verification: warning-free build,219/219 CTest PASS159.49s (`build/mean-monster-full-ctest.log`), five targeted checks2.95s; original final50M DMD preview inspected. Initial full run externallySIGTERMinterrupted; final fullrerun passed.

LiquidRally final verification: warning-free build,222/222 CTest PASS327.70s (`build/mean-rally-full-ctest.log`), four targeted checks7.59s; original22.5M finalbonus preview inspected.

Offroad final verification: warning-free build;23/23 targeted natural-chain/preview/shared-rule/spawn regressions PASS17.74s (`build/mean-offroad-regression.log`). Current suite224registered; fullsuite notrerun, prior222/222 fullpass retained in completion.last_full_regression. Original15M/fourball preview inspected.

ChickenRace final verification: warning-free build;29/29 targeted regression PASS26.18s plus1/1 Originalawardpixel PASS6.91s (30distinct tests), `build/mean-chicken-regression.log`, `build/mean-chicken-pixels-test.log`. Current suite229registered, fullsuite notrerun. Original56.078M preview inspected.

## MEAN-GEARS-NATURAL-053 — Gears, earned extra ball and fivefold bonus

Fresh legal-input route reaches gears2/3/4/5 at5250/20673/22605/23541, 137 actual lamp rotations. Fifth gear uniquely arms pending0→1; upper capture29119 consumes1→0 and credits1→2. First bonus base13.5M pays67.5M. Both banked credits replay the same ball; five bonuses end at43644/200130160, then64frozen steps/reset. Twice identical, four legal nudges, no field injection. Credits are fungible: gear credit proven by sole pending provenance and complete bank redemption, not arbitrarily assigned to first replay.

Missing original gear DMD dispatch now wired:41d153 requests410fcc for2..4 or41121c for5, shared admission and five capture-delay resets preserved. Original bitmap animations/gear page/extra-ready flash/restore match4716 pixel/counter/active ticks (gears2..7, two restore values). External lamp/audio/sharedscheduler bounded separately; no wholeOriginaltrajectory claim. Index `analysis/mean-gears-natural-island.json`.

Gear island verification: `cmake --build build/native -j 4` PASS,31/31 targeted CTests PASS44.44s (`build/mean-gears-final-regression.log`);232 registered, full suite not rerun. SDL screenshot original EXTRA BALL LIT inspected. No Git metadata available for diff.

## MEAN-KICKBACK-NATURAL-054 — KICK, physical rescue and grace expiry

Handbook mean.txt37–40 anchors four red KICK letters to left sidelane. Existing rules arm43f1da via41e724..41e7b9; material7 consumes at41e655, timer390=250, integerX12/Y518 preserving fractions, vx0/vy-0x34000. Timer decrements at50Hz; remaining>=0 permits further saves. Player-record restore preserves flag/letters across turns, while timer resets-1: no unconditional per-ball flag clearing added.

Fresh legal-input route arms30261, rescues actual poolindex3 at30280 onBall1, checks exact position/impulse and original411710 request, timer249 afterstep, expires31280. Four bonuses -> GameOver39224/407952580 ->64frozen steps/reset, twice identical; nine legalnudges, no state injection. Other pool objects remain independent. Physics/rules unchanged.

Missing presentation connected: service request{7,6,2,0,23,1,411710}, saved page, five capture selectors/delay0; 17 original DAT12e3ae frames,34animation+75hold+16restore, counter12 actual438afc effect. Dedicated verifier compares254 ticks of pixels/counters/activity/effect including inactive dispatch. Native screenshot original KICK BACK inspected. Index `analysis/mean-kickback-natural-island.json`; wholeOriginaltrajectory, repeated grace save and natural unconsumed-turn persistence not newly traced.

Kickback verification: full ABI rebuild PASS (`build/mean-kickback-final-build.log`),33/33 targeted CTests PASS15.66s (`build/mean-kickback-regression.log`);235 registered, full suite not rerun. Original254tick DMD/effect verifier and native screenshot pass.

## MEAN-LANE-SAVER-055

Physical fence geometry/rendering now implemented. Natural GOAL-bonus→collection→open→finite GameOver/reset passes twice; separate diagnostic drain/nextturn closure passes.180 Original geometry cases and2223 lap/goal pixel ticks exact. Ordinary lap admission/hold and full lap-built goal ladder remain partial. Details: `analysis/mean-lane-saver-island.json`, EVIDENCE055.

Verification055: full build PASS;36/36 targeted tests PASS24.21s (`build/mean-lap-goal-regression.log`),241 registered/full suite not rerun. Natural and diagnostic SDL fence screenshots inspected.

## MEAN-GOAL-LADDER-056

Ordinary lap display/admission and true capture timing now coupled. One fresh game naturally traverses goal1(GOAL bonus)→lap-built2/3→SideXB/upper credits→both redemptions→five bonuses/GameOver/reset twice. Fence state now survives unrelated raw-state reloads; closes after actual extra-ball turn reset. Cliff key fixture updated for original display priority. See `analysis/mean-goal-ladder-island.json` / EVIDENCE056. Next: Million Skull8second repeat/display.

Verification056: full build PASS,55/55 targeted CTests PASS29.19s (`build/mean-goal-ladder-regression.log`);244 registered/full suite not rerun. Native full-ladder EXTRA BALL screenshot inspected.

## MEAN-SKULL-057

MillionSkull now has original countdown/reset, increasing awards, score animation and correct shared-event display priority. Fresh5/10/15M→expiry→new5M+SPEED10M→fourbonuses/GameOver/reset twice. Three old native score totals corrected by precisely removed stale repeats; gameplay routes unchanged. See `analysis/mean-skull-island.json` / EVIDENCE057. Next: natural Skillshot selection/ramp/progressive award.

Verification057: full build PASS,61/61 targeted CTests PASS23.02s (`build/mean-skull-regression.log`);248 registered/full suite not rerun. Original15M SDL screenshot inspected.


Current2026-10-15 — MEAN-058: Skillshot prelaunch selection, actual41ac6f launch lock, original active DMD41455c and choice tiles414b60 implemented.870 bounded Original pixel cases; fresh legal-input20M770→30M3486, persistent tier across balls, GameOver7608/54200000/3bonuses/freeze/reset twice. Native compact prelaunch page uses exact Original tiles; generic Original player HUD excluded. Goal/lap input edges moved before launch; original strict outcomes unchanged. Index `analysis/mean-skillshot-island.json`. Next primary: remaining short-mode ramp progression.

MEAN-058 validation: full build without warnings;66/66 targeted regressions PASS36.47s; final five Skillshot tests PASS0.89s after prelaunch-preview boundary assertion. Earlier24/24 PASS63.53s includes long existing material5 Original pixel oracle. Both SDL pages inspected; full253CTest suite not rerun.


Current2026-10-15 — MEAN-059: Both-ramp red/yellow/green→short-mode arm→clear/SPEED progression now replays twice from fresh legal keys: left3cycles/right1cycle, Mode6, finite GameOver40380/482716240/4bonuses/freeze/reset. Original-valid mode5 right marker20 entry/callback4 no longer stops: same base timer/score/transfer routine as humanmode4.779 Original cases include251 sequential mode5 ticks; six native diagnostic finite chains (initial ball/rules injected, natural occurrence unproven). Eleven remaining guards classified; no blanket unreachability claim. Index `analysis/mean-ramp-progression-island.json`. Next primary: remaining audio-event coverage and real-play acceptance.

MEAN-059 final verification: buildPASS/no warnings,70/70 targetedCTestPASS41.98s.100fresh legal-input seed games twice (1584960ticks), no stops; three bonuses/GameOver/frozen8steps/reset each; aggregate reference792480ticks/691117830score perrun. Seeds cover normalmodes1..3 only; specialmodes remain covered by separate fixtures. `analysis/traces/mean-100-games-finite.json`. Full256tests not rerun; completeMean/manual/Originalwholetrajectory not claimed.


Current2026-10-15 — MEAN-060: shared405f98 mapped DMD admission now forwards original voice order/bank to88; rejected requests silent, negative-stack preemption conditionally stops onlyactive88 at playback and preserves queuedPCM otherwise. Four mainmode start themes51/46/40/2 and SPEED29 restored; timedreturn/Chicken completion4194e4 resumes62 or stops80.972 boundedOriginal request cases;16fresh natural mode start/return routes and real STIM/SFX PCM Skillshot+SPEED eachtwice through finiteGameOver/reset (21162708PCMframes, exact200Hz/44100Hzcadence). Full Original audio timing/human audibility unclaimed. Index `analysis/mean-audio-island.json`. Next primary: Mean laptop/input/layout/highscore/audio acceptance.

MEAN-060 verification: warning-free build;80/80 targetedCTestPASS39.55s. Full260scan185.68s:256PASS/fourfailures; four corrected legacychecks now4/4PASS16.73s, zeroopenfailures (not a single clean260-test invocation). Audio-on vsallMeanSimulationqueuewritesdisabled1.8Mstate/events byteidentical, provingstale randomSPEEDexpectation independent ofaudio; preservedfourrandomcontrols andexact7spawn/eight→singleball-mode2 contract via existingstricterfiniteSPEEDfixture. CachedRetail Monster/eightball previews replacedfragilelongbots; accepted405f98 Originalverifierstub nowincludesvoicewrite, strict530tick minigame state/pixel/audio comparisonpasses. Logs/commands `analysis/mean-audio-island.json`; screenshots inspected.


Current2026-10-16 — MEAN-061: frontend acceptance island implemented. Fixed Enter→Cancel/Reset, Crop100% ballfollow, highscore modal repeated/keyup leakage, global repeatedshortcuts; achieved score shown. Two freshSkillshot games7608/54.2M/3bonuses→ABC/RST/atomicpersistence/reload/duplicatefreeze/reset pass; actualSDL7frameGameOver→RAB→save→newgame→options→fullscreen flag→repeatEscape passes with isolatedstorage.276layout cases incl96Crop/HiDPI; options1366x768/overlay/crop/remap roundtrip.85targetedtestsPASS39.56s, finalfiveUItargetsPASS0.49s afterscorelabel; warningfreebuild.262registered/fullsuite notrerun. Index `analysis/mean-frontend-island.json`. Next: allfive mainmodes in onegame; physical laptop/input/audio acceptance remainsmanual.


MEAN-062 — Original MODE TOTAL / combined finite gameplay island (2026-10-16)

Implemented Original4146ac pending366 idle admission/reset and410c8c live total DMD, DAT151304, 100 visible ticks, zero-total8c and bank1/order30 voice.24 Original idle cases +416 full pixel/state/audio display cases exact. Fresh legal-input game twice: Chicken win15309, MODE TOTAL140208000 at15968, Rally start21968/two correct hits22813,23421, GameOver27116/194839960/3bonuses/2nudges, freeze/reset. No ball/state injection. Rally completion and allfive wins in one game remain unproved. Started marks are not completion marks; persistence audit found no proven blocker. Two bounded composition searches stopped without a second win.

Verification: warning-free full rebuild;89/89 targeted CTests PASS40.70s,266 registered/full suite not rerun. Native original MODE TOTAL screenshot inspected. Index `analysis/mean-mode-total-island.json`; fixtures `analysis/traces/mean-mode-total-{idle,display}-original.json`, `analysis/traces/mean-combined-modes-{input,native}.json`. Logs `build/mean-cross-mode-final-build.log`, `build/mean-cross-mode-regression.log`.

Next primary: Original normal mode2 idle score/PitStop/bank timer DMD pages (41472e..41496e), replacing missing visible HUD rather than further blind five-mode input searches.


MEAN-063 — Normal mode2 idle DMD (2026-10-16)

Original41472e..41496e now renders the animated player score, PitStop tyre state/countdown and timed bank value/countdown. Native idle admission retains MODE TOTAL, Skillshot, reward and tilt priority. Actual services3c/44/40 match all1920pixels plus sharedcounter in1276 bounded Original cases, including page thresholds64/80, bank3000, all framecycles and counterwrap. BCD score retains a minimum of two digits (406468); binary numeric paths unchanged.

Two fresh legal-input PitStop games each reach65M repair completion then GameOver36912/152091370/3bonuses/freeze/reset. Score and PitStop pages visible,73 score values and629 decreasing PitStop timer values; all visible HUD pixels recompose exactly and repeated-run hashes match. No state/ball injection. Natural bank occurrence not covered by this route; bank pages covered by Original oracle. Native score/PitStop SDL screenshots inspected. Index `analysis/mean-idle-hud-island.json`; fixtures `analysis/traces/mean-idle-hud-{original,finite}.json`.

Next primary: Original main-mode5 idle HUD, using existing mode/timer state. Generic prelaunch player HUD and physical laptop acceptance remain open.

MEAN-063 final verification: `cmake --build build/native -j 3` PASS/no warnings; all270/270 CTests PASS171.98s (`ctest --test-dir build/native -j 3 --output-on-failure`, `build/mean-idle-hud-full-regression.log`). Includes new bounded Original oracle, two fresh finite HUD chains, both SDL previews and full existing gameplay/audio/frontend regression. No open test failures; physical laptop/audio acceptance remains unverified. NoGit metadata or configured formatter/linter found.


MEAN-064 — Main-mode/SPEED DMD island (2026-10-16)

Implemented original idle dispatch413b04: Chicken414084, Monster413f68, Rally413e3c, Offroad413da8 and mode6SPEED413c94. Formula1 selection3 explicitly has no idle write here and retains its existing minigame renderer.1695 Original full1920pixel/counter cases exact using actual bitmap/numeric/clear services. Includes frame cycles, signedWORD39c countdowns, Rally WORD38c target/packedarrows/438bb0+438bc8 lookup, SPEED eight flag combinations/blinking lock markers, BCDscoreminimum2digits and mask0shadow. No generic callbacks fabricated.

Ten fresh legal-input finite games (two perroute), every visibleHUD recomposed, deterministic framehashes, expectedmode/selection, actualcallbacks, GameOverfreeze/reset. Existing finaltick/score unchanged: Chicken20872/156498980; Monster23640/147922810; Rally29268/159529640; Offroad35028/249209410; SPEED40380/482716240. Separate games, not five wins in one game. Allfive native SDL HUD screenshots inspected. Index `analysis/mean-main-mode-hud-island.json`; fixtures `analysis/traces/mean-main-mode-hud-{original,finite}.json`.

Next primary: Original prelaunch/player HUD and handoff to existing Skillshot selection. CompleteOriginaltrajectory and physical laptop/audio acceptance remain unclaimed.

MEAN-064 final verification: warning-free `cmake --build build/native -j 3`;7/7 focused HUD tests PASS10.99s; complete277/277 CTests PASS178.79s (`ctest --test-dir build/native -j 3 --output-on-failure`, `build/mean-main-mode-hud-full-regression.log`). Existing gameplay/audio/frontend tests remain green. NoGit metadata or configured formatter/linter.


MEAN-065 — Original player/ball/extra prelaunch HUD (2026-10-16)

Replaced compact native title with Original414970 player/ball/player-count introduction, alternating player/ball versus BCDscore with existing414b60 choicepairs, and existing41455c activeSkillshot handoff. Added Original extra-turn flag4077b5/4077d4 from actualbonus-turn result; initialengine5c50(407e6a) decrements afterdisplay404b2a.3420 Originalframes match fullpixels, packed480bytescratch, counter andWORD360. Runtime oracle resolved loopboundary: default/active clearall120DWORDs; no119DWORD preservation claim. Singleplayer engine04/08=1; no speculative multiplayer support.

Legal1000tick idle exposes allthreeprelaunch pages. Four fresh finite Skillshot/goal-ladder runs retain7608/54200000/3bonuses and67340/230621370/5bonuses, GameOverfreeze/reset. Two separate fresh goalprefixes earn extra ball at62988/ball3/score228521370; releaseallinputs800ticks, unchangedball/score, exactly101decrements100->-1, two blinkoutputs, thenplayer/scorepages. No state/ball injection. Index `analysis/mean-player-hud-island.json`; fixtures `analysis/traces/mean-player-hud-{original,finite}.json`, `analysis/traces/mean-player-extra-hud.json`.

Next primary: natural finite Overheat completion using existing Original rule implementation. Physical laptop/audio and wholeOriginaltrajectory acceptance remain open.

MEAN-065 final verification: warning-free fullbuild;284/284 CTests PASS183.47s (`ctest --test-dir build/native -j 3 --output-on-failure`, `build/mean-player-hud-full-regression.log`). Final preview-only correction captures lit ExtraBall blink and maps legacy choicepreview to real choicepage;13/13 affected tests PASS3.68s afterrebuild (`build/mean-player-hud-preview-tests.log`). Allfour SDLpages inspected. NoGit metadata/configuredformatter; no open test failures.


MEAN-066 — Natural Overheat collection/expiry and capture continuation (2026-10-16)

Fixed four missing Original40f754 continuations after Overheat display admission: activation41d3a0, half41518b, timeout41510f, collection41e330. Accepted/rejected requests preserve Original allfive selectors1/delay0 and raw038/024 policy;8 bounded Original contexts exact using existing native capture helper. Score/timer and musicstop already matched; no invented resume theme. Existing binary60M/manual75M discrepancy preserved.

Four fresh finite legal-input games, no injections/nudges/Skillshotreward: two five-lit-lane starts10154/60M -> bluecollection10678/54.76M bank+50k contact -> GameOver14036/61398660/3bonuses; two starts -> half13154/30M -> trueexpiry16155 -> GameOver19780/7822810/3bonuses/zeroawards.1000ticks at10Mfloor. Early/late bankHUD naturally observed2400/2192native steps, filling MEAN-063 naturalbank coverage gap. Both routes freeze/reset and deterministic twice. Index `analysis/mean-overheat-island.json`; `analysis/traces/mean-overheat-{natural,timeout}-{input,finite}.json`, `analysis/traces/mean-overheat-admission-original.json`.

Next primary: natural capped fifth-gear10M award and bonus/next-ball reset boundaries using existing Original rules. WholeOriginaltrajectory and physical laptop/audio acceptance remain open.

MEAN-066 final verification: warning-free fullbuild;292/292 CTests PASS185.54s (`ctest --test-dir build/native -j 3 --output-on-failure`, `build/mean-overheat-full-regression.log`). Preview-only capture moved past Originalinvertedtransition to stable54.76Mscore;9/9 affectedtests PASS1.44s afterrebuild (`build/mean-overheat-preview-tests.log`). Allfour SDL Overheatpages inspected; existing gameplay/audio/frontend goldens remain green. NoGit metadata/configuredformatter; zeroopenfailures.


MEAN-067 — Fifthgear cap × Offroad × bonus/turn island (2026-10-16)

Fresh legalinput route naturally caps fifthgear during Offroad(mode5/selection4) at38043:10Mcap+25kcontact, score238041760, gear5 retained, pending0/credits2 unchanged. Existingcallback41041c unchanged; no invented voice/music/display request. Actual Original41d177..41d189 confirms service58scoreonly return;320Originalrewardcases and existingbonus/turn helpers reused. No new engine mechanic needed.

Two fresh finite runs: firstbonus38981 base14M/gear5, award70M38984, extra-turn39972 retainsball1 but resetsgear1. Two extra credits redeemed; ordinaryball2 at44324/ball3 at46500, fivebonuses, GameOver48676/312380420/freeze64/newgameclear. No ball/stateinjection. Added permanent regression +twoSDLpreviews showing actualOffroadscore and5X BONUS70M; screenshots inspected. Index `analysis/mean-gear-cap-island.json`; fixtures `analysis/traces/mean-gear-cap-{input,finite}.json`.

Next primary: natural acceptance of remaining Skillshot reward branches using existing engine. WholeOriginaltrajectory and physical laptop/audio acceptance remain open.

MEAN-067 final verification: warning-free `cmake --build build/native -j 3`;14/14 targeted CTests PASS6.88s (`build/mean-gear-cap-regression.log`).295registered/fullsuite notrerun: thiscycle adds acceptancefixtures/previews, engineunchanged; lastfullMEAN-066292/292 preserved. NoGit metadata/configuredformatter.


MEAN-068 — Allseven natural Skillshot rewards / Originaladmission (2026-10-18)

Fixed missing41d429->40f754 continuation afterSkillshot40fdec displayrequest41d412. Originalrequest7/6/2/0/48/1 nowadmitted/applied before native score andbanktheme84/62;16accepted/rejectedOriginalcontexts exact, including cash/Overheat serviceorder. Existing scalarsevenbranch andcallbackpixeloracles reused. Reward362islatched ateligibleballreset419d55..419d84 fromengine3c, notprelaunchcyclic. No nativephysics orrewardchooser invented.

Seven legal fullRLE routes reused existingcorpusballboundaries;14freshreset finite games verifyeachprize effect, launchlockclear, actualvoice1/order48 thenbank0/order62 whenapplicable, exactGameOver/freeze/reset. Award/finalticks:9038/13160,25710/27656,12630/14576,29506/31452,35506/37452,18374/20320,40742/49216. Wholecaller GreenLights poststate correctly3bc2/3a2FFFF aftersame rightlaneprogress, notisolatedreward3bc1. AllsevenactualSDLrewardcards inspected. Index `analysis/mean-skillshot-rewards-island.json`; manifest `analysis/traces/mean-skillshot-rewards-input.json`, finite `analysis/traces/mean-skillshot-rewards-finite.json`, Originaladmission `analysis/traces/mean-skillshot-admission-original.json`.

Next primary: combined Mean end-to-end acceptance covering gameplay, real audio andfrontend/highscore persistence. WholeOriginaltrajectory and physical laptop/audio acceptance remain open.

MEAN-068 final verification: warning-free fullbuild;25/25focused tests PASS8.99s; complete304/304 CTests PASS192.58s (`ctest --test-dir build/native -j 3 --output-on-failure`, `build/mean-skillshot-rewards-full-regression.log`). Final diagnosticlabel-only cleanup toOriginalMODE LIT followed by14freshgames recheckPASS8.10s (`build/mean-skillshot-rewards-final-recheck.log`). SevenSDLcards inspected. NoGit metadata/configuredformatter; zeroopenfailures.


MEAN-069 — Combined finite gameplay/audio/highscore lifecycle (2026-10-18)

Seven existing legal Skillshot routes now run twice from fresh reset with real DAT/STIM/libxmp music and samples at exact 200Hz/44100Hz cadence: 14 games, 85,479,912 decoded stereo frames. Exact known final ticks/scores/bonus counts retained; request and PCM hashes match per fresh repeat, music and SFX independently nonzero. Each same live game then consumes SDL-scancode RAB initials (repeat suppression), atomically saves/reloads an isolated score, freezes 64 GameOver steps without new audio, resets audio to silence, and starts a new advancing game with fresh-equivalent startup PCM and retained score. Existing Skillshot/SPEED audio routes now include the same persistence checks.

Implementation: `tests/mean_audio_gameplay.cpp`; CTest `mean_reward_audio_lifecycle`; report `analysis/traces/mean-reward-audio-lifecycle.json`; index `analysis/mean-lifecycle-island.json`. Component integration, not whole Original timeline equivalence. Actual main event routing/fullscreen remains covered separately by `mean_frontend_sdl_acceptance`. No runtime gameplay changes or new RE. Next primary: physical laptop fullscreen/DMD/input/audio/save/newgame acceptance; all-five-modes single-game composition remains unverified.

MEAN-069 verification: `cmake --build build/native -j 3` PASS without warnings; six affected CTests PASS15.15s (`build/mean-lifecycle-tests.log`). Full suite not repeated: only acceptance tests/CMake/docs changed; prior304/304 baseline retained. No Git metadata or configured formatter.

MEAN-070: SDL window focus/minimize suspension implemented: gameplay/audio freeze, input release and background input rejection, safe return with held-key suppression and manual pause preserved. Actual SDL acceptance extended to14frames; new audio-enabled counterpart requires an open device and verifies its paused state/queued PCM. Evidence: `analysis/mean-window-activity-island.json`. Physical laptop check remains open.

MEAN-070 verification: warning-free full build;70/70 affected CTests PASS21.97s (`build/mean-focus-tests.log`), including both actual SDL main-loop acceptance routes and full frozen ball-byte comparisons. Full suite not repeated; prior304/304 baseline retained. No Git metadata/configured formatter.

MEAN-070 physical follow-up: user confirmed Alt-Tab audio works on retry ("geht doch!"). Real Wayland focus log `build/mean-alt-tab-live.log`: focus returns, no mute/manual pause/minimize. Initial silence not reproduced; no audio behavior changed. Added opt-in `SLAM_TRACE_ACTIVITY` event diagnostics. Refreshed CMake after system SDL library update; build PASS, both SDL frontend/audio acceptance tests PASS0.81s.

MEAN-071 — Arcade menu / GPU presentation: all previous options retained in Display/Visual Effects/DMD/Audio/Controls; Inter typography, responsive cards, sliders, hover and animated selection, persistent Apply/Cancel and V-held unobstructed paused preview. Six presets (Original/Clean HD/Soft Glow/Neon Arcade/CRT Classic/CRT Deluxe), Custom sliders, quality tiers and independent DMD glow implemented. Optional SDL>=3.4 Vulkan/SPIR-V with classic renderer fallback; no gameplay changes. Details: `docs/presentation.md`; index: `analysis/mean-presentation-island.json`.

MEAN-071 final verification: warning-free main and explicit no-shader builds. Full307/307 PASS215.20s; final UI/shader71/71 recheck PASS22.64s, last4/4 smoke PASS1.11s; no-shader2/2 PASS0.57s. Real Vulkan18-combination pixel contract and real GPU/audio/fullscreen/focus/highscore/newgame acceptance PASS.20 exact-size category screenshots plus six actual GPU presets inspected; 240-frame benchmarks at2506x1514 show medians Original5.002ms/SoftGlow5.007ms/CRTDeluxe5.005ms, p95<=5.160ms (CPU wall times including presentation, not GPU timestamps). Artifacts `build/arcade-acceptance/`, index `analysis/mean-presentation-island.json`. No Git metadata/configured formatter. Physical aesthetic preference remains a user check.

MEAN-072 — Final acceptance tracks (2026-10-18)

- Extended native soak:2072 fresh games /1036 configurations /16,975,800 ticks (~23.6 simulated hours), deterministic ball/input/audio hashes, finite GameOver/freeze/reset, up to8balls. Found/fixed reset-held flipper/launch latches; eight short reset cycles now pass.100 independently constructed seeds verify updated aggregate671,117,830 (seed44 minus20M; ticks unchanged792480), replacing a warm-reset-dependent reference.
- One finite legal-input game now proves Formula1 Retail120M win → Offroad six paid target changes/90M/end → Chicken completion; two fresh runs end46104/402,853,880/fourbonuses. Offroad does NOT require six different physical targets. All five in one game remain unproved after bounded directed continuations; do not substitute started flags for completion.
- Original comparisons expanded:17,960 normal-evaluator cases including boundaries/fractions/nudge;22 integration comparisons from actual fresh legal-route ball records, all100bytes exact. No new confirmed Original mismatch; complete contact/scheduler/trajectory equivalence unclaimed.

Index `analysis/mean-final-acceptance.json`; next primary: legal fourth-mode upper-trap admission from retained three-mode checkpoint42717, field1f2=4/394=0, selectedMonster.

MEAN-072 final verification: warning-free `cmake --build build/native -j 3`; complete `ctest --test-dir build/native -j 3 --output-on-failure` PASS312/312 in367.98s, including official2072-game soak154.66s. Six focused post-reference/marathon/oracle checks PASS13.81s. Initial old100-game aggregate failure resolved via100 independent constructor comparisons, not weakened assertions. No Git metadata/configured formatter. Three-of-five composition remains PARTIAL; bounded Original comparisons are not whole-trajectory equivalence.


MEAN-073 — All-five finite composition
VERIFIED two fresh legal-input games: Formula1 Retail120M/extra → Offroad six paid changes90M/end → Chicken → Monster six distinct targets125M → intervening SPEED peak8balls/normal return → Rally six correct turns. Completion ticks15520/26925/42717/54010/78512; finalGameOver83056/924072310/fourbonuses/eightnudges; frozen64/reset. No injected ball/rule fields; no gameplay changes. Index `analysis/mean-five-modes-search.json`. Exact three/four/four+SPEED/five regressions share strengthened marathon assertions. Next: real pre-contact context export for bounded Original collision comparison; human feel/full Original timelines remain unclaimed.

MEAN-073 verification: warning-free `cmake --build build/native -j 3`; affected34/34 CTests PASS24.01s (`build/mean-five-modes-regression.log`), including strict golden replays for three/four/four+SPEED/five. JSON/RLE totals PASS. Full suite not repeated because production code is unchanged; prior full312/312 remains historical, now315 configured tests. No Git metadata/configured formatter/linter.


MEAN-074 — Native live contact island
VERIFIED_BOUNDED actual Original408e70 against1036 natural contact states from all-five and existing GOAL+finite-coast routes (110615observed boundaries). All100ballbytes match at wall dispatch or full free/flipper return;358 full wall/material/separation cases also match under both accepted/rejected display answers (716executions). Coverage: all5geometrylayers,119flipper/559free/358wall,65activeNudge,336multiball,2actual LaneSaver tile states. Actual419da4/41e724/40f754 execute; only score/audio/display/music external services adapted. Enabled observer preserves strict all-five finite ball/input/audio golden. No formulas/rules changed. Index `analysis/mean-live-contact-island.json`. No physical raised-fence impact/material6/wholeOriginaltrajectory claim. Next: real eight-ball pair context at408bfc.

MEAN-074 final verification: warning-free `cmake --build build/native -j 3`; full `ctest --test-dir build/native -j 3 --output-on-failure` PASS317/317 in362.23s, including2072-game extended soak150.08s and both new live-contact/observer tests. Python syntax, JSON/RLE totals PASS; final changed source/test/CMake regions inspected. No Git metadata/configured formatter/linter. No physics formulas/rules altered.


MEAN-075 — Real pair collision + scheduler island
VERIFIED_BOUNDED Original408bfc matches both100-byte records for1861 real pair contexts from127828calls. All38 actual active-ball velocity responses retained:23SPEED/15Offroad;1823guard/no-op contexts and all28slotpairings included; other Original slots remain unchanged. Original408874 visitation matches11132 native tick batches/7patterns, static reference counts0..8. Actual patterns have fixed within-tick counts; phase1/physics/count causality adapted, not wholeOriginaltick proof. Optional pair observer preserves strict all-five finite ball/input/audio golden in two fresh runs. No physics formulas/rules changed. Index `analysis/mean-live-pair-island.json`.
Automated all-five/endurance/bounded-Original acceptance tracks CLOSED within their bounds. Next primary: relocatable Mean release-candidate start/data package; avoid more detail RE unless a concrete gameplay bug appears.

MEAN-075 verification: warning-free `cmake --build build/native -j 3`;18/18 affected CTests PASS20.28s (`build/mean-live-pairs-regression.log`),5/5 pair/contact/observer/five-mode cross-checks PASS11.20s, final pair oracle1/1PASS3.42s. Python syntax/JSON PASS; changed source/CMake/test regions inspected. No Git metadata/configured formatter/linter. Full suite not repeated for optional read-only observation/test changes; prior317/317 full suite remains historical,319 now configured.


MEAN-076 — Mean native RC package READY
`build/releases/mean-private-data/play-mean` starts the relocated RC. Program archive2641585bytes; private data archive876858bytes, eight exact-profile files. Original DAT/PE/minigame data remain only underbuild/private; program archive asset-free. POSIX source/bundle launcher supports --data-dir/SLAMTILT_DATA_DIR/--check and rejects missing/corrupt/unsupported data. Installed executable uses $ORIGIN/../lib; SDL3/libxmp bundled, source profile replaced by runtime metadata via env override. No Python/Wine/Unicorn/source checkout needed to play.
VERIFIED archive extraction/newpath/spaces/foreigncwd; Bubblewrap hides checkout and binds app/data read-only; zero checkout accesses/Python-Wine execs. Native SDL audio/fullscreen/focus/highscore/newgame acceptance passes; two complete packaged-data all-five games retain83056/924072310/hash. Final package also passes realhost --require-gpu/audio/frontend and screenshot inspection. Localx86_64 ABI glibc2.43/GLIBCXX3.4.32; no universal Linux compatibility claim. Index `analysis/mean-release-island.json`; docs `docs/release.md`. Next primary: supported raw Windows EXE/DAT import into this verified data profile.

MEAN-076 verification: warning-free `cmake --build build/native -j 3`;73/73 affected CTests PASS33.59s (`build/mean-rc-regression.log`), including isolated archive/frontend/all-five acceptance. Realhost GPU/audio/frontend14frames PASS; screenshot inspected. Python/shell syntax and JSON/hash checks PASS. No Git metadata/configured formatter/linter. Full suite not repeated for path/launcher/install/package changes; prior317/317 full suite remains historical,320 now configured.


MEAN-077 — Supported raw Demo import island CLOSED
IMPLEMENTED tools/slamimport in source and RC: Python3 stdlib only, no Wine/Unicorn/runtime capture. Exact EXE + MEAN.DAT + MAIN.DAT produce all eight existing-profile files byte-for-byte. Old Watcom PE .bss has raw size but source pointer0; explicit zero mapping required. LUT extracted from original image; 110 scalar DWORD writes preserve existing bounded-verified engine/flipper/minigame startup snapshots, not a recovered full loader. No original code/assets embedded in recipe. Other revisions/corrupt assets/missing MAIN/existing or empty destination/dangling symlink rejected; inputs and prior outputs preserved.
VERIFIED isolated entpacked RC imports raw originals with checkout/cache inaccessible, then native SDL frontend and two complete all-five games use newly imported data with unchanged83056/924072310 golden. Native runtime trace still has zero checkout accesses/Python/Wine execs. New ready pair: build/releases/slamtilt-mean-rc-import + mean-private-import; start latter/play-mean. Evidence analysis/mean-import-island.json, analysis/traces/mean-import-acceptance.json and mean-package-acceptance.json.
Verification: warning-free cmake --build build/native -j3; ctest -R '(import_acceptance|package_acceptance|launcher)' -j2 PASS3/3 in7.25s; Python syntax PASS. No gameplay changes; full suite not repeated,321 configured. Next primary: first-launch frontend original-data selection/import; broader Retail/Amiga/ABI support remains separate.


MEAN-078 — Native first-start/data selection island CLOSED
IMPLEMENTED slamsetup SDL window using existing UiSkin; native folder picker/drop, async existing stdlib importer, exact-profile checks and per-user remembered data. Launcher opens chooser when no default/saved data, --setup reopens it, explicit data paths remain authoritative and --check stays noninteractive. Read-only original/program dirs supported; imports/preferences stay in SDL user dir; failed or unsupported selections preserve prior preference. Safe argument arrays handle shell metacharacters without execution. No gameplay changes/new RE.
VERIFIED4/4 setup/import/package/launcher CTests in7.35s; warning-free CMake build, Python/shell syntax. Isolated relocated package imports raw original folder via native setup, remembers prepared data, then starts SDL game without a data argument and without Python/Wine runtime invocations. Two complete all-five games preserve exact existing golden. Native welcome rendered/visually inspected on actual desktop; final RC real GPU/audio/fullscreen/focus/highscore/reset acceptance PASS. System portal click itself not automated; selection/import/persistence paths covered via --select. Evidence analysis/mean-firststart-island.json, analysis/traces/mean-setup-acceptance.json and mean-package-acceptance.json.
Ready program build/releases/slamtilt-mean-rc-firststart; private starter build/releases/mean-private-firststart/play-mean. Native game still needs no Python; raw import needs Python3 once. No full-suite repeat for isolated frontend/launcher/package changes;322 configured tests. Next primary: older-ABI Linux RC compatibility, retaining working Mean/first-start fixtures.


MEAN-079 — Older Linux ABI island CLOSED within tested userspaces
IMPLEMENTED pinned Debian12/GCC12 toolchain, rebuilt SDL3.4.18/libxmp4.7.3, isolated offline Port build and prebuilt-archive acceptance. No gameplay/source-lift changes. New ABI maxima GLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9 versus prior host GLIBC2.43/GLIBCXX3.4.32. Exact pins and installed apt packages recorded; apt is not a bitreproducible snapshot. Source r/o during Port build; no game assets in image/program archive. Own Port compile has0warnings; upstream SDL Switch HID GCC12 calibration emits18 maybe-uninitialized warnings, unsuppressed/unmodified.
VERIFIED actual Debian12 glibc2.36 container userspace and current host: native setup/raw EXE+DAT import/eight exact hashes/saved path/frontend/audio/focus/highscore/newgame. Both environments run two full five-mode finite games with unchanged83056/924072310/hash7646546959636972790. Old runtime has no source checkout/network and prepared app/data r/o. Host strace still0checkout/Python/Wine runtime accesses. Final older-ABI RC also passes actual host GPU/audio/frontend; screenshot inspected. Remaining distro/kernel/driver universality unclaimed; container shares host kernel.
Ready: build/compat/releases/slamtilt-mean-rc-bookworm-data/play-mean. Program/archive remains asset-free; private data separate. Evidence analysis/mean-compat-island.json and analysis/traces/mean-compat-acceptance.json/mean-compat-package-acceptance.json. Verification tools/slamcompat + python tools/verify_mean_compat.py PASS; affected CTests4/4PASS7.27s, Python/shell syntax PASS, repeated builder preserves existing release. Full suite not repeated for packaging/build-only changes,322 configured. Next primary: native raw importer to remove one-time Python dependency; preserve exact profile and Mean fixtures.


MEAN-080 — Python-free native import island CLOSED
IMPLEMENTED C++ PE mapper/state recipe/SHA-256/profile validation plus standalone native slamimport; GUI background import and saved-data checks now native, portable launcher delegates supported-profile validation to native binary. No OpenSSL/new runtime DSO, no Python/Wine/emulator/external checksum process for import. Existing Python importer retained only as independent test reference, excluded from Runtime. Same frozen recipe and exact eight hashes; no gameplay changes. Exclusive staged publication preserves prior outputs/empty dirs/dangling symlinks; private manifest parsing rejects malformed rows.
VERIFIED native vs independent Python reference8/8byteexact; four standard SHA vectors including million-a on modern/old compiler. Isolated host and Debian12 imports pass with PATH=/no-import-tools; host strace0Python/Wine/sha256sum import executions and0checkout accesses. GUI/data selection/restart/highscore/focus/audio and two complete all-five games per runtime retain83056/924072310/hash7646546959636972790. Own CMake builds0warnings; affected5/5CTestPASS8.10s;323configured/full suite not repeated for import/frontend/package changes. Older ABI remains GLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9; final RC also passes realhost GPU/audio/frontend.
Ready: build/compat/releases/slamtilt-mean-rc-pythonfree-data/play-mean. Import and play need no Python; developer build/tests still may. Evidence analysis/mean-native-import-island.json and traces mean-import-acceptance/mean-package-acceptance/mean-compat-acceptance. Next primary: actual laptop frame pacing/input-to-flipper latency acceptance; retain deterministic gameplay and only optimize measured bottlenecks.


PIRATE-COMPLETION-038 final verification: 6/6 affected CTests PASS147.73s; modern/GCC12 builds0warnings;12actualWayland/PipeWire event cases PASS. RC1 fullscreen real-clock natural game15600steps/78.0398s matches10Originalvectors and233audio requests,0clampedframes;15.83M/ABC/GameOver/F1 andprivate saved-score fresh-process reload/no-rewrite PASS. Actual Debian12 import/25792game+90340rule steps andrelocated archive pass. Static automatic-throw PE snippets:`analysis/pirate-knife-auto-static.json`. Exactcommands/logs retained inislandJSON. NoGitmetadata/configuredformatter/linter;Python syntax,JSON/index references and48semanticcontracts PASS.

050 final verification: build0warnings; 5/5 final targeted CTests PASS78.34s. All25 distinct affected tests pass across runs: broader24-test run23PASS/1audio timeout180s, unchanged audio aggregate separatelyPASS164.23s. No timeouts/assertions weakened. Python syntax, PE hashes, seven fixture contracts, six SDL-key cases, JSON/evidence links and31-fixture audit integrity PASS. No Git metadata/configured formatter/linter; no full-suite claim. Logs and commands in050islandJSON.


2026-10-28 — Native controller/Batocera candidate
- IMPLEMENTED shared gamepad input in menu/options and Mean/Pirate/Space/Demon, saved pad bindings, mixed input, RT pull/release and neutral barriers. Original launch force unchanged.
- VERIFIED virtual SDL6 contract groups, actual four-table controller flow + menu, AArch64 QEMU controller/menu/import/table smokes; launcher14 cases. Physical Pi/controller/GPU/audio remains unverified.
- Candidate: build/arm64-controller-candidate/slamtilt-reborn-linux-aarch64.tar.gz. Publishedv1.0 unchanged. See controllers.md and packaging/batocera/README.md.

## Menu refresh verification (2026-10-28)
- Original-art Reborn menu and matching options implemented; classic remains selectable.
- Six option categories captured at 800x600, 1280x800, 1920x1080, 2560x1600 (SDL dummy).
- Actual OpenGL captures: main/options/preview, window 1566x946, render 2506x1514, pixel density ~1.6003.
- Evidence: build/menu-review/gpu-{main,options,preview}.json and PNGs; options-matrix.jpg.
- port_options, main_menu_flow, original_menu_pixels, gamepad_input passed. No release published.

## Browser verification 2026-10-29
Browser HTML: Vivaldi 4x4 canvas collapse fixed by explicit stage-filling CSS. Compact offline single HTML 3,025,140 bytes (78.4% reduction); 19 checks each on Chromium, Vivaldi, Brave. Local candidate build/web-release/Slamtilt-Reborn.html; published release unchanged.

## Release optimization / lamp upload cache — 2026-10-29
- Space/Demon immutable lamp-frame cache: 48,000 -> 1,026 and 52,000 -> 736 uploads across 1,000 rendered frames. State vectors and full BMP exact over 4,000 ticks per table.
- Five 8,000-tick, trace-free software-renderer samples: Space median wall -9.0%, Demon -1.46%; RSS effectively unchanged. Includes startup/replay JSON, not pure simulation or GPU frame latency.
- Optional compact+LTO stripped native sizes: menu -12.54%, slamview -2.78%, slamslice -1.61%. Mean/Pirate 4,000-tick profile parity and BMP exact; Space/Demon profile parity also verified. Flags remain opt-in pending CPU/platform benchmarks.
- Evidence: build/optimization-size/report.json, build/optimization-profile-verification/report.json, build/optimization-compact-verification/report.json, build/lamp-cache-benchmark/summary.json. Windows/ARM64/HTML optimization-profile validation remains open; no release changed.

## Phase profiling — 2026-10-29
- Optional slamslice --performance-output reports setup/simulation/post-step/render/present and frame p50/p95/p99; disabled path retains normal gameplay. Profiling enabled: state vectors and BMP exact over 4,000 steps per Space/Demon.
- Five runs each, input-only schedules, 4,000 steps per run, software/dummy vs OpenGL/actual Wayland, no trace/audio: original shared/table/DMD tick average 22–24us on this x86-64 host. Software presentation dominates; no physics simplification justified.
- Evidence: build/port-stage-profile/summary.json; build/performance-parity/report.json. Audio/GPU-effects cost, Mean profiling and ARM64/Windows timing remain open.

## Shared engine experiment — 2026-10-29
- SLAM_SHARED_ENGINE Linux-only opt-in; normal builds unchanged. Relative build RPATH verified after relocation; internal function binding avoids PLT interposition overhead.
- Exact states and BMPs over 4,000 steps on all four tables with final shared library: build/shared-engine-final-parity/report.json and build/shared-engine-final-retail/report.json.
- About 44% less stripped gameplay-program storage and 41% less gzip archive, counting shared library; exact final sizes/hashes: build/shared-engine-size/report.json. This covers two gameplay frontends and engine, not a complete distribution.
- NOT promoted: wall-time phase regressions exceed 5% for Demon in some trials; noisy compositor timing and PIC costs need separation. Five-run measurements: build/shared-engine-performance/report.json; first interposition trial retained separately.
- GPU/audio bounded timings: build/gpu-audio-profile/summary.json. Accelerated dummy-audio samples do not establish real-time audio decoding cost. Next: CPU-only timing and controlled affinity for shared-library assessment; Windows/ARM64 packaging remains open.

## CPU-bound validation and safe archive reduction — 2026-10-29
- Linux opt-in thread CPU timing separates simulation CPU from wall time; unsupported platforms explicitly report no CPU clock. Shared compiler-local binding reduced the observed overhead from 19–23% to 2–4% in five alternating 12,000-step repetitions. OpenGL tail-frame variance still blocks default adoption. Decision data: build/shared-engine-cpu-performance/report.json; earlier trial retained as before-compiler-binding.json.
- Final shared-engine state/BMP parity: 12,000 steps on each of four tables, build/shared-engine-local-parity/report.json and build/shared-engine-local-retail/report.json. Runtime installation bundles the matching private engine library, resolved from package lib/; no default runtime change.
- Optional `tools/slamtilt-pack --compression xz`: full static package 10,315,894 -> 6,632,996 bytes (-35.70%), tar payload exactly identical to gzip. Manifest hashes and no-original-assets check pass; packaged four-table 400-step smokes retain exact states/BMPs. Evidence: build/shared-engine-package/static-compact-verification.json, build/static-package-{mean-pirate,retail}/report.json.
- Local Linux candidates only, no release update. Remaining: stable GPU tail timing, older Linux and ARM64/Windows validation, full gameplay audit beyond tested scenarios.

### Audio parity investigation, 2026-11-01

- Experimental STIM mixer: four Retail starts each bit-exact for 2,048 manually
  clocked ticks; 65 synthetic gain levels exact; non-STIM isolation exact.
- All-order survey: 522 exact, 33 differing, 8 unresolved of 563 starts,
  32 ticks per case, before the channel-mute safeguard. See
  `analysis/stim-pcm-all-orders-survey.json` and evidence STIM-PCM-2026-11.
- The initial experiment has since been superseded by the v6 build; see the
  later STIM-PCM-2026-11 evidence for its scope and remaining unknowns.
