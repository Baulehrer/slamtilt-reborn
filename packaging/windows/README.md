# Windows x86_64 unsigned release

Build on a Linux Docker host from the repository root:

```sh
docker build -t slamtilt-windows-toolchain:bookworm packaging/windows
docker run --rm -v "$PWD:/workspace" slamtilt-windows-toolchain:bookworm sh -c 'sh packaging/windows/build.sh && sh packaging/windows/verify.sh'
```

The build uses MinGW GCC 12 (POSIX threading), SDL 3.4.18 and the existing
`build/libxmp` source checkout. Generated native physics sources already required
by the project must exist under `build/generated`. It builds the current shared
launcher and four native table engines. No game data enters the toolchain image.

Outputs under `build/windows-release/artifacts` are a portable ZIP, per-user NSIS
installer and SHA256SUMS. Packaging refuses to overwrite an existing stage; use a
new output directory for a new candidate. The installer requires no administrator
rights. It creates a Start menu shortcut and an uninstall entry. Imported data and
settings in the user's Windows profile are retained by uninstall.

There is no signing step and no certificate requirement. Windows can display
unknown-publisher or SmartScreen warnings for these unsigned artifacts.

`verify.sh` runs a native Windows smoke executable through Wine, checking atomic
replacement of existing preferences, repeated highscore saves and reload, and
SDL child process startup and exit. Wine is a cross-host check; actual Windows
hardware acceptance must be recorded separately.

To exercise the installer with Wine on Linux, add `i386` as a Debian architecture
and install `wine32:i386 xvfb xauth` in the toolchain image, then run:

```sh
xvfb-run -a sh packaging/windows/installer-check.sh
```

This uses a separate Wine prefix, performs a silent per-user install, verifies the
shortcut and uninstall registry entry, runs the installed launcher, uninstalls,
and checks that a user-profile sentinel remains.
