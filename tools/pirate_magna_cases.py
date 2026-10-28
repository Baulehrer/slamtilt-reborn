"""Frozen MagnaTable case schedules; no optional analysis dependencies."""
# Delays are simulation time, not RNG/state injection. Each predicted candidate
# is checked at its actual original admission before freezing the schedule.
AWARDS={0:(132,2),1:(112,0),2:(4,0),3:(44,1),4:(12,1),5:(16,0),
        6:(24,0),7:(4,2),8:(8,1),9:(0,1),10:(4,1),11:(0,0)}
CASES=['magna-slot-0','magna-slot-1','magna-slot-2','magna-escape','magna-expired','magna-idle',
       *[f'magna-award-{i}'for i in AWARDS],'magna-natural-both','magna-natural-left']
SCOPE=('Integer-only original MagnaTable with diagnostic free-ball events and legal '
       'Shift keys; no rule/timer/score/capture writes. Excludes post-prefix x87 '
       'render XY/visibility/sorting; not full original raster or legal-key-only trajectory equivalence.')
