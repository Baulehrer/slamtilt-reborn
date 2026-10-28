#pragma once
#include "physics/mean_right_gate.h"
namespace slam {
struct MeanRightCancelEvent {
  bool cancelled = false;
  std::uint32_t callback = 0;
};
// Original41c611..41c6d9; caller owns layer1/mask1/y<60 branch.
// service34_result is explicit external scheduler return (stored raw038).
// Supported original human table modes1..4; DMD40f754 remains external.
MeanRightCancelEvent mean_right_cancel(MeanBallResetState &,
                                      MeanRightGateState &,
                                      std::uint32_t service34_result);
} // namespace slam
