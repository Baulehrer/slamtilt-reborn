#pragma once
#include <array>
#include <cstdint>
#include <stdexcept>

namespace slam {
// Demo407a84..407b01: interpolate previous/current signed16.16 coordinates,
// subtract7 on both axes, truncate toward zero into the render WORDs.
inline std::array<int, 2> ball_display_position(std::int32_t x, std::int32_t y,
                                                std::int32_t previous_x,
                                                std::int32_t previous_y,
                                                unsigned residual_ms) {
  if (residual_ms > 5)
    throw std::out_of_range("Ball display residual outside original step");
  const double alpha = double(residual_ms) / 5.0;
  return {
      int((double(previous_x) * (1 - alpha) + double(x) * alpha) / 65536.0 - 7),
      int((double(previous_y) * (1 - alpha) + double(y) * alpha) / 65536.0 -
          7)};
}
} // namespace slam
