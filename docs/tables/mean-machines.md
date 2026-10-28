# Mean Machines

Windows evidence: initializer 0x41b9e0; DAT filename reference 0x41ba06; loader 0x40f7e0. Table-specific callback addresses are installed at global slots 0x46de14–0x46de64. Their individual event semantics remain unknown.

Playfield palette DAT+0x1590c8, pixels DAT+0x1594c8, 320×600 indexed8. See windows-subsystems.md and file-formats.md for confidence and validation. Historical first-pass note superseded: current native physics, scoring and several mode chains are implemented; see `../STATUS.md`.

Original rulebook now indexed in `analysis/table-rule-oracles.json`: STRONG behavioral matches identify native internalmode4/phase1 as Kickstart and phase2 as Drag Race. Official main-mode numbering is separate. Use mode start shots and awards to locate remaining callbacks.
