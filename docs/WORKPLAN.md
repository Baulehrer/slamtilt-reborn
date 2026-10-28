# Current gameplay workpack

## Observed asset reads — 071

- DONE: isolated developer-only RD/WR audit, actualPirateinputreuse, three60k exact ball trajectories, independent whole-object classification andMeanexplicitreader audit.
- DONE: two realDemonframe gaps fixed; nine tests, revision3 profile, oldrevision acceptance andRC6package.
- STOP: arbitrary file-gap investigation. Zero unexplained read differences inmeasured scenarios; source-specificmask/art differences remainoriginal.
- NEXT: broaden ADF corpus compatibility (HD-Ninja sharedgraphics revision); only return tographics gaps whenactualreads orvisiblefailures demand it.


## Original scene objects / revision2 — 070

- DONE: caller-backedPirate13-frame bank withone-byteoverlap; four restoredMean/Demonframes;192×20panorama andten16×20tiles validated.
- DONE: versionedasset profiles, preservedRC4dataset loading, native16ksteps,8CTests, newDebian12package acceptance.
- NEXT: trace reached DMD asset accesses against the remaining mapping gaps; skip unconsumed file padding. Amiga gameplay parity is still outside the asset-adapter proof.


## Amiga display island — 069

- DONE:1719 original compressedDMD bank frames, Original68k decoder/LUT oracle, seven verified source-specific repair frames, twelve originalMean contact frames; per-source trusted profiles regenerated.
- DONE: native4×4000steps,7CTests, asset-freeDebian12RC4, PC-only regression andADF-only packaged acceptance.
- NEXT: classify the remaining individual scene fragments against original Amiga callers; preserve actual source differences rather than forcing PC pixel equality. Original Amiga physics parity remains a separate unknown.


## ADF vertical slice — 068

- DONE: native reader/decoder, Amiga graphics bridge, four-table trusted profiles, CLI/menu/source persistence, separate scores; bounded four-table runtime smoke.
- NEXT: finish the original Amiga DMD/animation adapter, then isolated packaged ADF-only and older-Linux acceptance. HD-Ninja shared graphics revision is independently rejected, not silently substituted.


## DAT-only native initialization delivered — 067

- DONE: independent math formulas, structured engine/table initialization, trusted DAT-only profiles, directDAT/shared/standalone import, retained legacy modes andRC3.
- DONE: clean first-import isolation16k steps, actualDebian12 four-table240k steps, native/reference data equality andlegacy exact-file regression. No EXE or extracted-image blob inpublicpackage.
- NEXT: preserve RC3; prioritize concrete play regressions. DAT-only import is no longer an open task.

## Mean Retail input support delivered — 066

- DONE: Retail-only four-table import, Demo compatibility, native profile generation, standalone/shared chooser support, RC2 packaging and actual Debian12 validation.
- DONE:68k legal Mean ticks plus finite/minigame/Rally/combined regressions with Demo hidden and OriginalEXEs masked afterimport; four targeted CTests pass. Three failed partial-readset attempts retained; dynamic read audit located final inline mask arrays.
- NEXT: preserve RC2 and prioritize reported play regressions. Optional future scope: independently generate/replace remaining EXE data to allow DAT-only first import.

## Reborn shared release acceptance — 065

- DONE: modern/Classic main and options menus, focused runtime/import refactor, legal four-table replay suite, actual Debian12 distribution/isolation, actual compositor Alt-Tab/audio/F10, three five-minute GPU runs.
- DONE: final Demon controlled-background GPU replay passes60,000ticks/300,008.67ms/0clamps with QA-only SDL-call instrumentation. Earlier failures retained, cause UNKNOWN; no timing threshold or gameplay change.
- DONE: shared SHA-bound RC index and three tamper-rejection cases pass. NEXT: preserve RC; prioritize concrete play regressions. Mean full Original trajectory and subjective feel/hearing remain explicitly separate.

## Shared original menu delivered — 064

- DONE: originalWindowsmenuart + nativefour-table selection, shareddata import/options, lasttablesave, childlifecycle andsession-onlyMainMenu/F10 return. Source andisolatedassetfreebundle verified; allfour existinggameplayregressions pass.
- NEXT: use the sharedlauncher forplay andprioritize concreteuser-facing regressions. CombinedolderABI distributionvalidation remains separate; frozenindividualRCs retained.
- Start:tools/slamtilt. F2:data; O:options; arrows/Enter ormouse:select; intable F10 orOptions→MainMenu:return.

[Evidence](../analysis/frontend-island.json), [Frontend](frontend.md).

## Demon RC gate closed — 063

- DONE: complete36-fixture packaged replay, isolated package/storage/options, Debian12 ABI/runtime, packaged realtime/fullscreen/audio, actual savedscore reload, coherentPlayable metadata andseparate20-contract releasegate.
- NEXT: preserve frozenRC andprioritize concrete gameplay regressions. Further broadRE needs an actual failing scenario. Allfour tables now have bounded playable RC metadata.
- Reproduce: tools/build_demon_release_index.py → tools/build_demon_completion.py → tools/verify_demon_release_gate.py --negative-tests. See docs/demon-release.md for fixture/host checks.

[Evidence](../analysis/demon-rc-island.json), [Gate](../analysis/traces/demon-rc-gate.json).

## Demon standalone verified — 062

- DONE: native import/setup/launcher, isolated relocatable asset-free package, actual Debian12 ABI/runtime, packaged fullscreen realtime/audio and actual score reload. Existing engine and three release pipelines reused; no new broad gameplay RE.
- NEXT: final RC consistency audit and metadata promotion against the frozen062 runtime/archive. Do not rebuild/reanalyse gameplay without a concrete failing check.

[Evidence](../analysis/demon-release-island.json).

## Demon manual audit and legal storage closed — 061

- DONE: legalkey-only positive game→125k/ABC→actualproduction save/freshreload→F1/relaunch. One nativefeedback policy sufficed; no seed/pose/rule/timer writes.20 bounded manualcontracts/36pinnedfixtures validated, knownRetail differences recorded.
- NEXT: nativeDemon dataimport andisolatedstandalone releaseacceptance. Reuse Mean/Pirate/Space importer/setup/package/ABI/session workflows. No further broadruleRE before concrete releaseblockers.
- Release gate remainsNOT_ASSESSED; audit successalone cannot promoteDemon. Physicalkeyboard/listening/fullraster/allseed/Tilt/nudge/allmode-key-only outcomes remain outside boundedacceptance.

[Evidence](../analysis/demon-legal-audit-island.json).

## Demon three-mode variant bundle closed — 060

- DONE: Witch earned force on/off withsame100ballbytes andbothsidelane rescues; Twice twoheadpairs/doublebonus/rearm/actual11M drain payout; Zombie trapvalue escalation5→8M. Existing engine reused.
- NEXT: compact Demon manual/fixture coverage audit. Prioritize the highest playable/release blocker, including a positive legal-input-only scoring/save route, before additional detail RE or RC promotion.
- Keep Mean/Pirate/Space frozen. Current evidence is bounded to recorded coordinates/outcomes; all seeds/Tilt/ramp-height/driver/raster/listening variants are not claimed.

[Evidence](../analysis/demon-variants-island.json).

## Demon target banks closed — 059

- DONE: physical skull bank→paired kickback/grace/expiry/rearm, right bank→all12 real lottery outcomes→ordinaryClock tail, earned ExtraBall consumption and actual BallSaver rescue. No artificial seed/score/timer changes.
- NEXT: bundle Witchcraft magnet/sidelane rescue, Twice-Pain head/double rewards and Zombie value escalation. Reuse known mode admissions and contacts; no broad RE.
- Still open: other mode/lottery variants and bounded completion/release acceptance. Keep Mean/Pirate/Space RC baselines frozen; Demon staysPreview.

[Evidence](../analysis/demon-banks-island.json).

## Demon video family closed — 058

- DONE: four Moon contacts→earned Werewolf/Brain admissions→actual SDL left/right/Enter→positive/negative rewards→release. Shared-sample resolution fixes three concrete video-audio gaps; no decoder work.
- NEXT: reuse the adjacent material5 target consumers for skull bank→kickback and right bank→Clock awards. Preserve frozen three-table RC references.
- Open: remaining mode variants, legal-input-only acceptance, bounded manual completion and standalone release audit. One shuffle seed/two Werewolf kills do not imply every variant is verified.

[Evidence](../analysis/demon-video-island.json).

## Demon final campaign closed — 057

- DONE: seven earned played flags inonegame→Wolf-trap final admission→four FREE balls→2/3/4-ball jackpots→fifth-hit refill/cap bonus→last-ball return→fresh Wolf selection. Frozen RC references unchanged.
- NEXT: one shared moon-target-bank workpack for Werewolf and No Brain No Pain video admissions, actual controls, rewards and release. Reuse the existing DMD/input/video mechanisms.
- Still open: kickback/random Clock awards, remaining mode variants, bounded completion audit and standalone release acceptance. Demon remainsPreview.

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

Current 039 — **Ace of Space priority**. First gameplay vertical slice closed: original native step/ball/collision/flippers/lamps/DMD, natural finite game/ABC/F1; shared transfer also produces Demon preview. Next: prove one Space-specific mode through actual switch events and compile the whole entry→reward chain. Keep Pirate RC1 frozen; do not revisit its unknown undocumented Battle3x branch. Preview audio/options/persistence/camera/multiball remain separate bounded work. [Evidence](../analysis/retail-gameplay-island.json).

Earlier workpacks below are historical.

Current 038: Pirate bounded manual acceptance is closed; RC1 verification is recorded in `analysis/pirate-completion-island.json`. Do not repeat old preview work below.

Current2026-10-22 — Pirate priority. CLOSED: canonical three-ball game→bonus→initials/highscore→Game Over→original F1→second game;12000 original/native/reset/SDL steps exact.53 lamps execute original command/blit consumers; flipper masks compose pixel-exact. Native private highscore persistence passes separate-process reload. All4table lamp decoders reusable; Mean finite five-mode golden preserved.

CLOSED first Adventure: Walk the Plank success/duplicate/30M Super Jackpot/return and timeout;15336 original/native/reset/SDL diagnostic steps match, including864 rule bytes. Original callbacks added only from actual dispatch evidence; no rule writes or completion stubs.

CLOSED four additional Adventures: Swordfight, Treasure Dive, Monkey Business and Shark Attack. Seven directed original/native/reset/SDL fixtures cover jackpot growth/repeated awards, depth clamping, wrong/correct map targets, speed/escape and timer expiry;47256 steps match all observed state. Only462 additional compiled original instructions; no new native physics or invented mode rules.

CLOSED Knife Throwing: original50Hz DMD simulation, legal Shift/Enter controls,25kills/75M, win/lose→normal return and Extra Ball armed→right-trap collection. Two original/native/reset/SDL fixtures match15648 steps; additional892 video bytes cover projectiles/engine state. All17 affected CTests PASS88.11s. Evidence: `analysis/pirate-knife-island.json`.

CLOSED Crocodile + cannon miss:2 actual Cave locks, early-fire gate, physical cannon flight,2 balls, wrong-JP guard/5M/+1M growth/6M, rescue/drain and800-step single-ball return.8908 original integer-oracle/native/reset/SDL steps match all800 poolbytes. Shared blockers fixed:405b6a sine binding and408674 integer render-owned compaction.18/18 affected CTests PASS; final camera/SDL2/2 PASS. Evidence:`analysis/pirate-multiball-island.json`.

CLOSED four-multiball campaign: reuse frozen6400-step Crocodile prefix, then actual Storm/Battle/Mutiny locks/cannon/3,4,5 free balls; JP10/15/20M, Cave+1M, duplicate/unlit sideeffects, clockwise wrap, nine first-slot compactions and three normal returns.25780 integer-oracle/native/reset/SDL steps exact.19/19 affected CTests PASS140.40s; only701 compiled instructions added, no physics changes. Evidence:`analysis/pirate-multiball-campaign-island.json`. Handbooks nominal Battle3/Mutiny4 conflict with measured Windows4/5; measured behavior retained. Battle triple-JP arm and surplus-lock variants remain outside this proof.

CLOSED MagnaTable:20 fixtures/40876 original integer-oracle/native/reset/SDL steps; all12 nominal prizes, all slots, original magnet forces, admission expiry/full intro/skip, no-award exit and return. Two1800-step flights use keys only; prize captures are diagnostic.289 extra compiled instructions, no native physics changes.19 previous affected tests and final Magna1/1 PASS. Evidence:`analysis/pirate-magna-island.json`.

CLOSED Treasure Island composed campaign:54760 steps, frozen4MBprefix+all6actualAdventures+8-ballfinal+newPlank completion.15/47/80M SJ,284M controlled/300M return,7slot0 compactions.149 compiled instructions;21/21 affected CTests PASS155.41s. Evidence:`analysis/pirate-final-island.json`.

CLOSED Pirate audio implementation:2 STIM banks/15 PCM descriptors,1015 observed original service requests over20fixtures/183760steps; native/reset exact, finite/final SDL event sequences exact.60 original Retail mono PCM cases exact;14-frame focus/minimize/pause/options/mute/reset audio acceptance passes. Existing Mean backend reused; original mixed-output equivalence and physical listening remain outside proof. Evidence:`analysis/pirate-audio-island.json`.

CLOSED five-lock/surplus campaign:29844 original/native/reset/SDL steps; actual five-lock cap/sixth guard in all4multiballs, five free balls each, JP12.5/15/17.5/20M and16slot0compactions/normalreturns. No additional compiled original instructions. Battle unarmed trap500k/unchangedJP verified; activation remainsUNKNOWN. Selected-event call hooks remove measured~130x broad tracing penalty. Evidence:`analysis/pirate-surplus-island.json`.

CLOSED Magna earned eligibility + key-only reward:4fallback chains/64560steps plus2052step natural5M reward/return;25totalMagna fixtures/107488steps. Original/native/reset/SDL exact;63bounded native policies found468-step key-only free flight. Mode-lit/all-six→20M; earned HoldBonus/Kickback survive actualCrocodile/reentry and fall through10M/5M. No extra original instructions or physics changes.9affected CTests PASS; fullbuild0warnings. Evidence:`analysis/pirate-magna-completion-island.json`.

CLOSED Pirate Nudge/Tilt:12original/native/reset/SDL fixtures/45844steps; original direction/decay/warning/Tilt, flipper gating, Knife/Magna/Crocodile including held captures→finite next-ball recovery. Actual configurable SDL keys and modal/focus/minimize/repeat gates pass.295additional compiled instructions;32audio fixtures/1172requests now exact. Evidence:`analysis/pirate-nudge-island.json`.

CLOSED lock-count matrix:3new fixtures/26876steps, all10combinations using retained minima/maxima,8new compactions. CLOSED legal feedback island:11key-only fixtures/65068steps;3naturalCave locks,5.145M/ABC/GameOver/F1/free ball;10DMD+onebonus routine lifted from actual dispatch (+917instructions). Evidence:`analysis/pirate-{lock-matrix,legal-gameplay}-island.json`.

Battle3× is not specified by handbook; bounded direct-setter/runtime searches find no ordinaryBattle arm. Keep reachabilityUNKNOWN and defer speculative rule changes. CLOSED natural Crocodile finite game:15600key-only original/native/reset/SDL steps, two earned locks, actual cannon flight/two balls/5M JP, normal return,15.83M/ABC/GameOver/F1/free ball. No additional gameplay instructions; complete reachable silent-state branching found keys in679trials/30.71s, proof uses fresh reset only.47audio fixtures green;2/2affected CTestsPASS95.62s. Evidence:`analysis/pirate-natural-croc-island.json`.

CLOSED natural Plank entry/release/drain/finite game:11600key-only original/native/reset/SDL steps;6.08415M/ABC/F1/new free ball. Ordinary DMD42e140 now complete (+142instructions,201calls);10344additional key-only steps.5affected CTestsPASS120.72s;49audio fixtures/359092steps/4351deliveries pass. Evidence:`analysis/pirate-natural-plank-island.json`.

CLOSED first two natural Plank ropes: rope4at6763→rope3at7298,10M+250k perhit,+400ticks.26200new original/native/reset/SDL steps, finite17.53415M/28.18415M/ABC/F1/free next-game ball. Bonus DMD42ee48 lifted106instructions;51audio fixtures pass. Evidence:`analysis/pirate-plank-natural-ropes-island.json`.

CLOSED display/feedback island: original scene motion from x87/sourceRECT63contexts; all12Nudge/Tilt SDL origins match. Six priority-admitted Swordfight/Dive/Monkey messages compiled695instructions;3cases12124steps exact. One legal two-rope+Nudge finite game13400steps exact,96×18wave fields.55audio cases pass;5affected CTests pass. Evidence:`analysis/pirate-feedback-display-island.json`.

CLOSED final direct DMD/input bundle: four actual events/9104steps exact;43/43bounded direct targets compiled(+580instructions). Earned Magnasaver via configurable LeftCtrl, original activation/expiry and SDL gates/remap/legacy-profile migration pass.7/7affected tests PASS106.47s;59audio fixtures/4752deliveries exact. Evidence:`analysis/pirate-final-feedback-island.json`.

CLOSED standalone Magnasaver force/save/expiry/rearm/Tilt/following-ball island:7fixtures/21904steps match all10observed vectors original/reset/native/reset/SDL. Exact LeftShift2200..2320 returns saved ball to freeplay, no waypoint after1200. Existing23907instructions suffice.5/5affected checksPASS115.80s;66audiofixtures/4854deliveries. Evidence:`analysis/pirate-magnasaver-island.json`.

CLOSED MagnaTable capture/clock/inhibit island:7newfixtures13940steps,5real-context leaf predicates,all9original/reset/native/reset/SDL vectors exact. Previous20Magna fixtures pass;5/5affected checksPASS118.40s,73audiofixtures. No added original instructions. Evidence:`analysis/pirate-magna-capture-island.json`.

CLOSED composed finite campaign: frozen54760step4MB/6Adventure/final prefix→13legalactions/no newwaypoints→ABC/1.486839210B/GameOver62640/F162704/freeball62910.62992steps full9vectors original/reset/native/reset/SDL exact. No engineinstructions added;3/3finaltestsPASS148.15s,74audiofixtures. Evidence:`analysis/pirate-campaign-finite-island.json`.

CLOSED same-game MagnaTable+Magnasaver+finite campaign: unchanged54760prefix,real+3Mbank reward,802forceapplications/flipperreturn,ABC/1.498782380B/GameOver/F1/newball.65392original/reset/native/reset/SDL10vector steps;no placement after55486.4/4affectedtestsPASS182.02s;75audiofixtures.23907instructions unchanged. Evidence:`analysis/pirate-campaign-magnets-island.json`.

CLOSED bounded legal-input repeated-game acceptance:24policies/520244native steps,48GameOvers/48F1 restarts,201tailNudges,zero errors. Three frozen Nudge/Tilt/naturalCrocodile policies original/freshreset/native/reset/SDL exact62576steps; six finite games and third-game free balls. No waypoints/game-state injection/new gameplay instructions. Broad sweep alone is native discovery, not24original proofs; no earned Magnasaver. New reusable sweep target and compact public fixtures. Final4/4affectedCTestsPASS;78audiofixtures/6132deliveries/285205284two-passstereoframes,60originalmonoPCM; originalfinalmixedPCM unclaimed. Evidence:`analysis/pirate-acceptance-island.json`.

CLOSED original camera presentation: actual409350spring/acceleration-limited follow/state6multiball/empty-pool/GameOverpan and40549ainterpolation;9000original sequential states/45000x87values exact. ActualSDL6448frames/25792steps originalconsumer-exact,all10gameplay vectors preserved. Bounded render/queue inventory establishes no additional object family; lamp+0c overlaps remain the concrete nextpixel-test. No new original gameplay instructions. Fullbuild0warnings;6/6affectedCTestsPASS105.02s. Evidence:`analysis/pirate-camera-island.json`.

CLOSED lamp/flipper composition audit + native Pirate import029:108all-angle frames/321792spritepixels and4wholelamp canvases/768000pixels match original,zeroRGB/alpha differences. No speculative new compositor. NativeRetail raw EXE+PIRATE.DAT+MAIN.DAT maps/copies originaldata and341+1bounded startup scalars to4exact files. ImportedSDL25792steps/10vectors/6448camera frames/364audio requests exact; protected destination and corruptinput cases pass, Meanimport retained. Build0warnings;4/4CTestsPASS20.90s. Ready:`tools/slampirate --data build/imported/pirate-retail`. Developer importer still resolves source recipe; standalone packaging/UI next. Evidence:`analysis/pirate-import-island.json`.

CLOSED bounded Pirate firststart/package030: sharedSDLnativeUI/rawimport/preparedselection/separatepref,relocated stripped archive withSDL3/libxmp/licenses/metadata and0originalassets. CMakePirateRuntime relativeRPATH fixes observed build-directory library searches. Archive import/remember/restart25792steps/10vectors/6448camera frames/364audio requests exact,strace0checkout/Python/Wine/checksumexec. Meanpackage/setup/import retained;4/4testsPASS34.73s,fullbuild0warnings. Ready:`build/releases/slamtilt-pirate-native/slampirate`. Historical hostfocus-test failure resolved031; both030attempts werewindowed. Evidence:`analysis/pirate-firststart-island.json`.

CLOSED Pirate host031: observed actualfocusgain526/mainwindow4 after scriptedloss527/id0 explains frame2failure. Test-only SDL_PumpEvents beforeinjection fixes event order; no ignoredOS events/removedfreezechecks/audioorphysics changes.12source+12packaged realWayland/PipeWire runs and6dummy cases pass audio/Nudge/LeftCtrl focus/minimize/pause/options/mute/reset/repeat/remapping gates. New --fullscreen enablesgenuinefullscreenwithframes; earlier030attempts werebothwindowed.4/4CTestsPASS30.00s,fullbuild0warnings. Relocated25792steps/10vectors/6448camera frames/364audio requests unchanged. Ready:`build/releases/slamtilt-pirate-host/slampirate`. PhysicalAltTab/listening/otherdrivers/olderABI remainunclaimed. [Evidence](../analysis/pirate-host-island.json).

CLOSED Pirate older-Linux ABI032: same immutableMean Debian12/GCC12toolchain reused offline/sourceRO. MaxGLIBC2.34/GLIBCXX3.4.29/CXXABI1.3.9. ActualDebian12glibc2.36 imports4exactfiles withnativeUI/PATHempty; rememberedstart/SHA/audioNudgeSpecial pass.25792steps/10vectors/6448camera frames/364audio requests exact. No sourcecheckoutmount,program/raworiginalsRO,networknone. Relocatedarchive/currenthost and12Wayland/PipeWire actualwindow/fullscreen cases pass.4/4regressionCTestsPASS31.99s; ownbuild0warnings. Ready:`build/compat/releases/slamtilt-pirate-bookworm/slampirate`. Sharedhostkernel; otherdistros/drivers/physicalAltTab/listening unclaimed. [Evidence](../analysis/pirate-compat-island.json).

CLOSED Pirate real-time/cache033: preload75ball shading groups once; conditionalLampstate/actualflipperRGBA/DMDcolor texture uploads. 1000fixedframes/4000steps preserve10vectors/camera/fullBMP byte-exact; uploads58000→2974,MAINopens1002→3,perballrenderfileIO0. All600Ypixels matchprior decoder. RealWayland/GPU4secondruns/window+fullscreen:799steps,acceptedclockresidual<5ms,0clamps;8queuedpresses permode reachposechange inlowmilliseconds. Rendercallwallp95~0.82–0.86→0.16ms; loopintervalnotphysicalrefresh,not CPU/GPUcounters orphysicalinputlatency.5/5CTestPASS17.58s,12finalpackagehostcases pass,olderABI fullgame unchanged. Newready:`build/compat/releases/slamtilt-pirate-realtime-final/slampirate`. [Evidence](../analysis/pirate-realtime-island.json).

CLOSED Pirate fullreal-time034: nativeGPU/actualwallclock legalCrocodile replay15600steps/78.026s andtwofinitegames25792steps/128.986s matchall10original vectors;597audio requests exact,0timeclamps. Threecompletegames/3F1 continuations; firstnaturaltrajectory overlaps. Cave/Cannon/2ballJP/15.83M/ABC/GameOver/F1/freeball pass,plusactualprivatehighscore persistence andfreshprocess50byte reloadwithoutrewrite. Newexact-tickbound supportsnon4multiple37step test. Freshoriginal15600retains9vectors/addsMSstate; no newRE/physics.4/4CTestPASS14.43s,oldABIandmodernbuild0warnings,actualDebian12regression retained. Ready:`build/compat/releases/slamtilt-pirate-fullgame/slampirate`. Notwholeoriginal raster orphysicalinput/audio listening/all-mode acceptance. [Evidence](../analysis/pirate-full-realtime-island.json).

CLOSED Pirate rule035: fixedactualPlank30Mfeedback callback42eb6c,previouslymissedregisterpush432388/432390/4323c8. Oldreleasefailed4099;now271dispatches/51DMDframes exact. +211compiledOriginalinstructions,24118total/outsideboundary unchanged. Fourchains26008Original/freshreset/native/reset/SDL10vectorsteps:PlankSJ,Piranha10×2Madditions/11thnormal/rearm,1/2/4/6/8/10/12bonusladder/cap,20.7M×12payout/nextballreset. Allfour alsoGCC12/actualDebian12 pass.82uniqueaudio cases/6215requests exact acrossmain81+scoped1;retained78rows unchanged. Fullbuild0warnings;two4/4CTestbatchesPASS209.10/34.58s. Ready:`build/compat/releases/slamtilt-pirate-rules/slampirate`. Diagnosticphysicalwaypoints,notallkey-onlyall-featuregame. [Evidence](../analysis/pirate-rule-island.json).

Next primary: Verify Pirate Skillshot/Combo timing windows and earned Extra Ball thresholds through actual original events. Computed/register-pushed DMD targets remain outside inventory. Do not repeat exhausted third-rope sweeps.

Older workpacks below are historical.

Current2026-10-15: MillionSkull5/10/15M→expiry→new5M/sharedSPEED→finite GameOver/reset complete twice; stale timer bug/score references corrected. Next primary: Skillshot selection→ramp→increasing prize. Evidence057.


Current2026-10-15: ordinary lap admission, natural full goal ladder and both earned-extra redemptions complete twice, fence owner fixed; evidence056. Next primary: Million Skull8-second repeat→escalating award→DMD→finite lifecycle.


Current2026-10-15: physical LaneSaver fence complete; natural GOAL-bonus -> upper collection -> open -> GameOver/reset twice. Next primary: ordinary lap display/hold coupling -> full lap-built goal ladder. Goal2/3 still partial; see evidence055.


Current2026-10-15: KICK→actual multiball rescue→grace expiry→finite GameOver/reset complete twice. Next primary: natural lap goals/lane saver/extra-ball award and consumption. Evidence054.


Current2026-10-15: gear1→5/earned extra/×5bonus/credit consumption complete twice from reset. Next primary: natural KICK letters -> kickback armed -> save consumed -> finite lifecycle. See evidence053.


Current —2026-10-15: natural finite Cliff/Kickstart60M/PitStop65M chains pass. Next primary: natural StockCar15hits/75M→bonus/GameOver, reusing existing keyboard prefixes and rule fixtures. 212/212CTestPASS301.84s.

Earlier workpacks below are chronological; their blockers may be superseded.

Completed: ball writer+100-step live flight fixture, original ball sprite, collision bitmap, native bounded physics/flipper slice, SDL Shift→original flipper pose updates.

Launch/restart, four layers, original flipper frames and200Hz are implemented. Reported rail alignment and lower switch4 freeze fixed. Upper transfers now reach native BALL_DRAIN after1852states. Synchronized100step contact fixture now matches exactly with13contacts. Continuous native ball-loss→next-ball slice implemented (bonus/DMD skipped; no game-over limit yet). Lower switch4→25000points and native HUD implemented. Original material3/4 contact→6830score/flash and material5→50000score implemented. Bundled follow-up now ports this ramp plus layer4, baseline switch1, additional switch4 and materials6/7; next actual stop is baseline switch3. Do not revisit solved asset/platform analysis.

Validation: `tools/verify_mean_components.py`, `tools/verify_mean_flippers.py`, `tools/verify_mean_flipper_input.py`, `tools/verify_mean_simulation.py`, `tools/verify_mean_launch.py`, `tools/verify_mean_launch_flow.py`, `tools/verify_mean_ball_display.py`, `tools/verify_mean_directed_force.py`, CTest `ball_display`. Use `build/venv/bin/python` for Unicorn tests. Flight exact through63; step64 divergence unresolved, synchronized flipper trace needed. Native cadence is200Hz (original timeGetTime→5ms accumulator proven).

# Next workpacks ranked by RE value

Planning scores are subjective priorities, not recovered game facts. Information gain and affected scope use1–5; effort is a relative work-unit estimate. Value=gain×scope/effort. Re-rank after every useful trace or decoded section.

| Workpack | Gain | Scope | Effort | Value | Stop and implement when |
|---|---:|---:|---:|---:|---|
| Mean demo ball-coordinate writer and per-frame callback trace | 5 | 5 | 2 | 12.5 | Ballstate and step boundary are stable; record100-frame fixture |
| Overlay descriptor consumers / collision geometry directory | 5 | 5 | 3 | 8.3 | Geometric primitives or map values are explained by collisions |
| Ball and flipper sprite descriptors | 4 | 4 | 2 | 8.0 | Frames, masks, anchors and palette are known |
| Callback semantics from registered Mean targets | 4 | 5 | 3 | 6.7 | Minimal switch→event→state chain is demonstrated |
| libxmp PCM into SDL audio | 2 | 3 | 1 | 6.0 | Existing module renders audibly; no custom music decoder |
| Compiled WHDLoad3.6 hardware patch mapping | 3 | 3 | 2 | 4.5 | Addresses localize an unresolved engine boundary |
| Full menu/intro reconstruction | 1 | 1 | 4 | 0.25 | Defer until playable table |

For the next trace, choose Windows demo for convenient code/data observation, use decoded Amiga Main.Bin/table entry paths as original-reference candidates, and compare constants/state transitions explicitly. Shared artwork and saved-score format do not prove shared physics. Live trace harness and bounded native slice now exist; next capture must include per-step flipper state.


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


## Current delta — 2026-10-10
Completed ball-reset/bonus/turn/save island:39/39tests;3040originalhelper cases andfour400000-step schedules. Native bonusdisplay completes immediately; savedball initialization bypassesoriginal43e79c gate.
Next single workpack:43e79c initialization ownership + finite game-over/turn caller. Preserve existinghelpers and fixtures; no asset/platform RE.


## Current delta — saved-ball queue + game completion
Complete: sharedrestartgate,originalnextturnFFFF handoff,Fullboundedgame-over policy, nativeGAMEOVER/Rrestart.42/42tests;fourfinitegames+existingeightballqueues. OriginalDemoisunlimited; normalportadoptsFullzero-fieldthreeballpolicy; probesexplicitlyendless.
Next: bonusDMD dispatch andpresentation; reuseexistingdecoder/rendering, nohighscoreformatorplatformRE.


## Current delta — original bonus presentation
Complete:1200dispatcher+172pixel/clockcases,44/44tests;nativebonusphasebeforeturn,originalanimation/font,total-scoredisplay,ball-freezeandone-time-bookingchecks. Partial: player+0c writers/bonusheld/fastskipinput.
Nextsingleisland: existinglibxmp music→SDL audio +firstgameplayeventSFX. No trackerdecoder/assetREredo.


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

## Delta 2026-10-12 — Retail contact island

Done: actual Retail contact/response compiled and exposed through reusable adapter; 2,400 original comparisons, all four tables. Avoided further reverse analysis of the Demo/Retail difference. Next primary workpack: original wall/flipper caller ordering and offsets → contact-inclusive Pirate step fixture. Keep Mean backend stable until equivalent context is proven.

## Priority correction — Mean first (2026-10-12)

Pirate composition work is deferred. The previous NEXT entries are superseded. Mean already has verified collision/flipper composition. Closed a Mean event-feedback gap: Monster Car, Offroad and mode6 awards now have their original finite DMD sequences. Next single workpack: remaining Rally feedback callbacks → original pixel oracle → existing Mean gameplay event consumers. Keep unsupported branches explicit and avoid additional table expansion.

## Mean Rally complete feedback delta — 2026-10-12

Done: correct/wrong/final Rally callbacks → original pixel/counter proof → existing gameplay event consumers; shared-reward feedback now covers all six callbacks. Next primary workpack: complete finite Mean game coverage and resolve the first reproducible unsupported gameplay branch; keep Pirate deferred. Original display queue/preemption remains a separate unverified boundary.

## Mean continuation delta — 2026-10-12

Done:96 finite games/five inputprofiles, four800000step varying-input sweeps; bounded source audit exposed missing mode4 upper case, now original-proven and integrated through actualbitmap entry. New inputgeneration exists only in the testprobe; port input/physics unchanged. Nextprimary: longer synchronized original/native Mean event+state replay spanning capture/drain/new-ball; advancednatural minigame traversal remainsuncovered by this sweep.

## Mean retained-ball island — 2026-10-12

Done: longer original capture/RNG/release→flight comparisons; actual restart gate/initializer on retained100-byte records; production descriptor restoration and bit-view refresh. Mean remains primary. Next: original event/scheduler context across the table drain callback and next-ball transition; current proof stops before that callback.

## Mean lifecycle island — 2026-10-12

Done: original41aaac→408084→419ad8→4072cc+419554→407794+419b00→41ab94 composition, plus direct-save branch,48 contexts/4100 snapshots. Reuses existing native components; no physics or rules invented. Next primary: original scheduler/runtime cadence across this chain; local component order is now covered.

## Mean timing/bonus input island — 2026-10-12

Done: actual budget/dispatcher proof, two-flipper734 input→fast display→same award/next ball, corrected pre-dispatch phase1 skip, accelerated full reset chains. Next primary: replay an actual runtime transition with original catch-up budgets, to distinguish native fixed-step interleaving from original batching. No other-table expansion.

## Mean camera/transition island — 2026-10-12

Done: original gameplay camera service identified at existing200Hz timing boundary, native implementation and3512state oracle, SDL integration using cached renderY/current state;28 original terminal bonus frame batches prove resume deferred to next frame. Native fixed-step interleaving remains explicit policy. Next primary: natural Mean minigame/multiball entry coverage using existing callback/bitmap fixtures; no other-table expansion.

## Mean natural advanced-entry island — 2026-10-12

Done: ordinary-reset seed13/16 minigame enter/complete/release,27/29 fourball spawn/return, deterministic event fixtures and SDL previews with user controls after Space. Shared test/preview input generator preserves prior sequence; test-only event journal stores fullball100 and labels stale shared cache explicitly. Many diagnostic balls/endless policy; no injected mode/state, no original trajectory claim. Next primary: original ordinary upper rule_service_request consumption; prove effects before changing port.

## Upper service display island — 2026-10-13

Done:first-request original415727/411fdc branch→original asset frames→native DMD/restore/lamp29→312pixel/state cases→natural SDL preview. No ball physics changes. Other rule_service_request branches remain unconsumed; originalqueue/handle and438b20/field024 effects not inferred. Next primary:selected-mode upper announcements, bounded callback groups before general queue RE.

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

Final verification:134/134 full CTests PASS (`build/mean-minigame-audio-ctest.log`); final build plus7/7 targeted sample/gameplay/SDL dummy checks PASS (`build/mean-minigame-audio-final-checks.log`). Build warning-free, Python syntax PASS.

## Composed minigame presentation/audio — 2026-10-13

FOUND prior405f0c scene-scaler attribution was wrong: routine expands32pixel two-plane strips to96stride canvas, unused by generated4180d0..4194e4 consumers. Existing406680/406574/40f91c implementations match original unpack/mask pixels. No additional scaler needed.
IMPLEMENTED ordered minigame audio queue for40587c/4058a0/4058c8 → existing sequencer88/84/80. Original wrappers take EAXorder/EDXbank; preserve queue order with service5c sample events. Both native second-minigame success/failure input profiles require exactly one terminal84 bank0/order62 or80stop event selectedby signed37a.
VERIFIED3461 composed full1920pixel DMD frames across both variants and four seeded scenarios, executing actual original render/text/mask routines. Oracle framebuffer must be separate from original runtime1008000 scratch (43efd0); isolated1500000 canvas, reset betweencases. External scoring/audio/display-admission/lamp effects remain bounded adapters; no full original tick/physics equivalence claim. Eight original/native tick-aligned sample/music traces include raw37a0→84 order62 vs37a−1→80 stop. See MEAN-MINI-COMPOSED-023.
NEXT: carry first-minigame terminal callback40f994 into the existing shared DMD owner (native completion bridge currently only accepts41210c/4122cc).

Final verification:135/135 CTests PASS (`build/mean-minigame-composed-final-ctest.log`), including8audio traces/3461composedframes/native completion audio branch. Build warning-free; Python syntax PASS.

## First-minigame terminal island — 2026-10-13
DONE both originalterminalcallbacks andsharedownerhandoff, plus original4060a4 brightnessfade. Evidence MEAN-MINI1-TERMINAL-024;2814callbackstates/four native result-retirement chains.
NEXT: first-minigame120M success through actualsteering inputs (bounded injected completion oraclealreadyexists; naturalinputsuccess stillmissing).

Natural-regression delta: prior completion assertion expected missingterminalDMD/retainedcounter; now requires original40f994 request[callback,0,4,2,7,callback,0]. Diagnostic trace records first-minigame result-owner transitions. Natural ballrelease happens atresultcounter150; callbackretires167 independently, so no before-release requirement. Entry counterretention remainschecked; completioncounterreset isoriginalacceptedrequest behavior.

Final verification:138/138 CTests PASS (`build/mean-minigame1-result-final-ctest.log`), including natural minigame27/29 result-ownerretirement and1800000step mode6 eightballreturn. Final build warning-free/Python syntaxPASS. Natural traces nowcapture resultretirement; four debug-entry profilescompareoriginalresultpixels; screenshotinspected.

## First-minigame steering-only victory — 2026-10-13
DONE original4520tick winninginput→native120M→40fb78→301tickresult→ballrelease/ownerretirement. Two unforcedseed27 runs reproduceentire lifecycle withoutdebugtable/ballstateinjection. Newfixtureswinning-input/winning-original/winning-gameplay; evidence025.141/141testsPASS.
NEXT: Retail/Fix minigame cross-check; cachedcorpus alreadyidentifies2×vs4×contactenergydecrement.

## Retail/Fix first-minigame island — 2026-10-13
FOUND entire codefamily differs by3gameplayconstants:418848contactscale2→4,419220partial-lappoints20M→40M,4193c6rawcompletion7→4. Both terminalDMD bodiesalso20M→40M (40fb4f/40fd77). Initializer415bce..415d00 has65unchangedinstructions/constants. Demo/RetailMEAN.DAT byteidentical (SHA1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f).
IMPLEMENTED explicitnativeRetailrevision via`--retail-minigame`; three completedlaps→120M, onecompletedlapthenabort→40M; matchingDMD3LAPS/120M andpartial40M. Demo remainsdefaultreference; noother-table/runtimeversionequivalence implied. Generatorparametrizesonlythreeprovedinstructions; DMDlapamounttransferredwithterminalrawstate.
VERIFIED actualunmodifiedRetail/Fix executables, translatedcachedDemoentrycontext/compatibleDAT/LUT: win2455ticks andone-lap-abort1189ticks perbuild,24DWORDrawstate/flags/points/callback/packedframehash exactagainstnativeprofile. Four productionrunsperresult (two diagnostic,two unforcedendlessseed27) matchpixels,awardonce,ballrelease/DMDownerretirement.1407normalizedRetailDMDpixel/countercases useproven20M→40M changes+originalDemofont/render services; notactualRetailwholeframeoracle. SDL3LAPS/120M screenshotinspected.146/146fullCTestsPASS (`build/mean-minigame-retail-ctest.log`), warning-freebuild/PythonsyntaxPASS.
NEXT: boundedDemo/Retail comparison of remainingMeanrule/capturecallbacks, prioritizing realconstantchanges overrelocation.

Final initializercheck: expandedactualRetail/Fix mapper includes65unchangedinitializationinstructions; final142oraclePASS (`build/mean-minigame-retail-final-oracle.log`) after146/146fullsuite. Fullnormalizedbundle2609instructions/build; only5provedconstants differ.

## Mean rule reuse / Retail launcher — 2026-10-13
FOUND: 14 bounded Mean code ranges (5860 instructions per Retail/Fix build) match Demo after verified address relocation; numeric constants and instruction bytes are unchanged. Three consumed tables (153 DWORDs) also match byte-for-byte. Evidence: `analysis/mean-rule-reuse.json`; reproducible checker `tools/verify_mean_rule_reuse.py`.
IMPLEMENTED: `tools/slamplay` defaults to the verified Retail first-minigame profile (3 laps / 120M); `--demo-minigame` selects Demo (6 laps). Historical Demo SDL fixtures explicitly select their profile. This is not a claim of complete Retail runtime equivalence.
NEXT: exercise minigame win → return → drain/bonus → GameOver in a finite three-ball game; ordinary finite games are already covered.

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

Cliff result/display admission island implemented. Next primary: natural finite Cliff entry/rev/result → bonus/GameOver; reuse existing capture/release and state7 fixtures. Do not re-analyze unrelated tables. Retail/Fix reuse now21 ranges/6868instructions each.

Cliff final verification: warning-free CMake build;202/202CTestPASS295.17s, including original pixels, nativeCliff24contexts, visible preview and existing mode4/mode6 gameplay bundles. Log:`build/mean-cliff-full-ctest.log`.


## Left ramp / natural Cliff island —2026-10-15

Left ramp/Cliff natural finite island complete within native validation bound. Nextprimary: naturalfiniteKickstart start/magnet/25M+10M+25M→bonus/GameOver using same new392arming route. Existing Originalphase1 chain should be reused. No Pirate work. Full207CTest running; targeted6/6PASS12s.

Shared animation/capture delta: real438b38/3c/40 triplet is now coupled toexisting418030 renderer (Original417da7/417dac). This fixes rightcapture wait exposed byleft-ramp4-repeat initialization; unchanged DragRacefiniteentry/visible/originalminigameoracle pass again.360Originalanimationstatesexact. Extra-ballroute10positive/0negative stillpass; secondpositive inputroute beingupdated. Initialfull207run203PASS/4FAIL; threeDragfailuresfixed, no assertionsweakened.

Finalleft-ramp/animation verification supersedes initial failures: warning-free nativebuild;206/206fullCTestPASS352.38s +separateextra-ball187PASS(twopositive18/10exactrepeats,negative0),207/207finaltests green.360Originalanimationstatesexact. NaturalCliff46-input-run success/timeout→3bonuses/GameOver/reset unchanged. Nextprimary:naturalfiniteKickstart25M+10M+25M→bonus/GameOver. Index:`analysis/mean-left-progress-island.json`.


## Natural Kickstart60M island —2026-10-15

Kickstartnaturalfiniteisland implemented. Nextprimary: naturalfinitePitStop65M→bonus/GameOver, reuseexisting216rule/PitStopOriginalfixtures; no new broadRE. Full210regressionrunning. FourtargetedOriginal/nativechecks andtwofreshfinite60MreplaysPASS.

Kickstart finalverification: warning-freebuild;210/210CTestPASS191.01s (`build/mean-kickstart-full-ctest.log`); finalclear25Mpreview aftercounter40polish recheckedPASS1.41s andPNGinspected. Natural60Mgame→GameOver/reset repeatedexactly; Originalpixel2168 andcrossRetail/Fix26ranges7463instructions confirmed. Nextprimary:naturalPitStop65Mfinitechain.


## Natural PitStop65M island —2026-10-15

NaturalPitStop65M island implemented; reuseKickstartprefix ratherthannewRE. Nextprimary:naturalfiniteStockCar15bumperhits/75M→bonus/GameOver. Full212CTestrunning; threefocusednative/visibletestsPASS2.14s. PreserveOriginal25MDMDvs15Mactualjackpotdifference.

PitStop finalverification: warning-freebuild;212/212CTestPASS301.84s (`build/mean-pit-full-ctest.log`). Bothfreshnatural65M/deadline/bonus/GameOver/resetreplays andOriginal25MvisiblepreviewPASS. Nextprimary:naturalfiniteStockCar15hits/75M→bonus/GameOver.

## Stock Car75M natural island — 2026-10-15

Done: legal-input start/15bumperhits/75M -> threebonuses/GameOver/freeze/reset, twice; dispatcher counters and natural SDL preview. Fixtures indexed in `analysis/mean-stock-natural-island.json`.
Next primary: full natural finite SPEED lock/multiball chain.

StockCar island verification: warning-free build,214/214 CTest PASS (266.48s), `build/mean-stock-full-ctest.log`; original NO CARS LEFT preview inspected.

## Natural SPEED full finite island — 2026-10-15

Done: regular reset -> natural Formula1win -> fiveletters -> eightball SPEED -> three concurrent locks/40M jackpot -> normal return -> fourbonuses/GameOver/freeze/reset, repeated exactly. SPEED subtotal260M. Fixtures/preview indexed in `analysis/mean-speed-natural-island.json`. Rules/physics unchanged; actual dispatcher telemetry added.
Next primary: natural finite Monster Car six-distinct-shot completion. FullOriginaltrajectory and completeMean still unclaimed.

Natural SPEED verification: warning-free build;216/216 CTest PASS160.82s (`build/mean-speed-natural-full-ctest.log`), including strengthened exact Formula1completion/fourbonus/GameOver40380/507716240 checks. Original40M native preview inspected.

## Natural Monster Car success/timeout island — 2026-10-15

Done: legal Returnlock -> natural selected1 start -> six distinct shots/125M beforedeadline OR actual9401step timeout/15M -> threebonuses/GameOver/freeze/reset; each path repeated exactly. No nudges or injected fields. `analysis/mean-monster-natural-island.json` indexes fixtures/preview. Rules/physics unchanged.
Next primary: natural finite Liquid Rally correct/wrong-turn and completion chain.

MonsterCar final verification: warning-free build,219/219 CTest PASS159.49s (`build/mean-monster-full-ctest.log`), five targeted checks2.95s; original final50M DMD preview inspected. Initial full run externallySIGTERMinterrupted; final fullrerun passed.

## Natural Liquid Rally island — 2026-10-15

Done: real selected2 entry -> sixcorrect112.5M OR fivecorrect75M timeout -> threebonuses/GameOver/reset, each repeated; actual wrongturn/2000tickextension/timedbonus checks. No nudges or rule/physics changes. Index `analysis/mean-rally-natural-island.json`. Next primary: natural finite Offroad multiball/different-target/end chain.

LiquidRally final verification: warning-free build,222/222 CTest PASS327.70s (`build/mean-rally-full-ctest.log`), four targeted checks7.59s; original22.5M finalbonus preview inspected.

## Natural Offroad full finite island — 2026-10-15

Done: legal Formula1win/Returnlock/Offroad/fourball90M/paidtargetrepeat/oneball200Hzclockend/fourbonuses/GameOver/reset, repeated. Native rules/physics unchanged. Existing original initializer/spawn proves3additional despite handbook3 total; preserved, indexed in `analysis/mean-offroad-ball-count.json`. Trace/preview index `analysis/mean-offroad-natural-island.json`. Next primary: natural finite Chicken Race three-race/award chain.

Offroad final verification: warning-free build;23/23 targeted natural-chain/preview/shared-rule/spawn regressions PASS17.74s (`build/mean-offroad-regression.log`). Current suite224registered; fullsuite notrerun, prior222/222 fullpass retained in completion.last_full_regression. Original15M/fourball preview inspected.

## Chicken Race / allfive main-mode acceptance — 2026-10-15

Done: natural three-race140.208M, late75Mfinal/subtotal159.13M and two-race84.13M expiry, each repeated through bonus/GameOver/reset; exact timedformula. Original awardDMD1467ticks confirms no timer/race-counter reset. Allfive primary modes now independently complete in finite legal-input games (`analysis/mean-main-modes-natural.json`). Next primary: natural gear progression/fifth-gear extra-ball collection.

ChickenRace final verification: warning-free build;29/29 targeted regression PASS26.18s plus1/1 Originalawardpixel PASS6.91s (30distinct tests), `build/mean-chicken-regression.log`, `build/mean-chicken-pixels-test.log`. Current suite229registered, fullsuite notrerun. Original56.078M preview inspected.

Gear island verification: `cmake --build build/native -j 4` PASS,31/31 targeted CTests PASS44.44s (`build/mean-gears-final-regression.log`);232 registered, full suite not rerun. SDL screenshot original EXTRA BALL LIT inspected. No Git metadata available for diff.

Kickback verification: full ABI rebuild PASS (`build/mean-kickback-final-build.log`),33/33 targeted CTests PASS15.66s (`build/mean-kickback-regression.log`);235 registered, full suite not rerun. Original254tick DMD/effect verifier and native screenshot pass.

Verification055: full build PASS;36/36 targeted tests PASS24.21s (`build/mean-lap-goal-regression.log`),241 registered/full suite not rerun. Natural and diagnostic SDL fence screenshots inspected.

Verification056: full build PASS,55/55 targeted CTests PASS29.19s (`build/mean-goal-ladder-regression.log`);244 registered/full suite not rerun. Native full-ladder EXTRA BALL screenshot inspected.

Verification057: full build PASS,61/61 targeted CTests PASS23.02s (`build/mean-skull-regression.log`);248 registered/full suite not rerun. Original15M SDL screenshot inspected.


Current2026-10-15 — MEAN-058: Skillshot prelaunch selection, actual41ac6f launch lock, original active DMD41455c and choice tiles414b60 implemented.870 bounded Original pixel cases; fresh legal-input20M770→30M3486, persistent tier across balls, GameOver7608/54200000/3bonuses/freeze/reset twice. Native compact prelaunch page uses exact Original tiles; generic Original player HUD excluded. Goal/lap input edges moved before launch; original strict outcomes unchanged. Index `analysis/mean-skillshot-island.json`. Next primary: remaining short-mode ramp progression.


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

MEAN-070: close laptop window-switch/minimize safety gap in the actual SDL main loop; validate audio-enabled and silent routes plus affected presentation regressions. Next: physical laptop acceptance.

MEAN-070 verification: warning-free full build;70/70 affected CTests PASS21.97s (`build/mean-focus-tests.log`), including both actual SDL main-loop acceptance routes and full frozen ball-byte comparisons. Full suite not repeated; prior304/304 baseline retained. No Git metadata/configured formatter.

MEAN-070 physical follow-up: user confirmed Alt-Tab audio works on retry ("geht doch!"). Real Wayland focus log `build/mean-alt-tab-live.log`: focus returns, no mute/manual pause/minimize. Initial silence not reproduced; no audio behavior changed. Added opt-in `SLAM_TRACE_ACTIVITY` event diagnostics. Refreshed CMake after system SDL library update; build PASS, both SDL frontend/audio acceptance tests PASS0.81s.

MEAN-071 implements the approved English arcade menu and six optional GPU effect presets with Soft Glow/Balanced defaults. Existing menu/persistence tests migrated to named options; real GPU contract checks all18 preset/quality combinations, identity, DMD isolation, clipping, repeatability and target resize. Explicit no-shader build also passes. Complete regression, responsive screenshots and local frame-time reports close this presentation workpack; physical aesthetic judgment remains a user check.

MEAN-071 final verification: warning-free main and explicit no-shader builds. Full307/307 PASS215.20s; final UI/shader71/71 recheck PASS22.64s, last4/4 smoke PASS1.11s; no-shader2/2 PASS0.57s. Real Vulkan18-combination pixel contract and real GPU/audio/fullscreen/focus/highscore/newgame acceptance PASS.20 exact-size category screenshots plus six actual GPU presets inspected; 240-frame benchmarks at2506x1514 show medians Original5.002ms/SoftGlow5.007ms/CRTDeluxe5.005ms, p95<=5.160ms (CPU wall times including presentation, not GPU timestamps). Artifacts `build/arcade-acceptance/`, index `analysis/mean-presentation-island.json`. No Git metadata/configured formatter. Physical aesthetic preference remains a user check.

MEAN-072: three acceptance tracks processed together. Reset-latch bug fixed rather than relaxing determinism; previous100-seed score aggregate updated only after100 independent constructor-per-seed comparisons.2072-game soak and new bounded Original normal/natural-integration oracles pass. Three-mode marathon fixture retained; Monster-first/Rally-first and known51/81 input continuations did not complete a fourth mode. Next: inspect actual upper-trap admission from three-mode checkpoint, not further broad random sweeps. Whole Original contact verification needs the missing real precontact context export documented in `analysis/mean-original-acceptance.json`.

MEAN-072 final verification: warning-free `cmake --build build/native -j 3`; complete `ctest --test-dir build/native -j 3 --output-on-failure` PASS312/312 in367.98s, including official2072-game soak154.66s. Six focused post-reference/marathon/oracle checks PASS13.81s. Initial old100-game aggregate failure resolved via100 independent constructor comparisons, not weakened assertions. No Git metadata/configured formatter. Three-of-five composition remains PARTIAL; bounded Original comparisons are not whole-trajectory equivalence.


MEAN-073 — All-five single-game target CLOSED for native composition. Capture observation found firsttrap only lights394, and nextball clears it. Fresh replay from capture43285, legal seed22 keys → Monster45329/54010. Known81-step flipper schedule → SPEED54630, normal62453, nextupper63251; legal seed30 → Rally65113/78512. Reused existing winning suffixes only after actual mode starts. All-five fixture finishes ordinary GameOver83056, no Tilt/endless/state injection. Retained intermediate four and four+SPEED exact fixtures. Next primary: export actual pre-contact context to the existing Original collision oracle; stop searching more all-five schedules.

MEAN-073 verification: warning-free `cmake --build build/native -j 3`; affected34/34 CTests PASS24.01s (`build/mean-five-modes-regression.log`), including strict golden replays for three/four/four+SPEED/five. JSON/RLE totals PASS. Full suite not repeated because production code is unchanged; prior full312/312 remains historical, now315 configured tests. No Git metadata/configured formatter/linter.


MEAN-074 — Per-ball contact-context blocker CLOSED for bounded component comparison. Smallest boundary408e70 is after integration/pointforces and before table switches/pair processing. Export actual poses/globals/nudge/ball pointers/material fields and both mutable LaneSaver tiles; execute Original detection/normal/flipper, then full wall response/separation. Original material helpers run, service ABI adapters return both0/1 in separately restored machine/stack/memory. All1036states and716wallpasses exact. All-five route alone did not reach raised geometry; reused natural GOAL fixture+verified coast instead of weakening two-geometry guard. Next primary: export real eight-ball pair contacts at408bfc; no broad new RE or timing search.

MEAN-074 final verification: warning-free `cmake --build build/native -j 3`; full `ctest --test-dir build/native -j 3 --output-on-failure` PASS317/317 in362.23s, including2072-game extended soak150.08s and both new live-contact/observer tests. Python syntax, JSON/RLE totals PASS; final changed source/test/CMake regions inspected. No Git metadata/configured formatter/linter. No physics formulas/rules altered.


MEAN-075 — Real pair/scheduler island CLOSED. Reuse existing408bfc lift; capture every actual mutation and stratified no-ops during all-five RLE.1861×200bytes exact,38 active-active responses (23SPEED/15Offroad), all28indices and canary preservation;11132tick pair-visitation batches match actual408874 with phase1/physics adapters. No naturally changing within-tick counts observed. Enabled observer retains exact all-five finite golden. All three automated acceptance tracks now bounded-verified; no more all-five searches/endurance repetition/component RE absent a new failure. Next primary: portable Mean RC launch package using user data, removing tools/slamplay repository/corpus/prepared path coupling. Full Original trajectory perfection stays optional fidelity work.

MEAN-075 verification: warning-free `cmake --build build/native -j 3`;18/18 affected CTests PASS20.28s (`build/mean-live-pairs-regression.log`),5/5 pair/contact/observer/five-mode cross-checks PASS11.20s, final pair oracle1/1PASS3.42s. Python syntax/JSON PASS; changed source/CMake/test regions inspected. No Git metadata/configured formatter/linter. Full suite not repeated for optional read-only observation/test changes; prior317/317 full suite remains historical,319 now configured.


MEAN-076 — Relocatable Mean RC island CLOSED. CMake Runtime staging/relativeRPATH, optional runtime profile path, shared POSIX source/bundle launcher and slampack private-data whitelist implemented. Missing/tampered/minigame/unsupported-profile guards checked; existing outputs preserved. Namespace runtime has no checkout and read-only app/data; actual SDL frontend/audio and both packaged-data all-five goldens pass. Public runtime2641585bytes and private companion876858bytes ready underbuild/releases. Realhost GPU/audio/fullscreen/focus/save/reset also pass. Next primary: automate supported OriginalDemo EXE/DAT preparation; do not resume solved gameplay RE. RC currently consumes prepared profile, not arbitrary raw Retail/Amiga data.

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


Pirate 036: Nine Original/fresh-reset/native/reset/SDL chains match all 10 vectors across 29,076 steps. Skillshot: 10M once per ball, rearmed on next launch. Combo: 1M/2M/3M cap; timer 0 valid, −1 expired. Extra Ball: thresholds 25/50, next threshold 100; two earned credits replay Ball 1 twice before Ball 2. Player+0x0c counts successful Combos (historical ordinary_ramp_count keys retained). Existing native engine passed; added contracts, fixtures and CTest gates. Nine audio cases / 100 Original requests match. Diagnostic contacts; not legal-key-only all-feature acceptance. [Evidence](../analysis/pirate-window-island.json).
Next: Verify Mermaid bonus accumulation and carry/reset through original events and physical drains.


Pirate 037: Seven Original/fresh-reset/native/reset/SDL chains match all 10 vectors across 52,364 steps, also in the existing GCC12 package. Repeated Mermaid collection pays 1M/3M/4M; bank survives ball changes and F1 resets it to 1M. Hold Bonus preserves the base once, including under Tilt, but resets multiplier ×2→×1. Original quirk retained: Tilt suppresses base×multiplier, while Combo-count×1M still pays (2M proved). Seven audio cases / 217 Original requests match. Added fixtures/contracts/CTest; no production changes. Diagnostic free-ball trajectories, not legal-key-only all-feature acceptance. [Evidence](../analysis/pirate-mermaid-island.json).
Next: Audit Pirate manual-rule completion against existing end-to-end evidence and close the largest remaining acceptance gap.


Pirate 038: PLAYABLE_RC. Manual audit links 24 rule contracts to 56 SHA-pinned Original fixtures / 372,660 retained steps; 48 semantic checks rerun. Closed the concrete auto-Knife gap: left/right only during video, 25 kills / 75M / collected Extra Ball, 13,076 Original/reset/native/reset/SDL steps, 74 audio events exact. Pirate capability now Playable with Retail SHA (Mean stays Demo; Space/Demon viewers); removed Preview captions. Asset-free GCC12 RC1 built and verified under actual Debian12: raw import/selection,25,792-step game plus90,340 rule steps/all10vectors; relocated archive and12 actual Wayland/PipeWire window/fullscreen event tests pass. [Evidence](../analysis/pirate-completion-island.json). Bounded diagnostic feature coverage is not all-feature key-only/full-raster equivalence; undocumented Battle3x admission remains UNKNOWN.
Next: Transfer the verified shared engine to Ace of Space, beginning with its original ball/step and table-specific callbacks; keep Pirate RC evidence frozen.


PIRATE-COMPLETION-038 final verification: 6/6 affected CTests PASS147.73s; modern/GCC12 builds0warnings;12actualWayland/PipeWire event cases PASS. RC1 fullscreen real-clock natural game15600steps/78.0398s matches10Originalvectors and233audio requests,0clampedframes;15.83M/ABC/GameOver/F1 andprivate saved-score fresh-process reload/no-rewrite PASS. Actual Debian12 import/25792game+90340rule steps andrelocated archive pass. Static automatic-throw PE snippets:`analysis/pirate-knife-auto-static.json`. Exactcommands/logs retained inislandJSON. NoGitmetadata/configuredformatter/linter;Python syntax,JSON/index references and48semanticcontracts PASS.
