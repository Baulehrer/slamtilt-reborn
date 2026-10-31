#!/usr/bin/env python3
"""Rewrap the original demo MEAN.DAT tracker banks for libxmp. No synthesized events."""
import argparse, hashlib, json, struct
from pathlib import Path

BANK_OFFSETS = (0x5c2d2, 0x61590)  # Original 40f0e3/40f0f5 DAT relocation.
def extract(data, bank, offsets=BANK_OFFSETS):
    base = offsets[bank]
    nos, length, patterns = struct.unpack_from('>HHH', data, base + 4)
    if not (nos == 31 and 0 < length <= 128 and 0 < patterns <= 64):
        raise ValueError('Unsupported MEAN.DAT revision/header')
    if any(x >= patterns for x in data[base+10:base+10+length]):
        raise ValueError('Invalid order pattern index')
    end = base + 394
    for i in range(patterns):
        pattern = base + struct.unpack_from('>I', data, base+138+i*4)[0]
        cursor = pattern + 8
        for channel in range(4):
            relative = struct.unpack_from('>H', data, pattern+channel*2)[0]
            if pattern + relative != cursor:
                raise ValueError('Noncontiguous pattern channels: cannot use libxmp STIM decoder')
            row = 0
            while row < 64:
                first = data[cursor]; cursor += 1
                if first & 128:
                    row += (first & 127) + 1
                else:
                    cursor += 2; row += 1
            if row != 64:
                raise ValueError('Invalid pattern skip')
        end = max(end, cursor)
    samples = bytearray(nos*4)
    descriptors = []
    for i in range(nos):
        sample = struct.unpack_from('>I', data, i*4)[0]
        size = struct.unpack_from('>H', data, sample)[0]*2
        payload = data[sample:sample+8+size]
        if len(payload) != 8+size:
            raise ValueError('Truncated original sample')
        struct.pack_into('>I', samples, i*4, len(samples))
        descriptors.append({'index':i+1,'dat_offset':sample,'pcm_bytes':size})
        samples.extend(payload)
    module = data[base:end]
    sample_address = 12 + len(module)
    result = b'STIM' + struct.pack('>II', sample_address, 0) + module + samples
    return result, {'bank':bank,'dat_offset':base,'orders':length,'patterns':patterns,
                    'samples':descriptors,'module_end':end,'sha256':hashlib.sha256(result).hexdigest()}

def main():
    p=argparse.ArgumentParser();p.add_argument('dat',type=Path);p.add_argument('--out-dir',type=Path,default=Path('build/mean-audio'));a=p.parse_args()
    data=a.dat.read_bytes();a.out_dir.mkdir(parents=True,exist_ok=True);records=[]
    for bank in range(2):
        module, record=extract(data,bank);target=a.out_dir/f'mean-bank-{bank}.stim';target.write_bytes(module);record['path']=str(target);records.append(record)
    report={'source_sha256':hashlib.sha256(data).hexdigest(),'banks':records}
    (a.out_dir/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'source_sha256':report['source_sha256'],'banks':[{k:v for k,v in r.items() if k!='samples'} for r in records]}))
if __name__=='__main__':main()
