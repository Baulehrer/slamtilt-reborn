#pragma once
#include "dmd/mean_skillshot_display.h"
namespace slam {
struct MeanPlayerHudAssets {
  std::array<std::uint8_t,480> frame_14e92e{};
  WindowsDmdPixels frame_14eb0e{},frame_151a84{};
  MeanSkillshotDisplayAssets skillshot;
};
struct MeanPlayerHud {
  std::uint32_t counter=0,field_engine_5c=0,field_engine_60=0,
                field_engine_04=1,field_engine_08=1;
  std::int16_t field_360=100;
  std::uint16_t field_35c=0,field_358=0,field_206=0,field_362=0,player_0e=1;
  std::uint64_t score=0;
  WindowsDmdPixels pixels{};
  std::array<std::uint8_t,480> scratch{};
};
MeanPlayerHudAssets load_mean_player_hud(const std::filesystem::path &mean_dat,
                                        const std::filesystem::path &main_dat);
// Original414970 including41455c/414b60. Caller owns idle eligibility and
// engine5c countdown (404b2a, after the display dispatcher).
bool mean_player_hud_step(MeanPlayerHud &, const MeanPlayerHudAssets &);
} // namespace slam
