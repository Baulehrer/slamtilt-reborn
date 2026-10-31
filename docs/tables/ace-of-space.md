# Ace of Space

Current: supported Linux single-player RC1. Start `build/compat/releases/space-private-053/play-space --fullscreen`.
The asset-free archive imports original data natively; see [Space release](../space-release.md).
`tools/slamspace` remains the development launcher.
Shift controls flippers (left also controls the upper flipper), Enter launches;
Left Ctrl changes the spaceship-loop direction; Right Ctrl activates an earned Magnasaver. Both are configurable.
F1/R after Game Over restarts. Escape opens options; P pauses. Close the window to quit.
Display options include fullscreen/resolution, zoom, fit/stretch/fill-crop, GPU presets and DMD placement/colors (top by default). Controls and audio levels are configurable; menu/focus pauses both game and audio. Native Space highscores and shared options persist in the SDL preference directory. `--no-audio` disables music/SFX. [047](../../analysis/space-session-island.json).

Asteroid mission now has a bounded complete event lifecycle: four trapcaptures,
5M+500k growth ladder,60.005s expiry,played-state carry andF1reset. Twofixtures /
31,716steps match Original/native/reset/SDL. [040](../../analysis/space-asteroid-island.json).

The shared Retail original step drives ball physics, table geometry/collisions,
flippers, lamp commands, scoring and DMD. No replacement physics was added.
Space initializer439ae0 returns46664c; engine466424/callbacks46ed60.
Original200Hz440d10,ball441aa8,50Hz446850; launch44466c.

Proof:1200-step launch/flipper case and12000-step natural three-ball/bonus/ABC/
GameOver/F1/nextball case match Original/reset/native/reset/SDL. First100 launch
steps are pinned in `analysis/traces/space-ball-100.json`. Actual fullscreen
Wayland/OpenGL real-time1200step run also matches.

[Evidence](../../analysis/retail-gameplay-island.json).
[Entry anchors](../../analysis/space-entry-anchors.json).

Race, Hack and Blam now have bounded Original/reset/native/reset/SDL coverage: four cases including a negative guard, 47,412 steps. Space audio adds three music banks and ten samples; 119 Original audio requests match. [041](../../analysis/space-mission-audio-island.json).

Standard Multiball and Alien Attack now spawn and render three original balls; 15,472 Original/reset/native/reset/SDL steps match the whole ball pool. [042](../../analysis/space-multiball-island.json).

Standard Multiball and Alien Attack rewards and3→2→1 return now pass17,676 Original/reset/native/reset/SDL steps:10/20/30M standard jackpots, seven10M aliens and30M Super Jackpot, duplicate guards and801-step return.37 audio requests match. [043](../../analysis/space-multiball-rewards-island.json).

Light Sabre success, Speed Bikes hits/expiry, Walker aimed hit/loss return and Death Planet failure/ball release now have28,468 Original/reset steps and nine-vector/audio fixtures. Death Planet tunnel DMD works natively; its successful six-level path is now covered by045 below. [044](../../analysis/space-mode-family-island.json).

Death Planet now also clears six levels with three lives, earns/collects Extra Ball and replays Ball1 after a drain.19,392steps/nine vectors/15audio requests match. [045](../../analysis/space-planet-success-island.json).

BigBlam earned campaign,25M/100M bank rewards, negative guards and full6→1 return now match42,864 Original/reset/native/reset/SDL steps and87audio requests. Retail actually spawns six balls; manual says four. [046](../../analysis/space-bigblam-island.json).

Audit now covers24/24 bounded manual contracts, with0partial and0unknown; Space now has bounded RC acceptance. Skillshot/ComboExtraBall andship-speed bundle adds24,472 verifiedsteps and69audio events. Retail directCombos pay1M plusgrowingbonus data, notan invented direct1/2/3M ladder. [048](../../analysis/space-base-audit-island.json).

Weapon-bank multiplier/bonus and earned Magnasaver now have 5,548-step bounded acceptance, including actual SDL special keys. [049](../../analysis/space-weapons-island.json).

Four-grey-lamp kickback, consumption, grace/expiry/rearm and actual loop direction now pass7,352 steps /34 audio requests. Six SDL key cases include switching during the loop. [050](../../analysis/space-lane-kickback-island.json).

Four missions in one game now earn the75M station SuperJackpot, clear/rearm the bank and survive GameOver/F1:25,892 steps/53 audio events exact. Two early mission aborts prove victory is not required. [051](../../analysis/space-mission-campaign-island.json).

The repeat/payout/damage/aim bundle adds56,816steps/121audio events: second4-lock Multiball, second15M Walker, actual5–25M Race ladder and Sabre target/ramp damage pluspower display. Walker misses70/88 also spawnthree balls;87hits. [052](../../analysis/space-variants-island.json).

Standalone import/package/ABI/session acceptance now passes as053. [Release island](../../analysis/space-release-island.json). Mean/Pirate/Space RC baselines stay frozen; Demon is the remaining preview table. Untested mode variants and multiball edge cases remain unverified; these finite games do not imply complete
rule or original-raster equivalence. Mean/Pirate RC paths are retained.

## Post-Jackpot station sequence — 2026-10-30

A pinned Windows Retail Original replay and the current native SDL frontend match across 25,892 steps and ten state vectors. The 3,365-step station sequence after the earned Super Jackpot returns the ball through states 2→3→6→3→2, pays the recorded 75M jackpot and 5M station prize, and matches four audio requests and DMD-memory hashes. No diagnostic contact occurs between station entry and release. The entry and earlier route do use diagnostic contacts; other outcomes and mixed PCM remain open. [Evidence](../verification/space-post-jackpot-2026-10-30.json).
