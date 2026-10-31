#!/usr/bin/env python3
"""Watch three unresolved Mean SFX descriptors in original Demo mode callbacks.

Executes the existing bounded mode-audio cases with synthetic states and adapted
services. This tests only those component paths; it cannot prove unreachability.
"""
import argparse
import hashlib
import json
import runpy
from pathlib import Path

import pefile
import unicorn
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EIP
from verify_mean_sample_pcm_original import DEMO_SHA

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (0x437f54, 0x437f78, 0x437f9c)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    builds = json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds']
    exe = (ROOT/next(x['path'] for x in builds if x['sha256'] == DEMO_SHA)).read_bytes()
    assert digest(exe) == DEMO_SHA
    image = (ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
    original = pefile.PE(data=exe).get_memory_mapped_image()
    factory, write_text = unicorn.Uc, Path.write_text
    machines, accesses, positive, calls, blocks = [], [], [], [], set()
    fixture = ROOT/'analysis/traces/mean-mode-audio-original.json'

    def create(*args, **kwargs):
        u = factory(*args, **kwargs)
        machines.append(u)
        def watch(machine, kind, address, size, value, _):
            accesses.append({'pc': hex(machine.reg_read(UC_X86_REG_EIP)), 'address': hex(address), 'size': size, 'kind': kind})
        def control(machine, kind, address, size, value, _):
            positive.append(address)
        def service(machine, addr, size, _):
            calls.append({'pc':hex(addr), 'eax':machine.reg_read(UC_X86_REG_EAX)})
        def block(machine, addr, size, _):
            if 0x401000 <= addr < 0x429000:
                blocks.add((addr,size))
        u.hook_add(unicorn.UC_HOOK_MEM_READ | unicorn.UC_HOOK_MEM_WRITE, watch, begin=TARGETS[0], end=TARGETS[-1]+35)
        u.hook_add(unicorn.UC_HOOK_MEM_READ, control, begin=0x43f1e6, end=0x43f1e7)
        u.hook_add(unicorn.UC_HOOK_CODE, service, begin=0x200ff00, end=0x200ff10)
        u.hook_add(unicorn.UC_HOOK_BLOCK, block)
        return u

    def suppress_fixture(self, data, *args, **kwargs):
        if self == fixture:
            return len(data)
        return write_text(self, data, *args, **kwargs)

    try:
        unicorn.Uc = create
        Path.write_text = suppress_fixture
        namespace = runpy.run_path(str(ROOT/'tools/verify_mean_mode_audio.py'), run_name='__main__')
    finally:
        unicorn.Uc = factory
        Path.write_text = write_text
    assert len(machines) == len(namespace['results']) == 12
    assert positive and calls
    assert not accesses
    for addr, size in blocks:
        off = addr - 0x400000
        assert image[off:off+size] == original[off:off+size], hex(addr)
    result = {'status':'BOUNDED_NO_TARGET_ACCESSES', 'scope':__doc__, 'demo_sha256':DEMO_SHA,
              'prepared_image_sha256':digest(image), 'cases':len(machines),
              'targets':[hex(x) for x in TARGETS], 'target_accesses':accesses,
              'positive_control_reads':len(positive), 'adapted_service_calls':len(calls),
              'executed_original_blocks':len(blocks), 'mode_cases':namespace['results']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:', len(machines), 'original mode callback cases;', len(calls), 'adapted services; no target accesses')


if __name__ == '__main__':
    main()
