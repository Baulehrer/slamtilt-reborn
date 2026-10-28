import json,hashlib,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];os.chdir(root);features=[];fixtures={};evidence={}
def add(feature,lines,proof,cases,module=None,function='contract',case_arg=True):
    path='analysis/'+proof+'.json';evidence[path]=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    features.append(dict(feature=feature,manual_lines=lines,evidence=[path],fixtures=cases,confidence='VERIFIED',scope='Bounded original/native/reset/SDL contracts; diagnostic entry where declared.'))
    for case in cases:
        path=f'analysis/traces/pirate-{case}.json';assert Path(path).exists(),path
        row=dict(path=path,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
        if module:row.update(contract=module+':'+function,case_argument=case_arg)
        if case not in fixtures or module:fixtures[case]=row
add('skillshot',[21,26],'pirate-window-island',['skillshot-'+x for x in ['success-rearm','wrong-route','last-tick','expired']],'pirate_skillshot_contracts','contracts',False)
add('bonus_multiplier_and_payout',[27,34],'pirate-rule-island',['bonus-multiplier-ladder'],'pirate_multiplier_ladder_contracts','contracts',False)
add('kickback',[35,38],'pirate-final-feedback-island',['final-feedback-kickback'])
add('ramp_combos',[39,46],'pirate-window-island',['combo-'+x for x in ['chain','last-tick','expired']],'pirate_combo_contracts','contracts',False)
add('earned_extra_ball',[44,46],'pirate-window-island',['extra-threshold-chain'],'pirate_extra_threshold_contracts','contracts',False)
add('piranha_pops',[47,53],'pirate-rule-island',['piranha-chain'],'pirate_piranha_contracts','contracts',False)
add('mermaid',[54,62],'pirate-mermaid-island',['mermaid-'+x for x in ['base','growth-2m','growth-3m','hold-bonus','hold-tilt','hold-tilt-combo','hold-multiplier']],'pirate_mermaid_contracts','contracts',False)
add('magnasaver',[63,67],'pirate-magnasaver-island',['magnasaver-'+x for x in ['force-off','force-on','retrigger','rearm','tilt-armed','tilt-active','save-return']])
add('cave_locks',[68,111],'pirate-lock-matrix-island',['multiball-campaign'],'verify_pirate_multiball_campaign','contracts',False)
add('magnatable',[112,120],'pirate-magna-island',['magna-award-'+str(i)for i in range(12)],'verify_pirate_magna')
add('magnatable_fallbacks',[112,120],'pirate-magna-completion-island',['magna-mode-lit','magna-bonus-held','magna-kickback-lit','magna-all-played'],'verify_pirate_magna_eligibility','contracts')
add('adventure_selection',[121,131],'pirate-final-island',['final-campaign'],'verify_pirate_final','contracts',False)
add('walk_the_plank',[132,143],'pirate-rule-island',['plank-super-feedback'],'verify_pirate_rule_chains','plank_contracts',False)
for name,lines,cases in [('swordfight',[144,150],['sword']),('treasure_dive',[151,161],['dive-success','dive-timeout']),('monkey_business',[162,174],['monkey-success','monkey-timeout']),('shark_attack',[175,188],['shark-success','shark-timeout'])]:
    add(name,lines,'pirate-four-adventures-island',cases,'verify_pirate_modes')
add('knife_throwing_manual',[189,201],'pirate-knife-island',['knife-success','knife-failure'],'verify_pirate_knife')
# New automatic-only proof is independent of the manual-throw schedule.
features.append(dict(feature='knife_throwing_automatic',manual_lines=[194,200],evidence=['analysis/traces/pirate-knife-auto-acceptance.json'],fixtures=['knife-auto-success'],confidence='VERIFIED',scope='Only left/right during video; 25 kills,75M,earned Extra Ball collected.'))
evidence['analysis/traces/pirate-knife-auto-acceptance.json']=hashlib.sha256(Path('analysis/traces/pirate-knife-auto-acceptance.json').read_bytes()).hexdigest()
p=Path('analysis/traces/pirate-knife-auto-success.json');fixtures['knife-auto-success']=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),contract='pirate_knife_auto_contracts:contract',case_argument=True)
for name,lines in [('crocodile_multiball',[214,224]),('storm_multiball',[225,240]),('battle_multiball',[241,254]),('mutiny_multiball',[255,268])]:
    add(name,lines,'pirate-multiball-campaign-island',['multiball-campaign'],'verify_pirate_multiball_campaign','contracts',False)
add('treasure_island',[269,284],'pirate-final-island',['final-campaign'],'verify_pirate_final','contracts',False)
# Bonus accounting and credit consumption are acceptance extensions to manual rules.
for case,module in [('bonus-multiplier-payout','pirate_multiplier_payout_contracts'),('extra-credit-use','pirate_extra_use_contracts')]:
 p=Path(f'analysis/traces/pirate-{case}.json');fixtures[case]=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),contract=module+':contracts',case_argument=False)
out=dict(schema=1,evidence_id='PIRATE-COMPLETION-038',readiness='PLAYABLE_RC',build_sha256='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6',dat_sha256='6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6',manual=dict(path='build/manual-rules/pirate.txt',sha256=hashlib.sha256(Path('build/manual-rules/pirate.txt').read_bytes()).hexdigest()),features=features,fixtures=fixtures,evidence_sha256=evidence,limitations=['Diagnostic FREE-ball entry/contacts are declared per fixture; not legal-key-only all-features playthrough or full original-raster equivalence.','Battle conditional3x arm remains UNKNOWN outside manual contract; existing bounded negative evidence retained, not asserted unreachable.','Manual Battle ball count differs from observed Retail binary; original runtime remains authoritative.','Physical human input/audio listening and arbitrary distro/driver compatibility not newly verified.'])
Path('analysis/pirate-completion-contract.json').write_text(json.dumps(out,indent=2)+'\n');print(len(features),'manual contracts',len(fixtures),'unique fixtures')
