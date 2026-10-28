#!/usr/bin/env python3
"""Publish a bounded RC evidence index only after its complete gate verifies."""
import hashlib,json,tempfile
from pathlib import Path
from verify_demon_release_gate import ROOT,verify
REPORTS=['analysis/demon-import-recipe.json','analysis/traces/demon-import-acceptance.json',
 'analysis/traces/demon-rc-package.json','analysis/traces/demon-rc-compat.json',
 'analysis/traces/demon-rc-host.json','analysis/traces/demon-rc-fixtures.json',
 'analysis/traces/demon-rc-metadata.json','analysis/traces/demon-rc-timing-attempts.json']
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 archive='build/compat/releases/slamtilt-demon-rc1.tar.gz'
 x=dict(id='DEMON-RC-063',status='VERIFIED',archive=archive,archive_sha256=sha(archive),evidence=[dict(path=p,sha256=sha(p))for p in REPORTS],scope='Bounded supported Windows Retail single-player RC1, 20 handbook contracts/36 fixtures; no all-seed/physical-input/listening/whole-raster/universal-driver claim',next_action='Preserve frozen RC; prioritize concrete user-play regressions.')
 text=json.dumps(x,indent=2)+'\n'
 with tempfile.TemporaryDirectory()as tmp:
  candidate=Path(tmp)/'index.json';candidate.write_text(text);checked=verify(candidate)
 dest=ROOT/'analysis/demon-rc-island.json'
 if dest.exists():assert dest.read_text()==text,'Frozen RC index differs; create new revision'
 else:dest.write_text(text)
 print(json.dumps(checked,indent=2))
if __name__=='__main__':main()
