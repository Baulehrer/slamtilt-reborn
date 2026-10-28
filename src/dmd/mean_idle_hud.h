#pragma once
#include "dmd/mean_bonus_pixels.h"
namespace slam {
struct MeanIdleHudAssets {
  std::array<WindowsDmdPixels,15> pit_stop{};
  std::array<WindowsDmdPixels,7> bank_early{};
  std::array<WindowsDmdPixels,9> bank_late{};
  std::array<WindowsDmdPixels,10> score{};
  MeanBonusPixels font;
};
struct MeanIdleHud {
  std::uint32_t counter=0;
  std::int16_t field_398=-1,field_37a=-1,field_3ac=0;
  std::uint32_t field_054=0;
  std::uint64_t score=0;
  WindowsDmdPixels pixels{};
};
MeanIdleHudAssets load_mean_idle_hud(const std::filesystem::path &mean_dat,
                                    const std::filesystem::path &main_dat);
// Original41472e..41496e. Caller owns mode2/idle admission and shared438af8.
void mean_idle_hud_step(MeanIdleHud &, const MeanIdleHudAssets &);
} // namespace slam
