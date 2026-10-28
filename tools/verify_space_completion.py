#!/usr/bin/env python3
"""Validate evidence ledger integrity; success is NOT a release-ready claim."""
import json,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def main():
 x=json.loads((ROOT/'analysis/space-completion-contract.json').read_text());counts=dict(Counter(r['status']for r in x['rules']));assert counts==x['counts']
 for f in x['fixtures'].values():assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
 for f in x['native_acceptance_indices']:assert json.loads((ROOT/f).read_text())['status']=='VERIFIED',f
 for r in x['rules']:
  for f in r['fixtures']:assert f in x['fixtures'],f
 manual=ROOT/x['manual']['path'];assert manual.is_file()and hashlib.sha256(manual.read_bytes()).hexdigest()==x['manual']['sha256']
 complete=x['manual'].get('complete_source')
 if complete:assert hashlib.sha256((ROOT/complete['path']).read_bytes()).hexdigest()==complete['sha256'] and hashlib.sha256((ROOT/complete['pdf']).read_bytes()).hexdigest()==complete['pdf_sha256']
 manual_complete=all(r['status']=='VERIFIED'for r in x['rules']);assert x['manual_rules_complete']==manual_complete
 gate=x['release_gate'];release_complete=gate['status']=='VERIFIED'
 if release_complete:
  assert gate.get('evidence')and all(json.loads((ROOT/p).read_text())['status']=='VERIFIED'for p in gate['evidence'])
  archive=ROOT/gate['archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==gate['archive_sha256']
  for p in gate['evidence']:
   report=json.loads((ROOT/p).read_text());assert report.get('archive_sha256',gate['archive_sha256'])==gate['archive_sha256'],p
 ready=manual_complete and release_complete;assert x['release_ready']==ready
 out=dict(status='VERIFIED_AUDIT_INTEGRITY',manual_rule_count=len(x['rules']),counts=counts,pinned_fixtures=len(x['fixtures']),acceptance_indices=len(x['native_acceptance_indices']),manual_rules_complete=manual_complete,release_gate=gate['status'],release_ready=ready)
 (ROOT/'analysis/traces/space-completion-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
