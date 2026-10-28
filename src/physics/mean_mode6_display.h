#pragma once
#include "mean_reward_display.h"
namespace slam {
// Actual410b00 ends at frame267 and clears43f382 in the same display tick.
// Only uninterrupted announcement scheduling; rendering remains external.
inline void mean_mode6_display_tick(MeanRewardDisplay &display,
                                    std::int16_t &gate) {
  display.last_frame = 267;
  mean_reward_display_tick(display, gate);
  if (display.active == 0)
    gate = 0;
}
} // namespace slam
