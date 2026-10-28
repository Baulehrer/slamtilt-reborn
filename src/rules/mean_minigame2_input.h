#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanMinigame2InputEvent {
  std::uint32_t descriptor = 0;
  std::uint32_t edx = 0, ebx = 0;
};
// Original417374/41766c Engine44!=0, WORD3a4==2 variant.
// Both flipper press callbacks have the same effect. Negative edge is release.
MeanMinigame2InputEvent mean_minigame2_input(MeanBallResetState &,
                                             std::int32_t edge,
                                             std::int32_t service1c = 0,
                                             std::int32_t engine44 = 1);
} // namespace slam
