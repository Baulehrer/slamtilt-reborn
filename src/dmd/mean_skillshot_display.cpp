#include "mean_skillshot_display.h"
#include <algorithm>
#include <fstream>
#include <stdexcept>
namespace slam {
MeanSkillshotDisplayAssets load_mean_skillshot_display(const std::filesystem::path &path) {
  MeanSkillshotDisplayAssets a;
  std::ifstream in(path, std::ios::binary);
  auto read = [&](std::size_t offset, auto &tiles) {
    in.seekg(offset);
    for (auto &tile : tiles) in.read(reinterpret_cast<char *>(tile.data()), tile.size());
    if (!in) throw std::runtime_error("Truncated MEAN.DAT skillshot tiles");
  };
  read(0x1587a4, a.rewards_1587a4);
  read(0x158be8, a.scores_158be8);
  a.font = load_mean_bonus_pixels(path.parent_path() / "MAIN.DAT");
  return a;
}
bool mean_skillshot_display(std::int32_t &counter,
                            const MeanSkillshotDisplayAssets &a,
                            WindowsDmdPixels &pixels, std::uint16_t selection,
                            std::uint16_t tier, std::uint16_t reward) {
  const auto next = static_cast<std::uint32_t>(counter) + 1;
  if ((next & 2) && (selection ? reward >= a.rewards_1587a4.size()
                                              : tier >= a.scores_158be8.size()))
    return false;
  counter = static_cast<std::int32_t>(next);
  std::array<std::uint8_t, 480> packed{};
  if (next & 2) {
    const auto &tile = selection ? a.rewards_1587a4[reward] : a.scores_158be8[tier];
    for (unsigned plane = 0; plane < 2; ++plane)
      for (unsigned y = 0; y < 13; ++y)
        std::copy_n(tile.begin() + plane * 78 + y * 6, 6,
                    packed.begin() + plane * 240 + 87 + y * 12);
  }
  pixels = decode_windows_dmd(packed);
  draw_mean_bonus_text(a.font, pixels, "SKILLSHOT", 3, 1);
  return true;
}
bool mean_skillshot_choice_pair(std::int32_t counter,
                               const MeanSkillshotDisplayAssets &a,
                               WindowsDmdPixels &pixels, std::uint16_t selection,
                               std::uint16_t tier, std::uint16_t reward) {
  const bool score_visible = selection || (counter & 2);
  const bool reward_visible = !selection || (counter & 2);
  if ((score_visible && tier >= a.scores_158be8.size()) ||
      (reward_visible && reward >= a.rewards_1587a4.size())) return false;
  auto overlay = [&](const auto &tile, unsigned x_offset) {
    for (unsigned y = 0; y < 13; ++y)
      for (unsigned x = 0; x < 48; ++x) {
        const unsigned byte = y * 6 + x / 8, bit = 7 - x % 8;
        pixels[(y + 7) * 96 + x_offset + x] =
            ((tile[byte] >> bit) & 1) | (((tile[byte + 78] >> bit) & 1) << 1);
      }
  };
  if (reward_visible) overlay(a.rewards_1587a4[reward], 48);
  if (score_visible) overlay(a.scores_158be8[tier], 0);
  return true;
}
} // namespace slam
