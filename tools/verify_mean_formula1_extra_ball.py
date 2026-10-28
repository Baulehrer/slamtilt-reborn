#!/usr/bin/env python3
"""Finite native Formula1 prize collection/replay; no original whole-table claim."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
base = [sys.argv[1], str(next((root / 'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))),
        str(root / 'build/mean-prepared'), str(root / 'analysis/traces/mean-flight-100.json'),
        str(root / 'analysis/traces/mean-first-minigame-natural-finite-win.json')]
cases = []
for phase in [18, 10, 0]:
    actual = json.loads(subprocess.check_output(base + [str(phase)], text=True))
    assert actual['game_over'] and actual['new_game_restored'] and actual['ball_number'] == 4
    win = actual['events'][0]
    assert win['event'] == 'win' and win['pending'] == 1 and win['credits'] == 0
    if phase:
        assert actual['collected'] and actual['replayed'] and actual['bonus_completions'] == 4
        collection, replay = actual['events'][1:]
        assert collection['event'] == 'collected' and collection['pending'] == 0 and collection['credits'] == 1
        assert collection['callback'] == 0x410d34 and collection['ball'] == 3
        assert replay['event'] == 'replayed' and replay['credits'] == 0 and replay['ball'] == 3
        assert json.loads(subprocess.check_output(base + [str(phase)], text=True)) == actual
    else:
        assert not actual['collected'] and not actual['replayed'] and actual['bonus_completions'] == 3
        assert len(actual['events']) == 1
    cases.append(actual)
report = {
    'scope': 'Native finite games from reset using recorded SDL-equivalent entry and original-verified Retail steering. Win arms prize; real upper-trap collection credits extra ball; bonus consumes credit preserving ball3; four bonuses then GameOver and clean new game. Two exact repeats and an uncollected-prize control. No placements/endless mode or original whole-table trajectory equivalence.',
    'build_sha256': json.loads((root / 'analysis/traces/mean-flight-100.json').read_text())['build_sha256'],
    'original_evidence': 'analysis/mean-formula1-extra-ball-proof.json',
    'entry_inputs': 'analysis/traces/mean-first-minigame-natural-finite-win.json',
    'steering_inputs': 'analysis/traces/mean-minigame1-winning-input.json',
    'continuation': 'mean_finite_shot_input(global_step, ball_y, phase); launch held',
    'cases': cases,
}
(root / 'analysis/traces/mean-formula1-extra-ball-gameplay.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS Formula1 prize/collection/extra-ball replay/GameOver/reset: two routes, exact repeats, uncollected control')
