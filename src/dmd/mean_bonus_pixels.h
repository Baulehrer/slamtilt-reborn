#pragma once
#include "assets/mean_score_font.h"
#include "dmd/windows_dmd.h"
#include <filesystem>
#include <string_view>
namespace slam {
struct MeanBonusPixels {
  MeanScoreFont score;
  std::array<std::array<std::uint8_t, 40>, 43> text{};
};
struct MeanBonusTableState {
  std::uint32_t field_43f028 = 0, field_43f02c = 0;
};
struct MeanBonusTableResult {
  std::uint32_t result = 0, score_add = 0;
};
MeanBonusTableResult
mean_bonus_table_callback(MeanBonusTableState &, unsigned stage,
                          std::uint16_t field_player_0c = 0);
using MeanBonusAnimation = std::array<WindowsDmdPixels, 24>;
MeanBonusAnimation
load_mean_bonus_animation(const std::filesystem::path &mean_dat);
// counter is43f028 AFTER the stage1 callback increments it; counts1..64.
WindowsDmdPixels render_mean_bonus_intro(const MeanBonusAnimation &,
                                         unsigned counter);
MeanBonusPixels load_mean_bonus_pixels(const std::filesystem::path &);
void mean_bonus_background(WindowsDmdPixels &, int level);
void draw_mean_bonus_text(const MeanBonusPixels &, WindowsDmdPixels &,
                          std::string_view, int x, int y);
enum class MeanBonusScreen { Bank, Multiplier, Total, Held, NoBonus };
WindowsDmdPixels render_mean_bonus_pixels(const MeanBonusPixels &,
                                          MeanBonusScreen, int background,
                                          std::uint32_t bank,
                                          std::uint16_t multiplier,
                                          std::uint64_t score,
                                          bool held_visible = true);
} // namespace slam
