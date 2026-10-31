#!/usr/bin/env python3
"""Index retained table contracts without treating historical claims as fresh proof."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = {
    'mean': 'analysis/mean-completion.json',
    'pirate': 'analysis/pirate-completion-contract.json',
    'space': 'analysis/space-completion-contract.json',
    'demon': 'analysis/demon-completion-contract.json',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'build/gameplay-verification/coverage-inventory.json')
    args = parser.parse_args()
    result = {
        'schema_version': 1,
        'reference': 'Windows Retail, with Mean Demo evidence explicitly identified where used',
        'status': 'INVENTORY_ONLY',
        'complete_original_equivalence': False,
        'scope': 'Source-contract statuses are historical assertions, not fresh test results; file presence is not proof.',
        'tables': {},
    }
    for table, relative in CONTRACTS.items():
        path = ROOT/relative
        contract = json.loads(path.read_text())
        entries = contract.get('features', contract.get('rules'))
        if not isinstance(entries, list) or not entries:
            raise ValueError(f'No feature/rule list in {relative}')
        rows = []
        for index, entry in enumerate(entries):
            evidence = entry.get('evidence', [])
            if not isinstance(evidence, list):
                raise ValueError(f'Unsupported evidence field in {relative} entry {index}')
            refs = []
            for name in evidence:
                if not isinstance(name, str):
                    raise ValueError(f'Unsupported evidence reference in {relative} entry {index}')
                candidate = Path(name)
                # References are listed as reported; existence does not validate a claim.
                local = not candidate.is_absolute() and '..' not in candidate.parts
                refs.append({'path': name, 'file_present': local and (ROOT/candidate).is_file()})
            rows.append({
                'id': entry.get('id', entry.get('feature', f'entry-{index}')),
                'claim': entry.get('claim', entry.get('feature', '')),
                'reported_status': entry.get('status', entry.get('confidence', 'UNKNOWN')),
                'reported_scope': entry.get('scope', entry.get('verified_scope', '')),
                'reported_gaps': entry.get('gaps', entry.get('remaining', [])),
                'fixtures': entry.get('fixtures', []),
                'evidence': refs,
            })
        result['tables'][table] = {
            'contract': relative, 'contract_sha256': sha(path), 'entries': rows,
            'reported_status_counts': dict(collections.Counter(row['reported_status'] for row in rows)),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({table: len(value['entries']) for table, value in result['tables'].items()}))


if __name__ == '__main__':
    main()
