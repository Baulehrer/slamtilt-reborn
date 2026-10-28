# Slamtilt - Reborn

Gemeinsamer Linux-Release-Kandidat für Mean Machines, The Pirate, Ace of Space
und Night of the Demon. Start im Projekt: `tools/slamtilt-reborn`.
Die kompatible Kurzform `tools/slamtilt` bleibt erhalten.

Aktuelles Archiv: `build/compat/releases/slamtilt-reborn-linux-x86_64-rc3.tar.gz`.
Nach dem Entpacken `./slamtilt-reborn` starten; `./slamtilt` funktioniert ebenfalls.
Das Paket enthält keine Originalassets. Zum Importieren und Spielen werden weder
Python, Wine, Emulator noch Projektordner benötigt.

## Daten und Bedienung

F2 bzw. „Import Original Data“ übernimmt die unterstützten Windows-DAT-Dateien
für alle vier Tische gemeinsam. Wähle den DAT-Ordner oder seinen übergeordneten
Spielordner. Eine EXE wird auch beim ersten Import nicht benötigt; siehe
[benötigte Dateien und Erklärung](dat-only-import.md).
Originaldaten bleiben unangetastet. Vorhandene Einstellungen, Datenpfade
und getrennte Highscores werden im bisherigen SDL-Präferenzverzeichnis erhalten.

Maus oder Pfeiltasten/Enter wählen den Tisch; 1–4 wählen direkt. O öffnet die
Optionen. Im Tisch: Escape öffnet Optionen; „Main Menu“ oder F10 kehrt zurück.
Pause und Neustart verwenden weiterhin die jeweilige native Tischsteuerung.

Das neue Neo-90s-Menü zeigt Original-Playfields mit Chrom, Lampen und DMD-Akzenten.
Options → General schaltet auf Classic um oder reduziert Animationen. Display,
Shader, DMD-Position/Farbe, Audio und Steuerung bleiben gemeinsam einstellbar.
`--session-reports DIR` speichert bei Bedarf private Sitzungsdiagnosen.

## Reproduzierbare Prüfungen

- Build: `tools/slamtilt-reborn-compat` verwendet die gepinnte Debian-12-Umgebung
  mit GCC12, SDL3 und libxmp; Quellverzeichnis schreibgeschützt, Netzwerk aus.
- `tools/verify_reborn_distribution.py`: echte Debian-Laufzeit, Erstimport,
  Daten-SHAs, alle vier Tischprogramme und längere beschleunigte Sitzungen.
- `tools/verify_main_menu_package.py --archive ARCHIV`: verschobenes Paket,
  verborgener Checkout, schreibgeschützte Originale, leeres PATH.
- `tools/verify_reborn_focus.py`: echte Compositor-Fokuswechsel, Pause, Audio und
  Rückkehr über eigene Testfenster. Benötigt die vorhandenen lokalen Testwerkzeuge;
  diese sind keine Laufzeitabhängigkeiten des Spiels.
- `tools/verify_reborn_endurance.py`: vier seriell ausgeführte Fünf-Minuten-Läufe.
  Während der Messung keine parallelen Builds/GPU-Tests starten.

Gültige ABI-Anforderungen und archivgebundene Prüfergebnisse stehen in
`analysis/traces/reborn-distribution.json` und den abschließenden Reborn-Indizes.
Derzeit tatsächlich geprüft: Debian12 und die vorhandene Linux-/GPU-Umgebung.
Bisherige Einzel-RCs und frühere gemeinsame Pakete bleiben unverändert erhalten.

Abnahme: [Release-Index](../analysis/reborn-release-island.json) und
[Integritätsprüfung](../analysis/traces/reborn-release-gate.json). Vier serielle
Fünf-Minuten-Läufe bestanden; Demon ausdrücklich mit kontrolliertem Hintergrundfokus
und QA-only-SDL-Messprobe. Frühere Demon-Zeitspitzen bleiben mit unbekannter Ursache
dokumentiert. Echte Alt-Tab-/Audioprüfung ist davon unabhängig bei allen vier Tischen
bestanden. Vollständige Original-Trajektoriengleichheit für Mean bleibt PARTIAL.

Diese Echtzeit-Abnahme gehört zum erhaltenen RC1. Der RC2 ergänzt den Mean-Retail-
Import mit eigenen [Daten-/Gameplay-Nachweisen](../analysis/traces/mean-retail-import.json)
und [Debian12-Prüfungen](../analysis/traces/mean-retail-distribution.json).

RC3 ergänzt den vollständig nativen DAT-only-Erstimport. Die früher benötigten
EXE-Daten werden aus Formeln und nativen Tisch-/Engine-Parametern erzeugt.
Die [isolierte DAT-only-Prüfung](../analysis/traces/dat-only-import.json) startet
mit frischem Benutzerprofil ohne EXE, Checkout oder vorbereitete Caches.
