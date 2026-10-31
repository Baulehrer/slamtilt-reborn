# Audio / STIM

## Current verification — 2026-10-30

The four pinned Windows and Amiga source sets reconstruct ten byte-identical tracker banks, including source-backed samples ([evidence](verification/amiga-windows-music-banks-2026-10-30.json)). Original Amiga playback sequencing remains unverified. The SDL queue no longer discards active sound for deferred or inactive lower-track commands ([evidence](verification/retail-audio-deferred-2026-10-30.json)); full original mixed-output equivalence remains open.

Status: original music extraction and bounded libxmp PCM rendering VERIFIED. Avoid writing a new tracker decoder.

The upstream [libxmp STIM loader](https://github.com/libxmp/libxmp/blob/372272995bc67323a6e59a907ebdd093970c7875/src/loaders/stim_load.c) explicitly implements Slamtilt. Reviewed source at commit `372272995bc67323a6e59a907ebdd093970c7875`; built successfully with CMake into `build/libxmp-build/libxmp.so.4.7.3`. It recognizes `STIM`, reads big-endian sample and pattern offsets, decodes four channels of 64-row patterns, and loads signed PCM samples with loop metadata. This is sufficient groundwork for module-to-PCM playback once a valid STIM payload is available. It does not establish original trigger/timing behavior.

Direct `xmp_load_module` tests on the clean CD32 `Music.Bin` (195948 bytes) and `IntroMusic.Bin` (90072 bytes) both returned -3 (`XMP_ERROR_FORMAT`), recorded in `analysis/audio-load-results.json`. No `STIM` signatures were found in these raw files. The shared native-format `tools/slamdecode.py` now performs the necessary container decoding. Decoded Music.Bin (256232 bytes) and IntroMusic.Bin (119198 bytes) both start STIM, load and start in libxmp successfully, and render five seconds of nonzero stereo 16-bit PCM at 44100 Hz (882000 bytes each). All load/start/play calls returned zero. Reproduce with `python3 tools/verify_audio.py` after decoding. WAV artifacts are `build/validation/Music.wav` and `build/validation/IntroMusic.wav`; hashes and counts are recorded in `analysis/audio-load-results.json`. No listening comparison against original playback was performed.

Windows UK DAT files also contain no literal `STIM` signatures in their raw payloads. Windows audio containers and Paula music must not be assumed identical. Sound effects, voices, event IDs, per-table triggers and channel prioritization are still UNKNOWN.

Next: connect the verified libxmp PCM path to SDL audio, compare listening/timing with original playback, and establish per-table music sequencing. Investigate Windows DAT sample entries separately for raw PCM or their actual headers rather than infer them from offsets alone.
