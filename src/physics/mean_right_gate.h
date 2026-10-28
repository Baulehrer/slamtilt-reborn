#pragma once
#include "physics/mean_step.h"
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanRightGateState {
  std::int32_t field_438b2c = 0, field_438b34 = -1;
};
// Original416fe0/417b5b: supported human modes1..4 only.
bool mean_right_gate(MeanBallResetState &, MeanRightGateState &, unsigned active_count = 1);
// Caller supplies original layer0 directory (43f06c), and43f090-14 (ball
// preservation mask, not physical collision). 41cd50: caller owns preceding
// branch; x>=340 branch excluded.
bool mean_right_marker20_a(MeanObject &, const MeanBallResetState &,
                           std::uint32_t occlusion);
// 41de71..41df39 includes original fallback marker11.
void mean_right_marker20_b(MeanObject &, const MeanBallResetState &,
                           std::uint32_t occlusion);
} // namespace slam
