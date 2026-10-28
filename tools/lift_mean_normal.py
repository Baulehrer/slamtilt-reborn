#!/usr/bin/env python3
"""Generate bounded static C++ for the original Mean normal evaluator."""
import argparse
from pathlib import Path
import lift_mean_flippers as lift

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    lift.RANGES = [(0x40e1d0, 0x40e83f)]
    source, _ = lift.generate(args.exe)
    if isinstance(source, list):
        source = '\n'.join(source)
    source = source.replace('physics/flipper_lift.h', 'physics/mean_normal_lift.h').replace('FlipperLift', 'MeanNormalLift')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source)

if __name__ == '__main__':
    main()
