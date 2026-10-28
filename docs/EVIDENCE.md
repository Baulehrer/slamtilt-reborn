# Evidence log

## ADF-071 — Actual reads identify two missing Demon frames

`analysis/traces/asset-read-coverage.json`: three60000-step native scenarios, exact100-byte ball state eachstep,197758unique inputbytes read, no unresolved source-difference bytes afterfix. Original mask/art payloads are independently checked before classification. The first experimental genericPirate keyboard routing diverged atstep766; it was rejected and replaced by the actualPirateSession/replay implementation, not a relaxed state check.

Observed407020 DMDobjects: Demon target134b30/sourceBin65296/caller-return410dae fixes1byte; target1402f0/sourceBin9bcba/caller-return413927 fixes21bytes. Both complete480-byte source objects matchPC data andare actually rendered inmeasured scenarios. Mask ED168 remains original, not replaced. `mean-asset-read-audit.json` identifies488bytes ofeight authenticmaskvariants andanunconsumedzeroisland inexplicitloaders.

Scope: shared-native read evidence; not originalAmiga gameplay execution andnot exhaustiveall-path coverage. Productionbinaryhashes remainunchanged bybuilding/running the separateaudit. Newassetdata legitimatelychangesDemonimportfingerprints; older fingerprints remain accepted.


## ADF-070 — Scene identity, overlap and legacy compatibility

VERIFIED: `analysis/traces/amiga-fragments-v2.json` executes the actual original service binding: Game0x2d2 loadsA4=0x103e2, field+44 contains0x3d8a, service-24 enters0x3d66→0x3d8e. All13Pirateframes match compiledadapter output; frame0 consumes through0x6b8c4 whileentry1starts0x6b8c3.

`pirate-amiga-fragments-v2.json` and `pirate-amiga-mutable-scene-v2.json` establish source/native callers, count52/77andframeindex>>2; laterreport corrects WindowsPE file/VA mapping. Actualpanorama is192×20/960bytes plus80-byte tiles; nearby0x14155c was not established as a framebuffer and was left unchanged. `demon-amiga-fragments-v2.json` records two full480-byte identities, with individualsourcecallers/dimensions explicitly unproven. Mean1516c4/1525c4 likewise match complete source/PC frames and existing nativeconsumers.

`amiga-v2-legacy.json`: four unchangedRC4private datasets verify/run100steps each. Native16ksteps andDebian12ADF-only/PCacceptance are indexed by `analysis/amiga-fragments-island.json`. No originalAmiga physics orrules equivalence follows from these display/data proofs.


## ADF-069 — Original display execution and source-specific artwork

VERIFIED: `analysis/traces/amiga-dmd-original.json`: Original68k decoder0x3d8e..0x3e22 plus executed LUTinit0x4f1a..0x4f48 (256 distinct entries) agrees with all1719 converted bank frames. `amiga-dmd-banks.json` links sourceSHA/directories/nativeoffsets:1712 exactPC frames andsevenMean source variants. MeanBin0x65e28..0x65ec8 selectsbank0x6cd65 withcount/4 for28ticks, then25ticks and10000000award; counterpart nativecallback0x4132d4. Visual text differs TIRE/TYRE.

VERIFIED: `amiga-contact-frames.json`: fourRaw records, twelveframes/31488bytes, dimensions/anchors and original planar indices verified. Review rejected an initially proposed79→127/207→255 remap: palette colors differ, so sourceindices are retained. Full mask semantics UNKNOWN.

Bounded package proofs: `analysis/traces/amiga-package-debian12.json` and the PC regression indexed by `analysis/amiga-adf-island.json`. Shared-native geometry/gameplay acceptance does not establish originalAmiga gameplay parity. Remaining individual DMD fragments are not covered by the bank proof.


## ADF-068 — bounded native source integration

VERIFIED byte comparison: `analysis/traces/amiga-pc-assets-comparison.json` records all42 normal/hit/render planes across14 base layers, plus75 ball frames, mask and both scorefonts: converted Amiga bytes equal Windows retail. Differences retained: MeanL3/R3 andSpaceL2/R2 flipper art; Demon lamp8 has24 source rows versus25 native rows (transparent padding). This supports asset/layout reuse, not physics parity.

VERIFIED: `analysis/traces/amiga-adf-reader.json` independently compares native extraction/SLAM with amitools/Python: DLM54 files/21 compressed and HD-Ninja81/57; 20 existing decoded references each. `analysis/traces/amiga-import-integration.json`: DLM five-disk import, destination preservation/missing-set rejection, all four 100-step sessions and persisted menu/four-child reload PASS. These prove integration, not original-Amiga trajectory parity.

Original Game.exe hunk0:0x4108/0x43c6 binds hunk1 fonts0x2bce/0x2f1e; Matrix.Dat directory entry8 binds via hunk0:0x80a6..0x8110 and selects ball rows via0x6afa..0x6b12. Adapter reads data only. HD-Ninja full import currently rejects shared graphics revision; no source substitution.


## DAT-ONLY-067 — Independent initialized data, no executable input

VERIFIED_BOUNDED: native math formulas produce56,232bytes exact, with17 documentedquantization cases. Native descriptors/parameters/captions/callback-ID directories produce shared/allfour initialization454a00..466fec75,244bytes exact andsixMean ranges; fullinitialized readsets3×4000Originalsteps exact. Original EXE is a development oracle only. No original instruction/header/IAT/raster/PCM blobs included.

Fresh isolated program+DATs+emptyprofile: checkout/home/corpus/caches hidden, ownPIDnamespace, readonlyprogram/raws, networkoff/emptyPATH. Allfour firstimport, twoactual4-child reloads,4×4000 exact vectors/audio, corruption/missing/allocation rollback pass. FinalDebian12 archive separatelyimportsDATs andruns4×60000 exactlogicalticks. Fiveexplicit legacy import modes preservepreviousfilehashes. GCC12 warningcleanup produces byte-identical archive, so measuredbinary identities retained. Mean fullOriginaltrajectory remains PARTIAL; no newphysical/GPU/listening claim.

Proofs: `analysis/traces/dat-only-{math,retail-data,import,package,distribution,legacy-compatibility}.json`. [Index](../analysis/dat-only-island.json).

## MEAN-RETAIL-066 — Retail-only import and native data ABI

VERIFIED_BOUNDED: supportedRetail185d5893... andDemo31192e0b... MEAN.DAT/MAIN.DAT SHAidentical. Six source ranges/60,640bytes normalized with124 explicit source-expected pointer fixups. Full math island4556cc→42a144/56,232bytes exact; inline masks403fb8→403fe8/32bytes exact, actual consumer409060/40906d. QA-only memory-read audit isolated masks after retained first divergences6/625/1385. Generated code/header bytes are not copied as instructions.

`mean-retail-import.json`:68k native state/audio ticks, finite lifecycle,18minigame cases,Rally,combined modes; Demo directories hidden andOriginalEXEs masked afterimport. `mean-retail-package.json`: packaged importer/menu/allfourchildren/4000ticks. `mean-retail-distribution.json`: actualDebian12, no checkout/Demo inputs, Retail-only import/240k steps/allfour. `mean-demo-import-regression-066.json`: eight legacyDemo hashes unchanged. Four targetedCTests pass including frozenRC1 integrity; builds0warnings. No complete OriginalRetail startup/trajectory, physical input/GPU/listening or DAT-only first-import claim.

[Index](../analysis/mean-retail-island.json).

## REBORN-065 — Shared presentation, review and actual distribution QA

VERIFIED_BOUNDED: new Neo-90s/Classic frontend, 12 rendered layouts, transactional import/theme persistence, targeted process/configuration/lifetime tests, ASan+UBSan and11 CTests pass. Actual Debian12 native import/240,000 accelerated steps and relocated hidden-checkout package pass. Actual compositor Alt-Tab/manual-pause/audio-resume/F10 passes all four tables (`reborn-focus.json`).

Legal source/native suite:12 cases/272,000 ticks. Retail exact vectors/audio; Mean native determinism separately backed by22 verified Original component cases (14 excluded) and3,512 camera contexts. Full Mean Original trajectory remains PARTIAL. Demon41-instruction DMD extension at410ea0 and Pirate original user-input binding correction have separate hash-bound gap reports.

Timing remains separate: all four pass60,000-tick GPU/fullscreen runs each (240,000ticks/20minutes/0clamps). Demon background run is explicitly user-requested controlled focus, not real foreground proof; QA-only SDL-call instrumentation, packaged binary unchanged,300,008.67ms/no SDL call over50ms. Failed/interrupted attempts retained; prior timing-failure cause UNKNOWN. Shared archive61b44e1f1ee7681317f53dc36ddf980e4f766c2c7b26045ca4ee3922f858c476; SHA-bound gate rejects wrongarchive/evidencehash and missingfocusproof. No human feel/hearing, all-seed or universal-driver claim.

Files: `analysis/traces/reborn-{distribution,package-isolation,focus,gameplay-acceptance,visuals,menu-acceptance,review-acceptance}.json`, [review](reborn-review.md).

## FRONTEND-064 — Original menu and four-table lifecycle

Claim: OriginalRetailmenuart supports a sharednative four-table selection/import/options/return flow without alteringgameplay.

Evidence: MENU.DAT SHA eb46503d8a7b7b70366403ffc5a4d9075271bafa10a7efac3abc761dcb5990ee; RGB f04a774e60b1f56bb77d9bfda4690fd55f432709cab284717f0b4cd94453e946. PE40C23A..244 selectsbackground;40DB0E..19 selects palette. Pixelunitandactualdesktop screenshotchecked. Nativeimport/fourrealchildren/return/options/failurepreservation pass; relocatedarchiveworks withhiddencheckout, readonlyoriginals, networkoff andemptyPATH. NineCTests includeexistingfourtablegameplayregressions.

Confidence: VERIFIED_BOUNDED_HOST. Nativehitboxes visual-layoutonly. F10/MainMenu SDLquit tested inPortOptions; finiteactualchildren verifyparentreturn. No physicalkeyboard/mouse/listening orcombinedolderABI claim.

[Evidence](../analysis/frontend-island.json), [Frontend](frontend.md).

## DEMON-RC-063 — bounded playable single-player release

Claim: Demon RC1 satisfies the separate bounded completion and native distribution gates.

Evidence:20 manualcontracts/36packagedfixtures/222,852steps/861audio exact. Isolated rawimport/selection/storage/options; actualDebian12; packagedGPU/Wayland/PipeWire10512steps/52.596s/0clamps/twelvevectors/31audio and125kABC save/freshreload. Six affectedCTests pass, malformed releaseindices reject. ArchiveSHA2eedcecf98dd6b0f76e3e0d2d98ef717060b13a51df70969242c70d8ea10cf11.

Confidence: VERIFIED_BOUNDED_SINGLE_PLAYER_RC. Initialhostattempt248clamps retained; causeUNKNOWN, unchangedruntime andthresholds passedonisolatedretry. Physicalinput/listening/allseeds/universaldrivers/whole-raster equivalence remainunclaimed.

[Evidence](../analysis/demon-rc-island.json), [Gate](../analysis/traces/demon-rc-gate.json).

## DEMON-RELEASE-062 — native import to real-time packaged game

Claim: The supported Retail Demon profile runs as an independently imported native standalone preview.

Evidence: five exact files; isolated archive/native empty-PATH import/storage/options; four Debian12 fixtures/30,548 exact steps; actual Wayland/GPU/PipeWire10,512steps/52.577s/0clamps/twelve vectors/31audio; actual ABC save/freshreload. Public reports pin the archive SHA and original input hashes.

Confidence: VERIFIED_BOUNDED. One supported Retail build and recorded cases/current GPU host. Physical keyboard/listening/full-raster/all-seed/universal-driver coverage not claimed. Final RC metadata promotion remains separate.

[Evidence](../analysis/demon-release-island.json).

Only the stated claim is supported. Confidence is strength of evidence, not amount recovered. Original assets and disassemblies remain local under build. Addresses follow [ARCHITECTURE.md](ARCHITECTURE.md).

## CORPUS-001 — build equivalence and exclusions

Claim: several named variants share the same executable, while containers and other files differ.

Evidence: SHA256 groups and structural matches in [corpus.json](../analysis/corpus.json) and [binary-diffs.json](../analysis/binary-diffs.json); reproducible `tools/corpus_scan.py`. Retail-labelled TOSEC, DLM, DLM-alt, 68040 Digital Corruption, JST and CD32 share unpacked Game.exe SHA256 `22b894d3667887a0822e63999598ae80813e4a5fccf7881228a97189ebaa3a84`. EU SLAMTILT.EXE is an InstallShield wrapper. Resurrection1999 is a different game family. Therefore filename/version labels alone do not establish executable revisions or patch locations.

Confidence1.00 for byte identity, no claim all distributions are identical.

## PATCH-001 — source-supported Amiga patches

Claim: source WHDLoad revisions3.3/3.4/3.5 expose concrete loader/menu/VBR/decoder boundaries.

Evidence: [patches.json](../analysis/patches.json), 30 entries, original-byte contexts checked against unpacked HUNK0, source reference arithmetic normalized. Decoder hook HUNK0+0x8280, VBR+0xea2, quit+0x892, menu guards+0x936a et al. Context bytes are not automatically replacement spans. Compiled3.6 not yet semantically mapped.

Confidence0.98. Ghidra/radare2 are unavailable here; [amiga-hunk0.r2](../analysis/amiga-hunk0.r2) is an annotation export for base0, not an applied project. Regenerate with actual load base using `tools/export_annotations.py --hunk0-base ADDRESS`.

## AMI-001 — hardware islands

Claim: original main HUNK contains hardware takeover, interrupt dispatcher and VBlank branch.

Evidence: static disassembly and WHD source in [Amiga memory map](amiga-memory-map.md). Vector setup+0x21c; dispatcher+0xece tests INTREQR bits; VBlank branch+0xf0c; decoder+0x8280. Hardware literal scans are candidate data, not proof every match is executed code. Input+0x5292 is candidate handler, not a recovered input state machine.

Confidence0.95 for named core anchors; no dynamic timing measurements.

## AMI-002 — gameplay code outside Game.exe

Claim: decompressed table payloads contain executable code, so Game.exe alone is incomplete for physics/rules analysis.

Evidence: WHD source intercepts decoded length0xa89d4 (Demon.Bin) and searches range+0xa0000..+0xa8000 for instruction pattern `12f9ffffffff12f9ffffffff`, replaces it with guarded writes. Source also repairs MOVEC VBR in decoded0x60540 payload. See [patch map](patch-map.md).

Confidence0.99. Specific physics/rule entry points remain unknown.

## WIN-001 — Windows executable family

Claim: original Windows builds are disassemblable PE32/i386 with Watcom runtime clues.

Evidence: PE sections BEGTEXT/DGROUP, linker metadata2.18, explicit `WATCOM C/C++32 Run-Time system` string, imports and thunk cross-references in [Windows symbol map](../analysis/windows-symbol-map.json). Reference RIP/USA SHA256 `185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6`. PE timestamp is metadata, not authenticated build time.

Confidence0.99 for runtime family; individual C/C++/assembly provenance remains unknown.

## WIN-002 — API islands

Claim: DirectDraw, DirectSound, WinMM and Win32 message/file calls locate platform boundaries.

Evidence: direct imported-thunk calls; graphics creation0x4020b9/0x40383e; DirectSound0x44d5e7; message/clock island0x402c72..0x402d99; table loader0x40f7e0. See [Windows map](windows-subsystems.md) and reproducible `tools/analyze_windows.py`. COM calls are indirect; import graph alone is incomplete.

Confidence0.95; game tick and physics call chain not recovered.

## ASSET-001 — original indexed Windows playfields

Claim: four table DATs contain directly reusable 320×600 indexed base images and 256-entry00RRGGBB palettes.

Evidence: Mean initializer0x41bb88 takes DATbase+0x1590c8; next anchor+0x1882c8, difference1024+320×600. Other palettes are also code-referenced. Width320 has independent row arithmetic at0x40b76c/0x40b808. All four decoded images were visually inspected. SHA256/offset profiles in [formats](file-formats.md).

Confidence1.00 for recovered base-image layout. No dynamic compositing claim.

## RENDER-001 — native byte fidelity

Claim: native SDL3 exports reproduce original indexed base images exactly.

Evidence: independent Python DAT palette indexing versus every native BMP RGB pixel, four tables×192000 pixels, zero differences. Headless texture/window smoke and a real desktop three-frame smoke passed. Reports [renderer-validation.json](../analysis/renderer-validation.json), [verification](verification.md). Synthetic native tests also reject malformed layouts. Camera input is a new manual viewer, not original scrolling logic.

Confidence1.00 for pixels checked, no original-game screenshot equivalence.

## ASSET-002 — SLAM decoder

Claim: bounded backward-MSB LZ decoder produces valid declared-length original payloads.

Evidence: original HUNK0+0x8280 decoder translation; trailer at12+packed contains mode/reservoir/count. `tools/slamdecode.py` decodes13 retail-disk1 assets with exact header lengths. Decoded Music/IntroMusic begin STIM and independently load/play with libxmp. Full table extraction and manifest in [decoded-manifest.json](../analysis/decoded-manifest.json) when completed.

Confidence0.99; arbitrary corrupt inputs have no original checksum oracle.

## TABLE-001 — shared engine and per-table callbacks

Claim: Windows has shared loader/display with table-specific code/data registration.

Evidence: four-entry dispatch table0x404e60; Mean initializer0x41b9e0 loads DAT then registers code pointers in0x46de14..0x46de64 and data pointers as DATbase+constant. Twenty callback slots with instruction anchors are in [table engine](table-engine.md) and [Windows symbols](../analysis/windows-symbol-map.json). This supports a mixed hardcoded engine/table architecture, not proof of a scripting language.

Confidence0.94. Individual physics/rules callbacks not classified.

## WIN-005 — fixed-point-like display accesses

Claim: Windows0x40b720 extracts shifted coordinate-like fields in a display-copy routine.

Evidence: accesses unaligned+2,+0xa,+0xc,+0xe,+0x10,+0x12 and arithmetic shifts16; width320 copy arithmetic. This is insufficient to name ball state, confirm a fixed-point physics model or infer Amiga equivalence.

Confidence0.85 for observed operations;0.30 for sprite interpretation.

## SCORE-001 — saved-score representation

Claim: persisted highscore scores use six-byte Packed BCD, most significant digit first.

Evidence: independent supplied shm.c and SlamtiltJudge.cxx implement this format; STTF record stride14 and CFG stride10; default saved score+initial bytes cross-match between platforms. `tools/slamscores.py` parsed66 files; `slaminfo` cross-check60 STTF files shows zero differences. [Scoring/audio evidence](../analysis/scoring-audio-evidence.json).

Confidence0.99. Runtime scoring arithmetic and trailing record semantics remain unknown.

## AUDIO-001 — existing tracker decoder is sufficient for extracted music

Claim: original decoded STIM music can be rendered with upstream libxmp.

Evidence: pinned upstream STIM loader and successful build; decoded Music256232 and IntroMusic119198 bytes load/start/play with zero return codes and generate5s nonzero44100Hz stereo16-bit PCM each. WAVs are local build artifacts. [Audio results](../analysis/audio-load-results.json), [audio detail](audio.md).

Confidence0.99 for bounded decoding/playback; no listening/timing comparison or event-trigger recovery.

## ASSET-003 — original Amiga playfields and cross-architecture art

Claim: allfour decoded Amiga .Raw files contain the original320×600 row-interleaved eight-plane image with8-bit RGB palette.

Evidence: section directory, plane reconstruction and bounds in [overlay map](amiga-overlays.md), [decoded manifest](../analysis/decoded-manifest.json). Native C++ output independently compared to Python plane extraction: four×192000 RGB pixels, zero differences. Index equality against Windows art is180850/192000 Mean,188406 Pirate,189047 Space,188138 Demon. Differences are real and not yet classified. This proves substantial shared artwork, not identical gameplay.

Confidence0.99 for recovered layout and tested images.

## PHY-001 — live Mean demo ball trace

VERIFIED for recorded fields. Demo SHA31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00. Debugger captured100 consecutive per-ball steps at4088f0, ball pointer4298c8→43e568. X/Y+0/+4 signed16.16, VX/VY+14/+18; writes40a0d2/40a0dd. Raw object words and initial/final states in `analysis/traces/mean-flight-100.json`. Demo200Hz was subsequently proven statically (PHY-005); debugger elapsed time was not used.

## PHY-002 — native bounded physics / collision

VERIFIED in stated scope. `analysis/traces/mean-component-validation.json`:900 native-vs-original-x86 cases, all100 ball bytes identical, integration/free acceleration/material0/1/2; separation skipped both sides. Original40e1d0 normals evaluated into local cache over Mean baseline bitmap. `analysis/traces/mean-native-validation.json`: repeated native100steps deterministic, three contacts; flight X/Y/VX/VY exact through63, first divergence64. Flipper input/pose not recorded per original step; divergence cause UNKNOWN.

## PHY-003 — bounded native flipper lift and input

VERIFIED component comparisons: `analysis/traces/mean-flipper-validation.json`,1500 cases/275 contacts;409050/4096e8 native-generated C++ vs originalx86, ball bytes/return/scratch identical. `analysis/traces/mean-flipper-input-validation.json`:240 sequential edge-input steps4084bc,151 distinct pose snapshots, all78 descriptor bytes identical. Input edge globals4298b8/bc/c0; positive press, negative release consumed by original step. SDL left/right Shift map to these actions (right also upper). This verifies mechanical translation, not whole live-flight equivalence. `.bss` must be zeroed when preparing PE image; pefile mapped-image defaults copied file bytes there incorrectly. Original-derived generated code and data remain local under build.

## PHY-004 — launch components and native flow

VERIFIED components, PARTIAL whole flow. `analysis/mean-launch-routing.json`: original41ab94 initializer;41ac30 gatex>302,y>580,input+30=1 setsVY=-40000hex; caller4089c9 dispatches after integration. `analysis/traces/mean-launch-component-validation.json`:900 original-x86/native cases, all100object bytes identical for initializer+caller state0, gated launch, human-mode materialcallbacks1–3. Separation omitted both sides; notification service stubbed. `mean-native-launch-validation.json` is native-only regression:453states,29contacts,96switch changes, one launch, deterministic repeat. Stops unsupported baseline mask4 atfixedpoint(3763538,30288751). Full live-original launch equivalence is not verified.

## PHY-005 — demo simulation clock

VERIFIED static chain: IAT4402dc importsWINMM timeGetTime; call4036b8→elapsedms→4036ec calls4048cc.404951..404963 accumulates elapsed into43e848;404a5a..404a77 consumes5 then408874. Native fixed step5ms=200Hz. Trace fixtures updated with provenance. This does not establish Amiga timing.

## RENDER-002 — native original flippers and corrected geometry

STRONG static sprite interpretation, visually exercised native. `analysis/mean-flipper-sprites.json` documents initializer40f6aa..40f71a, renderer40a880, transparency40ab39..40ab52. Native screenshot `build/mean-native-ready.png` visibly includes both lower flippers and original ball. Foreground masking not yet implemented; no pixel-equivalence claim for composites.

VERIFIED correction: original40f17d and live bitmap pointer difference prove baseline normalmap959f6, not95af6. Earlier cache offset was wrong by256bytes. Regenerated cache SHA896ecc1015be2a9f62090a139421b6b9567c8775de72ba1a26c14cb981b317a4; live flight first divergence remains64. No causal interpretation attached.

## RENDER-003 — reported rail alignment

VERIFIED: original407a84..407b01, constants4292c7=0.2,4292cf=1/65536,4292d7=-7. Both screen axes use previous/current interpolation followed by trunc toward0 (422f74). Native formerly drew top-left atphysicsX/Y,7px right/down. `analysis/mean-ball-render-anchor.json`; `analysis/traces/mean-ball-render-anchor-validation.json`:7original x87 cases include fractional/negative coordinates and alpha0/0.4/1. CTest `ball_display` checks native helper against these originals. Native frames now use corrected renderY. This fixes the proven rendering offset; full original launch trajectory equivalence is still unverified.

## PHY-006 — reported lower switch freeze

VERIFIED component: baseline switch4,41ce03..41d0fa, y>=450.300random original-x86 cases acrossx0..319,y450..607 preserve all100ball bytes in initial mode; score notification stubbed, mode latches initially0. Included in1200-case `mean-launch-component-validation.json`, zero differences. Native now records the known switch without pausing physics; full score/lamp/mode effects remain open. `mean-native-launch-validation.json`: deterministic870states/49contacts/392switch changes, formerly453/29/96. Regression requires>=800states and>=40distinct positions in frames453..499, proving departure from the reported freeze. An attempted stronger assertion that this scripted path must reach lower flippers was invalid: the path returns to upper ramps, so it was replaced by the actual freeze regression without changing physics to force that outcome. Next unsupported callback layer3/mask1 atfixedpoint(16741364,2759240), ~255.45,42.10.


## PHY-007 — upper ramp continuation / directed acceleration

STRONG static ball-state branches:41ae95..41aefb (layer3 y<64 →layer2, velocity0, acceleration40),41b115..41b17d (y64..90 →layer2, directed target227,101),41c34c..41c38f (layer2 x212..296,y>=150 →layer3),41ae0e..41ae70 (layer3 y>=270,x>=160 →layer1). Implemented in mean_simulation.cpp; score/lamp services remain outside this slice. Correction to earlier plan:4152fc→417238 only adjusts force forfield5c18,415330 handles special state3/6; no separate timer release was established forfield5c14. Ordinary acceleration continues after the zero-velocity transfer.

VERIFIED component:409e18 directed acceleration uses original atan LUT42c9fc (1025u16). `analysis/mean-directed-force.json` records original fixtures/provenance; `tools/verify_mean_directed_force.py` compares all100bytes in64native cases, zero differences. Zero target delta preserves explicit unsupported result rather than inventing a direction.

Native-only launch regression:1852states,90contacts,840switch changes, regular y>=608 drain. Previous upper callback stops870/1125/1333 passed. This is progression/determinism evidence, not full original trajectory equivalence; live flight first divergence remains64.


## PHY-008 — step64 composition isolated

VERIFIED bounded original execution: original40a010→408e70 using the saved static flipper descriptors yields precisely the native step64 XY/VX/VY [12462355,35852158,-46592,158592]. Both lower original probes miss; original409e18 applies free acceleration. Live sample64 differs. `analysis/traces/mean-contact64-static-context.json` preserves state/calls/context hashes. This rejects a native composition error for that tested context, without proving which missing live field caused the contact difference.

Implemented observation path: oracle_trace.py now records27flipper DWORDs at43e850 and40engine-global DWORDs at43e700 at every4088f0 entry. mean_sim_probe can replay this externally observed contact context without reapplying the input/pose tick. Existing static-context100step simulation remains byte-for-byte equivalent when context is supplied per step. Fresh synchronized live comparison pending.


## PHY-009 — synchronized live lower-flipper contact fixture

VERIFIED bounded contact sequence: `analysis/traces/mean-contact-live-100.json` records101original4088f0-entry states plus synchronized flipper/engine context. Starting239.60046,514.57402, ending149.50032,422.04776. Native simulation consumes only the initial ball state and each step's observed external contact context; no intermediate original ball positions/velocities are injected. All101XY/VX/VY samples match,13native contacts, deterministic repeat. Includes original right-flipper motion during the sequence. `mean-contact-live-100-native-validation.json`; conditional CTest `mean_contact_oracle`.

Scope: proves native integration/contact composition for this observed context sequence, including moving flipper interaction. It does not validate autonomous input timing, complete table rules, or retroactively recover the missing context of the older flight fixture (still diverges64).


## PHY-010 — continuous single-player ball lifecycle slice

Original baseline drain gate40897b..408999 requireslayer0 andy>=608. Mean41aaac initially setsstate4 andmovesballoffscreen; ball-save/rule modes choose different continuation. Normal last-ball service43f0d0+24 resolves at runtime to408084, entering globalstate3 bonus/DMD path4072cc. At its completion407794, single-player turn update4077bb..4077e4 consumes positive signedWORD extra balls(player+10), otherwise incrementsWORD ball number(player+e).256original-x86 counter cases match native; player+12 presentation flag is preinitialized1 in this bounded comparison.

Native --play now skips bonus/DMD presentation, applies the single-player counter update, restores layer0 and the already verified41ab94 initializer/callerstate0. Original flipper input continues; cumulative contacts/events retained. No invented respawn delay; no finite game-over or ball-save claim. Viewer title reports ball number.2500deterministic native steps produce1drain,2launches,ball2; `tools/verify_mean_ball_cycle.py`, `analysis/traces/mean-ball-cycle-validation.json`. Existing single-ball launch test still stops at drain; continuous mode is explicitly enabled separately.


## RULE-001 — first native scoring event

VERIFIED: baseline switch4 handler41ce03..41d0fa, y>=450, calls score service43f0d0+58 withEAX=0x61a8=25000 in each of fiveXregions (boundaries23,45,160,275). Call sites41ce28,41cecc,41cf62,41cff7,41d081. Additional table-mode awards/lamps remain unported. Native awards on the existing observed switch-entry dispatch, retaining the original no-mutation ball behavior.

Shared service40560c converts uint32 points to decimal and adds to six-byte packedBCD player score through405708, preserving decimal carries and discarding overflow beyond12digits. `src/rules/mean_score.h` uses modern uint64 modulo10^12. `tools/verify_mean_score.py`:320addition cases including carry/overflow plus320original lower-event cases acrossallXpixels, zero differences. Additional mode awards disabled in the bounded event comparison.

Native2500step regression:3awards=75000points; sustained switch4 samples do not repeatedly award, and score survives next-ball preparation. Viewer draws a temporary native BALL/SCORE strip with SDL debug text (not original DMD). Screenshot `build/mean-score-ready.png`. Physics/contact oracle and ball-cycle regressions still pass. Full table scoring, multipliers/bonus/jackpot logic remain open.


## RULE-002 — contact response, base scores and original flashes

VERIFIED bounded human-mode material3/4/5:41e092 fixesnormal=-256 andrequests6830points;41e154 activatesonlyincomingnormal>64, fixesnormal=-416 andrequests6830points; otherwise material4usesordinaryfactor80.41e245 usesfactor64 andrequests50000points. Material3 triggers438b38 triplet[0,0,2]; material4 selects438b08(leftx<=160) or438b14(right) with[0,0,3]. Original bonus43f38a and other mode/rule effects excluded.1000original-x86/native comparisons match all100ball bytes, base score and trigger selection; `mean-contact-event-validation.json`. Native6000step cycle continuespastpreviousmaterial5 stop,3launches/2drains/275000points, deterministic repeat.

Original flash sources: DAT85cfe (64x51 at0,549),91dee(64x50 at240,550),82dbe(48x66 at0,140),3frames used each. Source40a984 offsetsframe*width*height. Original418030 triplet progression and renderer-busy gating match240native steps. Dispatch417d68→419890 registeredat43f340(callback+3c);404a88..404b15 runsitfrom20ms accumulator=50Hz. Native schedules it every4physicssteps with immediate frame consumption. Original dynamic mask/compositing not yet ported; native renders raw original rectangles before flippers/ball, so pixel equivalence is not claimed. `analysis/mean-contact-animation.json`, `mean-contact-animation-validation.json`, synthetic bitmap-contact smoke screenshot `build/mean-contact-flash.png` (6830points). Synthetic fixture is explicitly not a live-original trace.

Exploratory long native run reaches8409states/5launches/4drains/398contacts/331830points, thenunsupportedlayer3/switch1 atfixed(5619534,9262469),~85.75,141.33. This is next bounded gameplay blocker, not original trajectory verification.


## PHY-011 — bundled ramp/material/switch continuation

VERIFIED bounded original-x86 comparisons: `mean-ramp-bundle-validation.json`1200 cases, `mean-material-bundle-validation.json`512, `mean-baseline-one-bundle-validation.json`480, `mean-switch-bundle-validation.json`512, all zero differences across100ball bytes (plus relevant gates/base awards). Sources and scopes are retained in each fixture/helper. Layer4 hit/normal/mask offsetsd5466/d20d6/db406, stride3390, one extra plane. Original4388c0 callback table gives41e828 for both layers3/4; launch-component test1200 cases includes75layer4 wall responses. Initial43f390=-1 proven419b95..419bcb; material7 acceptance is not assumed. Player+8 increment500000 at41b2e8 is distinct from packedBCD score bytes0..5. Native route coverage uses synthetic flipper schedules, never presented as original trajectory equivalence.


PHY-011 addendum: ramp comparison extended to1600cases, including400 layer1 right-return cases41c78c..41c84d; all100ball bytes match. Baseline switch3 no-op region41d94c matches480cases (`mean-baseline-three-bundle-validation.json`); capture regions excluded. Coverage recorded in `analysis/traces/mean-route-coverage.json`, three full12000step schedules and one left-capture stop; deterministic repeat identical.


## PHY-012 — left capture through release

VERIFIED bounded:512original entry/gate cases;253callback states match all100ball bytes, slots438b68/74/50, timer43f380, gate43f364,field43f204 and score-service requests. Step51 adds500000score; step153 changescallback2→3; step253 releasesstate2 at34,391 withvx0/vy0x4000. Original415330 dispatcher;415fd7 callback2,417068 transfer,416db8 release. Rule-only4161bb tail and service41b8d0 excluded, but actual416235..4162cc mode/gate branch executes. No DMD-completion injection. Frozen fixture `mean-capture-release-cycle.json`, validator `mean-capture-tick-validation.json`. Originalwrapper4089a4..4089c2 separately establishes held previousXY/zeroVX/VY, no collision/switch; originaldispatcher releases before same-step integration. Initial43f392=0 proven419b0d..419b2e;field43f204 PE/BSS0, separate reset writer not proven.

Release adds7 to hit/normal pointers. `mean-pointer-shift-validation.json`:512original40e1d0 cases establish cache lookup at X+56 for normalpointer+7, supported bitmap interior. Layer2 switch1 middle/right branches41c00c..41c09f now included in768original switch cases; player+8/rule effects excluded. Native four-schedule12000-step regression completes;60000sweep reaches upper capture in3schedules and completes in1, deterministic repeat. Upper callback1 mode lifecycle remains unported: `mean-upper-capture.json`.


## PHY-013 — upper capture, repeat flow and mode5 left award

VERIFIED bounded upper entry41d983..41d9de:512original cases;406840+actualCRT422f40 and416be4/417068:1024cases match all100ball bytes and32bitRNGstate. First352,second552,third252 original callback states match complete native replay in `mean_upper_oracle` (1156total). Runtime execution corrects static misconception:415374 timer<-1 dispatches slot release before415505, so first cycle staysmode2. First timer-2 sets394=-1 and secondaryslot300; second setsmode5 withslot400; subsequentmode5 usesno secondarydelay. Actual40f754 executed, DMD service34 returns bounded nonzero handle; full rendering/rule effects excluded.

Mode5 initial fields confirmed after original second release:1e6=0,05c=10000000,058=0,3b4=0 (`mean-mode5-init.json`).153mode5-left states match ball bytes/slots/timer/award fields:51→500000,52→10000000,153→417068. Native third-award/75000000 reset guard remains unsupported. Original player+8 increments remain separate from score. Callback3 mode-independent gate established415355→4164a4; original253step contact capture fixture still passes.

Layer2 switch1Y<60 ball-local41be36..41be5a reduces eachvelocity by its signed arithmetic quarter;896switch cases include128new cases stopped before external419da4 rule call. Original seed unknown; native seed1 +startup RNG step +one RNG step per simulationtick documented. Frontend pause freezes native simulation. All4synthetic schedules complete120000steps without stops, deterministic repeat identical; no claim of full original trajectory equivalence. Fixtures: `mean-upper-*-original-cycle.json`, `mean-route-extended.json`; CTest6/6.


## PHY-014 — actual mode5 clock and terminal reset

1499original/native cases, zero differences (`mean-mode-island-validation.json`):1009clock cases include signedWORD wrap(-32768→32767),480selection/guard/completion cases,8award terminals,2full reset/release cycles. Original reset/lamp routines execute in oracle; DMD/audio services bounded. Frozen fixture compares score,timer,tablemode,selectedmode,counter,43f366,sum,capturetimer andall100ball bytes. Terminal10M withcounter2 producescounter3/mode2/selection1/sum30M;75M producescounter2/mode2/selection1/sum95M. Both release after253steps.

Clock414e79: originaltimer8400 gives20600000 beforetimer8399;1000gives65000000;999gives75000000. Callback43f334=table+30 dispatched408898 before per-ball4088a9,200Hz. Timeout atnew signedtimer<0 resetsmode2/selection and43f366=-1 without ball mutation. Actual reset selects next unlit completion flag through419da4;The all-lit edge preserves selection (480enumeratedcases). Lamp419f6c and audio4194e4 effects excluded in native.

Correct timing exposes next selectedmode1 upper-rule boundary; `mean_gameplay_bundle` intentionally retained and fails there. Six ofsevenCTest checks pass. Previous120000step all-active regression assumed incomplete ruleclock, not original trajectory equivalence. No remaining full-game success claimed.


## PHY-015 — follow modes and sixth left reward lifecycle

VERIFIED bounded original-x86 vs native:3523clock/reset/left cases,2260upper callback states,18mode-entry sentinel/all-lit states,4465sixth-capture states; zero differences. Fixtures `mean-mode-island-fixture.json`, `mean-upper-selected{1,2}-original-cycle.json`, `mean-mode5-begin-fixture.json`, `mean-sixth-capture-fixture.json` under analysis/traces. Original415976/415ad3 initializes modes1/2 with9400/6400 and preserves05c/3b4;4169e4 selects38c from engine38 via{4,5,4}. Clock414f4e..414fde decrements signedWORD and uses existing timeout reset. Callback2 selected1/2 skips award4162e3, retains transfer/release.

Original416073..4161b1 sixth left capture adds25000000 to initial500000request, resets204, sets secondarydelay740 via actual40f754, increments signed1fe and selects200/202/1fa reward state. Five complete893-step callback2→3→active cycles match100ball bytes and slots/counters/scores. Native8/9CTest; three120000step schedules complete, fourth stops116726 at upper reward415e3f before unproven DMDgate. This is coverage, not full original gameplay equivalence.


## PHY-016 — upper reward entry, finite display and real gate release

VERIFIED bounded:45original415330 reward-entry cases; actual405f98 installsstate4/active2/frame0 for accepted idle requests. Actual4071e8 scheduler invokes410a34/410910/410d34, then413b04/413b60 onlyonce idle.533display states match native: gateclear171/162/200. Scheduler407291 converts3→0 atprecedingtick; tabledisplay404b15 precedesscheduler404b18. Reward3frame75 actualservices405da8/405e48 alter lampstate/cursor only; no ball/score/inputwrites in those routines.

Complete2030original callback/display/release states match100ballbytes, slots,timers,gate,rewardfields,score: reward1cycle1033steps;reward2cycle997. Fixtures `mean-upper-rewards-fixture.json`, `mean-reward{,2,3}-display-original.json`, `mean-upper-reward-cycle-original.json`. NonrewardDMDannouncements/idle rendering bounded separately; rewardstart/scheduler/gatewriter/release actualoriginalexecutes. No injectedcompletion.

Native14/14CTest; allfour120000-step schedules complete,repeatedidentical,reward1request/completion1/1. Largercoverage reaches separate selected3mini-game boundary. Original415b9a..415c85 sets shared44=1 and retains tablemode2;152callback-only states match (`mean-upper-selected3-original.json`), but wholemini-game is unported; native stops on explicitstartrequest. Nativecoverage is not fullautonomousoriginalgameplay equivalence.


## PHY-017 — bounded native car minigame, controls, DMD and return

VERIFIED bounded: selected3 entry415b9a initializes shared44 and480bytes43ec3c; dispatcher4180d0 is table+28 (43f32c), called through40721c at50Hz. Main404a12 skips physics while preserving200Hz RNG/flipper stepping; ordinary419890 table-display slot ticking pauses. Native compiled static intermediate preserves dispatcher/math/progress routines; generated original-derived code remains underbuild.

Original/native2672states agree across four input schedules (691/651/650/680displayticks), including24DWORD fields, all480bufferbytes, active/mode/selection andpoints. Input4186e5..41874e:1024cases, shared54/58 hold=-1/release=0. Actual40af14+406680 decode32two-plane cases/61440pixels exactly. Progress4192d0:288cases including4winning120000000 awards, extra-ballWORD wrap and actual40f754 secondary1100slot installation. Failure/timeout returns also covered. Fonts/announcements/audio and lamp presentation are bounded adapters, not complete original display execution.

Evidence: `analysis/mean-minigame-island.json` and listed fixtures. Native19/19CTest; four200000-step scenarios finish, two complete mini-game and resume captured-ball release. Larger coverage reaches selected4 upper-rule boundary. Full autonomous original trajectory equivalence remains unverified.


## PHY-018 — selected4 initializer, bounded single-ball clock and upper transfer

VERIFIED bounded: actual415330 timer-1→-2 sets376=800,36e=3,37e=1,388=2,24bytes23c..253,mode5,upper secondary400. Actual414e79 executed801times withengine activeballs1 preserves original signedWORD timer and resets through419da4/4194e4/419f6c;802snapshots match native. It setsengine40=5, not0. Presentation adapters bounded.

Actual415330 upper ready-slot branch4153f3..415472 and416b28:128sentinel cases across stages0/1/2/4 matchall100ballbytes,438b50,438b90,37e,3ae and260descriptor. Position13,306/state3/callback5 is distinct from417068 position34,391/callback3. Stage1→2 requests additional-ball spawn4151e4 on next shared table step; native explicitly stops there.

Evidence: `analysis/traces/mean-mode4-fixture.json`, `analysis/traces/mean-mode4-transfer-fixture.json`, `analysis/mean-mode4-consumers.json`. Build21/21CTest. Extended native coverage stops at genuine spawn boundary after206318/232380steps; other two schedules reach240000. Multiball and live-original trajectory equivalence remain unverified.


## PHY-019 — native ball pool, four-ball spawn, pair response and eject flight

VERIFIED bounded:408050/4151e4/41db1c poolallocation/gate,4079dc removal:432sentinel cases match. Capacity8, allocationonlywritesWORD58=-1; stage2spawn transfers416b28 anddecrementsWORD36e; <=0sets37e3. Actual408874 wrapper observer confirms tabletick→step0→pair01/02→step1→pair12→step2. Native input/physics scheduling preserves thisorder andsharedtableclock. Generated bounded408bfc+40964c/40968c compares1024paircases includingheld/ramp states andmask gates.

Actual415330 callback5/416ad8/416e78/416f24:49cases167states agree (35release). Actual417238 railguide:252cases. Full actual4088f0 releaseflight121states matchesnativeall100ballbytes afterrelocatingDATpointers40/44/54. Fixture disablespointforces andusescapturedrestflippers; presentation services bounded. Originalstep72contactnormal965 located inrow608; oldcache had-1 becauseprepareloopended608.812actual40e1d0 calls fill layer1rows608..615; nativeguard nowpermits them. No fittedvelocity/normal or guessedphysics.

Native24/24CTest; four225000-step schedules finish,repeatidentical. Three extras,max4,returncount1/mode2 proven innativecoverage. Extended300000 allfour exercisemultiball; nextactualupperrule boundaryafterfive modes remainsunsupported. Originalremoval occurs404d6f renderprep; native50Hz removal cadence is explicitpolicy, notoriginaltiming claim. Zeroedunusedpool initialization is nativepolicy; exact originalspare startupcontext unverified.

Evidence: `analysis/mean-multiball-island.json`, `analysis/mean-multiball-loop.json`, fixtureandcoverage paths inindex.


PHY-020 — Mean mode6 eight-ball island
Claim: post-five-mode upper capture starts mode6; original announcement gate permits eight-ball launch; upper/side capture clocks release balls and mode6 expires to mode2.
Evidence:415567 entry30cases;415dc7/416821 capture480;414e79→41504f clock192;actual405f98→4071e8→410b00 scheduler270ticks;full415330 cb2/4 side4096cases. Native replay exact at bounded interfaces; transfer/lamp helper calls stubbed in capture fixtures, existing verified transfer integrated withslot74 guard. Four native400000-step schedules finish/max8 andreturn count1. See analysis/mean-mode6-island.json.
Confidence: VERIFIED components; native coverage only for composed trajectories.
Limits: uninterrupted announcement scheduler; original graphics/lamp reset/bonus presentation pending.


PHY-021 — Original lamp and score display
Claim: Mean lamps use MSB-first1-bit DAT masks, indexedpalette highbit updates, four-byte statecommands; score glyph formatter supports12digits andcomma dots.
Evidence: actual408110 clock630cases5040states; actual40a41c/40a654126fullcanvaspatches with parentptr0; actual406280/40646836scorecases69120pixels. Native parser/clock/font replay passes; native screenshot build/mean-lamps-score.png.
Confidence: VERIFIED at fixture boundaries. Original on/off fast path direction corrected through actualpixeltrace, rather than inferred from dynamicobjectbranch40a54b.
Limits: variable original render cadence/dynamic occlusion/full lamp-rule writers remain outside scope.


PHY-022 — Mode rebuild / upper-target reward
Claim:419f6c rebuilds63lamp commands fromexplicitglobals; upper3targets animate lamps30..32 andcompletegroupreward via41d153; table+14 callbackrebuild followsnewball.
Evidence:1024actual419f6c/41a54c randomizedsentinel cases;504actualtop-targetcaller cases;320actualrewardcases through40f754. Registration40efaf/40f005→43f318 and40784d table+14 after407833 table+1c.4077bf provesplayer+12=1 onballadvance. Fixtures listedinanalysis/mean-lamp-rules-island.json. Nativefour400000schedules exercise98hits/14groups.
Confidence: VERIFIED boundedhelpers/events; nativeinputdefaults explicitlypartial.
Limits: missinginputwriters, rewardDMD, fullballreset/bonus/gameover; no fulloriginaltrajectory equivalence.


PHY-023 — Persistent ball reset / bonus / entry / ball-save clock
Claim:419ad8 saves52bytes;419b00 restores persistentrecord andresets per-ball fields withoutchangingtablemode;40735b computeslow32bonus;407794 advancesextra/normalturn;41b210 entersmode2 onlyatlayer3switch1Y90..116.41aaac returnsstateFFFF forsave;4199a6 commoncountdowns at50Hz.
Evidence:analysis/traces/mean-{ball-reset,bonus-turn,turn-entry,turn-clock}-original.json:3040cases exact;mean-turn-boundary-original.json:23caller cases. PEimageSHA8ec7d39b5b56cee1d929536d71446743604fb0ae8fcf260f9be6a3fde81e96d1. Original408943 continuesintegration afterinitializer. Native39/39CTest;mean-turn-gameplay-validation.json;mean-turn-determinism.json.
Confidence: VERIFIED boundedhelpers andcaller ordering; native integrationPARTIAL.
Limits: bonusDMD immediately completed; original43e79c initializergate bypassed bynativepolicy; service1c/suppression usezero; finitegameover/multiplayer/frontend andcompletebonuswriters pending.


PHY-024 — Shared saved-ball launch gate
Claim: original43e79c permitsoneFFFF initializeruntilramp exit; nextnormalturnpreservesgate/FFFF.
Evidence: mean-restart-gate-original.json112actual408915..408943/41b1f8cases;mean-restart-turn-original.json8actual408084→407808cases (count>1 nextturndiagnostic only).42/42CTest; mode6nativequeuedwaits2008stepsandreturn-singleballchecked.
Confidence: VERIFIED boundedbranches; nativeno fulloriginaltrajectoryclaim.

PHY-025 — Full finite game boundary, Demo difference
Claim: Full4083a9 selectedplayer signedWORD+0e >=4 (454aa4zero) or>=6(nonzero) enters408465gameover; Demo407808doesnotcontainthisboundary.
Evidence: mean-game-end-original.json52actualFullcases andrecordedgameoverwrites; buildSHA185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6. Nativefinitegames6047/11275/9398/8076states;100frozenstepsandR-resetverifiedeach;deterministicrepeat. Screenshotbuild/mean-game-over.png.
Confidence: VERIFIED boundedpredicate, nativepolicyadoptsFull454aa4=0.
Limits: Fullqualifyinghighscoreentrybeforethisbranch andbonusDMD skipped;454aa4meaningunknown; no assumedFull/Demophysicsidentity.


PHY-026 — Original bonus presentation and delayed turn
Claim:4072cc clocksbonusphase;419554 stage1 completes65thcallback,stage2immediate. Bonusawardphase0precedesdisplay,407794 turnrunsafterphase5oldtimer>=112. Meanstandardcycle18650Hzcalls,positivebank/mult!=1cycle248calls.
Evidence:mean-bonus-display-original.json1200actualdispatchercases;mean-bonus-pixels-original.json172text/background/animation/clockcases. Original4060f8font91b4andMEAN11cc4e24frames.404a12mode3routekeepsRNG406840/flippers4084bcwhile skipping408874physics.44/44CTest;mean-lifecycle-gameplay-validation.json:fourfinitegames3bonusphases/558tickseach,allball-freeze/onceaward/resetchecks;seed0deterministic. Screenshotbuild/mean-bonus.png.
Confidence: VERIFIED boundeddispatcher/pixels/callback; nativegameplayintegrationpartialbecausebonusbankwriters/player+0c/fastskipinputremainunported.


AUD-001 — Windows Mean banks and native event sequencing
Claim: DAT5c2d2/61590 stripped STIM banks have80/63orders; shared signedPCM reconstructed without synthesis. Service84/88 EAXorder/EDXbank requests4058a0/40587c feed405b94. Selected3 calls415c54/415c67 produce53/1 and23/0.
Evidence: analysis/mean-audio-events.json; analysis/mean-audio-sequencer.json; analysis/traces/mean-audio-bank-validation.json (six cases); analysis/traces/native-mean-banks-validation.json (native/Python byte equality); native_music_pcm/native_audio_queue/mean_music_sequencer/native_mean_banks tests.
Confidence: VERIFIED banks/request/priority and nativePCM continuation; PARTIAL integration. Callback4 416644/416654 native branch unported. Exact originalF00 completion timing UNKNOWN; native stops onF00/firstloop, no equivalent-timing claim.


AUD-002 — Base reset and bonus requests
Claim:419b00→419d88 requests90 order4/bank0;419554 stage0→419576 requests88 order49/bank1.405824 storesbaseorder/bank andclears84pending+requests88stop;405a2e consumesbase.405a80 snapshotsbasebefore84.
Evidence:tools/verify_mean_audio_base.py;analysis/traces/mean-audio-base-original.json(7Unicorncases).mean_music_sequencer testexactPCMbasecontinuation,replacementand88/84nestedpause;mean-audio-bank-validation.jsonorders4/49rendernonzero.
Confidence:VERIFIED boundedrequests/priority;nativebasecontinuousloop andhigherF00/firstloopendpolicy lackoriginaltimingcomparison. ContactSFXUNKNOWN.


AUD-003 — Direct contact/launch sample consumer
Claim:405c60 maintainsdescriptorFIFOandkeepsfirstduplicatearguments.401760→4016dcselectsslots4/5,resolves437cf0/437d14directPCMpointer,length,period,volume. Initializer40f053/40f065 mapsuserDAT63a1d/6535e. Launchandmaterial7sharefirstdescriptor;material3/4sharesecond.
Evidence:tools/verify_mean_sample_consumer.py;analysis/traces/mean-sample-consumer-original.json(duplicatequeue,2actualdescriptorconsumerstates,7allocatorcases);analysis/mean-sample-island.json. NativePCMchunk/duration/reset/twovoice/signedprofilesandSDLqueuecoveredbytests.
Confidence:VERIFIEDboundedqueue/allocator/descriptor/callsite;nativefinalmixerandprioritycompletionpolicyPARTIAL,nooriginalaudioequivalenceclaim.


AUD-004 — Exact bounded mono PCM/resampler
Claim:41eb60 builds128×256 signedLUT;420120 usesfloorQ32 frequency/rate withlow4fractionbitscleared. Fullvolume65536clamped65535 selectsrow127; LUTfactor131072/6.401551/4015af establishsixvoiceWindowsconfig. Mono voiceend42020esetsfrequencyzero.
Evidence:10UnicornPCMcasesandphaseassertions includingbothsampleends;analysis/traces/mean-sample-resampler-original.json. NativefirstchannelPCMhashesequaloriginalmonooutputsforallsizes. Factorymaster65536policyconforms4015ce/41eafc default,notuser-configurableoriginalgainvariants.
Confidence:VERIFIEDboundedmonoPCM/LUT/phase; finalstereo/musicmixanddevicecadencePARTIAL.


RULE-005 — Material5 target/group/contact chain
Claim:41e269..41e7fe choosesfourtargets using80/160/270coordinates,positivecooldowngate,sets5+flag+lampcommand;completion41e724 clearsfourflags,enables43f1daandlamp24. Accepted41e625 consumes43f1da,sets390=250and268command4/3/1/0. y>350 useslamp62/437da4 plusboundedmode/37aawardbranch.
Evidence:analysis/traces/mean-material5-original.json (1344exactoriginal/nativecases);tools/verify_mean_material5.py;analysis/traces/mean-material5-gameplay-validation.json(4×400000steps,374events/25groups). ThirdSFXconsumerand15resamplerhashesmatchoriginal. Existingmean_turn_gameplay_bundle nowassertsmaterial5hits/groupsforallschedules.
Confidence:VERIFIEDboundedrules/state/lamps/sample,PARTIALnativeintegrationbecauseDMD/field054writersremainunported. No originalwholetrajectoryclaim.


DMD-004 — Material5 target/group/award pixel callbacks
Claim:413a2c/413958/41062c driveoriginalDAT144d8e/150e2c/1483ee;service50=40607cpixelinvert;service3c=4066802plane decode;service40=406280score overlay. Completeclockcyclesendafter50/105/155drawticks.
Evidence:analysis/traces/mean-material5-dmd-original.json;tools/verify_mean_material5_display.py (1390cases,actualpixelservices);tests/mean_material5_display_probe.cpp. Actualnativecontactgroup→panelpreviewtools/slamplay --material5-preview,capturebuild/mean-material5-dmd.bmp.56/56CTest.
Confidence:VERIFIEDboundedpixels/callbackcounters;native50Hz/immediatereplacementpolicyPARTIAL;awardcounter45setupservicesandfield054writersnotported.


RULE-006 — Five-target award bank
Claim:41ce03..41d0fa chooses targets atX23/45/160/275;mode<=4 andnegative37a gate flags, fiveflags==1 invoke41d294, clearflags,set6000/60M.414cfa..414d20 gates4150b8 at200Hz mode<4/service1c0. DWORD378 highWORD aliases37a;054=max(10M,(newtimer>>2)*40000). Material5 consumes054 once.
Evidence:tools/verify_mean_award_bank.py;analysis/traces/mean-award-bank-original.json(1550exactcases);tests/mean_award_bank_probe.cpp native composition/expiry;analysis/traces/mean-award-bank-gameplay-validation.json(15nativeactivations,zeroobservedcollections).
Confidence:VERIFIED boundedstate/lamps/timer;PARTIAL gameplayintegration. DMD activation/midpoint/expiry andsecondaryreward omitted; no original wholetrajectory comparison.


DMD-005 — Award-bank activation/midpoint/expiry
Claim:4107c8/41086c use48frameindicescount&7 then100staticframes150a6c/150c4c;410504 uses8frames1474ee each3ticks,5hold,12fade ticks. Original4060a4 sevenlevel fill usesalternating shades withrowparity (checkerboard),notuniform pixels.
Evidence:tools/verify_mean_material5_display.py;analysis/traces/mean-material5-dmd-original.json(1730cases across6callbacks);nativeSDLpreviewbuild/mean-award-bank-dmd.bmp.
Confidence:VERIFIED boundedpixels/counters;native50Hz callbackreplacementPARTIAL,external70/68 setupandsharedDMDschedulerexcluded.


RULE-007 — Side extra-ball collection and display
Claim:41ce2b X<23/field1fc1 and41d084 X>=275/field1fc2 call41d220 beforebankgates.41d220 incrementsplayerWORD10(withwrap),clears1fc,setscommands264[0]=1/2f8[0]=2/2fc[0]=2,requests410e4c. Displayholds0,inverts1,holds2..5,blinks6..105,maskrestore106..121,ends122.
Evidence:analysis/traces/mean-side-extra-original.json(150cases);analysis/traces/mean-side-extra-gameplay-validation.json(2nativecollections);tests/mean_side_extra_probe.cpp bonuslifecyclecomposition;mean-material5-dmd-original.json(1976pixelcases). Service38=406574 uses2planeEAXsource/MSBfirstEDXmask240bytes.40e895returnsallocatedbuffer;423236 allocationzeroesvia422ea0;43efd0initialized40efee.
Confidence:VERIFIEDboundedrules/pixels;nativeintegrationPARTIAL(syntheticsweep,sharedDMDscheduleromitted,indirectrestore-bufferwritersnotruntimeexcluded).


RULE-008 — Switch reward dispatcher and display
Claim:41d3e4 resets35c;358zero scores20M+signed206*10M,206 incrementsif<7. Nonzero358 selects3620..6:bank054,1fa,394,3ba/3bc/392,398/1d4/060,1fe/200/202/1fa,1f2 progress. Rawfields preserveoffsetnames. Common40fdec154drawticks:invert,hold,50blink,100reward/score stage;maskedpages useactual406574.
Evidence:mean-switch-reward-original.json216fullstatecases;mean-material5-dmd-original.json16856pixel/countercases;mean-switch-reward-gameplay-validation.json22nativecashrewards. Entry41de3d X>230,Y<225,ball5c0sets3b6=100;41990350Hzdecrements;41cb1d requires3b6>=0/35a>=0.
Confidence:VERIFIEDboundeddispatcher/pixels;PARTIALintegration. Superseded input blocker: registered41766c contains417842 writer; native input wired and960cases verified. Selector3 mode4 activation remains deferred. Originalwholetrajectory/schedulerexcluded;nativeDMDsnapshotfieldsand50Hzimmediatereplacementpolicy.


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


## MEAN-SHARED-001 — shared rewards and manual-guided native chains

Claim: bounded Demo41b8d0 implements Monster Car/Rally/Offroad/mode6 reward decisions;4169e4 selects Rally targets from438ddc/438df4 and engine+38. Six direct caller IDs0..5 are independently located at416230/41b300/41af27/41c0cb/41cbc4/41c7d0. Native consumers now invoke the helper, including41cbc4's exact position between combo writes and the post-reward mode test.
Evidence: `tools/verify_mean_shared_reward.py`576 complete raw0x3c0 states+scores+mode+callback/control/service args; `tools/verify_mean_rally_target.py`288 complete raw states; fixture `analysis/traces/mean-manual-reward-chains.json`3chains18events; `analysis/traces/mean-shared-native-chains.json`3chains17native steps at actual original bitmap pixels and captured-left timer. Original complete USA manual Mean pages6–11 zero-based anchors behavior names, not memory semantics.
Confidence: VERIFIED bounded rules; native full-trajectory UNKNOWN. DMD scheduler/control and completion service bodies are explicit boundaries; existing separately verified native mode/lamp reset helpers implement needed side effects. Primary proof remains Demo, not entire Retail rule block.

## PIRATE-ENGINE-001 — table data reused by the existing engine

Claim: Pirate supplies different geometry directories to shared engine components already ported for Mean.
Evidence: `tools/validate_pirate_engine.py` runs actual Retail42b390 through42b675 and reset436428 (loader/allocation adapters). Full40f0d0/Demo40e1d0 yield540 identical normals on all three Pirate layers; Full40aa10/native mean_separate506 complete ball states match; Full40aca8/40aab0/native integration/free100steps200complete component states match. Retail SHA185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6; fixture contains DAT SHA and every state.
Confidence: VERIFIED components. Synthetic free start has no collisions; contact response, flipper setup, table callbacks and playable Pirate remain unverified. `analysis/pirate-engine-validation.json`, `analysis/traces/pirate-ball-100.json`.

MEAN-SHARED-001 extension: `analysis/traces/mean-right-common-original.json`72 complete composed states verify combo score→common award→new mode→right progression order. Oracle instruction budgets explicitly assert original return or the declared41d0f5 exit boundary before comparison.


## CORPUS-SECOND-001 — common descriptors and asset families

VERIFIED: tools/audit_table_descriptors.py executes Mean41b9e0, Pirate42b390, Space439ae0, Demon40febc through actual returns using only loader/allocation adapters; records callback stores and geometry. Static shared consumer409823..40983e establishes descriptor+4→engine+0→directory[layer]. Raw motion entry format remainsPARTIAL. tools/audit_table_data_families.py freshlyhashes24 exactbasename DAT files (6MAIN/6MEAN/4PIRATE/4SPACE/4DEMON); onefamily each. EXE equality and Germaninstaller role evidence recorded. Scope is extracted copies, not all possible releases. Evidence: analysis/corpus-table-descriptor-levers.json, analysis/corpus-table-data-families.json.

## CORPUS-SECOND-002 — correction of car minigame scaler scope

VERIFIED: actual Demo418842/Retail425282/Fix425652 fourinstruction snippets produce remainingcounter−2×magnitude (Demo) or−4×magnitude (Retail/Fix),120 synthetic arithmetic-boundary cases. Actual Demo4180d0 selector with3a4=1 reaches418113;3a4=2 reaches418a81. Thus previously named DragRace scaler does not affect that known variant2 branch. Atremaining3/magnitude1 Demo leaves1, Retail/Fix produce−1: concrete earlier exhaustion at this boundary. Upstream projection and fulltrajectory not verified; countermeaning remainsunknown/STRONGresourcehint from4183bc displayconsumer. Evidence analysis/corpus-minigame-scaler.json; reproducible tools/verify_corpus_minigame_scaler.py. Native behavior unchanged.


## TABLE-PROFILE-001 — native profile geometry and renderer

Claim: Native shared profile layerassignment preserves original ballwrites forallfour tables andMean wrapper behavior.
Evidence: `tools/verify_table_profiles.py`56complete100byte states vsactualDemo40f8a0 usingvalidatedRetail directoryrecords. ExistingMeanregression suitePASS. ActualSDL--collision2frames+capture foreachoriginalDAT; screenshotbuild/four-table-profile-overlays.png visuallychecked. ProfileSHAstoredasprovenance; nativevalidator checksbounds, notcryptographicidentity. Specialnewtable callbackcreatedlayersnotclaimed.
Confidence: VERIFIED bounded original layerwrites andnativeviewer; fullnewtable gameplayUNKNOWN.

## PIRATE-WALL-002 — composed response and separation

Claim: Native supportedPirate contact→separation pipeline matches actualRetail40a884 (including40aa10).
Evidence: `analysis/traces/pirate-contact-original.json`1188supported cases+212unsupported no mutation; `analysis/traces/pirate-wall-original.json`506actualgeometry coordinates/materials/normals,494supported completeballmatches+12unsupported no mutation. Originaloracle sets46c670 toverifiedinputnormal (callerboundary), movingoffsets46c604/46c5f8 andgeometryoffsets46c600/46c4a4=0. NoSeparationstub in composedtest. ActualPirate−512clamp documentedin contactisland.
Confidence: VERIFIED bounded; movingflippercontact/wholetrajectoryUNKNOWN.

## TABLE-FLIPPER-001 — input and pose reuse

Claim: Original graphics+0c/+10/+14 records andstartup WORDcopy canreuse existingcompiledflipperinput/pose engine forallfour tables.
Evidence: `tools/verify_table_flippers.py --native build/native/table_flipper_probe` actualRetail405057..405153 startupcopy and409154 inputupdate,960complete78byte states matchnativeconfigure_table_flippers+step_table_flipper_pose. Fixtureanalysis/traces/table-flippers-original.json recordsinitial/100/final+traceSHA. Defaults areoriginalcoldBSS withsyntheticedge schedules. Ballcontactdiagnostic differsatnormalangle/scratch; notincluded inverifiedscope.
Confidence: VERIFIED input→pose; flipperball-contact/responseUNKNOWN pendingcontext/calleeproof.

### RETAIL-FLIPPER-002

Claim: the bounded native Retail contact/response adapter preserves original routine outputs in the tested context.
Evidence: `tools/verify_retail_flipper_contacts.py` executes actual Retail `0x409ce8`/`0x40a380`, SHA `185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6`; 600 synthetic ball states per table, 2,400 total and 965 contacts. Original startup parameter copy, cold BSS plus explicit Demo-derived shared globals and trig/atan/aux inputs. Compare complete 100-byte ball, contact result and `0x46c660` scratch. Fixture: `analysis/traces/retail-flipper-contact-original.json`. Confidence: VERIFIED within this controlled context; no whole-game/live-context or Demo/Retail-equivalence claim.

### MEAN-SHARED-DISPLAY-002

Claim: native Monster Car/Offroad/mode6 reward display sequences preserve actual Demo callback pixels, counters and active/end states in the tested isolated context.
Evidence: `tools/verify_mean_material5_display.py` with `SLAM_SHARED_DISPLAY_ONLY=1`, 12 series / 1,448 frame states, score inputs 0/15M/50M/4294967294. Actual `412fa8`/`41041c`/`410158` plus original bitmap/font/clear/invert services; every 1920-pixel frame compared by FNV hash. Original return asserted. Fixture `analysis/traces/mean-shared-reward-dmd-original.json`. Native switch chain asserts Monster/Offroad callback selection; SDL event preview inspected.
Confidence: VERIFIED isolated pixels/counters and bounded native event integration. Engine+70/+68 lamp and+5c audio adapters are skipped in this pixel proof; original scheduler/preemption and autonomous whole-table equivalence remain unverified.

### MEAN-RALLY-DISPLAY-003

Claim: correct-turn, final-turn and wrong-turn native Rally displays match actual Demo callbacks in their isolated context.
Evidence: `SLAM_RALLY_DISPLAY_ONLY=1 tools/verify_mean_material5_display.py`,14series/2372 frames vs actual411c60/411db4/411824 and bitmap/font/clear/invert/masked pixel services. Counter,active and every1920-pixel FNV hash match; original return asserted. Scores0/15M/50M/4294967294; zero/synthetic restore inputs. Fixture `analysis/traces/mean-rally-dmd-original.json`. Native original-bitmap switch chain asserts wrong turn leaves target unchanged and scores0; six correct events finish at211.5M/mode2 with411db4.
Confidence: VERIFIED isolated pixel/state and bounded native event composition; synthetic ball placements, no whole-table trajectory claim. Original queue, lamp and audio service bodies excluded as before.

### MEAN-MODE4-UPPER-004

Claim: original upper callback1 in internal mode4 can hold, award500000 and request release without advancing ordinary upper modes.
Evidence: actual415330 dispatcher, branch415545/415dc7 and release boundary415473→416be4. New nativeprobe failed with exit2 before guard correction. `tools/verify_mean_mode4_upper.py`:768boundarycontexts +152sequential states (920total), timer/gate/slot/score/actualplayer08bonus/selection preservation/release signals match. Original100ballbytes unchanged before separately-proven release boundary; reward flags200/202/1fa zero. `analysis/traces/mean-mode4-upper-original.json`. Nativephase1initializer +actualfree upperbitmap pixel+explicitavailable-slot state captures, holds152steps and releases; four12000step continuations and repeatseed0 pass (`mean-mode4-upper-gameplay.json`). ConfidenceVERIFIED bounded, naturalentryUNKNOWN.

### MEAN-FINITE-COVERAGE-005

Native-onlycoverage:96finite games/905632steps/fiveinputprofiles; eachGameOver→freeze→reset, consistentbonus and46captures/releases/222saves; five deterministicseed0 repeats. Four further800000step varying-inputruns remainactive, one mode4start, no minigames/multiball. Reproduction `tools/verify_mean_finite_coverage.py` plusmean_sim_probe800000cycleSEEDsummaryrandom. Fixturesmean-finite-input-coverage.json andmean-long-random-gameplay.json. Doesnotestablish originalwholetrajectory orcompleteadvancedmodecoverage.

### MEAN-CAPTURE-FLIGHT-006

`tools/verify_mean_capture_flight.py`: actual406840 RNG/422f40 CRT,415330 mode4 capture,416be4 release, then4088f0 physical path until40898b. Three seeds:456 capture states +3951 full100-byte flight states exact. Fixture `analysis/traces/mean-capture-flight-original.json`. Confidence VERIFIED controlled context only: TLS/score/audio adapters, cached rest flippers, point forces disabled,408b04 switches suppressed; no live whole-table/table drain body proof.

### MEAN-RESTART-REUSE-007

`tools/verify_mean_restart_reuse.py`: actual408915 gate→real41ab94→caller408943,288 retained/shifted100-byte cases. Pre-fix mismatch case9 offsets40/42/43/44/45/46/47/54/56/57 proves missing geometry/render pointer restoration. Native production now calls full initializer and refreshes bit views; preserve unknown retained fields. Fixture `analysis/traces/mean-restart-reuse-original.json`. Confidence VERIFIED bounded gate/initializer, not complete next-ball scheduler.

### MEAN-DRAIN-CHAIN-008

Claim: native bounded lifecycle components compose in the same state order as original across bonus/held/extra-ball and direct-save branches. Evidence: `tools/verify_mean_drain_chain.py`, `tests/mean_drain_chain_probe.cpp`, fixture `analysis/traces/mean-drain-chain-original.json`;24 original expired-save chains +24 direct-save contexts/4100 exact snapshots. Real41aaac/408084/419ad8/4072cc/419554/407794/419b00/41ab94. Bonus low32 score arguments, display globals,100ballbytes,960tablebytes,52savedbytes and player counters compared. Controlled retained drain records, one player; direct-save covers count1/2 with timers0/50/400. Drawing/audio/lamp rebuild and save scheduler service34/40f754 adapted; original callback order retained. Confidence VERIFIED bounded composition only; live timing/full gameplay/Full game-over remain outside scope.

### MEAN-TIMING-BONUS-009

`tools/verify_mean_runtime_cadence.py`: actual4049e0..404b87/4071e8,56 budget0..100ms and gameplay/bonus/overlay contexts; exact call order and5/20ms remainders, service bodies adapted. `verify_mean_bonus_input.py`:1032 byte-write contexts at40423e/4042b1/404347/4043bb; upper734 bytes preserved. SDL existing left/right actions now feed those bit semantics.
Expanded `mean-drain-chain-original.json`:72 contexts/5076 snapshots,24 fast paths; pre-fix accelerated case48 tick3 native028/02c counter2 vs original1 proved extra intro callback. Corrected effective phase before production table+38 dispatch/render. `mean-bonus-skip-gameplay.json`:natural native drain→controlled no/left/both press,185/185/41 remaining50Hz ticks,score1050000 and ball2 equal; ball frozen. Confidence VERIFIED bounded input/dispatch/chain; original catch-up batching, live jitter/transition and whole-table equivalence excluded.

### MEAN-CAMERA-010

Actual4086b8..4087f9 reads ball DWORD10 signedhighWORD renderY; existing407a84 interpolation oracle proves packed renderWORDs10/12. `tools/verify_mean_camera.py`:512boundarycontexts +five600step trajectories=3512 exact center/velocity/scroll/previous-scroll states, including empty/multiball/state6 fallback, signed viewport division and bounds. `analysis/traces/mean-camera-original.json`. Implemented inmean_camera.cpp and SDL main:cached last-render anchorY, currentstate,5ms step. Userlogical viewport400/200 and startupfocus supplied explicitly, original menu/startup omitted. ConfidenceVERIFIED bounded camera function; frontend dynamic cadence scope inherited from native policy. SDLdummy upper-preview capture inspected.

### MEAN-RUNTIME-TRANSITION-011

`tools/verify_mean_runtime_transition.py` executes actual4049e0/4071e8/4072cc/407794/419ad8/419b00,28 terminalbonus/extra-ball framebudget20..100ms contexts. Realfinish/reset callbacks run; simulation services and presentation/table-idle adapted. Exact eventsequence:all RNG/flipper/service/camera ticks first with no physics, thenbonus once, then new-mode table display/idle; stateFFFF survives entire batch. Fixturemean-runtime-transition-original.json. VERIFIED controlled original scheduler; not live clock or native interleaving equivalence.

### MEAN-NATURAL-ADVANCED-012

`tools/verify_mean_natural_modes.py`, `analysis/traces/mean-natural-advanced-gameplay.json`:four native400000step runs, repeated13/27 identical event/fullsummary. Seed13: ball88 upper capture244635/release244987, upper capture246968→selected3 mini247020→completion/selected4 at249704→release250304; no ball increment during minigame. Seed16 likewise enters/completes once. Seed27 firstextra161125 (ball59), seed29 firstextra317265 (ball129), both threeextras/max4→oneball/mode2. All begin ordinary reset, actions onlyLaunch +shared deterministic10..200tick flipper holds; no debug/table/ball injection. Mean DAT/prepared SHA recorded. Confidence VERIFIED native composition, not original/live trajectory or finite3-ball achievement. SDL natural previews400/64step continuation stay active; captures inspected. No demonstrated entry defect in bounded read-only audit; ignored rule_service_request merely open boundary.

### MEAN-UPPER-NOTICE-013

Actual415727..415795:field394→−1,43f27c..27f={4,6,1,0},service34 requests411fdc,40f754 delay300; the existing upper helper already preserves hold/release. Actual411fdc increments engine1c counter, draws11904e then119b8e (each frame4ticks), repeats first4 second frames, holds75ticks, restores through16fdd4e masks, clears engine14 atoldcounter155. Existing original bitmap/mask execution versus native312pixels/counter/active states exact (`analysis/traces/mean-upper-announcement-original.json`). Original service queue,438b20 andfield024 not proved/reimplemented here. Native existing display pipeline consumes first ordinary request and lamp29; actual normal-reset seed13 SDL preview upper succeeds at ball2 (capture inspected). VERIFIED bounded callback/first-request wiring; full queue and selected-mode notices remain outside scope.

### MEAN-UPPER-MODES-014

Original4158b5/415985/415b39/415c9a request callbacks412d24/411f10/412af8/412c58 for selections0/1/2/4. Bodies respectively animate16frames×2,20×4, two20tick ping-pong sequences+18ticks linear,18×2; hold100/75/100/100; mask restore16ticks; clear engine14 nexttick. Framebases10a7ce/11a6ce/11f94e/13380e. `analysis/traces/mean-upper-modes-original.json`:1298 actual original bitmap/mask pixel/counter/active comparisons exact, blank and patterned saved pages. VERIFIED bounded bodies and request mapping; native immediate policy does not establish original shared queue/handle arbitration.

SDL upper-mode entry smoke:ordinary reset, seed13 diagnostic input, budget2000000steps,32tick continuation; inspected original car animation at ball489. Initial400000 budget failed. No injected rule/ball fields; finite3-ball achievement not established.

### MEAN-DISPLAY-ADMISSION-015

405f98..406078: rejects game43e7a0<2 or==3; signedEAX must exceed43e7b0 and active43e788. Success writes43e788=EDX,43e78c=EBX,43e784=ECX,43e790=stack3,43e780=4; returns−1, stack12 setup and4297cc bit2 conditional writes preserved.4071e8..4072a8: active0→state3/callback0/priority−1, end state3→0; next tickidle engine34, no return to interrupted callback.1516 actual/native contexts exact (`analysis/traces/mean-display-scheduler-original.json`), callback/idle/alternate/restart effects explicitly adapted. `analysis/display-request-args.json` proves22caller sites/21callbacks incl413a2c5/2 exception. Seven actual405f98→4071e8→pixel callback overlap chains compare full admission/counter/callback state+1920pixel hash on every operation (`analysis/traces/mean-display-overlap-original.json`). VERIFIED bounded shared admission/retirement and pixel composition; other overlay ownership/global floor/sound/page/score/live-frame effects not claimed equivalent.

### MEAN-REWARD-OWNER-016

`analysis/reward-display-request-args.json`:actual upper rewards service34 EAX8/EDX7;Mode6 EAX10/EDX9. `analysis/traces/mean-reward-mode6-pixels-original.json`:1590 exact actual callback/bitmap/text/invert/mask pixel states. `analysis/traces/mean-reward-owner-original.json`:2945 complete admission/pixel/rawgate states;actual405f98→4071e8→410a34/410910/410d34/410b00 and413b04 gatebranch. Reward364 cleared413b60 after retirement then idle;Mode6 clears382410c0e atcounter267;reward3 writes438afc atcounter75. Enginefield1c explicitly0 for idle gate, post-gate idlegraphics skipped; no sound/lamp consumption equivalence. Synthetic11/10 request demonstrates preemptedMode6 never clears382 automatically; no invented forced release. Production uses this single owner and preserves native presentation reset/bonus/minigame boundaries. VERIFIED bounded pixel/ownership/gates.

### MEAN-DISPLAY-OWNERS-017

Actual415bf7/415c04/415c11/415c1e/415c2b clear engine14,18→−1,20,10 andset44=1;1c retained. Bonus4080bc mode3+4080d4 state6 preserve other scheduler fields. Return407870 setsstate3;40788c movesEDX intoEAX then407894 XOR→0;40789b sets44=0;4078a0 mode1.324 varied actual/native raw contexts (`analysis/traces/mean-display-owner-boundaries-original.json`), external table-save adapted and table-reset before return excluded. Production minigame return imports raw state from existing lift, not resurrected callback. Natural seeds13/16 retainedcounter156, oldcallback0 and44 toggles1→0; `analysis/traces/mean-natural-advanced-gameplay.json`. Confidence VERIFIED bounded first-entry/bonus-return contracts and native first-minigame composition; second native entry follows existing cached initializer contract, not a newly traced original caller.

### MEAN-RETURN-PASS-018

Actual41be5d→419da4 mode-selection guard and45..49lamp writes;41be6c incrementsWORD37c before readingDWORD37a>>16 (exactalias37c).41be7c score=signedupdated37c*5M wrap32-bit;41bea4 writes050;41beb3 requests41163c withregs5/4/2/0,stack45/1/callback;41beca actual40f754 selectorsall1 clears five timer slots if038!=0.41bed8..41befd timer374150+lamp21{4,3,1,0}.419944..4199a6 decrements374; terminalnegative resets37c andlamp21, phase1mode4 override retained.1536 actual/native rawfields/score/announcement comparisons (`analysis/traces/mean-return-pass-original.json`).324 actual41163c pixel/counter/active cases (`analysis/traces/mean-return-pass-dmd-original.json`). Production three targeted realbitmap hits0/5/15M andselected2/3/4 exact repeated native chain; field050/preemption and timers wired, opaque038/024/audio consumption excluded.2finite firsthits/no repeats observed; native/full-original trajectory equivalence not established.

### MEAN-RETURN-CYCLE-019

Actual41be5d..41bf03+419da4 calls actual405f98 thenactual40f754;405f98 returns−1/0,41bebd stores038;40f754 checks038, then024=0 andallfive selectors1 clear438b64/70/7c/88/94. `analysis/traces/mean-return-pass-cycle-original.json`:2053 exact selectedrawfields/total score/five timers/displaystate/1920pixelhash operations. Six sequences include original151tick expiry,150tick repeat acceptance, chainrestart and higher-priority interruption/rejection. Actual41163c andblocking412d24 pixels executed; saved packedpage explicitlysameinboth implementations. External binaryscore andidlegraphics adapted. Native production dispatch nowuses same adapter; raw038 is a resultflag inthisscope, not an opaque pointer. VERIFIED bounded full rule/dispatch/expiry/pixel composition, not complete original flight.

### MEAN-PLAYER-DEFAULTS-020

Mean40efcb EBP419e68;40f00b→43f324,tablebase43f304+20. Shared407e48 NewGame→407f21 calls table+20,407f31 calls+1c(reset419b00). Actual419e68 writes8×52byte records(first43ee24),words04/12hex=4,22hex1f40=8000, explicitunwrittenholes11/17/1dhex.256record oracle comparisons exact. FullUSA4268a8 andUK/ROM426c78 same49instruction/35write pattern moduloaddresses (readonlytargetedcomparison).419b00 importsrecord34decimal into43f1f6. Actual418d34 comparesunsignedWORD1f6;win418e00..418e49 awards30M+signedprior1f8*15M, decrements1f6by400 andincrements1f8. Expandedexistingactual4180d0 oracle15cycles/15168states including8000 target, old0/20000remainexplicitsyntheticboundaries. Production seededactualrightbitmap/flipperedge tests win/fail andnextball/newgame persistence. Native originalinitializednatural8-ball Mode6 chain also verified; no capturedwhole-originalflight or Amiga equivalence claim.

### MEAN-MINI2-FEEDBACK-021

Actual41910e..41916f clearscanvas,draws caption4293a4,readsWORD1f6,smallnumeric+44 x10/y10/align1/mask3, then'S'atreturnedwidth+12. Actual40617c/40638c/406468 widths/alignment/glyph masks/groupdots;BCDzero returns2glyphs,UINT32zero1.93actualpixels/width comparisons (`analysis/traces/mean-minigame-text-original.json`), native alsoexecutes lift externalservice ABIbridge. Actual418d93 requests41210c8/7 stack8/1;418e92 requests4122cc8/7 stack44/1. Callback41210c239states/4122cc214states ×raw43efcc0/8000/65535 ×score30M/45M ×savedpageblank/pattern =5436exactpixels/counter/active cases (`analysis/traces/mean-minigame2-terminal-pixels-original.json`). Native success/failure completion nowassertsselectedcallback; SDL actualgoalfontcall andterminal previewsinspected. Scene405f0c/audio/catch-up/livewholeframe remains excluded.

## MEAN-MINI-AUDIO-022
Claim: Both minigames' original countdown/start samples can use the native sample mixer without a new decoder.
Evidence:418406/418423/418440/4184b1 and418f15/418f74/418f91/418fae call service5c with EDX255/EBX245.4175a8 starts the same438050 sample on an early flipper press.4017a8..4017be resolves sample18 slices through DAT's big-endian sample table;401760 exact four voice records and PCM hashes in`analysis/traces/mean-sample-consumer-original.json`. Four original/native tick-aligned request sequences in`analysis/traces/mean-minigame-samples-original.json`;55 mono LUT/resampler hashes in`analysis/traces/mean-sample-resampler-original.json`. Native completion fixture verifies no duplicated early-start request.
Confidence: VERIFIED for requests/asset slices/mono resampling. Native stereo sum and SDL buffering remain port policy.

## MEAN-MINI-COMPOSED-023
Claim: Both minigames' composed native DMD presentation matches original code within bounded initial contexts; remaining internal music requests can reuse existing sequencer.
Evidence: `tools/verify_mean_minigame_pixels.py` executes actual4180d0 plus406680/406574/40f91c/4060f8/40617c/406280/4060a4;3461 tick-frame hashes match native lift/presentation bridge (`analysis/traces/mean-minigame-pixels-original.json`). Original405f0c disassembly405f0c..405f95 is32pixel strip expansion, not scaler; no matching generated consumer.40587c/4058a0 store EAXorder andEDXbank;4058c8 stops84. Eight original/native audio request traces (`analysis/traces/mean-minigame-samples-original.json`) cover both variants andterminal signed37a branches. Native completed second-minigame test requires single signed37a-selected84 bank0/order62 or80stop request oncompletion.
Confidence: VERIFIED bounded DMD pixels andaudio request sequence; original rendering register-clobbers differ in adapter but consumers reload registers. External gameplay effects remain adapted; SDL buffering/stereo sum remains native policy.

## MEAN-MINI1-TERMINAL-024
Claim: First-minigame terminalpresentation can reuse native sharedDMDowner; originalClear must preserve brightnesspatterns.
Evidence: Original41929d→40f994 request8/7/2/0 stack37hex/1;419483→40fb78 samewith36hex/1.415bce/415c4e initializes43efdc1,4193c0increments; terminalread40fa9e/40fccb.40f994 stages5+12+50+100→retireoldcounter167;40fb78 stages46+75+75+1+3+100→retire300, originalframe13f92e/15018e/1585c4.2814pixel/counter/active states acrossraw1/2/3/5/7/20 (`analysis/traces/mean-minigame1-terminal-pixels-original.json`). Original4060a4 reads429a9c7pairs, signedclampslevel, alternatespixels/rows;10newbrightnessboundarycontexts in103font/clearcases (`analysis/traces/mean-minigame-text-original.json`). Four nativeinputprofilesdebugcapture→abort→167tickresult→sharedownerretirement matchactualpixel fixture; SDLNO SCORE rendered/inspected.
Confidence: VERIFIED bounded callbacks/fades/admissionmetadata; success120Mbranch alreadyboundedoriginal4192d0 fixture, but naturalinputsuccess not established. No newphysics or duplicated scoring.

## MEAN-MINI1-WIN-025
Claim: First-minigame sixlap120Mcompletion isreachable withrealsteering inputs, using existingnativephysics/trackdata.
Evidence:418722..41878a readsDAT1565c4 collisionbits;418541..41859c integratesrawpositions;4186e5..418748 processesShared54/58 inputs;4192d0 validatesforwardsectionprogress,4193b9..4193c9 incrementsraw43efdc,41940d awards120M atbaseline1+6laps. `analysis/traces/mean-minigame1-winning-input.json` containsonlydiagnostickeysequence+observedstates; actualOriginal4180d0 replay agreeswithnative24DWORDfields/packedframehash andterminalstate for4520ticks (`mean-minigame1-winning-original.json`). Native production test compares301resulttickpixels,once-onlyaward beforeballrelease,ownerretirement; two diagnosticcaptures andtwo unforcedendlessseed27 runs identical (`mean-minigame1-winning-gameplay.json`). Normalgameplay continues afterballrelease(+25k); notduplicatedminigameaward. SDL screenshot6LAPS/120000000 inspected.
Confidence: VERIFIED Demo boundedwinningisland andnativeunforcedlifecycle; nooriginalwhole-tabletrajectory/finite3-ball/Retailphysicsequivalence claim.141/141CTestsPASS.

## MEAN-MINI-RETAIL-026
Claim: Retail/Fix first-minigame semantics needonecoherentnativeprofile, notonlydoublecollisionabzug.
Evidence: pairedoriginalinstructions4180d0..4194e4 plus40e960/40f754/419da4/DMD40f994/40fb78 andinitializer415bce..415d00: onlyfiveconstantsdiffer (3gameplay+2DMD), initializerunchanged. CodeCore offsetsRetail+ca40/Fix+ce10; MeanGlobals+2eb10/+2fb10; services+9a0/+c00; descriptor/random/timer mappings explicit in`analysis/traces/mean-minigame-retail-original.json`. ActualrawEXE SHA185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6 and5054441d4966efc4cdf14edef6061bad9c8af70ea56ec7f772d69cdc16612667 executedwithoutcodepatches:2455tick3lap120Mwin/1189tick1lap40Mabort matchnativefullrawstate/packedframehash. InitialcontexttranslatedfromcachedDemo capture; bothusebyteidenticalDemo/RetailMEAN.DAT andexistingLUT; sharedpresentation/audio/score/lamp servicesbounded.
Productiontwoforceddiagnosticcaptures +twounforcedseed27runs peroutcome in`mean-minigame-retail-gameplay.json`/`mean-minigame-retail-abort-gameplay.json`, exactrepeat andball/ownerrelease.1407normalizedDMDpixelcases in`mean-minigame-retail-terminal-pixels.json` useDemo fontservices+twoverifiedRetailimmediates. SDL3LAPS/120M inspected.146/146CTestsPASS.
Confidence: VERIFIED boundedRetail/Fix minigame/profile/initializerconstants; notOriginalRetailstartup/whole-table/wholeframe/fontengineequivalence.

## MEAN-RULE-REUSE-027
Claim: Existing native Mean rule/capture consumers can reuse these bounded Demo code bodies for Retail/Fix.
Evidence: 14 ranges, including 415330..4180d0 capture/input/modes, 419e68..41ac30 initialization/lamp/callback/turn, and bounded reward/capture/progress/award/material5 ranges: 5860 instructions per target match boundaries, opcodes, operand widths, registers and non-address constants. PE HIGHLOW entries distinguish pointers from numeric immediates; local branches match code relocation and external references form a consistent address map. Tables438bdc (128 DWORD),438ddc (6),438df4 (19) are byte-identical. SHA-guarded original builds, ranges, normalized hashes and address mappings: `analysis/mean-rule-reuse.json`. SDL default launcher screenshot `build/mean-launcher-retail-win.png` shows3LAPS/120000000; both explicit profiles pass targeted tests.
Confidence: VERIFIED bounded structural equivalence and three table contents; indirect pointer initialization, external service behavior and whole-table runtime equivalence remain outside scope.

Final verification:148/148 CTests PASS (`build/mean-rule-reuse-ctest.log`,117.31s); build warning-free, Python syntax PASS. Default Retail screenshot inspected (3LAPS/120M); historical Demo preview remains6LAPS.

## MEAN-FINITE-MINIGAMES-028
Claim: Both native Mean minigame terminal paths compose with the finite three-ball lifecycle.
Evidence: `tests/mean_minigame_finite.cpp`, CTest149PASS; `analysis/traces/mean-minigame-finite.json` contains6outcomes×2identicalruns. Firstcallbacks40fb78/40f994 andsecond4122cc/41210c are present atcompletion, subsequentlyretire; capturedball isreleased; eachgamehas3bonusstarts/completions/awards; remainingball state staysfixed duringbonus; GameOver emptiesballpool/tablemode, freezesball/score40steps; resetrestores ball1/count1/mode1/score0/minigamecounter0. Continuation6996..11000steps. Setup is explicitly original selected3 diagnostic capture or synthetic rightcapture; subsequentsteeringandplay uses productionnative state. No new gameplaysemantics.
Confidence: VERIFIED native composition/repeatability, not original whole-table trajectory or natural finite capture entry.128random finite seeds foundzero entries (`mean-finite-entry-search.json`); stop broadscan anduse targetedshots.

## MEAN-NATURAL-FINITE-MINI2-029
Claim: Second minigame isreachable in a normalfinite native game viarealkeyactions, andcomposes throughwinningresult/gameend.
Evidence:24coarse ballY/policy timings+16refinedpulsephase timings (`analysis/traces/mean-targeted-shot-search.json`); scheduleY>=470,16-stepalternationphase4 entersat12185steps,phase12at13904. Sharednativekeyhelper onlyreadsY/step andreturnsleft/right booleans; reset→continuousfiniteplay→launchheld, no debugstatecalls in naturaltestbranch. Ball1entryscore5906830; alternating5-stepaccelerations→4122cc/30Mafterentry,release,3bonuses,final117640980,ballnumber4/pool0/mode0/GameOver; repeatidentical and40frozensteps/newgamereset in`mean-minigame-finite.json`. SDLnaturalpreviewBEAT8000/ball1inspected. Originalbounded minigame/terminalphysics fixtures remainpriorproof, notanoriginalwhole-tableentrytrace.
Confidence: VERIFIED nativeunforcedfiniteentry/composition; originalwhole-tabletrajectory equivalence remainsunverified. First-minigame finite naturalentry remainsunproven.

Final verification:150/150 CTests PASS (`build/mean-route-island-ctest.log`,128.72s); warning-freebuild;14finiteintegrationcases includingtwo naturalball1entries. SDLnaturalfinitepreview screenshotinspected.

## MEAN-NATURAL-MINI-ORACLE-030
Claim: Originalsecond-minigame control/math/input/reset agrees with productionnative at a naturallyreachedfiniteentry.
Evidence: Probe followsnormalreset/finitepolicy/diagnostickeys toball1step12185,score5906830; noforcedball/rulecontext. Nativeentrysnapshot exportedunderbuild thenloadedintoUnicorn. Actual417374/41766c registeredinputcallbacks atobservedrisingedges; actual4180d0 atnative20msboundaries;530ticks/2119inputsubstepscompare24DWORDstateplus960rawbytes,engineflags,packed480byteFNV,points/callback. Actual416fe0 runsunhooked andobservedmode2/field3a2=0; native30M/4122cc matches. Twoordered5c/musicterminaleventscompareparameters; initialentrymusic isoutsideprobe'sscope. `analysis/traces/mean-natural-minigame-original.json` contains hashes/resetobservations/audioevents andexplicitlimits.
Confidence: VERIFIED boundedoriginalexecutionfromnative-derivedentry, notoriginalwhole-table/startup/liveentrytrace; presentation/font/render/audio-device services adapted. Existingfiniteproductionresult/release/GameOver checksprovideindependentnativecomposition.

Verification:7/7 relevantoriginal/native/integration/SDLtestsPASS (`build/mean-natural-oracle-regression.log`,20.75s); warning-freebuild, Python syntaxPASS. Prior150/150fullsuite islastfullrun; no151/151fullsuiteclaim.

## MEAN-NUDGE-TILT-031
Claim: Nudge waveform, pendingacceptance andcommonTiltengineeffects form reusable nativecomponents.
Evidence: actual40671c..406804 and404b48..404b82 (EDX0) compared900cases incl600boundary/random+300sequentialcadencecases;17DWORDLUTs429814/429860 extractedfromuserPEcache, exacthashes in`analysis/traces/mean-nudge-original.json`. Input40407c uses42980c(horizontal−1/+1) and429858(upward−1),defaults40d2e2LeftAlt38/RightAltb8 fromControl.txt. Actual40554c..405609 compared528commonstate/callbackcases: mode−1..6,existingTilt0/1,counterboundaries/overflow,count0/1/8,full8rawglobals andballstatusbytes. `analysis/traces/mean-nudge-tilt-original.json`; callback+4 isrecordedadapter, tableconsequencesunproven. Nativephysicalcoupling remainsdisabled:40981b/409829 alreadyreadforces,40e1d9/40e1df queryoffsets, so wiringneedsbothquery/normal/separation andflipperpaths plusTiltlifecycle.
Confidence: VERIFIED boundedcommondriver/tiltlogic; PARTIAL gameplayintegration. No inventedphysics, nooriginalassetsadded. REAproviderunavailable, noREAdecompilation claim.

## MEAN-TILT-TABLE-032
Claim: MeanTilt tablecallback, warningDMD andmusicrequests areimplementable independently ofcaptureTilt dispatch.
Evidence: originalcallbackpointerbinding40f0af/40f10c installs417ae0 at43f308; runtime/staticpointergraph43e740→438ae4→4388d4→43f304.108actual417ae0contexts comparefields/services (`mean-nudge-table-original.json`); serviceboundariesrecorded,40f754notrunthere. Actual40f93c originalbitmap14ecee toggleson counterbit1,clearotherwise; retiresatoldcounter50 withcounter51.51actualoriginalpixel/counter/active cases (`mean-nudge-warning-pixels-original.json`), SDLWARNINGscreenshotinspected. NativeAudio8c stopsforeground88 usingexistingsequencer; Tilt84 bank1/order52 queuesactualuserDATPCM; no physicalaudibilityclaim.
20actual415330callbacks1..5,state3/6,service1c0/1 observations provecontinuationafterTiltrelease (`mean-tilt-capture-observation.json`). They identify416d08 andbranchordering, do notprovewhole-nativeTiltcomposition. Playerkeysstayunbounduntilcaptured-balls/bonus/reset/physicscouplingverified.
Confidence: VERIFIED boundedtablecallback/warning/audioadapter; PARTIAL completeNudge/Tilt gameplay. Noinventedforces/earlyreturns.

Finalverification:157/157CTestsPASS (`build/mean-tilt-table-ctest.log`,96.10s),warning-freebuild/PythonsyntaxPASS. SDLWARNINGscreenshotinspected;TiltmusicPCMqueuedonDummydevice. Capturerelease-before-continuation observationsrerunvia`tools/observe_mean_tilt_capture.py`,seed/stubboundariesretained.

## MEAN-TILT-CAPTURE-033
Claim: Five captured-ballTiltentrypaths can preserve originalrelease-before-continuation order natively within tested domains.
Evidence:288cb2/3actual415330cases (new416d08full100bytehelper, timer/slotcontinuation;cb3doublerelease/sample);384cb4actual4164e1cases (pretransferthencontinuedtimer/points, changedcallbackretainedwhenretransferblocked);70cb5actual415330cases/135states (unconditional416f24,slotcontinuation,doubleaudio,mode2/5/6);216cb1actual415330contexts (human1..3, early416be4followedbysaved-entrytimer/gate/awardlogic). Fourmachine-readableoriginalfixtures recordscopes/hashes/casecounts. Samples437dec priority6/slot5 match;417068 itself emitsnosample (originalcodeverified; erroneousinitialsampleassumptioncorrected).
Native`--tilt-release-preview` executesverifiedcb2fixtureandthenproductionphysics32steps, screenshotinspected. Thisisdiagnosticballsetup+localTiltsignal, notpersistentfull-gameTilt. Originalcommoncounter/tablecallbacks/bonus-suppression routines remainseparateverifiedcomponents; shareddispatcher/mode5left/mode6side composition andNudgephysicsqueryoffsets remainunconnected. DefaultAPIs preserved; noearly-returnapproximation.
Confidence: VERIFIED boundedoriginal/nativecaptures; PARTIAL completeNudge/Tiltgameplayintegration.

Finalverification:162/162CTestsPASS (`build/mean-capture-tilt-ctest.log`,195.90s), warning-freebuild. Python syntaxPASS;cb2/3sampleargstrengtheningfinal158PASS;legacyselected3152stepregressionPASS. SDLdiagnosticrelease screenshotinspected. No full keyboardNudge/Tiltcompositionclaim.

## MEAN-TILT-LIFECYCLE-034
Claim: A sharednativeTilt signal composes with humanmode2captures andfinitebonus/turnlifecycle.
Evidence: servicebase43d848 at405396 passedtoMean40efa0;40efb9storesitinto43f0d0,so+1c=43d864 exactly. Original40734b/4073ad suppressbonusaward/accumulation;40560c..405705 doesnotgateScorebyTilt. Original40786a clearsflagafter419b00/419f6c turncallbacks;407f91 newgameclears. Nativefield_43d864_ follows these boundaries, helper APIs preserveverifiedearlyrelease/continuation, capture-entry/ball-save/pointforce guards consumeit. `mean_tilt_gameplay` testsfive diagnosticcaptures×repeat withsynthetic10Mbank: nofirstbonusaward, music8c/84once,437dec6/5samplecount (cb4firsttransfernone),ballstationaryinbonus,clearfirstnextball,finiteGameOver/newgamerestore. Output`mean-tilt-gameplay.json`; nativewhole-tablecontextnotanoriginalcapturetrace. Existing958originalcomponentcasesremainboundedproof; mode5/6specialdispatchandallscore-boundarycasesnotclaimed.
Confidence: VERIFIED nativehumanmode2composition/staticsharedaliasandbonus/resetboundaries; PARTIAL fullNudge/Tilt/input integration.

Finalverification:163/163CTestsPASS (`build/mean-tilt-dispatch-ctest.log`,211.54s),warning-freebuild. TenpersistentTiltfinitechainswithnonzero10Mbank,sample/musicorder,bonusfreeze,nextballclear/newgamerestore;SDLpreviewPASS. Nudgekeysandfullspecializedmode5/6Tiltremainunclaimed.

## MEAN-NUDGE-INTEGRATION-035
Claim: Native Mean now connects the verified original nudge wave to collision occupancy/material masks, normal queries, wall response, separation and lifted flippers; switch queries remain unshifted.
Evidence: `analysis/traces/mean-nudge-wiring-original.json` stores original bytes/instructions for seven bounded ranges:408e70/409090/40e1d0 query offsets,408b04 unshifted switches,404a3e/404a6d waveform cadence and404b1f outer gate. Existing900driver/528Tiltcountercases remain component oracles. MeanSimulation loads original LUTs from user PE cache, advances40671c-equivalent after physics (also bonus/minigame), then decays counter and accepts pending inputs every20ms in normal gameplay. LeftAlt=-1,RightAlt=+1,Space=up; key-down edges only, P pauses, Space resumes paused diagnostics. Live input invokes original warning/Tilt paths.
Limits: native fixed200/50Hz cadence, not complete original outer UI-mode reconstruction; no original full-table trajectory equivalence, specialized mode5/6Tilt composition remains partial. Nudged collision coordinates outside existing320x616 cache stop explicitly rather than clamp or invent geometry. Table shake presentation not yet wired.

Verification:163/163 existing CTestsPASS (`build/mean-nudge-live-ctest.log`,215.32s), plus new100-step nudge integration testPASS. All three directions change ball state at launcher warmup48 with deterministic repeats; three rapid inputs Tilt/resetPASS. Build warning-free. Next: specialized mode5/6Tilt capture continuations.

## MEAN-SPECIAL-TILT-036
Claim: Native special capture dispatch now preserves Tilt release-before-continuation for left mode4/5 and side mode6; released mode6 balls resume integration instead of being unconditionally held.
Evidence: actual416d08/417068 through415330:1152mode1..4 activation/transfer cases (`mean-mode4-capture-tilt-original.json`),72mode5left selection0/nonterminal10M cases (`mean-mode5-left-tilt-original.json`),1280mode6side cases (`mean-tilt-mode6-side-original.json`). Mode6 tests execute all417068 helpers including current-ball callback3 self-blocking, full100ballbytes/slots/timers/gates/score/bonus/samples match. UpperTilt adds positive-timer modes4..6 (288totalcases including existinghuman1..3), `mean-tilt-upper-capture-original.json`. Simulation syncs mode6right timer/slots/counters and callback3 occupancy, queues original437dec6/5 samples, only holds state3/6 after side dispatch.
Native integration:7synthetic mode/callback pairs (4/5/6 upper,4/5/6left,6right), each repeated:100steps then5660..9160continuationsteps→suppressed10Mtestbank bonus→nextballTiltclear→finiteGameOver. `analysis/traces/mean-special-tilt-gameplay.json`.
Limits: mode5positive capture-delay at awardtimer>=-2 notcovered (original40f754 presentation sideeffect clearsdelay); terminal/select1..4Tilt combinations notclaimed; uppermode4..6timer/transfer/rewardboundary combinations notfullyexpanded. Originallamp416fe0/score/audio service boundaries stubbed/recorded, no entireoriginaltrajectory claim.
Confidence: VERIFIED bounded original/native capture paths and deterministic native finite chains; PARTIAL complete special-mode Tilt rule/presentation combinations.

Finalverification:168/168CTestsPASS (`build/mean-special-tilt-ctest.log`,220.04s); warning-freebuild. Final strengthened seven-pair finite integrationPASS (`build/mean-special-tilt-finite.log`), Originaloracle length checksPASS; Python syntax/map/fixture validationPASS.

## MEAN-CAPTURE-DELAY-AWARD-037
Claim: Original40f754 admission/selector semantics and callback2 mode5 award412908 now compose with native capture/score/DMD.
Evidence:384actual40f754 contexts in `mean-capture-delay-original.json`: nonzero43f038 clears43f024; selectors(stackarg1,ECX,EBX,EDX,entryEAX) choose0 vs stackarg2 for five secondary delays. Rejection preserves all. Header `mean_capture_delay.h` verified against these records.416306..41634e requests412908(EAX7,EDX6,ECX2,EBX0;stack3,1), then40f754(allselectors1,delay0). Native routes award request before mode5 continuation, applies helper to all five delays, queues existing animation effect. Standalone mode5left accepts admission result;224Original/native cases include positive delays and accepted/rejected service34, Tilt/nonTilt, timer/slot boundaries; previous exclusion removed. New412908 assets/display callback:1304Originalpixel/counter/active comparisons, preserved163tick lifecycle/score blink/masked restore, counter16 original438afc effect.
Native integration:4synthetic award entries(Tilt×admission), field39c1000→65M per originalclock, step1 allfive delay gate/score/callback assertions plus680runningsteps. `mean-mode5-award-gameplay.json`.
Correction to MEAN-SPECIAL-TILT-036: old debug_tilt_capture loaded stale rawtablemode2, so its earlier seven finite chains did not establish special modes. Diagnostic now sets raw.table_mode before load, test asserts entry mode, and seven mode4/5/6pairs rerun through real selected-mode dispatch→bonus/nextball/GameOver. Regenerated `mean-special-tilt-gameplay.json`; direct originalcaptureoracles were unaffected.
Limits: terminal/otherselection award combinations and all40f754 callers not claimed. Fixed native cadence/synthetic entries, no entireoriginaltrajectory equivalence.
Confidence: VERIFIED bounded helper/award pixels/admission integration and corrected finite special-mode native chains; PARTIAL completeMeanrules.

Finalverification:171/171 fullregressionPASS (`build/mean-award-delay-ctest.log`,100.88s) + newSDLvisibleTest172PASS (`build/mean-award-delay-visible.log`). Warning-freebuild. Screenshot `build/mean-mode5-award.png` inspected: original65Maward on originalplayfield; preview `tools/slamplay --mode5-award-preview` uses synthetic diagnosticentry. Syntax/mapPASS.

MEAN-COMPLETION-038

Claim: native frontend and collision/Mode Lock island implemented with bounded original verification.
Evidence: mean-normal-original.json6920 original/native cases; mean-bitmap-linear-original.json180 edge/layer cases; mean-mode-lock-original.json448 input contexts; mean-mode-lock-pixels-original.json540 pixels/counter states; mean-upper-delay-original.json768 actual415330/40f754 contexts; mean-mode4-exit-input-pixels-original.json152 states (4114cc alternates empty/14f82e for75ticks); mean-dmd-palette-original.json1920 mapped indices plus4 RGB levels. Settings/layout/audio/highscore tests and dummy SDL captures cover new frontend.
Implementation: native Mode4 dispatcher requests display before committing input, passes actual admission to4175d4/417870 consumer and40f754, preserves existing/new display across mode exit. Direct40e1d0 replaces finite normal caches; original408e70 addressing replaces coordinate clamps.
Limits: bounded original component equivalence; full original trajectories, all handbook chains and physical laptop fullscreen/drag acceptance not established. Highscores are native-only; original files untouched.
Confidence: VERIFIED bounded oracles; PARTIAL complete Mean.

Final verification: warning-free build;186/186 CTest PASS in101.64s (`build/mean-options-normal-final-ctest.log`), including100 finite games, original normal/bitmap/Mode Lock/upper admission and4114cc pixel oracles. Options screenshot inspected. Hardware laptop acceptance remains pending.

MEAN-FORMULA1-FINITE-039
Claim: native Formula1 first-minigame has a naturally reached finite entry, win/abort and complete return lifecycle.
Evidence: test mean_minigame_finite now18cases. Win/abort each start fromreset,19717 SDL-equivalent gameplay steps lead to upper selected3 capture onball3.264run key RLE including one Return release/press is replayed independently from written fixture; repeated results identical. Win120M,final137848070; abort40M,final53820750. Five total releases,3bonuscompletions,finalGameOver and frozen40steps,reset ball1/score0. Pixel hashes match existing actual Original40fb78/40f994 references in1200/668 post-result observations. Build SHA31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00, Retail minigame profile.
Artifacts: analysis/traces/mean-first-minigame-natural-finite-win.json; mean-first-minigame-natural-finite-abort.json; mean-minigame-finite.json; analysis/mean-first-minigame-entry-levers.json.
Limits: native finite trajectory, not captured original whole-table trajectory. Formula1 handbook identification STRONG; full extra-ball prize collection remains unproved. No production physics/rules changed for the route.
Confidence: VERIFIED native finite chain and bounded original result pixels; STRONG named handbook identification.
Verification:5/5 targeted original/ModeLock/finite tests PASS (35.31s); final key-release/replay18case test PASS (21.36s). Warning-free affected build. Prior186/186 regression precedes this diagnostic-only extension.

MEAN-FORMULA1-EXTRABALL-040
Claim: natural finite Formula1 win can yield and actually play its extra ball.
Original: WIN4194c5..4194d5 increments43f1fa. Actual Retail/Fix oracles report initial0/final1 win,0/final0 abort. Existing upper45case fixture includes pending1→0/playercredit+10=1 (goal rewards200/202 take priority). Bonus407794 original1024contexts includes ball3/credit1→ball3/credit0.
Native: recorded finite entry19717steps; win29536steps, pending1/credit0. Shotphase10 collects at32615steps, callback410d34, pending0/credit1; extra-ball replay40544steps retainsball3/credit0; four bonus completions thenGameOver/newgame. Phase2 independently repeats collection65273/replay68596. Both exact repeats pass; phase0 keeps uncollectedprize and ends afterthree bonuses. No placement/endless mode. Test asserts original reward callback/captured-ball fields, frozenGameOver and clean reset.
Artifacts: analysis/mean-formula1-extra-ball-proof.json; analysis/traces/mean-formula1-extra-ball-gameplay.json; tools/verify_mean_formula1_extra_ball.py; tests/mean_formula1_extra_ball.cpp.
Implementation: observational pending_extra_ball_prizes/extra_ball_credits getters; original adapter unchanged. New CTest187 covers complete causal chain.
Verification:6/6 affected testsPASS45.53s; warning-freefull build; Python syntaxPASS. Original whole-table trajectory not claimed.
Confidence: VERIFIED bounded original transitions and finite native chain.

MEAN-SHORT-MODES-041
Claim: StockCar andPitStop original islands are now natively wired with correct perrequest admission, timing and originalDMD; Overheat existing island has combined named proof.
Evidence: Stock actual41e00c material3/4 plus actual419da4/40f754,480states byteexact; Pit actual41b61c +419890timers186states inclmixedDMDadmissions; Stock849/Pit867actualpixel/counterstates. ActualRetail/Fix17range normalized instruction equivalence6248instructions/153dataDWORDs. Sources/paths/limits consolidated in analysis/mean-short-modes.json.
Integration: Native Pit4mainmodes/duplicate/Tilt65Mtotal chain, Stock15+15/30hits150M/Returnlock. Existing actualbitmap shared-ramp tests now include Pit firstpuncture2.5M while all Monster/Rally/Offroad score/target/DMD assertions retained. CorrectOriginalbumperselection preserves tablemode366 unlike terminalmean_mode_reset.
Verification: full195/195 CTestsPASS110.61s;100finitegames; warning-freefullbuild. OriginalDMD stock14CARSLEFT andPit25MJACKPOT screenshots inspected. Newpreviewstates explicitlydiagnostic.
Limits: originalwhole-tabletrajectory equality, naturallyreachedfullStock/Pitfinitechains andnewcallbackspecificaudio not claimed.
Confidence: VERIFIED bounded original states/pixels/crossbuild and nativecomposition; PARTIAL completeMean.

MEAN-SPEED-042
Claim: native SPEED gate/capture/expiry/Jackpot presentation-admission chain now contains bounded originalmissing adapters.
Evidence: actual416fe0 mode6 branch417bb8..417c8c: command43f250[4,6,1,0]; permitrightlock only36c<0 andlocks-count<-1, thencommandfirstbyte2/3b8FFFF/gateb34=1; otherwiseclosed. Actual41da51 entry hasno mode<=4 guard and directlycloses gate41dad9..41dae6. Nativepreviousguard causedunsupportedcallback at5356steps/seed1; corrected400000stepfour-input probe passes.
Original41bcd5..41bce9 SPEED service34 then40f754(allselectors1,delay0) now receives actualnativeadmission.312originalgate/rewardstates includezero/negative/2000timers,1..8activeballs,all lock combinations andID0/ID2exclusions. Native8admission contexts verifyaward, owner, five delays andfield024.888Originalpixel/counterstates cover10/20/30/40M and410b00start/gate382clear. Locktest preservesinclusive0/expiry2001/transfer2002 andallheldprotection.
Corpus: unique byte-isomorphic Retail408ce8 andFix408f48 allocators literalcap8; literalpointer assignedAPI+20 at405a68→46b768 and405cc8→46c768. Handbook4 differs; originalnativeeight not changed. CompleteRetailautonomousbinding/runtime not claimed.
Artifacts: analysis/mean-speed-island.json; analysis/mean-speed-ball-count.json; analysis/traces/mean-speed-rules-original.json; analysis/traces/mean-speed-jackpot-pixels-original.json; tests/mean_speed_gameplay.cpp; tests/mean_speed_locks.cpp.
Limits: no naturalfinitefullSPEEDthree-lockwin proof, no entireoriginaltrajectory equivalence; othermode5 sharedreward helper coupling stillpartial.
Confidence: VERIFIED bounded originalstates/pixels/staticallocator and nativecomposition; PARTIAL completeMean.

Final SPEED verification: full200/200CTestPASS290.18s (`build/mean-speed-final-ctest.log`), including100finitegames andfour400000step SPEEDcontinuations; warning-freebuild. Bright40M screenshot `build/mean-speed-jackpot.png` inspected. Prior199/200 run exposedmissingmode6rightentry; fixed viaOriginal41da51, extendedentryoracle and reranfullsuite. No tests weakened.


## Cliff Jumper result island —2026-10-14

MEAN-CLIFF-043 — Original41249c/4126ec plus existing412574/41265c match2278 pixel/counter/active states (`analysis/traces/mean-mode4-dmd-original.json`). Static41af73..41afbc uses8/7 priority, sound6, actual40f754;414d95..414dcc timeout uses8/7 sound4, all five selectors1/delay0. Native24 contexts test instruction→left input→award/timeout→mode2, accepted/rejected delay/control/display ownership. Fixture explicitly supplies held-ready bits3; natural full jump not established. Retail/Fix normalized21ranges6868instructions+153DWORD identical. Index:`analysis/mean-cliff-island.json`.

Cliff final verification: warning-free CMake build;202/202CTestPASS295.17s, including original pixels, nativeCliff24contexts, visible preview and existing mode4/mode6 gameplay bundles. Log:`build/mean-cliff-full-ctest.log`.


## Left ramp / natural Cliff island —2026-10-15

MEAN-LEFT-CLIFF-044 — Original41b31f..41b491216fullrawstates/APIparams match;412df0 1896pixel/counter/activecases match. Original41b305/310/319 write438b38/3c/40=(0,0,4) aftersharedreward. Right41cd0e..45 request5/4; left6/5; both40f754 selectorsall1/delay0. Naturalfinitefixture46keyRLEruns reachesCliffonball1,18state7steps,30Msuccess vs earlyrevtimeout, then3bonuscycles/GameOver/freeze/reset; bothrepeatedexactly. Naturalnativeproof, notcapturedoriginaltrajectory. Retail/Fix normalized22ranges6979instructions+153DWORD identical. Index:`analysis/mean-left-progress-island.json`.

Shared animation/capture delta: real438b38/3c/40 triplet is now coupled toexisting418030 renderer (Original417da7/417dac). This fixes rightcapture wait exposed byleft-ramp4-repeat initialization; unchanged DragRacefiniteentry/visible/originalminigameoracle pass again.360Originalanimationstatesexact. Extra-ballroute10positive/0negative stillpass; secondpositive inputroute beingupdated. Initialfull207run203PASS/4FAIL; threeDragfailuresfixed, no assertionsweakened.

Finalleft-ramp/animation verification supersedes initial failures: warning-free nativebuild;206/206fullCTestPASS352.38s +separateextra-ball187PASS(twopositive18/10exactrepeats,negative0),207/207finaltests green.360Originalanimationstatesexact. NaturalCliff46-input-run success/timeout→3bonuses/GameOver/reset unchanged. Nextprimary:naturalfiniteKickstart25M+10M+25M→bonus/GameOver. Index:`analysis/mean-left-progress-island.json`.


## Natural Kickstart60M island —2026-10-15

MEAN-KICKSTART-045 — Original4130cc/4102c0:2168pixel/counter/activecomparisons exact. Static40726f/413ba6 provesphase1idlewaits780==0; actual4141ec initializes3aa. Entry41b0cb..41b101 request8/7 stack5,1 +allfive40f754; exit41c10b..41c14d same with57,1. Natural1237entrykeyruns plus15continuationruns:25/35/60M at26917/27133/27256, twofreshfiniteGameOver/freeze/resetreplays exact. No ball/ruleinjections; solvercheckpointscopy onlyusedtofindkeys, freshreplayvalidatesfromreset. Retail/Fix26ranges7463instructions each +153DWORD. Index:`analysis/mean-kickstart-island.json`.

Kickstart finalverification: warning-freebuild;210/210CTestPASS191.01s (`build/mean-kickstart-full-ctest.log`); finalclear25Mpreview aftercounter40polish recheckedPASS1.41s andPNGinspected. Natural60Mgame→GameOver/reset repeatedexactly; Originalpixel2168 andcrossRetail/Fix26ranges7463instructions confirmed. Nextprimary:naturalPitStop65Mfinitechain.


## Natural PitStop65M island —2026-10-15

MEAN-PIT-NATURAL-046 — FreshresetSDL-onlyfixture1394keyruns:fourpunctures thenrepair0/3/1/2, total65M by33243 (expiry33256); exactrepeat, bonus/GameOver36912/157091370/freeze/reset. Rightnudges27456/31437 only, noTilt. Originalrules186/pixels867 reused, nonewPhysics. Original4131ccdisplay25Mvsactualjackpot15M preserved. Index:`analysis/mean-pit-natural-island.json`; input/finitefixtureslinkedthere.

PitStop finalverification: warning-freebuild;212/212CTestPASS301.84s (`build/mean-pit-full-ctest.log`). Bothfreshnatural65M/deadline/bonus/GameOver/resetreplays andOriginal25MvisiblepreviewPASS. Nextprimary:naturalfiniteStockCar15hits/75M→bonus/GameOver.

## MEAN-STOCK-NATURAL-047 — Natural finite Stock Car75M

- Original bounded starter41c607/41c69a, bumper419da4 and DMD413490/413770 reused; no further physics/rule changes. Read-only dispatcher statistics added.
- Fresh native legal-input activation tick7311; fifteenth material3/4 award tick13468, Ball1,75M StockCar points. Four separate horizontal SDL-equivalent nudges; no field/ball injection.
- Two exact reset-to-input-to-threebonus/GameOver/freeze/reset replays: GameOver19480, final96391110. `analysis/traces/mean-stock-natural-input.json`, `analysis/traces/mean-stock-natural-finite.json`, `tests/mean_stock_finite.cpp`.
- Native trajectory proof only; no complete capturedOriginal trajectory, original audio timeline or completeMean claim.

## MEAN-SPEED-NATURAL-048 — Five letters through triple-lock40M and finite GameOver

- Existing bounded original rules415dc7/416fe0/41b8d0 and DMD410158 reused; simulation rules/physics unchanged. Read-only jackpot statistics and live letter/lock getters added.
- Fresh legal-input path: natural RetailFormula1 win120M, fiveletters22839, mode6 entry24821, eightballs26777, three simultaneouslocks31369,40Mjackpot31413, normaloneball return32693; all Ball1.
- SPEED awards8x10M+4x20M+2x30M+1x40M=260M. Nine legalnudges, no injected field/ball state.
- Two fresh exact replays through fourbonuses/GameOver40380, score507716240,64frozensteps andreset. `analysis/traces/mean-speed-natural-finite.json`; index `analysis/mean-speed-natural-island.json`.
- Natural SDL preview displays original40M pixels (`build/mean-speed-natural.png`, inspected). No captured Original wholetrajectory/audio timeline equivalence or completeMean claim.

## MEAN-MONSTER-NATURAL-049 — Six distinct125M and actual deadline

- Existing original initializer selected1 (9400ticks/six flags), shared rules and intro411f10/reward412fa8 reused; no rule/physics changes. Read-only dispatcher start/hit/completion/clock-expiry statistics added.
- Legal Returnlock -> natural start9395 onBall1. Six distinct actual switch IDs ->125M at18076,720ticks before18796 deadline. No nudge/state injection.
- Separate natural continuation reaches clock expiry18796 (9401post-entry steps),15M forIDs1/5; no completion reward.
- Success and expiry each replay twice from reset -> threebonuses/GameOver ->64frozensteps -> cleanreset. Success GameOver23640/147922810; expiry24632/32029640. Index `analysis/mean-monster-natural-island.json`.
- Native SDL preview original final50M page inspected (`build/mean-monster-natural.png`), subtotal125M. Captured Original wholetrajectory/audio timeline and completeMean unclaimed.

## MEAN-RALLY-NATURAL-050 — Natural timed completion and extended expiry

Original selected2/6400timer, target lookup and412af8/411824/411c60/411db4 reused; rules/physics unchanged. Natural Returnlock/start9395Ball1 -> sixcorrect/twowrong ->112.5M at22794 (90M+22.5M for3001remainingticks), or fivecorrect/fivewrong ->75M timeout25796. Eachcorrect adds2000ticks; wrongturn preserves target/Rallyscore and consumes normal1tick. Both paths replay twice through threebonuses/GameOver/freeze/reset, no nudges/injections. Success29268/159529640; expiry30944/127079640. Index `analysis/mean-rally-natural-island.json`; original22.5M DMD preview inspected. FullOriginaltrajectory/audio timeline and completeMean unclaimed.

## MEAN-OFFROAD-NATURAL-051 — Natural multiball90M/repeat/end

Natural Formula1win -> Returnlock4 -> Offroad starts21258Ball1 -> three additional balls/fourtotal -> six different-from-previous15Mawards/90M, five suppressed repeats (one after paidtarget) -> oneball401clockchecks -> modeends26925 -> fourbonuses/GameOver35028/249209410/freeze/reset, twice identically. Two legalnudges, no state injection; rules/physics unchanged. Windows415c95 `BB03000000` ->415cb5 storesBX at43f36e; existing Original4151e4 spawn oracle and Retail/Fix normalized capture family corroborate3additional/fourtotal despite handbook3. Index `analysis/mean-offroad-natural-island.json`; count proof `analysis/mean-offroad-ball-count.json`. Original15M preview inspected; wholeOriginaltrajectory/audio/manual acceptance remain unproved.

## MEAN-CHICKEN-NATURAL-052 — Three timed races/max/expiry

Handbookmode1=selected0/tablemode5. Natural Returnlock/start9395 -> races11910/14037/15309 pay35.684+48.446+56.078=140.208M; late third16988 pays75M/subtotal159.13M; separate two-race subtotal84.13M expires17796. Exact before-tick formula asserted peraward; two legalnudges, no state injection or rule/physics changes. Three paths each replaytwice through threebonuses/GameOver/freeze/reset. GameOver ordinary20872/156498980, maximum22552/175420980, expiry23004/101995980. Original4129081467executedticks preserve39c/3b4 (external lamp/audio/sharedscheduler bounded). Index `analysis/mean-chicken-natural-island.json`; original56.078M preview inspected. Allfive main modes now independently completed (`analysis/mean-main-modes-natural.json`), not allfive in onegame or wholeOriginaltrajectory proof.

## MEAN-GEARS-NATURAL-053 — Gears, earned extra ball and fivefold bonus

Fresh legal-input route reaches gears2/3/4/5 at5250/20673/22605/23541, 137 actual lamp rotations. Fifth gear uniquely arms pending0→1; upper capture29119 consumes1→0 and credits1→2. First bonus base13.5M pays67.5M. Both banked credits replay the same ball; five bonuses end at43644/200130160, then64frozen steps/reset. Twice identical, four legal nudges, no field injection. Credits are fungible: gear credit proven by sole pending provenance and complete bank redemption, not arbitrarily assigned to first replay.

Missing original gear DMD dispatch now wired:41d153 requests410fcc for2..4 or41121c for5, shared admission and five capture-delay resets preserved. Original bitmap animations/gear page/extra-ready flash/restore match4716 pixel/counter/active ticks (gears2..7, two restore values). External lamp/audio/sharedscheduler bounded separately; no wholeOriginaltrajectory claim. Index `analysis/mean-gears-natural-island.json`.

## MEAN-KICKBACK-NATURAL-054 — KICK, physical rescue and grace expiry

Handbook mean.txt37–40 anchors four red KICK letters to left sidelane. Existing rules arm43f1da via41e724..41e7b9; material7 consumes at41e655, timer390=250, integerX12/Y518 preserving fractions, vx0/vy-0x34000. Timer decrements at50Hz; remaining>=0 permits further saves. Player-record restore preserves flag/letters across turns, while timer resets-1: no unconditional per-ball flag clearing added.

Fresh legal-input route arms30261, rescues actual poolindex3 at30280 onBall1, checks exact position/impulse and original411710 request, timer249 afterstep, expires31280. Four bonuses -> GameOver39224/407952580 ->64frozen steps/reset, twice identical; nine legalnudges, no state injection. Other pool objects remain independent. Physics/rules unchanged.

Missing presentation connected: service request{7,6,2,0,23,1,411710}, saved page, five capture selectors/delay0; 17 original DAT12e3ae frames,34animation+75hold+16restore, counter12 actual438afc effect. Dedicated verifier compares254 ticks of pixels/counters/activity/effect including inactive dispatch. Native screenshot original KICK BACK inspected. Index `analysis/mean-kickback-natural-island.json`; wholeOriginaltrajectory, repeated grace save and natural unconsumed-turn persistence not newly traced.

## MEAN-LANE-SAVER-055 — Physical fence, goal bonus and lap/goal pixels

Original417dd4 was missing: LaneSaver flag378 selected a fence target, but native geometry never changed. Added slot438b44 tick at50Hz (fourticks/frame), actual service60 frames DAT852de (three32×27 sprites at272/473), terminal normal30DWORDrows + allfour hit/material32DWORDrows atbyte49e1/stride6040.43f074 points to normal959f6;43f078 to hit9ba36: these four planes are collision/material, not visible graphics.180 original/native cases compare slot/draw/both geometry regions exactly. SDL descriptor draws complete immediately; original varying render-busy timing remains bounded.

Natural legal-input fixture has lap captures4341/5949/7055, then actual GOAL switch bonus40fdec case5 at15058 (field2043→0, goal1fe0→1, pending2000→-1). This is NOT six captured laps. Upper collection15663 consumes pending200 and arms378; physical fence opens15696. Threebonuses/GameOver19012/18345620/freeze/reset twice, two legalnudges, no state injection. Separate diagnostic real upper-reward boundary opens36, actual drain/nextturn closes2232, twice;632 actual DAT geometrybytes checked.

Lap4119e0 and goal413608 pixel decoders added:2223 original/native pixel/counter/active/effect ticks. Ordinary lap dispatch/hold is still unconnected. Goal25.5M dispatch wired with original8/7/2/0 stack22/1, selectors{1,1,1,0,1}/740 and024=-1; new natural firstgoal follows GOAL-bonus route instead. Existing Original capture routine awards goal when PRE204==5 frominitial0 (sixthcapture); no invented handbook correction. Full natural lap-built goal1/2/3, extra awards and natural raised-fence ball deflection remain pending. Index `analysis/mean-lane-saver-island.json`; preview `tools/slamplay --natural-mode-preview laps`, diagnostic `--lane-saver-preview`.

## MEAN-GOAL-LADDER-056 — Lap admission, complete goal ladder and fence ownership

Original415330+405f98+40f754 executed in12 contexts: accepted lap4119e0 clears selected slot delays; timer/gate still-1/-1→-2/0→-3/0. Normal capture enters callback3 at103/releases203 regardless display, while stale delay200 releases303 if request rejected/omitted. Production now uses actual8/7/2/0,stack14/1 and delay0. No fabricated DMD-long ball hold. Cliff admission priority moves valid Return2453→2956; fresh legal success/earlyfailure2892 yield3200 result, finite GameOver9072/40700000 and9096/7725000, repeated. Initial783/1474/2169 ball checkpoints retain original assertions with new lap callback.

Fixed missing reverse synchronization of fence slot438b44/4c: stale raw reset targets previously closed active fence on unrelated load. Native mirrors both ways and after50Hz tick. New natural route keeps fence open15696 until actual extra-ball turn reset, closes63024 (36steps after62988 credit replay); test rejects earlier closure.

One fresh legal-input game: GOAL-bonus goal1 at15058 after3 laps; six-capture goal2 at26579, SideXB enabled38086/15actual rotations/award42717; six-capture goal3 at54647, upper extra awarded59565. Both banked credits consumed62988/65164, sameBall3; fivebonuses/GameOver67340/260621370/freeze/reset, twice identical, eight legalnudges, no state injection/Tilt. Thirteen ordinary lap displays plus two goal displays accepted. Original component proofs reused; allthree solely lap-built and wholeOriginaltrajectory remain unclaimed. Index `analysis/mean-goal-ladder-island.json`; inspected SDL original EXTRA BALL preview `tools/slamplay --natural-mode-preview goals`.

## MEAN-SKULL-057 — Real eight-second repeat, expiry/restart and shared reward ordering

Found missing native419919..419944 countdown: signed3b0>=0 decrements at50Hz;400→0 after400ticks, nexttick-1 clears39a and onlybyte258=2. Existing native never decremented, paying invalid late repeats.458actual Original/native clock states match;648cached41cb28 progress contexts reused.

Original411544 implemented: eight DAT13038e frames,32intro+64loop/score ticks, stops96;792fullpixel/counter/effect states exact. Request{6,5,2,0,47,1}, allfive capture selectors/delay0 executes BEFORE41b8d0/shared reward and optional lower-priority412df0. Native preserves this ordering.

Fresh legal-input game pays5M22839/10M23996/15M25297 (pre-window104/111/74); expiry26900 resetscount, new5M35024 (pre264) alongside sharedSPEED10M. Shared higher-priority410158 correctly wins display; raw05010M and totalstep15M asserted. Second expiry36624, fourbonuses/GameOver44284/261225260/freeze/reset twice, eight legalnudges/no state injection. Original15M SDL preview inspected.

Exact score-reference corrections for old native routes: SPEED507716240→482716240(-25M), Kickback407952580→397952580(-10M), goal ladder260621370→230621370(-30M); all equal invalid old Skull awards removed. Input/mode outcomes/finalticks unchanged. Strict scalar tests updated, not relaxed. Machine delta `analysis/mean-skull-score-correction.json`; index `analysis/mean-skull-island.json`. WholeOriginaltrajectory/audio/manual acceptance remain unclaimed.


MEAN-058 — Skillshot selection/launch/award/display island (VERIFIED bounded)

Actual41ac6f setsWORD43f35c=ffff only after successful41ac30 launch; failed launch preserves it. Native previously omitted this write.300 Original launch lock observations, existing1200ball cases, expanded1728 Original flipper-action cases coverffff lock; native three fresh selections verify before/after-launch edges/reset. Actual41d3e4 cash branch reads signedWORD206, awards20M+tier*10M, increments cappedtier7, clears35c. Existing216 dispatcher cases cover score and seven reward branches.

Original41455c active Skillshot: increment438af8, blink selected48x13 two-plane tile at24,7, text SKILLSHOT via actual4060f8; DAT158be8 score0..7,1587a4 award0..6, stride156.198 fullpixel/counter cases exact. Original414b60 choice helper overlays score at0,7/reward48,7, chosen tile blinks, background/counter preserved;672 fullpixel cases exact. Native idle gating follows413b04/414970/4146ac. Prelaunch title/background is native composition, not a recovered generic Original player HUD.

Fresh legal launch/flipper RLE produces20M tick770 Ball1 and30M tick3486 Ball2, tier0→1→2; persists across ball reset, three bonuses/GameOver7608/54200000,64 frozen steps/reset, twice. No injected fields. Goal/lap fixtures had relied on postlaunch selection: Ball3 GOAL edges moved14341/14401 to14300/14301 before launch14326; unchanged strict score/time/rotations pass. Files and limits: analysis/mean-skillshot-island.json. Whole Original trajectory, remaining natural reward variants and manual acceptance not claimed.

MEAN-058 verification: `cmake --build build/native -j 3` PASS/no warnings;66 targeted tests PASS36.47s, final five Skillshot tests PASS0.89s; earlier24 include long material5 pixel oracle PASS63.53s. Active and prelaunch SDL captures inspected. Machine commands/logs in `analysis/mean-skillshot-island.json`; full253 suite not rerun.


MEAN-059 — Both-ramp progression / surviving right marker / finite guard audit

Fresh existing SPEED input reused unchanged: left ramp0→1 tick783→2/armed1474→0/+letter2498; right0→1 tick18335→2/armed21655→0/+letter22839 (letter4→5). Nine left/three right hits, three left/one right complete cycles. Strict tests compare old-lamp stop, new4/6/1/0 commands, green flags392/3a2, enabled mode commands, clear/disarm/+letter/capped5/fifth SPEED lamp, Mode6 entry. Twice through four bonuses/GameOver40380/482716240, frozen64steps/reset. Original stage primitives unchanged; whole Original trajectory unclaimed.

Guard audit found valid Original case blocked by two native filters: layer0/mask3/x>=260/marker20 in mode5. Actual41da51 has no mode filter;4164e1 callback4 base timer/slot/score/417068 transfer also applies in mode5 (416579/416664 exclude only mode6 special lock branch). Removed native entry filter and expanded base callback4 helper to mode5.779 Original comparisons exact, including251 sequential mode5 callback4 states through transfer. Six native diagnostic chains (three selected main modes twice) capture1→transfer252→release352→three bonuses/GameOver5712/78625000/freeze/reset. Diagnostic ball/rules deliberately injected via existing debug APIs; natural surviving-marker occurrence not claimed. Existing special Tilt integration also adds mode5/callback4.

Artifacts: `analysis/mean-ramp-progression-island.json`, `analysis/mean-guard-audit.json`, `analysis/traces/mean-mode4-right-entry-original.json`, `analysis/traces/mean-mode5-right-finite.json`, `analysis/traces/mean-ramp-progression-natural-finite.json`. Other guards are bounded invariant/domain checks with STRONG confidence; universal unreachability is not proved.

MEAN-059 final verification: buildPASS/no warnings,70/70 targetedCTestPASS41.98s.100fresh legal-input seed games twice (1584960ticks), no stops; three bonuses/GameOver/frozen8steps/reset each; aggregate reference792480ticks/691117830score perrun. Seeds cover normalmodes1..3 only; specialmodes remain covered by separate fixtures. `analysis/traces/mean-100-games-finite.json`. Full256tests not rerun; completeMean/manual/Originalwholetrajectory not claimed.


MEAN-060 — Shared DMD voice / mode themes / real gameplay PCM island

Claim: mapped DMD admission already held the Original voice order/bank but failed to deliver it. Actual405f98 writes4297ac=stack0/order,4297a8=stack1/bank,4297bc0/4297b8-1 for accepted nonnegative stack0, same88 pending request. Negative stack cancels only when previous display state4 and actualaudioflag2 active; rejected requests no writes.960 full Original request cases exact (360positive/12cancel). Native queues positive requests centrally plus the separate right-SPEED path. Negative preemption transports conditional8c; actual playback checks foreground88 before stop/PCMclear, otherwise preservesqueuedPCM. Simulation does not fabricate an audioactive flag. Tests cover inactiveforeground cancellation preserving SDLqueuedbasePCM.

Original upper415330 init calls84 bank0 orders51/46/40/2 for selections0/1/2/4 (415969/415ac6/415b83/415dba), SPEED29 at415710. Original4194e4 resumes84bank0order62 when signed37a>=0, otherwise80; confirmed Chicken success41637a and timedreturn;12 bounded Original cases. Native now queues these missing starts and returns. First ordinary uppercapture has no extra84/88; no invented cue added.

Eight natural main-mode success/timeout RLE routes twice verify16starts/16returns plus finiteGameOver, exactservice/bank/order. Real DAT/STIM/libxmp + sample mixer: Skillshot7608steps/54200000/1677564PCMframes and SPEED40380steps/482716240/8903790frames eachtwice. Exact220/221framesper200Hzstep, deterministic request/PCM hashes, nonzero isolatedmusic/SFX/mix, reset silence and newgamefreshPCM.21162708totalframes. These are native audio regressions, not complete Original PCM/timing equivalence or human audibility.

Artifacts: `analysis/mean-audio-island.json`, `analysis/traces/mean-display-audio-original.json`, `analysis/traces/mean-mode-audio-original.json`, `analysis/traces/mean-mode-audio-gameplay.json`, `analysis/traces/mean-audio-gameplay.json`. Unclassified native debug-display fallbacks and complete callback coverage excluded.

MEAN-060 verification: warning-free build;80/80 targetedCTestPASS39.55s. Full260scan185.68s:256PASS/fourfailures; four corrected legacychecks now4/4PASS16.73s, zeroopenfailures (not a single clean260-test invocation). Audio-on vsallMeanSimulationqueuewritesdisabled1.8Mstate/events byteidentical, provingstale randomSPEEDexpectation independent ofaudio; preservedfourrandomcontrols andexact7spawn/eight→singleball-mode2 contract via existingstricterfiniteSPEEDfixture. CachedRetail Monster/eightball previews replacedfragilelongbots; accepted405f98 Originalverifierstub nowincludesvoicewrite, strict530tick minigame state/pixel/audio comparisonpasses. Logs/commands `analysis/mean-audio-island.json`; screenshots inspected.


MEAN-061 — Native frontend acceptance (no additional Original RE)

Concrete failures: Enter on explicit Cancel/Reset options rows used apply(), persisting edits; fixed dispatch to activate(), with failing-old/passing-new isolated persistence tests. Crop aspect clipped vertically atzoom1 but camera onlyfollowedzoom>1; fixedfollowwhenaspectCrop,96edge/center cases ×fourDMDpositions/laptop+HiDPI/zoom1,2; prior180Fit cases retained.

Highscore handle returnedfalse on repeatedkeydown, allowingR/P/Escape throughmain. Modal now consumes repeat/keyup; main globalshortcuts requirefreshkeydown, gameplaykey suppression onconfirmation. Two freshlegalSkillshot54.2M games reachGameOver7608/3bonuses, actualscancodes ABC/RST/backspace/repeats, atomicisolatedpersist/reload,64duplicate/frozen checks, newgameclear+freshstep retainingtable. Actualmain SDL_PushEvent test runs scorednativeGameOver8,256,830, repeatedR/P whileediting, RAB+Enter/save/reload, freshRreset, Escapeoptions, Right+Enterfullscreen, repeatedEscapeignored. ChecksactualSDL_WINDOW_FULLSCREEN; storage/flags/testsnapshots isolated from userprefs. Dialog nowshowsachievedscore; screenshotinspected.

Verification: warningfree `cmake --build build/native -j 3`;85/85targetedCTestPASS39.56s (`build/mean-frontend-regression.log`), final5frontendtestsPASS0.49s afterlabel (`build/mean-frontend-final-tests.log`).262registered/fullsuite notrerun; previous260scan+corrections retained. HeadlessSDL/276layoutchecks do not establishphysicalmonitor/HID/audioaudibility. CompleteMean andallfivemodesinonegame unclaimed. Index `analysis/mean-frontend-island.json` and fixture `analysis/traces/mean-frontend-lifecycle.json`. NoGit metadata available.


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

MEAN-070 — Source audit found no window-focus/minimize handling in SDL main loop. Implemented independent activity gates. Actual pushed SDL events cover focus loss with launch/nudge/reset input, minimize, focus gain while minimized, restore, and a second focus cycle with manual pause. Full ball bytes and shared state stay frozen; audio-enabled test checks actual SDL device pause and nonempty resumed PCM queue. Dummy backend only; physical output is not claimed. Reports: `build/frontend{,-audio}-acceptance/report.json`.

MEAN-070 verification: warning-free full build;70/70 affected CTests PASS21.97s (`build/mean-focus-tests.log`), including both actual SDL main-loop acceptance routes and full frozen ball-byte comparisons. Full suite not repeated; prior304/304 baseline retained. No Git metadata/configured formatter.

MEAN-070 physical follow-up: user confirmed Alt-Tab audio works on retry ("geht doch!"). Real Wayland focus log `build/mean-alt-tab-live.log`: focus returns, no mute/manual pause/minimize. Initial silence not reproduced; no audio behavior changed. Added opt-in `SLAM_TRACE_ACTIVITY` event diagnostics. Refreshed CMake after system SDL library update; build PASS, both SDL frontend/audio acceptance tests PASS0.81s.

MEAN-071 — Native presentation evidence (not Original RE): real `SDL_GetGPURendererDevice` path and SPIR-V shaders tested via `presentation_probe --require-gpu`;18 preset/quality combinations, six distinct Balanced pixel hashes, Original and zero-strength exact identity, deterministic repeat, independent DMD parameters, clipping and target resize. No GPU readback during ordinary gameplay (test capture only). Classic fallback and `SLAM_ENABLE_GPU_EFFECTS=OFF` build tested separately. Artifacts in `build/arcade-acceptance/`; user-owned original graphics remain in build. Menu font/stb provenance and licenses bundled separately.

MEAN-071 final verification: warning-free main and explicit no-shader builds. Full307/307 PASS215.20s; final UI/shader71/71 recheck PASS22.64s, last4/4 smoke PASS1.11s; no-shader2/2 PASS0.57s. Real Vulkan18-combination pixel contract and real GPU/audio/fullscreen/focus/highscore/newgame acceptance PASS.20 exact-size category screenshots plus six actual GPU presets inspected; 240-frame benchmarks at2506x1514 show medians Original5.002ms/SoftGlow5.007ms/CRTDeluxe5.005ms, p95<=5.160ms (CPU wall times including presentation, not GPU timestamps). Artifacts `build/arcade-acceptance/`, index `analysis/mean-presentation-island.json`. No Git metadata/configured formatter. Physical aesthetic preference remains a user check.

MEAN-072

Claim: reset retained input edges across sessions. Evidence: legal Reward7 game → held inputs at frozen GameOver → reset → Seed0 loses exactly two initial5c samples versus fresh construction; `mean-reset-held-input-regression.json`. Clearing left_/right_/launch_pressed_ restores eight repeated/double-reset cycles and2072-game deterministic soak. Seed44's old inherited initial Skillshot choice contributed20M to the former100-game reference; fresh constructor-per-seed audit confirms671117830 vsold691117830 with unchanged792480ticks. No assertion removed.

Claim: three distinct main-mode contracts compose in one finite ordinary game. Evidence: fresh legal RLE; Formula1 actual120M and pending-extra increment, Offroad six paid changes/90M/end, Chicken completion, then46104stepGameOver/402853880/fourbonuses, freeze64 and reset; two independent runs exact. Source/result: `mean-three-modes-{input,finite}.json`. Flags for started modes are not completion evidence. All-five claim remains false.

Claim: bounded Original behavior matches expanded native domain. Evidence: `mean-normal-boundaries-original.json`17,960 cases; `mean-natural-component-original.json`22 actual legal-route ball records, all100bytes exact after40a010. Full collision requires actual flipper/engine/nudge/pointforce/material/rule/other-ball precontact context, not fabricated substitutes. See `analysis/mean-original-acceptance.json`.

MEAN-072 final verification: warning-free `cmake --build build/native -j 3`; complete `ctest --test-dir build/native -j 3 --output-on-failure` PASS312/312 in367.98s, including official2072-game soak154.66s. Six focused post-reference/marathon/oracle checks PASS13.81s. Initial old100-game aggregate failure resolved via100 independent constructor comparisons, not weakened assertions. No Git metadata/configured formatter. Three-of-five composition remains PARTIAL; bounded Original comparisons are not whole-trajectory equivalence.


MEAN-073
Claim: all five main-mode contracts compose in one ordinary finite native game, with intervening SPEED.
Evidence: `analysis/traces/mean-five-modes-input.json` contains complete reset-origin legal RLE and original DAT/image identities. `mean-five-modes-finite.json` contains two identical independent runs: actual Formula1 Retail120M/extra, Offroad6paidchanges90M/end, Chicken, Monster all6distinct125M, Rally6correct; five at78512 onball2; SPEED1start/peak8/normalreturn; GameOver83056/924072310/fourbonuses, freeze64/newgame. Intermediate fixtures `mean-four-modes-{input,finite}.json` and `mean-four-modes-speed-{input,finite}.json` retain the capture and SPEED boundaries. Production physics/rules untouched. Native composition VERIFIED; full Original event/contact trajectory equivalence unproved. Offroad changes are not six unique targets, and this is not a separate Original Offroad win flag.

MEAN-073 verification: warning-free `cmake --build build/native -j 3`; affected34/34 CTests PASS24.01s (`build/mean-five-modes-regression.log`), including strict golden replays for three/four/four+SPEED/five. JSON/RLE totals PASS. Full suite not repeated because production code is unchanged; prior full312/312 remains historical, now315 configured tests. No Git metadata/configured formatter/linter.


MEAN-074
Claim: real native contact states match Original per-ball contact orchestration and complete physical response/separation.
Evidence: `mean-live-contacts-original.json`; two fresh reset-origin legal RLE routes,110615observed/1036stratified states. All100bytes exact at Original408e70 wall dispatch409bec or full free/flipper return; all358wallstates then execute full materialcallback and409d78separation with both0/1displayanswers,716runs exact. Original419da4/41e724/40f754 run; external score/audio/display/music services adapted. All5layers, movingflippers,65activeNudge/336multiball states, two exact mutable LaneSaver tile hashes. Source/input/image/DAT/context SHA recorded; raw original-derived contexts remain underbuild. `mean_contact_observer_finite` uses unchanged all-five strict ball/input/audio hash and finite lifecycle golden, proving enabled observation does not alter that game.
Coverage guard initially exposed missing raised-geometry route; added existing natural GOAL RLE+verified coast to19012/18345620, not injected geometry or weakened assertions. Per-ball component VERIFIED_BOUNDED; no wholeOriginaltrajectory, global outcomes, material6 or actual fence-area impact proof. Next: natural408bfc ball-pair context.

MEAN-074 final verification: warning-free `cmake --build build/native -j 3`; full `ctest --test-dir build/native -j 3 --output-on-failure` PASS317/317 in362.23s, including2072-game extended soak150.08s and both new live-contact/observer tests. Python syntax, JSON/RLE totals PASS; final changed source/test/CMake regions inspected. No Git metadata/configured formatter/linter. No physics formulas/rules altered.


MEAN-075
Claim: naturally reached ball-ball collision responses and pair visitation match Original bounded components.
Evidence: `mean-live-pairs-original.json` from full legal all-five RLE:127828paircalls; every38mutation plus1823no-ops retained. All200bytes exact under actual Original i/j vs native compact0/1 slots; unselected Original canary records unchanged. All38 alter velocity of state2/state2 balls:23SPEED/15Offroad. All28pairindices covered. Actual408874 scheduler supplies reference count0..8 order;11132native tick batches/7patterns match with adapted phase1/physics and supplied native row counts. No mid-tick count changes naturally observed. Exact all-five ball/input/audio hash and finite lifecycle remain unchanged with enabled observer in two fresh constructions. Raw Original-derived contexts stay underbuild; image/lookup/route/context hashes in report. Physics/rules unchanged; wholeOriginaltick/trajectory equivalence unclaimed. Automated acceptance tracks closed within these bounds; next portable Mean RC package.

MEAN-075 verification: warning-free `cmake --build build/native -j 3`;18/18 affected CTests PASS20.28s (`build/mean-live-pairs-regression.log`),5/5 pair/contact/observer/five-mode cross-checks PASS11.20s, final pair oracle1/1PASS3.42s. Python syntax/JSON PASS; changed source/CMake/test regions inspected. No Git metadata/configured formatter/linter. Full suite not repeated for optional read-only observation/test changes; prior317/317 full suite remains historical,319 now configured.


MEAN-076
Claim: native Mean RC runs without checkout/developer runtime dependencies using a private data companion.
Evidence: `analysis/traces/mean-package-acceptance.json`: fresh archives extracted elsewhere/pathswithspaces/foreigncwd; read-only app/data in Bubblewrap without checkout; strace0checkout accesses/0Python-Wine execs; SDL real event routing/audio device queue/fullscreen/focus/initials save/newgame pass. Existing all-five native checker explicitly mounted with inputfixture verifies two full games using package eight datafiles/minimalstart/profile metadata: hash7646546959636972790,83056ticks/924072310. Missing data/minigame, corrupthashes and existingoutput guards pass. Original runtime image/cache/DAT files excluded from program archive; exact private whitelist hashes in packaging/mean-data.sha256. Public2641585bytes/private876858bytes archives underbuild/releases.
Realhost final private launcher --require-gpu with14-framefrontend/audio acceptance exits0 (`build/mean-rc-host/report.json`); actual table/DMD screenshot inspected. This proves local devices/API flow, not subjective sound/control feel or older Linux compatibility. Local ABI glibc2.43/GLIBCXX3.4.32. Raw EXE/DAT importer remains pending; no original whole-game equivalence claim.

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


## PIRATE-CLOCK-003 — native full-clock / controls / DMD / first-ball lifecycle

VERIFIED within retained trajectories, Retail SHA185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6. Original405234 consumes5ms physics409154→40950c and20ms435414→407b88; actualCRT RNG44f4d0/44f4c6/45021e and nudge/camera execute. Native boundary405486 bypasses only display interpolation and uses original4054e1 epilogue. Native fixed compiled C++, no runtime instruction decoder and no gameplay service substitutions. File/allocation adapters are confined to original initialization; frontend memory/clock are isolated synthetic fixture conditions.

Proof:10000original steps plus fresh replay; native and SDL match every100-byte ball state,11clock/RNGfields and1920-byte DMD hashes per step. Physical drain at2188 enters original bonus; next ball at2976. Separate1000step full-clock original Shift route and native/reset/SDL match; right Shift also drives upper flipper. Key adapters preserve original callbacks, guards, control byte/timers and physical edge inhibition.24original keyboard-vs-action contexts independently verified; this is not24native whole-game scenarios. See analysis/pirate-input.json and analysis/traces/pirate-full-{tick,input,10000}.json; full outputs under build/oracle/.

Original40bbac nibble lookup initializes DMD;404f09..404f15 selects table-data+20;406137..406190 maps intensity to palette indices. Pirate465824+20 gives22/28/e0/ef; actual active table RGB used. Native original DMD hash sequence matches2500updates/78distinct frames in10000step route, including score/bonus. Screenshot build/pirate-native-full-1000.png inspected. Runtime host scaling/driver/audio output is a separate boundary.

Diagnostic correction: backward reachable blocks can precede a function entry numerically. CFG generation must begin with goto real-entry; previous sorted-fallthrough bug diverged at653 despite correct jump-table contents. Retained1000/10000step fixtures cover it. Shared Mean generator's default output regenerated byte-for-byte unchanged.

Long-run clock proof also corrects an invalid unconditional scheduler-count assumption: original bonus/control states suppress scheduler/timer calls. Oracle now checks actual eligibility branches, exact200Hz flipper/RNG totals,50Hz frame counter and identical call counts on fresh replay. No failed comparison was discarded.

Implementation: src/physics/pirate_session.{h,cpp}, src/frontend/pirate_play.cpp, tools/lift_pirate_step.py, tools/slampirate. Ten affected CTests PASS14.79s including Mean finite all-five-modes and actual SDL frontend; full CMake build without warnings; original sprite/ball check and Python/shell syntax pass. No Git metadata/formatter configuration. Complete Pirate finite-game/all-mode/audio/lamp/import acceptance remains pending; unsupported original branches throw rather than inventing behavior.

## TABLE-SPRITES-001 — original sprites transferable across all four tables

VERIFIED:103frames/304448pixels (11flippers) exactly match actual Retail preprocessing40b71c on pristine user DATs and original descriptor-selected foreground masks. Shared native TableDefinition validates exact Retail/DAT identities; Mean complete-game readiness remains tied to its accepted Demo engine, Pirate is GameplayPreview, Space/Demon ViewerOnly. No physics equivalence is inferred from shared assets.

Ball interpolation40871c..40879d independently executes7x87 cases: trunc((previous*(1-rest/5)+current*rest/5)/65536-7), signed16.16;16x15 MAIN mask/pixel layout remains shared. Flippers precede balls; ball draw sort is ascending renderY and foreground uses object+54. Sources and complete scope: analysis/table-sprites.json; tools/validate_table_sprites_original.py. Native API src/assets/table_sprites.{h,cpp}; all4DAT definitions/decodes and mutation rejection pass.


## PIRATE-FINITE-004 — canonical finite game, initials, original restart

VERIFIED bounded Retail SHA185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6. Correction to PIRATE-CLOCK-003: relocation of454b68 pointers into synthetic runtime split ball state from original408d78's direct canonical46c1b4 write. Previous phase3→1 agreement did not prove a usable next ball. Original canonical46c15c+i*100 retained; startup404f09..404f62 and Pirate2/404ebf..404ee6 restore table/53lamp/highscore pointers. Superseded compact traces preserved separately; canonical baseline traces regenerated, not weakened. Evidence: analysis/pirate-next-ball-boundary.json, pirate-startup-bindings.json.

Original player record+0e ballnumber/+10 extra credits;408274..408291 increments exhausted-credit ball; default three balls,454aa4 alternative five. Final408465..408547 sets phase0/players0/activeballs0. Initials admitted only phase3/46c61c6;405d54 actual key lookup,405de8 insertion,405e63 NUL. OriginalF1→408ae0 guarded phase0 preserves clock/RNG. NativemidgameR remains a distinct diagnostic fresh reset. See analysis/pirate-gameover-boundary.json and pirate-highscore-input.json.

Proof: original legal Enter timeline, three naturally drained balls/bonuses,ABC scans1e/30/2e andEnter1c,GameOver9480,F1 newgame9581,second launch9911,12000steps total. Native/reset/SDL match each100byteball,11clock/RNGfields,15lifecyclefields andDMD/highscore/53lamp hashes. Fresh native profile stores original4.5M/ABC record, separate SDL process loads exact50bytes without file rewrite.200malformed-profile cases plus atomic-replacement preservation covered. No gameplay/output service substitutions; initialization file/allocation adapters and synthetic5ms clock,CRTseed1,initial zero highscore table are explicit fixture conditions. No actual host audio/display,all-Adventures/multiball or extended attract proof implied.

Artifacts: analysis/traces/pirate-complete-game.json (pinned states/timing/lifecycle/three hash sequences,inputs,context hashes); analysis/pirate-complete-game-boundary.json (actual call targets); tools/verify_pirate_complete_game.py; private full traces/screenshots and complete-game-verification.json in build/oracle/pirate-complete-game-lamps-ready/. Implemented src/physics/pirate_session.*,src/core/pirate_input_replay.h,src/frontend/pirate_play.cpp,pirate_highscores.*. Unsupported original paths still stop explicitly.

## TABLE-LAMPS-002 — shared original lamps and flipper parent masks

VERIFIED original Retail lamp descriptor/command boundaries. Mean63/Pirate53/Space48/Demon52 =216lamps/432off-onframes,303296localpixels; actual original40b0b4/40b2ec vs native decoder0differences. Independent bounded command execution retains parent links; NativePirate408da8 runsactualcommandconsumer every20ms,descriptor+8 state hashes agree for12000steps. No guessed blink/timer semantics.

Flipper40b526 loads mask[descriptor+20] without frameoffset;40b5a8..40b5c7 frame-indexes source[descriptor+1c];40b5e1..40b5f3 writes source AND NOT mask. WORD+14 framecount,WORD+16 drawcache. Fourpatterns(alloff/allon/twoseededmixed),threeflippers,first/lastframes:24actualoriginalblits/72192pixels vs C++ compose_table_flipper,0RGB/alpha differences. Original40b71c preprocessing changes no native-opaque sourcebytes; retain pristine foreground alpha even when maskedpaletteindex is0/1. Static lamp reference clears parents only for isolated local-pixel comparison; full command and flipper comparisons retain parents. Arbitrary additional dynamic objects are not claimed verified.

Evidence analysis/table-lamps.json,table-lamps-original.json,pirate-flipper-lamps.json; tools/validate_table_lamps_original.py and verify_flipper_lamp_composite.py --native build/native/table_flipper_composite_probe. Actual original-derived pixels/snapshots remain underbuild/. Shared implementation src/assets/table_lamps.*,table_sprites.*; Mean's established gameplay renderer unchanged.

Verification for FINITE-004/TABLE-LAMPS-002: full `cmake --build build/native -j3` PASS,0warnings. `ctest --test-dir build/native --output-on-failure -j3 -R '^(pirate_original_native_sdl_1000|pirate-full-.*_native_sdl|pirate_complete_game_native_sdl|pirate_highscore_storage|table_(definition|sprite|lamp)_metadata|mean_five_modes_finite|mean_frontend_sdl_acceptance|presentation_fallback|ball_display)$'` PASS13/13,16.41s. Separate `ctest --test-dir build/native --output-on-failure -R '^pirate_flipper_lamps_original$'` PASS1/1. All4DAT native lamp decode432frames PASS; changed Python/shell syntax and JSON PASS. Actual GameOver9520/phase0 SDL capture build/pirate-gameover.png inspected. Mean all-five golden unchanged. No Git metadata or configured formatter; full unrelated suite not repeated.


## PIRATE-ADVENTURE-005 — Walk the Plank vertical island

VERIFIED bounded Retail SHA185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6. Original rulebook PDF SHAbe23f47fba12a5749bacae511b41fd00a8f3f7b03c1abdc1edf9db0aecfcd869 supplies behavioral expectations; all addresses/numbers below are original instruction/runtime evidence, not handbook inference.

Original right ramp: layer1 switch3 at225,45 →437c34/right branch arms46e2de and4659c0. Upper-left: layer0 switch1 at24,60 →437a98 guide18 →4340ca capture3/callback5 →4332d3 phase5/Adventure0, played flag46e2c2, rope bytes46e564..568=1. Capture releases naturally at step1481 with12000 remaining200Hz ticks. 436c78 grants10M only for an outstanding target; repeated same ramp grants its250k base award without another10M. Distinct target adds400ticks; all five set46e556=1/timer3000. Capture2 at86,10 →43234c grants30M plus500k base;4366b4 returns phase2 and selects Adventure1. Success fixture totals83M. Timeout at13482 sets signed timer-1 and returns phase2/next selection, score remains1M.

Physical trigger witnesses: layer1 points81,228(id4),49,74(id2),225,45(id3); layer2 point91,44(id1) after actual base guide clear/skull guide; base302,185 captures callback1(id0) and86,10 collects. Dat-backed switches, original integration/scheduler/collision/capture/score/DMD/lamp code all execute. After entry, actual layer2 return-lane switch at70,340 →438cdf clears shared field46e560. Teleporting past this necessary transit left the original waiting at later capture release; no fake gate clear was added.

Implementation adds original observed DMD callbacks430168/4301dc/42ef80,820 compiled instructions within the existing bounded island. Original407c09 dispatches timeout42ef80 (11 observed calls). Late Unicorn hooks require translation-cache invalidation to observe previously compiled shared clock/DMD blocks; ctl_remove_cache changes no game state, and uninstrumented fresh original replay matches all samples. Evidence: analysis/pirate-adventure-boundary.json.

Proof:1812 success steps and13524 timeout steps, original fresh replay/native fresh reset/SDL exact for100ball bytes,all864bytes46e220..46e57f,11clock/RNGfields,15lifecyclefields,DMD1920byte hashes,53lamp-state and50highscore hashes each step. Directed waypoints alter only free-ball position/velocity and validated layer bindings (including switch-cache invalidation). No rules, scores, timers, capture states or callback IDs injected. Diagnostic mode is separate from legal-key replay, visibly labeled, rejects captured-ball placement, and refuses persistent highscore profiles. Success screenshot build/pirate-plank-active.png inspected. This is not a legal-human-input flight or all-Adventures proof; full basic finite-game acceptance remains a separate retained regression.

Artifacts: analysis/pirate-plank-island.json; analysis/traces/pirate-plank-{success,timeout}.json (frozen inputs/waypoints/milestones and sequence hashes); tools/pirate_adventure_oracle.py,verify_pirate_adventure.py; private full traces/screenshots/verification.json under build/oracle/pirate-adventure/. Native source: src/core/pirate_shot_replay.h,src/physics/pirate_session.*,src/frontend/pirate_play.cpp. Original-derived instruction bodies/data remain under build/. Next primary: Swordfight jackpot growth/collection/timeout using these same entry/trigger boundaries.

PIRATE-ADVENTURE-005 verification: `cmake --build build/native -j3` PASS,0warnings. `python tools/verify_pirate_adventure.py` PASS including captured-ball rejection and untouched profile guard. ctest --test-dir build/native --output-on-failure -j3 -R '^(pirate_original_native_sdl_1000|pirate-full-.*_native_sdl|pirate_complete_game_native_sdl|pirate_plank_adventure_native_sdl|pirate_flipper_lamps_original|pirate_highscore_storage|table_(definition|sprite|lamp)_metadata|mean_five_modes_finite|mean_frontend_sdl_acceptance|presentation_fallback|ball_display)$' PASS15/15,27.09s. Mean finite all-five golden and SDL frontend, Pirate full finite-game/highscore/lamps/Shift/baselines remain green. Changed Python compile and JSON parse PASS. Full unrelated suite not repeated; no Git metadata/formatter configuration. Exact logs/commands also in analysis/pirate-plank-island.json.


## PIRATE-ADVENTURES-006 — four-Adventure reuse island

VERIFIED bounded Retail SHA185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6. Four modes reuse the proved entry/physical event boundaries. Actual material3 bumper169,38 →438f17..438ff6→436508 selects1..4; no mode-field assignment. All setup changes are explicit diagnostic free-ball position/velocity/layer/cache bindings; no rule/score/timer/capture/callback injection.

Swordfight1:433427 initializes DWORD46e2a8=5M.436da8 awards the current jackpot for every lit ramp/trap, including repeating the same ramp.43952c and4370f4 add250k for bumper/target hits; tested upper trap adds500k. Fixture reaches6M jackpot and41,017,480 score, then original timeout/phase2/selection2. No invented one-shot completion condition.

Dive2:4334f5 initializes WORD46e54c=10,WORD46e54a=0; actual bumper raises rate11 via439588.436e19 caps progress:11,22,33,44,55,66,77,88,99,100. Final partial depth award is clipped; an extra hit after bottom grants only250k base, not another depth award. Original30M collection/release/phase2→selection3 yields84,253,720. Separate timeout retains1,002,480 without jackpot.

Monkey3:WORD46e544 starts1.436f85 accepts only its current target:1→2→3→4→0. Wrong4 gives only250k base; four ordinary pieces pay10M each, final piece30M. DWORD4659a8 reaches5; natural capture/release returns phase2/selection4,72,503,720 total. Separate timeout retains1,003,720 with no pieces.

Shark4:WORD46e55a is pending speed; ramp+150,bumper+20,target+25 verified.4318f2 consumes one pending unit and adds8timer ticks before the ordinary decrement (net+7). Actual escape threshold is raw0x1b3a=6970, not an assumed handbook-derived constant; fixture escapes at6973 and awards50M, total51,771,200,phase2/selection5. Independent timeout retains1,004,960 without escape award.

Seven fixtures/47,256 steps replay from fresh original context without tracing hooks, then native/reset/SDL exactly match100ball bytes,all864rule bytes,11clock/RNGfields,15lifecyclefields,DMD1920byte/53lamp/50highscore hash sequences every step. Independent cases do not prove all five modes in one finite game or a legal-key-only trajectory. Existing full basic finite-game and Plank proofs remain separate and green. Monkey completion SDL screenshot inspected.

Only462 additional compiled original instructions; actual dispatch targets retained in analysis/pirate-modes-boundary.json. Reached helper4067be requires SETE CL; byte write preserves other ECX bits and leaves flags unchanged. Added only to Pirate's custom generator handler, shared Mean generator unchanged. Original/native DMD and rule traces verify the resulting paths. Generated original instruction bodies remain private belowbuild/, no runtime CPU decoder or gameplay service stubs.

Artifacts: analysis/pirate-four-adventures-island.json; analysis/traces/pirate-{sword,dive-success,dive-timeout,monkey-success,monkey-timeout,shark-success,shark-timeout}.json. Reproducers tools/pirate_modes_oracle.py andverify_pirate_modes.py; private traces/screenshots/report underbuild/oracle/pirate-modes/. `cmake --build build/native -j3` PASS0warnings; `python tools/verify_pirate_modes.py` PASS7/7 original/native/reset/SDL contracts;15 existing affected CTests PASS32.49s, including Mean finite five-mode golden/SDL frontend and Pirate finite/highscore/Plank/lamps/input. New CTest pirate_four_adventures_native_sdl is registered and invokes the exact verified command; no redundant second execution. Changed Python/JSON syntax checked; no Git metadata/formatter configuration, full unrelated suite not repeated. Next primary: Knife Throwing input→DMD simulation→win/lose→extra-ball/return.


## PIRATE-KNIFE-007 — original video/Extra Ball vertical island

Claim: Adventure5 now runs the original50Hz Knife Throwing simulation, Shift
movement/automatic crossing throws/manualEnter, win/lose DMD→normal-play return
and earned Extra Ball collection natively. Bounded evidence, confidence1.0;
not a legal-key-only table trajectory or combined six-Adventure finite game.

Original entry433739..433917 sets46c6c0/video and holds canonical ball state3.
407bbc invokes4349f0;364 intro frames precede simulation. Player X46e29c,
previous46e290 and direction46e294; eight knife slots46e0b4/stride8; five opponent
activation/projectile ages46e278/46e264. Actual keyboard40404c dispatches existing
434268/434340 and434160→434184;434e5a also throws when crossing an active opponent.
Original input configuration binds46c5dc=2a/46c5e0=36; no gameplay fields injected.

25kills reduce DWORD46e230 from24 to signed-1, award3M each/cumulative75M at
46e298, and reduce spawn period46e238 from100 to25. Actual result dispatches
42fb54 success/42fd1c failure;63 observed indirect edges retained in
analysis/pirate-knife-boundary.json. Success increments pending WORD46e2d8.
Physical upper trap86,10 pays500k but leaves that pending credit untouched; right
trap302,185 invokes437388, consumes pending credit and increments player+10.
Runtime success milestones: video starts658, active2112, win9548, released9898,
Extra Ball collected11353; final score76,756,200. Failure result3780/released4130
yields no video points/credit. Subsequent extra-ball drain/redemption not covered.

Proof:11436 success+4212 failure steps=15648, fresh original replay/native fresh
reset/SDL exact for all100ballbytes,864rulebytes,additional892videobytes in three
explicit ranges,11clock/RNGfields,15lifecyclefields,DMD1920bytes,53lamp states and
50highscore-byte hashes each step. No waypoint occurs during active video. Table
entry and post-video traps use diagnostic free-ball positions on actual DAT
triggers; no rule/score/timer/enemy/capture/award/completion writes or stubs.

Implementation:985 additional compiled original instructions (18210→19195),
Pirate-only bounded ROR support; shared Mean generator unchanged. Original
mutates its own DAT DMD frames via434e7c/434ed4; no invented sprites. Original
code/assets/full snapshots remain underbuild/. Existing game-action adapters
need no production input change. Extra video hashes collected only for explicit
diagnostic traces; normal play has no extra tracing cost.

Artifacts: analysis/pirate-knife-island.json;analysis/traces/pirate-knife-{success,failure}.json;
tools/pirate_knife_oracle.py,verify_pirate_knife.py; private full traces and
knife-verification.json underbuild/oracle/pirate-modes/. Screenshot
build/pirate-knife-active.png inspected (step3000, colored DMD above playfield).

Validation: cmake --build build/native -j3 PASS0warnings;17/17 affected CTests
PASS88.11s including newpirate_knife_native_sdl, all five prior Adventures,
Pirate finite/highscore/lamps/input and Mean finite five-mode golden/SDL.
Changed Python compile/JSON parse PASS; independent source review found no
material issues. No Git metadata/configured formatter; full unrelated suite
not repeated. Next primary: first Pirate multiball lock→release→jackpot→return.


## PIRATE-MULTIBALL-008 — Cave/cannon/Crocodile and shared lifecycle fixes

VERIFIED bounded integer-oracle/native/reset/SDL. Actual43,198/layer0 switch3
enters437618/capture4/432c84; locks46e2bc progress0→1→2.42bae4 enforces real
slot cooldown465a44 after release. Top trap86,10→432075 opens phase6. Original
434418 ignores early press until465974<0. Legal left Shift at center sine
index2024/value603 launches the real ball at2225; no waypoints during flight.
Mermaid capture3/43260c starts phase4 at2407.46e2be increments on entry, so it
is named played_multiballs, not completed modes. Original408ce8 allocates the
second ball at3146. Wrong target pays no jackpot;43683c pays5M, Cave grows
46e2a0 by1M without adding a lock, then6M pays; cumulative46e298=11M.

Six diagnostic drains exercise original rescue/grace expiry. Count2→1 at5520,
then original43163c waits800physics steps and returns phase2 at6320. Separate
miss at initial aim1024 loses one lock at2428, yields no jackpot/multiball and
returns normally. Manual Cave/Multiball sections were starting evidence only;
all claims above checked against actual binary execution.

Two shared blockers resolved. First, retained isolated context assigned math
pointer46c66c after service startup, leaving46b778 null. Original405b6a..405b78
loads that pointer and writes it into46b778. Original oracle executes these
instructions; native reset performs the same sole memory effect. Original
snapshot files/hashes remain unchanged; no rule-state initialization fabricated.

Second, actual render preparation40566f→408674 compacts lost state5 balls.
Its integer prefix408674..4086d4 copies25DWORDs from the last canonical record,
decrements46c67c and marks the unused record5. Original epilogue4089cb..4089d4
restores six registers/64stackbytes and returns. Both oracle and native now
execute that exact prefix/epilogue at50Hz, independently of lamps enabled.
Without it, a lost ball stayed state5/count2; with it, count1 and normal return
are observed. Subsequent original x87 render XY/visibility/sorting are excluded;
800-byte equivalence is the declared integer-oracle boundary, not full original
raster state. Independent original-byte/source review confirmed cuts/stack.

Proof:6400 Crocodile+2508 miss=8908steps, uninstrumented fresh original replay,
native reset and SDL exact for100firstballbytes AND all800canonical poolbytes,
864rule/892video bytes,11clock/RNGfields,15lifecyclefields,1920DMDbytes,53lamp
states/50highscore bytes per step. Diagnostic placement modifies only selected
active FREE balls and real DAT layer bindings; no rules, timer, enemy, capture,
score, award or completion injection/stubs. Invalid ball8 and inactiveball1
are rejected; previous captured-ball/profile guards remain green. Source
waypoints default to0, preserving old fixtures. Original aiming/flight uses
only keys; table entry/jackpot/drain trajectories remain diagnostic.

838 additional compiled original instructions (19195→20033), including40
compaction instructions; no new opcode handlers or shared Mean changes.
Existing input adapters work. SDL uses original40938c's lowest-ball selection
(exclude state6/fallback) over validated display coordinates, while retaining
its previous viewport offset/clamp; exact original inertial camera not claimed.
Colored DMD/two active balls/occlusion/camera screenshot
build/pirate-crocodile-active.png inspected atstep3200.

Artifacts:analysis/pirate-multiball-island.json,analysis/pirate-multiball-boundary.json,
analysis/traces/pirate-{crocodile,cannon-miss}.json; tools/pirate_multiball_oracle.py
andverify_pirate_multiball.py. Full snapshots/traces/generated code stayunderbuild/.
Build PASS0warnings;18/18 affected CTests PASS101.59s. After final camera edit,
multiball and finite-game SDL CTests2/2 PASS16.19s. Python/JSON and final scope
assertions checked. No Git metadata/formatter; full unrelated suite not rerun.
Next: Storm3-ball release/jackpots/first-slot compaction/return, then Battle/Mutiny.


## PIRATE-MULTIBALL-CAMPAIGN-009 — remaining three modes in one original campaign

VERIFIED bounded integer-oracle/native/reset/SDL. Fresh replay proves the
unchanged6400-step Crocodile prefix; clock/player state then continues through
actual3/4/5 Cave locks, early-fire gate and genuine cannon flight into
Storm/Battle/Mutiny. No ordinal, score, timer, capture or completion writes.
Actual return-lane switches release the next original ball; waiting/parking
uses only explicit free-ball diagnostic positions. Original aiming/flight has
no waypoints. Total25780steps,19380 new after the prefix.

Init432807/4328e3/432a32 and allocator43175e..431782 give3/4/5 active records,
allstate2. Handbooks3/3/4 is a genuine measured discrepancy for this pinned
Windows build; no Amiga equivalence or explanation inferred. Original
436a4a/436b05/436bbd use46e569[5]: pay only lit target, clear it, ALWAYS light
(ID+1)%5. Runtime proves unlit Storm2 lights3 without pay, immediate duplicates
pay nothing, and a full five-hit wrap pays. Cave432d11..1f adds1M without lock.
JP10/15/20M→11/16/21M; controlled totals76/111/146M. Storm additionally collects
one11M jackpot during subsequent original drain/rescue flight; do not mistake
that for a duplicate award. Return totals87/111/146M; final game score377.5M.

Storm entered8075/3balls8826/return12228; Battle14331/4balls15084/return18744;
Mutiny21278/5balls22197/return25700. Nine actual408674 pool compactions all
replace slot0. Observer4086c1 runs AFTER25DWORD copy/count decrement, BEFORE
source retirement; EAX=index,EBP=newcount. Source/destination100byte hashes
equal for3→2→1,4→3→2→1,5→4→3→2→1. Hook-free fresh original replay preserves
every sampled byte/hash; native/reset/SDL match all800poolbytes,864rule/892video
bytes,11clock/RNGfields,15lifecyclefields,DMD1920bytes,53lamps/50highscore bytes
each step. Original post-prefix x87 display XY/visibility/sorting excluded;
this is not full-raster or legal-key-only trajectory equivalence.

Only701 compiled original instructions added (20033→20734); actual dispatch
roots42c8ac,42ca50,42d3e4,42e7dc,42f384 recorded. No native physics, renderer,
input or opcode-handler changes; no runtime CPU decoder or gameplay stubs.
Full original traces/assets/generated bodies stayunderbuild/.

Battle upper-trap4322e9..432339 has a gated3×JP branch, but activation remains
UNKNOWN. Two direct-writer passes42b390..439b00 found Battle init clear43295e
and no reachable Battle arm; known setters4368f8/436d93/436f77 belong other
modes. Do not fabricate this flag. Surplus-lock variants and composition with
all six Adventures remain unproved; core four-mode campaign is the claim.

Artifacts:analysis/pirate-multiball-campaign-island.json,analysis/pirate-multiball-campaign-boundary.json,
analysis/traces/pirate-multiball-campaign.json; tools/pirate_multiball_campaign_oracle.py
andverify_pirate_multiball_campaign.py. Mutiny screenshot
build/pirate-mutiny-active.png inspected atstep22200; overlaps/occlusion can
hide some of the five verified active records. Build PASS0warnings;19/19
affected CTests PASS140.40s, new campaign44.32s. Mean finite five-mode golden/SDL
and all prior Pirate cases remain green. Independent binary/source/evidence
review found no blocker; Python/JSON/pinned-fixture checks pass. No Git metadata
or configured formatter; full unrelated suite not repeated. Next: MagnaTable.


## PIRATE-MAGNA-010 — MagnaTable controls and all twelve nominal rewards

VERIFIED bounded integer-oracle/native/reset/SDL:20 fixtures,40876steps.
Actual Cave lock→left lane layer0switch4(34,468),4374dc arms WORD46e540=400.
No-lock guard/expiry reject admission; top trap(86,10),431d95 consumes46e2dc,
sets active46e542=-1 and intro4659b4=575. Phase stays2. Both held Shift keys
skip the intro via432552..43256c; full idle countdown is separately verified.

434268/434340 set WORD465864/465858 to2/on or0/off and original lamp commands.
Global46b760 links465860→465854→465848. Original409608→40aca8→40ad80 type2
40af63..40afdd computes integer LUT acceleration before position integration.
Left/right descriptors center at94/147,93 with descriptor.z76. Squared distance
includes signed ballfield1C; cutoff9999; original uint16 LUT46c678 minus16,
SAR32(delta*k,5) adds to VX/VY. No new native force equations were invented.
Two1800-step post-release flights use only held keys and remain active with
unchanged score: bothheld ends100.771606,33.167099; leftheld147.963425,76.770065.
Neither earns a reward. Capture bounds apply inside DAT callback43810c;
being geometrically inside that rectangle alone is insufficient.

Original431e77 samples three bytes from existing system+3c, each&127; slots
4659b8 cycle0..2 every26 idle-display calls. Delays0..132 simulation steps
produce all12 prize IDs; no RNG/rule/timer writes. Actual layer1switch2(120,14)
→438210→4380dc table pays Extra Ball, light Extra Ball, light Mode,20M,
Hold Bonus,10M,Ball Saver,5 Cave locks,Mermaid+2M/+3M,Kickback,5M.
Capture sets state3/substate6, clears active/magnets, waits150 original steps.
433b2a writesstate2 at120,14 withzero velocity; same-step remainder givesVY640.
Actual switch2(120,81)→438463 instead runs state7/path46af87→normal without prize.
All12 nominal targets/all3slots verified; already-lit eligibility fallbacks,
inhibition/cooldown rejection and exact geometry boundaries remain separate.

Frozen original schedules independently replayed without hooks; native/reset
and SDL match100ballbytes/all800poolbytes,864rule/892video bytes, clock/RNG,
lifecycle, colored DMD,53lamps andhighscores per step. Original post-prefix
x87 render/visibility/sorting excluded; diagnostic capture is not key-only
reward success. Two natural intervals have no shots after top entry until exit.

Only289 compiled original instructions added20734→21023, observed42d094.
No production physics/render/input/opcode handlers changed, no gameplay stubs.
An initial natural-left fixture redundantly released an already-up right key;
original raw callback changed one rule frame, native Game Actions ignore equal
states. Corrected frozen legal transition schedule and added an early redundant
edge guard; all original/native comparisons retained.19 existing affected tests
PASS; final Magna CTest1/1 PASS. Build0warnings; Python/JSON/pins checked.
Independent bounded review found no blocker. No Git metadata/formatter.

Artifacts:analysis/pirate-magna-island.json,pirate-magna-static.json,
pirate-magna-boundary.json; analysis/traces/pirate-magna-*.json;
tools/pirate_magna_oracle.py,pirate_magna_cases.py,verify_pirate_magna.py.
Private full traces/assets/generated code stayunderbuild/.
Screenshot build/pirate-magna-active.png inspected at2200steps.
Next primary: Treasure Island final admission→jackpots→Super Jackpot→return.


## PIRATE-FINAL-011 — four multiballs + six Adventures + Treasure Island + next cycle

VERIFIED bounded integer-oracle/native/reset/SDL:54760steps; unchanged25780step
four-MB prefix and its Crocodile ancestry. Actual orderKnife→Plank→Sword→Dive→
Monkey→Shark retains cumulative sixflags andMB4; Knife failure/Sword expiry
still countasplayed. No progression, score, timer or completion injection.
Readiness4346b4 checksall6; initializer4330f7 checksfirst5+MB4. Exploratory
firstfive-before-Knife ordinaryarm enteredfinal; that route is not frozen.

Actual upperleft4340ca→433140 enters48380, clearsall6flags/MBcounter,phase4/ID6,
JP15M, queued7. Eight canonical FREE balls at49222, not handbook4; pinned
Windows build only.43683c consumesonlylit target, addsJP toaggregate46e28c
andcollected46e298, armsSJ46e556. Unarmedtoptrap andduplicate rejectpayout;
ball1target4 pays15M.43215d paysaggregate, clearsSJ/aggregate, relightsall5,
keepsphase4. SJ15M,47M,80M verified. Cave432d18 growsJP15→16M; an additional
lit target0 pays16M duringthe capture/release interval and contributes to47M.
Its sourceball isuntraced; do notassign that payout directlytoCave. Five-target
sweepcollects80M andarms80MSJ. Collected284M at50187; actualdrain addsanother
16M, so300M atnormalreturn53428;aggregate16M/SJFFFF retainedasoriginal.

Seven observed4086c1 source/destination100byte SHA pairs proveactualslot0
copies8→7→6→5→4→3→2→1. All800pool/864rule/892video bytes, clock/RNG/lifecycle,
1920DMD pixels,53lamps/highscores matchperstep. Originalx87post-prefix raster
excluded. ReturnselectsAdventure0. Requiredactualreturn-lane switch clears
shared46e560 before newPlank:entry53562/release/completion54679. Continuation
Plankcollected80M ispreservedwithout assigningnewsemantics; isolated30M
fixturestillpasses. WORD46e53e stays neutrallynamed.

Only149 compiledoriginalinstructions21023→21172; observed42bde8/42bed0.
No productionphysics/render/input/opcode changes; nogameplaystubs/runtimeCPU.
Oracle privateentry/return checkpoints support bounded continuation; each
frozen trace independentlyreplayedfromoriginalinitialcontext. Swordwait call
hooks pausedforcost; edgecounts arenotexhaustive, statechecksremaincomplete.

Build PASS0warnings;21/21 affectedCTests PASS155.41s;finalcampaign70.01s.
Python/pins/JSON/contracts/nativevectors checked. Independentreviewfoundno
blocker. Screenshotbuild/pirate-treasure-island.png inspectedat50188; overlap
canhideballs. NoGitmetadata/formatter; unrelatedfullsuite not repeated.
Artifacts:analysis/pirate-final-{island,static,boundary}.json andtraces/
pirate-final-{entry,return,campaign}.json;tools/pirate_final_oracle.py,
verify_pirate_final.py. Assets/fullsnapshots/generatedbodies remainunderbuild/.
Scope:diagnosticcomposition, notlegal-key-onlyfullfinitegame; Magna/finite
GameOver+save+newgame separatelyverified. Next:Pirateaudio viaexistingbackend.


## PIRATE-AUDIO-012 — Original requests → Pirate music/SFX → SDL (2026-10-20)

VERIFIED banks DAT51876/568e8 registered42b4d3..42b4f1:68/55orders,62/53patterns, shared31sample directory.15descriptors464f18..465134 (8direct+7shared); periods160/226/300/452, full64volume. Existing stripped-STIM parser/libxmp/sequencer/two-slot mixer reused with explicit table profiles. No tracker decoder or guessed event names. Read-only compiled call observer preserves original service execution; retained454a64/68 base0/0 is explicitly seeded.

462 original entry-register requests in14fixtures/87304steps (finite basic game,4MB+6Adventure+final campaign,12Magna rewards) match native/reset. Full finite/final SDL event lists exact.38,501,064 native stereo frames across two passes have deterministic nonzero music/SFX.60 actual Retail44b640 gain-LUT/44cc00 mono cases match byteexact across all15real PCM slices/chunks. Explicit fixture gain:6voices/full64/master65536/SFX10; inactive retained mixer does not establish actual global level. Original final stereo/device/tracker PCM timeline excluded. Eight direct descriptors occur in retained requests; shared seven tested as PCM, not claimed as covered gameplay triggers.8c absent in these schedules; existing Mean sequencer cancellation tests retained.

SDL14frame acceptance: device pauses and simulation freezes on focusloss/minimize/P/options; restores with nonempty queue; M pauses only audio; R clears old output/reset state and resumes. Default launcher now audio-enabled; M/--no-audio supported. No physical listening thiscycle.

Verification: `cmake --build build/native --target pirate_audio_probe slamview pirate_session_probe -j3` PASS0warnings. `ctest --test-dir build/native --output-on-failure -j2 -R '^pirate_audio_original_native_sdl$'`1/1 PASS37.32s;43other affected Pirate/audio/Mean/presentation/metadata CTests PASS179.88s (full command inanalysis/pirate-audio-island.json verification). Original refresh and mono oracle PASS; Python syntax PASS. NoGitmetadata/formatter; full configured suite not repeated. Evidence:analysis/pirate-audio-island.json, pirate-audio-static.json,traces/pirate-audio-{events,pcm}.json; private PCM reports/build/oracle/pirate-audio.


## PIRATE-SURPLUS-013 — Five-lock caps and all four surplus multiballs (2026-10-20)

29844 original integer-oracle/native/reset/SDL steps, all100ball/800pool/864rule/892video bytes and clock/RNG/lifecycle/DMD/53lamps/highscores exact. Actual fiveCavecaptures then sixthguard in each mode; real cannon keys/flight, no shots during cannon. Crocodile/Storm/Battle/Mutiny release5actual free balls each; initialJP12.5/15/17.5/20M, Cave+1M,16actualslot0 compactions5→4→3→2→1 and allfourreturns. Original432d66 cap5 and432751/432811/4328ed arithmetic explain surplus2.5M/lock. Existing21172compiledinstructions suffice; no original-rule/physics changes.

Battle upper-trap trajectory19577→19679:46e556 stays0, score312.5M→313M, collectedJP128.5M unchanged. Bounded original write hook saw only43295e Battleclear and432a98 Mutinyclear. Triple-JP admission remainsUNKNOWN; does not prove global unreachability. Intermediate surplus counts and legal-key-only whole-game remain outside proof. Ramp waits include incidental other-ball jackpots; aggregate changes are not attributed to an invented single event.

New audio190requests bring total652/15fixtures/117148steps; all native/reset events exact,51,662,268 deterministic nonzero stereo frames perbus across two replays. Prior finite/final SDL audio sequences and focus/minimize/pause/options/mute/reset acceptance still pass. Bounded60originalmono cases retained; full original mixedPCM/physical listening unclaimed.

RE speed evidence: same1000initialsteps nohooks0.070s, broadcallhooks9.402s, wordwritehook0.088s. Surplus now gathers calls only on selected event steps; long waits/parking unhooked. Every step state still independently replayed from original reset. Approximate host timings, not universal performance promises.

Verification: warning-free affected build; `ctest --test-dir build/native --output-on-failure -j2 -R '^pirate_multiball_surplus_native_sdl$'` PASS37.68s; extended `ctest --test-dir build/native --output-on-failure -j1 -R '^pirate_audio_original_native_sdl$'` PASS43.62s;43prior affected CTests remainPASS. New500k/unchangedJP contract checked against already verified fulltrace. Python/shell/JSON checked. NoGitmetadata/formatter/fullsuite run. Evidence:analysis/pirate-surplus-{island,static,boundary}.json,traces/pirate-multiball-surplus.json,pirate-re-performance.json. Private fulltraces/screenshots underbuild. Next:MagnaTable eligibility/fallback rewards.

PIRATE-SURPLUS-013 visual/check delta: build/pirate-surplus-fiveballs.png inspectedat4516steps (diagnostic label, original playfield/flippers/lamps/colored DMD); overlap/offviewport limits visibleballcount. --no-audio4frame capture passes. Final15case original audio refresh checks every retained row unchanged; eventfixture idempotent.


## PIRATE-MAGNA-014 — Earned fallback gates and key-only Magna reward (2026-10-21)

Four new original/native/reset/SDL fixtures64560steps: already-lit mode (raw7,slot0)→20M; all6played/unlit mode (raw5,slot0)→20M after frozen48328step final-earned prefix; earned HoldBonus→Crocodile→newCave→Magna(raw37,slot1)→10M; earned Kickback→same actualreentry(raw100,slot2)→5M. Eligibility flags earned by original events and preserved, not injected. Original selection431eba/431f44/43202a is ordered-threshold fallthrough; HoldBonus field is WORD[player+0x14] (20 decimal), ambiguity in older static artifact corrected. Delays searched in cloned OriginalVMs; published schedules independently replay from reset and prefix vectors match retained source.

63bounded native policies find natural reward: frozen diagnostic admission through toptrap1209, release1352; bothShift OFF1352→ON1472→OFF1592→ON1712; actual original state3/sub6 capture1820, releasekeys1820, original return1970/state2/active0/(120,14)/vy640. Source468-step free flight uses only legal keys; +5M actual selectedid11, not injected completion. Full2052step original/native/reset/SDL exact.25totalMagna fixtures/107488steps. No additional originalinstructions (21172) or new physics rules. Reproducible CMake targetpirate_magna_key_search; fixture is frozen, search not needed at runtime/test.

All sampled100ball/800pool/864rule/892video bytes and clock/RNG/lifecycle/DMD/lamp/highscore hashes exact perstep. New audio extension20fixtures/1015requests/183760steps,81,038,160 deterministic nonzero stereo frames perbus across two native passes;60originalmono cases retained. Full OriginalmixedPCM/physical listening outside proof.

Full CMake-j3 PASS0warnings; eligibility CTest1/1 PASS77.71s;8regressions PASS70.30s (key-only3.10s,20oldMagna60.66s,extendedaudio58.09s,finitegame12.21s,Mean5modes5.48s,3metadata). Exact commands inanalysis/pirate-magna-completion-island.json; Python syntax checked. Screenshotbuild/pirate-magna-key-reward.png inspectedat1820, original threecandidate DMD and diagnostic-entry label. NoGitmetadata/formatter/fullsuite run. REA connected/no target open; Ghidra notconfigured, retained Capstone/Unicorn fallback used without setup changes.

Scope: table entry still diagnostic; only Magna flight/capture/return key-only. All-played uses slot0; later selector/display priority, exact geometry/inhibit/cooldown remain separate. Evidence:analysis/pirate-magna-completion-island.json,magna-eligibility-static/boundary,magna-keys-boundary; traces/pirate-magna-{mode-lit,bonus-held,kickback-lit,all-played,key-reward}.json. Next:Nudge/Tilt routing, currently absent from Pirate frontend despite shared option bindings.


## PIRATE-NUDGE-015 — Original forces, SDL keys and finite Tilt recovery (2026-10-21)

Retail4049e3/404a25/404a67 request Up/Left/Right;405eec adds40 to46c6e4 except phase<=1/phase3/alreadyTilted.20ms decay1; observed counters40→79(warning)→118(Tilt), table4344c8 arguments0/1. Pending waveform is still admitted afterTilt. Existing compiled4070bc/405234 supplies physics unchanged. CommonTilt releases454b58/5c/60 and clears held latches; warning42bd08 blinks original DMD asset. Table callback selects music33; Knife video exits, rule timers skip, ordinary bonus skips, next-ball408410 clears46b764. Static addresses inpirate-nudge-table-static.json; dynamic proof below.

12independently reset-replayed original fixtures/45844steps:3directions, standalone warning/expiry, decay, prelaunch, ordinary finite Tilt game, Knife, free/held Magna and free/held Crocodile. Full100ball/800pool/864rule/892video bytes, clock/RNG/lifecycle/DMD/lamp/highscore hashes plus18nudge fields match native/reset/SDL every step. Mode admission uses frozen diagnostic physical prefixes; all post-entry Nudge/drain/recovery uses original simulation and actions only. Native finite game resumes atball2 with clearedTilt. Extra original service edges438b85→40ac08 and433cca→40ab64 now compiled; total21172→21467(+295), no invented force/capture rules or stubs.

Actual SDL injected keys prove defaultAlt/Space and remappedZ; repeat/key-up/focus/pause/options/minimize gates. Warning screenshotbuild/pirate-nudge-warning.png visually inspected at696steps. Original screen shake and physical host/desktop Alt interception remain unverified. An early test duplicated already-held Magna Shift-down; generator preserves inherited held state now, all state checks retained.

Audio extended to32fixtures/1172original requests/229604steps; native/reset exact with101255364deterministic stereo frames across two passes; four SDL event sequences include ordinary and held-MagnaTilt. Original mixedPCM/physical listening remain separate. SHA-pinned event rows reused only for unchanged replay files; changed/new replay rows execute original handlers again.

Final CMake-j3 PASS0warnings; new Nudge+audio CTests2/2PASS70.81s. Five separate regressions PASS: Pirate final72.04s, complete game12.45s, Magna keys3.20s, MeanNudge1.73s, options.13s. Earlier new-fixture failure in regression log is superseded by final2/2run. Python syntax/JSON/SHA links checked; noGitmetadata/formatter/fullsuite. REA provider limitation retained; bounded Capstone/Unicorn fallback, no setup changes. Exact commands/reports/scope:analysis/pirate-nudge-island.json. Next:Battle triple-Jackpot arming via actual events.


## PIRATE-MULTIBALL-016 — Complete bounded lock-count matrix (2026-10-21)

Crocodile3/4locks start7.5/10M; Storm4starts12.5M. ActualCave +1M, first/raised JP,3/4original balls and eight slot0compactions→single-ball return.3new original/reset/native/SDL fixtures/26876steps exact. SHA-pinned minima/maxima complete all10legal ordinal/lock combinations; no engineinstructions added for matrix. Diagnostic physical entry/parking remains explicit. CTestpirate_lock_matrix_native_sdlPASS47.57s. Evidence:analysis/pirate-lock-matrix-island.json.

## PIRATE-LEGAL-017 — Natural Cave game and ordinary DMD/bonus continuations (2026-10-21)

Native88policy/488721step/60s search finds3naturalCave locks but43unsupported-call stops. Freeze error-free off/left16step policy; original keyboard run independently proves locks1317/4517/7717 on successive balls, score5.145M, ABC admission9616, GameOver10080/freeze64, F110144 resets locks/score and preserves records; free second-game ball11517.11600steps original/reset/native/SDL exact, zero diagnostic shots.

First7missing targets proven at exact original Native-failure boundaries; full407c09 DMD dispatch watch exposes successor42dc64 too. Compile actual routines, second87policy/685581step/60s native search passes40former failure points and exposes3later display targets42e478/42e718/42d640; independently original-prove/lift those too. Total10DMD callbacks+406650 through43522f/service+54,917extra instructions(21467→22384). No new forces/rules invented.11legal-key fixtures/65068steps now match100ball/800pool/864rule/892video bytes plus clock/RNG/lifecycle/DMD/highscore/lamp hashes every step, including independent native reset and SDL. `--full-state-trace` enables complete hashes without a diagnostic waypoint source. DMD captures inbuild/pirate-legal-feedback-dmd.png inspected; ShootMagnaTable and MermaidBonus visibly restored.

Battle3× investigation: handbook Battle section(PDFzero16/printed18) has no such activation rule; nearby SuperJackpot text is TreasureIsland.15direct absolute gate uses in42b390..439b00:3nonzero setters guarded by TreasureIsland/Plank/Dive,8clears,4reads. Every overlapping46e556 write observed across retained4/5lock campaigns;8770Battle steps stay unarmed. Alias/external writes or other paths remainUNKNOWN; do not invent an arm or treat it as a demonstrated handbook requirement. Evidence:analysis/pirate-battle-{handbook-contract,writers}.json,traces/pirate-battle-gate-original.json.

Build-j3PASS0warnings; legal11fixtureCTestPASS75.38s; Nudge67.49s,completegame12.76s and prior43audio90.65s pass. Final46audioCTestPASS90.26s:321548steps/3567deliveries(46synthetic retained base +3521actual original entries),141802668deterministic native stereo frames overtwo passes.60original monoPCM fixtures retained; no new final-original-mix equivalence claim. Python/shell/JSON/SHA checks and manual source review; noGitmetadata/formatter/fullsuite. REA provider unavailable as previously recorded; cached Capstone/Unicorn used, no setup changes. Native searches are bounded discovery, not all-path guarantees. Original x87 raster/physical host/listening and complete legal all-mode game remain outside proof. Next:legal-key-only Crocodile entry from earned locks. Detailed commands/cases/scopes:analysis/pirate-legal-gameplay-island.json.


## PIRATE-NATURAL-018 — Key-only Crocodile jackpot and finite game (2026-10-21)

Reachable silent native snapshot after unchanged verified5400-step Cave prefix.679input continuations/314769steps/30.71s find bothShift5574→5582(40ms), then release and freshLeft6168→6169 at originalangle2024. Snapshot is only an offline search shortcut; original proof and native/reset/SDL verification start fresh and replay frozen keys, no checkpoint/ball/velocity/rule/timer injection.

Fresh original confirms Cave locks1317/4517; Cannon5805; Crocodile6351/5M JP; twoactual freeballs7090; naturallycollected5M JP7623; original canonical2→1compaction9432; normalreturn11112. Continueactual three-ball game:15.83M/ABC/GameOver14240, freeze64, F114304 retains highscore and resets locks/played/score; free next-game ball15519. Full15600steps and independent original reset replay exact. Native/reset/SDL match all observed100ball/800pool/864rule/892video bytes and clock/RNG/lifecycle/DMD/highscore/lamp hashes. No new gameplay instructions(22384unchanged).

Targeted binary/DAT gate evidence: layer0switch3 edge has34validpixels around88,12; cooldown/noTilt/noother uppercapture required. After50-step hold, Magna can take precedence when46e2dc!=0 and signed46e540>=0. Otherwise signed locks-played>=2 admits Cannon; ready65→−1 takes264steps; freshShift fires actual ballistic path. Detailed source addresses/region hashes:analysis/pirate-natural-cannon-gates.json.

Full build-j3PASS0warnings; natural15600stepCTest18.05s and47caseaudio95.61s,2/2PASS95.62s. Audio233new original requests;47fixtures/337148steps/3800deliveries include47retained base deliveries and3753actual service entries,148682268deterministic stereo frames overtwo native passes; prior46rows preserved. No finalOriginalmixedPCM/physicalhost claim. Screenshotsbuild/pirate-natural-croc{,-jackpot}.png inspected: actual table/ball/lamps/DMD transition frames, no diagnostic label. Python/JSON/SHA checks and source reviewed; noGitmetadata/formatter/fullsuite. REA provider remains unavailable; retained Capstone/Unicorn fallback used without setup changes. Scope/details/commands:analysis/pirate-natural-croc-island.json. Next:natural Walk the Plank using reached-state input search, then fresh original/native/reset/SDL proof.


## PIRATE-NATURAL-019 — Natural Plank admission/drain and ordinary DMD continuation (2026-10-21)

35native key policies/329235steps/28.40s find rightShift ON/OFF each40steps. Real layer0switch2 ramp ingress→layer1switch3 arms46e2de at1750(selectedAdventure4); ordinary bumper selection later cycles toPlank0. Upper-left guide24/capture5 reachesphase5 at4104, five rope flags1/timer12828; original intro releases at4932/timer12000. Natural drain6093/phase3/timer10839, score6.08415M→ABC→GameOver10240/freeze64→F110304 resets played/locks/score, retains records→free second-game ball11519.11600fresh original+independent original reset+native/reset/SDL steps exact for all nine observed vectors. No waypoint/checkpoint/ball/velocity/rule/timer writes in proof. Natural Plank title/table screenshotbuild/pirate-natural-plank.png inspected.

Search also exposes unsupported ordinary DMD42e140 at9063. Actual407c09 indirectcall bytesff159cc64600; fresh original proves201entries through9863, contextcounter0..200 and original draw services.10344key-only steps independently replay exact, full bounded callback compiled142instructions (22384→22526). Outsidecall boundary unchanged; no stubs or new physics/rule semantics. First feedback generation lacked policy offset metadata; zero-offset search handled explicitly, corrected generation passed. Callback title semantics not inferred; screenshotbuild/pirate-natural-feedback.png is a DMD transition.

Two separate reachable-state rope searches at5400/5600 tested1216branches each,495878/292567steps,49.76/28.96s, no rope. These are bounded negative results, not evidence of impossibility. Retain best rightShift5696..5720 trajectory and change observation point next; no repetitive third sweep.

Final build-j3PASS0warnings. Five CTests-j2PASS120.72s: naturalPlank12.95s, naturalCroc17.29s, prior diagnosticPlank20.09s, legal12fixtures/75412steps87.67s, audio49fixtures95.59s.49audio cases/359092steps/4351deliveries(49retained base+4302actual service entries); prior47event rows preserved,549new actual entries. Native/reset158359572deterministic stereo frames,60original monoPCM cases retained; original finalmixedPCM/physical listening remain outside proof. SixPython syntax checks,49audio replay SHA links and compact source/artifact review PASS. NoGitmetadata/formatter/fullsuite. REA native provider unavailable as previously recorded; cached Capstone/Unicorn reused without setup changes. Evidence:analysis/pirate-natural-plank-island.json,natural-plank-gates/boundary,natural-feedback-boundary;traces/pirate-natural-plank-game.json,pirate-legal-feedback-42e140.json. Next:natural Plank rope collection from a new actual contact/flight observation.


## PIRATE-NATURAL-020 — Two natural Plank ropes and finite recovery (2026-10-21)

Read-only native flight inspection changes observation point: right5696..5720 reaches actual Cave/upper return, then free lower contact around6664. Left6664..6688 earns rope4at6763; freshLeft7128..7136 earns rope3at7298. Original436c78 clears flags to[1,1,1,0,0]; each hit gives10Mrope+250kbase and400timer ticks (timers10569/10434). Actual10.25M per-step deltas verified from packedBCD lifecycle bytes. Native first hit exposed missing407c09→42ee48 DMD. Full original simulations execute104/208dispatches;106original instructions added,22526→22632, outsidecalls unchanged/no stubs/no invented physics.

Two frozen legal-input cases12800/13400steps independently replay fresh original twice, then native/reset/SDL all nine observed vectors exact, including full800ballpool/864rule/892video bytes through hashes. Finite scores17.53415M/28.18415M; ABC/GameOver11440/12044, stable64, F111504/12108 resets played/score/locks and retains records, free second-game balls12719/13319. Shared5600-step base prefix remains byte/hash-exact. No checkpoints, diagnostic waypoints or rule/timer/score writes in proof.

Native discovery: first contact913branches/389566steps/34.48s finds rope4 but stops at then-missing DMD; second229branches/97287steps/8.99s reaches two ropes. Third-goal913branches/318547steps/29.48s at7600..7900 finds no new distinct rope; bounded negative, not impossibility. Change next steering/contact observation rather than repeat that sweep. Both ramp hits include250kbase; semantic contracts retain that actual10.25Mdelta.

Final build-j3PASS0warnings; Total Test time (real) = 107.17 sec. Four affected CTests pass: prior diagnosticPlank20.34s,naturalCroc17.83s,naturalPlank3cases43.96s and51caseaudio.51audio fixtures/385292steps/4574deliveries(51base+4523actual), prior49event rows preserved;223newdeliveries include221actual entries.169913772deterministic stereo frames/native two passes;60original monoPCM cases retained, no finalOriginalmixedPCM/physical listening claim.4Python syntax/51audioSHA checks and source/artifact review pass. Screenshotbuild/pirate-plank-natural-rope.png inspected. NoGitmetadata/formatter/fullsuite. REA native provider remains unavailable; cached Capstone/Unicorn retained without setup changes. Evidence:analysis/pirate-plank-natural-ropes-island.json,pirate-plank-{rope,two-ropes}-boundary.json,traces/pirate-natural-plank-{rope,two-ropes}.json. Next:natural third distinct Plank rope.


## PIRATE-DISPLAY-021 — Original Nudge scene motion and six actual DMD messages (2026-10-21)

Actual x87render405486..4054e1,clamp4035af andCOMsourceRECT402e58 prove sceneoffset=-horizontalPixels/negativecameraPlusVerticalFixed,sourceXborder8,Yclip0..maxScroll+8.63contexts from pinned Nudge traces match nativehelper. All table/lamp/flipper/ball destinations share offset;DMD/options fixed. Existing native camera policy retained;no fullraster claim. All12Nudge/Tilt SDL frame origins and statevectors pass.

Two native Nudge searches2591branches/1320332steps found no third distinct Plank rope, so stop that low-yield approach. Freeze a genuine LeftAlt7740..7741 route: two ropes→drain7852→28.18415M/ABC/GameOver12044/F112108/free nextball13319.13400original/reset/native/reset/SDL steps exact;96×18Nudge fields7741..7836 match, maxcounter40/noTilt, actualhorizontal pixels-2..0.

Bounded static DMD audit finds57push/service+34 registrations/43targets,10uncompiled. Wait original DMDidle,then actual known Adventure events:42f0cc/42f130Swordfight,42f3e8/4300b4Dive,42f6ec/42f800Monkey. Allsix dispatch naturally onfirstattempt;no priority/rule/timer/score/callback writes. Three diagnostic free-ball fixtures3012+2532+6580=12124steps independently original-reset/native-reset/SDL exact9vectors;messages have complete observed lifetimes/distinctDMDframes. Compile695original instructions,22632→23327, outsidecalls unchanged/no stubs.39of43enumerated targets compiled;4remaining static only, computed targets excluded.

Final build-j3PASS0warnings; Total Test time (real) = 122.26 sec;5/5affected CTests pass (scene63,Nudge12,naturalPlank4,feedback3,audio55).55audio cases/410816steps/4722deliveries(55base+4667actual),prior51rows retained;new4cases148deliveries include144actual entries.181169856deterministic stereo frames/native two passes;60original monoPCM cases retained,no finalmixedPCM/physicalhost claim. Python/sourcefixture/SHA checks and finalsource review pass;noGitmetadata/formatter/fullsuite. REA native provider still unavailable;cached Capstone/Unicorn reused. Visual capturesbuild/pirate-nudge-scene.png andpirate-monkey-feedback.png inspected (Nudge scene/Monkey coin animation). Sources:analysis/pirate-feedback-display-island.json,nudge-presentation,mode-feedback-island,dmd-next. Next:four remaining registered DMD messages as one event-admission bundle.


## PIRATE-FEEDBACK-022 — Four remaining direct DMD callbacks and LeftCtrl Magnasaver (2026-10-21)

Actual25th ordinary ramp increments player+0c,43534a doubles threshold25→50,435366 pendingExtra+1;42c42c dispatch124times. Actual material5target pair/righttrap earns46e536; original default prefix40df1e..40df5f bindsLeftCtrl1d, real404ab4→4341dc consumes earned state at1201 and enables46584c/window200/lamp4. Original4355ef expires record/window/lamp at2004;42e41c dispatch151times. This is standalone Magnasaver, not PiranhaPops. RightCtrl descriptor+50→434264 is ret/noop. Actual stackret/Capstone edge recorded, no manually invented root.

TwoSkull ramps arm bonus multiplier, righttrap collects1→2 with42c03c/355dispatches. ThreeMermaid targets earnKickback, actualrightoutlane consumes1→0 with42e5bc/129dispatches; earlier uppertrap hypothesis superseded. Fourfixtures1840+2084+3496+1684=9104steps independently original-reset replay then native-reset/SDL exact all9vectors. Explicit free-ball DAT waypoints; no rule/score/timer/phase/priority/callback injection. Physical left-outlane force/rescue not newly compared.

Compile580originalinstructions23327→23907, outsidecall boundary unchanged/no stubs.43/43targets in bounded57immediate-push registrations now compiled; computed/register-pushed targets remain outside enumeration. SDL exposes seventh configurable Left special(defaultLeftCtrl), preserving all six-key profile mappings/settings with free fallback onCtrl conflict. Actualkey events prove six admitted calls, remapZ, repeat/up/focus/pause/options/minimize gates and unboundRightCtrl;40simulationticks. SharedMean frontend regression passes.

Fullbuild-j3PASS0warnings;7/7affectedCTests-j2PASS106.47s (newfeedback13.29s,priorfeedback15.90s,finitegame12.22s,Meanfrontend.61s,options.12s,specialSDL.40s,audio106.47s).59audiofixtures/419920steps/4752deliveries(59base+4693actual), prior55rows preserved.185184720deterministic native stereo frames overtwo passes;60originalmonoPCMcases retained. Additional actualSDL LeftCtrl2084steps gives exact9audio requests/20480queuedbytes. OriginalfinalmixedPCM/physicalhost unverified. Native Magnasaver title and multiplier coin animation captures inspected. SixPython/shellsyntax,59replaySHA links,5newboundedroots and source review pass; noGitmetadata/formatter/full unrelatedsuite. REA native provider unavailable as recorded; cached Capstone/Unicorn reused withoutsetupchanges. Sources/commands/scopes:analysis/pirate-final-feedback-island.json,a/bboundary/evidence,entry-verification;traces/pirate-final-feedback-*.json. Next:actual left-outlane Magnasaver force/rescue and expiry/Tilt/rearm guards.


## PIRATE-MAGNASAVER-023 — Physical ball save, expiry/rearm and Tilt boundaries (2026-10-21)

Actual original force40ad80 reads linked descriptor465848/typeWORD46584c=FFFF. Paired fresh-reset fixtures share1200steps and samefree-ball entry25,530/zero velocity; only realLeftCtrl differs. Inactive crossesY600 by1401 (later other-rule rescue is not called permanent drain). Active firstforce1201 changesVX/VY0/0→95/−1012, reachesY405.7785 at1400, then settles near417.8.804actual force applications through2004; original expiry clears record/window. Four-candidate bounded original checkpoint search finds leftShift2200..2320; fresh-reset proof preserves unchanged active prefix through2004, then ball crossesY400 at2327, reaches175.261/377.9184 at2400 and staysfree through2800. No waypoint after1200; no force/rule/timer/phase/Tilt injection. Diagnostic initial entry, not natural all-key admission or arbitrary guaranteed rescue.

Uncharged repeatedCtrl does not extend original expiry2004. Actual targetpair/righttrap reearns whileactive;Ctrl1463 reloads200,expiry2264:201eligible50Hz calls with engine-phase quantization, not universally804elapsedsteps. Tilt40ad8b/40ad92 rejects force;43541f/435428 skips countdown. Active recordFFFF/window186 remain frozen; lastforce1256, no influence afterTilt. Armed inactive charge cannot activate whileTilt. Actual phase1 nextball435718 resets earned0/windowFFFF/force0/Tilt0; subsequent ball launch runs. Exact bytes/static guards:analysis/pirate-magnasaver-guards.json.

Sevenfixtures1880+3680+2160+2344+4480+4480+2880=21904steps independently original-reset then native-reset/SDL exact all10vectors. Five additional raw fields WORD46e536/WORD46e552/WORD46584c/BYTE46e450/DWORD46b764 are collected only for full-state/diagnostic tracing; native reset checks them too.23907compiled instructions unchanged, outsidecalls unchanged/no stubs. No gameplay rewrite needed; existing bounded force/rule implementation passes.

Build-j3PASS0warnings;5/5affectedCTests-j2PASS115.80s:Magnasaver30.16s,priorfourfeedback13.11s,finitegame11.96s,specialSDL.39s,audio115.79s.66audiofixtures/441824steps/4854deliveries(66base+4788actual),prior59rows preserved;194844384deterministic native stereoframes/two passes,60originalmonoPCMcases. SDL activeMagnasaverTilt audio events exact; finaloriginalmixedPCM/physicalhost listening unverified. Pull/return SDL screenshots inspected. Python syntax/66audioSHA/sourceJSON/review pass;noGitmetadata/formatter/unrelatedfullsuite. REA native provider unavailable as recorded;cached Capstone/Unicorn reused withoutsetupchanges. One initial expiry assertion assumed phase-aligned804steps; corrected to exact201service-clock boundary after original1463→2264 observation, all state comparisons retained. Sources/commands/scopes:analysis/pirate-magnasaver-island.json,boundary,guards,traces/pirate-magnasaver-*.json. Next:separate MagnaTable capture eligibility/inhibit/cooldown boundaries.


## PIRATE-MAGNA-CAPTURE-024 — Genuine trigger, admission and occupied/cooldown/Tilt boundaries (2026-10-21)

Original43810c compares signed16.16 rectangle40<x<=200,y<=49capture or49<y<=89exit, but DATswitch2central footprint onlycapturey10..17/exity81..87. Exactx40/x200/y49directsamples do not call route. Collision can move initialwaypoint before switch lookup; no routine-call injection to fake boundary coverage. Runtime120,18→17 and120,80→81 prove outside/inside capture andexit. Existing frozen1355stepMagna prefix preserved9vectors.

Capture150calls releases1506 with465a68=10; zero1544 stillrejects;−1at1548 permits capture1549. Diagnostic re-placement afterrelease observes original route does not test activeflag; repeated5M is not claimed ordinary repeated-mode entry. Tilt rejects newcapture yet exitclears active/magnets; heldreward Tilt releasesearly with142remaining hold/no cooldown10 andretainsaward. Armed1209prefix: toptrapinput2760→431d95at2812 withwindow0 admits;2761→2813 withFFFFrejects, due52step capturewait and50Hzexpiry ordering.

7fresh original/reset/native/reset/SDL fixtures1588+1540+1780+1552+1448+3088+2944=13940steps exact all9vectors. Additional42bae4(6,465a68) leaf invocations atactual1355/1356/1506/1544/1548 contexts return1/0/0/0/1; actualheldstate3/sub6rejects, releasedstate2/sub6isnotoccupied. Native sameprivateSHA-pinned contexts twice, memoryunchanged. No fabricatedsecondball; staticstate6guard separate from runtimecases.23907instructions unchanged/no stubs/no rule/timer/phase/force/callback writes.

Build-j3PASS0warnings;5/5affectedCTests-j2PASS118.40s (prior20Magna60.46s,finite12.10s,newcapture20.22s,leaf.45s,audio118.40s).73audiofixtures/455764steps/4953deliveries(73base+4880actual),prior66rows preserved;200991924deterministicnative stereoframes/two passes;60originalmonoPCM retained. ExtraSDLheldTilt/cooldown eventstreams exact; finalOriginalmixedPCM/physicalhost notclaimed. Python syntax/73replaySHA/guard sourceSHA/sourceJSON review pass;noGitmetadata/formatter/unrelatedfullsuite. REA provider unavailable as recorded; cachedCapstone/Unicorn reused. Sources/commands/scopes:analysis/pirate-magna-capture-island.json,guards,boundary,traces/pirate-magna-capture-*.json. Next:composed finalcampaign→finite GameOver/highscores/F1, withno postprefixwaypoints.


## PIRATE-FINITE-CAMPAIGN-025 — Composed campaign→natural finite ending/highscore/newgame (2026-10-22)

Bounded Original discovery5.627s reuses unchanged54760step finalcampaign context:4multiballs,6playedAdventures,TreasureIsland8balls,nextPlank. Only13Enter/ABC/F1actions follow; no further waypoints or statewrites. Ball2phase1at56344,ball3at59176; ABCadmission62176,scansA62176/B62180/C62184/Enter62188; GameOver62640 score1,486,839,210 packedBCD001486839210 andASCIIABC inoriginal50bytehighscores. Stableball/phase64steps; newgame62704 preservesallrecords andresets score;Enter62800→freeball62910. PlayedAdventures include original failure/timeout paths, not allsixwins.

Fresh Original generator comparesall9vectors everyprefixstep, retainsallprefixmilestones/inputs/shots, then independently replaysfull62992steps fromreset. Native/reset/SDL all9vectors exact throughending/restart; highscorehash/pool800/rule864/video892bytes preserved.8232continuationsteps include final80/alignment; no checkpointrestore inproof.23907compiledinstructions/outsidecalls unchanged/no stubs; existingnativeengine handlescompleteboundedchain. MagnaTable andstandaloneMagnasaver remain separatelyverified, notpresent inthis samecampaign. Diagnosticprefix scopeexplicit; fully legal-key-only all-mode trajectory/whole originalraster/physicalhost remain outsideproof.

Finalbuild-j3PASS0warnings;3/3CTests-j2PASS148.15s:campaign78.70s,capture7strengthenedcases20.45s,audio148.14s. Earlier5/5affectedPASS118.40s retainsprior20Magna/finitegame/5actualcontextleafchecks.74audiofixtures/518756steps/5221deliveries(74base+5147actual),prior73rows preserved;newcampaign268deliveries includes267actualentries.228771396deterministic native stereoframes/two passes;60originalmonoPCMcases retained. Fullnew62992step SDLcampaignaudio requests exact; originalfinalmixedPCM/physicalhost listening notclaimed.8Python syntax/74replaySHA/JSON/source reviews pass;noGitmetadata/formatter/unrelatedfullsuite. REA provider unavailable as recorded;cachedCapstone/Unicorn reused withoutsetupchanges. Sources/commands/scopes:analysis/pirate-campaign-finite-island.json,boundary,traces/pirate-campaign-finite.json;tools/pirate_campaign_finite_{probe,oracle}.py,verify_pirate_campaign_finite.py. Next:combinebothMagna systems into same finitecampaign.


## PIRATE-MAGNET-CAMPAIGN-026 — Both magnet systems in composed finite campaign (2026-10-22)

Retainall54760existing4multiball/6playedAdventure/TreasureIsland prefix vectors/milestones/inputs/shots. ActualCave54761 enablesMagna,lane55005/toptrap55006 admits55057. BothShift type2[2,2],independent[2,0]/[0,2],actualrewardcapture55152 selectsID9/slot0:Mermaidbank1M→4M,not immediate3Mscore;150step release55302. Actualpairedmaterial5targets/righttrap earnstandalone55485;LeftCtrl55486 consumescharge/reloads200; actualfreeball25,530 islastwaypoint55486.802original forceapplications55487..56288;Y405.7785after200steps,originalexpiry56288. LeftShift56486..56606 returnsballaboveY400,remainsfree through57086. No later placement.

Naturalfiniteending:ABC64576..64588,GameOver65040 score1,498,782,380/packedBCD001498782380 andABC;freeze64,F165104 preservesrecords/resets score;newfreeball65310. Total65392steps includes final80/alignment.23postprefixkeyevents/11freeballwaypoints,then9905key-onlytailsteps. Discovery74orderedoperations/40snapshots recomputedfresh,notblindcopied; complete fresh original reset/native reset/SDL all10vectors exact. Existing9vectors plus5fieldMagnasaver perstep; compactpublicfixture keepsvectorSHA,fullvaluesprivate. No force/rule/timer/phase/callback injection; diagnostic wholecampaign scopeexplicit,not allkey-only/all6wins.23907instructions/outsidecalls unchanged/no stubs.

Build-j3PASS0warnings;4/4CTests-j2PASS182.02s:priorfinite78.45s,specialSDL.37s,newcombined82.29s,audio182.02s.75audiofixtures/584148steps/5503deliveries(75base+5428actual),prior74rows preserved;newcampaign282deliveries includes281actualentries.257609268deterministic native stereoframes/two passes;60originalmonoPCM retained. Fullcombined65392stepSDLrequests exact; originalfinalmixedPCM/physicalhost listening notclaimed.5Python syntax/75audioSHA/probeSHA/sourceJSONreviews pass;noGitmetadata/formatter/unrelatedfullsuite. REA provider unavailable as recorded;cachedCapstone/Unicorn reused withoutsetupchanges. Sources/commands/scopes:analysis/pirate-campaign-magnets-island.json,boundary,traces/pirate-campaign-magnets.json;tools/pirate_campaign_magnets_{probe,oracle}.py,verify_pirate_campaign_magnets.py. Next:bounded variedlegal-input Pirate acceptance andoriginalproof onlyforconcretefailurepoints.


## PIRATE-ACCEPTANCE-027 — Legal-input repeated games (2026-10-22)

Observed24deterministic native policies/520244steps:48GameOvers/48F1 restarts,32tailinitials admissions,201tailNudges,zero native errors. Four frozen legal seeds reused with SHA pins; no free-ball placement or rule/phase/score writes. No earned Magnasaver observed; prior023/026proof retained. Source policies, percase scope and hashes: `analysis/pirate-acceptance-island.json`.

Three frozen candidates independently executed and fresh-reset replayed in original Retail, then native/reset and SDL: Nudge16792steps; Tilt19992; naturalCrocodile25792. All10vectors exact62576steps. Six GameOvers freeze canonical100ballbytes/highscore records at least64steps; real408ae0 F1 preserves highscore and original clock/RNG; third free ball verified before final80step padding. Actual admitted405d54 ABC only; 40404c input and405234step. Diagnostic shots empty throughout. Wide native sweep is not24original equivalence or exhaustive all-mode acceptance; inheritedx87raster omission remains. No gameplay modifications/23907original instructions unchanged.

Implemented `tools/pirate_acceptance_sweep.cpp`, original fixture generator and `verify_pirate_acceptance.py`; new CTest. Cursor optimization reproduces first2frozen candidates byte-for-byte. Warning-free fullbuild; acceptance+priorcampaign CTests2/2PASS83.49s; specialfrontendPASS. Commands, audio followup and limitations in evidenceJSON. NoGitmetadata/projectformatter; unrelatedfullsuite not rerun. Next: original frame evidence for Pirate dynamic-object presentation, then implement only confirmed missing objects.

027audiofollowupPASS:78fixtures646724steps6132deliveries(78base+6054actual);75priorrows unchanged,629new deliveries.285205284deterministicstereoframes/twopasses;60originalmonoPCMcases retained. Selected naturalmultiball SDL eventstream exact; existing affectedstreams/frontend pass. AudioCTest198.81s; total4/4affectedtests acrossseparatebatchesPASS. ThreePython syntax,78audioSHA pins and3sourcecandidateSHA/input checksPASS. Original finalmixedPCM/physicalhost unclaimed.


## PIRATE-CAMERA-028 — Original camera dynamics in native presentation (2026-10-22)

Bounded original render inventory:403638→405234;4036b7→405590;408ff0→40b518flippers,408f68→40b61clamps,405660→408674ball projection,40b860/40b984ball masking/draw.408da8queue opcode branches dispatch40b0b4/40b2ec descriptor toggles. No extra object family proved; lampdescriptor+0c overlap consumers remain a bounded pixel-test opportunity, not a claim of missing sprites.

Concrete camera gap: SDL usedballY−260 while original409350 reads signed projected WORDYball+12, selects lowest nonstate6/fallback; spring/acceleration cap±0x20000 follows into0..200viewport.409492GameOver halfpixel/tick pan bounces; original mixed-scale position=pan+height/4 preserved exactly.40549a..4054da x87 current/previous interpolation transferred. Fixed native viewport320×400. Newpurepresentationclass never mutates100ballbytes/gamepool/clock/RNG/rules. ActualF1 retainscamera; forcedreset clears it.

9000consecutive original409350states and45000actual405486x87values match C++ exactly, including explicitly synthetic state6/empty/pan branches. Separate actualSDL naturalCrocodile/twofinitegames6448frames/25792steps: freeze preceding rendered projected positions andphase sequence, independently execute original409350/405486, compare sixcamera fields andscroll eachframe. All10prior gameplay vectors stay exact. ActualSDL BMP rendered/PNG visually inspected. No whole original raster, exact scheduler coupling or physicalhost acceptance claim. Sources/hashes/commands:`analysis/pirate-camera-island.json`; two publiccamera fixtures. REA native provider known unavailable; cachedCapstone/Unicorn reused, no setup changes.

028finalverification: fullCMake-j3PASS0warnings;6/6affectedCTests-j2PASS105.02s(cameraOriginal,cameraSDL,Nudgepresentation,12Nudge/Tilttrajectories,repeatedgamesacceptance,specialfrontend). ThreePython syntax andtwofixtureJSON/count/SHA checksPASS. NoGitmetadata/configuredformatter; unrelatedfullsuite/audio not repeated for presentation-only change. Audio code/services unchanged.


## PIRATE-IMPORT-029 — All-angle composition proof and native raw data path (2026-10-22)

Original40b518flipper pixelAND,40b0b4/40b2ec lamp consumers and408da8queue: all27Pirateframes under4lamp patterns produce108native comparisoncases/321792pixels with0RGB/alpha differences. Wholelamp canvas4×192000pixels matches original exactly. All53original lamp masks are pairwise opaque-disjoint; four+0clinks already accounted for by original parent-mask paths. No new pixel bug or extra object family established; do not repeat endpointonly/draw-order investigation. Report:`analysis/pirate-flipper-lamps.json`.

Native importer exactRetail EXE185d5893…+PIRATE.DAT6050b576…+MAIN.DAT: normal PEsection mapping skips rawptr0BSS, copies192000table pixels into image+a0000 and userMAIN into+d0000. All341remaining imageDWORD differences constrained to state52000..6ffff; no code/graphics patches. Runtime startszero,600damage rows plusoneCRT scalar. Fourfiles reproduce existing5c112a97…image/0ddf8440…runtime hashes exactly. Recipe contains scalar startupstate/offsets/hashes only; bounded original postF1snapshot reconstruction,not recovered full loader. Assets stay privateunderbuild.

`slampirate-import` uses existing Mean nativePE/SHA/exclusive staged publication helpers. UnsupportedEXE,missing/corruptMAIN rejected; prioroutput/emptydir/danglingsymlink preserved. Native importer and SDLgame run with PATH=/no-import-tools; no Python/Wine/emulator dependency there (developer harness stillPython). ImportedSDL25792steps match10prior gameplay vectors,6448camera frames and364audio requests. Source launcher --data smoke14frames passes; readybuild/imported/pirate-retail. Exactrevision only; source-recipe developer build,not portable package/data chooser yet.

FullCMake-j3PASS0warnings;4/4affectedCTestsPASS20.90s (Pirateimport,allanglecompositor,cameraSDL,Meanimport).3Python syntax/bashsyntax/4outputSHA/recipeSHA pass; expandedreport rerunPASS. NoGitmetadata/configuredformatter; unrelatedfullsuite not rerun. Sources/scopes/commands:`analysis/pirate-import-island.json`,recipe andtraces/pirate-import-acceptance.json. REA cachedCapstone/Unicorn reused; nativeproviderknownunavailable,no setup changes. Next:native Pirate data selection andasset-free package.


## PIRATE-FIRSTSTART-030 — Native data selection and relocated asset-free package (2026-10-22)

SharedMeanSDLUI compiledforPirate: Retail chooser/drop,asyncnative importer,preparedfolder validation,rememberedpath,invalidselection preservespriorchoice. Separatepirate-data-path.txt/importfolders; Meanpaths untouched. slampirate supports savedselection/--setup/--data/--check. Nativeimporter resolvesbundledrecipe relativetoexe. First packagefiletrace exposed buildRUNPATHsourcechecks; fixedusingCMakePirateRuntime installcomponent with$ORIGIN/../lib andstripping,not copiedbuildELFs.

Assetfreeprogramarchive built/unpacked/renamed,thenimport fromraworiginals underisolatedHOME/XDG andforeignCWD.25,792SDLsteps/all10gameplay vectors/6448camera frames/364audio deliveries exact; savednewprocess works,wrongselection doesnotreplaceprefs. Literal shellmetacharacterpath handled safely. strace records0checkoutfileaccesses and0Python/Wine/sha256sum execs. Fourassets/contexthashes retained; binary/lib/license/metadata manifest hashes pass. Existingdestination/archive preserved. Nativewelcome BMP/PNG inspected. No namespace-denial/broadolderABI/physicalsound-listening/portal-click claim.

Fullbuild0warnings;4/4affectedCTestsPASS34.73s: newPiratepackage andMeanpackage/setup/import. PriorPirateimport13.73s passes. Python/sh syntax andmanifest checks pass; noGitmetadata/configuredformatter,unrelatedfullsuite notrerun. Readyprogram/archive:`build/releases/slamtilt-pirate-native{,.tar.gz}`; evidence/scopes/commands:`analysis/pirate-firststart-island.json` andtraces/pirate-firststart-acceptance.json. No newRE required.

Additional realdesktopcheck remainsOPEN: bothfullscreen/windowed14frames fail syntheticfocuslossfreeze atframe2(ticks8→12). Devicepaused always matchesactualexpectedpaused andqueuepopulated; pause/minimize/options/mute/reset branches otherwise run. Lateactualfocusgain mayoverride injectedloss, HYPOTHESIS only; eventorderingnotrecordedyet. Do not claimrealhostacceptance complete orchangeaudio blindly. Logs:build/oracle/pirate-package-realhost-{audio,windowed}.json. Next: actual/injectedfocus-eventtrace.


## PIRATE-HOST-031 — Actual focus-event ordering and real-driver matrix (2026-10-22)

Pirate host031: observed actualfocusgain526/mainwindow4 after scriptedloss527/id0 explains frame2failure. Test-only SDL_PumpEvents beforeinjection fixes event order; no ignoredOS events/removedfreezechecks/audioorphysics changes.12source+12packaged realWayland/PipeWire runs and6dummy cases pass audio/Nudge/LeftCtrl focus/minimize/pause/options/mute/reset/repeat/remapping gates. New --fullscreen enablesgenuinefullscreenwithframes; earlier030attempts werebothwindowed.4/4CTestsPASS30.00s,fullbuild0warnings. Relocated25792steps/10vectors/6448camera frames/364audio requests unchanged. Ready:`build/releases/slamtilt-pirate-host/slampirate`. PhysicalAltTab/listening/otherdrivers/olderABI remainunclaimed. [Evidence](../analysis/pirate-host-island.json).

Instrumentation-first baseline `build/oracle/pirate-focus-before.json`: frame2injected527/id0 then actual526/id4, ticks8→12. Audio report confirmsgamewindowID4; post-fix queue ordergain→loss oractualgain arrivesnextframe, preserving scriptedfreeze. Windowevents/timestamps/IDs,actualdriver/fullscreenflags exported underaudioacceptance. Ordinaryevent loop remains unchanged. No newREneeded forsource-leveltestcorrection.

Source andnewstrippedassetfreepackage each12cases(audio/Nudge/special×actualwindow/fullscreen×2),14frames each; actualWayland/PipeWire.6dummy cases in CTest plusrelocatedfullgame/special/Nudge checks. Commands/hashes/scopes:`analysis/pirate-host-island.json`; compactmatrixfixtures andprivateeventlogs retained. Three earlierpair-of-mode claims corrected: frames forcedwindowed until031addedexplicit--fullscreen; actualflags nowasserted. NoGitmetadata/configuredformatter; Python/shsyntax pass; unrelatedfullsuite notrerun. New archive/launcher:build/releases/slamtilt-pirate-host{,.tar.gz}. Next: olderABItoolchain.


## PIRATE-COMPAT-032 — Older Linux native import and full gameplay (2026-10-22)

Pirate older-Linux ABI032: same immutableMean Debian12/GCC12toolchain reused offline/sourceRO. MaxGLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9. ActualDebian12glibc2.36 imports4exactfiles withnativeUI/PATHempty; rememberedstart/SHA/audioNudgeSpecial pass.25792steps/10vectors/6448camera frames/364audio requests exact. No sourcecheckoutmount,program/raworiginalsRO,networknone. Relocatedarchive/currenthost and12Wayland/PipeWire actualwindow/fullscreen cases pass.4/4regressionCTestsPASS31.99s; ownbuild0warnings. Ready:`build/compat/releases/slamtilt-pirate-bookworm/slampirate`. Sharedhostkernel; otherdistros/drivers/physicalAltTab/listening unclaimed. [Evidence](../analysis/pirate-compat-island.json).

Newcompatwrapper reuses exactcontent-addressedimage fromMeanmetadata; noDocker rebuild/download/tag substitution. Ninja cache reused,workspaceRO/outputRW/networknone. Separatepirate-build.json/release/toolchainreports preserveMeanreports/releases. Targets:slamview/slampirate-import/slampirate-setup/sha256_tests. Packagerusespinnedlicenses/actualELFversionrequirements; everybinary/library withinABIceilings. Existingrelease/archive refusal verified.

Actualoldcontainer mounts onlyinstalledprogram/raworiginals/replay/SHAchecker/state. NativeUIimport underPATH=/no-import-tools;4hashes,rememberedlauncher,3eventacceptances,full25,792stepreplay againstoriginalhostgolden. All10vectors/6448camera frames/364audioevents exact,importedfilesunchanged. Hostunpack/rename/foreignCWD/strace0checkout/Python/Wine/checksumexecs;12realhostoldbinary cases pass. Prebuiltarchive/output options extend existing tests withoutweakerassertions.

Newpirate_compat_runtimeCTest registered; sameverifier manuallyPASS.4modern/MeanCTestsPASS31.99s. Python5tools/shsyntax,manifest/profile/ABI hashes pass; ownoldbuild0warnings,upstreamSDLcached. NoGitmetadata/configuredformatter; unrelatedfullsuite notrerun. Commands/pins/hashes/scopes inanalysis/pirate-compat-island.json and3compactfixtures. NoRE/gameplaycode changes. Next: measuredrelease real-time frame/input behavior.


## PIRATE-REALTIME-033 — Measured render work and real-clock input path (2026-10-23)

Pirate real-time/cache033: preload75ball shading groups once; conditionalLampstate/actualflipperRGBA/DMDcolor texture uploads. 1000fixedframes/4000steps preserve10vectors/camera/fullBMP byte-exact; uploads58000→2974,MAINopens1002→3,perballrenderfileIO0. All600Ypixels matchprior decoder. RealWayland/GPU4secondruns/window+fullscreen:799steps,acceptedclockresidual<5ms,0clamps;8queuedpresses permode reachposechange inlowmilliseconds. Rendercallwallp95~0.82–0.86→0.16ms; loopintervalnotphysicalrefresh,not CPU/GPUcounters orphysicalinputlatency.5/5CTestPASS17.58s,12finalpackagehostcases pass,olderABI fullgame unchanged. Newready:`build/compat/releases/slamtilt-pirate-realtime-final/slampirate`. [Evidence](../analysis/pirate-realtime-island.json).

Baselineactualrelease:4seconds/windowmode yields1814/1844renderframes,1813/1842ballfile reads,105211/106950texture uploads. PriorfunctionopenedMAIN at3da4+(Y/8)*256 foreachdisplayedball. Newbank opensonceatstartup,validatesexistingf028size,reads75×240bytes; priorper-YAPI remainsindependenttestreference.53lamp frames uploadonlyonvisibleword change; flippercachecomparesRGBAafterruntimeparentmask composition,soequalpose withlamp changes stillupdates. DMDcachecomparesfinalcoloredRGBA; customcolor/options updates preserved. Sharedballtexture stillupdatedeveryball becauseperballmask/lightingdiffers. No rendercadence/physics/rules changes.

Pre/post1000frameactualstraceMAIN opens1002→3,textureuploads58000→2974. All10vectors+camera+completeBMP byteidentical; publichashfixture retains preoptimizationgolden.75shadinggroups/600Ypositions verified against existingfile decoder. Native andolderGCC12builds warningfree. Newboundedrealtime diagnostics avoidfixed20ms frame clock,preferactualGPU,avoidpersistentprefs/highscores; capturetime/acceptedelapsed/stepcounts/posechange andwallcallgroupdurations. CPUcounter/GPUexecution/physicalinputlatency NOTmeasured. Firstsecondexcluded;8queuedSDLpresses perwindowmode. Finaltickquanterrors4.571242/3.783472ms,0clamped frames. Shortinstrumented measurements,not generalperformance promise.

5/5affectedCTestsPASS17.58s:bankallY,4000step/scenepixelgolden,dummyhost,relocatedmodernpackage,actualDebian12compatibility. FinalolderABI package25,792step10vectors/6448camera/364audio intact;12realWayland/PipeWirehostgate cases pass. ABImaxima2.34/3.4.29/1.3.9 retained. Existingcompatverifier outputpaths generalized so033doesnot overwrite032proof. Python/shsyntax checked; noGitmetadata/configuredformatter/unrelatedfullsuite. No newREneeded. Rawprofiles/strace/BMP stay privatebuild; compacthashes/scopes/commands:analysis/pirate-realtime-island.json. Next: longerreal-clock finitegame replay.


## PIRATE-FULL-REALTIME-034 — Complete real-clock multiball games/highscore/newgame (2026-10-23)

Pirate fullreal-time034: nativeGPU/actualwallclock legalCrocodile replay15600steps/78.026s andtwofinitegames25792steps/128.986s matchall10original vectors;597audio requests exact,0timeclamps. Threecompletegames/3F1 continuations; firstnaturaltrajectory overlaps. Cave/Cannon/2ballJP/15.83M/ABC/GameOver/F1/freeball pass,plusactualprivatehighscore persistence andfreshprocess50byte reloadwithoutrewrite. Newexact-tickbound supportsnon4multiple37step test. Freshoriginal15600retains9vectors/addsMSstate; no newRE/physics.4/4CTestPASS14.43s,oldABIandmodernbuild0warnings,actualDebian12regression retained. Ready:`build/compat/releases/slamtilt-pirate-fullgame/slampirate`. Notwholeoriginal raster orphysicalinput/audio listening/all-mode acceptance. [Evidence](../analysis/pirate-full-realtime-island.json).

Native--realtime-steps stopsafterexactNstep,includingwithinrenderer catchupbatch; timeoutdefaultN×5ms+30s,guardnotextra simulation. Existing--frames fixedclockunchanged. Legalreplay callbacks only; noball/rule/timer/phase/waypoint injection. Optionalrealtimebudgetexpandedforfullgame. 37steporiginalprefix test demonstratesno4step rounding/overshoot.

Freshoriginal15600stepNaturalCrocodile inputreplay preservesexisting9vectors exactly anddirectlyobserves5MSfields; publicsourceSHA/MSsequenceSHA,rawvectorprivate. Realtime15600loop63483frames,active78000.835129ms,totalprofilewall78025.656917ms. Two-game25792replay128986.202777ms,2GO/F1→thirdfreeball. All10vectorsperstep+233/364audio requeststreams exact. No clampedrawtimesteps. CoreOriginalfrozenfixtureintegrity independentlycheckedbothcases. Nativecamera/render cadencevariable andnotclaimedpixel-identical tooriginalraster. FinalGPU screenshot captured/visuallyinspected.

Samefixturesacceleratedinprivatefreshscoreprofile: final15830000/ABC records matchoriginal50bytes; subsequentnativeprocessloadsall50bytes anddoesnotrewriteinode/size/mtime/content. No realuserprofileswritten. ActualDebian12nativeimport/finiteoriginalgame/camera/audio andrelocatedhostpackage regressionPASS,newreleasemaxABI2.34/3.4.29/1.3.9. Fullmodern/olderbuild0warnings;4/4affectedCTestsPASS14.43s;3Pythonsyntaxchecks andarchive/fixture hashes pass. NoGitmetadata/configuredformatter; unrelatedfullsuite notrerun. ExistingdynamicRE/runtimeprovidersnotneeded; cachedUnicornoriginaloracle reusedwithoutsetup. Scope remainsbounded,keyreplaynotphysicalinput/listening/notallmodes. Commands/hashes/case details:analysis/pirate-full-realtime-island.json. Next: onlyconcretePirateremainingacceptancegap against existinghandbook/mode evidence.


## PIRATE-RULES-035 — Plank display fix / Piranha / full multiplier payout (2026-10-23)

Pirate rule035: fixedactualPlank30Mfeedback callback42eb6c,previouslymissedregisterpush432388/432390/4323c8. Oldreleasefailed4099;now271dispatches/51DMDframes exact. +211compiledOriginalinstructions,24118total/outsideboundary unchanged. Fourchains26008Original/freshreset/native/reset/SDL10vectorsteps:PlankSJ,Piranha10×2Madditions/11thnormal/rearm,1/2/4/6/8/10/12bonusladder/cap,20.7M×12payout/nextballreset. Allfour alsoGCC12/actualDebian12 pass.82uniqueaudio cases/6215requests exact acrossmain81+scoped1;retained78rows unchanged. Fullbuild0warnings;two4/4CTestbatchesPASS209.10/34.58s. Ready:`build/compat/releases/slamtilt-pirate-rules/slampirate`. Diagnosticphysicalwaypoints,notallkey-onlyall-featuregame. [Evidence](../analysis/pirate-rule-island.json).

BoundedCapstone registerconstant/push extension found3sites beyond57immediates.42dbb4/42f384alreadycompiled;42eb6cmissing. ActualfiveDATropes+uppertraprequest it: event4048,firstdispatch4100,last5180,271calls,51DMDframes. Existingadmit40step bound initiallymissed51stepcapturelatency; actualcapturecompletionrevealeddispatch. OldO2release reproducesUnsupportedPiratecall42eb6c at4099. Onlynew211instructioncallback lifted;score30M+ordinarytrap500k wasalreadyimplemented. No generic runtime decoder/stubs/new physics. NativecoloredDMDcapture inspected;4chain Original/freshreset/native/reset/SDL vectors exact. Localregisterconstant inventory60sites/44targets isbounded,nonlocal/tablecomputed targetsstillunknown.

Handbookprinted14/build/manual-rules/pirate.txt47..53:Piranha pair. Actual139,225 and151,260 set46e2c8/c9;439608 resetsWORD46e2ca10;4394c4/4394e9 paysEAX2M,additiontoordinaryvelocity-dependentbumper score. 10paidcontacts→0,11thnormal,duplicateleft guard,7→10rearm,14total2Mpays;actual42cf8c/42dc64 dispatch. Full8524stepSkull/righttrapladder1/2/4/6/8/10/12 requires2/3/4/5/6/7contacts.17furtherSkulls do notarm;unlitcaptrapno437247registration. No multiplierfieldinjection.

Payoutfixture preservesall8524prefixvectors,addsonefreeballdrain(160,590). Phase3at8586;score405fac calls8588:7M(return4351ef,neutrallynamed) and248.4M(return407d1e)=20.7Mbase×12. Score20M→275.4M;ball2/phase1at9924 clearsbase/multiplier1. Total10004inclfinishpadding. Fourcases5264/2216/8524/10004=26008steps,all10vectors perstep;alsoactualDebian12 andinstalledGCC12SDL. Othermanualgaps classifiedunverified ratherthanassertedmissing.

Global81audio cases662728steps/6194deliveries PASSNative/reset/SDL plusseparatepayout10004/21:82unique/672732steps/6215deliveries(82base+6133actual).296674812Native deterministicstereoframes/twopasses,60uniqueOriginalmonoPCM retained;finalmixedOriginalPCMnotclaimed. Scopedfixture/workdir CLI avoids rewritingglobalevidence whiletestsrun. Original78rows preserved. Main4/4CTestPASS209.10s;final4/4PASS34.58s,5uniquetestnames. Modern/olderbuild0warnings,Python source/contracts syntax pass. NoGitmetadata/configuredformatter/unrelatedfullsuite. CachedCapstone/Unicorn reusedunderREAworkflow;knownnativeproviderunavailable,no setupchanges. Newreadyassetfreepackagebuild/compat/releases/slamtilt-pirate-rules; hashes/commands/scopes inanalysis/pirate-rule-island.json. Next: Skillshot/Combo timingwindows/ExtraBallthresholds.


## PIRATE-WINDOWS-036

Pirate 036: Nine Original/fresh-reset/native/reset/SDL chains match all 10 vectors across 29,076 steps. Skillshot: 10M once per ball, rearmed on next launch. Combo: 1M/2M/3M cap; timer 0 valid, −1 expired. Extra Ball: thresholds 25/50, next threshold 100; two earned credits replay Ball 1 twice before Ball 2. Player+0x0c counts successful Combos (historical ordinary_ramp_count keys retained). Existing native engine passed; added contracts, fixtures and CTest gates. Nine audio cases / 100 Original requests match. Diagnostic contacts; not legal-key-only all-feature acceptance. [Evidence](../analysis/pirate-window-island.json).
Anchors: Skillshot43898c/4389eb/46e53a;Combo438a37/4367ec/436832/46e550;Extra43531c/43534a/435366/46e2d8. Windows Retail SHA 185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6.

PIRATE-WINDOWS-036 verification: 5/5 affected CTests PASS (`build/pirate-window-final.log`); Python syntax and artifact-reference/step-count checks PASS. Existing GCC12 package matches all nine SDL fixtures. No production code changed.


## PIRATE-MERMAID-037

Pirate 037: Seven Original/fresh-reset/native/reset/SDL chains match all 10 vectors across 52,364 steps, also in the existing GCC12 package. Repeated Mermaid collection pays 1M/3M/4M; bank survives ball changes and F1 resets it to 1M. Hold Bonus preserves the base once, including under Tilt, but resets multiplier ×2→×1. Original quirk retained: Tilt suppresses base×multiplier, while Combo-count×1M still pays (2M proved). Seven audio cases / 217 Original requests match. Added fixtures/contracts/CTest; no production changes. Diagnostic free-ball trajectories, not legal-key-only all-feature acceptance. [Evidence](../analysis/pirate-mermaid-island.json).
Targeted original PE bytes/disassembly: `analysis/pirate-mermaid-static.json`. Runtime calls: Mermaid return432b7f, Combo bonus4351ef, base×multiplier407d1e. Hold cleanup408228..408252; player-bank save435710/restore435776; newgame4359a2. `drain_*_bonus_entered` is the payout base snapshot: an already scheduled plunger event may add500k between the diagnostic drain contact and bonus entry. Earlier inferred pre-drain base is not used as the payout oracle.

PIRATE-MERMAID-037 verification: `cmake --build build/native -j3` PASS, 0 warnings. Four affected CTests PASS in209.40s (`build/pirate-mermaid-regression.log`); exact commands retained in the island JSON. Existing GCC12 package matches all seven SDL cases. Python syntax and JSON/reference checks PASS. No Git metadata or configured formatter/linter; no production code changed.


## PIRATE-COMPLETION-038

Pirate 038: PLAYABLE_RC. Manual audit links 24 rule contracts to 56 SHA-pinned Original fixtures / 372,660 retained steps; 48 semantic checks rerun. Closed the concrete auto-Knife gap: left/right only during video, 25 kills / 75M / collected Extra Ball, 13,076 Original/reset/native/reset/SDL steps, 74 audio events exact. Pirate capability now Playable with Retail SHA (Mean stays Demo; Space/Demon viewers); removed Preview captions. Asset-free GCC12 RC1 built and verified under actual Debian12: raw import/selection,25,792-step game plus90,340 rule steps/all10vectors; relocated archive and12 actual Wayland/PipeWire window/fullscreen event tests pass. [Evidence](../analysis/pirate-completion-island.json). Bounded diagnostic feature coverage is not all-feature key-only/full-raster equivalence; undocumented Battle3x admission remains UNKNOWN.
Automatic throw static anchors:434e24..434e72 compare previous/current playerX+48 sides of active enemyX;434e5a calls434184 on crossing; eight free projectile slots at46e0b8,stride8. Actual mode2112..11188 received294 left/right edges andnoEnter. Keys before video include the legitimate launch. Full independent Original reset and native/reset/SDL prove outcome; static conditions are separately sourced from retained PE/generated lift.


PIRATE-COMPLETION-038 final verification: 6/6 affected CTests PASS147.73s; modern/GCC12 builds0warnings;12actualWayland/PipeWire event cases PASS. RC1 fullscreen real-clock natural game15600steps/78.0398s matches10Originalvectors and233audio requests,0clampedframes;15.83M/ABC/GameOver/F1 andprivate saved-score fresh-process reload/no-rewrite PASS. Actual Debian12 import/25792game+90340rule steps andrelocated archive pass. Static automatic-throw PE snippets:`analysis/pirate-knife-auto-static.json`. Exactcommands/logs retained inislandJSON. NoGitmetadata/configuredformatter/linter;Python syntax,JSON/index references and48semanticcontracts PASS.


## RETAIL-GAMEPLAY-039

Claim: Selected original Retail table data/callbacks run natively for Space and Demon without substitute physics. Four independently reset Original/native/SDL cases cover26,400 steps, including natural three-ball games andF1. Space also qualifies/entersABC; Demon observed route scoreszero anddoesnotqualify. All100ballbytes,9clock/phasefields,3poses,DMD1920bytes,15lifecyclefields,actualselected-table50bytehighscores andlampWORDs match.

Anchors: Space439ae0→46664c/466424/46ed60;200Hz440d10,perball441aa8,50Hz446850,launch44466c,input44486c/444940. Shared fullclock405234; canonical pool454b68→46c15c+i*100. Original404ebf..404ee0 sets46c498=46c510+50*(selection−1): Space46c574,Demon46c5a6. Original404b87..404c03 choosesleftupper when graphics+1c==ffff; rightpath404c9d..404d03 requires+1. Selection0skipsstartup; Demon=4,not0. [Static/init evidence](../analysis/space-entry-anchors.json); [fixtures, boundaries and scope](../analysis/retail-gameplay-island.json).

Space real-time host:1200steps in6014.73ms,Wayland/OpenGL fullscreen,0clamps; same raw vectors/reset. This is not physical human input, physicalGPU identification, audio or whole-raster parity. No diagnostic ball/score/rule writes in these trajectories. Audio/options/persistence/camera/multiball are outside the new preview acceptance.

039 final checks:6/6 affected CTests PASS51.27s; final Space/Demon2/2 PASS11.18s; build0warnings. `tools/verify_retail_slice.py` checks both1200/12000cases andtheirindependent native reset. Real-time fullscreen replay checkedallvectors again. SharedOracledefaultPirate1000step/contextSHA regression PASS. Python/shell syntax PASS. Exactlogs/binary fingerprint inislandJSON.


## SPACE-ASTEROID-040

SPACE-ASTEROID-040: two Original/reset/native/reset/SDL fixtures /31,716steps. Allfour actual trapcaptures1/2/5/3 pay5/5.5/6/6.5M plus500k each; ramp no-Asteroid guard,exact12001-tick expiry,played flag acrossball2/3 andF1reset,46M/ABC/GameOver pass. All100ballbytes,clock/phase/DMD,poses,lifecycle/highscore/lamps and1536rawstatebytes match. AllSpace4/Demon3 layerhandlers seeded fromverified directories; +1041compiledinstructions,44802total,outsideboundary unchanged.7/7 affected CTests PASS35.73s;build0warnings. Extra20M return4413d5 preserved,meaning UNKNOWN. Diagnosticcontacts,notkey-only/allrules/fullraster. [Evidence](../analysis/space-asteroid-island.json).
Score callsites:441e9b/4423fc/443955/4484ce;expiry440e45..440e62→441770;played0set447e7d,ordinaryreset446fbc;player save/restore446b58/446b80. Actualcasevectors pinned in`analysis/traces/space-asteroid-{chain,traps}.json`. Alltrapcases assertordinary500k separately; unclassified20M isneverfolded intoAsteroidawards. Corrected earlierstaticname:166,101 iscapture5 (airlock STRONG),top iscapture2 at210,18. Exact IDs/consumers takeprecedence overnames.


## SPACE-MISSIONS-AUDIO-041

Original/reset/native/reset/SDL: four mission cases, 47,412 steps, all seven comparison vectors including 1536-byte raw table state. Race goal return448601 pays25M; separate expiry return441690 pays5M. Hack return448705 pays75M for runtime winner2; wrong3 does not. Blam return4487ca pays10M for six distinct events; return442517 pays30M only when earned. Event6 is layer1(269,51); old(187,82) reaches a different branch and is retained as a negative guard. Hack event1 pair is static-only.

Three Original STIM banks at DAT53642/5b8e0/5fef8 and ten sample descriptors feed existing libxmp/mixer. Seven audio traces /80,328steps /119requests match; enabling audio leaves gameplay vectors unchanged. 26 independent PCM checks pass, without claiming original mixed-PCM equivalence. Static lift46071instructions, six outside calls unchanged. 10/10 CTests PASS109.45s, build0warnings; actual fullscreen Wayland/OpenGL/PipeWire1200step run matches state and five audio requests,0clamps. [Evidence and exact scope](../analysis/space-mission-audio-island.json). Next: multiball spawning/compaction/rendering.


## SPACE-MULTIBALL-042

Two Original/fresh-reset/native/reset/SDL cases /15,472steps match eight vectors, including full800-byte ball pool. Standard phase4 at2118; additional balls3109/3201. Alien phase6 at653; additional balls1657/1749. Original441ab4 jump table maps capture3→442b1a (multiball admission442c70) and capture5→4430a7 (mode admission443352): prior geometric airlock/mode names were reversed. Actual airlock(199,188), mode(166,101). Third top capture arms150/50Hz window; actual immediate airlock works. Earlier166,101 airlock probes did not start standard multiball.

Native frontend now calls original408674 integer compaction every4ticks and renders all active balls using existing original sprites/masks/occlusion and stable Y order. Static compiled intermediate47051instructions (+980), six outside calls unchanged. Actual fullscreen Wayland/OpenGL/PipeWire Alien replay7004steps matches all eight vectors, screenshot inspected with three balls. Diagnostic contacts/parking only; no rule/score/timer/spawn writes. Loss/compaction transitions and jackpots remain unaccepted. [Evidence](../analysis/space-multiball-island.json).

042 final verification:11/11 affected CTests PASS117.91s (`build/space-multiball-final.log`), build0warnings; Python syntax and JSON/index references PASS. Exact commands/native hash in island JSON. No Git metadata/configured formatter; changed source reviewed directly.


## SPACE-MULTIBALL-REWARDS-043

Original/reset/native/reset/SDL:17,676steps, eight vectors incl800-byte pool and actual nonlast ball0 deletions3→2→1. Standard return441641 and Alien return441834 occur801steps after second deletion. Standard payout return442251 pays10/20/30M for1/2/3 distinct eligible ramps0/5/6, followed by rearming. Alien return4488f9 pays seven distinct10M awards; top return44267f pays30M once, then rearms targets. Duplicate ramp and unearned/repeated top guards preserve only ordinary awards. Final scores65.25M/104M; actual Alien DMD shows100M mode total.

Two independent Original reset replays also record37 audio requests, matched by existing native audio while allgamevectors stay exact.526 added static Original instructions (47577total), six outside calls unchanged; no replacement physics, score/rule/timer/spawn writes. Actual fullscreen Wayland/OpenGL/PipeWire7416-step Alien chain passes all eight vectors and14audio requests, screenshot inspected. Fixed-step host replay, not real-time/physical input/listening or original mixedPCM parity. [Evidence, callsites and scope](../analysis/space-multiball-rewards-island.json).

043 final verification:12/12 affected CTests PASS129.93s (`build/space-multiball-rewards-final.log`), build0warnings; syntax and JSON/index references PASS. Exact commands/native hash retained in island JSON. Existing Space/Demon/Pirate regressions pass.


## SPACE-MODE-FAMILY-044

Real selector bumper layer0(200,128) cycles1/2/3/4 with4steps each, independently reset twice. Four further reset-based outcomes /28,468steps: Sabre44×2M return44b172 and30M return44273d; Bikes3×30M return448a46,wrong-side guard,expiry12,921steps; Walker aimed71..87→15M return444752 then3→2→1 loss/return; Death Planet video flag46c6c0 runs withphase2, no-input lives loss ends5304, actual ballFREE at5824 (520later). Success/PowerCore/Extra Ball not verified.

Original44551a ff1424 CALL[ESP] target is read before CPU pushes44551d return address. Static lift previously pushed first, reading its own return as target; fixed generic operand evaluation order. Original actual target groups observed at1864 in`analysis/space-video-entry-probe.json`. Added256-byte opaque aux hash466b6c..466c6c andnative reset check. New callbacks compiled asstatic C++,50,279instructions, six outside calls unchanged. Walker4436bc BF02000000 +443786 66893d5eee4600 prove2extra; runtime3FREEballs contradictmanual2-ball, reasonUNKNOWN.

Actual fullscreen Wayland/OpenGL/PipeWire Death Planet2000-step segment matches nine vectors and audio, tunnel DMD screenshot inspected. Original/reset fixtures retain90 audio requests. Diagnostic contacts/key events, no rule/score/timer writes; not all-mode legal-key-only/full-raster/PCM equivalence. [Evidence](../analysis/space-mode-family-island.json).

044 final verification:13/13 affected CTests PASS154.45s, allfour native/reset/SDL cases match nine vectors and90audioevents; build0warnings; syntax andJSON/index referencesPASS. Actual final hostbinary DeathPlanet2000step segment rechecked. Exactcommands/nativeSHA inislandJSON; noGitmetadata/configuredformatter.


## SPACE-PLANET-SUCCESS-045

Six actual endrecords pay15M each atreturn445df8; remaininglevels466b72 reaches0 withlives466b78 always3. Automatic finish increments pendingWORD46ed50 at445089. Actualtop(210,18) capture2 calls442103→444214:444246..44425a consumes pending andincrementsplayerWORD+10 credit. Physicaldrain/bonus consumescredit, Enterlaunch replays Ball1; score92,502,480.19,392 Original/reset/native/reset/SDL steps, nine vectors and15 Original audio requests match. Frozen steering592left/right edges uses actual obstacle records andposition/velocity, no video/rule/score/timer writes. Actorreturn aftersuccess720steps; separate failure044 delay520 retained.

Source fixture/acceptance:`analysis/traces/space-planet-success-{rewards,acceptance}.json`. Original instruction evidence:`analysis/space-planet-success-static.json`.234 addedcompiledinstructions,50,513total, outsidecalls unchanged. Reused044 raster closure to omit hot call-edge tracing whilevideo runs; score hooks, nine state/DMDvectors and independent reset remain. Default trace behavior unchanged. Actualfullscreen Wayland/OpenGL/PipeWire full19392step chain matches ninevectors and audio; screenshot inspected. Fixedstep,not physical input/listening/OriginalmixedPCM. [Evidence](../analysis/space-planet-success-island.json).

045 final verification:14/14 affected CTests PASS158.96s (`build/space-planet-success-final.log`); build0warnings; syntax andJSON/index/callback-root coverage PASS. Existing Space/Demon/Pirate regressions retained. Exact commands/nativeSHA inislandJSON.


## SPACE-BIGBLAM-046

Actual reset-based campaign completes modes0..4; five WORDs46ed44+2i are1 while allfour missionflags remain0. Capture5(166,101) invokes443168..4431b9, clearsfive flags,phase7,WORD46ee5e=5. Runtime reaches6FREE balls, notmanual4. Eligible ramps0/2/3/4/5/6 pay10M return448ae3 andgrowbank46ed10 by15M; event1disabled.25M/100M bank payouts return442820 resetbank10M/rearm. Duplicate ramp andunearned/repeated top guards retain onlyordinary awards. Specialawards195M; player346,804,560. Actual ball0 deletionscompactpool6→5→4→3→2→1; phase2return441a14 exactly801steps later, playedflagsremaincleared.

42,864 Original/reset/native/reset/SDL steps,nine vectors incl800-byte pool and256-byte aux,87audio requests exact.15/15 affected CTests PASS198.06s, build0warnings.255addedstaticinstructions(50,768total), sixoutsidecalls unchanged. Reused verified0..4closure; discovery onlyfromearnedfinal-readystate, allstate/DMD hashesretained. Actualfullscreen Wayland/OpenGL/PipeWire36568step campaignsegment matchesninevectors/audio, six-ballscreenshot inspected. Diagnosticcontacts, no rule/played/score/timer/spawn writes; notallseeds/Tilt/legal-key-only/fullraster/PCM acceptance. [Evidence](../analysis/space-bigblam-island.json).


## SPACE-SESSION-047

Source integration, no newbinary claims: PortOptions/UiSkin/Presentation reused inretail_slice. Optional tableheight600 display_layout preservesdefault400 forMean/Pirate. Realmenu SDL events changezoom1.05,Neonpreset3,DMDleft,volume.95 andapply; freshprocess reloadmatches. Menu/focus holdsimulation tick and actualNativeAudio.device_paused; resume tick advances/deviceunpauses. Enter/Backspace initials stayindependent ofplunger mapping. Runtime-owned UI resources destructbefore SDL renderer.

Private space-highscores.json usesexisting atomic50-byte storage, writesonlyselected tablepointer46c498 target(Space46c574), savescompleted GameOver records.12000-step Original finitegame exact→ABC/save, freshprocess reloadselected50hash withunchangedmtime; corruptfile bytes preserved. Diagnosticshots rejectexplicitpersistent profile, automateddefaultprofiles disabled.1200presentationstepsmatchOriginalvectors; allpriorrulefixtures remaincanonical.

20/20 affected CTests PASS191.62s; finalcosmeticwindowtitle smoke5/5 PASS12.89s, build0warnings. Actual Wayland/GPU/PipeWire1200step replay matchesOriginalgame+5audioevents withrealSDL menu/focus injection, devicepause/resume,Neon,DMDleft; separateFill/Crop+DMDtop viewportcoverage/Originalvectors PASS. Screenshots inspected. These areprogrammatic events/fixedsteps, notphysicalkeyboard/listening/realtime/fullraster parity. [Evidence](../analysis/space-session-island.json).


## SPACE-BASE-AUDIT-048

Four Original/reset/native/reset/SDL cases24,472steps,ninevectors/69audioevents. Skillshotreturn44a867 pays10/15M,WORD46ee5a launchwindow/repeat/latearrival guard;46ed58 advances5M. Alternating0/5 actualramps yield40 literal1M awards44a45d/449b64, +1M bonusbase, playerWORD+0c count. Threshold46ed5c20→40→80 givespending46ed50 thenactualplayer+10 credits; two physicaldrains/relaunches replayBall1, thirdmovesBall2. Return4465b2 countbonus40M onthree successive drains retained. Armedtimer inphase6 producesAlienaward butnoCombo.

Actual speedpath: inlane0(241,468)→event2 layer1(156,25), notevent1pair.44a0fd pays4/6/8/10M then4Mafterreset;44a082 Lunatic20M resetsgrade.46ee4a passagecounter1→0→ffff, nottimer.6swindow expiredguard and751actual50Hz frames for1→0 decay pass.997additionalstaticinstructions,51,765total, outsidecalls unchanged. Actual GPU/PipeWire13296step skill/credit chainninevectors+55audioevents exact; screenshot inspected.21/21CTestPASS206.29s; auditcheck1/1PASS. No rule/counter/timer/score edits.

Manualindex24contracts:15VERIFIED/4PARTIAL/5UNKNOWN;20hashedfixtures; release_ready=false. FullExpertRetailPDF verifies missingBigBlamtail (ramp→planet→Jackpot), originalcutexcerpt preserved. Source-specificbehavior documented ratherthanforcingmanual wording. [Evidence](../analysis/space-base-audit-island.json).

## SPACE-WEAPONS-049 — Weapon bank, bonus and earned Magnasaver

VERIFIED_BOUNDED: weapon flags 46ed2e/30/32; completion448cc0; multiplier player+0x12 through table466f5c; cap return448de3 pays10M. Actual250k×10 bonus return407d1e pays2.5M and next ball resets1. Duplicate bank flags and flipper rotation observed.

Actual RightCtrl scan9d dispatch404af7→444784 consumes46ed36, enables force node466564/type466568 and duration46ee5c=200. Same100-byte ball state at604: after20steps offY451.85546875/onY415.151062; actual expiry20150Hz frames, unarmed/retrigger/rearm verified. Actual LeftCtrl1d dispatch404ab4→444810 is input-only evidence; lane-changing geometry NOT accepted. RightShift does not activate Magna.

Four fixtures/5548steps/16audio match ten vectors across Original/reset/native/reset/SDL; three SDL key cases pass. 40be98 conditional1920-byte DMD restore is STATIC evidence only (46c720=0 in fixtures). Source compiled count52262; remaining external calls407340/4075b8/40762c/4076c0/44fd30. 24/24 affected CTests PASS225.00s. Host controlled-focus GPU/PipeWire proof excludes physical-keyboard/listening/fullscreen/full-raster acceptance. [Index](../analysis/space-weapons-island.json).

## SPACE-LANE-KICKBACK-050 — Earned kickback and loop direction

VERIFIED_BOUNDED: material5/6 consumers44ac23/44aeb2 update grey WORD46e930/32/34/36; four Layer0 contacts(61,330),(102,180),(197,264),(207,277). Completion44b034 clears bank and arms46ed34=ffff. Material7(5,533) callback44af98 consumes charge, sets46ee58=250; its internal vy=-3 write is static evidence, not a final post-step velocity claim. Paired100ballbytes at620 equal. By700 armedball(12,400,state3), unarmed(32.5426,547.9396,state2). Actual saved-ball release933; grace repeat934 retains172; expiry1624 (25150Hz frames), expired contact1625 matches unarmed first32bytes. Four fresh contacts rearm1629, second save1630.

Actual LeftCtrl1d→444810 toggles46ed2c and46ec74/78 lamp commands. Consumer449636 selects Original paths: first ball difference708, field5c11/13; same entry and states0..707 equal. Double toggle restores entire default ball trace; LeftShift does not select alternate path. Switching during loop at680 equals preselected alternate trajectory. Seven Original/reset/native/reset/SDL fixtures7352steps/34audio exact; six actual SDL key cases pass.111 Original instructions compiled,52373total; outside calls unchanged. [Index](../analysis/space-lane-kickback-island.json). Diagnostic physical contacts, no rule/timer edits; not whole-table/legal-key-only or full-raster equivalence.

050 final verification: build0warnings; 5/5 final targeted CTests PASS78.34s. All25 distinct affected tests pass across runs: broader24-test run23PASS/1audio timeout180s, unchanged audio aggregate separatelyPASS164.23s. No timeouts/assertions weakened. Python syntax, PE hashes, seven fixture contracts, six SDL-key cases, JSON/evidence links and31-fixture audit integrity PASS. No Git metadata/configured formatter/linter; no full-suite claim. Logs and commands in050islandJSON.

## SPACE-MISSION-CAMPAIGN-051 — Four missions, station jackpot and fresh bank

VERIFIED_BOUNDED: admission447e7d sets WORD46ed38/3a/3c/3e by mission; two actual drains carry partial sets into next balls. Actual four-played station guard441b87→441eff clears played+armed441f01..441f32, then pays75M at return441f47. This run additionally pays500k at441b4a and5M slot result4413a5:80.5M total. One slot result only. Zero/three-played and repeat guards, fresh Asteroid admission, GameOver/ABC/F1/launch pass. Five MODE-played flags stay0; BigBlam is separate.

25892 Original/reset/native/reset/SDL steps, ten vectors/53audio exact;206 compiled instructions added,52579total, outside5calls unchanged. Eight retained PE ranges and every instruction byte independently checked. Source full-four clearing at ball transition446e7c..446ede is STATIC only; campaign collects before final drain. 8/8 affected CTests PASS, build0warnings and syntax/JSON/audit pass. GPU jackpot-prefix proof uses controlled focus; no full-raster/physical-input/listening/fulltable claim. [Index](../analysis/space-mission-campaign-island.json).

## SPACE-VARIANTS-052 — Repeat cycles, reachable Race ladder, Sabre channels, Walker aim

VERIFIED_BOUNDED: seven Original/reset/native/reset/SDL fixtures56816steps/121audio exact, ten vectors/wholepool. MB second4contacts: first3remainunarmed, fourtharms; threshold3→4,3→2→1return. Cap9at442d22 STATIC. Walker recapture3826→secondaim4160→second15M4161, poolstays3. Freshreal aim70/88 no15M,87pays15M at444752; initialEnter0 leavesfullsample/payments unchanged. Misses also eventuallyspawn3balls, not hit-gated spawning.

Race448601 pays5/10/15/20/25M; tenordinary advances44857d pay2.5M, cap5; tengate-consumption loops do not repay. Goal resets46ee42 to1, sets46ee4a oldcounter−1 and extendsclock100×counter. No rank0 fabricated: observed Retailstarts/resetsfifth; absolute-writer scan439ae0..44b500 isnot aliasanalysis. Below-fifth guard remainsSTATIC.

Sabre44b124 target−1/2M,448b38 ramp−3/6M except event1; health1 residual448c5a2M, zero guard;44273d finish30M. Actual440803 observesfield46ee20+1 inEBX (0→1,44→45), matchingstatic4407f5..440803. NativeDMDhashes exact.345 compiled Original instructions added (52924total), outside5calls unchanged. PE SHA/nine probe ranges+threeSabre ranges independentlychecked. New seven comparisons,6/6regression tests and1/1audit PASS; build0warnings/syntaxPASS. [Index](../analysis/space-variants-island.json).

Manual ledger24/24 boundedVERIFIED,39hashedfixtures; release_ready remainsfalse. Validator now checksmanual_rules_complete separatelyfromexisting-unassessed standaloneimport/package/ABI/session releasegate; rule coverage alone cannot promote Space. GPU Sabre prefix5664steps exact undercontrolledfocus; not physicalkeyboard/listening/fullraster/legal-key-only fulltable proof.

## SPACE-RELEASE-053 — Native import, isolated standalone RC and actual older ABI

Five-file recipe copies original PE sections, zero-mapsBSS, copies192000tablepixels atDAT1360949→imagea0000 andMAIN→d0000;359 canonical imageDWORDs in52000..70000 plus1 runtimeDWORD produce exact known image/runtime SHA. Summary only contains source/context hashes. No original code/asset patches, no recovered-full-loader claim. Native importer rejects wrong/corrupt source and preserves existing/empty/symlink targets. Mean/Pirate wrapper APIs retained; native setup uses dedicatedSpace saved path.

Extracted final archive inBubblewrap withhiddenhome/checkout, freshproc/dev, readonlyprogram/raws, networkoff: import underemptyPATH, quotedfoldernames, savedselection, natural12000step GameOver/ABC/F1, options/audio/menu/focus andscore save/reload pass. No checkout reads orPython/Wine/checksumprocesses. ActualDebian12 container (checkoutnotmounted) nativeimport +82708steps/eight Original cases,tenvectors/audio exact; maxGLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9.

Packaged GPU/Wayland/PipeWire fullscreen realtime12000steps/60019ms/0clamped exactOriginalstate andcanonical25audio requests, scorefreshreload/no-rewrite. Initial unrestricted replay acquiredunscheduledleftflipper (pose8335,ball8352); explicit--replay-only+physicaljournal providesverified deterministic inputownership. Parallelteststress clamped340frames; unchangedstrictcheck passedisolated. Actualruntime binary/library hashes frozen through provenance-only metadata repack; finalarchive namespace/ABI retested.13/13 regression+2/2 finalarchive+1/1releasegate PASS, builds0warnings, Python/shellsyntaxPASS. [Index](../analysis/space-release-island.json).

Space metadata nowPlayable/RetailSHA185d5893..., Demon stillPreview. Completion gate pins finalarchive SHA and VERIFIED evidence;24manual contracts alone do not implyrelease. Scope excludes physicalkeyboard/listening/fullraster/universaldrivers/multiplayer/nudge/Tilt.

## DEMON-BASE-054 — First bounded rule, audio and frontend island

Original layer0material4:418974→419434, topy<100/xsplit140/160/190 setsDWORD46d690/694/698. Actualcontacts(126,60),(148,60),(170,60) plusLeftShift proveflagcycle/duplicateguard;419620 completebank→playerWORD+12hex multipliers2/4/6/8, nextbank15M atreturn4197cb. Actualthreephysicaldrains, earned15M ABC scoreboard, GameOver/F1/launch:6668Original/reset/native/reset/SDL steps,eightvectors and19audio exact. Bonusbase/payout0 inthiscase; do notclaim nonzero×8payout.

410005/410017/410029 bindSTIM offsets6ffb4/6b2bc/6e2ce;11Originalsample descriptors retained,463398 unbound/excluded. Existing parser/libxmp/mixer tests deterministic/nonzero; Originallaunch1200steps/5requests exact. Genericpresentation/session: options/shaders/zoom/DMD, actualaudio/menu/focus pause, privateoptions reload, zero-score12000step naturalgame/no-save, SHA-identical actualOriginal15M ABC recordload/no-rewrite andcorruptprofile preservation pass. Persistentdiagnostic scoresremainforbidden.

Nativeadds105compiled Originalinstructions (53029total), outside5calls unchanged. FivePEranges independentlychecked, build0warnings,9/9CTestPASS89.22s andsyntaxPASS. ActualGPU/Wayland/PipeWire full6668step casevectors/audio exact undercontrolledfocus; screenshot inspected. [Index](../analysis/demon-base-island.json).

Neutralrawhash46d400+400 coversobserved directtablewrites only; linearCapstone scanstops418960 atjumptable, aliases/tail notcovered. Threeactualtrapanchors havefield5a3/1/2; identitiesunknown. Legal-only searchnegative: bothheld/alternating flippers score0; Enterup400/600 produceall100sameballbytes through4000steps vs5mstap, so weak-duration hypothesisfalsified withinthosetests. No legal-only scoring orwholeDemon/release claim. NextClockToweradmission/collision/rule chain.


## DEMON-CLOCK-055 — Earned Clock Tower / held-ball jackpot / multiplied bonus

VERIFIED_BOUNDED: trap0(21,196) consumer4150c0→415fe8 incrementsDWORD46d658 at4162fa; third capture416306 entersphase4. Game pointer46d60c: field0 activecount, field34 heldcount. Layer1(130,30) through419bac→419c14→419d73→419268 decrements46d6c4. Actual DAT0xcbbc6=ff/mask20; switch plane is independent of solid geometry.

4144d1 waits for active==held, releases slots via414e70, increments46d6c0 byheld and rearms46d6c4=total+1. Return414544 pays20M×held: observed60M then20M, ramp requirements1/4/5. First two locks wait withheld1/2; third immediately runs release script. Negative captures genuinely enterstate3 and eject. Service+84=406240 ismusic/audio, not spawning. Actual250k bonusbase with earned×8 pays2M at407d1e; nextball resets1. Separate multiball-loss return observed4001steps.

Three fixtures24484steps/ninevectors/58audio exact across Original/reset/native/reset/SDL.743Original instructions added,53772total/fiveoutsidecallsunchanged.9/9CTestPASS102.78s; build0warnings/syntaxPASS; sixPEranges/allretainedbytes andDATbit independentlychecked. ActualGPU/Wayland/PipeWire5400step threeballprefix matchesvectors/14audio, screenshotinspected. Diagnosticcontacts; notlegal-key-only/fullraster/listening/fulltable. Other eligible traps' normal Wolf/Spirit identities remainopen. [Index](../analysis/demon-clock-island.json).


## DEMON-MODES-056 — Earned seven-mode family and visible two-ball Twice-Pain

VERIFIED_BOUNDED: Wolf0(266,153) field5a2→415563 consumes46d6d0:1/2/3→phase10/8/9; flags46d6b0/4/8. Ramp419c14Y<=100 selects3;41a4d8X<=130 selects2;131..250 selects1;X>250 calls419fcc Spirit admission. Actual DAT contacts1(130,30),2(54,30),2(172,45),2(281,30). Top0(91,14) field5a3→41651c/416574 choosesfirstunplayedSpirit;4189ec cycles46d6c8.419fcc marks46d69c/6a0/6a4/6a8 anddispatches1/2/3/4→phase5/11/6/7. Unarmed guards, selectors andplayedflags observed inruntime.

Bat418c44 pays25M; Grave4190c8 observed46.37M treasure (one seed, not fixedpayout); Meatball414c72 pays50M andreturns. Zombie actualfour5M awards; Witchfour2M+5M Clock. Twice actualpool2/four1Mramps andClockhead15M at416209 (+ordinary1M4164d4); physical2→1/drain/nextball. Vampires41918e paysfour10M,4191c9 finalextra20M, countdown0→normal. Bat/Zombie/Witch/Twice ending isphysical loss, notalltimed/winvariants.46d5f4 isphase-specific; no universal timer interpretation.

Seven Original/reset/native/reset/SDL cases42412steps/tenvectors/90audio exact. Newauxhash coversneutral463b54+100hex and46ceec+20hex; notwholemutable/aliascoverage.1629compiledOriginalinstructions added55401total/outside5unchanged;19PEranges/allinstructionbytes/fourDATbits independentlychecked. Build0warnings/PythonsyntaxPASS;10/10CTestPASS177.23s. ActualGPU/Wayland/PipeWire4800step two-ballTwiceprefix exact/14audio andscreenshotinspected. Diagnosticcontacts; no rule/timer/score/spawn edits. Sequentialcampaign/final, video, kickback, randomClock andvariants remainopen. [Index](../analysis/demon-modes-island.json).


## DEMON-FINAL-057 — One-game earned final, jackpots, refill and fresh bank

VERIFIED_BOUNDED:417ed0 all-seven guard→46d6e8. Bat/Zombie expire; Witch physical loss carries flags fromBall1 toBall2; all seven played at38271. Actual Clock trap remainsnormal; Wolf0(266,153)→phase12 clearsplayed/selectors/ready. Four FREE balls at42101.418ee3 pays21 jackpots including5×7M,5×8.5M and11×10M; fifth counter46d590 resets. Actual2→3→4 refills; already4 yields35M at418f2a twice. Mode Total257.5M. Final compaction2→1 then normal in1step; genuine ramp reselectsWolf3 withallplayedclear.

52904 Original/reset/native/reset/SDL steps, tenvectors/64audio exact.373 instructions added55774total/outside5 unchanged;11PEranges/all retained bytes independentlychecked. Build0warnings/syntaxPASS;11/11CTestPASS199.86s. GPU/Wayland/PipeWire42324step campaignprefix/fourballs/55audio exact, screenshotinspected. Diagnosticcontacts/no rule/played/score/timer/spawn writes. One campaign; Top final admission STATIC only; no whole-table/legal-key-only/raster/listening/realtime/release claim. [Index](../analysis/demon-final-island.json).


## DEMON-VIDEO-058 — Earned moon bank, both video modes and real SDL controls

VERIFIED_BOUNDED: material5 contacts0(30,318/338/358/378) set46d680/684/688/68c;41b3dc completes/clears/arms46d57c.41b500 pays600k first,15.1M when already armed. Repeated one-target flag does not arm; ordinary hit points retained. Wolf4154d4 consumescharge/46d6e4=0, Top415b8a consumescharge/46d6e4=1. Both setGame+44. Brain earlyEnter ignored; selection clamps0..4; positive50M4169c7/negative0. Werewolf actual5M/10M4170ac through left/right keys, then stopshooting/failure; separate idle failure. Both release ball toFREE.

Four Original/reset/native/reset/SDL cases17052steps/elevenvectors/197audio exact. Two actual SDL-event control cases8108steps matchvectors/audio/journal; startup focus release-only tick0 events leave canonical state unchanged. Brain schedule selected from observed cups, not human visualtracking. Source hot draw-call tracing excluded, execution/DMD hashes/reset preserved.

Three Original isolated4017a8 pointer probes resolve shared IDs30/30/27 for463398/463428/46344c; profile PCM SHA and14-profile/3bank/34pass deterministic nonzero tests pass.463428 length intentionally retained one byte beyond sample30 header length.951 instructions added56725total/outside5unchanged;12PEranges/allbytes/fourDATbits independentlychecked. Build0warnings/syntaxPASS;12/12CTestPASS158.39s. GPU/Wayland/PipeWire Werewolf5M and Brain skull-shuffle prefixes exact, screenshots inspected. No whole-table/legal-key-only/raster/listening/physical-keyboard/release claim. [Index](../analysis/demon-video-island.json).


## DEMON-BANKS-059 — Kickback, twelve earned lottery effects and real ball credits

VERIFIED_BOUNDED: material5 skulls0(135,168),(150,162),(166,160)→41b508/46d65c. Paired100ballbytes at1000; armed contact0(16,520) writesvy-3, after80stepsY363.9189 versus uncharged533.5876. Grace250→repeat210 withoutrefresh; expiry2000, expired guard andfreshbank/rearm pass. Right0(300,264/284/304/324/344)→41b5f0/600k/46d6ac. Real elapsed delays0..22 cover12 choices via41511e; both-flipper stop415d68 afterelapsed312. Before415e3b/after415f8d snapshots prove effects, ordinary415fe8 tail retained.

Actual5/10/20M, earned250k bonus collection/base retained and×2, video/Spirit/kickback arms, ExtraBallcredit→physicaldrain/relaunchBall1, +1500saver→physicaldrain→FREE/Ball1 verified. PlayerWORD+0C +8/+5 stays neutrally named. No rule/seed/timer/score/spawn edits; partialbank/global fields differ inpairedcase, not whole-context equality.

14 Original/reset/native/reset/SDL cases43660steps/elevenvectors/230audio exact.642 instructions added57367total/outside5unchanged. SixPEranges/allretainedbytes/nineDATcontacts independentlychecked; build0warnings/syntaxPASS;13/13CTestPASS208.39s. GPU/Wayland/PipeWire kickback and20M-grant lottery prefixes exact, screenshotsinspected. All12 baseline choices only; alternative availability-remapping STATIC. No whole-table/legal-key-only/raster/listening/realtime/release claim. [Index](../analysis/demon-banks-island.json).


## DEMON-VARIANTS-060 — Actual Witch force/rescues, two head pairs and escalating kills

VERIFIED_BOUNDED: earnedWitch node463ae4=1 versus actual-rescued0; same100ballbytes at3000,20steps onXY187.8369/295.2833 versus off175/301.8555. Onphase11/offphase2, notwholecontext equality. Shared40ad80/40aecd node/LUT branchpreserved. Right1(308,594) reboundsvy-4 andendsWitch immediately; left0(10,598) enterssaver/missing-ball flow andreturnsFREE; bothretainBall1/force0.

Twice415486/416209 payfour15M awards overtwoheadpairs; duplicateClock no15M, ordinaryawards retained. Top415b64 doubles2.25→4.5M; repeatguard retains4.5M. Paircompletion resets463bc8/463bc0 andallows5.25→10.5M double; actualbonusdrain407d1e pays11M, nextBall2/base0. Zombie Clock/Top/Wolf raises46d5f0; actualrampreturns4104c6 pay5/6/7/8M.

Five Original/reset/native/reset/SDL cases25160steps/twelvevectors/172audio exact. Newvariant vector includescurrent-player bonusbase plusforce/head/value fields.30instructions added57397total/outside5unchanged.9PEranges/allretainedbytes independentlychecked; build0warnings/syntaxPASS;14/14CTestPASS149.75s. GPU/Wayland/PipeWire Witch3020/Twice6680 prefixes exact, screenshotsinspected. Diagnosticcontacts/no rule/force/score/timer/spawn writes; oneforcecoordinate/twoheadpairs/one ladder, notfulltable/legal-key-only/raster/listening/release acceptance. [Index](../analysis/demon-variants-island.json).


## DEMON-LEGAL-AUDIT-061 — Natural keys, actual ABC save/reload and bounded coverage

VERIFIED_BOUNDED: first nativefeedback policy(threshold440/duration4/side split160) reaches25k at3009. FrozenactualEnter/Shift sequence runsOriginalfromreset, no shot/park calls allowed. Stopflippers afterfirstscore, naturallyfinishthreeballs125k/ABC at10308, F1/relaunch by10512. All10512steps/twelvevectors/31audio exact acrossOriginal/reset/native/reset/SDL. Actualproductionstore writesoriginalearned50-byte record, freshprocess reload/no-rewrite verified in initiallyempty privateprofile. GPU/Wayland/PipeWire10340steps throughABC/GameOver plusactualprofilewrite exact; screenshotinspected.

20 boundedmanualcontracts/36hashedfixtures/eight acceptanceindices, withreleasegateNOT_ASSESSED. Grave value5000/step verified byPE414946..414a33 andruntime samples49.685→48.58→47.475→46.37M, freezesaftertreasure; floor10M STATIC. Sevenplayedflags sufficeforfinal; fifthalready4 pays35M,3→4 refilldoesnot. ActualRetail behavior retained ratherthanforcingmanualwording.

No newOriginalinstructions (57397total/outside5 unchanged); onlytraceobserverpolicy/tooling. Build0warnings/syntaxPASS;16/16CTestPASS314.25s plusfinalaudit1/1PASS0.04s. SearchCMake target reproduceskeys, auditdependsoneight acceptancechecks. Onekey schedule/freshprofile, nothumanphysicalkeys/listening/allmodes-key-only/fullraster/realtime/release. [Index](../analysis/demon-legal-audit-island.json).
