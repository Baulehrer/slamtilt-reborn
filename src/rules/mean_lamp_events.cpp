#include "mean_lamp_events.h"
namespace slam {
MeanLampEventResult
mean_top_target_lamps(MeanLampEvents &s,
                      std::array<std::array<std::uint8_t, 4>, 3> &commands,
                      std::int32_t x, std::int32_t y, unsigned layer,
                      unsigned mask, std::int32_t field_services_1c) {
  if (layer != 0 || mask != 4 || y >= 80 * 65536 || field_services_1c != 0)
    return {};
  const unsigned index = x < 64 * 65536 ? 0 : x < 91 * 65536 ? 1 : 2;
  commands[index] = {5, 1, 0, 25};
  s.field_43f1e8[index] = 1;
  if (s.field_43f1e8[0] && s.field_43f1e8[1] && s.field_43f1e8[2]) {
    s.field_43f1e8 = {0, 0, 0};
    for (auto &command : commands)
      command = {6, 2, 0, 25};
    return {true, true};
  }
  return {true, false};
}
} // namespace slam
namespace slam {
MeanTopTargetRewardResult mean_top_target_reward(MeanTopTargetReward &s) {
  // Actual438e44 lookup. Bounded to initialized/reachable indices0..7.
  constexpr std::int16_t next[]{2, 2, 3, 4, 5, -1, -1, -1};
  if (s.field_player_12 < 0 || s.field_player_12 > 7)
    return {};
  const auto value = next[s.field_player_12];
  if (value < 0)
    return {true, 10000000, false};
  s.field_player_12 = value;
  if (value == 5) {
    s.command_43f2f4 = {4, 6, 1, 0};
    s.field_43f1fa = static_cast<std::int16_t>(
        static_cast<std::uint16_t>(s.field_43f1fa) + 1);
  }
  return {true, 0, true};
}
} // namespace slam
