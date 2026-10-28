#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
// Original417374/41766c human (engine44==0), excluding attract-mode4 extras.
std::uint32_t mean_flipper_actions(MeanBallResetState &, std::int32_t mode,
                                   std::int32_t edge, bool right,
                                   std::int32_t service_1c = 0);
} // namespace slam
