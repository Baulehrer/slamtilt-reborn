#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanMode4SwitchEvent {
  std::uint32_t score = 0, callback = 0;
  bool service84 = false, service80 = false, lamp_rebuild = false,
       service416fe0 = false;
};
// Phase0 only; supplied layer/mask and Q16 x/y refer to pre-switch ball pose.
// 41c57a..5a3 lower timer arm;41af2c..affb upper exit/reward.
MeanMode4SwitchEvent mean_mode4_switch(MeanBallResetState &, unsigned layer,
                                       unsigned mask, std::int32_t x,
                                       std::int32_t y);
} // namespace slam
