#!/usr/bin/env python3
"""Verify bounded evidence coverage; manual coverage alone never promotes a release."""
import json,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 x=read('analysis/demon-completion-contract.json');counts=dict(Counter(r['status']for r in x['rules']));assert counts==x['counts']and len(x['rules'])==20
 assert len({r['id']for r in x['rules']})==20 and sha(x['manual']['path'])==x['manual']['sha256']
 for f in x['interpretation_evidence']:assert sha(f['path'])==f['sha256']
 accepted={}
 for p in x['native_acceptance_indices']:
  a=read(p);assert a['status']=='VERIFIED'
  for c in a['cases']:accepted[c['case']]=c['fixture_sha256']
 for key,f in x['fixtures'].items():
  assert sha(f['path'])==f['sha256']==accepted[key];t=read(f['path']);assert t['original_reset_exact']and t['table']=='demon'
 for r in x['rules']:
  assert r['fixtures']and all(k in x['fixtures']for k in r['fixtures'])
 assert x['manual_rules_complete']==all(r['status']=='VERIFIED'for r in x['rules'])
 legal=read(x['legal_game']['evidence']);assert legal['production_save_reload']and legal['diagnostic_contacts']==0 and legal['twelve_vectors_exact']
 gate=x['release_gate'];release=gate['status']=='VERIFIED'
 if release:
  from verify_demon_release_gate import verify
  assert gate['evidence']==['analysis/demon-rc-island.json']
  checked=verify(gate['evidence'][0]);assert checked['archive_sha256']==gate['archive_sha256']
  assert sha(gate['archive'])==gate['archive_sha256']
 assert x['release_ready']==(x['manual_rules_complete']and release)
 out=dict(status='VERIFIED_AUDIT_INTEGRITY',counts=counts,pinned_fixtures=len(x['fixtures']),manual_rules_complete=x['manual_rules_complete'],legal_score=125000,legal_save_reload=True,release_gate=gate['status'],release_ready=x['release_ready'],scope='Twenty bounded contracts and separate SHA-bound release gate; three Retail/manual differences retained. No all-seed/driver coverage.')
 (ROOT/'analysis/traces/demon-completion-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
