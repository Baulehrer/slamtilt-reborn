#pragma once
#include <cstdint>
namespace slam {
struct MeanBonusTurn {
  std::uint32_t field_player_08 = 0;
  std::uint16_t field_player_0e = 1, field_player_10 = 0;
  std::uint16_t field_player_12 = 1, field_player_14 = 0;
  std::uint32_t current_player = 1, player_count = 1;
};
// 40735b..407374. Returns original low32-bit score-service argument.
std::uint32_t mean_drain_bonus(const MeanBonusTurn &,
                               std::uint32_t field_43d864);
// 407794..407808. Bonus is awarded before this boundary, not here.
bool mean_finish_bonus_turn(MeanBonusTurn &);
} // namespace slam
