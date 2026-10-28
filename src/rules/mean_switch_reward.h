#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanSwitchRewardEvent {
  std::uint32_t score = 0;
  bool service84 = false;
};
// Original41d3e4..41d8af; unknown field meanings remain original offsets.
MeanSwitchRewardEvent mean_switch_reward(MeanBallResetState &);
} // namespace slam
