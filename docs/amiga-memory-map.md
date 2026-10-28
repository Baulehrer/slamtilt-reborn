# Amiga coordinate and memory map

Reference: `build/corpus/test-adf/Game.exe`, 105592 bytes, extracted retail disk image; validate hash against `analysis/patches.json`. This is a relocatable Amiga HUNK executable, not a flat image.

- Hunk 0: CODE, file payload starts at **0x24**, length **0x106D0** (0x41B4 longwords).
- Hunk 1: declared allocation 0x1AAD longwords = **0x6AB4**, CHIP flag set. Hunk parser required to determine serialized data and relocations; allocation size is not a file range.
- All addresses below are **hunk-0-relative offsets**, before relocation. File offset = offset + 0x24 for this reference only. Runtime address = loaded hunk base + offset.
- WHDLoad 3.3/3.4 uses artificial reference base 0x1DA50 by subtracting it from patch base; 3.5 mostly expresses the subtraction in its patch entries. Those values are not universal RAM addresses.
- 3.5 menu entries use 0x1DBA0 rather than 0x1DA50; retain their explicit expression. Do not silently normalize the source label with a single global subtraction.
- BTTR HDD Game.exe contains a packing stub. WHDLoad 3.6 installed Game.exe starts RNC1. Source offsets apply to decoded executable hunks, not packed files.

| Offset | Evidence | Interpretation | Confidence |
|---|---|---|---|
| 0x0000 | MOVEM; Exec accesses through address 4 | OS startup | high |
| 0x021C–0x02C8 | INTENA/INTREQ/CIA save and disable; writes vector offsets 0x70/0x6C/0x68 | Hardware takeover and vector installation | high |
| 0x0EA2 | MOVEC VBR,D0, stores at 0x0EAE | Read vector base; WHDLoad substitutes zero | very high |
| 0x0EB2 | interrupt frame save; INTREQ/INTENA bit 7; RTE | level-4 interrupt handler | high |
| 0x0ECE | INTREQR read; dispatch bits 4,5,6; RTE | level-3 interrupt dispatcher (Copper/VBlank/blitter) | very high |
| 0x0F0C | clears INTREQ bit 5; calls 0x0FB6 | VBlank branch | very high |
| 0x2EE2 / 0x2F84 | dispatcher bit 4 / 6 targets | Copper / blitter interrupt branches | high |
| 0x5292 | installed in vector slot +0x68 | level-2 handler, probable CIA/input | medium |
| 0x7950–0x7AE0 | CIAB disk-select writes, CIAA disk status, DOS Lock/UnLock-like calls | floppy/media probing | high |
| 0x8280–0x83B8 | backward output, MSB bit reader; WHDLoad names StoneCracker | SLAM asset decruncher, StoneCracker generation-8 family | high |

`build/patches/hardware-candidates.json` records 155 aligned literal custom/CIA address occurrences. These are operand candidates, **not** 155 proven instructions: embedded data may match and A5-relative accesses are not included. A5 is frequently initialized to 0xDFF000, so literal search alone undercounts display/audio operations.
