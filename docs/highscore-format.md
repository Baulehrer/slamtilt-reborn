# Highscore file formats

Status: REIMPLEMENTABLE for reading original Amiga STTF and observed Windows CFG. Original runtime scoring is a separate question.

## Amiga STTF

Independent bundled sources `build/corpus/amiga/_extras/SlamMan/SlamMan/shm.c` (`highfill`, `hman`) and `build/corpus/amiga/patches/SlamtiltJudge-1.4/SlamtiltJudge/SlamtiltJudge/SlamtiltJudge.cxx` (`HighScore::Peek`, `Judge`) agree with corpus bytes:

| Field | Offset / length | Meaning |
|---|---|---|
| Magic | 0 / 4 | ASCII `STTF` |
| Score-array offset | 0x1e / 4 | Big-endian file offset; shm reads its low byte at 0x21 |
| Score | record +0 / 6 | Packed BCD, most significant digits first, 12 decimal digits |
| Initials | record +6 / 3 | Three stored characters; spaces are meaningful |
| Trailing bytes | record +9 / 5 | Observed zero; shm writes zeros; semantics unknown |

There are five records, stride 14. Judge uses fixed offsets Demon 0x76, Pirate 0x94, Mean 0x90, Space 0x90. Prefer the header pointer because highscore tools and table descriptors share the file. Preserve all bytes outside the record array when writing.

Example Mean default score bytes `00 15 00 00 00 00` represent 1,500,000,000; initials `44 20 53` are `D S`. The Slam-HI extra has `00 23 22 58 50 80`, or 2,322,585,080. This discriminates packed BCD from binary and unpacked BCD. Judge sorts scores lexicographically from byte zero, consistent with most-significant-first storage.

Judge's writer copies only nine meaningful bytes into a 16-byte buffer but writes 14 bytes: it should not be copied as a safe native implementation. shm's literal string mutation is also unsuitable for modern C. Their layouts are evidence, not reusable production code.

## Windows CFG

Observed demo, UK, US, ROM and RIP `SLAMTILT.CFG` are 332 bytes. Four arrays preserve the exact six BCD bytes and three initials of the clean CD32 STTF defaults, but use stride 10 (one trailing byte).

| Table | Array offset | Records |
|---|---:|---:|
| Mean Machines | 0x68 | 5 |
| The Pirate | 0x9a | 5 |
| Ace of Space | 0xcc | 5 |
| Night of the Demon | 0xfe | 5 |

Leading 56 bytes decode as seven little-endian doubles: 60, 70, 56, 70, 91, 75, 75. Their meanings are unknown. Bytes 56..103 and 304..331 remain unknown configuration fields. Do not assume platform equivalence beyond the matching record payload.

`tools/slamscores.py FILE` provides read-only JSON inspection with bounds checks and strict BCD validation. Validation parsed 66 STTF/CFG corpus files without errors. Mapping of Windows groups to tables is confirmed by comparing each group's complete score/initial payload against all four CD32 defaults, not solely by array order.
