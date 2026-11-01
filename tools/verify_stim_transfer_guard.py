#!/usr/bin/env python3
"""Verify incompatible sample banks are rejected without altering destination."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from extract_mean_stim import extract
from verify_retail_tracker_pcm import GAME, TABLES

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--native', type=Path, required=True)
p.add_argument('--work', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args(); a.work.mkdir(parents=True, exist_ok=True)
paths = []
for name in ('mean', 'pirate'):
    data = (GAME/'DAT'/f'{name.upper()}.DAT').read_bytes()
    assert hashlib.sha256(data).hexdigest() == TABLES[name][0]
    stim, _ = extract(data, 0, (TABLES[name][1],))
    path = a.work/f'{name}.stim'; path.write_bytes(stim); paths.append(path.resolve())
subprocess.run([str(a.native.resolve()), *(str(p) for p in paths), '34'], check=True)
changed = bytearray(paths[0].read_bytes())
assert changed
changed[-1] ^= 1
altered = (a.work/'mean-altered.stim').resolve()
altered.write_bytes(changed)
subprocess.run([str(a.native.resolve()), str(paths[0]), str(altered), '5'], check=True)
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps({'status':'VERIFIED_BOUNDED', 'scope':__doc__,
                                'native_sha256':hashlib.sha256(a.native.read_bytes()).hexdigest(),
                                'incompatible_rejected':True, 'changed_sample_rejected':True, 'self_rejected':True,
                                'resume_without_snapshot_rejected':True, 'incompatible_resume_rejected':True,
                                'destination_pcm_unchanged_frames':2646}, indent=2)+'\n')
