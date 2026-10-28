#pragma once
#include "rules/mean_ball_reset.h"
#include <functional>
namespace slam {
struct MeanRightProgressEvent {
  std::uint32_t score = 0, callback = 0;
  bool reset_right_gate = false;
};
// 41cb28..41cd50 after lower switch/common reward;41b8d0 andDMD queue external.
MeanRightProgressEvent mean_right_progress(MeanBallResetState &,
    const std::function<void(MeanBallResetState &)> &common_reward = {});
} // namespace slam
