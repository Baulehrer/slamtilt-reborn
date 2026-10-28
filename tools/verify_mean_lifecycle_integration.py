#!/usr/bin/env python3
"""Real native input schedules through Full-policy game-over, freeze and R reset.
This is integration coverage, not original trajectory equivalence.
"""
import argparse, concurrent.futures, json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--native', type=Path, required=True)
a = p.parse_args()
def run(seed):
    command = [str(a.native), str(ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT'), str(ROOT/'build/mean-prepared'), str(ROOT/'analysis/traces/mean-flight-100.json'), '100000', 'finite', str(seed), 'summary']
    result = json.loads(subprocess.check_output(command, text=True))
    assert result['game_over'] and not result['active'], result['status']
    assert result['ball_number'] == 4 and result['ball_count'] == 0 and result['table_mode'] == 0
    assert result['game_over_frozen'] and result['new_game_restored']
    assert result['bonus_awards'] >= 3 and result['restart_initializations'] >= 2
    assert result['bonus_ball_frozen'] and result['bonus_frozen_steps'] > 0
    assert result['bonus_starts'] == result['bonus_completions'] == result['bonus_awards']
    # Both-flipper input can accelerate the original bonus to42 ticks.
    assert result['bonus_display_ticks'] >= 42 * result['bonus_completions']
    assert result['status'].startswith('GAME OVER'), result['status']
    return dict(seed=seed, **{k: result[k] for k in ['states', 'ball_number', 'ball_count', 'table_mode', 'status', 'score', 'bonus_awards', 'bonus_starts', 'bonus_completions', 'bonus_display_ticks', 'bonus_ball_frozen', 'bonus_frozen_steps', 'ball_saves', 'restart_initializations', 'restart_waits', 'game_over_frozen', 'new_game_restored', 'final_raw_words']})
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    cases = list(pool.map(run, range(4)))
assert run(0) == cases[0], 'Finite game is not deterministic'
path = ROOT/'analysis/traces/mean-lifecycle-gameplay-validation.json'
path.write_text(json.dumps(dict(method='Native gameplay; Full finite default, demo physics. No original trajectory equivalence.', cases=cases, deterministic_seed0=True), indent=2)+'\n')
print(json.dumps(dict(games=len(cases), steps=[c['states'] for c in cases], game_over_freeze_and_restart=True, deterministic=True)))
