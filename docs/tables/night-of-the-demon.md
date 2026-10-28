# Night of the Demon

RC evidence: [063 index](../../analysis/demon-rc-island.json);20 bounded rules,36packaged fixtures/222,852steps, verified nativeimport/package/DebianABI/realtimeaudio.

Current: bounded native single-player RC1. Start
`build/compat/releases/slamtilt-demon-rc1/slamdemon --fullscreen`; first start imports
your supported Retail data. Development launcher: `tools/slamdemon`.
Shift controls flippers, Enter launches; F1/R after Game Over restarts. Escape opens
shared display/effects/audio/controls options; P pauses. DMD colors/placement,
zoom/fillcrop and GPU presets reuse the accepted Space/Mean/Pirate frontend.

The original shared Retail200Hz/50Hz step already drives ball physics, collisions,
flippers, score, lamps and DMD. Initializer40febc returns463b54; engine4639a0,
graphics463b34; three layercallbacks418974/419bac/419f74. Existing1200step launch
and12000step finite three-ball/F1 cases match Original/native/reset.

First rule island: actualtop6-lamp contacts layer0(126,60),(148,60),(170,60),
DWORDflags46d690/694/698;419620 completesbank, player+12hex multiplier2/4/6/8,
then15M return4197cb. ActualLeftShift cyclesflags.6668steps/eightvectors/19audio
match across Original/reset/native/reset/SDL, includingearnedABC scoreboard,
GameOver/F1 andlaunch. This fixtureusesdiagnostic free-ball contacts.

Music:3STIM banks and14sample profiles reuse libxmp/samplemixer. Video descriptors
463398/463428/46344c resolve through the Original shared-sample-ID consumer. Options/audio/focus/private
recordloading checks pass. The historical12k route scoreszero; newlegalflipper
feedback now earns125k/ABC andproduction save/reload isverified (061). Nonzero bonuspayout is now verified:250k×8=2M, nextball resets1.

Clock Tower layer0(21,196): third actual capture earns three balls. Layer1 ramp
(130,30) arms jackpot locks. All active balls must be held: three pay60M, last
remaining ball pays20M; ramp requirements advance1→4→5. Unarmed/rearm captures
eject without collection.24,484steps/ninevectors/58audio exact inthree cases.
Wolf trap0(266,153) and Spirit arming trap0(91,14) now have proven normal-mode
consumers. Three Wolf modes (Bat/Grave/Meatball) and four Spirit modes
(Zombie/Witch/Twice/Vampires) are implemented through Original shared dispatch.
Bat25M, Meatball50M and one Grave46.37M treasure; Zombie four5M kills,
Witch2M ramps/5M trap, Twice two balls/15M head, Vampires four10M+20M finish.
Seven independent admission/reward/return cases:42,412steps/tenvectors/90audio exact.
Four cases return through physical loss; not all win/expiry/seed variants.
Demon’s Night now follows an earned seven-mode campaign inonegame. Four FREE balls,
21 jackpots at7M/8.5M/10M, fifth-hit refill below4 or35M when already4; Mode Total
257.5M. Last-ball return takes1step; allplayed flags clear and fresh Wolf selection
works.52,904steps/tenvectors/64audio exact; one diagnostic-contact campaign.
Moon bank now earns both video modes. Brain correct choice50M/wrong0, early Enter
and left/right0..4 bounds; Werewolf two5M/10M kills then failure, idle failure and
return verified. Actual SDL input cases match Original state/audio. Four cases:
17,052steps/elevenvectors/197audio; original skull graphics visible on GPU.
Skull bank now earns physical kickback: paired100ballbytes, grace/repeat/expiry/rearm.
Right target bank earns all12 Clock outcomes through genuine elapsed schedules,
including5/10/20M, bonus collection/double, charges, ExtraBall consumption andactual
BallSaver rescue.14cases/43,660steps/elevenvectors/230audio exact.
Witch force now haspaired100ballbyte/20step proof andbothsidelane rescues that
retainBall1. Twice twoheadpairs pay4×15M, Topdouble/repeat/rearm work andrealdrain
pays11M. Zombie Clock/Top/Wolf raisespaidrampkills5→6→7→8M. Fivecases:
25,160steps/twelvevectors/172audio exact; original engine/force LUT reused.
Legal Enter/Shift feedback now scores25k at3009, finishes125k/ABC, saves/reloads
throughproductionstorage andstartsnextgame;10512steps/twelvevectors/31audio exact,
zero diagnosticcontacts.20 boundedmanualcontracts/36pinnedfixtures areverified.
KnownRetail/manual differences stayexplicit. **Next: nativeDemon dataimport and
standalone RC acceptance.** GameplayPreview remainsuntilpackage/release gatepasses.
[Legal/audit evidence](../../analysis/demon-legal-audit-island.json).

Historical Amiga references: Windows palette DAT+0x146830 +1024bytes then320×600
pixels; Amiga decoded.Bin code9c2be runtimebase unresolved. STTF highscores at0x76,
five14byte packedBCD records, aredistinct fromthe verified shared Windows format.
