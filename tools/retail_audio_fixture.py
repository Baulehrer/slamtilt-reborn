"""Adapt only the synthetic startup event in retained Retail audio fixtures.

Historical fixture writers seeded [0, 0x90, 0, 0, 0] from uninitialized
snapshot globals. Original Retail initialization sets the table-specific order.
Never alter the fixture or normalize any later original event.
"""

ORIGINAL_START_ORDERS = {'pirate': 34, 'space': 32, 'demon': 25}


def corrected_audio_events(events, table):
    order = ORIGINAL_START_ORDERS[table]
    if events and events[0] == [0, 0x90, 0, 0, 0]:
        return [[0, 0x90, 0, order, 0], *events[1:]]
    return events
