#!/usr/bin/env python3
"""Publish only a verified, archive-bound Reborn release index."""
import hashlib,json,tempfile
from pathlib import Path
from verify_reborn_release import ROOT,REPORTS,verify

def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 archive='build/compat/releases/slamtilt-reborn-linux-x86_64-rc1.tar.gz';paths=list(REPORTS.values())
 e=json.loads((ROOT/REPORTS['endurance']).read_text())
 paths += [c['path']for c in e['cases']]
 paths += ['analysis/reborn-gameplay-boundary.json','analysis/traces/reborn-demon-dmd-gap.json','analysis/traces/reborn-pirate-input-binding-gap.json','docs/reborn-review.md','analysis/traces/reborn-interrupted-attempt.json','analysis/traces/reborn-demon-timing-attempt.json','analysis/traces/reborn-demon-focus-attempt.json','analysis/traces/reborn-demon-controlled-attempt.json','analysis/traces/reborn-demon-memory-isolated-attempt.json','tools/reborn_sdl_stall_probe.c']
 index=dict(id='REBORN-065',project='Slamtilt - Reborn',status='VERIFIED_BOUNDED_RC',archive=archive,archive_sha256=sha(archive),evidence=[dict(path=p,sha256=sha(p))for p in paths],controlled_background_replay_tables=['demon'],qa_sdl_probe_tables=['demon'],interactive_focus_evidence='analysis/traces/reborn-focus.json',scope='Shared Neo-90s/classic frontend and supported single-player builds; actual Debian12 and currenthostGPU. Demon background timing passed with QA-only SDL call instrumentation; prior timing failures retained, cause unknown. Mean full Original trajectory remains PARTIAL; subjective feel/hearing/all-seeds/universal drivers unclaimed.',next_action='Preserve RC and prioritize concrete play regressions; optional subjective feel/hearing acceptance.')
 with tempfile.TemporaryDirectory()as tmp:
  candidate=Path(tmp)/'index.json';candidate.write_text(json.dumps(index,indent=2)+'\n');verify(candidate)
 dest=ROOT/'analysis/reborn-release-island.json';text=json.dumps(index,indent=2)+'\n'
 if dest.exists():assert dest.read_text()==text,'Frozen Reborn index differs; create a new revision'
 else:dest.write_text(text)
 print('Reborn RC1 release gate and pinned index PASS')
if __name__=='__main__':main()
