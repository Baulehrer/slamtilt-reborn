#pragma once
#include <array>
#include <cstdint>
#include <filesystem>
namespace slam {
struct MeanScoreFont {
  std::array<std::array<std::uint8_t, 96>, 10> digits{};
};
MeanScoreFont load_mean_score_font(const std::filesystem::path &main_dat);
// Original406280: decimal uint32,8-pixel advance, grouped comma dots.
// x is in4-pixel units; y is in pixels; align0/1/2 subtracts0/4/8 pixels per
// digit.
void draw_mean_score(const MeanScoreFont &, std::array<std::uint8_t, 1920> &,
                     std::uint32_t score, int x, int y, int align = 0);
// Native uint64 input uses decimal digits; verified against original6-byteBCD
// path.
void draw_mean_score_u64(const MeanScoreFont &,
                         std::array<std::uint8_t, 1920> &, std::uint64_t score,
                         int x, int y, int align = 0);
} // namespace slam
