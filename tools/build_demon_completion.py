#!/usr/bin/env python3
"""Bounded handbook coverage index; rule evidence is separate from release readiness."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 groups=['base','clock','modes','final','video','banks','variants','legal'];indices=[f'analysis/traces/demon-{g}-acceptance.json'for g in groups];fixtures={}
 for p in indices:
  x=read(p);assert x['status']=='VERIFIED'
  for row in x['cases']:
   c=row['case'];f=f'analysis/traces/demon-{c}-rewards.json';assert sha(f)==row['fixture_sha256'];fixtures[c]=dict(path=f,sha256=sha(f))
 defs=[
 ('BONUS','Six-lamp multiplier progression and actual multiplied bonus payout',['base-rules','clock-bonus']),
 ('KICKBACK','Skull bank, physical rescue, grace/expiry/rearm',['kickback-on','kickback-off']),
 ('CLOCK-AWARD','Five right targets and twelve earned random awards',[f'clock-award-{i}'for i in range(12)]),
 ('CLOCK-ADMIT','Third Clock capture earns three free balls',['clock-tower']),
 ('CLOCK-JACKPOT','Ramp requirement, held-ball multiplier and rearm',['clock-rewards']),
 ('WOLF-SELECT','Three actual ramp selections and Wolf trap admission',['mode-bat','mode-grave','mode-meatball']),
 ('SPIRIT-SELECT','Top trap arm, cycling and right-ramp start',['mode-zombie','mode-witch','mode-twice','mode-vampires']),
 ('ZOMBIE','Earned kills and increasing trap-dependent value',['zombie-values']),
 ('WITCH','Original force response and both sidelane rescues',['witch-force-on','witch-force-off','witch-left']),
 ('TWICE','Two-ball head pairs, double bonus, guards and rearm',['twice-cycles']),
 ('VAMPIRES','Four unique ramp kills, final extra award and return',['mode-vampires']),
 ('MEATBALL','Earned escape reward and normal return',['mode-meatball']),
 ('GRAVE','Distinct coffin state, decreasing value, treasure and return',['mode-grave']),
 ('BAT','Changing event selector, actual matching-ramp hit and other-ramp misses',['mode-bat']),
 ('VIDEO-BANK','Four moon targets, duplicate and already-armed bank effects',['video-wolf-idle']),
 ('WEREWOLF','Actual flipper shooting, increasing kills and no-input failure',['video-wolf-shoot','video-wolf-idle']),
 ('BRAIN','Early-input guard, bounded selection, correct/wrong confirm and release',['video-brain-win','video-brain-miss']),
 ('FINAL-ARM','Seven played modes in one game and cleared/rearmed final state',['final-campaign']),
 ('FINAL-POOL','Four free balls and pool-dependent jackpots',['final-campaign']),
 ('FINAL-REFILL','Fifth-award ball replenishment and cap bonus',['final-campaign'])]
 rules=[dict(id='DEMON-'+i,claim=claim,status='VERIFIED',scope='Bounded supported Windows Retail cases; not all seeds/timings/Tilt variants',fixtures=fs)for i,claim,fs in defs]
 grave=read(fixtures['mode-grave']['path']);marks={m['label']:m for m in grave['milestones']};names=['mode_started','reward_ramp_0_done','reward_ramp_1_done','reward_ramp_2_done'];samples=[marks[k]for k in names]
 for a,b in zip(samples,samples[1:]):assert a['aux'][9]==0 and a['aux'][10]-b['aux'][10]==5000*(b['tick']-a['tick'])
 assert marks['reward_ramp_2_done']['aux'][10]==marks['reward_ramp_3_done']['aux'][10]==46370000
 assert [p['amount']for p in grave['payments']if p['return_address']=='0x4190c8']==[46370000]
 bat=read(fixtures['mode-bat']['path']);bm={m['label']:m for m in bat['milestones']};hit=[p for p in bat['payments']if p['return_address']=='0x418c44'];assert len(hit)==1 and hit[0]['tick']==bm['reward_ramp_1_done']['tick']and hit[0]['amount']==25000000
 assert [bm['reward_ramp_'+str(i)+'_done']['aux'][1]for i in range(4)]==[2,1,0,1]
 rules[12]['retail_difference']='Observed value declines5000 per200Hz step before treasure, rather than a proven extra decrement per empty coffin. Treasure freezes value. Floor10M is STATIC only.'
 rules[17]['retail_difference']='Original requires played flags, not seven victories.'
 rules[19]['retail_difference']='Original pays35M on fifth collection when already4 active; a3-to4 replenishment itself does not pay35M.'
 manifest=dict(schema=1,interpretation_evidence=[dict(path='analysis/demon-grave-retail-difference.json',sha256=sha('analysis/demon-grave-retail-difference.json'))],status='BOUNDED_MANUAL_COVERAGE',manual=dict(path='build/manual-rules/demon.txt',sha256=sha('build/manual-rules/demon.txt'),scope='Demon handbook rules, pages26..29; source excerpt also has adjacent pages'),rules=rules,fixtures=fixtures,counts={'VERIFIED':20},native_acceptance_indices=indices,manual_rules_complete=True,release_ready=False,release_gate=dict(status='VERIFIED_STANDALONE_PREVIEW',legal_game_save='VERIFIED',evidence=['analysis/demon-release-island.json'],pending=['Final RC consistency audit and metadata promotion']),legal_game=dict(evidence=indices[-1],score=125000,diagnostic_contacts=0),not_assessed=['All seeds, timing/ramp-height/Tilt/nudge variants','Human visual tracking and physical listening','Whole-raster equality and universal drivers','Complete all-mode game using legal keys only'],next_action='Final RC consistency audit and metadata promotion against frozen062 standalone package.')
 if (ROOT/'analysis/demon-rc-island.json').exists():
  from verify_demon_release_gate import verify
  checked=verify('analysis/demon-rc-island.json')
  manifest.update(status='VERIFIED_BOUNDED_SINGLE_PLAYER_RC',release_ready=True,release_gate=dict(status='VERIFIED',evidence=['analysis/demon-rc-island.json'],archive=checked['archive'],archive_sha256=checked['archive_sha256'],pending=[]),next_action='Preserve frozen RC; fix concrete user-play regressions without broad speculative RE.')
 (ROOT/'analysis/demon-completion-contract.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Demon20 bounded contracts /',len(fixtures),'pinned fixtures; release_ready=',manifest['release_ready'])
if __name__=='__main__':main()
