#!/usr/bin/env python3
"""Watch Mean Demo SFX descriptors in bounded original contact replays.

Inputs are retained native legal-input contact snapshots replayed through
original collision code; audio/display/score services are adapted. This is
component evidence, not an original whole-game trajectory or reachability proof.
"""
import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path

import pefile
import unicorn
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EIP
from verify_mean_sample_pcm_original import DEMO_SHA

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (0x437f54, 0x437f78, 0x437f9c)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probe', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    builds = json.loads((ROOT / 'analysis/windows-symbol-map.json').read_text())['builds']
    exe = (ROOT / next(x['path'] for x in builds if x['sha256'] == DEMO_SHA)).read_bytes()
    assert sha(exe) == DEMO_SHA
    pe = pefile.PE(data=exe)
    original = pe.get_memory_mapped_image()
    image = (ROOT / 'build/mean-prepared/pe-data.bin').read_bytes()
    original_factory = unicorn.Uc
    machines, accesses, control, queue, blocks = [], [], [], [], set()

    def create(*args, **kwargs):
        uc = original_factory(*args, **kwargs)
        machines.append(uc)

        def watch(machine, kind, address, size, value, _):
            accesses.append({'pc': hex(machine.reg_read(UC_X86_REG_EIP)), 'address': hex(address), 'size': size, 'kind': kind})

        def positive(machine, kind, address, size, value, _):
            control.append(1)

        def audio(machine, address, size, _):
            queue.append(machine.reg_read(UC_X86_REG_EAX))

        def block(machine, address, size, _):
            if 0x401000 <= address < 0x429000:
                blocks.add((address, size))

        uc.hook_add(unicorn.UC_HOOK_MEM_READ | unicorn.UC_HOOK_MEM_WRITE, watch, begin=TARGETS[0], end=TARGETS[-1]+35)
        uc.hook_add(unicorn.UC_HOOK_MEM_READ, positive, begin=0x43f068, end=0x43f06b)
        uc.hook_add(unicorn.UC_HOOK_CODE, audio, begin=0x2101010, end=0x2101010)
        uc.hook_add(unicorn.UC_HOOK_BLOCK, block)
        return uc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    contact_report = args.output.with_name(args.output.stem + '-contacts.json')
    contexts = args.output.with_name(args.output.stem + '-contexts.json')
    original_argv = sys.argv
    try:
        unicorn.Uc = create
        sys.argv = ['verify_mean_live_contacts.py', '--probe', str(args.probe), '--contexts', str(contexts), '--output', str(contact_report)]
        runpy.run_path(str(ROOT / 'tools/verify_mean_live_contacts.py'), run_name='__main__')
    finally:
        unicorn.Uc = original_factory
        sys.argv = original_argv
    report = json.loads(contact_report.read_text())
    assert report['status'] == 'VERIFIED' and control and queue
    assert len(machines) == 1 and not accesses
    for address, size in blocks:
        off = address - pe.OPTIONAL_HEADER.ImageBase
        assert image[off:off+size] == original[off:off+size], hex(address)
    result = {'status': 'BOUNDED_NO_TARGET_ACCESSES', 'scope': __doc__,
              'demo_sha256': DEMO_SHA, 'prepared_image_sha256': sha(image),
              'dat_sha256': report['dat_sha256'], 'routes_sha256': report['route_sha256'],
              'contact_fixture_sha256': sha(contexts.read_bytes()),
              'retained_contacts': report['retained'], 'observed_native_contacts': report['observed'],
              'full_response_separation': report['full_response_separation'],
              'targets': [hex(x) for x in TARGETS], 'target_accesses': accesses,
              'positive_control_memory_reads': len(control), 'adapted_audio_calls': len(queue),
              'adapted_audio_eax_counts': {hex(x): queue.count(x) for x in sorted(set(queue))},
              'executed_original_blocks': len(blocks)}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS:', report['retained'], 'original contact snapshots;', len(queue), 'adapted audio calls; no descriptor accesses')


if __name__ == '__main__':
    main()
