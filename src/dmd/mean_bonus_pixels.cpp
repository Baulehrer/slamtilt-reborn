#include "mean_bonus_pixels.h"
#include <algorithm>
#include <fstream>
#include <stdexcept>
#include <string>
namespace slam {
MeanBonusTableResult mean_bonus_table_callback(MeanBonusTableState &s,
                                               unsigned stage,
                                               std::uint16_t field_player_0c) {
  if (stage == 0) {
    s.field_43f028 = 0;
    return {1, std::uint32_t(std::int64_t(std::int16_t(field_player_0c)) *
                             1000000)};
  }
  if (stage == 2)
    return {1, 0};
  auto count = ++s.field_43f028;
  if (std::int32_t(count) < 5)
    s.field_43f02c = count;
  else if (std::int32_t(count) < 17)
    s.field_43f02c = count - 5;
  else if (std::int32_t(count) < 65)
    s.field_43f02c = count - 17;
  else {
    s.field_43f02c = count - 65;
    return {1, 0};
  }
  return {};
}
MeanBonusAnimation load_mean_bonus_animation(const std::filesystem::path &p) {
  std::ifstream in(p, std::ios::binary);
  in.seekg(0x11cc4e);
  MeanBonusAnimation animation{};
  for (auto &frame : animation) {
    std::array<std::uint8_t, 480> packed{};
    in.read(reinterpret_cast<char *>(packed.data()), packed.size());
    if (!in)
      throw std::runtime_error("Truncated MEAN.DAT bonus animation");
    frame = decode_windows_dmd(packed);
  }
  return animation;
}
MeanBonusPixels load_mean_bonus_pixels(const std::filesystem::path &p) {
  MeanBonusPixels f;
  f.score = load_mean_score_font(p);
  std::ifstream in(p, std::ios::binary);
  for (unsigned c = 0; c < f.text.size(); ++c)
    for (unsigned y = 0; y < 5; ++y) {
      in.seekg(0x91b4 + c * 96 + y * 16);
      in.read(reinterpret_cast<char *>(f.text[c].data() + y * 8), 8);
      if (!in)
        throw std::runtime_error("Truncated MAIN.DAT bonus font");
    }
  return f;
}
void mean_bonus_background(WindowsDmdPixels &out, int level) {
  // Original4060a4 table429a9c and alternating48-word row halves.
  constexpr unsigned char levels[7][2] = {{0, 0}, {0, 1}, {1, 1}, {1, 2},
                                          {2, 2}, {2, 3}, {3, 3}};
  level = std::clamp(level, 0, 6);
  for (unsigned y = 0; y < 20; ++y)
    for (unsigned x = 0; x < 96; ++x)
      out[y * 96 + x] = levels[level][(x + y) % 2];
}
WindowsDmdPixels render_mean_bonus_intro(const MeanBonusAnimation &animation,
                                         unsigned counter) {
  WindowsDmdPixels out{};
  if (counter < 5)
    mean_bonus_background(out, 6);
  else if (counter < 17)
    mean_bonus_background(out, std::max(0, 6 - int((counter - 5) / 2)));
  else if (counter < 65)
    out = animation[(counter - 17) / 2];
  return out;
}
void draw_mean_bonus_text(const MeanBonusPixels &f, WindowsDmdPixels &out,
                          std::string_view text, int x, int y) {
  x *= 4;
  for (unsigned char c : text) {
    if (c != ' ' && c >= 48 && c < 48 + f.text.size())
      for (int row = 0; row < 5; ++row)
        for (int col = 0; col < 8; ++col) {
          auto v = f.text[c - 48][row * 8 + col];
          if (v && x + col >= 0 && x + col < 96 && y + row >= 0 && y + row < 20)
            out[(y + row) * 96 + x + col] = v;
        }
    x += 8;
  }
}
WindowsDmdPixels render_mean_bonus_pixels(const MeanBonusPixels &f,
                                          MeanBonusScreen screen,
                                          int background, std::uint32_t bank,
                                          std::uint16_t multiplier,
                                          std::uint64_t score,
                                          bool held_visible) {
  WindowsDmdPixels out;
  mean_bonus_background(out, background);
  switch (screen) {
  case MeanBonusScreen::Bank:
    draw_mean_bonus_text(f, out, "BONUS", 7, 1);
    draw_mean_score(f.score, out, bank, 1, 7);
    break;
  case MeanBonusScreen::Multiplier: {
    auto digits =
        std::to_string(std::uint32_t(std::int32_t(std::int16_t(multiplier))));
    draw_mean_bonus_text(f, out, digits, 4, 1);
    draw_mean_bonus_text(f, out, "X BONUS", int(digits.size()) + 5, 1);
    auto product =
        std::uint32_t(std::uint64_t(bank) *
                      std::uint32_t(std::int32_t(std::int16_t(multiplier))));
    draw_mean_score(f.score, out, product, 1, 7);
    break;
  }
  case MeanBonusScreen::Total:
    draw_mean_bonus_text(f, out, "TOTAL SCORE", 1, 1);
    draw_mean_score_u64(f.score, out, score, 1, 7);
    break;
  case MeanBonusScreen::Held:
    if (held_visible)
      draw_mean_bonus_text(f, out, "BONUS HELD", 2, 1);
    draw_mean_score(f.score, out, bank, 1, 7);
    break;
  case MeanBonusScreen::NoBonus:
    draw_mean_bonus_text(f, out, "NO BONUS", 4, 7);
    break;
  }
  return out;
}
} // namespace slam
