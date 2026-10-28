#include "mean_bonus_turn.h"
namespace slam {
std::uint32_t mean_drain_bonus(const MeanBonusTurn &s,
                               std::uint32_t suppressed) {
  if (suppressed)
    return 0;
  const std::int32_t multiplier = s.field_player_12 < 0x8000
                                      ? s.field_player_12
                                      : std::int32_t(s.field_player_12) - 65536;
  return s.field_player_08 * std::uint32_t(multiplier);
}
bool mean_finish_bonus_turn(MeanBonusTurn &s) {
  if (s.field_player_14 == 0)
    s.field_player_08 = 0;
  s.field_player_14 = 0;
  s.field_player_12 = 1;
  if (s.field_player_10 > 0 && s.field_player_10 < 0x8000) {
    --s.field_player_10;
    return true;
  }
  ++s.field_player_0e;
  s.current_player =
      s.current_player == s.player_count ? 1 : s.current_player + 1;
  return false;
}
} // namespace slam
