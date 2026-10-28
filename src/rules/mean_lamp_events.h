#pragma once
#include <array>
#include <cstdint>
namespace slam {
struct MeanLampEvents {
  std::array<std::uint8_t, 3> field_43f1e8{};
};
struct MeanLampEventResult {
  bool handled = false;
  bool request_41d153 =
      false; // Original reward continuation; not inferred semantics.
};
// 41c974..41cab7 and41d0fc..41d153. Commands correspond to43f280..43f28b.
MeanLampEventResult
mean_top_target_lamps(MeanLampEvents &state,
                      std::array<std::array<std::uint8_t, 4>, 3> &commands,
                      std::int32_t x, std::int32_t y, unsigned layer,
                      unsigned mask, std::int32_t field_services_1c = 0);
} // namespace slam
namespace slam {
struct MeanTopTargetReward {
  std::int16_t field_player_12 = 1;
  std::int16_t field_43f1fa = 0;
  std::array<std::uint8_t, 4> command_43f2f4{};
};
struct MeanTopTargetRewardResult {
  bool handled = false;
  std::uint32_t score_points = 0;
  bool services_pending = false;
};
MeanTopTargetRewardResult mean_top_target_reward(MeanTopTargetReward &state);
} // namespace slam
