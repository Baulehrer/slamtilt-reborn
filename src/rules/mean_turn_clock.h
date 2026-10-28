#pragma once
#include <array>
#include <cstdint>
namespace slam {
struct MeanTurnClockState {
  std::int16_t field_3ae = -1, field_390 = -1, field_35a = -1, field_3b0 = -1,
               field_af4 = 0;
  std::array<std::int16_t, 4> fields_ee1c{{-1, -1, -1, -1}};
  std::array<std::uint8_t, 4> field_260{}, field_268{}, field_258{};
  std::int32_t service_1c = 0;
};
// 4199a6..419a97, within419890 display callback:50Hz, once per four200Hz steps.
void mean_turn_clock(MeanTurnClockState &);
} // namespace slam
