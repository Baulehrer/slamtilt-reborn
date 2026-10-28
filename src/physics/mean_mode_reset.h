#pragma once
#include <array>
#include <cstdint>
namespace slam {
struct MeanModeResetState {
  std::array<std::uint8_t, 5> field_43f1e0{};
  std::int16_t field_43f1e6 = 0, field_43f384 = 0, field_43f366 = -1;
};
// Original419da4 selection plus terminal mode reset; lamp/audio effects
// external.
bool mean_mode_reset(MeanModeResetState &state, std::int32_t &table_mode);
} // namespace slam
