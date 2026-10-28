#pragma once
#include <array>
#include <cstdint>
namespace slam {
using MeanLampCommands = std::array<std::array<std::uint8_t, 4>, 63>;
struct MeanLampModeInput {
  std::array<std::uint8_t, 4> field_1d4{}, field_060{}, field_1dc{};
  std::array<std::uint8_t, 5> field_1e0{}, field_1ec{};
  std::array<std::uint8_t, 3> field_1e8{};
  std::int16_t field_398 = 0, field_3ba = 0, field_3bc = 0, field_392 = 0,
               field_3a2 = 0, field_3b0 = -1, field_374 = -1, field_3ae = 0,
               service10_field10 = 0, field_1da = 0, field_394 = 0,
               field_38a = 0, field_1f2 = 0, field_1e6 = 0, field_384 = 0,
               field_204 = 0, field_1fa = 0, field_202 = 0, field_200 = 0,
               field_1fc = 0, field_37a = -1, field_37c = 0;
  std::int32_t table_mode = 2;
};
// Original419f6c including41a54c. Preserve untouched command bytes.
void mean_lamp_mode_reset(const MeanLampModeInput &, MeanLampCommands &);
// Original4194e4 service selection; caller implements presentation service.
inline bool mean_lamp_mode_service84(std::int16_t field_37a) {
  return field_37a >= 0;
}
} // namespace slam
