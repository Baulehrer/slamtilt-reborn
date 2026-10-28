# Originaldaten für Slamtilt - Reborn

Ab RC3 reichen die unterstützten **Windows-DAT-Dateien für alle vier Tische**.
Eine EXE wird weder beim Import noch zum Spielen benötigt. Mean Machines
akzeptiert auch die bytegleichen DAT-Dateien der bisher unterstützten Demo.
Im Hauptmenü F2 / „Import Original Data“ wählen und den Ordner mit
`MAIN.DAT` und den Tischdateien auswählen. Der übergeordnete Spielordner mit
einem Unterordner `DAT` funktioniert ebenfalls.

```text
DAT/
  MAIN.DAT
  MEAN.DAT
  PIRATE.DAT
  SPACE.DAT
  DEMON.DAT
  MENU.DAT     optional für das Originalmenü
```

Einzelne Tische benötigen jeweils ihre DAT und MAIN.DAT beim Import.
Der Import prüft die Versionen
und Dateiintegrität. Amiga-Daten sind derzeit keine unterstützte Spielgrundlage.

## Wie der Port ohne EXE läuft

Die DAT-Dateien enthalten Grafiken, Musik, Tisch- und Kollisionsdaten. Weitere
vom Original verwendete Daten liegen in dessen EXE. Der Port erzeugt diese
jetzt selbst: mathematische Lookup-Tabellen aus Formeln, native Lampen- und
Sound-Deskriptoren, Tischparameter und Callback-Verzeichnisse. Die Grafiken,
Fonts, Musik, Samples und Tisch-/Kollisionsdaten kommen aus deinen DAT-Dateien.
Wine oder ein Windows-Emulator sind nicht nötig.

Die 56.232 Bytes der gemeinsamen Mathematiktabellen stimmen vollständig mit
der Referenz überein. Native Parameter und Callback-Verzeichnisse ersetzen
die früher aus der EXE gelesenen Daten. Die Spielroutinen laufen als bereits
kompilierter nativer Code. Es wird kein verpacktes EXE-Abbild mitgeliefert.

**Ein frischer Import funktioniert ausschließlich aus DAT-Dateien.** Das ist
in einer isolierten Umgebung ohne EXE, Projektordner oder vorbereitete Caches
für alle vier Tische geprüft. Die importierten Daten bleiben erforderlich.

Bestehende importierte Daten bleiben nutzbar. Der ausdrückliche alte EXE-Import
steht als Kompatibilitätsweg weiterhin zur Verfügung. Das Programmpaket enthält
keine Original-Grafik-, Audio- oder Spieldateien.

[DAT-only-Import- und Gameplay-Nachweis](../analysis/traces/dat-only-import.json)
