# Table engine — first static evidence

Status: PARTIAL. Windows has separate table initializers sharing a file loader and display code. Full VA 0x404e60 is a four-entry indirect dispatch table (data embedded in code); table identities should be confirmed from targets rather than linear disassembly.

Mean entry 0x41b9e0 loads MEAN.DAT and installs many code pointers into globals 0x46de14–0x46de64, while installing DATbase+constant pointers into other globals. Thus a shared engine plus table-specific code/data and callback slots is supported. A standalone rule scripting language is not established. Mean DAT size is hardcoded as 0x18c008 at 0x41ba01.

Porting boundary: separate native table asset profiles from rules. Preserve a generic event interface as a new design, without claiming SWITCH_HIT/MODE_START etc are recovered original event IDs. The next useful analysis is callback dispatch and matching Mean demo/full initialization.

## Mean callback candidates (full RIP)

Stores within initializer 0x41b9e0; semantic names unknown. These are static code pointers and may include callbacks plus other dispatch helpers.

| Global slot | Code target | Store instruction |
|---|---|---|
| 0x46de24 | 0x4275d4 | 0x41ba33 |
| 0x46de20 | 0x427670 | 0x41ba39 |
| 0x46de38 | 0x427068 | 0x41ba3f |
| 0x46de28 | 0x4269ac | 0x41ba45 |
| 0x46de34 | 0x4268a8 | 0x41ba4b |
| 0x46de2c | 0x426518 | 0x41ba6f |
| 0x46de50 | 0x4262d0 | 0x41ba75 |
| 0x46de58 | 0x423db4 | 0x41ba7b |
| 0x46de5c | 0x4240ac | 0x41ba8d |
| 0x46de60 | 0x423db0 | 0x41ba99 |
| 0x46de54 | 0x423ce8 | 0x41bb00 |
| 0x46de40 | 0x421d3c | 0x41bb12 |
| 0x46de44 | 0x421700 | 0x41bb29 |
| 0x46de48 | 0x420544 | 0x41bb3b |
| 0x46de18 | 0x424520 | 0x41bb4c |
| 0x46de14 | 0x4274ec | 0x41bb52 |
| 0x46de30 | 0x426540 | 0x41bb62 |
| 0x46de64 | 0x423db0 | 0x41bb72 |
| 0x46de3c | 0x424b10 | 0x41bb82 |
| 0x46de4c | 0x425f94 | 0x41bb9f |
