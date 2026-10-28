# Reborn-Spielprüfung

Zwölf neue legale Eingabesitzungen ergeben 272.000 beschleunigte Sitzungsticks:
je Tisch 60.000 für die Hauptsitzung und zwei Varianten mit je4.000. Die
Eingaben enthalten keine diagnostischen Ballversetzungen, Regel-/Score-Edits
oder künstlichen RNG-/Timeränderungen.

Pirate, Space und Demon werden mit den vollständigen aufgezeichneten Original-
Zustandsvektoren und Audioanforderungen verglichen. Für Pirate wird die belegte
Benutzer-Tastenbelegung im Original ausdrücklich initialisiert; dessen gespeicherter
Ausgangszustand hatte leere Shift-Belegungen. Unterschiedliche Vorher-/Nachher-
Step-Bezeichnungen der Pirate-Audiozeitstempel werden vor dem exakten Vergleich
explizit in dieselbe Konvention überführt.

Mean wird vollständig nativ auf deterministische Zustände und Audioereignisse
geprüft. Separat bestehen22 Original-Komponentenfälle;14 Kontexte bleiben außerhalb
dieser Prüfung. Die Kamera ist über3.512 Original-Routinenkontexte abgesichert.
Damit wird keine vollständige Original-Trajektoriengleichheit für Mean behauptet.
Die Kamera hängt von der Präsentationskadenz ab und wird getrennt von den
Spielzuständen auf gültige Scrollgrenzen geprüft.

Die vier seriellen Echtzeitläufe verwenden die gleichen Hauptsitzungen mitje
60.000 logischen200Hz-Ticks, GPU, Vollbild und realem Audioausgabegerät.
Game-Over-Wartezeit und aktive Mean-Simulationsaufrufe werden getrennt ausgewiesen.
Die Messgrenzen bleiben unverändert: keine100ms-Clamps und ungefähr300Sekunden
Laufzeit. Fehlversuche werden nicht durch tolerantere Grenzen „repariert“.

Echte Fokusprüfungen verwenden einen temporären uinput-Tastatureingang und
vorhandene Compositor-Bindings auf einer eigenen temporären Arbeitsfläche.
Tasteneingaben erfolgen ausschließlich, wenn ein Testfenster aktiv ist; danach
wird die ursprüngliche Arbeitsfläche wiederhergestellt. Simulation, manuelle
Pause, Audiopause/-Fortsetzung und F10-Rückkehr werden in echten SDL-Ereignissen
geprüft. Frühe Wayland-only-Testversuche lösten die Desktop-Bindings nicht aus;
diese sind keine bestätigten Fehler des Spiels.

Die Ergebnisse sagen nichts über menschliche Flipper-Haptik, Lautsprecherklang,
alle möglichen Spielverläufe oder universelle Treiberkompatibilität aus.

Auf ausdrücklichen Benutzerwunsch läuft die abschließende Demon-Messung als
kontrollierter Hintergrund-Replay: synthetische Fokus-Gain-Ereignisse halten nur
diesen Benchmark aktiv. Seine Fokuswerte sind kein Beleg für reale Fensteraktivität.
Die echten Vollbild-/Alt-Tab-/Pause-/Audio-Prüfungen aller vier Tische wurden separat
mit Compositor-Ereignissen bestanden. Vorherige Fokusunterbrechungen und ein
Timing-Fehllauf bleiben in den Attempt-Berichten erhalten; Grenzen unverändert.

Abschluss: alle vier Hauptläufe bestehen mit je60.000Ticks und0Clamps. Demon:
300.008,67ms, exakte Originalvektoren/Audio, unverändertes Paketbinary. Ein nur für
QA vorgelagerter SDL-Aufruf-Probe meldet keinen Aufruf über50ms. Die große
Original-JSON wird im Prüfer erst nach der gemessenen Sitzung geladen. Frühere
Fehlläufe (zuletzt zwei Clamps) bleiben erhalten; daraus ist keine gesicherte
Ursache der früheren Zeitspitzen ableitbar. Der bestandene Lauf beseitigt diese
beobachtete Unsicherheit nicht. Sie ist im Release-Index ausdrücklich vermerkt.
