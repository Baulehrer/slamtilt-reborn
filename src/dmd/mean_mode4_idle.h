#pragma once
#include "dmd/windows_dmd.h"
#include "rules/mean_ball_reset.h"
#include <filesystem>
namespace slam {
struct MeanMode4IdleAssets {
  std::array<std::array<std::uint8_t, 480>, 5> frames_10482e{};
  std::array<std::array<std::uint8_t, 120>, 20> needles_f9776{};
};
MeanMode4IdleAssets load_mean_mode4_idle(const std::filesystem::path &);
struct MeanMode4IdleEvents {
  std::uint32_t callback = 0;
  bool clear_slots = false, displayed = false, invalid_lookup = false;
};
// Original4143b8. Native shared DMD priority/delay scheduler excluded.
MeanMode4IdleEvents mean_mode4_idle(MeanBallResetState &,
                                    const MeanMode4IdleAssets &,
                                    WindowsDmdPixels &,
                                    std::int32_t lookup_value,
                                    std::uint32_t service34_return = 1);
} // namespace slam
