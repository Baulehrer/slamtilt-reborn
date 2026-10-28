#pragma once
#include <array>
#include <cstdint>
#include <filesystem>

namespace slam {
struct BallMask {
  static constexpr int width = 16;
  static constexpr int height = 15;
  // Original background-preservation bytes: 255 outside, 0 inside.
  std::array<std::uint8_t, width * height> preserve_background{};
};
BallMask load_windows_ball_mask(const std::filesystem::path &main_dat);

// Original palette indices, selected by table-space screen Y / 8.
// Resolve these through the active table palette; zero is not an alpha key.
std::array<std::uint8_t, BallMask::width * BallMask::height>
load_windows_ball_pixels(const std::filesystem::path &main_dat, int screen_y);
using BallPixelBank=std::array<std::array<std::uint8_t,240>,75>;
BallPixelBank load_windows_ball_pixel_bank(const std::filesystem::path& main_dat);
} // namespace slam
