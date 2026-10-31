# X-Arcade / three-screen cabinet extension

The optional `SLAMTILT_CABINET_DMD=1` environment variable enables a separate
`Slamtilt Cabinet DMD` SDL window and removes the DMD allocation from the
playfield. Mean Machines and The Pirate render all 600 table rows without
camera scrolling; Ace of Space and Night of the Demon already use whole-table
presentation. Fit aspect preserves the original geometry. The compositor
places the DMD on the secondary screen; no fixed monitor IDs are built in.
The DMD renderer has VSync disabled so it cannot impose the secondary display's
60 Hz cadence on the 120 Hz playfield. It is borderless and non-focusable.

`SLAMTILT_CABINET_KEYBOARD=1` disables native gamepad action synthesis and lets
Batocera's per-ROM evmapy configuration own the X-Arcade mappings and hotkey
chords. Keyboard input remains enabled. R also activates the selected item in
the main menu, allowing Start to mean start/new game throughout the port.
Neither variable is enabled by default. Simulation code and physics cadence
are unchanged.

Deployed cabinet scripts, key mappings, display rules, source patch, checksums
and the German setup record are maintained in the adjacent computer-tools
project under `batocera-cabinet/` and `BATOCERA-CABINET.md`. Runtime and saves on
Batocera live entirely under `/userdata`, outside the updateable system image.

Verification: compatibility Docker build of `slamtilt`, `slamview`, `slamslice`,
`slamimport`, `slamsetup`; CTest `display_layout`, `gamepad_input`, and
`frontend_runtime_safety`; all four tables exercised on the target machine.
The layout test also covers the optional 2160x3840 / 600-row cabinet viewport.
