# Amiga subsystem islands

Coordinates and reference file are defined in [amiga-memory-map.md](amiga-memory-map.md).

| Island | Status | Evidence | Port strategy |
|---|---|---|---|
| Startup / hardware takeover | LOCATED | Exec calls at entry; vector setup 0x21C; WHDLoad replaces quit/VBR | Replace with SDL lifecycle, no original takeover code needed |
| File/media loader | PARTIAL | Slam1–Slam5 assignments and DOS LoadSeg in WHDLoad; 0x7950 media probe | Native filesystem adapter and decoded asset loading |
| Asset decoder | REIMPLEMENTABLE | Source hook at 0x8280; SLAM header skips 8 then reads lengths; backward MSB decoder | Bounded native StoneCracker gen8 decoder; confirm output on multiple files |
| Timing / interrupt dispatch | LOCATED | 0xECE tests INTREQR bits 4,5,6; VBlank 0xF0C | Fixed simulation tick after measured PAL/NTSC cadence; no proven timing constants yet |
| Renderer | PARTIAL | Copper/blitter interrupt branches; A5 custom-register base | Decode playfield data first, replace hardware pipeline |
| Input | LOCATED candidate | vector level2 ->0x5292; CIA setup | Trace handler before assigning keyboard scan state |
| Menu | LOCATED | WHDLoad six negative-index guards (analysis/patches.json) | Later native UI; skip detailed lift |
| Audio | UNKNOWN | Level4 handler clears audio interrupt bit7; alone insufficient to identify full mixer | Investigate decoded STIM assets and libxmp |
| Table code | LOCATED | WHDLoad patches decompressed demon.bin after decoding; named table payload contains executable code | Decode table overlays before physics/rules analysis |
| Physics / rules / scoring | UNKNOWN | No validated routine identification yet | Prioritize decoded overlays rather than menu executable helper functions |

A key architectural result: **Game.exe is not the complete gameplay code corpus**. WHDLoad explicitly repairs instructions inside decompressed `demon.bin` (raw length 0xA89D4), searching relative range 0xA0000–0xA8000 for two consecutive `MOVE.B ($FFFFFFFF),(A1)+` instructions. A second payload of decoded length 0x60540 contains VBR instructions. The strongest next step is decoding every SLAM payload, then separating graphics/data from executable tails.

StoneCracker classification is static, high-confidence rather than a verified decode: original 0x828C loads trailer words into D2/D6/D7; instructions shift the bit reservoir left; distance classes use A0+0x20 and A0+0x220 and variable D2, matching generation 8's distance VLC {5,9,modeBits}. `build/patches/decrunch.asm` preserves the exact local disassembly. No original code is proposed as the permanent renderer.

## Decoder implementation milestone

`tools/slamdecode.py` now implements the bounded backward MSB LZ decoder. It decodes all 13 SLAM containers on retail disk 1 to their declared lengths; decoded `Music.Bin` begins with **STIM**, an independent format anchor. Output hashes and counts are in `build/patches/decode-validation.json`; decoded assets stay under `build/decoded/`. Empty/truncated headers, invalid output sizes and truncated trailer cases were rejected. Byte equality against original-runtime output remains unverified because the container has no decoded checksum. Status for Asset Decoder is therefore IMPLEMENTED, with semantic validation on music and broader validation pending.

Usage: `python tools/slamdecode.py INPUT OUTPUT`. Headers, lengths, trailer mode, input exhaustion, run length and backreferences are checked; output defaults to a 64 MiB cap. Graphics are decoded bytes, not yet parsed here.
