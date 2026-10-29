# Release optimization experiments

Default gameplay and arithmetic are preserved. Compact release experiments are
opt-in; they do not change installed distributions or frozen v1.0 artifacts.

```
cmake -S . -B build/optimization-compact -DCMAKE_BUILD_TYPE=Release \
  -DSLAM_RELEASE_COMPACT=ON -DSLAM_RELEASE_LTO=ON
cmake --build build/optimization-compact --target slamtilt slamview slamslice -j4
```

Compact native profiles use function/data sections and linker garbage collection
on supported GNU/Clang non-Apple toolchains. LTO requires CMake's IPO support check.
The settings apply to Release; the compact section flags exclude Emscripten.
Do not compare debug binaries to stripped releases as an optimization result.

`tools/benchmark_port.py --output BUILD_REPORT --runs 5 -- /absolute/binary ARGS`
records five raw runs, elapsed/user/system CPU time, peak RSS (Linux KiB), hashes
and discoverable CMake configuration. Use the same bounded deterministic replay,
isolated preferences and renderer, with no concurrent builds or correctness tests.
Reported elapsed time includes process startup and data loading, not just physics.

`tools/verify_lamp_upload_cache.py --before OLD_SLAMSLICE --after NEW_SLAMSLICE`
uses private local Space/Demon fixtures. It compares 4,000 steps per table, all
non-wall-clock state vectors, and complete BMP bytes. These fixtures are never
included in a distribution. Mean/Pirate compact-profile evidence is separately
recorded under `build/optimization-profile-verification`.

The Space/Demon lamp cache preserves immutable off/on pixels per imported table,
uploading only on frame changes. Caches belong to that frontend's renderer/session;
no shared state survives a table/source switch. Physics/rules are untouched.

## Stage timing

`slamslice TABLE PREPARED DAT --frames 1000 --replay INPUTS.json --replay-only
--performance-output REPORT.json` optionally records setup, original shared/table
simulation (including periodic DMD ticks), post-step audio/highscore work, render
preparation and SDL presentation. Frame p50/p95/p99 are measured wall times,
not GPU execution counters. Leave `--trace` off for timing. Without this option
no per-frame timing samples or extra profiling clock reads are collected.

Evidence: `build/port-stage-profile/summary.json` contains five repetitions per
Space/Demon and software/OpenGL renderer, 4,000 ticks each, no audio or trace.
The input-only schedules preserve every original replay input event while avoiding
full oracle-state JSON parsing. On this host original ticks took 22–24 microseconds;
software presentation dominated. OpenGL measurements use the actual Wayland
compositor. These numbers do not establish Raspberry Pi speed or audio/GPU-effect
cost, nor do they imply changing the original 5ms simulation interval.

`tools/verify_lamp_upload_cache.py --performance --before OLD --after NEW` checks
that enabling stage measurement still preserves complete state vectors and BMP
pixels, and validates the bounded sample count and percentile ordering.

## Shared native engine experiment

`-DSLAM_SHARED_ENGINE=ON` builds the generated common engine once as an internal
shared library for Linux frontends. It is off by default and explicitly rejects
other platforms/Emscripten. Distributions must bundle `libslamtilt_engine.so`
with the matching frontends; this is not a public or version-stable plugin ABI.
Build-tree lookup uses relative RPATH and installed frontends use `../lib`.
Actual stripped aggregate and archive sizes must include the shared library.
Equal-name/equal-size symbol overlap is only a lead, not a savings measurement.

GPU/audio phase evidence: `build/gpu-audio-profile/summary.json` records five
1,000-frame/4,000-step runs per Space/Demon with the native GPU renderer and default
Soft Glow, with and without SDL dummy audio. These accelerated tests do not play
20 seconds of real-time PCM; queue pumping follows wall time. They establish
bounded frontend costs, not physical audio latency or human listening acceptance.

## Thread CPU and compact archives

On Linux stage timing additionally records `simulation_thread_cpu_ns` using
`CLOCK_THREAD_CPUTIME_ID`; unsupported targets report zero with
`thread_cpu_supported=false`, never a substituted wall time. This is opt-in and
does not change the gameplay clock. Five alternating runs on the same child-process
CPU affinity, 12,000 ticks each, exposed a real ~19–23% shared-engine CPU cost.
Compiler-local function binding (`-fno-semantic-interposition`, plus local linker
binding) reduced the observed cost to ~2–4%. OpenGL tail-frame variance remains
above the agreed adoption threshold in some cases, so shared engine stays off.
Final 12,000-step state/BMP parity for all four tables is under
`build/shared-engine-local-{parity,retail}/report.json`.

`tools/slamtilt-pack --build BUILD --output DEST --compression xz` creates an
optional `.tar.xz`; default remains gzip for existing release tooling. Both formats
contain the identical tar payload and manifest. Only archive extraction changes;
installed files, simulation speed and save formats are unaffected. Python's
standard gzip/lzma modules suffice; no runtime decompressor is added to the port.
Full static candidate: `build/shared-engine-package/slamtilt-reborn-static-compact.tar.xz`.
Manifest/hash and byte-identical archive-payload proof:
`build/shared-engine-package/static-compact-verification.json`.
