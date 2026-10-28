#pragma once
#include <array>
#include <cstdint>
namespace slam {
// Original43f000-relative fields; unknown semantics remain offsets.
struct MeanBallResetState {
  std::array<std::uint8_t, 0x3c0> fields{};
  std::array<std::uint8_t, 52> player_record{};
  std::array<std::uint8_t, 8> field_43ee1c{};
  std::int16_t field_438a40 = 0, field_438af4 = 0;
  std::int32_t field_438af8 = 0, field_438b44 = 0, field_438b4c = 0;
  std::int32_t table_mode = 2;
  std::uint32_t engine_3c = 0;
};
struct MeanBallResetEvents {
  bool lamp_rebuild = false;
  bool service90 = false;
};
// 419b00;416fe0 is a presentation boundary, implemented by caller.
// Valid original player records have signedWORD1e6 in0..4. Mode unchanged.
void mean_ball_reset(MeanBallResetState &, MeanBallResetEvents &);
// Original419ad8 per-player end-turn persistent record.
inline void mean_ball_save(MeanBallResetState &s) {
  for (unsigned i = 0; i < 52; ++i)
    s.player_record[i] = s.fields[0x1d4 + i];
}
} // namespace slam
