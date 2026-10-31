#!/usr/bin/env python3
"""Inventory direct pointer bytes for the three unobserved Mean descriptors.

This is a bounded static negative search of two authenticated PE images. It
cannot exclude computed/indexed pointers, runtime patches, addresses encoded
as offsets, indirect references, unvisited events or differing Amiga logic.
"""
import argparse
import hashlib
import json
from pathlib import Path

import pefile
from verify_mean_sample_pcm_original import DEMO_SHA
from verify_retail_tracker_pcm import EXE_SHA, GAME

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ((0x437f54,0x464008), (0x437f78,0x46402c), (0x437f9c,0x464050))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    builds = json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds']
    demo = (ROOT/next(x['path'] for x in builds if x['sha256'] == DEMO_SHA)).read_bytes()
    retail = (GAME/'SLAMTILT.EXE').read_bytes()
    assert digest(demo) == DEMO_SHA and digest(retail) == EXE_SHA
    rows = []
    for label, binary, index in (('demo',demo,0),('retail',retail,1)):
        mapped = pefile.PE(data=binary).get_memory_mapped_image()
        for pair in PAIRS:
            address = pair[index]
            needle = address.to_bytes(4,'little')
            matches = []
            at = 0
            while True:
                at = mapped.find(needle,at)
                if at < 0: break
                matches.append(hex(0x400000+at))
                at += 1
            assert not matches, (label,hex(address),matches)
            rows.append({'build':label,'descriptor':hex(address),
                         'mapped_pe_bytes_scanned':len(mapped),'direct_pointer_matches':matches})
    report = {'status':'BOUNDED_NO_LITERAL_REFERENCES', 'scope':__doc__,
              'demo_sha256':DEMO_SHA, 'retail_sha256':EXE_SHA, 'cases':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: no direct pointer bytes for three descriptors in either pinned PE image')


if __name__ == '__main__':
    main()
