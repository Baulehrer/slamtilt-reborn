#!/usr/bin/env python3
"""Embed a project resource; invoked by CMake, no runtime asset dependency."""
import pathlib, sys
source, destination, symbol = sys.argv[1:]
data = pathlib.Path(source).read_bytes()
pathlib.Path(destination).write_text('#pragma once\n#include <cstddef>\nalignas(4) inline const unsigned char '+symbol+'[] = {\n'+',\n'.join(','.join(str(x) for x in data[i:i+32]) for i in range(0,len(data),32))+'\n};\n')
