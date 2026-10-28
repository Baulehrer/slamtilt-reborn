#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanMode4Events {
  std::uint32_t score_add = 0, callback = 0;
  bool clear_slots = false, exit_to_mode2 = false;
};
// Bounded Mode4 post-ramp/collision branches, after existing common effects.
// branch is original41bf0c,41c0df or41c39e. Exit4194e4/419f6c/416fe0
// caller-owned.
MeanMode4Events mean_mode4_event(MeanBallResetState &, std::uint32_t branch,
                                 std::uint32_t service34_return = 1);
} // namespace slam
