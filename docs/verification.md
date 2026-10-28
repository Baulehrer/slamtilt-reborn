# First native viewer verification

Independent validation executed 2026-10-07. Machine-readable results: `analysis/renderer-validation.json`. Reproduce after corpus extraction and native build:

```sh
cmake -S . -B build/native
cmake --build build/native
ctest --test-dir build/native --output-on-failure
python3 tools/verify_renderer.py
```

The validator uses only Python's standard library. It independently reads each original DAT's palette and 320×600 index array, invokes the native SDL3 BMP exporter, parses BMP dimensions and BGR pixels, handles bottom-up rows, and compares every RGB pixel. Palette offsets are evidence-backed profiles, not inferred from exported images.

| Table | Pixels compared | RGB pixel mismatches |
|---|---:|---:|
| Mean Machines | 192000 | 0 |
| The Pirate | 192000 | 0 |
| Ace of Space | 192000 | 0 |
| Night of the Demon | 192000 | 0 |

Windows demo MEAN.DAT is SHA-256 identical to retail Mean Machines and exports successfully. Empty, unknown short, truncated table and invalid palette inputs return exit 1 with diagnostics. Invalid/incomplete command options (`--frames 0`, negative frames, suffix junk, missing export destination, unknown option) also fail cleanly.

A separate SDL3 dummy-video run rendered three frames successfully. This validates window/renderer/texture lifecycle without requiring a physical screen. Interactive keyboard/wheel scrolling and displayed orientation on the user's real desktop were not exercised by this run. Existing native CTest `assets` passed (1/1).

`slaminfo` STTF highscore records were cross-checked against the independent `slamscores.py` reader for 60 files: identical record offsets, scores and initials throughout.

## Limits

This validates fidelity of the native export to decoded asset bytes. It does **not** claim pixel equivalence to an original-game screenshot, correctness of scene layering, lamps, animated sprites or original scrolling behavior.

Native DAT identification currently uses known size plus zero high-byte palette shape. A deliberately forged all-zero file of Mean's size is accepted and renders black. Therefore this is a bounded format-profile decoder, not exact revision authentication. `slaminfo` uses SHA-256 profiles and identifies such a forged file as UNKNOWN. Adding whole-file authentication is optional depending on whether modified user assets should remain loadable; do not advertise rejection of every unsupported same-sized revision.

## Music decoder integration

After decoding original music with `tools/slamdecode.py`, `python3 tools/verify_audio.py` loads both resulting STIM modules through the locally built libxmp. IntroMusic (119198 bytes) and Music (256232 bytes) both return zero for load/start/render and produce five seconds each of nonzero 44100 Hz stereo 16-bit PCM. WAVs remain under ignored `build/validation`. Evidence: `analysis/audio-load-results.json`. This validates the decoder-to-library integration, not original playback timing or audible equivalence.

## Native Amiga planar renderer

The same `python3 tools/verify_renderer.py` now additionally exports all four decoded `build/decoded/full/{Mean,Pirate,Space,Demon}.Raw` files through native `slamview --amiga`. Each exported BMP's complete 320×600 RGB image was compared against `tools/slamamiga.py`'s Python bitplane decoder: **192000 pixels per table, zero differences across all four tables**. Source and decoded RGB hashes are retained in `analysis/renderer-validation.json`.

Amiga empty input, truncated header, out-of-range section pointer, unsupported pixel offset, truncated palette, invalid palette reserved byte and still-compressed `SLAM` input each fail cleanly with exit 1. The native CTest remains passing (1/1). Together the Windows and Amiga exports now cover 1536000 exact RGB pixel comparisons. These checks establish agreement between independent native/Python decoders, not original screenshot or hardware-renderer equivalence.

## Final local checks

`clang-format --dry-run --Werror` passed for the four native C++ files/header and the native test. `cmake --build build/native -j4`, `ctest --test-dir build/native --output-on-failure`, `python tools/verify_renderer.py` and `python tools/verify_audio.py` passed after final native parser changes. Python tools passed `py_compile`; all analysis JSON parsed successfully. Native SDL3 real-desktop three-frame smoke passed for Windows and decoded Amiga playfields. Manual scroll input and original screenshots remain unverified.

The starting directory has no Git repository, so `git diff`/status could not be used. Final source, generated maps and negative-input results were reviewed directly. No existing formatter configuration was present; native source was formatted using installed clang-format.
