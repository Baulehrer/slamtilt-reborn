#include "mean_score_font.h"
#include <fstream>
#include <stdexcept>
#include <string>
namespace slam {
MeanScoreFont load_mean_score_font(const std::filesystem::path &path) {
  std::ifstream f(path, std::ios::binary | std::ios::ate);
  if (!f || f.tellg() != 0xf028)
    throw std::runtime_error("Unsupported MAIN.DAT score font revision");
  MeanScoreFont font;
  for (unsigned d = 0; d < 10; ++d)
    for (unsigned y = 0; y < 12; ++y) {
      f.seekg(0x8994 + d * 208 + y * 16);
      f.read(reinterpret_cast<char *>(font.digits[d].data() + y * 8), 8);
      if (!f)
        throw std::runtime_error("Truncated score font");
    }
  return font;
}
void draw_mean_score_u64(const MeanScoreFont &font,
                         std::array<std::uint8_t, 1920> &out,
                         std::uint64_t score, int x, int y, int align) {
  const auto digits = std::to_string(score);
  x = x * 4 - align * 4 * int(digits.size());
  auto put = [&](int px, int py, std::uint8_t v) {
    if (v && px >= 0 && px < 96 && py >= 0 && py < 20)
      out[py * 96 + px] = v;
  };
  // Original comma pass before each glyph, except leading group.
  int group = (int(digits.size()) - 1) % 3 + 2;
  for (unsigned i = 0; i < digits.size(); ++i) {
    if (--group == 0) {
      group = 3;
      put(x - 1, y + 11, 3);
      put(x, y + 11, 1);
      put(x - 2, y + 12, 3);
      put(x - 1, y + 12, 1);
    }
    auto &glyph = font.digits[digits[i] - '0'];
    for (int row = 0; row < 12; ++row)
      for (int col = 0; col < 8; ++col)
        put(x + col, y + row, glyph[row * 8 + col]);
    x += 8;
  }
}
void draw_mean_score(const MeanScoreFont &font,
                     std::array<std::uint8_t, 1920> &out, std::uint32_t score,
                     int x, int y, int align) {
  draw_mean_score_u64(font, out, score, x, y, align);
}
} // namespace slam
