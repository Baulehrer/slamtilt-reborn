#pragma once
#include "mean_step.h"
namespace slam {
// Original41d94c human-mode gate-independent no-op region.
// False leaves left capture and right state20 unsupported until their
// slot/other-ball gates and captured-ball tick are implemented.
bool mean_baseline_three_noop(const MeanObject &ball);
} // namespace slam
