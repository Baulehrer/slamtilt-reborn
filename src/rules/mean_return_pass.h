#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanReturnPassEvent {
  bool announcement = false;
  std::uint32_t score = 0;
};
// Caller supplies original layer2/mask1/Y<60 entry; ball mutation is separate.
// Actual41be5d..41bf03 includes419da4; service34/40f754 remain caller
// boundaries.
MeanReturnPassEvent mean_return_pass_hit(MeanBallResetState &);
// Actual419944..4199a6, once per admitted table display tick.
void mean_return_pass_tick(MeanBallResetState &);
} // namespace slam
