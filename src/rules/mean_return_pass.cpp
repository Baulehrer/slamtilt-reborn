#include "rules/mean_return_pass.h"
namespace slam {
namespace {
std::int16_t word(const MeanBallResetState &s, unsigned o) {
  return static_cast<std::int16_t>(s.fields[o] |
                                   (unsigned(s.fields[o + 1]) << 8));
}
void put(MeanBallResetState &s, unsigned o, std::uint16_t v) {
  s.fields[o] = v;
  s.fields[o + 1] = v >> 8;
}
} // namespace
MeanReturnPassEvent mean_return_pass_hit(MeanBallResetState &s) {
  MeanReturnPassEvent e;
  if (word(s, 0x384) == 0 && s.table_mode <= 4) {
    bool all = true;
    for (unsigned i = 0; i < 5; ++i)
      all &= s.fields[0x1e0 + i] != 0;
    if (!all) {
      const int previous = word(s, 0x1e6);
      int selected = previous;
      do {
        if (++selected >= 5)
          selected = 0;
      } while (s.fields[0x1e0 + selected] != 0);
      put(s, 0x1e6, selected);
      s.fields[0x2bc + previous * 4] = s.fields[0x1e0 + previous] ? 1 : 2;
      const auto o = 0x2bc + selected * 4;
      s.fields[o] = 4;
      s.fields[o + 1] = 6;
      s.fields[o + 2] = s.fields[o + 3] = 0;
    }
  }
  if (word(s, 0x374) >= 0) {
    put(s, 0x37c, static_cast<std::uint16_t>(word(s, 0x37c)) + 1);
    e.score =
        static_cast<std::uint32_t>(static_cast<std::int32_t>(word(s, 0x37c))) *
        5000000u;
    for (unsigned i = 0; i < 4; ++i)
      s.fields[0x050 + i] = e.score >> (8 * i);
    e.announcement = true;
  }
  put(s, 0x374, 150);
  s.fields[0x25c] = 4;
  s.fields[0x25d] = 3;
  s.fields[0x25e] = 1;
  s.fields[0x25f] = 0;
  return e;
}
void mean_return_pass_tick(MeanBallResetState &s) {
  const auto t = word(s, 0x374);
  if (t < 0)
    return;
  put(s, 0x374, static_cast<std::uint16_t>(t) - 1);
  if (word(s, 0x374) >= 0)
    return;
  put(s, 0x37c, 0);
  s.fields[0x25c] = 2;
  if (s.table_mode == 4 && word(s, 0x3a6) == 1) {
    s.fields[0x25c] = 4;
    s.fields[0x25d] = 3;
    s.fields[0x25e] = 1;
    s.fields[0x25f] = 0;
  }
}
} // namespace slam
