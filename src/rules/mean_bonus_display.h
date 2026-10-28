#pragma once
#include <cstdint>
namespace slam {
// Engine globals 43e73c/43e7e4/43e738/43e734/43e714/43e718.
struct MeanBonusDisplay {
  std::uint32_t phase = 0, timer = 0, step = 1, field_43e734 = 0;
  std::uint32_t bonus_total = 0, field_43e718 = 0;
};
struct MeanBonusDisplayInput {
  std::uint32_t bonus = 0, suppressed = 0;
  std::uint16_t multiplier = 1;
  // Actual table+38 return for stage1 or stage2; no guessed duration.
  std::uint32_t callback_result = 0;
};
struct MeanBonusDisplayEvents {
  bool award = false, finish = false, rotate_only = false, initialize = false;
  std::uint32_t score_argument = 0;
  int callback_stage = -1;
};
// Original40424f/404366 key-down and4042ca/4043bb key-up bit writes.
void mean_bonus_input_edge(MeanBonusDisplay &, bool right, bool pressed);
MeanBonusDisplayEvents mean_bonus_display_step(MeanBonusDisplay &,
                                               const MeanBonusDisplayInput &);
} // namespace slam
