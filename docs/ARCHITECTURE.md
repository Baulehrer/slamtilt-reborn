# Slam Tilt architecture map

## Asset read gate — 071

`build_asset_read_audit.py` creates private header/source copies and wraps labelled liftedRD/WR operations withtheir exact instructionPCs. The audit executable reuses actualPirateSession/replay; source file reads inSDLloaders remain outside its scope. Reads afterDATwrites are excluded from initial-source provenance checks. `classify_asset_read_audit.py` verifies complete originalRaw mask/flipper objects andverifiedPirateframes beforeclassifying differences. Release targets andtheirheaders contain noaudit hooks. Demon adds a separateV3profile; V1/V2 metadata remain unchanged.


## Versioned scene-object adapter — 070

`amiga_dmd_fragments_v2` runs afterRC4normalization. It copies bounded whole raw objects and decodes the13-frame Pirate bank to480bytes perframe, allowing the original overlapping compressed streams. The old decoder/bankmap andprofiles remain unchanged. New*-amiga-v2-startup/mean-amiga-v2-data profiles are selected for newimports; verification andcompiledDAT checks accept exactV1orV2hashes. Existing privateRC4data needs no conversion tokeepplaying.


## Amiga display decoding — 069

`amiga_dmd` expands inner literal/zero runs to logical96×20/two-plane frames; its output precedes the original physical-dot LUT. Offset-only bank mappings feed the existing DMD frontend. OriginalGame hunk0:0x3d8e..0x3e22 and LUTinit0x4f1a..0x4f48 are the bounded runtime oracle. `amiga_contact` reads the MeanRaw animation directory, verifies dimensions/anchors/size and converts three8-plane frames perrecord without palette substitution. Runtime imports use only original ADF contents and native constructors; no oracle/emulator dependency.


## ADF source adapter — 068

`amiga_disk` → bounded SLAM → `amiga_assets`/`amiga_main` → private normalized asset buffers → existing shared-native engine. New trusted profiles are separate from frozen PC profiles. `AssetSource` travels through menu/child environment and highscore namespaces; standalone launches infer source from the import receipt. Source geometry profiles accept only exact compiled normalized-data hashes. Gameplay parity with original Amiga remains UNKNOWN.


## Native DAT-only initialization — 067

- `assets/native_math_tables.cpp` constructs sin/atan/geometric-flipper/force tables;17 explicit quantization compatibility cases. Full56,232byte math island exact.
- `assets/native_retail_data.cpp` builds zero-based data ABI using captions, SampleDefinition/LampDefinition records, native neutralparameter records and logical callback directories. Original code/headers/IAT andraster/audio assets omitted. Complete initialized shared/table island75,244bytes exact; code-address-space only contains explicit callback-ID directories andcollision masks used asdata.
- `import_mean`/`import_retail`: emptyEXEpath selects native initialization+userDATs+bounded startup scalars; explicitEXE retainsold extraction. Mean normalized profile unchanged; three new*-dat-startup.json profiles pin nativeinitialized states. PirateSession trusts anadditional exactnative-context hash, retainingold full/physics contexts.
- Shared/standalone choosers defaultto DAT-only andaccept DAT folder orparent. Native profile generation needsconstructor+DATs, noEXE. Private generated compatibility images remain data containers forcompiled routines, not distributedOriginal snapshots orruntime instruction decoders.

[Evidence](../analysis/dat-only-island.json), [current data requirements](dat-only-import.md).

## Mean Retail input normalized to native data ABI — 066

- `assets/mean_import.cpp`: import_mean dispatches by supported EXE SHA to Demo or Retail recipe/profile. Retail copies only six data ranges/60,640bytes and applies124 source-expected pointer fixups; no runtime instruction decoder. Existing startup scalars and native Mean code reference ABI retained.
- Retail4556cc..463274 maps byte-exact to Demo42a144..437cec (56,232byte math lookup island). Retail403fb8..403fd8 maps to Demo403fe8..404008 inline DWORD masks consumed by409060/40906d. Remaining ranges cover strings/nudge/Mean descriptors. Details in `analysis/mean-retail-readset.json`.
- `verify_mean_data` accepts either trusted eight-file profile; old Demo output hashes preserved. Shared Retail import includesMean, standalone chooser and installed runtime carry both profiles. WindowsEXE is an import data source only; originalEXEs masked during verified play. DAT-only first import remains a separate task.

[Evidence](../analysis/mean-retail-island.json), [data requirements](data-import.md).

## Reborn presentation and runtime ownership — 065

- `frontend/reborn_menu.{h,cpp}` owns original-preview textures, modern chrome/cards/DMD decoration and hit regions; optional Classic rendering reuses verified MENU.DAT. New optional settings `modern_menu`/`reduced_motion` retain preference version1 compatibility.
- `frontend/frontend_runtime.h` centralizes table catalog, SDL base path, configuration recovery, argv construction, child process lifetime and transactional three-table import. Shared parent owns selection/options; existing Mean/Pirate/Space/Demon child engines remain separate.
- Same asset-free shared archive built with pinned Debian12/GCC12; native importer/profile recipes bundled. Real compositor lifecycle, deterministic gameplay, older-runtime execution and wall-clock timing have distinct evidence, avoiding inferred cross-platform/whole-game equivalence.
- Demon callback 0x410ea0..0x410f18 extends bounded Original closure by41 instructions to57,438, with five existing outside calls unchanged. Pirate comparison explicitly restores original user Shift bindings; no native physics modification.

[Review](reborn-review.md), [QA scope](reborn-playtest.md).

## Shared native frontend and Original menu asset — 064

- MENU.DAT pixel0xB2BC8,640×480bottom-up indices,RGBpalette0x32ECF8. OriginalPE40C23A..244/40DB0E..19 andindependentRGBhash establishassetformat. Native selectionrectangles followartwork visually; notOriginalinputRE.
- slamtilt ownsSDLselectionwindow andchildprocess lifecycle; directlylaunchesslamview Mean/Pirate orslamslice Space/Demon. No gameplaydispatch changes. Sessionenvironmentenables PortOptionsMainMenu/F10→SDLquit, thenparentrestoreswindow.
- ExistingSHA-boundimporters reusedinprocess: oneRetailfolderimports3tables; separateMeanDemoimport. frontend.json storespaths/lasttable, existingoptions.json shared, highscoresremainpertable. Combinedbundleuses Runtime+FrontendRuntime, profiles/recipes/libraries; nooriginalassets.

[Evidence](../analysis/frontend-island.json), [Frontend](frontend.md).

## Demon RC identity and capabilities — 063

- Demon TableGameplaySupport::Playable now exposes the same supportedRetail executable binding asPirate/Space; metadata CTest assertsit. No simulation instruction changes.
- Completion generator promotesonly after theindependent releasegate passes. Gate pins archive/evidence/actual archivedmember hashes, isolatedpackage, DebianABI, realtimeaudio, all36manualfixtures andRCmetadata/runtime identity. Three malformedindex cases reject.
- Packaged Original equality usesSHA-pinned source sequences and exact numeric array equality (existing oracle semantics); integralJSONfloat serialization can differ fromC++ without a statevalue difference. Original hashes remainunchanged.

[Evidence](../analysis/demon-rc-island.json), [Gate](../analysis/traces/demon-rc-gate.json).

## Demon native data and standalone path — 062

- Existing shared Retail importer now accepts Night of the Demon using its SHA-bound recipe. PE sections/BSS plus DAT canvas/MAIN copies and bounded startup scalars reproduce canonical image/runtime. Shared Pirate/Space layout and wrappers preserved.
- Dedicated slamdemon-import/slamdemon-setup and launcher use demon-prepared/ and separate demon-data-path preferences. SDL options/audio/presentation and production score storage reused. DemonRuntime CMake component bundles only program/libraries/metadata/licenses.
- Debian12 offline build and isolated import/session pass; packaged realtime GPU/audio matches twelve Original vectors. No physics/rule/decoder changes.

[Evidence](../analysis/demon-release-island.json).

## Demon legal input/storage path and release gate — 061

- Shared200Hz input/physics already supportnatural scoring. Threshold440, short4-step pulses, side-dependent flipperfeedback reaches25k at3009 usingordinaryEnter/Shift events. Original naturalgame records125k/ABC andF1/relaunch; no replacementphysics orrulepatch needed.
- Demon raw rule-window tracing is now independent ofdiagnostic-shot mode. This permits twelve-vector legalreplay plusactual production highscorefile save/reload. Diagnostic profile-protection staysunchanged. Existing50-byte store/atomicwriter reused.
- Machine ledger pins20 boundedrulecontracts to36fixtures/eight acceptanceindices. Grave time-decay andfinal played/fifth rules retain observedRetail behavior. Separate unassessedimport/package/ABI/realtime gatekeepsGameplayPreview despite completeboundedmanual coverage.

[Evidence](../analysis/demon-legal-audit-island.json).

## Demon mode-variant state and original force node — 060

- Witch41a24c enables WORD463ae4 in the existing463ae0 node. Shared40ad80/40aecd consumes node/ball/LUT; no native force formula was invented. Right layer1(308,594)→41b7b0/41b83c returnsvy-4/phase2; actual leftoutlane uses missing-ball/saver return. Both clear463ae4 andretainBall1.
- Twice Clock/Wolf guards use463bc8 bits1/2; Top usesbit4 anddoublesplayer+8. Completedheadpair clears463bc8/463bc0, allowingbothheads andbonus again. Two full cycles andactual11M bonuspayout areverified. Zombie46d5f0 rises atClock/Top/Wolf; paidrampvalue follows5/6/7/8M.
- New diagnostic variant_state observes nodeenable/globaldisable/playerbonus/headpair/headflags/value/modetotal andparticipates in independent reset. Twelve vectors now cover the previously unobserved current-player bonusbase. Gameplay remains Original lifted engine/code.

[Evidence](../analysis/demon-variants-island.json).

## Demon physical target banks and Clock lottery — 059

-41b508 clears46d660/664/668 and arms46d65c.419567 material4/Y>490 ignoreszero, convertsnegativecharge to250, preservespositive grace and writesvx0/vy-3.417bdd decrementspositivecounter on50Hz callback.
-41b5f0 clears46d66c/670/674/678/67c, pays600k and arms46d6ac.41511e consumescharge and selects46d5d8 from absoluteGame+38 and conditional denominator/remapping. Both flippers Game+54/+58 stopspin415d68 after minimumelapsed.415e3b..415f8d applies12 effects;415fe8 then preserves ordinaryClock capture awards/counter.
- Existing integer engine, audio and eleven-vector observer reused. Bonus/ExtraBall/BallSaver effects observed directly; playerWORD+0C changes8/5 retain neutral naming. All12 baseline choices are runtime-verified; unavailable-entry remapping isSTATIC only.

[Evidence](../analysis/demon-banks-island.json).

## Demon video and shared sample descriptors — 058

- Material5 consumer41ade1/41af19 classifies four left targets by Y bands;41b3dc clears46d680/684/688/68c and arms46d57c. Wolf4154d4 and Top415b8a consume the charge, setGame+44, and select46d6e4=0/1.
-416a0c/416b70 handle both video families. Brain bounds46d584 to0..4 after46d594 becomes negative;4168c8 confirms against46d554..564 and pays50M at4169c7. Werewolf left primes/right fires;4170ac pays5M per increasing kill count. Original416d6c callback draws/advances video; no replacement minigame implementation.
-4017a8 resolves shared sample IDs1-based, then header+8+descriptor offset. Video descriptors463398/463428/46344c map to DAT5bbd8/5d4d8/4b040; direct pointer0 is valid for shared records. Existing three-bank libxmp/mixer reused. Diagnostic Game10/14/18/20/44hex observer extends reset verification to eleven vectors.

[Evidence](../analysis/demon-video-island.json).

## Demon final campaign dispatch — 057

-417ed0 checks the seven played DWORDs46d69c/6a0/6a4/6a8/6b0/6b4/6b8 and sets46d6e8. Wins are unnecessary. Runtime Wolf trap→4166e0/41670f clears flags/selectors and entersphase12; Clock-trap guard does not admit. Top alternative is STATIC only.
-414d1d/463b88 stage initial three extra-ball requests; actual pool reaches four FREE balls.418eb0 pays7M/8.5M/10M at2/3/4 active balls.46d590 counts five; below4 refills once, already4 pays35M. Last-ball return414d99 follows compaction by1step.
- Existing shared integer engine, rendering, audio and ten-vector observer reused;373 Original instructions extend the native closure. One campaign/rearm proof, not all Demon rules or whole mutable-state coverage.

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

SPACE-ASTEROID-040: two Original/reset/native/reset/SDL fixtures /31,716steps. Allfour actual trapcaptures1/2/5/3 pay5/5.5/6/6.5M plus500k each; ramp no-Asteroid guard,exact12001-tick expiry,played flag acrossball2/3 andF1reset,46M/ABC/GameOver pass. All100ballbytes,clock/phase/DMD,poses,lifecycle/highscore/lamps and1536rawstatebytes match. AllSpace4/Demon3 layerhandlers seeded fromverified directories; +1041compiledinstructions,44802total,outsideboundary unchanged.7/7 affected CTests PASS35.73s;build0warnings. Extra20M return4413d5 preserved,meaning UNKNOWN. Diagnosticcontacts,notkey-only/allrules/fullraster. [Evidence](../analysis/space-asteroid-island.json).
Next: Port and verify the remaining three Space mission chains (Space Race,Hack the Net,Blam) as one shared mission-family workpack.

039: Native Retail gameplay now shares one static C++ intermediate across Pirate/Space/Demon. `src/frontend/retail_slice.cpp` validates selected-table context/DAT hashes and reuses all-table graphics decoders. Space/Demon are bounded GameplayPreview, not complete-rule acceptance. Table IDs1/2/3/4=Mean/Pirate/Space/Demon; shared highscore binding46c498=46c510+50*(ID−1). Space upper flipper is left-controlled (`graphics+1c==ffff`); Pirate is right-controlled (`==1`). See [039](../analysis/retail-gameplay-island.json), [Space anchors](../analysis/space-entry-anchors.json).

Pirate 038: PLAYABLE_RC. Manual audit links 24 rule contracts to 56 SHA-pinned Original fixtures / 372,660 retained steps; 48 semantic checks rerun. Closed the concrete auto-Knife gap: left/right only during video, 25 kills / 75M / collected Extra Ball, 13,076 Original/reset/native/reset/SDL steps, 74 audio events exact. Pirate capability now Playable with Retail SHA (Mean stays Demo; Space/Demon viewers); removed Preview captions. Asset-free GCC12 RC1 built and verified under actual Debian12: raw import/selection,25,792-step game plus90,340 rule steps/all10vectors; relocated archive and12 actual Wayland/PipeWire window/fullscreen event tests pass. [Evidence](../analysis/pirate-completion-island.json). Bounded diagnostic feature coverage is not all-feature key-only/full-raster equivalence; undocumented Battle3x admission remains UNKNOWN.

Pirate rule035: fixedactualPlank30Mfeedback callback42eb6c,previouslymissedregisterpush432388/432390/4323c8. Oldreleasefailed4099;now271dispatches/51DMDframes exact. +211compiledOriginalinstructions,24118total/outsideboundary unchanged. Fourchains26008Original/freshreset/native/reset/SDL10vectorsteps:PlankSJ,Piranha10×2Madditions/11thnormal/rearm,1/2/4/6/8/10/12bonusladder/cap,20.7M×12payout/nextballreset. Allfour alsoGCC12/actualDebian12 pass.82uniqueaudio cases/6215requests exact acrossmain81+scoped1;retained78rows unchanged. Fullbuild0warnings;two4/4CTestbatchesPASS209.10/34.58s. Ready:`build/compat/releases/slamtilt-pirate-rules/slampirate`. Diagnosticphysicalwaypoints,notallkey-onlyall-featuregame. [Evidence](../analysis/pirate-rule-island.json).

Pirate fullreal-time034: nativeGPU/actualwallclock legalCrocodile replay15600steps/78.026s andtwofinitegames25792steps/128.986s matchall10original vectors;597audio requests exact,0timeclamps. Threecompletegames/3F1 continuations; firstnaturaltrajectory overlaps. Cave/Cannon/2ballJP/15.83M/ABC/GameOver/F1/freeball pass,plusactualprivatehighscore persistence andfreshprocess50byte reloadwithoutrewrite. Newexact-tickbound supportsnon4multiple37step test. Freshoriginal15600retains9vectors/addsMSstate; no newRE/physics.4/4CTestPASS14.43s,oldABIandmodernbuild0warnings,actualDebian12regression retained. Ready:`build/compat/releases/slamtilt-pirate-fullgame/slampirate`. Notwholeoriginal raster orphysicalinput/audio listening/all-mode acceptance. [Evidence](../analysis/pirate-full-realtime-island.json).

Pirate real-time/cache033: preload75ball shading groups once; conditionalLampstate/actualflipperRGBA/DMDcolor texture uploads. 1000fixedframes/4000steps preserve10vectors/camera/fullBMP byte-exact; uploads58000→2974,MAINopens1002→3,perballrenderfileIO0. All600Ypixels matchprior decoder. RealWayland/GPU4secondruns/window+fullscreen:799steps,acceptedclockresidual<5ms,0clamps;8queuedpresses permode reachposechange inlowmilliseconds. Rendercallwallp95~0.82–0.86→0.16ms; loopintervalnotphysicalrefresh,not CPU/GPUcounters orphysicalinputlatency.5/5CTestPASS17.58s,12finalpackagehostcases pass,olderABI fullgame unchanged. Newready:`build/compat/releases/slamtilt-pirate-realtime-final/slampirate`. [Evidence](../analysis/pirate-realtime-island.json).

Pirate older-Linux ABI032: same immutableMean Debian12/GCC12toolchain reused offline/sourceRO. MaxGLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9. ActualDebian12glibc2.36 imports4exactfiles withnativeUI/PATHempty; rememberedstart/SHA/audioNudgeSpecial pass.25792steps/10vectors/6448camera frames/364audio requests exact. No sourcecheckoutmount,program/raworiginalsRO,networknone. Relocatedarchive/currenthost and12Wayland/PipeWire actualwindow/fullscreen cases pass.4/4regressionCTestsPASS31.99s; ownbuild0warnings. Ready:`build/compat/releases/slamtilt-pirate-bookworm/slampirate`. Sharedhostkernel; otherdistros/drivers/physicalAltTab/listening unclaimed. [Evidence](../analysis/pirate-compat-island.json).

Pirate host031: observed actualfocusgain526/mainwindow4 after scriptedloss527/id0 explains frame2failure. Test-only SDL_PumpEvents beforeinjection fixes event order; no ignoredOS events/removedfreezechecks/audioorphysics changes.12source+12packaged realWayland/PipeWire runs and6dummy cases pass audio/Nudge/LeftCtrl focus/minimize/pause/options/mute/reset/repeat/remapping gates. New --fullscreen enablesgenuinefullscreenwithframes; earlier030attempts werebothwindowed.4/4CTestsPASS30.00s,fullbuild0warnings. Relocated25792steps/10vectors/6448camera frames/364audio requests unchanged. Ready:`build/releases/slamtilt-pirate-host/slampirate`. PhysicalAltTab/listening/otherdrivers/olderABI remainunclaimed. [Evidence](../analysis/pirate-host-island.json).

Pirate firststart/package030: same `mean_setup.cpp` compiled withSLAM_SETUP_PIRATE toslampirate-setup; native verify_pirate_data/recipe andimporter4filehashes. `pirate-data-path.txt` andpirate-data-* separatefromMean. Launcher savedpath/--setup/explicit--data/--check; installed importerrecipe ../share/slamtilt. PirateRuntime component installs3binaries withrelative$ORIGIN/../lib; package includesSDL3/libxmp/font/stb/port licenses andmetadata, nooriginaldata. Relocatedarchive tests andMean regressions pass. Historicalfocus-test failure resolved031 with observed event-order evidence. [Evidence](../analysis/pirate-firststart-island.json).

Pirate raw-data path029: native `slampirate-import` reuses existing PE/SHA/staged-publication helpers; exactRetail SHA only. Fouroutputfiles: PIRATE.DAT,MAIN.DAT,pirate-prepared/human-{image,runtime}.bin. Graphics/Main/code copied from originals;341image+1runtime scalar initialization and600damage rows recreate frozen context,not original fullstartup. No runtime Python/Wine/emulator. Existing8fileMeanimport unchanged. Source launcher accepts --data. Full imported finitegame/camera/audio pass. Lamp/flipper audit nowcoversall27angles×4patterns and4fullcanvas states,zeroRGB/alphaerrors. [Evidence](../analysis/pirate-import-island.json).

Pirate presentation028: `renderer/pirate_camera.h` replaces direct ballY−260 SDL follow with original409350 dynamics/lowest projected WORDY/state6fallback/GameOver pan;40549a residual interpolation.200Hz camera consumes previous rendered projected positions; presentation state stays outside verified gameplay machine. Actual F1 retains camera,forcedRreset clears it.9000original states/45000x87values and6448SDL frames verified;25792gameplay steps retain all10vectors. Native rendering cadence is the declared input boundary; no complete original raster/scheduler claim. [Evidence](../analysis/pirate-camera-island.json).

Pirate repeated-game acceptance027: shared engine survives24legal-input policies/520244native steps/48F1 continuations. Three selected Nudge/Tilt/Crocodile traces62576steps match original/freshreset/native/reset/SDL all10vectors, no waypoints. Original405234step/40404cinput/405d54initials/408ae0newgame reused; canonical46c15c pool and46c6acphase unchanged. Each run preserves clock/RNG/highscores across two actual F1 restarts. Native-only breadth and original-proven subset remain distinct; no engine instructions added. [Evidence](../analysis/pirate-acceptance-island.json).

Current2026-10-22 — **Pirate native composed finite campaign verified**, full table remains `GameplayPreview`; Mean accepted, Space/Demon `ViewerOnly`. Shared `TableDefinition` validates4 Retail asset identities,103flipper frames and216lamps/432frames. No cross-table physics equivalence inferred.

`PirateSession`: explicit original image/runtime/DAT, bounded statically compiled C++ intermediate under `build/generated/`; no runtime CPU decoder. Original405234 runs200Hz physics/40950c and50Hz435414/407b88 plus RNG/nudge/camera. SDL supplies separately verified interpolation. Canonical balls46c15c+i*100, pointer table454b68, are required because408d78 writes canonical ball state directly. Unsupported calls throw.

Same-game Pirate magnet acceptance: unchanged54760step4MB/6playedAdventure/TreasureIsland prefix→actualCave/lane/toptrapMagna admission55057→Mermaidbank1M→4M via4383de→pairedtargets/righttrap earnstandalone55485→LeftCtrl55486/typeFFFFforce802steps→expiry56288→leftShift56486..56606/realreturn. No placement after55486;ABC/1.498782380B/GameOver65040/F165104/freeball65310.65392original/reset/native/reset/SDL10vectors exact.5fieldMagnasaver vector SHA-pinned in compactpublicfixture,fullvalues private. No new originalinstructions;23907unchanged.75audiofixtures/5503requests exact. Diagnostic physical entries explicit. [Evidence](../analysis/pirate-campaign-magnets-island.json).

Composed finite Pirate acceptance:54760step4multiball/6playedAdventure/TreasureIsland prefix remains bit/hash-identical; only13actual original actions follow. Natural bonus/ball2/ball3→ABC/1.486839210B/GameOver62640→stable64→newgame62704→freeball62910. All62992steps original/reset/native/reset/SDL9vectors exact; includes bigscore highscore handling. No new original instructions;23907total. Diagnostic prefix retained, Magna systems integrated byPIRATE-MAGNET-CAMPAIGN-026 below; not a fully legal-key-only campaign.74audiofixtures/5221requests native/reset exact, fullnewcampaign SDL requests exact. [Evidence](../analysis/pirate-campaign-finite-island.json).

MagnaTable capture: actual layer1switch2 at17/81Y resolves capture/exit; rectangle predicates43810c do not imply bitmap reachability.431d95 admission follows52step uppertrap hold: input2760→window0/init2812 admitted;input2761→windowFFFF/init2813 rejected.433b07 holds150200Hz calls,then465a68=10 and11eligible50Hz decrements→−1;42bae4 rejects >=0 or occupiedstate3/6-sub6. Tilt rejects capture but bypasses an existing hold without cooldown10.7fixtures13940steps9vectors exact plus5real-context native/original read-only leaf cases. No extra original instructions. [Evidence](../analysis/pirate-magna-capture-island.json).

Standalone Magnasaver: linked force descriptor465848/typeWORD46584c=FFFF uses original40ad80. Actual paired entry25,530 is lifted; active force runs804steps through2004, then LeftShift2200..2320 returns the ball aboveY400/free through2800. Timer4355c9 expires after201eligible50Hz calls; new earned charge reloads200 even whileactive. Tilt40ad8b blocks force and435428 freezes timer without clearing record; nextball435718 resets earned/window/force. `magnasaver_state()` exposes five raw original fields only for optional full-state/diagnostic traces.7fixtures/21904steps exact original/reset/native/reset/SDL10vectors, no extra original instructions. [Evidence](../analysis/pirate-magnasaver-island.json).

Final direct DMD/input bundle: all43targets in57enumerated immediate-push registrations now compiled, total23907instructions; computed/register-pushed targets excluded. Four actual threshold/Magnasaver/multiplier/right-outlane events add9104original/reset/native/reset/SDL exact steps. `PirateSession::special_left()` preserves original404a7c Tilt gate and invokes actual404ab4 descriptor+4c4341dc; original callback guards earned46e536 and enables46584c/window46e552/lamp46e450, then4355ef expires it. DefaultLeftCtrl is seventh configurable action; six-key profiles preserve all mappings, conflictingCtrl gets free fallback. RightCtrl callback434264 is original no-op. Actual SDL gating/remapping and59audio fixtures passed; physical rescue is now verified byPIRATE-MAGNASAVER-023. [Evidence](../analysis/pirate-final-feedback-island.json).

Display island: compiled406938 registration priority gate and407c09 dispatch are reused. Wait for original DMDidle before actual Swordfight/Dive/Monkey events; six formerly uncompiled messages now run as original static C++ (+695instructions,23327total),12124event steps exact. Native scene origin consumes nudge_state[9] signedX pixels and[7] signed16.16Y; actual original x87405486,sourceclamp4035af andCOM sourceRECT402e58 establish negative scene displacement andmaxScroll+8clip. One common origin translates table/lamps/flippers/balls; DMD/options fixed.63original renderer contexts,12fullNudge/Tilt traces and legal PlankNudge13400steps/96×18fields pass. [Evidence](../analysis/pirate-feedback-display-island.json).

Natural Plank rope follow-up: unchanged5600-step prefix, right5696..5720 then left6664..6688 earns inner-ramp rope4at6763. Fresh left7128..7136 sends the real ball into layer1right-ramp endpoint, rope3at7298. Original436c78 awards10M plus existing250kbase and adds400timer ticks on each distinct hit; five flags become[1,1,1,0,0]. Finite17.53415M/28.18415M games including ABC/F1/next ball match26200original/native/reset/SDL steps. DMD42ee48 via407c09 now compiled106instructions(22632total),104dispatches per retained rope animation. Offline inspector exposes read-only flight fields, search accepts1..5distinct-rope goal; no live UI state restore. [Evidence](../analysis/pirate-plank-natural-ropes-island.json).

Natural Plank now runs via Enter/rightShift periodic40-step policy: arm1750 while selectedAdventure4, ordinary bumper selection cycles toPlank0 before phase5 at4104. Original guide24/capture5,50-count hold and Plank intro release at4932; actual drain6093 withtimer10839, then6.08415M/ABC/GameOver10240/F110304/free ball11519.11600key-only original/native/reset/SDL steps exact. Targeted DAT evidence identifies layer0ramp ingress230pixels→layer1endpoint170pixels→upper-left gate1047pixels. This initial fixture ends at drain; the follow-up above proves two natural ropes. Old diagnostic five-rope success/timeout still pass. Ordinary gameplay additionally exposed DMD42e140 via407c09; complete201call cycle proven,142instructions compiled (22526total), no added force/rule semantics. [Evidence](../analysis/pirate-natural-plank-island.json).

Natural Crocodile: the verified legalCave prefix runs unchanged through5400; releaseLeft5400, bothShift ON5574/OFF5582, freshLeft ON6168/OFF6169. This actual40ms stroke reaches34-pixel layer0switch3, Cannon5805, original angle2024/physical catch then mode4 at6351; two free balls7090,5M JP7623, pool compaction9432, normal return11112,15.83M/ABC/GameOver14240/F114304/free ball15519.15600steps match original/native/reset/SDL with zero waypoint events. Offline `PirateSessionSearch` copies complete silent reachable machine states via a narrow peer; hooks/audio are rejected, deleted ordinary copy/move remain. The proof never restores checkpoints. No new gameplay instructions(22384 unchanged). [Evidence](../analysis/pirate-natural-croc-island.json).

Pirate ordinary legal gameplay now covers three naturally earned Cave locks at1317/4517/7717,5.145M/ABC/GameOver10080/F110144/free ball11517.11no-waypoint fixtures/65068steps match all observed original/native/reset/SDL vectors. Actual407c09→[46c69c] dispatch exposes10new DMD callbacks (including ShootMagnaTable/MermaidBonus);43522f→service+54 reaches406650 bonus-control field update. All11 routines compiled,917instructions; no runtime decoding/stubs. `--full-state-trace` hashes rules/video/pool independently of diagnostic waypoints. The10lock-count combinations now have retained/new native proofs, including intermediate Crocodile3/4 and Storm4. [Evidence](../analysis/pirate-legal-gameplay-island.json),[matrix](../analysis/pirate-lock-matrix-island.json).

Pirate Nudge/Tilt: SDL bindings LeftAlt/RightAlt/Space route only nonrepeat gameplay actions to original4049e3/404a25/404a67 semantics: pending454af8/454aac then compiled405eec. Existing405234 accepts the pending request and4070bc applies original wave/force tables.46c6e4+=40, decay1/20ms;42..81 warns through4344c8(EAX0)/42bd08,>81 sets46b764 and releases three flippers and sets lamp command bytes to2 before4344c8(EAX1). Physical wave remains accepted while Tilted; scoring/mode timers are inhibited, next-ball408410 clears Tilt.12fixtures/45844steps prove original/native/reset/SDL, including held Magna/Crocodile and Knife exits.Two dynamically observed service+74/+78 responses included; total21172→21467. Original scene motion is now implemented;seePIRATE-DISPLAY-021. [Evidence](../analysis/pirate-nudge-island.json).

Original startup404f09..404f62 binds table/lamp/palette pointers; Pirate index2 plus404ebf..404ee6 selects highscore table46c542. Original408da8 consumes commands and actual40b0b4/40b2ec raster routines; shared native lamp RGBA uses descriptor+8 on/off. Flipper40b518 source is frame-indexed but descriptor+20 lamp mask is not; native RGB=source AND NOT mask, pristine foreground alpha retained. Actual original blits and native pixels compared, including parents.

Original player record46b620+24*(index-1), packed BCD score+0..5, ballnumber+0e, extra credits+10. Initials admission phase3/46c61c=6;405d54 accepts original scan codes;405de8 inserts6BCD+3initials+NUL. Native JSON persists50bytes in a private Pirate profile. Original408ae0(F1) admitted only phase0, retains running clock/RNG; diagnostic reset is separate.

Walk the Plank (Adventure0): right-ramp switch arms46e2de/4659c0; upper-left guide4340ca captures and4332d3 sets phase5, played flag and five rope bytes46e564..568. Original436c78 consumes distinct targets; all five arm46e556. Capture2 branch43234c awards30M and4366b4 returns to phase2/next selection. Timer46e546 runs at200Hz. Return-lane switch438cdf clears shared field46e560; diagnostic skipping of this transit must not be mistaken for a missing release routine.

`PirateShotReplay` is separate from legal key replay. It binds actual DAT layers and repositions only free balls, invalidating the previous switch cache; no rule/score/timer/capture/callback injection. Explicit CLI diagnostics are labeled and cannot persist scores. Two trajectories (1812 success/13524 timeout) match original/native/reset/SDL, including all864 bytes46e220..46e57f per step. Evidence: [pirate-plank-island.json](../analysis/pirate-plank-island.json).

Four further Adventure contracts now reuse the same physical events and original engine. Selector436508 is reached by actual bumper material3 collisions at169,38; no selection-field write. Swordfight (id1) uses DWORD46e2a8 for repeatable5M jackpots,250k bumper/target and500k upper-trap growth. Dive (id2) uses WORD46e54a depth/46e54c rate, clamps at100, then original30M collection. Monkey (id3) uses WORD46e544 next target and DWORD4659a8 piece count, order1→2→3→4→0. Shark (id4) uses WORD46e55a pending speed: net+7timer ticks per pending step, escape at raw6970/50M. Seven separate original/native/reset/SDL cases,47256steps, all100ball/864rule bytes plus clock/lifecycle/display/lamp/highscore states match. Evidence: [pirate-four-adventures-island.json](../analysis/pirate-four-adventures-island.json). This is individual diagnostic mode coverage, not a legal-key-only all-mode game.

Knife Throwing (Adventure5):433739..433917 sets engine+44/video and holds the physical ball;407bbc dispatches4349f0 at50Hz. After364 intro frames, original player movement46e29c/46e294, eight knife slots46e0b4 and five opponent/projectile slots46e278/46e264 drive colored DMD pixels. Existing Shift/Enter callbacks work; crossing an active opponent also throws automatically.25kills award75M;42fb54/42fd1c complete win/lose and return to phase2. Success increments pending Extra Ball46e2d8; right-trap437388 consumes it into player+10, upper trap does not. Two original/native/reset/SDL cases match15648 steps, now also hashing892 video bytes outside the864-byte rule block. Diagnostic table entry/post-video traps; exclusively legal keys during video. [Evidence](../analysis/pirate-knife-island.json).

Crocodile: actual Cave switch3 at43,198 captures4/432c84 and increments lock WORD46e2bc; two locks plus top trap86,10 enter cannon phase6/432075. Original434418 key launches real ballistic flight; Mermaid capture3/43260c starts phase4 and increments played-multiball WORD46e2be at entry.408ce8 allocates second ball;43683c pays5M, Cave adds1M, next target pays6M. Original rescue expires; after count2→1,43163c waits800physics steps before normal phase2. Cannon miss decrements locks2→1.8908 original integer-oracle/native/reset/SDL steps match all800canonical ball bytes,864rule/892video bytes and clock/display/lamp/score states. [Evidence](../analysis/pirate-multiball-island.json).

Shared boundary correction: render preparation40566f→408674 owns state5 pool compaction. Native runs only integer prefix408674..4086d4→original epilogue4089cb at50Hz independently of lamp enable. Interpolation/visibility/sorting remain SDL; full original raster state equivalence is not claimed. Retained context lacked46b778 sine-service binding because46c66c was assigned after startup; original405b6a..405b78 and native reset now complete that exact pointer assignment. Snapshot hashes stay pinned. Diagnostic waypoints may select an active free ball0..7, with runtime guards; per-step800-byte pool hashes cover unused records too. SDL follows the greatest eligible ball Y as40938c does, retaining its existing viewport policy rather than claiming the original inertial curve.

Four-multiball campaign now composes Crocodile→Storm→Battle→Mutiny without ordinal/rule writes or reset. New init branches432807/4328e3/432a32, jackpot consumers436a4a/436b05/436bbd; five flag bytes46e569..56d clear current and always light next, even for unlit hits. Cave adds1M; initial10/15/20M becomes11/16/21M. Actual minimum-lock Windows release yields3/4/5 FREE balls, while handbook lists3/3/4; no cross-version behavior inferred. Nine observed4086c1 source/destination SHA pairs prove real slot0 replacement3→2→1,4→3→2→1,5→4→3→2→1.25780 original integer-oracle/native/reset/SDL steps exact, frozen Crocodile6400 prefix included. Only701 compiled instructions added; all physics and native render/input adapters reused. [Evidence](../analysis/pirate-multiball-campaign-island.json). This covers core chains; Battle upper triple-JP admission and surplus-lock variants remain unproved.

MagnaTable: one actual Cave lock plus left lane34,468 arms400-frame window; upper trap initializes431d95 without phase change. Shift callbacks434268/434340 set original type2 force descriptors465864/465858;40ad80 applies original integer LUT force. All12 reward targets4380dc verified through actual layer1switch2 captures, including direct/pending Extra Ball, mode light,5/10/20M, Hold Bonus, Ball Saver,5 Cave locks, Mermaid growth and Kickback. All three slots, no-lock/expiry guards, full intro/skip, no-award exit and two1800-step key-only flights pass.20 fixtures/40876 integer-oracle/native/reset/SDL steps exact; only289 compiled instructions added. Follow-up below verifies one key-only reward and the earned-state fallback gates. [Evidence](../analysis/pirate-magna-island.json).

Magna eligibility/capture follow-up:431eba skips LITE MODE if already lit or all6played, falling through20M;431f44 excludes HOLD BONUS for nonzero WORD[player+0x14], falling through10M;43202a excludes activeKickback, falling through5M. Actual earned HoldBonus/Kickback persist through Crocodile/drain/newCave to Magna reentry; all6 case freezes48328step final-earned prefix. Four64560step original/native/reset/SDL traces prove exact candidates/captures/points. Native bounded63-policy search additionally found OFF/ON both magnets every120steps; original independently confirms468free steps→5M capture1820→return1970. Full2052step trace matches native/reset/SDL, last diagnostic waypoint1209. Existing21172 compiled instructions suffice. All25Magna fixtures/107488steps bounded; all-played collects slot0, later display priority/guard boundaries unproved. [Evidence](../analysis/pirate-magna-completion-island.json).

Treasure Island campaign: frozen25780-step four-multiball prefix→six actual Adventures→final→new Plank cycle,54760 integer-oracle/native/reset/SDL steps exact. Eight actual free balls (handbook4),15M→16M JP, duplicate/unarmed guards, target sweep and15/47/80M Super Jackpots;284M beforedrain,300M afterone further16M. Seven slot0 compactions8→1, progression reset, actualreturn-lane gate andnextPlank entry/release/completion verified. Only149 compiled instructions added; no productionphysics/render/input changes. [Evidence](../analysis/pirate-final-island.json).

Surplus locks: original432d66 caps Cave count at5; actual sixth capture cannot increment. Initialization432751/432811/4328ed uses base5/10/15M+(locks−2/3/4)×2.5M; Mutiny stays20M at its five-lock minimum. New29844-step campaign composes all4 modes with5actual free balls each, Cave+1M and16slot0 compactions/returns. All sampled bytes/hash vectors match original/native/reset/SDL; existing21172 compiled instructions suffice. Battle46e556 watchpoint records only clear43295e (and Mutiny432a98) in this run; unarmed upper trap yields500k and no JP collection. Triple-JP admission remainsUNKNOWN, no flag injection. Call-edge collection is selected-event-only; full state replay remains complete. [Evidence](../analysis/pirate-surplus-island.json).

Pirate audio: initializer42b4d3..42b4f1 binds DAT+51876/+568e8; same stripped-STIM layout/shared31-sample directory as Mean.15 descriptors464f18..465134 give direct/shared PCM slices and periods160/226/300/452. Optional read-only call observer in compiled dispatcher captures original406600(SFX5c),406240/40621c/4061c4(music84/88/90),406268/4061f8(cancel80/8c); original state writes still execute. Retained pre-step base request454a64/68 explicitly seeds native music0/0. No rule-to-sound guesses. Parameterized existing bank parser/sample mixer and original-priority libxmp sequencer feed SDL; per-bus gains, focus/minimize/manual pause/options/mute and reset handled.1015 requests/20fixtures/183760steps match original/native/reset; legal finite/final SDL sequences exact.60 original44b640/44cc00 mono PCM cases exact under explicit6voice/full64/master65536/SFX10 fixture. Final original stereo/device/PCM timeline and physical listening remain unproved. [Evidence](../analysis/pirate-audio-island.json).

VERIFIED retained12000step legal three-ball/bonus/ABC/GameOver/F1/second-game chain: original/native/reset/SDL100ballbytes,11clock/RNGfields,15lifecyclefields,DMD/highscore/53lamp hashes each step. Core mode composition is now verified diagnostically. Magna boundary/inhibit/cooldown variants, physical audio/host acceptance, combined legal all-mode acceptance and extended attract/package acceptance remain unverified. See [pirate-native.md](pirate-native.md), [map.json](../analysis/map.json). Older summaries below are historical, including superseded relocated ball contexts.

Updated2026-10-14. This is the integration map; evidence and uncertainty are explicit. Machine counterpart: [map.json](../analysis/map.json).

Amiga addresses are uncompressed retail HUNK0 offsets, **not packed-file offsets or absolute RAM addresses**. Windows addresses are preferred RIP/USA PE VAs; build SHA and conventions are in map.json. Table overlay offsets are separate address spaces.

First working island: original Windows and Amiga base playfields → RGBA → SDL3 viewport. Four tables on both platforms verified against decoded asset pixels. A bounded Mean demo native physics/bitmap/flipper slice is now implemented; full gameplay remains incomplete.

```text
User assets
  ├─ Windows DAT → palette/index decoder → SDL3 playfield + manual scrolling
  └─ Amiga SLAM → backward decoder → data + executable table overlays
                                       ├─ physics/collision: UNKNOWN
                                       ├─ table rules/callbacks: PARTIAL
                                       └─ STIM music → libxmp
STTF / Windows CFG → Packed BCD highscore reader
```

## Startup

Status **LOCATED**; confidence 0.95 for the stated boundary (not percentage of subsystem recovered).

- Amiga: hunk0+0x21c
- Windows: 0x44f448
- Files: Game.exe, SLAMTILT.EXE
- Patches: WHDLoad quit/VBR
- Evidence: AMI-001, WIN-001
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: SDL lifecycle replaces hardware takeover
- Next: No additional startup RE needed for viewer

## File Loader

Status **PARTIAL**; confidence 0.90 for the stated boundary (not percentage of subsystem recovered).

- Amiga: hunk0+0x7950
- Windows: 0x40f7e0
- Files: Game.exe, DAT/*.DAT
- Patches: None mapped
- Evidence: WIN-002, AMI-001
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: User filesystem paths; no disk assignments required
- Next: Map overlay boundaries and asset descriptors

## Asset Decoder

Status **IMPLEMENTED**; confidence 0.98 for the stated boundary (not percentage of subsystem recovered).

- Amiga: hunk0+0x8280
- Windows: 0x404f40, 0x41bb88
- Files: *.Raw, *.Bin, DAT/*.DAT, tools/slamdecode.py, tools/slaminfo
- Patches: WHDLoad start_stc
- Evidence: ASSET-001, ASSET-002
- Known functions/data: tools.slamdecode.decode; slam::load_windows_table; slam::load_amiga_table
- Port strategy: Bounded SLAM decoder and Windows palette profiles
- Next: Inspect decoded table geometry

## Renderer

Status **IMPLEMENTED**; confidence 1.00 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: 0x404f40, 0x40b76c, 0x40b808
- Files: src/assets/windows_table.cpp, src/renderer/main.cpp
- Patches: None mapped
- Evidence: ASSET-001, RENDER-001
- Known functions/data: slam::load_windows_table; SDL3 viewer main
- Port strategy: SDL3 textures from original indexed assets
- Next: Recover dynamic object descriptors

## Playfield

Status **VERIFIED**; confidence 1.00 for the stated boundary (not percentage of subsystem recovered).

- Amiga: decoded Raw BE32@0 → section+0x18 pixels, section+0x32938 palette
- Windows: 0x41bb88
- Files: MEAN.DAT, PIRATE.DAT, SPACE.DAT, DEMON.DAT, decoded table .Raw, src/assets/amiga_table.cpp
- Patches: None mapped
- Evidence: ASSET-001, RENDER-001, ASSET-003
- Known functions/data: palette[256] bytes00RRGGBB; indices[600][320]
- Port strategy: Native Windows indexed8 and Amiga row-interleaved8planes, same SDL3 viewport
- Next: Original screenshots for compositing comparison

## Scrolling

Status **PARTIAL**; confidence 1.00 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: Unmapped
- Files: src/renderer/main.cpp
- Patches: None mapped
- Evidence: RENDER-001
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Manual SDL viewport implemented; original camera unknown
- Next: Locate original ball-follow camera update

## Sprites

Status **UNKNOWN**; confidence 0.30 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: 0x40b720 candidate copy routine
- Files: *.Raw, DAT/*.DAT
- Patches: None mapped
- Evidence: WIN-005
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Native textured objects once descriptors known
- Next: Follow callers and object bounds

## Lamps

Status **UNKNOWN**; confidence 0.00 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: Unmapped
- Files: *.Raw, DAT/*.DAT
- Patches: None mapped
- Evidence: No confirmed evidence yet
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Separate lamp state from static image
- Next: Locate lamp overlay descriptors

## Dmd Renderer

Status **UNKNOWN**; confidence 0.00 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: Unmapped
- Files: Matrix.Dat, DAT/*.DAT trailing graphics
- Patches: None mapped
- Evidence: No confirmed evidence yet
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Native indexed DMD canvas
- Next: Decode matrix font/animation sections

## Main Loop

Status **LOCATED**; confidence 0.90 for the stated boundary (not percentage of subsystem recovered).

- Amiga: hunk0+0xece
- Windows: 0x402c72..0x402d99
- Files: Game.exe, SLAMTILT.EXE
- Patches: None mapped
- Evidence: AMI-001, WIN-002
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Measured simulation cadence plus independent render loop
- Next: Trace gameplay step calls

## Timing

Status **LOCATED**; confidence 0.95 for the stated boundary (not percentage of subsystem recovered).

- Amiga: hunk0+0xf0c
- Windows: 0x401014, 0x4012fd
- Files: Game.exe, SLAMTILT.EXE
- Patches: None mapped
- Evidence: AMI-001, WIN-002
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Demo5ms fixed simulation step; renderer independent
- Next: Measure PAL/Windows gameplay cadence

## Input

Status **LOCATED**; confidence 0.60 for the stated boundary (not percentage of subsystem recovered).

- Amiga: hunk0+0x5292 candidate
- Windows: Unmapped
- Files: Game.exe, SlamTiltAddCD32Pad
- Patches: CD32 pad helper
- Evidence: AMI-001
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: SDL events map to game actions
- Next: Trace input state reads; compiled pad helper

## Physics

Status **UNKNOWN**; confidence 0.00 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: Unmapped
- Files: decoded Mean.Bin, decoded Space.Bin, SLAMTILT.EXE
- Patches: None mapped
- Evidence: No confirmed evidence yet
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Prioritize original compact physics island; no invented coefficients
- Next: Locate ball-state writes and capture100-frame trace

## Collision

Status **UNKNOWN**; confidence 0.00 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: Unmapped
- Files: decoded table .Raw/.Bin, DAT/*.DAT
- Patches: None mapped
- Evidence: No confirmed evidence yet
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Geometry parser plus native collision
- Next: Identify collision maps/line tables

## Table Engine

Status **PARTIAL**; confidence 0.94 for the stated boundary (not percentage of subsystem recovered).

- Amiga: decoded Demon.Bin+0xa0000..0xa8000, decoded Mean.Bin+0x5954c, decoded Pirate.Bin+0x5a3a0, decoded Space.Bin+0x588fa, decoded Demon.Bin+0x9c2be
- Windows: 0x404e60, 0x41b9e0
- Files: decoded table .Bin, SLAMTILT.EXE
- Patches: WHDLoad decoded demon fix
- Evidence: TABLE-001, AMI-002
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Shared engine with explicit per-table code/data boundary
- Next: Map callback registration and dispatch

## Table Rules

Status **LOCATED**; confidence 0.80 for the stated boundary (not percentage of subsystem recovered).

- Amiga: decoded table executable tails
- Windows: 0x41b9e0, 0x46de14..0x46de64 callback slots
- Files: table .Bin, SLAMTILT.EXE
- Patches: None mapped
- Evidence: TABLE-001, AMI-002
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Table state machines; scripting not established
- Next: Classify callbacks via reads/writes

## Scoring

Status **PARTIAL**; confidence 0.99 for the stated boundary (not percentage of subsystem recovered).

- Amiga: decoded Main.Bin+0xd4e..0xd62 UNPK candidate
- Windows: Unmapped
- Files: SlamtiltJudge.cxx, shm.c, *.Dat, SLAMTILT.CFG
- Patches: None mapped
- Evidence: SCORE-001
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Packed BCD saves proven; runtime representation UNKNOWN
- Next: Trace bonus/score update writes

## Dmd Logic

Status **UNKNOWN**; confidence 0.00 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: Unmapped
- Files: Matrix.Dat, table overlays
- Patches: None mapped
- Evidence: No confirmed evidence yet
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Event-driven score/mode display
- Next: Locate score formatter and font indices

## Audio

Status **PARTIAL**; confidence 0.95 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: 0x44d5e7
- Files: Music.Bin, IntroMusic.Bin, libxmp STIM loader
- Patches: None mapped
- Evidence: AUDIO-001, ASSET-002
- Known functions/data: xmp_load_module; xmp_start_player; xmp_play_buffer
- Port strategy: Use libxmp; avoid custom tracker implementation
- Next: Integrate verified STIM→libxmp PCM path with SDL audio and recover event sequencing

## Menu

Status **LOCATED**; confidence 0.98 for the stated boundary (not percentage of subsystem recovered).

- Amiga: hunk0+0x936a, hunk0+0x93d8, hunk0+0x9446
- Windows: Unmapped
- Files: Main.Bin, MENU.DAT, MENU2.DAT
- Patches: WHDLoad menu index guards
- Evidence: PATCH-001
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Defer original menu, native table choice first
- Next: No menu RE until playable table

## Highscores

Status **REIMPLEMENTABLE**; confidence 0.99 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: Unmapped
- Files: STTF *.Dat, SLAMTILT.CFG, tools/slamscores.py
- Patches: None mapped
- Evidence: SCORE-001
- Known functions/data: six-byte big-digit-first Packed BCD; STTF record stride14; Windows CFG record stride10
- Port strategy: Read original five-record saves; keep unknown tails
- Next: Add native save adapter after runtime scoring

## Amiga Hardware

Status **PARTIAL**; confidence 0.90 for the stated boundary (not percentage of subsystem recovered).

- Amiga: hunk0+0x21c, hunk0+0xece, hunk0+0x8280
- Windows: Unmapped
- Files: Game.exe, WHDLoad sources
- Patches: None mapped
- Evidence: AMI-001, PATCH-001
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: Replace Copper/blitter/Paula interfaces with native subsystems
- Next: Decode overlays; hardware literals are candidates, not all confirmed instructions

## Windows Platform

Status **LOCATED**; confidence 0.99 for the stated boundary (not percentage of subsystem recovered).

- Amiga: Unmapped
- Windows: 0x4020b9, 0x40383e, 0x44d5e7
- Files: SLAMTILT.EXE
- Patches: None mapped
- Evidence: WIN-001, WIN-002
- Known functions/data: See subsystem detail; no additional recovered names
- Port strategy: SDL3 replaces DirectDraw/DirectSound/WinMM integration
- Next: Use Windows for gameplay RE, not as Amiga identity assumption

## Integration decisions

DirectDraw and Amiga blitter internals are no longer prerequisites for the first display island. Full Amiga gameplay cannot be recovered from Game.exe alone: table overlays are executable. Stored BCD scores do not prove runtime BCD arithmetic. No original Amiga/Windows physics equivalence is claimed. Compiled WHDLoad3.6 still needs mapping; older source versions are not interchangeable.

See [status](STATUS.md), [evidence](EVIDENCE.md), [binary map](binary-map.md), [patch map](patch-map.md), [formats](file-formats.md), [renderer](renderer.md), and [verification](verification.md).

## Mean demo native gameplay slice — 2026-10-08

All addresses here are **demo** VAs, SHA31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00; earlier retail addresses are not interchangeable.

| Island | Status | Evidence / implementation | Limit |
|---|---|---|---|
| Ballstate / step | PARTIAL | table4298c8→43e568, object64hex bytes; X/Y+0/+4 signed16.16, VX/VY+14/+18;4088f0 ball step,408874 loop; PHY-001 | demo200Hz, original camera unknown |
| Integration / ordinary response | IMPLEMENTED |40a010,409e18,409bec; `src/physics/mean_step.*`; PHY-002 | no point forces; field22=0; materials0/1/2 |
| Collision bitmap | IMPLEMENTED | MEAN.DAT+9ba36 hit planes, normal occupancy+959f6; native cached original40e1d0 normal evaluator | layers0–3; remaining routing partial |
| Flipper contact / input | PARTIAL |409050,4096e8,4084bc; bounded generated C++ via `tools/lift_mean_flippers.py`; PHY-003 | original flipper frames render; whole-flight integration not verified |
| Ball sprite | IMPLEMENTED | MAIN.DAT+3da4 row-dependent frame, mask+88a4; `src/assets/ball_mask.*` | uses table palette |
| SDL gameplay view | IMPLEMENTED | `--simulate PREPARED --trace INITIAL_FIXTURE`, C overlay, Space pause, Period step, Shift flippers | `--play` starts ready; Enter launch, R reset;200Hz; special events partial |

Static lift compiles bounded original routines into native C++ and uses locally prepared data. No runtime x86 interpreter is part of the port. Generated original-derived source/data stay under build. `tools/prepare_mean.py` and lift generator require the exact user-owned demo build. Local captured globals/poses are currently additional preparation inputs; preparation is not yet one-command reproducible. Trace validation: exact through63steps, first divergence64, no causal claim without synchronized flipper state. Native probe100steps deterministic with3contacts. No Amiga/Windows physics equivalence claimed.

### Launch/display delta — PHY-004/005/006

`tools/slamplay` invokes native `--play PREPARED --trace INITIAL_FIXTURE`; original initializer41ab94 and caller state0 are ported. Mean action41ac30 is invoked after integration for state1 (4089c9), gated by Enter. Native route baseline→layer1→layer2→layer3→baseline is implemented with known switch branches. Other branches pause explicitly. `mean-native-launch-validation.json` records453states,29contacts,96switch changes, one launch; no full live-original launch equivalence claimed. The ball-state side of baseline mask4/y80..120 is implemented; its bonus/lamp/mode services are not.

Mean DAT flipperframes: left6eabe,10×64×45 at(92,533); right75b3e,10×64×45 at(170,533); upper7cbbe,8×64×49 at(256,145). Indices0/1 transparent; original foreground masking remains open. Parser `src/assets/mean_flippers.*`.

200Hz evidence: WINMM timeGetTime IAT4402dc called4036b8, elapsed milliseconds passed4036ec→4048cc, accumulated404951..404963 into43e848;404a5a..404a77 consumes5ms and calls408874. Native uses5ms; trace replay viewer retains60samples/s for inspection.

Correction: baseline normalmap is DAT959f6, proven40f17d and live +40−+44=6040. Earlier95af6 was256bytes too high. `tools/prepare_mean.py` now emits original-evaluator caches for layers0–3; baseline first-difference64 persists after correction, so cause remains unresolved.

### User-reported rail offset / lower-event pause — RENDER-003, PHY-006

Ball texture top-left is **trunc(interpolatedX−7),trunc(interpolatedY−7)**. Original407a84..407b01 interpolates old/current16.16 positions with43e848/5 and truncates through422f74. Sprite frame uses this render-Y/8. Native previously used physicsX/Y as top-left, producing a7px right/down shift. `src/renderer/ball_display.h` now implements the original transform and interpolation;7original x87 fixtures pass native CTest.

Lower baseline switch4/y>=450,41ce03..41d0fa, leaves ball bytes unchanged in the tested initial mode; its score/lamp services remain unported. Native accepts this known ball-state branch and continues.300original-x86/native lower-event cases match. A subsequent layer2→3 branch41bfb6..41bff9 is implemented. Native regression now870states/49contacts/392switch changes, stops at layer3/mask1(255.45,42.10). This is native progression evidence, not full launch-physics equivalence.


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


## Gameplay bundle: ramp, fifth collision layer and bounded switches

Native Mean supports layers0..4; layer4 callback41e828 equals layer3. Ramp41ada4, layer4 entry41c300, layer4 switch41ac7c and baseline switch1 extension41ddec have bounded native helpers. Materials6/7 preserve explicit original gate state; initial43f390=-1 selects material7 fallback. Further table rule transitions remain unported. Original comparisons: ramp1200, materials512, baseline-one480, other switches512; zero differences. No500000 score is awarded for player+8 updates (separate field).

Layer1 right-return41c78c..41c84d and gate-independent baseline switch3 no-op41d94c are also native. Left switch3 capture/release remains UNKNOWN, explicitly stops simulation; no guessed slot initialization.


## Captured-ball island

IMPLEMENTED bounded single-ball initial mode: entry41d9e3→callback dispatcher415330→415fd7→417068→416db8. Native helpers `mean_capture_bundle`/`mean_capture_tick`; global slot/timer fields retain addresses. Held wrapper4089a4..4089c2 copies previous XY and zeros velocity; held balls bypass collision/switch. Release becomes active before integration on the same step. 253original callback states match; effects/rules omitted. Upper callback1 remains PARTIAL, explicitly stops. Evidence PHY-012.


## Upper capture and mode5 continuation

IMPLEMENTED bounded callback1 first/reentry/repeat cycles:41d983 entry→415330→416be4 or417068→callback3/416db8. Full original1156state replay verified; mode5 callback3 is independent of mode. Native helpers preserve slot50Hz and timer200Hz clocks. Direct release uses original RNG406840/422f40; reset seed1 is native deterministic policy. Mode5 callback2 initial awards/transfer implemented via `mean_mode5_left`, with third-award/reset guard explicit. Full mode rules/effects remain PARTIAL. PHY-013.


Mode5 clock/reset native: `mean_mode5_clock`414e79..414f47 runs before per-ball step; `mean_mode_reset`41635f/4163a6 plus419da4 selection. Reset preserves capture continuation and synchronizes43f1e6 with upper-state copy. PHY-014. Other selected-mode rule phases remain UNKNOWN; legacy all-active coverage fails explicitly there.


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

## Retail flipper contact backend — 2026-10-12

`retail_table_flipper_contact(FlipperLift&, index)` accepts a prepared Retail context and invokes original `0x409ce8`, then `0x40a380` on a zero contact result. Runtime descriptors: left `0x46c77c`, right `0x46c762`, upper `0x46c748`. Generated original-derived instructions remain under `build/generated/retail_flippers.cpp`; CMake conditionally enables `SLAM_RETAIL_FLIPPER_LIFT`. Separate backend from existing Mean Demo lift. VERIFIED for controlled original startup poses and supplied globals/LUTs; not yet integrated into autonomous Pirate gameplay.

## Mean shared reward display integration — 2026-10-12

`mean_shared_reward` → `MeanSimulation::apply_shared_reward` → existing `MeanMaterial5Display` now handles Monster Car `412fa8` (80+75 ticks), Offroad `41041c` (42+75 ticks), mode6 `410158` (12+20+1+4+50 ticks). Original user DAT frames and existing original score font; updates at existing 50Hz presentation boundary. Start occurs after mode-reset adapters so final award survives. Original queue/lamp/audio service bodies excluded from this proof. No Retail physics backend substitution in Mean.

## Rally event feedback — 2026-10-12

Shared reward event callbacks `411c60`/`411db4`/`411824` reuse `MeanMaterial5Display` at the existing50Hz boundary. Original MEAN.DAT frames:25 at12336e,14 at12624e, completion page1506ac; existingfdd4e masks provide masked page/restore. Correct turn overlays15M, completion preserves field050 through mode reset; wrong turn restores the supplied saved page. Native immediate replacement policy persists; original queue/preemption not proven.

## Mean upper capture mode4 — 2026-10-12

Original415545 compares engine mode>=4; at−2 mode4 jumps415dc7→4169db without ordinary upper mode-selection/lamp scheduling. Subsequent slot expiry follows415473→416be4. `mean_upper_capture_tick` now accepts mode4 and preserves that earlyreturn; existing MeanSimulation capture/reward/release adapters handle it. No new physics/force/route invented. Test inputprofiles are isolated inmean_sim_probe, including explicitlyseeded available upper-slot/bitmap scenario.

Mean retained-ball initialization: `mean_initialize_ball` composes verified layer0 descriptor restoration with scalar reset and caller408943 state0. Original41ab94 restores40/44/54 pointers,4c stride and50 planes without clearing other fields. Production reset/restart uses it; restart refreshes bit views before same-tick integration. Long physical oracle stops at40898b before table-specific drain callback; scheduler composition remains separately bounded.

Mean lifecycle composition oracle now executes actual table drain41aaac, engine408084, persistent save419ad8, engine bonus4072cc with real table419554, finish407794/reset419b00 and initializer41ab94. Native composed adapters match4100 snapshots across48 contexts. Deferred boundaries: render/audio/lamp bodies, save presentation scheduling34/40f754, live cadence and Full game-over policy.

Mean bonus input now preserves original edge semantics:40424f/404366 set734 bits1/2,4042ca/4043bb clear;4080dc clears at bonus entry. `set_flippers` feeds active bonus edges, existing display decoder handles734==3 step4. The adapter uses effective phase2 before table callback/render when old phase1 and734==3, matching4072de. Original4049e0 batches5ms simulation then20ms display; native fixed5ms steps interleave display.56 controlled budget cases verify original consumption/dispatch, not live batching equivalence.

Mean camera4086b8 gameplay branch now `src/renderer/mean_camera.*`:429aec center16.16,429af0 response,43e77c scroll,4297f4 previous scroll. Target maximum signed cached renderY (ball packedWORD+12), excluding state6 unless no eligible target; velocity+=(bounded desired change), center-=velocity, viewport offset frontend1c/4, clamp0..frontend10. SDL supplies current logical400/200geometry, runs once per5ms simulation after physics, stores renderY at presentation. Native startup focus explicit; attract/menu branch omitted.
Original bonus-end frame batching is separately proven by28 controlled realdispatcher chains. All5ms catch-up precedes20ms display; new mode1 remains ballFFFF until next frame. Native interleaves every4 fixedsteps; no exact catch-up/live clock equivalence claimed.

Natural advanced-mode coverage now uses `MeanDiagnosticInput` in core (diagnostic key schedule only) and native ordinary reset/physics/bitmap rules. Four400000step chains plus13/27 repeats demonstrate minigame→completion→release and selected4→mode5→threeextras→max4→oneball/mode2. Advanced journal exists only in mean_sim_probe; cached_shared_fields explicitly denotes projection cache. SDL --natural-mode-preview minigame/multiball fast-forwards seed13/27 with no debug_start or field injection, uses endless diagnosis and pauses for Space/user control. This does not prove finite3-ball attainability or original whole-table equivalence.

Upper first ordinary capture415727 sets lamp43f27c={4,6,1,0} and requests DMD411fdc. Native consumes rule_service_request only for resulting mode<4; selected mode5/6 paths remain separate. MeanMaterial5Display adds six11904e and six119b8e frames:24+24+16 animationticks,75hold,16masked restore, termination atcounter155.312actual pixel/counter/active states match. Immediate native replacement/saved native page policy persists; originalservice34 queue/handle038,field024 and438b20 effects excluded. Natural upper preview drives normal seed13 inputs, not field injection.

## Upper selected-mode announcement island — 2026-10-13

IMPLEMENTED selections0/1/2/4 service34 requests→412d24/411f10/412af8/412c58: original MEAN.DAT frames10a7ce/11a6ce/11f94e/13380e, exact animation/hold/16mask restore and termination. Selection3 retains existing minigame. Native immediate display/saved-page policy retained; original queue/handles not claimed equivalent. VERIFIED1298 original/native pixel/counter/active states (eight complete blank/patterned restore series), fixture `analysis/traces/mean-upper-modes-original.json`. Natural SDL preview `--natural-mode-preview upper-mode` uses ordinary reset and diagnostic keys, no injected state.
NEXT: shared display request arbitration when gameplay events overlap.

Natural upper-mode preview:seed13 reaches original car animation at ball489 within2000000step budget,32same-input continuation and inspected SDLcapture `build/mean-upper-mode.png`. Initial400000step budget insufficient; endless diagnostic only, not normal3-ball entry coverage.

## Shared DMD admission/retirement island — 2026-10-13

FOUND405f98 has no suspended queue: reject unless requestEAX>43e7b0 and (inactive orEAX>43e788), then storeEDX as43e788, callback/active/counter; successful return−1. Same-class request can replace becauseEAX/EDX intentionally differ. IMPLEMENTED original admission and4071e8 retirement/idle transition for21 native pixel callbacks. Upper8/7 blocks bank6/5, ordinary7/6;413a2c special5/2. Rejected requests leave active animation/counter/saved page intact. Bonus/newturn/mode4 finish retain explicit native display reset.
VERIFIED1516 original/native admission/scheduler contexts incl signed comparisons, raw stack sideeffects, branch/idle/restart actions; real callback pixels across7 overlap sequences in `analysis/traces/mean-display-overlap-original.json`. Request metadata22sites/21callbacks in `analysis/display-request-args.json`. Callback bodies/bitmap executed; alternate/idle/restart/control services adapted. Native50Hz interleaving unchanged; bonus/minigame/reward/mode6 overlay arbitration, global floor writers, sound consumption, complete shared score/page equivalence remain separate boundaries.
NEXT: merge reward/mode6 display ownership with the proven admission component.

## Reward/Mode6 visible shared-owner island — 2026-10-13

IMPLEMENTED original410a34/410910/410d34 reward pixels and410b00 full multiball announcement (clear25,19frames×4,hold100,mask16,READY50+invert cadence). Reads user MEAN.DAT frames14352e/14244e/137f4e/13bf0e and reuses MAIN.DAT text font. Replaces independent reward/mode6 clocks with shared405f98 admission and4071e8 retirement. Rewards8/7;Mode6 10/9. Reward364 releases only on idle;Mode6 382 at oldcounter267;reward3 438afc={1,0,0} at75 only if callback runs. Native shared display now follows table-display tick; bonus/minigame remain explicit separate owners.
VERIFIED1590 callback pixel/counter/active states and2945 admission/scheduler/pixel/gate states across9 composed sequences, including blocked low request, preemption, before/after75 reward3 effect and synthetic11/10 interruption. Actual413b04 reward gate executed with enginefield1c=0; post-gate idle rendering and lamps/audio adapted. Native original normal-frame batching/global floor/438afc downstream scheduling remain unproved.118/118 full CTests PASS (`build/mean-reward-owner-ctest.log`); additional Mode6 SDL119th test PASS, capture inspected. Existing --mode6-preview uses explicit seeded capture then native event/200step animation; not natural finite3-ball proof.
NEXT: shared display ownership at minigame/bonus entry and return.

## Bonus/minigame display ownership island — 2026-10-13

IMPLEMENTED first/second native minigame entry discards prior callback/priority rather than pausing it; shares retained engine1c counter with the existing original-code lift, imports raw engine10/14/18/1c/20/44 on return. Bonus entry state6/mode3 preserves raw active/priority/callback/counter; return state3/mode1/field44=0, not arbitrary all-field reset. Admission reads current native table/engine30 mode. Existing normal turn reset/pending policy retained.
VERIFIED324 raw contexts:actual415bf7..415c32 takeover,408084 bonus entry (table-save adapter),407870..4078a6 return writes. All old active/priority/counter contexts preserved or cleared exactly. Actual first minigame takeover validated; second minigame reuses already-cached initializer field contract, original second-entry caller not newly recovered. Natural seeds13/16 entry display{callback0,counter156,state0,active0,priority−1,storedcallback0,field44=1}; exit same raw fields andcounter156,field44=0. No old callback restored. Native ordinary-reset/endless diagnostic; no original/live entire trajectory or finite3-ball achievement claim.
NEXT: validate remaining Mean gameplay/rule gaps in a finite three-ball run.

## Upper return-pass gameplay/rule island — 2026-10-13

FOUND layer2/mask1/Y<60 native ball-local slice stopped at41be5d, omitting entire mode-selection/repeat-score/timer chain. IMPLEMENTED literal419da4 guards (3840/mode<=4/not-all-complete), next unfinished selection+lamps without terminal-mode reset;374=150,21flash; repeat37c++ with signedupdated37c*5M modulo32-bit. DWORD37a highWORDaliases37c.50Hz419944 expiry clears37c/lamp21; mode4/3a6==1 restoresflash. Score050/41163c request5/4 and originalflashpixels integrated; accepted40f754 request resets five capture secondarytimers, opaque038/024 remain excluded.
VERIFIED1536 actual rule/expiry raw-state contexts,324 actual41163c pixels/counter/active states. Native original-bitmap targeted chain rotates2→3→4 andscores0→5→15M, repeated exact (`analysis/traces/mean-return-pass-gameplay.json`); explicit ball/mode fixture, not natural trajectory.96ordinary finite games observe2first-pass entries/no repeat awards, allcomplete; existing natural advanced tests retaincoverage. SDL `--return-pass-preview` seeds3passages, then separate verified ramp beforedisplay continuation; originalscoreflash/lamp visible, explicit fixture.
NEXT: synchronize a complete return-pass/expiry sequence with original gameplay and audit the next missing gameplay consumer.

## Complete return-pass cycle/dispatch island — 2026-10-13

IMPLEMENTED shared return-pass presentation adapter: actual405f98 result−1/0 stored asraw038, accepted40f754 clearsraw024 andfive secondary capture timers; rejection preserves both resetfield/timers. Score050 written even when display admission fails. Replaces inline production timer wiring with reusable verified dispatch.
VERIFIED2053 composed original/native operation states and pixels across6cycles: hit→repeat→expiry→new chain;150tick boundary permits repeat,151tick expires; higher8/7 advertisement rejects5/4 repeat notice while score continues; later admission resumes normally. Actual419da4/405f98/40f754/419944/4071e8/41163c and bitmap/font routines executed. Binary score accumulation and idle rendering adapted; no full ball physics, capture timer countdown, live frame batching or whole-table equivalence claim. Evidence `analysis/traces/mean-return-pass-cycle-original.json`.
NEXT: audit the next unconsumed Mean gameplay callback, prioritizing a complete rule chain.

## Original player defaults / second-minigame progression island — 2026-10-13

FOUND real NewGame407f21→registered40f00b/43f324→419e68, then407f31→419b00. Old native all-zero record incorrectly started selection1 andsecond-mini target0. IMPLEMENTED full52byte initializer: WORDrecord04/12hex=4,22hex=8000; byteholes11/17/1dhex preserved. Eight originalrecords/256sentinel+random comparisons exact; nativefrontend remains singleplayer/freshrecordzeroBSS policy. Newgame selectionnow0 after originalresetrotation. FullUSA4268a8,UK/ROM426c78 initializer instruction/defaultpattern agrees (relocated addresses), no Amiga assumption.
VERIFIED15 original minigame2 cycles/15168states, five nowuse actual initialized8000 instead of onlysynthetic0/20000. Native actual-bitmap seeded rightcapture +flipper edges: periods5/10 win30M (+500k entry),8000→7600/count1; periods20/40 fail with8000/count0; save→next-ball reset retains target, newgame restores8000. Repeat exact; not naturalrightentry/fulloriginaltrajectory proof. Fixtures `analysis/traces/mean-player-record-original.json`, `mean-minigame2-original.json`, `mean-minigame2-player-gameplay.json`.
Updated unforced regression after correcteddefaults:400000step seeds27/29 minigame enter/complete,13/16 negativecontrols; seed27 at1800000steps enters Mode6,spawns7extras/max8,returns oneball/mode2 (firstspawn1650985,eight1651825,return1656149), exactrepeat. Endless many-ball diagnostics, not finite3-ball achievement. Natural preview uses27 forminigame/multiball, latterbudget1800000.127/127fullCTestsPASS (`build/mean-player-init-ctest.log`), warning-free build/Python syntaxPASS.
NEXT: show original second-minigame goal and terminal feedback using existing fonts/services.

## Second-minigame original text/result feedback island — 2026-10-13

IMPLEMENTED original text4060f8,smallnumeric40617c (binary/6byteBCD,width return,alignment,inkmask,group dots) andlarge406280 through optional native lift presentation hook andexisting MAIN.DAT fonts. Lift externalcalls omit hardware returnaddress; fontbridge supplies virtualESP−4 while preserving argument cleanup. Actual smallBCD zero formatting retains2digits aftermax10leading-zero shifts. Legacy gameplay oracle remains explicit no-text adapter; liveSDL nowrenders originalgoalcaption/8000/S.
IMPLEMENTED41210c failure239ticks and4122cc success214ticks: DAT11670e animation, raw43efcc numeric/S caption, failure14fbee maskedpage, successaward/invert andsavedpage restoration. Captures requested callback from liftedservice34 stack+8 (nohardware return), original8/7 admission onreturn; initialized raw43efcc andaward050 carried intoexisting sharedDMD owner. Native winner/failure testchecks actualterminalcallback.
VERIFIED93actual text/numeric pixel+width contexts through liftbridge,5436actual terminalpixel/counter/active states (24series).132/132fullCTestsPASS (`build/mean-minigame-feedback-ctest.log`) plusnew133goalSDLandfinalfont checksPASS; warning-free build/Python syntaxPASS. Goal/success/failure PNGscapturedandinspected; new `--minigame2-result-preview success|failure`, existing`--minigame2-preview` stopsatactualgoalfontcall. Previews seedoriginalrightcapture/route anddiagnosticflipperinputs; no naturalfinite3-ball/originalwholeframe equivalence claim. Other scene scaler405f0c/audio bodies remain explicit boundaries.
NEXT: reuse existing audio pipeline for missing minigame countdown/event samples.

## Minigame sample island — 2026-10-13

IMPLEMENTED both minigames' service405c60 requests and second-minigame417570 early-start input forwarded into existing native SDL sample mixer. Four original sample18 slices437fe4/438008/43802c/438050: DAT27b66/286ea/292f5/2a100, lengths2747/2882/3395/4536, period428, volume64, arguments255/245. Resolver4017a8 uses BE DAT sample index plus8 plus descriptor10; no new decoder. Early flipper press legitimately skips countdown; native four input profiles each emit exactly one start sample.
VERIFIED four original/native countdown request traces (both variants, two input schedules), exact ticks/descriptors/arguments; actual401760 resolves four PCM addresses/voice records; 55 original/native mono PCM cases across all11 samples. Evidence MEAN-MINI-AUDIO-022. Final stereo saturation remains native policy; no listening test or complete original music/display-frame equivalence claim.
NEXT: close remaining minigame scene-scaling405f0c presentation boundary using original data and a bounded pixel oracle.

## Composed minigame presentation/audio — 2026-10-13

FOUND prior405f0c scene-scaler attribution was wrong: routine expands32pixel two-plane strips to96stride canvas, unused by generated4180d0..4194e4 consumers. Existing406680/406574/40f91c implementations match original unpack/mask pixels. No additional scaler needed.
IMPLEMENTED ordered minigame audio queue for40587c/4058a0/4058c8 → existing sequencer88/84/80. Original wrappers take EAXorder/EDXbank; preserve queue order with service5c sample events. Both native second-minigame success/failure input profiles require exactly one terminal84 bank0/order62 or80stop event selectedby signed37a.
VERIFIED3461 composed full1920pixel DMD frames across both variants and four seeded scenarios, executing actual original render/text/mask routines. Oracle framebuffer must be separate from original runtime1008000 scratch (43efd0); isolated1500000 canvas, reset betweencases. External scoring/audio/display-admission/lamp effects remain bounded adapters; no full original tick/physics equivalence claim. Eight original/native tick-aligned sample/music traces include raw37a0→84 order62 vs37a−1→80 stop. See MEAN-MINI-COMPOSED-023.
NEXT: carry first-minigame terminal callback40f994 into the existing shared DMD owner (native completion bridge currently only accepts41210c/4122cc).

## First-minigame terminal handoff — 2026-10-13
40f994(abort) /40fb78(completion) readraw43efdc initialized1at415c4e, incremented4193c0, score(raw−1)×20M. Display specialNO SCORE/1 LAP/LAPS;40fb78 singularbranchomitslargepoints. Assets15018e/13f92e(23frames)/1585c4; request8/7/2/0 stack55or54/1. Nativeimportstablemode2beforeadmission, usesexistingDMDscheduler,167/300terminalticks. Shared4060a4 brightnesspair429a9c =00,01,11,12,22,23,33, alternatingrows; signedclamp0..6. Evidence024; bounded renderingVERIFIED; natural120Mfirst-minigameinputsuccessUNKNOWN.

## First-minigame complete winning lifecycle — 2026-10-13
Native original-lift first-minigame physics/collision/progress nowverifiedthrough fullsixlap/120Mrun, notonlyinjectedterminalbranches. Fixturekeys0none/1left/2right for4520shared50Hzticks; nativeSDLusesfour5msstepsperkey. minigame_steps() telemetryallows phase-correctinputreplay afterunforcedentry. Existingengine/physics unchanged; search/controllergenerateddiagnostickeys only. Sourceframebuffer480bytes and24DWORDstateblock matchactualoriginalcodeeachstep; originalsharedpresentation/audio/scoring/lamp boundariesremainexplicitadapters. Unforcednative resetseed27 reachesminigame,keyswin,40fb78 renders6LAPS/120M,releasesball andDMDowner; exactrepeat. Demo referenceonly; Retailcontactcounterdifference remainsnextportvalidation.

## Retail/Fix first-minigame island — 2026-10-13
FOUND entire codefamily differs by3gameplayconstants:418848contactscale2→4,419220partial-lappoints20M→40M,4193c6rawcompletion7→4. Both terminalDMD bodiesalso20M→40M (40fb4f/40fd77). Initializer415bce..415d00 has65unchangedinstructions/constants. Demo/RetailMEAN.DAT byteidentical (SHA1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f).
IMPLEMENTED explicitnativeRetailrevision via`--retail-minigame`; three completedlaps→120M, onecompletedlapthenabort→40M; matchingDMD3LAPS/120M andpartial40M. Demo remainsdefaultreference; noother-table/runtimeversionequivalence implied. Generatorparametrizesonlythreeprovedinstructions; DMDlapamounttransferredwithterminalrawstate.
VERIFIED actualunmodifiedRetail/Fix executables, translatedcachedDemoentrycontext/compatibleDAT/LUT: win2455ticks andone-lap-abort1189ticks perbuild,24DWORDrawstate/flags/points/callback/packedframehash exactagainstnativeprofile. Four productionrunsperresult (two diagnostic,two unforcedendlessseed27) matchpixels,awardonce,ballrelease/DMDownerretirement.1407normalizedRetailDMDpixel/countercases useproven20M→40M changes+originalDemofont/render services; notactualRetailwholeframeoracle. SDL3LAPS/120M screenshotinspected.146/146fullCTestsPASS (`build/mean-minigame-retail-ctest.log`), warning-freebuild/PythonsyntaxPASS.
NEXT: boundedDemo/Retail comparison of remainingMeanrule/capturecallbacks, prioritizing realconstantchanges overrelocation.

## Mean rule reuse / Retail launcher — 2026-10-13
FOUND: 14 bounded Mean code ranges (5860 instructions per Retail/Fix build) match Demo after verified address relocation; numeric constants and instruction bytes are unchanged. Three consumed tables (153 DWORDs) also match byte-for-byte. Evidence: `analysis/mean-rule-reuse.json`; reproducible checker `tools/verify_mean_rule_reuse.py`.
IMPLEMENTED: `tools/slamplay` defaults to the verified Retail first-minigame profile (3 laps / 120M); `--demo-minigame` selects Demo (6 laps). Historical Demo SDL fixtures explicitly select their profile. This is not a claim of complete Retail runtime equivalence.
NEXT: exercise minigame win → return → drain/bonus → GameOver in a finite three-ball game; ordinary finite games are already covered.

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

## Natural-entry original mini-game execution — 2026-10-13
IMPLEMENTED: readonly diagnostic minigame accessor, `mean_natural_minigame_oracle_probe`, `tools/verify_mean_natural_minigame.py`, CTest151. Probe reachesball1entryviaexistingrealkeysequence, exportsbinarysnapshot onlyunderbuild, records2119native5msinputsteps. Actualoriginal417374/41766c inputcallbacks and4180d0 execute530mini20msticks; actual416fe0 executes, notstubbed.
VERIFIED: everytick24DWORD43efd8..43f034+960rawbytes43f000..43f3c0,flags/mode/30M/4122cc/480packedbytehash match; orderedtwoaudioevents andargumentsmatch acrossallinputsteps. Originalcore/input/resetcodebytes comparedtocachedoriginalimage; snapshot/DAT SHAs recorded. Actualresetobservedmode2/field3a2=0. Nativealltablephysics/startup BEFOREentry remainsnotanoriginalruntimecapture; renderer/font/audio-device services remainboundedadapters. Fixture`analysis/traces/mean-natural-minigame-original.json`.
NEXT: reach the first minigame in finite play via targeted Return-Pass/upper-capture shots; preserve the verified second-minigame route.

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

## Five bounded Tilt capture paths — 2026-10-13
IMPLEMENTED: cb2/3optionalservices1c inmean_capture_tick;416d08releasebeforetimercontinuation;cb3immediatereleasepluspossiblesecondrelease. cb4optionalflag afterentryguard,shared417068proxy beforecontinuedtimer/award logic; blockedsecondtransferpreserveschangedcallback3. cb5unconditional416f24beforetimer,normalreadyrelease mayrepeat; originalsamplecountrecorded. cb1newboundedhumanwrapper executes416be4beforeconstsaved-entrytick,early_release_count1 leavesnormalrelease/transfercaller-owned. DefaultnonTiltAPIs unchanged.
VERIFIED:288actual415330cb2/3contexts (mode2;positive/<=−3timers,slotready/busy,fullball/slots/timer/sample437decargs6/5);384actual4164e1cb4contexts (human1..4,armed/blocked/timers);70actual415330cb5cases/135states (modes2/5/6);216actual415330uppercases (human1..3,gate/expired/positive/RNG), total958cases. Fixturesmean-capture-tilt-original /mean-tilt-right-capture-original /mean-tilt-multiball-original /mean-tilt-upper-capture-original. Existing360right/1757multiballcases passedagentisolatedchecks; legacyselected3timers152stepsstillmatchafterdependencyupdates.
VISIBLE: `tools/slamplay --tilt-release-preview` setsdiagnosticcallback2entry,executesoriginalTiltrelease+timer50→49/sample once,then32ordinarynativephysicssteps; screenshotinspected. No persistentgameTiltstateornudgeforces areinjected; notgeneralkeyboardTilt/gameendproof. Alt/Space stillunbound.
NEXT: compose verified capture entrypoints into the sharedTilt dispatcher, retaining uncoveredmode5/6/rule-boundary guards, thenconnectwaveform/queryoffsets andSDLkeys.

## Persistent Tilt dispatcher / finite lifecycle — 2026-10-14
IMPLEMENTED: singlefield43d864 signal feeds captured-ball dispatcher, flipperaction release, capture-entryguards, originalpoint-force/ball-save suppression andMeanBonusDisplayInput.suppressed. Usesverified417ae0requestmodule for8c→84bank1/order52/displayretirement. Clearsaftertableturncallbacks atoriginal40786a;newgameresetsflag. Score-service calls remainunconditional per40560c, no blanketscorefreeze.
VERIFIED native10chains (fivehumanmode2diagnosticcaptures×exactrepeat): release/continuedtimer/sampleordering,nonzero10Mdiagnosticbanknotawarded,stationarybonusball,flagheldthroughbonus,clearednextball,finiteGameOver/newgame. Casecontinuations5660/6600/6352/6352/10036steps; fixture`analysis/traces/mean-tilt-gameplay.json`. Targetedlifecycle+SDL2/2PASS (`build/mean-tilt-dispatch-targeted.log`). Nooriginalwhole-tabletrajectoryproof; specializedmode5/6captures/scoreboundarycomposition remainoutsidecoverage.
VISIBLE: `--tilt-release-preview` nowusespersistentTiltcapture2dispatcher andcontinuesnativephysics;Space resumes untilnextball. Alt/SpaceNudgecontrols stillunbound pendingoriginalwaveform/queryoffsetcoupling.
NEXT: connectNudgewaveform tocollisionquery/normal/separation/flipperresponse, verifyoriginalcomposedcases, thenbindAlt/Space.

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


## Cliff Jumper result island —2026-10-14

Cliff Jumper = Mean mode4phase0 (STRONG: handbook rev input and30M+15M reward). Original4143b8 idle, input41265c, success41af2c/41249c, timeout414d30/4126ec connected natively through real DMD scheduler admission +40f754 five-slot delay adapter. Return preserves display owner. Phase1 remains Kickstart; second mini remains Drag Race.


## Left ramp / natural Cliff island —2026-10-15

Mean left rampLayer3/mask1 X<160/Y140..159: deferredbonus→Pit0→shared1→438b38/3c/40→41b31f stageprogress. Newnative mean_left_progress armsCliff/Kickstart or wrapsSPEEDletter. Display412df0 implemented withlive1f2 andsavedpage; leftpriority6/5, right5/4, sound11, actualadmission resetsfive capture delays. Original callbackcount157 thenretire. Naturalcliffpreview usesSDL-equivalentdiagnostic keys, noball/rule setup.


## Natural Kickstart60M island —2026-10-15

Kickstart mode4phase1:41b010 requests4130cc(8/7,sound5),40f754 allfive delay0; shared40726f idle only→413ba6→4141b8 initializes3aa0 afterintro. Nativepreviously initializedwhileactivecallback; corrected. Clock200Hz releasesmagnetat18; rightinput3aa1/2→3; engine41bf0c25Mthen10M; inner41c0df25M +4102c0(8/7,sound57),preservedthroughmode2reset. 4102c0 displaysfixed25M, cumulative058 holds60M.


## Natural PitStop65M island —2026-10-15

PitStop gameplayunchanged; MeanPitStopStats countsactualdispatcher punctures/repairs/start/completion/points plus50Hzexpiry, read-onlyinstrumentation resetpergame. Frontendnaturalfixtureplayer sharedKickstart/PitStop handlesSDL-equivalentflippers/start/nudge bits. Newfinitefixtureprovesfull65M inball2 before30secdeadline. Original4131cc says25M; ruleawardlastrepair15M +four10Mrepairs +four2.5Mpunctures=65M.

## Natural Stock Car acceptance — 2026-10-15

`MeanSimulation::stock_car_stats()` observes actual right-cancel starts and bumper awards; it does not drive simulation. `mean_stock_finite` replays legal SDL-equivalent keys from reset through15hits/75M, threebonuses, GameOver/freeze/reset twice. Original bounded starter/bumper/display consumers unchanged. `--natural-mode-preview stock-car` replays the same fixture and pauses on the original NO CARS LEFT page. Index: `analysis/mean-stock-natural-island.json`. WholeOriginaltrajectory/audio timeline remain unverified.

## Native finite SPEED acceptance — 2026-10-15

`MeanSimulation::speed_stats()` observes actual410158 score events by10M multiplier, independent of DMD admission. `speed_letters()`/`speed_lock_timers()` expose live state for deterministic checks. No simulation decisions consume this telemetry. `mean_speed_finite` replays only legal keys from reset through fiveletters, natural RetailFormula1win, eightball spawn, allthree concurrent locks,40Mjackpot, normal return, fourbonuses/GameOver/freeze/reset twice. Input/trace index: `analysis/mean-speed-natural-island.json`. `--natural-mode-preview speed` pauses on the naturally reached original40M DMD. WholeOriginaltrajectory and audio timeline remain unverified.

## Natural Monster Car acceptance — 2026-10-15

`MeanSimulation::monster_stats()` observes actual selected1 initialization,412fa8 per-ID awards/completion and mode5 clock expiry; simulation never consumes these counters. `mean_monster_finite` verifies four fresh legal-input success/timeout/bonus/GameOver/freeze/reset chains. Original9400timer expires on9401stpost-entry step; six distinct IDs award5+10+15+20+25+50=125M. `--natural-mode-preview monster` pauses on the original final50M page. Index `analysis/mean-monster-natural-island.json`; complete Original trajectory/audio timeline remain unverified.

## Natural Liquid Rally acceptance — 2026-10-15

`rally_stats()` observes selected2 starts, actual411c60/411db4 scores and411824wrongturns/clockexpiry; `shared_mode_ticks()` exposes live39c. These counters never drive simulation. `mean_rally_finite` proves four fresh legal-keyboard complete/expiry/bonus/GameOver/reset chains, eachcorrect+2000ticks, wrongturn invariance and timed finalbonus. `--natural-mode-preview rally` shows natural22.5M finalbonus (subtotal112.5M). Index `analysis/mean-rally-natural-island.json`; fullOriginaltrajectory/audio timeline unverified.

## Natural Offroad acceptance — 2026-10-15

`offroad_stats()` observes actual selected4 initialization,41041c awards, same388target guards and mode5 clockreset; counters never affect simulation. `mean_offroad_finite` proves two reset-to-Formula1win-to-Offroad-to-fourbonus/GameOver/reset chains, exact15M pernewtarget, repeat suppression and401oneball200Hzclock checks. Original writes3additionalballs (415c95/415cb5), existing4151e4 oracle and Retail/Fix capture family corroborate; native observes4 total, handbook says3. `--natural-mode-preview offroad` replays first natural15M in fourballplay. Index `analysis/mean-offroad-natural-island.json`; wholeOriginaltrajectory/eventaudio timeline remain unverified.

## Chicken Race natural acceptance — 2026-10-15

`chicken_stats()` observes selected0 initialization, actual left-capture timedawards/completion/max and mode5 clockexpiry; no simulation reads these counters. `mean_chicken_finite` proves six fresh legal-input ordinarythree-race/late75M/partialexpiry finite lifecycles, exact existing Original before-tick formula. `verify_mean_chicken_display_timer.py` reuses actual bitmap-service harness:412908 preserves39c/3b4 for1467ticks (external lamp/audio/sharedscheduler bounded). `--natural-mode-preview chicken` pauses on56.078M finalaward (140.208M subtotal). `analysis/mean-main-modes-natural.json` maps handbook1..5 to selected0..4; selected3 uses shared44, others tablemode5. Allfive have independent natural completions; wholeOriginaltrajectory/audio timeline and allfive-in-onegame remain unverified.

## MEAN-GEARS-NATURAL-053 — Gears, earned extra ball and fivefold bonus

Fresh legal-input route reaches gears2/3/4/5 at5250/20673/22605/23541, 137 actual lamp rotations. Fifth gear uniquely arms pending0→1; upper capture29119 consumes1→0 and credits1→2. First bonus base13.5M pays67.5M. Both banked credits replay the same ball; five bonuses end at43644/200130160, then64frozen steps/reset. Twice identical, four legal nudges, no field injection. Credits are fungible: gear credit proven by sole pending provenance and complete bank redemption, not arbitrarily assigned to first replay.

Missing original gear DMD dispatch now wired:41d153 requests410fcc for2..4 or41121c for5, shared admission and five capture-delay resets preserved. Original bitmap animations/gear page/extra-ready flash/restore match4716 pixel/counter/active ticks (gears2..7, two restore values). External lamp/audio/sharedscheduler bounded separately; no wholeOriginaltrajectory claim. Index `analysis/mean-gears-natural-island.json`.

## MEAN-KICKBACK-NATURAL-054 — KICK, physical rescue and grace expiry

Handbook mean.txt37–40 anchors four red KICK letters to left sidelane. Existing rules arm43f1da via41e724..41e7b9; material7 consumes at41e655, timer390=250, integerX12/Y518 preserving fractions, vx0/vy-0x34000. Timer decrements at50Hz; remaining>=0 permits further saves. Player-record restore preserves flag/letters across turns, while timer resets-1: no unconditional per-ball flag clearing added.

Fresh legal-input route arms30261, rescues actual poolindex3 at30280 onBall1, checks exact position/impulse and original411710 request, timer249 afterstep, expires31280. Four bonuses -> GameOver39224/407952580 ->64frozen steps/reset, twice identical; nine legalnudges, no state injection. Other pool objects remain independent. Physics/rules unchanged.

Missing presentation connected: service request{7,6,2,0,23,1,411710}, saved page, five capture selectors/delay0; 17 original DAT12e3ae frames,34animation+75hold+16restore, counter12 actual438afc effect. Dedicated verifier compares254 ticks of pixels/counters/activity/effect including inactive dispatch. Native screenshot original KICK BACK inspected. Index `analysis/mean-kickback-natural-island.json`; wholeOriginaltrajectory, repeated grace save and natural unconsumed-turn persistence not newly traced.

## MEAN-LANE-SAVER-055

Physical fence geometry/rendering now implemented. Natural GOAL-bonus→collection→open→finite GameOver/reset passes twice; separate diagnostic drain/nextturn closure passes.180 Original geometry cases and2223 lap/goal pixel ticks exact. Ordinary lap admission/hold and full lap-built goal ladder remain partial. Details: `analysis/mean-lane-saver-island.json`, EVIDENCE055.

## MEAN-GOAL-LADDER-056

Ordinary lap display/admission and true capture timing now coupled. One fresh game naturally traverses goal1(GOAL bonus)→lap-built2/3→SideXB/upper credits→both redemptions→five bonuses/GameOver/reset twice. Fence state now survives unrelated raw-state reloads; closes after actual extra-ball turn reset. Cliff key fixture updated for original display priority. See `analysis/mean-goal-ladder-island.json` / EVIDENCE056. Next: Million Skull8second repeat/display.

## MEAN-SKULL-057

MillionSkull now has original countdown/reset, increasing awards, score animation and correct shared-event display priority. Fresh5/10/15M→expiry→new5M+SPEED10M→fourbonuses/GameOver/reset twice. Three old native score totals corrected by precisely removed stale repeats; gameplay routes unchanged. See `analysis/mean-skull-island.json` / EVIDENCE057. Next: natural Skillshot selection/ramp/progressive award.


Current2026-10-15 — MEAN-058: Skillshot prelaunch selection, actual41ac6f launch lock, original active DMD41455c and choice tiles414b60 implemented.870 bounded Original pixel cases; fresh legal-input20M770→30M3486, persistent tier across balls, GameOver7608/54200000/3bonuses/freeze/reset twice. Native compact prelaunch page uses exact Original tiles; generic Original player HUD excluded. Goal/lap input edges moved before launch; original strict outcomes unchanged. Index `analysis/mean-skillshot-island.json`. Next primary: remaining short-mode ramp progression.


Current2026-10-15 — MEAN-059: Both-ramp red/yellow/green→short-mode arm→clear/SPEED progression now replays twice from fresh legal keys: left3cycles/right1cycle, Mode6, finite GameOver40380/482716240/4bonuses/freeze/reset. Original-valid mode5 right marker20 entry/callback4 no longer stops: same base timer/score/transfer routine as humanmode4.779 Original cases include251 sequential mode5 ticks; six native diagnostic finite chains (initial ball/rules injected, natural occurrence unproven). Eleven remaining guards classified; no blanket unreachability claim. Index `analysis/mean-ramp-progression-island.json`. Next primary: remaining audio-event coverage and real-play acceptance.


Current2026-10-15 — MEAN-060: shared405f98 mapped DMD admission now forwards original voice order/bank to88; rejected requests silent, negative-stack preemption conditionally stops onlyactive88 at playback and preserves queuedPCM otherwise. Four mainmode start themes51/46/40/2 and SPEED29 restored; timedreturn/Chicken completion4194e4 resumes62 or stops80.972 boundedOriginal request cases;16fresh natural mode start/return routes and real STIM/SFX PCM Skillshot+SPEED eachtwice through finiteGameOver/reset (21162708PCMframes, exact200Hz/44100Hzcadence). Full Original audio timing/human audibility unclaimed. Index `analysis/mean-audio-island.json`. Next primary: Mean laptop/input/layout/highscore/audio acceptance.


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

Window activity (MEAN-070): independent `input_focus`/`minimized` gate for input, simulation accumulator and SDL audio; manual `paused` remains independent. Transitions clear accumulator/release game inputs/cancel DMD drag; restoration waits for key release. `NativeAudio::device_paused()` observes SDL device state for acceptance.

MEAN-071 presentation: `slamui` embeds licensed fonts and owns renderer-lifetime text atlases; `PortOptions` groups existing stable option IDs into categories and snapshots all visual settings on open. `slampresentation` selects optional SDL GPU/Vulkan, owns two independent bloom layers and shaders, extracts/blur/composites table and DMD, then main draws UI/highscores unprocessed. Quality uses 1/8,1/4,1/2 output dimensions; zero bloom skips blur. Source/table coordinates and gameplay remain unchanged. See `docs/presentation.md`.

MEAN-072: native newgame reset clears left/right/plunger latches so the first input matches an independent game, including audio and initial Skillshot selection. This does not change ordinary finish_turn held-input semantics. Explicitly avoid implicit MeanSimulation copies for search acceptance (internal normal DAT pointer and minigame callback refer to source objects); retained marathon/soak traces use reset or independent construction. Acceptance index: `analysis/mean-final-acceptance.json`.


MEAN-073 acceptance: `mean_mode_marathon` checks required completion mask, actual Formula1 Retail120M/extra, Offroad paid-change/end contract, Monster all6 distinct targets/125M and Rally6 correct turns. Two independent constructors hash every legal action, ball byte and audio request; upper capture/lit/goal landmarks and SPEED start/peak/return are exact fixture contracts. Three/four/four+SPEED/five CTests share this harness. All-five native composition VERIFIED; no production simulation or rules changed. Full Original trajectory equivalence remains outside this claim.


MEAN-074: physics_step→contact_step→contact_step_impl preserves the previous collision block. Default observer absent; no trace copies. Optional MeanContactTrace captures live pre-contact/dispatch/post-contact ballbytes,27poseDWORDs/40engineDWORDs,4nudges, materialstate, cachedrulefields and mutable LaneSaver tiles. Probe keeps six per mode/layer/kind/material/nudge/multiball/geometry bucket from two fresh legal routes; raw contexts stay underbuild. Original408e70→409bec/return and409bec→409d78→return compare100bytes with only pointer relocation and external score/audio/display/music service adapters. Table geometry directory restored from validated profile after mapping cachedrulefields; thirdflipper flag derives from captured descriptor→graphics+1c. Pointforce/integration, switches, ballpairs and global outcomes remain outside scope.


MEAN-075: optional MeanPairTrace observer wraps the unchanged collide_pair body. std::optional avoids snapshot construction when observation is off. Trace captures actual slot indices/count/mode and before/after100-byte records; probe retains all38 changes plus stratified no-ops and compresses identical per-tick pair visitation patterns. Original408bfc uses actual i/j, native compiled lift uses temporary0/1;1861contexts exact, unused Original slots canaried. Original408874 scheduler tested via adapted phase1/physics callbacks using observed per-row counts; all11132nativepairbatches match. This does not prove phase1/physics/count-change/clock causality. Release-candidate packaging is now primary, not further detail RE.


MEAN-076 deployment: tools/slamplay is the same POSIX launcher in checkout or bundle. Bundle root/bin/slamview +lib SDL3/libxmp +share/slamtilt profiles/minimal initial state/eight-file SHA manifest. SLAM_TABLE_PROFILES overrides developer compiletime metadata path. External data root supplies MEAN/MAIN DAT, four engine tables and two minigame caches; obsolete normals caches excluded. slampack stages with CMake Runtime/--strip, copies only allowed libraries/licenses, archives hashed program separately from opt-in original/private data, and refuses existing outputs. Private play-mean uses relative paths to sibling runtime; user preferences remain SDL-owned. Tests use hidden checkout/read-only bindings plus explicitly mounted native golden checker/input fixture for whole finite replay; actual app runtime needs no Python or test tools.


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


Pirate 036: Nine Original/fresh-reset/native/reset/SDL chains match all 10 vectors across 29,076 steps. Skillshot: 10M once per ball, rearmed on next launch. Combo: 1M/2M/3M cap; timer 0 valid, −1 expired. Extra Ball: thresholds 25/50, next threshold 100; two earned credits replay Ball 1 twice before Ball 2. Player+0x0c counts successful Combos (historical ordinary_ramp_count keys retained). Existing native engine passed; added contracts, fixtures and CTest gates. Nine audio cases / 100 Original requests match. Diagnostic contacts; not legal-key-only all-feature acceptance. [Evidence](../analysis/pirate-window-island.json).
Next: Verify Mermaid bonus accumulation and carry/reset through original events and physical drains.


Pirate 037: Seven Original/fresh-reset/native/reset/SDL chains match all 10 vectors across 52,364 steps, also in the existing GCC12 package. Repeated Mermaid collection pays 1M/3M/4M; bank survives ball changes and F1 resets it to 1M. Hold Bonus preserves the base once, including under Tilt, but resets multiplier ×2→×1. Original quirk retained: Tilt suppresses base×multiplier, while Combo-count×1M still pays (2M proved). Seven audio cases / 217 Original requests match. Added fixtures/contracts/CTest; no production changes. Diagnostic free-ball trajectories, not legal-key-only all-feature acceptance. [Evidence](../analysis/pirate-mermaid-island.json).
Next: Audit Pirate manual-rule completion against existing end-to-end evidence and close the largest remaining acceptance gap.


PIRATE-COMPLETION-038 final verification: 6/6 affected CTests PASS147.73s; modern/GCC12 builds0warnings;12actualWayland/PipeWire event cases PASS. RC1 fullscreen real-clock natural game15600steps/78.0398s matches10Originalvectors and233audio requests,0clampedframes;15.83M/ABC/GameOver/F1 andprivate saved-score fresh-process reload/no-rewrite PASS. Actual Debian12 import/25792game+90340rule steps andrelocated archive pass. Static automatic-throw PE snippets:`analysis/pirate-knife-auto-static.json`. Exactcommands/logs retained inislandJSON. NoGitmetadata/configuredformatter/linter;Python syntax,JSON/index references and48semanticcontracts PASS.


Native controller adapter (2026-10-28)
`src/input/gamepad_input.h` owns SDL gamepads and aggregates virtual key levels with the existing keyboard actions. All four frontend loops and the main menu consume it; Mean's polled keyboard path explicitly merges pad state. Menus have stable navigation, while game actions follow persisted pad/button and keyboard bindings. RT release emits one short original-Enter pulse; no physics changes. Controls use neutral barriers on focus/modal/remap/device changes. `gamepad_overlay.h` displays real trigger pull.
Batocera launcher preflights native import once from a user data folder, preserves profiles and SDL mapping DBs, and does not generate pad2key mappings. Virtual/QEMU verification only; physical board/controller status remains UNKNOWN.

## Renderer optimization delta — 2026-10-29
Retail slice (Space/Demon) now keeps the last uploaded immutable lamp variant per SDL texture. Session-local initialization uses -1, so every texture is initialized before first draw; variant changes upload before drawing. Tick/state evaluation and composition order are unchanged. Trace exposes lamp_texture_uploads. Optional CMake SLAM_RELEASE_COMPACT and SLAM_RELEASE_LTO preserve default build behavior; experiment guide: docs/optimization.md.
