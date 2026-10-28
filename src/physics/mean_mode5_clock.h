#pragma once
#include "mean_mode5_left.h"
namespace slam {
// Original414e79..41504e; selections0/1/2 and bounded selected4 single-ball
// stage. Returns true when timeout resets the mode; presentation effects
// external.
bool mean_mode5_clock(MeanMode5LeftState &mode, MeanCaptureTickState &state,
                      unsigned ball_count = 1);
} // namespace slam
