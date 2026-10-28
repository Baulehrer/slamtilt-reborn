# Decoded Amiga overlays and original playfields

`analysis/decoded-manifest.json` records every `.Bin` and `.Raw` in the full WHDLoad 3.6 installed data directory: input/output SHA256, decoded length, compression and section candidates. Outputs are in `build/decoded/full/`, excluded from source control. The supplied files contain no known decoded checksum, so successful length checks alone do not establish every output byte.

## Original playfield: implemented and visually checked

Every table's decoded `.Raw` starts with BE32 section base S. At S is a six-entry BE32 section-relative offset directory:

| Entry | Meaning | Size |
|---|---|---|
| 0 | Playfield pixels, offset 0x18 | 192000 bytes |
| 1 | 256-color palette, offset 0x32938 | 1024 bytes |
| 2 | Graphic candidate, offset 0x30220 | unresolved |
| 3 | Second palette, offset 0x32D38 | 128 bytes before next section; likely 32 colors |
| 4 | Descriptor/pointer list, offset 0x32DB8 | unresolved |
| 5 | Further descriptor/data island | unresolved |

Playfield dimensions are **320×600**. Each row uses 320 bytes: eight planes of 40 bytes, planes ordered least-significant index bit first. Within a byte, bit7 is the leftmost pixel. Palette entries are `[0,R,G,B]` with eight-bit channels, matching Windows palette encoding. Dimensions were established by reconstructing image data and comparing full rows with Windows assets, not by identifying a width/height header field.

| Table | S | Absolute pixel offset | Indexed pixels equal Windows UK retail |
|---|---|---|---|
| Mean | 0x6FB58 | 0x6FB70 | 180850 / 192000 |
| Pirate | 0x64EDE | 0x64EF6 | 188406 / 192000 |
| Space | 0x6F612 | 0x6F62A | 189047 / 192000 |
| Demon | 0x844FE | 0x84516 | 188138 / 192000 |

Differences remain around lamp states/palette revisions or artwork and have not been classified. Exact agreement over 94–98% of indices is strong evidence that the table art is shared across architectures. It does not establish identical gameplay logic.

`python tools/slamamiga.py Mean.Raw build/Mean.ppm` accepts either compressed or decoded original data. It checks section bounds, palette reserved bytes and image extent. `build/decoded/Mean-amiga.png` was visually inspected and shows the complete recognizable Mean Machines playfield. PNG generation was only a local inspection conversion; the exporter itself requires no third-party Python packages.

## Table executable islands

The second BE32 at decoded `.Bin` offset4 points to a mixed code/data island. The island begins with 25 longwords; the following bytes disassemble coherently as 68k code. No relocation/base semantics are assigned to the 25 entries yet.

| Table | Island start | First coherent instruction |
|---|---|---|
| Mean | 0x594E8 | 0x5954C |
| Pirate | 0x5A33C | 0x5A3A0 |
| Space | 0x58896 | 0x588FA |
| Demon | 0x9C25A | 0x9C2BE |

All coordinates in this document refer to **decoded file offsets**, not Game.exe hunks or runtime RAM. Mean's first instructions save A0, find a PC-relative routine, call it, then write repeated state bytes through A4+0x50. Space starts directly with similar A4+0x50 writes. Demon begins by reading PC-relative bytes and changing state before its A4+0x50 writes. This supports a common table-state ABI with table-specific routines; it does not identify these bytes as physics ball state.

`Main.Bin` is 394560 bytes and starts directly with coherent PC-relative 68k instructions. It is another primary engine-analysis target, rather than treating Game.exe as the entire game engine. Main's 0xD4E–0xD62 contains six consecutive UNPK operations, a stronger score/display candidate than random isolated opcode matches. Static linear scanning into the rest of either payload produces many false math/UNPK hits from data; such hits have not been promoted to functions.

No collision geometry or ball update function has been validated. `.Raw` section offset5 and `.Bin` pre-code data are bounded candidates for descriptor/geometry searches, **not identified collision maps**. Highest-value next step: trace consumers of `.Raw` section offsets and A4 state pointers from coherent entry paths; locate table callback dispatch, then observe ball position writes.

## Decoder provenance and licensing

The implementation in `tools/slamdecode.py` was written for this project using the original retail 68k decoder, hunk0-relative 0x8280 onward. Original disassembly is retained locally at `build/patches/decrunch.asm`; source executable SHA256 is recorded in `analysis/patches.json`. WHDLoad JOTD source supplies the entry-point and header evidence.

During development, Teemu Suutari's **ancient** `StoneCrackerDecompressor.cpp` generation8 implementation and `VariableLengthCodeDecoder.hpp` were consulted to identify the format and cross-check run classes/VLC offsets. Accordingly this is **not a clean-room implementation**. Python source was written independently; no C++ implementation is bundled. The upstream reference is https://github.com/temisu/ancient (retrieved 2026-10-07); retained attribution/license is `LICENSES/ancient-BSD-2-Clause.txt`. Reference downloads stay under `build/`.

The decoder implements finite input bounds, declared-size checks, a default64MiB output cap, run bounds and backward-reference checks. All13 disk1 SLAM files decoded; `Music.Bin` starts STIM. All full-pack `.Bin`/`.Raw` assets have now been processed and their original Amiga playfields reconstruct successfully. Runtime-oracle byte comparison remains outstanding.
