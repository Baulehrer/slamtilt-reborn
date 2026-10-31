#!/usr/bin/env python3
"""Compare a private ProTracker-table period experiment on four first ticks.

Experimental library applies a zero-finetune table, uses that integer period
for zero pitch bend, and floors nearest sampling. The optional --stim-only
variant gates these changes to STIM; the default changes all MODRNG modules.
The experimental library is never installed
or used by the port. First ticks use adapted Original startup and cannot prove
long-run timing, finetune/effects, or audible equivalence.
"""
import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=ROOT/'build/libxmp')
    p.add_argument('--native', type=Path, default=ROOT/'build/native/stim_audio_probe')
    p.add_argument('--channel-probe', type=Path, default=ROOT/'build/native/tracker_channel_probe')
    p.add_argument('--work', type=Path, default=ROOT/'build/tracker-period-experiment')
    p.add_argument('--output', type=Path, default=ROOT/'build/tracker-period-experiment/report.json')
    p.add_argument('--stim-only', action='store_true', help='Isolate experiment to modules identified as STIM')
    p.add_argument('--original-rate', action='store_true', help='Experiment with original integer frequency calculation')
    args = p.parse_args()
    source, work = args.source.resolve(), args.work.resolve()
    if source == work or source in work.parents:
        raise ValueError('work directory must not alter source')
    work.mkdir(parents=True, exist_ok=True)
    copy = work/'source'
    if copy.exists():
        if not (copy/'.slamtilt-period-experiment').is_file():
            raise RuntimeError(f'refusing to replace unmarked directory: {copy}')
        shutil.rmtree(copy)
    shutil.copytree(source, copy, ignore=shutil.ignore_patterns('.git'))
    (copy/'.slamtilt-period-experiment').write_text('Generated experiment; safe to replace.\n')
    mixer = copy/'src/mix_all.c'
    text = mixer.read_text()
    start = text.index('#define NEAREST_ROUND()')
    end = text.index('\n\n#define VAR_NORM', start)
    assert 'frac += (1 << (SMIX_SHIFT - 1))' in text[start:end]
    if args.stim_only:
        old = text[start:end]
        new = old.replace('    frac +=', '    if (!vi->slam_stim) { \\\n    frac +=').replace('    frac &= SMIX_MASK; \\', '    frac &= SMIX_MASK; \\\n    } \\')
        assert new != old
        mixer.write_text(text[:start] + new + text[end:])
        voice = copy/'src/mixer.h'
        text = voice.read_text()
        anchor = '\tint chn;\t\t/* channel number */'
        assert text.count(anchor) == 1
        voice.write_text(text.replace(anchor, anchor + '\n\tint slam_stim; /* isolated experiment */'))
        mix_loop = copy/'src/mixer.c'
        text = mix_loop.read_text()
        anchor = '\t\tvi = &p->virt.voice_array[voc];'
        assert text.count(anchor) == 1
        mix_loop.write_text(text.replace(anchor, anchor + '\n\t\tvi->slam_stim = strcmp(m->mod.type, "Slamtilt") == 0;'))
    else:
        mixer.write_text(text[:start] + '#define NEAREST_ROUND() do { } while (0)' + text[end:])
    if args.original_rate:
        mix_loop = copy/'src/mixer.c'
        text = mix_loop.read_text()
        anchor = '\t\tstep = C4_PERIOD * c5spd / s->freq / vi->period;'
        assert text.count(anchor) == 1
        condition = 'if (vi->slam_stim) ' if args.stim_only else ''
        mix_loop.write_text(text.replace(anchor, anchor + '\n\t\t' + condition +
                                         'step = floor(3546895.0 / vi->period) / s->freq;'))
    period = copy/'src/period.c'
    text = period.read_text()
    anchor = '\td = (double)n + (double)f / 128;'
    assert text.count(anchor) == 1
    injection = '''\t/* Experiment only: normal-tuning ProTracker periods, three octaves. */
\tif (IS_PERIOD_MODRNG() && f == 0 && n >= 48 && n < 84) {
\t\tstatic const unsigned short notes[36] = {
\t\t\t856,808,762,720,678,640,604,570,538,508,480,453,
\t\t\t428,404,381,360,339,320,302,285,269,254,240,226,
\t\t\t214,202,190,180,170,160,151,143,135,127,120,113
\t\t};
\t\treturn notes[n - 48];
\t}

'''
    if args.stim_only:
        injection = injection.replace('IS_PERIOD_MODRNG()', 'strcmp(m->mod.type, "Slamtilt") == 0')
    period.write_text(text.replace(anchor, injection + anchor))
    player = copy/'src/player.c'
    text = player.read_text()
    anchor = '\tfinal_period = libxmp_note_to_period_mix(xc->note, linear_bend);'
    assert text.count(anchor) == 1
    condition = 'strcmp(m->mod.type, "Slamtilt") == 0' if args.stim_only else 'IS_PERIOD_MODRNG()'
    player.write_text(text.replace(anchor, anchor + '''
\t/* Experiment: preserve the table period only for zero bend. */
\tif (''' + condition + ''' && xc->finetune == 0 && linear_bend == 0 &&
\t    xc->note >= 48 && xc->note < 84)
\t\tfinal_period = xc->period;
'''))
    build = work/'build'
    subprocess.run(['cmake','-S',str(copy),'-B',str(build),'-DBUILD_SHARED=ON',
                    '-DBUILD_STATIC=OFF','-DCMAKE_BUILD_TYPE=Release'],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['cmake','--build',str(build),'-j','4'],check=True,stdout=subprocess.DEVNULL)
    library = build/'libxmp.so.4'
    env = dict(os.environ, LD_LIBRARY_PATH=str(build))
    linkage = subprocess.check_output(['ldd',str(args.native.resolve())],env=env,text=True)
    assert str(library) in linkage
    measurement = work/'measurement'
    subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_native.py'),
                    '--native',str(args.native.resolve()),'--output',str(measurement)],env=env,check=True)
    channel = subprocess.check_output([str(args.channel_probe.resolve()),
                                      str(measurement/'pirate-bank0.stim'), '34', '1'],env=env)
    assert len(channel) == 4 + 882 * 4
    period_q12 = struct.unpack_from('<I', channel)[0]
    assert period_q12 == 190 * 4096, f'Pirate channel 1 period: {period_q12}'
    compared = json.loads((measurement/'comparison.json').read_text())
    baseline = json.loads((ROOT/'docs/verification/retail-tracker-native-2026-10-31.json').read_text())
    floor = json.loads((ROOT/'docs/verification/tracker-floor-experiment-2026-10-31.json').read_text())
    cases=[]
    for row, old, floored in zip(compared['cases'], baseline['cases'], floor['cases']):
        assert row['table']==old['table']==floored['table']
        assert row['original_sha256']==old['original_sha256']
        cases.append({'table':row['table'],'original_sha256':row['original_sha256'],
                      'baseline_correlation':old['uncentered_correlation'],
                      'floor_correlation':floored['floor_correlation'],
                      'table_floor_correlation':row['uncentered_correlation'],
                      'table_floor_best_alignment':row['original_relative_frame_offset'],
                      'table_floor_exact_frames':row['exact_frames']})
    result={'status':'EXPERIMENT_ONLY','scope':__doc__,'stim_only':args.stim_only,'original_rate':args.original_rate,'library_sha256':sha(library),
            'period_source_sha256':sha(source/'src/period.c'),'native_sha256':sha(args.native),
            'frames_per_table':882,'pirate_channel_1_period_q12':period_q12,'cases':cases}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: experimental period table tested on four original first ticks')


if __name__=='__main__':
    main()
