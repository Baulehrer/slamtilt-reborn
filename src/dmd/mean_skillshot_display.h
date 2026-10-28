#pragma once
#include "dmd/mean_bonus_pixels.h"
#include <filesystem>
namespace slam {
struct MeanSkillshotDisplayAssets {
  std::array<std::array<std::uint8_t, 156>, 7> rewards_1587a4{};
  std::array<std::array<std::uint8_t, 156>, 8> scores_158be8{};
  MeanBonusPixels font;
};
MeanSkillshotDisplayAssets load_mean_skillshot_display(const std::filesystem::path &mean_dat);
// Original41455c only. Caller owns idle dispatch/selection eligibility.
// False means an invalid tile index; pixels are left untouched.
bool mean_skillshot_display(std::int32_t &field_438af8,
                            const MeanSkillshotDisplayAssets &,
                            WindowsDmdPixels &, std::uint16_t field_358,
                            std::uint16_t field_206, std::uint16_t field_362);
// Original414b60 only: overlays the visible choice tiles, preserving background.
// Counter is supplied by the idle caller and is not incremented here.
bool mean_skillshot_choice_pair(std::int32_t field_438af8,
                               const MeanSkillshotDisplayAssets &,
                               WindowsDmdPixels &, std::uint16_t field_358,
                               std::uint16_t field_206, std::uint16_t field_362);
} // namespace slam
