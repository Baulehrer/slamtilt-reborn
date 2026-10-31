#!/usr/bin/env python3
"""The legacy adapter must never change an observed non-startup event."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from retail_audio_fixture import corrected_audio_events

for table, order in [('pirate', 34), ('space', 32), ('demon', 25)]:
    retained = [[0, 144, 0, 0, 0], [123, 144, 0, 0, 0], [124, 92, 6, 5, 42]]
    expected = [[0, 144, 0, order, 0], *retained[1:]]
    assert corrected_audio_events(retained, table) == expected
    assert retained[0] == [0, 144, 0, 0, 0]
    assert corrected_audio_events(expected, table) == expected
    wrong_tick = [[1, 144, 0, 0, 0]]
    assert corrected_audio_events(wrong_tick, table) == wrong_tick
    assert corrected_audio_events([], table) == []
print('Retail legacy audio startup adapter: all tables and unchanged later events pass')
