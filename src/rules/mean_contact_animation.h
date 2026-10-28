#pragma once
#include <cstdint>
namespace slam {
// Original418030, with the native renderer consuming each submitted frame.
struct MeanContactAnimation {
  std::int32_t countdown = 0, cursor = 0, repetitions = 0;
  int displayed_frame = -1;
  void trigger(int count) {
    countdown = cursor = 0;
    repetitions = count;
  }
  int tick(bool renderer_available = true) {
    if (!repetitions)
      return -1;
    if (cursor < -1) {
      cursor = 2;
      --repetitions;
    }
    if (countdown >= 0) {
      --countdown;
      if (countdown >= 0)
        return -1;
      countdown = 1;
    }
    if (!renderer_available)
      return -1;
    const auto frame = cursor--;
    if (frame >= 0)
      displayed_frame = frame;
    return frame;
  }
};
} // namespace slam
