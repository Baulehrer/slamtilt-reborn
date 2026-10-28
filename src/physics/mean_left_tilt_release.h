#pragma once
#include "mean_step.h"
namespace slam {
// Actual416d08, before callback2 timer/mode continuation.
inline void mean_left_tilt_release(MeanObject &b, std::uint32_t base) {
  mean_set_layer(b, 0, base);
  for (auto o : {0x22, 0x2a, 0x5c}) b.put16(o, 0);
  b.put16(0x1c, 40); b.put32(0x60, 0xaa1);
  b.put32(0, 26 * 65536); b.put32(4, 279 * 65536);
  b.put32(0x14, 0x2000); b.put32(0x18, 0x4000);
  b.put16(0x58, 2); b.put16(0x28, 40);
}
}
