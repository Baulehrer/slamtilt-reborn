#pragma once
#include "rules/mean_lamp_mode.h"
#include <array>
#include <cstdint>
namespace slam {
// Original41ce03..41d0fa and41d294; common25000points remain with caller.
bool mean_award_bank_target(std::int32_t x, std::int32_t mode,
                            std::array<std::uint8_t, 5> &flags,
                            std::int16_t &field_37a, std::uint32_t &field_054,
                            MeanLampCommands &commands);
// Original4150b8..415194. Caller applies414cc0 mode/service gates at200Hz.
std::uint32_t mean_award_bank_tick(std::int16_t &field_37a,
                                   std::uint32_t &field_054,
                                   MeanLampCommands &commands);
} // namespace slam

namespace slam {
// Original41ce2b/41d084 gate +41d220. Call before bank-target writes.
bool mean_side_extra_ball(std::int32_t x, std::int16_t &field_1fc,
                          std::uint16_t &player_10, MeanLampCommands &);
} // namespace slam
