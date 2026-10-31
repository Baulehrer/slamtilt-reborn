#!/usr/bin/env python3
"""Search bounded Mean descriptor interiors across pinned PE/DAT inputs.

Any byte hit is only a candidate, not proof of a pointer or code reference.
Absence cannot exclude runtime construction, indexing, relative addresses,
compression, other versions or original Amiga behavior.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile
from verify_mean_sample_pcm_original import DEMO_SHA
from verify_retail_tracker_pcm import EXE_SHA, GAME

ROOT = Path(__file__).resolve().parents[1]
DAT_SHA = {
    'DEMON.DAT':'0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d',
    'INTRO.DAT':'596017e94b52e8470d1efd199709f58e5dc6f507df77ae90834c008dd60f04bf',
    'MAIN.DAT':'e82addadc9b40b172615983034825ebf3e077c3ff3c167531520c50dd8c9188c',
    'MEAN.DAT':'1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f',
    'MENU.DAT':'eb46503d8a7b7b70366403ffc5a4d9075271bafa10a7efac3abc761dcb5990ee',
    'MENU2.DAT':'9fbfe3a48b41eec57405db8a7cd974bc7a6d7171c255ed7c61dc8d298197130f',
    'PIRATE.DAT':'6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6',
    'SPACE.DAT':'18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b',
}
FIX_SHA = '5054441d4966efc4cdf14edef6061bad9c8af70ea56ec7f772d69cdc16612667'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def hits(data, base):
    result = []
    # Every possible byte within three contiguous 36-byte descriptors, not
    # only aligned fields; scan every byte position in each input.
    for delta in range(3 * 36):
        value = base + delta
        needle = struct.pack('<I',value)
        at = 0
        while True:
            at = data.find(needle,at)
            if at < 0:
                break
            result.append({'value':hex(value),'offset':at})
            at += 1
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--fix', type=Path, help='Optional SHA-pinned Windows Fix executable')
    a = p.parse_args()
    builds = json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds']
    demo = (ROOT/next(x['path'] for x in builds if x['sha256'] == DEMO_SHA)).read_bytes()
    retail = (GAME/'SLAMTILT.EXE').read_bytes()
    assert sha(demo) == DEMO_SHA and sha(retail) == EXE_SHA
    variants = [('demo',demo,0x437f54),('retail',retail,0x464008)]
    if a.fix:
        fix = a.fix.read_bytes()
        assert sha(fix) == FIX_SHA
        retail_image = pefile.PE(data=retail).get_memory_mapped_image()
        fix_image = pefile.PE(data=fix).get_memory_mapped_image()
        # Same three original descriptor records, located at a different VA.
        for index in range(3):
            r, f = 0x464008 + index*36 - 0x400000, 0x46506c + index*36 - 0x400000
            assert retail_image[r:r+36] == fix_image[f:f+36]
        variants.append(('fix',fix,0x46506c))
    pe_results = []
    for name,binary,base in variants:
        mapped = pefile.PE(data=binary).get_memory_mapped_image()
        found = hits(mapped,base)
        assert not found, (name,found)
        pe_results.append({'build':name,'mapped_bytes':len(mapped),'descriptor_base':hex(base),
                           'address_values_scanned':108,'matches':found})
    dat_results = []
    mean = None
    for name, expected in DAT_SHA.items():
        data = (GAME/'DAT'/name).read_bytes()
        assert sha(data) == expected, name
        found = [{'address_space':label, **entry}
                 for label,_,base in variants
                 for entry in hits(data,base)]
        if name == 'MEAN.DAT': mean = data
        dat_results.append({'name':name,'sha256':expected,'size':len(data),'raw_matches':found})
    # One incidental little-endian byte sequence lies inside original sample26
    # PCM. This proves its location in audio data, not an executable reference.
    nonempty = [(r['name'],e) for r in dat_results for e in r['raw_matches']]
    assert nonempty == [('MEAN.DAT',{'address_space':'retail','value':'0x464032','offset':0x409a0})]
    header = struct.unpack_from('>I',mean,(26-1)*4)[0]
    length = struct.unpack_from('>H',mean,header)[0]*2
    assert (header,length) == (0x3e47c,38494)
    assert header+8 <= 0x409a0 and 0x409a0+4 <= header+8+length
    report = {'status':'VERIFIED_BOUNDED','scope':__doc__,
              'demo_sha256':DEMO_SHA,'retail_sha256':EXE_SHA,
              'fix_sha256':FIX_SHA if a.fix else None,
              'pe_results':pe_results,'dat_results':dat_results,
              'single_dat_match_location':{'sample_id':26,'sample_data_offset':hex(header+8),
                  'sample_data_length':length,'raw_match_offset':'0x409a0',
                  'classification':'bytes within sample PCM, not established as a pointer'}}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: descriptor interiors absent from {len(variants)} PE images; one DAT hit lies in sample26 PCM')


if __name__ == '__main__':
    main()
