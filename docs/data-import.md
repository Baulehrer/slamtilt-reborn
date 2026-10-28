# Originaldaten für Slamtilt - Reborn

Ab RC2 reicht die unterstützte **Windows-Retail-Version für alle vier Tische**.
Mean Machines unterstützt zusätzlich weiterhin die bisherige Windows-Demo.
Im Hauptmenü F2 / „Import Original Data“ wählen und den Ordner mit
`SLAMTILT.EXE` und dem Unterordner `DAT` auswählen.

```text
SLAMTILT.EXE
DAT/
  MAIN.DAT
  MEAN.DAT
  PIRATE.DAT
  SPACE.DAT
  DEMON.DAT
  MENU.DAT     optional für das Originalmenü
```

Einzelne Tische benötigen jeweils ihre DAT, MAIN.DAT und die passende EXE beim
Import. Für den zusätzlichen Demo-Import von Mean stammen EXE, MEAN.DAT und
MAIN.DAT gemeinsam aus der unterstützten Demo. Der Import prüft die Versionen
und Dateiintegrität. Amiga-Daten sind derzeit keine unterstützte Spielgrundlage.

## Warum die EXE noch gebraucht wird

Die DAT-Dateien enthalten Grafiken, Musik, Tisch- und Kollisionsdaten. Weitere
vom Port noch verwendete Originaldaten liegen in der EXE: mathematische
Lookup-Tabellen, Deskriptoren und Pointer für Engine- und Tischdaten.
Der native Importer extrahiert daraus private Datendateien und richtet den
belegten Anfangszustand ein. Die Windows-EXE wird dabei nicht ausgeführt;
Wine oder ein Windows-Emulator sind nicht nötig.

Für Mean Retail werden 60.640 Datenbytes aus sechs Bereichen übernommen und
124 Pointer auf das Datenlayout der nativen Mean-Engine umgesetzt. Darunter
liegen zwei kleine Maskentabellen im Codeabschnitt der EXE; sie werden als
Daten gelesen. Die Spielroutinen laufen als bereits kompilierter nativer Code.

**Nach erfolgreichem Import wird die Original-EXE zum Spielen nicht mehr
benötigt.** Das ist mit verborgenem Demo-Ordner und nachträglich unlesbaren
Original-EXEs getestet. Die importierten Daten bleiben erforderlich.

Ein reiner DAT-Import wäre möglich, wenn die noch benötigten EXE-Daten im Port
unabhängig erzeugt oder ersetzt werden. Das ist derzeit noch nicht vollständig
umgesetzt. Das Programmpaket enthält keine Originalassets.

[Import- und Gameplay-Nachweis](../analysis/traces/mean-retail-import.json)
