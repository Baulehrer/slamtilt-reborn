# Windows subsystem map — first static pass

Addresses below are preferred PE virtual addresses in the extracted English RIP executable, SHA256 recorded in `analysis/windows-symbol-map.json`. They are instruction anchors unless explicitly marked entry points. Reproduce import and cross-reference extraction with `python tools/analyze_windows.py` (GNU objdump required). No original bytes are shipped by the analysis tool.

## WIN-001: executable family

Full: PE32 i386 GUI, entry `0x44f448`, image base `0x400000`, PE timestamp 1996-12-09 06:14:51 UTC. Demo: entry `0x422eb8`, timestamp 1996-12-09 20:21:05 UTC. Downloaded fix: entry `0x44f818`, timestamp 1997-08-20 13:59:25 UTC. PE dates are metadata, not independently authenticated build dates.

Full code section BEGTEXT is 0x53000 bytes; demo 0x27c00. DGROUP, .bss, .idata and .reloc are present. Full contains the explicit string `WATCOM C/C++32 Run-Time system` at file offset 0x4e85b. Watcom runtime identification: high confidence; whether each gameplay routine originated in C, C++ or assembly remains unknown. Code is directly disassemblable, without a detected executable unpacking stage.

Both builds import DirectDrawCreate, DirectSoundCreate, WinMM timing and MCI, Win32 messages, file IO and threading. No static DirectInput import or external CRT DLL is present. COM calls are indirect and therefore absent from an import-only callgraph.

## WIN-002: API islands

| Island | Full anchors | Demo anchors | Interpretation |
|---|---|---|---|
| Renderer setup | DirectDrawCreate calls 0x4020b9, 0x40383e | 0x40216d, 0x4038f2 | Two display paths; detailed role unresolved |
| Main loop / timing | timeGetTime at 0x401014, 0x4012fd and 9 further sites | corresponding early sites equal, later displaced | WinMM clock plus message processing |
| Timer installation | SetTimer at 0x4020a5, 0x40382a | 0x402159, 0x4038de | Close to display setup |
| Audio setup | DirectSoundCreate 0x44d5e7 | 0x420b07 | Strong audio anchor |
| File IO / CRT | ReadFile 0x4507de; CreateFileA 0x450533/555, 0x4524b0/4da | 0x4257b8; 0x4242d8/2fa, 0x427256/280 | These are runtime wrappers, not DAT parser boundaries |
| Table file loader | 0x40f7e0 called with filename and exact byte count | Not yet mapped | Shared loader used by table initializers |

Full 0x402c72–0x402d99 combines PeekMessage/GetMessage/TranslateMessage/DispatchMessage, surface COM operations and timeGetTime. This is a concrete main-loop/display integration island; it does not establish a gameplay tick rate.

## WIN-003: original image data is immediately reusable

Mean initializer entry 0x41b9e0 passes `DAT\\MEAN.DAT`, expected length 0x18c008, to 0x40f7e0. At 0x41bb88 it forms DATbase+0x1590c8; at 0x41bb99 it forms DATbase+0x1882c8. Their difference is 1024+320×600. Palette at 0x1590c8 uses 256 entries with bytes 00,R,G,B; pixels follow at 0x1594c8. Root agent visually confirmed the resulting table.

Other loader-referenced palette candidates, validated for 00 prefix on all 256 entries:

| DAT | Palette offset | Pixel offset | Initializer filename anchor |
|---|---|---|---|
| DEMON | 0x146830 | 0x146c30 | 0x40fee2 |
| MEAN | 0x1590c8 | 0x1594c8 | 0x41ba06 |
| PIRATE | 0x14605c | 0x14645c | 0x42b3b6 |
| SPACE | 0x14c035 | 0x14c435 | 0x439b06 |

Width 320 is independently supported by row address arithmetic at 0x40b76c and row advance at 0x40b808. At 0x404f40–0x404f91 graphics setup reads a descriptor's +0x18 pointer, stores it at 0x46b770/0x46c48c, then adds 0x400 and stores pixels at 0x46c490. This is a useful generic descriptor anchor, but the complete descriptor lifetime has not been reconstructed.

Port strategy: load known DAT profiles and render indexed pixels immediately. Stop detailed DirectDraw recovery for this milestone. Per-table hardcoded offsets imply that a fully generic self-describing DAT directory must not be assumed.

## WIN-004: demo/full matching

Import order and early clock anchors are strongly shared. A bounded comparison zeroed HIGHLOW relocation operands and matched 64-byte aligned unique code blocks: 1105 shared full/demo blocks, versus 109 full/fix. The lower fix count is not evidence of a rewrite: aligned block comparison misses insertions and relative-call changes. Matches and limitations are in `analysis/windows-symbol-map.json`. Function equivalence is not proven by a block match.

The 1999 Resurrection CD is a distinct game family: BMB/WMw/GM4/IN4 files must not be treated as original 1996 DAT equivalents.

## Next highest-value actions

1. Use image profiles for native renderer now; trace palette and scroll position only as needed.
2. Compare Mean initializer and its installed callback table against demo; map callbacks at globals 0x46de14–0x46de64.
3. Follow the caller of 0x40b720 and identify whether its signed 16-bit shifts describe sprites, ball state or collision rectangles before naming fields.
4. Find physics through writes to stable ball coordinates and controlled runtime traces; API proximity alone is insufficient.

The CD Gamer Mean demo DAT is byte-identical to the full RIP Mean DAT: 1,622,024 bytes, SHA256 `1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f`. The same image profile applies directly.
