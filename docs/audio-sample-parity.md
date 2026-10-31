# Retail single-voice PCM: Pirate, Space and Demon

Status: **VERIFIED for the bounded test conditions below**. This is not a claim
of whole-game audio equivalence.

The test executes Windows Retail `44b640` (gain LUT) and `44cc00` (one-shot
resampler) in Unicorn. Every executed original x86 basic block is compared byte
for byte against the SHA-256-pinned Retail executable
`185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6`.
The original output is compared to the actual C++ `MeanSampleMixer`, with native
output deliberately split into 137-frame chunks.

| Table | Descriptors | Frame lengths per descriptor | Cases | Result |
| --- | ---: | --- | ---: | --- |
| The Pirate | 15 | 1, 221, 2,048, 30,000 | 60 | exact mono PCM |
| Ace of Space | 10 | 1, 221, 2,048, 30,000 | 40 | exact mono PCM |
| Night of the Demon | 14 | 1, 221, 2,048, 30,000 | 56 | exact mono PCM |

Both native output channels equal the original mono samples. This checks neither
original stereo positioning nor the final simultaneous music/SFX device mix.
The test uses explicit six-voice, full-volume settings, not measured live mixer
settings. Tracker sequencing, sample priority/overlap, event-to-playback timing
and physical listening remain separate open questions. Initial descriptor pointers are zero for seven Pirate descriptors (listed in the result),
Space `465de0` and Demon `463398`, `463428`, `46344c`; the selected
sample offsets rely on separately retained original descriptor-resolution
research, not a pointer observed in these initial snapshots.

Reproduce with the private Retail EXE/DAT and the prepared per-table Original
contexts present in the workspace:

```sh
cmake -S . -B build/native
cmake --build build/native --target retail_sample_pcm_probe -j4
ctest --test-dir build/native -R '^retail_sample_pcm_original$' --output-on-failure
```

The test verifies the executable, image, DAT and sample hashes; its machine
report is `build/retail-sample-pcm/report.json`. Private original data is neither
copied into source nor needed by the released native port's DAT-only import.

[Asset-free result and input hashes](verification/retail-sample-pcm-2026-10-30.json).
