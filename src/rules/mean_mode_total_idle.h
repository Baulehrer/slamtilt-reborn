#pragma once
#include <cstdint>
namespace slam {
// Original4146ac..4146ef: mode2 idle consumes any nonzero366 even when
// service34 rejects the subsequent fixed410c8c request.
inline bool mean_mode_total_idle(std::int16_t &pending366, std::int32_t &engine40) {
  if (!pending366) return false;
  pending366 = 0;
  engine40 = 0;
  return true;
}
}
