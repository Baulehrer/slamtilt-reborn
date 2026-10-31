#!/usr/bin/env python3
"""Instrument the retained Original Demo minigame sound regression.

Runs the existing eight bounded Original/native scenarios with descriptor-read
and queue-entry hooks. State and score thresholds are synthetic, dispatcher
services are adapted and this does not establish complete-game reachability.
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
from verify_mean_sample_pcm_original import DEMO_SHA, DAT_SHA

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (0x437f54,0x437f78,0x437f9c)
CONTROLS = {0x437fe4,0x438008,0x43802c,0x438050}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    builds = json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds']
    exe = (ROOT/next(x['path'] for x in builds if x['sha256'] == DEMO_SHA)).read_bytes()
    dat = next((ROOT/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')).read_bytes()
    assert sha(exe) == DEMO_SHA and sha(dat) == DAT_SHA
    pe = pefile.PE(data=exe)
    expected_image = pe.get_memory_mapped_image()
    original_factory = unicorn.Uc
    machines, target_access, control_access, calls, blocks = [], [], [], [], set()

    def create(*factory_args, **factory_kwargs):
        uc = original_factory(*factory_args, **factory_kwargs)
        machines.append(uc)
        def watch(u,kind,address,size,_value,_):
            target_access.append({'pc':hex(u.reg_read(UC_X86_REG_EIP)),
                                  'address':hex(address),'size':size,'access':kind})
        def watch_control(_u,_kind,address,_size,_value,_):
            control_access.append(address)
        def queue(u,_address,_size,_):
            calls.append(u.reg_read(UC_X86_REG_EAX))
        def block(_u,address,size,_):
            if 0x401000 <= address < 0x429000:
                blocks.add((address,size))
        uc.hook_add(unicorn.UC_HOOK_MEM_READ|unicorn.UC_HOOK_MEM_WRITE,watch,
                    begin=TARGETS[0],end=TARGETS[-1]+35)
        uc.hook_add(unicorn.UC_HOOK_MEM_READ|unicorn.UC_HOOK_MEM_WRITE,watch_control,
                    begin=0x43f034,end=0x43f037)
        uc.hook_add(unicorn.UC_HOOK_CODE,queue,begin=0x405c60,end=0x405c60)
        uc.hook_add(unicorn.UC_HOOK_BLOCK,block)
        return uc
    unicorn.Uc = create
    original_argv = sys.argv
    sys.argv = [str(ROOT/'tools/verify_mean_minigame2.py'),str(args.native.resolve()),'--sounds']
    try:
        try:
            runpy.run_path(sys.argv[0],run_name='__main__')
        except SystemExit as e:
            if e.code not in (None,0): raise
    finally:
        unicorn.Uc = original_factory
        sys.argv = original_argv
    assert len(machines) == 1
    assert control_access and CONTROLS <= set(calls), 'instrumentation positive controls failed'
    assert not target_access and not (set(calls) & set(TARGETS)), target_access
    for address,size in blocks:
        offset = pe.get_offset_from_rva(address-0x400000)
        assert expected_image[address-0x400000:address-0x400000+size] == exe[offset:offset+size]
        assert bytes(machines[0].mem_read(address,size)) == exe[offset:offset+size]
    fixture = ROOT/'analysis/traces/mean-minigame-samples-original.json'
    data = json.loads(fixture.read_text())
    assert len(data['cases']) == 8
    report = {'status':'BOUNDED_NO_TARGET_ACCESSES','scope':__doc__,'demo_sha256':DEMO_SHA,
              'dat_sha256':DAT_SHA,'native_sha256':sha(args.native.read_bytes()),
              'source_fixture_sha256':sha(fixture.read_bytes()), 'cases':len(data['cases']),
              'targets':[hex(x) for x in TARGETS], 'target_accesses':target_access,
              'positive_control_memory_accesses':len(control_access),
              'control_descriptor_counts':{hex(x):calls.count(x) for x in sorted(CONTROLS)},
              'executed_original_blocks':len(blocks)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: eight original/native minigame cases; four queue controls observed, no target access')


if __name__ == '__main__':
    main()
