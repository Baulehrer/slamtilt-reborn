#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanMode4InputEvents {
  std::uint32_t callback = 0;
  bool clear_slots = false;
  bool exit_to_mode2 = false;
  bool invalid_divisor = false;
};
// Human engine44==0 mode4 branch AFTER common flipper actions. service34's
// returned handle is explicit. lookup_value is 438bdc[(WORD3a8 &127)].
MeanMode4InputEvents mean_mode4_input(MeanBallResetState &, bool right,
                                      std::int32_t lookup_value,
                                      std::uint32_t service34_return = 1);
} // namespace slam
