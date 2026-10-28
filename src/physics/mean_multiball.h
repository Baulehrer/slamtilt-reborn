#pragma once
#include "mean_ball_pool.h"
#include "mean_mode5_left.h"
namespace slam {
inline bool mean_mode4_spawn(MeanBallPool &pool, MeanCaptureTickState &capture,
                             MeanMode5LeftState &mode,
                             std::array<std::int32_t, 3> &slot,
                             std::uint32_t base) {
  if (!pool.can_spawn(slot[0]))
    return false;
  auto *b = pool.allocate();
  if (!b)
    return false;
  mean_mode4_transfer(*b, capture, mode, base);
  slot[1] = mode.field_438b90;
  mode.field_43f36e = static_cast<std::int16_t>(
      static_cast<std::uint16_t>(mode.field_43f36e) - 1);
  if (mode.field_43f36e <= 0)
    mode.field_43f37e = 3;
  return true;
}
} // namespace slam
