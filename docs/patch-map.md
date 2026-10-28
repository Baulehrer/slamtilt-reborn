# Patch archaeology

Source-backed patch list: `analysis/patches.json` (30 records across 3.3/3.4/3.5). Offsets are hunk-0-relative; original bytes are an **8-byte context**, not necessarily the replaced span. Replacement calls target slave routines and cannot be serialized to stable bytes without assembling/loading the slave.

## WHDLoad 3.5 validated reference contexts

| Hunk offset | File offset | Original context | Operation / target | Purpose |
|---|---|---|---|---|
| 0x936a | 0x938e | `c0fc0048d3c00c79` | PL_PS fix_in_game_menu_af | menu index bounds guard |
| 0x93d8 | 0x93fc | `c0fc0048d3c00c79` | PL_PS fix_in_game_menu_af | menu index bounds guard |
| 0x9446 | 0x946a | `c0fc0048d3c00c79` | PL_PS fix_in_game_menu_af | menu index bounds guard |
| 0x94c0 | 0x94e4 | `c0fc0048d3c00c79` | PL_PS fix_in_game_menu_af | menu index bounds guard |
| 0x953a | 0x955e | `c0fc0048d3c00c79` | PL_PS fix_in_game_menu_af | menu index bounds guard |
| 0x95a8 | 0x95cc | `c0fc0048d3c00c79` | PL_PS fix_in_game_menu_af | menu index bounds guard |
| 0x7960 | 0x7984 | `6700003008f90004` | PL_B $60 | LED |
| 0x79aa | 0x79ce | `6700003008f90003` | PL_B $60 | LED |
| 0x79f4 | 0x7a18 | `6700003008f90003` | PL_B $60 | LED |
| 0x7a3e | 0x7a62 | `6700003008f90003` | PL_B $60 | LED |
| 0x892 | 0x8b6 | `4eb90000d3ba33fc` | PL_P _quit | original quit crashes |
| 0xea2 | 0xec6 | `4e7a080123c00000` | PL_L $70004E71 | VBR |
| 0x8280 | 0x82a4 | `50492a48d1d9d3d1` | PL_PS start_stc | start of StoneCracker decrunch |
| 0x8286 | 0x82aa | `d3d178007a104c91` | PL_W $4E71 |  |

## Pattern patches outside Game.exe

| Payload | Search | Replacement / behavior | Confidence |
|---|---|---|---|
| intro.bin via intercepted DOS RunCommand, first 28700 bytes | 1001 4841 16F4 | Replace write with chip-memory destination guard | 0.98 source |
| intro.bin, first 28700 bytes | 4E7A0801 (MOVEC VBR,D0) | 70004E71 (MOVEQ 0,D0; NOP) | 0.99 source |
| decoded payload size 0x60540, first 0x4000 bytes | 4E7A0801 | 4E717000 (NOP; MOVEQ 0,D0) | 0.99 source |
| decoded demon.bin size 0xA89D4, range 0xA0000–0xA8000 | 12F9FFFFFFFF12F9FFFFFFFF | call writes six literal FF bytes, then skip original sequence | 0.99 source |

These are pattern-relative coordinates and must not be listed as fixed Game.exe addresses. No runtime trace has been performed.

## Version and other patch boundaries

WHDLoad 3.3 source is present in old-2003, 3.4 in old-2006, 3.5 in old-2009. The 3.6 archive contains compiled slaves and ReadMe, **no source**. ReadMe says 3.6 was rewritten by Psygore, eliminated Kickstart/lowlevel dependencies, adds blitter wait, colorbit correction, CD32 input and immediate-highscore saving. Therefore 3.5 addresses cannot automatically describe 3.6 patch implementation.

`slampch` is a binary-containing unified diff, not an executable; author describes Workbench/MCP startup hang fix and file shrinking by four bytes. Exact changed instructions still require safely reconstructing both sides and comparing HUNK/relocations.

`DC-STFIX.DMS` is a disk container, not a flat code patch. The separate Digital Corruption ADF provides a full Game.exe suitable for binary comparison. Neither has yet been given semantic patch addresses here.

SLAMFIX/Game.exe has three hunks and an added leading code hunk; raw byte-offset comparison with retail will mislabel relocated original code. `nts_slamtiltcd` and `slamtilthd` include `SlamTiltAddCD32Pad`, so CD32 input evidence is available even without a standalone SlamCD32PAD archive. These compiled helpers remain unmapped.

## Highest-value next steps

1. Decode SLAM table overlays; this immediately enables graphics plus executable gameplay-tail analysis.
2. Parse compiled 3.6 slave patch lists with command definitions from WHDLoad includes; confirm addresses against decoded retail.
3. Reconstruct slampch diff as binary input/output, isolate 68040/HD-Ninja hunks, and classify changed instructions.
4. Annotate Ghidra from hunk offsets after actual import image bases are known. No Ghidra project exists yet; JSON avoids falsely claiming annotations were applied.
