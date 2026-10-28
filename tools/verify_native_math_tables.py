#!/usr/bin/env python3
"""Compare independently generated engine math with the private Original oracle."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', type=Path, default=ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE')
    parser.add_argument('--compiler', default='c++')
    parser.add_argument('--report', type=Path, default=ROOT / 'analysis/traces/dat-only-math.json')
    args = parser.parse_args()
    work = ROOT / 'build/dat-only-math'
    work.mkdir(exist_ok=True)
    probe = work / 'probe.cpp'
    probe.write_text('''#include "assets/native_math_tables.h"
#include <iostream>
#include <stdexcept>
int main() {
  bool rejected=false; std::vector<std::uint8_t> small;
  try { slam::initialize_native_math(small); }
  catch(const std::invalid_argument&) { rejected=true; }
  if(!rejected) return 2;
  std::vector<std::uint8_t> image(0x100000,0xaa);
  slam::initialize_native_math(image);
  if(image[0x556cb]!=0xaa || image[0x63274]!=0xaa) return 3;
  auto copy=image; slam::initialize_native_math(copy);
  if(copy!=image) return 4;
  std::cout.write(reinterpret_cast<const char*>(image.data()+0x556cc),0x63274-0x556cc);
}
''')
    exe = work / 'probe'
    subprocess.run([args.compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', '-Wpedantic',
                    '-I' + str(ROOT / 'src'), str(probe),
                    str(ROOT / 'src/assets/native_math_tables.cpp'), '-o', str(exe)], check=True)
    actual = subprocess.check_output([exe])
    spec = importlib.util.spec_from_file_location('mean_reference', ROOT / 'tools/slamimport_reference.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = args.exe.read_bytes()
    source_sha = hashlib.sha256(source).hexdigest()
    assert source_sha == '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
    original = module.mapped_image(source, 0x100000)[0x556cc:0x63274]
    differences = [(hex(0x4556cc + i), a, b) for i, (a, b) in enumerate(zip(actual, original)) if a != b]
    report = dict(status='VERIFIED' if actual == original else 'DIFFERENCE',
                  source_build_sha256=source_sha, native_range=['0x4556cc', '0x463274'],
                  bytes=len(actual), sha256=hashlib.sha256(actual).hexdigest(),
                  original_sha256=hashlib.sha256(original).hexdigest(),
                  differences=len(differences), first_differences=differences[:8],
                  generated_from_formulas=True, atan_compatibility_exceptions=6,
                  force_compatibility_exceptions=11, size_guard=True,
                  outside_range_preserved=True, deterministic_repeat=True,
                  scope='Complete bounded 56,232-byte shared math island. Independently generated sine/atan/flipper/force tables; 17 sparse historical quantization exceptions and two adjacent native scalars. No EXE/code/header/prepared-image bytes embedded. Original EXE is a test oracle only.')
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    assert actual == original, differences[:8]
    print('Native math formulas: all56,232bytes exact;17 sparse quantization quirks, bounds/determinism PASS')


if __name__ == '__main__':
    main()
