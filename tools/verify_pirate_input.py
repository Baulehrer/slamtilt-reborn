#!/usr/bin/env python3
"""Bounded original Pirate Shift ABI/effects plus legal-input 1000-step trace.

Uses existing original F1-created snapshots; never changes those snapshots.
Original runtime data remains under build/. No gameplay services are stubbed.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_ESP, UC_X86_REG_EIP

ROOT = Path(__file__).resolve().parents[1]
BUILD = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
OBJ, DAT, STACK, STOP = 0x1000000, 0x1100000, 0x200f000, 0x2100000
INPUTS = [
    {'tick': 200, 'action': 'launch', 'down': True, 'scancode': 0x1c},
    {'tick': 201, 'action': 'launch', 'down': False, 'scancode': 0x1c},
    {'tick': 400, 'action': 'left', 'down': True, 'scancode': 0x2a},
    {'tick': 440, 'action': 'left', 'down': False, 'scancode': 0x2a},
    {'tick': 600, 'action': 'right', 'down': True, 'scancode': 0x36},
    {'tick': 640, 'action': 'right', 'down': False, 'scancode': 0x36},
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Oracle:
    def __init__(self, image, runtime, dat, keymap=True):
        self.u = Uc(UC_ARCH_X86, UC_MODE_32)
        for a, n in [(0x400000, 0x100000), (OBJ, 0x400000),
                     (0x2000000, 0x10000), (STOP, 0x1000)]:
            self.u.mem_map(a, n)
        self.u.mem_write(0x400000, image)
        self.u.mem_write(OBJ, runtime)
        self.u.mem_write(DAT, dat)
        if keymap:
            # Original keymap0 assignments at40df1e..40df3d.
            self.put(0x46c5dc, 0x2a)
            self.put(0x46c5e0, 0x36)
        self.calls = []
        for address in (0x434268, 0x434340, 0x434418, 0x406600):
            self.u.hook_add(UC_HOOK_CODE, self.called, begin=address, end=address)

    def called(self, u, address, size, context):
        self.calls.append({'address': hex(address),
                           'eax': u.reg_read(UC_X86_REG_EAX)})

    def put(self, address, value):
        self.u.mem_write(address, struct.pack('<I', value & 0xffffffff))

    def get(self, address):
        return struct.unpack('<I', self.u.mem_read(address, 4))[0]

    def run(self, address, eax=0, edx=0):
        self.put(STACK, STOP)
        self.u.reg_write(UC_X86_REG_ESP, STACK)
        self.u.reg_write(UC_X86_REG_EAX, eax & 0xffffffff)
        self.u.reg_write(UC_X86_REG_EDX, edx)
        self.u.emu_start(address, STOP, count=500000)
        assert self.u.reg_read(UC_X86_REG_EIP) == STOP, hex(address)
        assert self.u.reg_read(UC_X86_REG_ESP) == STACK + 4, hex(address)

    def direct(self, action, down):
        # Explicit native action adapter, bounded to unpaused gameplay.
        assert action in ('left', 'right')
        bit = 1 if action == 'left' else 2
        edge = 1 if down else -1
        if down and (not self.get(0x46c6ac) or self.get(0x46b764)):
            return
        flags = self.get(0x46c610)
        self.put(0x46c610, (flags | bit) if down else (flags & ~bit))
        self.run(0x434268 if action == 'left' else 0x434340, edge)
        self.put(0x46c6d0 if action == 'left' else 0x46c6d4, -1 if down else 0)
        if not down or not self.get(0x46c6c0):
            self.put(0x454b58 if action == 'left' else 0x454b5c, edge)
            upper_side = struct.unpack('<h', self.u.mem_read(0x465954, 2))[0]
            if (action == 'left' and upper_side == -1) or (action == 'right' and upper_side == 1):
                self.put(0x454b60, edge)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--human', type=Path, default=ROOT / 'build/oracle/pirate-human')
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/oracle/pirate-input')
    parser.add_argument('--report', type=Path, default=ROOT / 'analysis/pirate-input.json')
    args = parser.parse_args()
    assert args.steps >= 641
    out = args.output.resolve()
    assert out.is_relative_to(ROOT / 'build'), 'Original snapshots must stay under build/'
    image = (args.human / 'human-image.bin').read_bytes()
    runtime = (args.human / 'human-runtime.bin').read_bytes()
    dat = (args.human / 'human-dat.bin').read_bytes()
    provenance = json.loads((args.human / 'trace.json').read_text())
    assert provenance['build_sha256'] == BUILD
    for name, value in [('human-image.bin', image), ('human-runtime.bin', runtime),
                        ('human-dat.bin', dat)]:
        assert digest(value) == provenance['context_hashes'][name]
    report = {
        'schema': 1, 'build_sha256': BUILD, 'dat_sha256': provenance['dat_sha256'],
        'status': 'VERIFIED bounded original keyboard/actions/pose and legal-input trajectory',
        'keyboard': {'entry': '0x40404c', 'abi': 'EAX0 down / EAX1 up; EDX configured scan code',
                     'keymap0': '40df1e..40df3d: [46c5dc]=2a left Shift, [46c5e0]=36 right Shift',
                     'press_guards': '46c6ac!=0 AND46b764==0; tests start unpaused46c720==0',
                     'release_guards': 'Key-up branches have no equivalent gameplay/inhibit press guard'},
        'callbacks': {'directory': 'returned465958 -> +4 -> +8 ->46e4c4',
                      'left': {'slot': '+44', 'target': '0x434268'},
                      'right': {'slot': '+48', 'target': '0x434340'},
                      'abi': 'EAX+1 press / -1 release; callback precedes edge writes',
                      'common_press_effect': '406600 queues descriptor464f60(left)/464f84(right), EDX2 EBX1',
                      'field44_path': '46c6c0 nonzero: left press46e294=-1/right+1; matching-side release clears to0',
                      'field542_path': 'WORD46e542 nonzero: press writes WORD465864(left)/465858(right)=2 and bytes46e458(left)/46e45c(right)=[4,2,1,0]; release WORD=0 and first byte=2',
                      'mode6': 'When46c6ac==6 press calls434418; active434418 secondary path not asserted here'},
        'engine_edges': {'left': '454b58', 'right': '454b5c', 'upper': '454b60',
                         'upper_side': 'graphics WORD+1c: +1 right (Pirate), -1 left, 0 absent',
                         'values': '+1 press, -1 release, 0 unchanged;409154 consumes and clears',
                         'press_inhibit': '46c6c0!=0 suppresses physical press edges after callback; release still writes-1'},
        'key_side_effects': '46c610 byte sidebits1left/2right; timers46c6d0(left)/d4(right)=-1down,0up',
        'bounded_cases': [], 'inputs': INPUTS,
        'scope': 'Original instructions execute without gameplay stubs. Synthetic callback flag cases are distinct from the original F1-created legal-input replay. Pause/menu dispatch and active434418 secondary events excluded.',
    }
    # Synthetic but actual original instructions: compare every static/runtime
    # byte against the explicit action adapter after each keyboard event.
    for scenario, changes in [
        ('normal', []), ('field542', [(0x46e542, 1)]),
        ('field44', [(0x46c6c0, 1)]),
        ('blocked', [(0x46b764, 1)]), ('inactive', [(0x46c6ac, 0)]),
        ('mode6_helper_inactive', [(0x46c6ac, 6), (0x465974, 0)]),
    ]:
        for side, scan in [('left', 0x2a), ('right', 0x36)]:
            full = Oracle(image, runtime, dat)
            direct = Oracle(image, runtime, dat)
            for address, value in changes:
                full.put(address, value)
                direct.put(address, value)
            for down in (True, False):
                full.run(0x40404c, 0 if down else 1, scan)
                direct.direct(side, down)
                assert bytes(full.u.mem_read(0x400000, 0x100000)) == bytes(direct.u.mem_read(0x400000, 0x100000)), (scenario, side, down, 'image')
                assert bytes(full.u.mem_read(OBJ, 0x10000)) == bytes(direct.u.mem_read(OBJ, 0x10000)), (scenario, side, down, 'runtime')
                report['bounded_cases'].append({'scenario': scenario, 'side': side, 'down': down,
                                                'calls': full.calls[:], 'edges': [full.get(a) for a in (0x454b58, 0x454b5c, 0x454b60)],
                                                'static_and_runtime_bytes_equal': True})
                full.calls.clear()
    full, direct = Oracle(image, runtime, dat), Oracle(image, runtime, dat)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'image.bin').write_bytes(full.u.mem_read(0x400000, 0x100000))
    (out / 'runtime.bin').write_bytes(runtime)
    states = [list(full.u.mem_read(OBJ, 100))]
    actual_inputs = [event for event in INPUTS if event['tick'] < args.steps]
    for tick in range(args.steps):
        for event in actual_inputs:
            if event['tick'] != tick:
                continue
            full.run(0x40404c, 0 if event['down'] else 1, event['scancode'])
            if event['action'] == 'launch':
                direct.run(0x40404c, 0 if event['down'] else 1, event['scancode'])
            else:
                direct.direct(event['action'], event['down'])
        for oracle in (full, direct):
            oracle.run(0x409154)
            assert [oracle.get(a) for a in (0x454b58, 0x454b5c, 0x454b60)] == [0, 0, 0]
            oracle.run(0x40950c)
        state = list(full.u.mem_read(OBJ, 100))
        assert state == list(direct.u.mem_read(OBJ, 100)), tick
        states.append(state)
    trace = {'schema': 1, 'build_sha256': BUILD, 'dat_sha256': provenance['dat_sha256'],
             'tick_count': args.steps, 'inputs': actual_inputs, 'initial_state': states[0],
             'final_state': states[-1], 'states': states,
             'all_ball_bytes_equal_original_keyboard_and_direct_actions': True,
             'state_sha256': digest(bytes(v for state in states for v in state)),
             'initial_image_sha256': digest((out / 'image.bin').read_bytes()),
             'source_context_hashes': provenance['context_hashes'], 'gameplay_stubs': []}
    (out / 'trace.json').write_text(json.dumps(trace, separators=(',', ':')) + '\n')
    report['trajectory'] = {key: value for key, value in trace.items() if key not in ('initial_state', 'final_state', 'states', 'inputs')}
    report['trajectory']['trace'] = str((out / 'trace.json').relative_to(ROOT))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS', len(report['bounded_cases']), 'original edge contexts;', args.steps,
          'original keyboard/direct action steps, all100 ball bytes equal; no gameplay stubs')


if __name__ == '__main__':
    main()
