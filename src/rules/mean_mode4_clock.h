#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanMode4ClockEvents {
  bool exit_to_mode2 = false, clear_slots = false;
  std::uint32_t callback = 0;
  // Original service84(bank0,order62) when signedWORD37a>=0; otherwise80.
  bool bank_order62 = false, stop80 = false;
};
// Original414d30..414e78 mode4 pre-ball 200Hz clock. Exit reset adapters
// 419f6c/416fe0 are caller-owned. Original service1c gate is caller-owned.
MeanMode4ClockEvents mean_mode4_clock(MeanBallResetState &,
                                      std::int32_t &engine40,
                                      std::uint32_t service34_return = 1);
} // namespace slam
