#pragma once
#include "physics/mean_step.h"
#include <array>
#include <cstdint>
namespace slam {
struct MeanTurnEntry {
  std::int32_t mode = 1;
  std::int16_t field_43f3ae = -1, field_43f35a = -1;
  std::array<std::uint8_t, 4> command_43f258{}, command_43f260{};
};
// Call only after the original layer3/switch1 route reaches41b184.
bool mean_turn_playfield_entry(MeanTurnEntry &);
// 41aaac caller sets state4/x=-16/y616 even when normal drain requested.
// Return true means original ball-save; next engine tick initializes stateFFFF.
bool mean_turn_drain_intercept(MeanObject &, MeanTurnEntry &,
                               unsigned ball_count,
                               std::int32_t field_services_1c);
// 4199a6..4199fe; caller must preserve original callback38 frequency.
bool mean_turn_save_clock(MeanTurnEntry &);
} // namespace slam
