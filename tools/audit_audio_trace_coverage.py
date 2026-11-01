#!/usr/bin/env python3
"""Inventory audio request coincidences in retained Retail traces.

A same-step request is not proof of an audible overlap: actual channel lifetimes,
tracker phase and device cadence are not captured. This inventory covers only
the listed fixture formats and does not include every possible game state.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACES = ROOT / 'analysis/traces'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    tables = {}
    for table in ('pirate', 'space', 'demon'):
        paths = sorted(TRACES.glob(f'{table}-*-rewards.json'))
        events_file = TRACES / f'{table}-audio-events.json'
        if events_file.exists():
            paths.append(events_file)
        groups = []
        sources = []
        for path in paths:
            data = path.read_bytes()
            parsed = json.loads(data)
            sources.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(data).hexdigest()})
            if 'audio_events' in parsed:
                groups.append((parsed.get('case', path.stem), parsed['audio_events']))
            else:
                groups.extend((c.get('case', ''), c.get('events', [])) for c in parsed.get('cases', []))
        requests = collections.Counter()
        pairs = collections.Counter()
        same_step_music_sfx = 0
        for _, events in groups:
            steps = collections.defaultdict(list)
            for event in events:
                if not isinstance(event, list) or len(event) < 5:
                    raise ValueError('Unsupported event format')
                requests[hex(event[1])] += 1
                steps[event[0]].append(event)
            for rows in steps.values():
                sounds = [tuple(row[2:5]) for row in rows if row[1] == 0x5c]
                if len(sounds) > 1:
                    pairs[tuple(sounds)] += 1
                if sounds and any(row[1] in (0x80, 0x84, 0x88, 0x8c, 0x90) for row in rows):
                    same_step_music_sfx += 1
        tables[table] = {'fixtures': len(groups), 'sources': sources,
                         'requests_by_service': dict(sorted(requests.items())),
                         'same_step_sfx_groups': sum(pairs.values()),
                         'distinct_ordered_sfx_groups': len(pairs),
                         'same_step_sfx_and_music_requests': same_step_music_sfx}
    tables['mean'] = {'status': 'PARTIAL', 'reason': 'Retained Mean natural gameplay audio summaries do not contain comparable complete original service-entry event streams.',
                      'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                                  for p in (TRACES / 'mean-audio-gameplay.json', TRACES / 'mean-mode-audio-original.json', TRACES / 'mean-display-audio-original.json')]}
    result = {'scope': __doc__, 'tables': tables}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    for table, data in tables.items():
        print(table, data.get('fixtures', data.get('status')), data.get('same_step_sfx_groups', 'unknown'))


if __name__ == '__main__':
    main()
