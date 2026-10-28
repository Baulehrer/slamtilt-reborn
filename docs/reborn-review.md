# Slamtilt - Reborn — Code-Review und Refactoring

Review-Grenze: gemeinsamer Launcher, Import, Kindprozesse, SDL-Lebensdauer,
Optionsmenü, Eingabe-/Audioübergänge, Testadapter und gemeinsame Distribution.
Generierter Gameplay-Code wird nur bei einer nachgewiesenen Lücke erweitert.

| Befund | Änderung | Beleg |
|---|---|---|
| P1: Mean-Import fing auch Schreib-/Lesefehler als „nicht unterstützt“ ab | Build-SHA vorab unterscheiden; echte Fehler weitergeben; Mehrtisch-Import bei Fehler vollständig zurückrollen | `main_menu_flow`, `reborn-menu-acceptance.json` |
| P1: Kindprozess startete vor dem Speichern; ein Fehler konnte die Kontrolle verlieren | Vor dem Start speichern; `ChildSession` besitzt Start, Poll, sanften Stopp und begrenzten Notabbruch | `frontend_runtime_safety`, ASan/UBSan |
| P1: Neue legale Demon-Route erreichte fehlenden DMD-Callback `0x410ea0` | Originalroutine gezielt übernommen: +41 Instruktionen, weiterhin fünf unveränderte externe Aufrufgrenzen | `reborn-demon-dmd-gap.json`, Original-/Native-Vergleiche |
| P2: Initialen-Modal verschluckte F10 | Sitzungs-Rückkehr vor Initialeneingabe behandeln | Review, `port_options`, reale F10-Rückkehr aller vier Tische |
| P2: Dialogende konnte die Anwendung blockieren | Callback-Daten besitzen ihre Lebensdauer unabhängig vom Fenster; kein Warteloop beim Schließen | statischer Lebensdauerreview; echte Portal-Abbruchinteraktion nicht behauptet |
| P2: Ungültige Menü-Konfiguration beendete den Launcher | Originaldatei gesichert erhalten, kontrolliert auf Standardwerte zurückfallen | `frontend_runtime_safety` |
| P2: Doppelte Aktivierung konnte zweiten Start bzw. falsche Rückkehr-Zuordnung erzeugen | Nach erfolgreichem Start Event-Verarbeitung beenden; Prozessbesitz zentralisieren | Vier-Tisch-Lifecycle, Review |
| P3: Programmpfad war Linux-procfs-spezifisch | `SDL_GetBasePath()`; bestehende Daten-/Präferenzpfade bleiben kompatibel | verschobenes Paket mit verborgenem Checkout |

Während der neuen Testadapter-Implementierung zusätzlich erkannt und behoben:
GameOver als normalen Sitzungszustand statt Enginefehler behandeln; aktive
Simulationsaufrufe und Warte-Ticks getrennt zählen; Initialenaufnahme respektieren;
Neustart einschließlich Audio über denselben Helfer wie die echte R-Taste führen;
vier exakte Steps pro beschleunigtem Replay-Frame; VSync dabei ausschalten;
Audioereignisse im Mean-Replay am Simulations-Step statt Renderframe erfassen.
Die normale Live-Spielsteuerung behält ihre bisherige Simulation.

Die anfängliche Pirate-Abweichung war ein Fehler der Vergleichsgrundlage:
Der gespeicherte Originalzustand enthielt keine Shift-Belegung. Nur die belegten
Benutzer-Eingabefelder wurden für den Vergleich konfiguriert. Die native Pirate-
Physik wurde deshalb nicht geändert. Die korrigierte Vergleichsrunde ist exakt.

Die neue Darstellung wurde zusätzlich auf Frame-Clear, Mauskoordinaten bei
minimierten Fenstern, optionales Einstellungsformat und SDL-Destruktionsreihenfolge
geprüft. Fehlerhafte erste Testversuche bleiben unter `build/reborn-*` erhalten.

Vollständige Original-Trajektoriengleichheit bleibt bei Mean **PARTIAL**; die
separaten Original-Komponenten- und Kameraprüfungen sind davon unabhängig.
Subjektives Spielgefühl, Lautsprecherklang und universelle GPU-Kompatibilität
werden nicht als automatisch verifiziert ausgegeben.
