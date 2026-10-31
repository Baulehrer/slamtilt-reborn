#!/usr/bin/env python3
"""Inventory pinned Retail descriptors against compiled native sample profiles.

This is bounded to the listed descriptor directories and retained event traces;
literal presence, PCM equality or an unobserved event do not prove reachability.
No original PCM is written to the report.
"""
import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT_HASHES = {'mean':'1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f',
              'pirate':'6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6',
              'space':'18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b',
              'demon':'0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--mean-sequences', type=Path)
    p.add_argument('--mean-minigame', type=Path,
                   help='Optional bounded Original Demo minigame request fixture')
    p.add_argument('--amiga-mean', type=Path,
                   help='Optional imported Amiga adapter DAT; compare native profile slices')
    p.add_argument('--demon-callback', type=Path)
    p.add_argument('--retail-coverage', type=Path)
    p.add_argument('--pirate-coverage', type=Path)
    a = p.parse_args()
    exe = (GAME/'SLAMTILT.EXE').read_bytes()
    assert sha(exe) == SHA
    image = pefile.PE(data=exe).get_memory_mapped_image()
    profiles = json.loads(subprocess.check_output([str(a.native.resolve())]))
    callback = json.loads(a.demon_callback.read_text()) if a.demon_callback else None
    if callback:
        assert callback['status'] == 'VERIFIED_BOUNDED' and callback['exe_sha256'] == SHA
        assert callback['dat_sha256'] == DAT_HASHES['demon'] and callback['emitting_cases'] > 0
    coverage = json.loads(a.retail_coverage.read_text()) if a.retail_coverage else None
    if coverage:
        assert coverage['status'] == 'VERIFIED_BOUNDED' and coverage['exe_sha256'] == SHA
    pirate_coverage = json.loads(a.pirate_coverage.read_text()) if a.pirate_coverage else None
    if pirate_coverage:
        assert pirate_coverage['status'] == 'VERIFIED_BOUNDED' and pirate_coverage['build_sha256'] == SHA
        assert pirate_coverage['dat_sha256'] == DAT_HASHES['pirate']
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    lift_path = ROOT/'build/generated/pirate_step.cpp'
    lifted = lift_path.read_text() if lift_path.is_file() else None

    def direct_candidates(address):
        # Raw-byte candidates only: decoding from a guessed start does not
        # establish instruction boundaries or gameplay reachability.
        pattern = b'\xb8' + struct.pack('<I', address)
        pos, found = 0x1000, []
        while True:
            pos = image.find(pattern, pos, 0x54000)
            if pos < 0:
                break
            va = 0x400000 + pos
            code = list(decoder.disasm(image[pos:pos+48], va))
            if code and code[0].mnemonic == 'mov' and code[0].op_str == f'eax, {hex(address)}':
                for instruction in code[1:]:
                    if instruction.mnemonic == 'call' and '+ 0x5c]' in instruction.op_str:
                        found.append({'mov':hex(va), 'service_call':hex(instruction.address),
                                      'lift_label_present':f'L{va:x}:' in lifted if lifted is not None else None})
                        break
                    if instruction.mnemonic in ('ret','jmp'):
                        break
            pos += 1
        return found
    sequence_events = {}
    if a.mean_sequences:
        sequence = json.loads(a.mean_sequences.read_text())
        assert sequence['exe_sha256'] == SHA and sequence['status'] == 'VERIFIED_BOUNDED'
        for case in sequence['cases']:
            for event in case['events']:
                key = int(event['descriptor'], 0)
                sequence_events[key] = sequence_events.get(key, 0) + 1
    minigame_events = {}
    if a.mean_minigame:
        fixture = json.loads(a.mean_minigame.read_text())
        assert len(fixture['cases']) == 8
        assert len(fixture['image_sha256']) == 64
        for case in fixture['cases']:
            for event in case['requests']:
                if event['service'] == 0x5c:
                    desc = event['descriptor']
                    minigame_events[desc] = minigame_events.get(desc, 0) + 1
        assert set(minigame_events) == {0x437fe4,0x438008,0x43802c,0x438050}
    tables = {}
    for name in ('mean', 'pirate', 'space', 'demon'):
        dat = (GAME/'DAT'/f'{name.upper()}.DAT').read_bytes()
        assert sha(dat) == DAT_HASHES[name]
        native = profiles[name]
        assert len({x['descriptor'] for x in native}) == len(native)
        for row in native:
            assert row['period'] > 0 and 0 <= row['offset'] <= len(dat) - row['length']
        amiga = None
        if name == 'mean' and a.amiga_mean:
            amiga_dat = a.amiga_mean.read_bytes()
            different = []
            for row in native:
                start, length = row['offset'], row['length']
                assert start <= len(amiga_dat) - length
                if amiga_dat[start:start+length] != dat[start:start+length]:
                    different.append(hex(row['descriptor']))
            amiga = {'adapter_dat_sha256':sha(amiga_dat),
                     'matching_native_slices':len(native)-len(different),
                     'different_native_slices':different,
                     'scope':'Imported adapter DAT only; no original Amiga trigger or timing proof'}
        rows = []
        if name == 'mean':
            # Bounded Retail table, distinct from the Demo-addressed native Mean engine.
            addresses = list(range(0x463ec4, 0x464128, 0x24))
            context = None
        else:
            static = json.loads((ROOT/'analysis'/{'pirate':'pirate-audio-static.json',
                                'space':'space-audio-reuse.json',
                                'demon':'demon-audio-profile.json'}[name]).read_text())
            entries = static['sfx_descriptors'] if name == 'pirate' else static['sample_profiles']
            addresses = [int(x.get('descriptor', x.get('address')), 0) for x in entries]
            base = 'pirate-full-tick' if name == 'pirate' else f'{name}-full-game'
            context = (ROOT/'build/oracle'/base/'human-image.bin').read_bytes()
            expected = (static['artifact']['image_sha256'] if name == 'pirate' else
                        static['image']['sha256'] if name == 'space' else static['canonical_context_sha256'])
            assert sha(context) == expected
            assert set(addresses) == {x['descriptor'] for x in native}
        observed = {}
        trace_name = {'pirate':'pirate-audio-events.json', 'space':'space-audio-events.json'}.get(name)
        if trace_name:
            trace = json.loads((ROOT/'analysis/traces'/trace_name).read_text())
            for case in trace['cases']:
                for event in case['events']:
                    if event[1] == 0x5c:
                        observed[event[4]] = observed.get(event[4], 0) + 1
        # These retained original traces were also compared to SDL requests by
        # verify_retail_music_events.py; report separately, not as new playback.
        mode_counts = {}
        mode_cases = {'space':('bigblam','mission-campaign','multiball'),
                      'demon':('final-campaign','video-consecutive','kickback-on',
                               'clock-award-4','clock-rewards')}.get(name, ())
        mode_paths = [ROOT/'analysis/traces'/f'{name}-{case}-rewards.json' for case in mode_cases]
        if mode_paths and all(path.is_file() for path in mode_paths):
            for path in mode_paths:
                trace = json.loads(path.read_text())
                assert trace['table'] == name and trace['build_sha256'] == SHA
                assert trace['dat_sha256'] == DAT_HASHES[name]
                for event in trace['audio_events']:
                    if event[1] == 0x5c:
                        mode_counts[event[4]] = mode_counts.get(event[4], 0) + 1
        # Search the remaining compact, SHA-identified retained original traces
        # as well. Merely finding an event here does not establish that this run
        # replayed the corresponding native scenario.
        trace_counts, trace_sources = {}, {}
        if name in ('pirate', 'space', 'demon'):
            for path in sorted((ROOT/'analysis/traces').glob(f'{name}*.json')):
                try:
                    trace = json.loads(path.read_text())
                except (OSError, ValueError):
                    continue
                if not isinstance(trace, dict) or trace.get('build_sha256') != SHA or \
                   trace.get('dat_sha256') != DAT_HASHES[name]:
                    continue
                event_lists = []
                if isinstance(trace.get('audio_events'), list):
                    event_lists.append(trace['audio_events'])
                if isinstance(trace.get('cases'), list):
                    event_lists.extend(c['events'] for c in trace['cases']
                                       if isinstance(c, dict) and isinstance(c.get('events'), list))
                for event_list in event_lists:
                    for event in event_list:
                        if isinstance(event, list) and len(event) >= 5 and event[1] == 0x5c \
                           and isinstance(event[4], int):
                            desc = event[4]
                            trace_counts[desc] = trace_counts.get(desc, 0) + 1
                            trace_sources.setdefault(desc, set()).add(path.name)
        for address in addresses:
            words = struct.unpack_from('<6I', image, address - 0x400000)
            sample_id, period, volume, length, displacement, _ = words
            assert period and volume == 64 and length
            if sample_id:
                assert sample_id <= len(dat)//4
                offset = struct.unpack_from('>I', dat, (sample_id-1)*4)[0] + 8 + displacement
            else:
                assert context is not None
                initialized = struct.unpack_from('<6I', context, address - 0x400000)
                assert initialized[:5] == words[:5] and initialized[5] >= 0x1100000
                offset = initialized[5] - 0x1100000
            assert 0 <= offset <= len(dat) - length
            candidates = [x for x in native if x['length'] == length and x['period'] == period
                          and dat[x['offset']:x['offset']+length] == dat[offset:offset+length]]
            if name != 'mean':
                assert any(x['descriptor'] == address and x['offset'] == offset for x in candidates), hex(address)
            rows.append({'retail_descriptor':hex(address), 'sample_id':sample_id,
                         'dat_offset':hex(offset), 'length':length, 'period':period,
                         'volume':volume, 'pcm_sha256':sha(dat[offset:offset+length]),
                         'native_matching_descriptors':[hex(x['descriptor']) for x in candidates],
                         'raw_direct_call_candidates':direct_candidates(address),
                         'observed_requests':observed.get(address, 0) if trace_name else None,
                         'retained_mode_requests':mode_counts.get(address, 0)
                            if mode_paths and all(path.is_file() for path in mode_paths) else None,
                         'additional_retained_original_requests':trace_counts.get(address, 0)
                            if name != 'mean' else None,
                         'additional_original_trace_files':sorted(trace_sources.get(address, ())),
                         'controlled_callback_emissions':callback['emitting_cases']
                            if name == 'demon' and callback and callback['sample_descriptor'] == hex(address) else None,
                         'targeted_native_replay':(
                            hex(address) in coverage['observed_descriptors'][name]
                            if coverage and name in coverage['observed_descriptors'] else
                            hex(address) in pirate_coverage['target_descriptor_counts']
                            if name == 'pirate' and pirate_coverage else None),
                         'synthetic_original_sequence_requests':sequence_events.get(address, 0)
                            if name == 'mean' and a.mean_sequences else None,
                         'demo_minigame_original_requests':sum(minigame_events.get(x['descriptor'], 0)
                            for x in candidates) if name == 'mean' and a.mean_minigame else None})
        tables[name] = {'dat_sha256':DAT_HASHES[name], 'native_profile_count':len(native),
                        'retail_directory_count':len(rows), 'retail_descriptors':rows,
                        'amiga_adapter_slice_comparison':amiga,
                        'event_trace':trace_name,
                        'unmatched_retail_descriptors':[r['retail_descriptor'] for r in rows
                                                        if not r['native_matching_descriptors']]}
    report = {'status':'PARTIAL', 'scope':__doc__, 'retail_exe_sha256':SHA,
              'native_probe_sha256':sha(a.native.read_bytes()),
              'lift_source_sha256':sha(lift_path.read_bytes()) if lifted is not None else None,
              'tables':tables}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    for name, info in tables.items():
        print(name, 'native', info['native_profile_count'], 'retail directory',
              info['retail_directory_count'], 'unmatched', len(info['unmatched_retail_descriptors']))


if __name__ == '__main__':
    main()
