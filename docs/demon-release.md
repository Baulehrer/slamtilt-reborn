# Demon playable RC1 — 063

Current: `build/compat/releases/slamtilt-demon-rc1/slamdemon`.
Archive: `build/compat/releases/slamtilt-demon-rc1.tar.gz`.
Twenty bounded contracts/36packaged fixtures/222,852steps/861audio verified.
SHA-bound releasegate passes; metadataPlayable and release_ready=true.
Realtime:10,512steps/52.596s/0clamps onGPU/Wayland/PipeWire.
First failedtiming attempt retained; no tolerance changes.
See `analysis/demon-rc-island.json` and `analysis/traces/demon-rc-gate.json`.

## Historical standalone preview — 062

Build: `python3 tools/slamdemon-compat --release-name slamtilt-demon-preview-062`.
Program/archive: `build/compat/releases/slamtilt-demon-preview-062{,.tar.gz}`.
Run `./slamdemon`; choose the supported original Windows Retail folder containing
`SLAMTILT.EXE`, `DAT/DEMON.DAT`, `DAT/MAIN.DAT`. No original assets bundled.
`--setup` changes selection, `--data DIR` overrides it, `--check` verifies it.
Enter launches, Shift controls flippers, Escape opens options. Presentation,
options persistence and audio enabled by default. Import/play need no Python,
Wine, emulator or checkout. Tools used to build/test are not runtime dependencies.

- Native importer reconstructs five SHA-bound files exactly: PE sections/BSS,
  original canvas/MAIN copies, 308 bounded image DWORDs and one runtime DWORD.
  Existing destinations, symlinks and corrupt inputs are rejected/preserved.
- Imported legal game: 10,512 Original-exact steps, twelve vectors and31 audio.
- Relocated archive tested in bwrap: hidden checkout/home, readonly program and
  originals, no network, import with empty PATH, saved data choice, actual score
  save/reload, options persistence, menu/focus audio pause/resume.
- Actual Debian12/GCC12 build and runtime: four fixtures/30,548 steps, exact
  twelve vectors/audio. Maximum symbols GLIBC2.34, GLIBCXX3.4.29, CXXABI1.3.9.
- Host realtime evidence is separately recorded in
  `analysis/traces/demon-release-host.json`; consult its bounded status.

Verification: `tools/verify_demon_{import,package,compat,release_host}.py`.
See `analysis/demon-release-island.json`. This is a verified standalone preview;
metadata RC promotion remains separate. Physical listening/keyboard, full-raster
parity, universal drivers and all timing/seed/Tilt variants are not claimed.
The three existing RC archives remain frozen.

## RC1 acceptance — 063

RC candidate: `build/compat/releases/slamtilt-demon-rc1{,.tar.gz}`.
The final gate is `tools/verify_demon_release_gate.py`; all36 pinned completion
fixtures run against freshly imported packaged data via
`tools/verify_demon_rc_fixtures.py`. Realtime reproduction:
`python3 tools/verify_demon_release_host.py --run --report analysis/traces/demon-rc-host.json`
(default fresh work directory `build/demon-rc-host`; running again requires a new
`--work` directory). Package and Debian checks use `--report` to preserve062.
Original Mean/Pirate/Space RCs and Demon062 remain frozen.
