#pragma once
#include "rules/mean_ball_reset.h"
#include <vector>
namespace slam {
struct MeanSharedRewardEvents {
  std::vector<std::uint32_t> scores;
  std::uint32_t callback = 0;
  std::uint32_t callback_eax = 7, callback_edx = 6, callback_ecx = 2;
  std::int32_t callback_arg0 = -1, callback_arg1 = -1;
  std::uint32_t control_arg1 = 0;
  bool control = false, service_419da4 = false, service_419f6c = false,
       service_4194e4 = false, service_4169e4 = false;
};
// Original 41b8d0. Event IDs 0..5; service34 return is explicit.
// External service bodies are adapter boundaries, never inferred side effects.
MeanSharedRewardEvents mean_shared_reward(MeanBallResetState &, unsigned event_id,
                                         std::uint32_t service34_return);
// Original4169e4. Tables are loaded from the user PE at438ddc/438df4.
// Returns false only for invalid original memory-index domains.
bool mean_rally_target(MeanBallResetState &, std::uint32_t engine_38,
                       const std::vector<std::uint32_t> &table_438ddc,
                       const std::vector<std::uint32_t> &table_438df4);
}
