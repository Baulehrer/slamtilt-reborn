Mean Machines runtime data (private, user-owned)

The native first-run window opens automatically when no data is available.
Choose the supported Windows DAT folder containing MEAN.DAT and MAIN.DAT,
or select a complete prepared data folder. Drop a folder onto the window as
an alternative to the system folder dialog. The selection is saved in your
normal SDL preference directory and verified again on subsequent starts.
Use ./slamplay --setup to choose another folder. Bad selections do not replace
the prior working selection. Imported data is stored in the user preference
directory; program and original game folders can remain read-only.

Put your prepared Mean data here, or start:
  ./slamplay --data-dir /path/to/private-mean-data
You can also set SLAMTILT_DATA_DIR. The game never writes to this data folder.

Required layout:
  MEAN.DAT
  MAIN.DAT
  mean-prepared/pe-data.bin
  mean-prepared/engine-globals.bin
  mean-prepared/flipper-state.bin
  mean-prepared/lookup.bin
  mean-minigame-prepared/image.bin
  mean-minigame-prepared/runtime.bin

Import supported Windows DAT files with the native importer:
  ./slamimport /path/to/DAT /path/to/new-private-data
  ./slamplay --data-dir /path/to/new-private-data --check
  ./slamplay --data-dir /path/to/new-private-data

No EXE is needed. Math tables, engine and table parameters are initialized
by native code. Supported DAT files are checked against their known hashes.

Optional legacy import remains available with an explicit EXE argument.
Supported legacy Demo EXE SHA-256:
  31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00
Supported legacy Retail EXE SHA-256:
  185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6
MEAN.DAT and MAIN.DAT must match the included data profiles. Retail prepared
data uses share/slamtilt/mean-retail-data.sha256; Demo uses mean-data.sha256.
All eight generated files are checked against the verified runtime profile.
Existing destinations are preserved. No Wine, emulator or cache capture is
needed. Import, data validation and play do not require Python.
The default DAT-only importer does not read any EXE or prepared cache.
Runtime game routines are compiled native code.
Amiga imports are not provided by this package.
Original assets and prepared binary data are not included in the public runtime.
