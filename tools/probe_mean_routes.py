#!/usr/bin/env python3
"""Bounded native gameplay sweep; synthetic input schedules, not original traces."""
import argparse, concurrent.futures, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--require-material5',action='store_true');p.add_argument('--require-turn',action='store_true');p.add_argument('--scenario',choices=['cycle','multiball','mode6','mode5','minigame'],default='cycle');p.add_argument('--steps',type=int,default=12000);p.add_argument('--seeds',type=int,default=4);p.add_argument('--require-multiball',action='store_true');p.add_argument('--require-mode6',action='store_true');p.add_argument('--require-targets',action='store_true');p.add_argument('--require-active',action='store_true');p.add_argument('--require-capture',action='store_true');p.add_argument('--require-mode5',action='store_true');p.add_argument('--require-reward',action='store_true');p.add_argument('--require-minigame',action='store_true');p.add_argument('--output',type=Path,default=ROOT/'analysis/traces/mean-route-coverage.json');args=p.parse_args()
def run(seed):
 command=[str(ROOT/'build/native/mean_sim_probe'),str(ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT'),str(ROOT/'build/mean-prepared'),str(ROOT/'analysis/traces/mean-flight-100.json'),str(args.steps),args.scenario,str(seed),'summary','periodic-no-bonus']
 j=json.loads(subprocess.check_output(command,text=True))
 return dict(seed=seed,states=j['states'],active=j['active'],status=j['status'],xy=[j['final_x']/65536,j['final_y']/65536],layer=j['layer'],mask=j['field_38'],material=j['material'],score=j['score'],material5_hits=j['material5_hits'],material5_groups=j['material5_groups'],top_target_hits=j['top_target_hits'],top_target_cycles=j['top_target_cycles'],lamp_updates=j['lamp_updates'],contacts=j['collisions'],restart_gate=j['restart_gate'],restart_waits=j['restart_waits'],restart_initializations=j['restart_initializations'],ball_number=j['ball_number'],ball_saves=j['ball_saves'],bonus_awards=j['bonus_awards'],last_bonus=j['last_bonus'],drains=j['drains'],launches=j['launches'],captures=j['captures'],upper_captures=j['upper_captures'],mode5_awards=j['mode5_awards'],mode_resets=j['mode_resets'],selected_mode=j['selected_mode'],table_mode=j['table_mode'],releases=j['releases'],reward_requests=j['reward_requests'],reward_completions=j['reward_completions'],ball_count=j['ball_count'],max_balls=j['max_balls'],mode6_starts=j['mode6_starts'],multiball_spawns=j['multiball_spawns'],minigame_starts=j['minigame_starts'],minigame_completions=j['minigame_completions'],final_raw_words=j['final_raw_words'])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,range(args.seeds)))
report=dict(method='Native-only synthetic input coverage; not original trajectory equivalence',scenario=args.scenario,requested_steps=args.steps,scenarios=results)
args.output.write_text(json.dumps(report,indent=2)+'\n')
for result in results:print(json.dumps({k:v for k,v in result.items() if k not in ('final_raw_words','lamp_updates')}))

if args.require_active:assert all(r['active'] and r['states']==args.steps+1 for r in results), 'Unsupported gameplay stop'
if args.require_capture:assert sum(r['captures'] for r in results)>0 and all(r['captures']==r['releases'] for r in results), 'Capture did not complete'
if args.require_mode5:assert any(r['mode5_awards']>0 for r in results) and any(r['upper_captures']>=2 for r in results), 'Mode5 award was not exercised'

if args.require_reward:assert sum(r['reward_completions'] for r in results)>0 and all(r['reward_requests']==r['reward_completions'] for r in results), 'Reward gate did not complete'

if args.require_minigame:assert sum(r['minigame_completions'] for r in results)>0 and all(r['minigame_starts']==r['minigame_completions'] for r in results), 'Mini-game did not finish'

if args.require_multiball:assert any(r['max_balls']>=4 and r['multiball_spawns']>=3 and r['ball_count']==1 for r in results), 'Multiball spawn/return was not completed'

if args.require_mode6:assert all(r['mode6_starts']>0 and r['max_balls']==8 for r in results) and any(r['ball_count']==1 and r['table_mode']==2 for r in results), 'Mode6 eight-ball spawn/return was not completed'

if args.require_targets:assert all(r['top_target_hits']>0 for r in results) and sum(r['top_target_cycles'] for r in results)>0, 'Top target cycle not exercised'

if args.require_turn:assert all(r["bonus_awards"]>0 and r["ball_number"]>1 and r["ball_saves"]>0 for r in results), "Ball reset/bonus/save lifecycle not exercised"

if args.require_mode6:assert sum(r["restart_waits"] for r in results)>0, "Multiball saved-ball queue was not exercised"

if args.require_material5:assert all(r["material5_hits"]>0 and r["material5_groups"]>0 for r in results), "Material5 contact/group chain not exercised"
