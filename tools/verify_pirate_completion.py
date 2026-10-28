#!/usr/bin/env python3
"""Check the bounded Pirate manual acceptance index and semantic fixtures.

This rechecks retained proof integrity/contracts, not fresh Original execution or
all native renders. Separate CTest and RC package runs exercise current binaries.
"""
import hashlib,importlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    index=json.loads((ROOT/'analysis/pirate-completion-contract.json').read_text())
    assert index['readiness']=='PLAYABLE_RC' and index['limitations']
    manual=index['manual'];assert sha(ROOT/manual['path'])==manual['sha256']
    names=[r['feature']for r in index['features']];assert len(set(names))==len(names)==24
    for path,digest in index['evidence_sha256'].items():assert sha(ROOT/path)==digest,path
    steps=0;semantic=0
    for case,row in index['fixtures'].items():
        p=ROOT/row['path'];assert sha(p)==row['sha256'],case
        t=json.loads(p.read_text());assert t['build_sha256']==index['build_sha256']and t['dat_sha256']==index['dat_sha256'],case
        assert t['deterministic_original_replay']and t['gameplay_stubs']==[],case
        assert t['tick_count']>0 and t['tick_count']%4==0,case;steps+=t['tick_count']
        if 'contract'in row:
            module,function=row['contract'].split(':');check=getattr(importlib.import_module(module),function)
            check(case,t)if row['case_argument']else check(t);semantic+=1
    for row in index['features']:
        assert row['confidence']=='VERIFIED'and row['scope']and row['evidence']and row['fixtures']
        assert all((ROOT/p).is_file()for p in row['evidence']),row['feature']
        assert all(c in index['fixtures']for c in row['fixtures']),row['feature']
    print(len(names),'manual contracts;',len(index['fixtures']),'pinned fixtures;',semantic,'semantic checks;',steps,'retained Original steps')
if __name__=='__main__':main()
