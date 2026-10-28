#pragma once
#include "dmd/mean_bonus_pixels.h"
namespace slam {
struct MeanMainModeHudAssets {
  std::array<WindowsDmdPixels,6> chicken_a{},chicken_b{};
  std::array<WindowsDmdPixels,3> monster_a{},monster_b{},speed_locks{};
  std::array<std::array<std::uint8_t,480>,22> rally{};
  std::array<std::array<std::uint8_t,56>,5> rally_arrows{};
  std::array<WindowsDmdPixels,20> offroad{};
  std::array<WindowsDmdPixels,7> speed{};
  MeanBonusPixels font;
};
struct MeanMainModeHud {
  std::uint32_t counter=0;
  std::uint16_t mode=5,selected=0;
  std::int16_t field_39c=0,field_38c=0,field_38e=-1,field_368=-1,field_36c=-1;
  std::uint32_t field_05c=0;
  std::uint64_t score=0;
  WindowsDmdPixels pixels{};
};
MeanMainModeHudAssets load_mean_main_mode_hud(const std::filesystem::path &mean_dat,
                                             const std::filesystem::path &main_dat);
// Original413b04 dispatch: mode5 selections0/1/2/4; mode6 SPEED.
// Formula1(selection3) uses its existing minigame display, no idle write here.
bool mean_main_mode_hud_step(MeanMainModeHud &, const MeanMainModeHudAssets &);
} // namespace slam
