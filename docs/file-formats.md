# File formats and immediately reusable assets

Status: Windows and Amiga original playfields IMPLEMENTED; both native decoders verified against independent decoded pixels. Original files stay under user corpus/build, never in native source.

## Windows table DAT: verified native path (ASSET-001)

The files have no identifying magic. SHA256 profiles in `tools/slaminfo` identify the four tested full-release assets. Native viewer currently selects the layout by exact file size and verifies the reserved zero byte of every palette entry; it does not authenticate the whole file. Other layouts/revisions are rejected by size, and a same-sized modified file can pass structural checks.

| Table | File bytes | Palette | Indexed pixels | Extent |
|---|---:|---:|---:|---|
| Mean Machines | 1622024 | 0x1590c8 | 0x1594c8 | 320×600 |
| The Pirate | 1543772 | 0x14605c | 0x14645c | 320×600 |
| Ace of Space | 1568309 | 0x14c035 | 0x14c435 | 320×600 |
| Night of the Demon | 1546096 | 0x146830 | 0x146c30 | 320×600 |

Palette = 256 four-byte entries `[0,R,G,B]`, 8-bit components. Pixels = one byte per index, row-major, top-to-bottom, stride320, 192000 bytes. RGB output has been visually inspected; loader instructions independently reference these offsets. See [Windows map](windows-subsystems.md), WIN-003, for VAs. These images are base playfields; the observed bright lamps do not establish dynamic lamp state or compositing rules.

At file start the first big-endian u32 is 0x7c: 31 big-endian sample offsets. At each sample offset, five big-endian u16 fields precede sample bytes: length in words, volume-like field, loop start words, loop length words, reserved. Consecutive offsets agree with `10 + 2*length_words` in examined files. Signedness, original playback rate and audio engine use require separate validation. The following music/graphics/overlay payload is not a fully understood generic archive directory. Per-table code contains hardcoded offsets.

Do not assume every `.DAT` follows this layout. MAIN, MENU, MENU2, INTRO and SLAMTILT.CFG differ. Resurrection 1999 is a separate game family.

## Amiga SLAM containers (ASSET-002)

```
0x00  char[4]  "SLAM"
0x04  BE u32   marker 0x50 in inspected files
0x08  BE u32   unpacked length
0x0c  BE u32   packed length
0x10  bytes    backward compressed stream; trailer starts at12+packed
```

Game.exe hunk-relative decoder entry 0x8280 supports backward StoneCracker generation8 interpretation; see [Amiga map](amiga-memory-map.md). Trailer at12+packed is three BE16 values: distance mode, bit reservoir, available bits. Decoding is bounded and validated on20 full-pack SLAM assets. Do not equate packed length with file size minus16 without accounting for trailer/alignment. Table `.Bin` contains executable gameplay code as well as data. Decoded `.Raw` starts with BE32 section base S; six BE32 section-relative offsets at S. Offset0=0x18 points to320×600 pixels, row stride320 bytes, eight planes of40 bytes, plane0 supplies index bit0 and bit7 is leftmost. Offset1=0x32938 points to256×[0,R,G,B] palette. Native `slamview decoded.Raw --amiga` loads this layout. Other sections remain partially understood. See [overlay map](amiga-overlays.md).

RNC1-packed WHDLoad Game.exe is a different compression layer; use uncompressed retail/JST/CD32 HUNK reference for static addresses.

## Amiga descriptors and saves

`STTL` is a big-endian table-path pointer list terminated by 0xffffffff. `STTF` descriptors include disk filenames and highscore records; score pointer is BE32 at0x1e. Five records each contain six bytes Packed BCD, three initials and five unresolved trailing bytes. See [highscore format](highscore-format.md). Runtime score representation is still unverified.

## Tools

- `tools/slaminfo FILE... --json`: SHA256, entropy, compression/descriptor signatures, exact known Windows playfield profiles, sample directory and STTF saves.
- `tools/slamview TABLE.DAT` or `tools/slamview DECODED.Raw --amiga`: native SDL3 viewer. Up/Down/wheel scroll; Home/End; Escape. `--export file.bmp` exports the entire base image; `--frames N` bounds a smoke run.
- `tools/slamscores.py`: read-only dedicated score inspection.

Next assets with highest value: decode Amiga `.Bin` overlays; identify collision geometry and callbacks; recover Windows sprite descriptors and the 49-row trailing display asset. The latter has not been promoted to a DMD format solely from its appearance.
