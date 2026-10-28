# Mean Machines – Linux RC

Das lokale RC startet mit:

```sh
build/compat/releases/slamtilt-mean-rc-pythonfree-data/play-mean
```

Die beiden Ordner `slamtilt-mean-rc-pythonfree` und `slamtilt-mean-rc-pythonfree-data` können gemeinsam
verschoben werden. Das Programmpaket enthält SDL3/libxmp, eingebettete
Schriften/Shader und technische Metadaten. Die acht Original-/Cachedateien
liegen ausschließlich im separaten privaten Datenpaket unter `build/`.

Einzeln ist das Programm ebenfalls verschiebbar:

```sh
/path/to/slamtilt-mean-rc/slamplay --data-dir /path/to/private-data --check
/path/to/slamtilt-mean-rc/slamplay --data-dir /path/to/private-data
```

Alternativ setzt `SLAMTILT_DATA_DIR` den Datenpfad. Launcher-Optionen stehen
vor den normalen Spieloptionen. `--check` prüft Vollständigkeit und die
SHA-256-Werte des unterstützten Datenprofils. Fehlende Minigame-Caches führen
zu einer klaren Fehlermeldung. Optionen/Highscores bleiben im bisherigen
SDL-Benutzerverzeichnis; Programm und Spieldaten können schreibgeschützt sein.

## Original-Demo direkt importieren

Ohne Terminal-Import: `slamplay` öffnet im entpackten Programmpaket automatisch
das native Erststartfenster, wenn keine Daten gefunden werden. Dort den
Original-Demo-Ordner mit `SLAMTILT.EXE` und `DAT` auswählen oder einen bereits
vorbereiteten Datenordner übernehmen. Ordner können auch auf das Fenster
gezogen werden. Der Import läuft im Hintergrund; danach startet Mean direkt.
Import und Datenprüfung laufen vollständig nativ, ohne Python/Wine/Emulator.
Importierte Daten und die gemerkte Auswahl liegen im normalen SDL-
Benutzerverzeichnis. Spätere Starts prüfen die Daten und öffnen sofort den
Tisch. `slamplay --setup` öffnet die Auswahl erneut. Fehlgeschlagene Auswahl
ersetzt keine zuvor gültige Auswahl; explizite `--data-dir`- und Environment-
Pfade bleiben maßgeblich. `--check` öffnet keine Dialoge.

Der System-Ordnerdialog hängt vom vorhandenen SDL/Desktop-Backend ab; der
Drop-Pfad sowie `--data-dir` bleiben verfügbar. Automatisiert geprüft ist der
gemeinsame Auswahl-/Import-/Speicherpfad; ein echter Portal-Klick wurde nicht
automatisiert. Das native Fenster wurde auf diesem Desktop gerendert und
sein Screenshot geprüft.

Im Quellbaum und im entpackten Programmpaket:

```sh
./slamimport /pfad/SLAMTILT.EXE /pfad/DAT /pfad/neue-private-daten
./slamplay --data-dir /pfad/neue-private-daten --check
./slamplay --data-dir /pfad/neue-private-daten
```

Im Quellbaum heißen die Werkzeuge `tools/slamimport` und `tools/slamplay`.
Der native C++-Importer benötigt keine zusätzliche Laufzeit. Er prüft
EXE und beide DAT-Dateien, extrahiert PE-Sektionen und Lookup-Tabelle und
ergänzt die bereits verifizierten Startzustände. Alle acht Ergebnisse müssen
bytegenau dem bestehenden SHA-256-Profil entsprechen. Wine, Unicorn, alte
Caches und ein laufendes Originalspiel sind nicht erforderlich. Vorhandene
Zielverzeichnisse werden abgewiesen, auch leere. Unterstützt ist ausschließlich
EXE-SHA `31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00`
mit den passenden Demo-DATs; kein allgemeiner Retail-/Amiga-Importer.

Die kleine Startzustands-Rezeptdatei ist aus vorhandenen, geprüften Snapshots
abgeleitet. Sie rekonstruiert nicht den vollständigen Original-Startup.
`tools/slamimport_reference.py` bleibt ausschließlich als unabhängige
Entwickler-/Testreferenz im Quellbaum und wird nicht mit dem Programm geliefert.

## Paket erstellen

Voraussetzung: der bereits validierte lokale Build und die vorbereiteten Daten.

```sh
cmake --build build/native -j 3
tools/slampack --output build/releases/mean-rc-next \
  --data-output build/releases/mean-private-next
```

Vorhandene Ziele werden nicht überschrieben. Ohne `--data-output` entsteht
nur das assetfreie Programmpaket. `--source-data`, `--prepared` und `--minigame`
geben alternative Quellen des exakt unterstützten Acht-Dateien-Profils an.
Die nötigen Dateinamen stehen in `packaging/DATA-README.txt`.

Für andere Build-Umgebungen sind die Lizenzquellen mit `--sdl-license` und
`--xmp-license` wählbar. CMake-Komponente `Runtime` ist das Staging-Layout;
`slampack` ergänzt die beiden Bibliotheken, Hashmanifest und Archive.

Zum Spielen werden weder Python noch Wine, Unicorn oder der Quellbaum benötigt.
Rohdatenimport aus einer beliebigen Retail-/Amiga-Version ist in diesem RC
nicht implementiert. Dieses Paket verwendet das verifizierte Windows-Mean-
Demo-Datenprofil mit den vorhandenen Retail-Minispielregeln.

## Verifikation und Plattformgrenze

`mean_package_acceptance` erstellt die Archive, entpackt sie an einen neuen
Pfad mit Leerzeichen und testet einen unabhängigen Arbeitsordner. Auf diesem
Host blendet Bubblewrap den Quellbaum vollständig aus; Programm/Daten sind
schreibgeschützt. Der echte SDL-Frontendpfad prüft Audio, Fokus/Minimieren,
Vollbild, Highscore-Speichern und Neustart. Ein zusätzlich eingebundener nativer
Prüfer spielt die bestehende Fünf-Modi-Fixture zweimal mit Paketdaten und der
minimalen Startdatei bis zur unveränderten Endreferenz durch. Dieser Prüfer
und seine Eingabefixture sind Testwerkzeuge und werden nicht ausgeliefert.

Separat wurde das fertige Paket mit echtem GPU-/Audiogerät gestartet. Eine
Screenshot-Kontrolle und die Geräte-/Frontendprüfungen waren erfolgreich.
Das bestätigt keine gehörte Ausgabe oder subjektives Spielgefühl.

Das neue x86_64-Paket wurde mit Debian12/GCC12 und neu gebautem SDL3/libxmp
erzeugt. Seine höchsten Symbolanforderungen sind GLIBC2.34, GLIBCXX3.4.29 und
CXXABI1.3.9. Tatsächlich geprüft sind Debian12-Userspace mit glibc2.36 im
Container sowie dieser Laptop mit glibc2.43, dort auch echtes GPU-/Audiogerät.
Der Container verwendet den Host-Kernel; andere Distributionen, ältere Kernel
und fremde GPU-Treiber sind damit nicht pauschal bestätigt. Das bisherige
Host-RC mit glibc2.43/GLIBCXX3.4.32 bleibt unverändert erhalten.
Alle ermittelten ABI-Versionen und Datei-Hashes stehen in `bundle.json`.

Belege: `analysis/mean-release-island.json`,
`analysis/traces/mean-package-acceptance.json`, `build/mean-rc-host/report.json`.

## Build mit älterer Linux-ABI

```sh
tools/slamcompat
python tools/verify_mean_compat.py
```

Voraussetzungen sind Docker, die vorhandenen fünf lokalen geprüften Lifts und
die unterstützten Originaldaten. Der erste Toolchain-Build benötigt Netzwerk;
Port-Build und Debian-Laufzeittest laufen ohne Netzwerk. Basis-Image-Digest,
SDL-Quellhash und libxmp-Commit/Archivhash stehen in
`packaging/compat-sources.json`. Apt-Paketversionen werden protokolliert; dies
ist kein bitreproduzierbarer Apt-Snapshot. Originale Spieldaten kommen nicht
ins Toolchain-Image. Der Quellbaum ist beim Port-Build schreibgeschützt.

Ergebnisse liegen unter `build/compat/releases/`; `build/compat/build.json`
verknüpft Image-ID, Quellpins und Prüfbericht. Bestehende Releases werden nicht
überschrieben. Neue Namen sind mit `--release-name NAME` möglich.

Die Prüfung entpackt die fertigen Archive separat und testet Erststart,
Raw-Import, gespeicherten Datenpfad, fehlende/beschädigte Daten, Audio/Fokus/
Vollbild/Highscores sowie zweimal das vollständige Fünf-Modi-Spiel. Derselbe
Compiler-Build besteht diese Spielreferenz auch unter Debian12 unverändert:
83056Ticks,924072310Punkte,State/Audio-Hash7646546959636972790. Programm und
vorbereitete Daten werden im Laufzeittest schreibgeschützt eingebunden;
der Quellbaum ist nicht eingebunden. Belege:
`analysis/mean-compat-island.json`, `analysis/traces/mean-compat-acceptance.json`
und `analysis/traces/mean-compat-package-acceptance.json`.
