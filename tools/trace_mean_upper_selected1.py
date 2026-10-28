#!/usr/bin/env python3
"""Reuse the original upper cycle harness for mode selections1/2."""
import sys
from pathlib import Path
selection=int(sys.argv[1]) if len(sys.argv)>1 else 1
assert selection in (1,2)
source=(Path(__file__).parent/'trace_mean_upper_second.py').read_text()
source=source.replace('b=bytearray(100)',f"u.mem_write(0x43f1e6,struct.pack('<h',{selection}))\nb=bytearray(100)")
source=source.replace('mean-upper-second-original',f'mean-upper-selected{selection}-original')
source=source.replace('SECOND upper capture',f'SELECTION{selection} SECOND upper capture')
exec(compile(source,str(Path(__file__).parent/'trace_mean_upper_second.py'),'exec'))
