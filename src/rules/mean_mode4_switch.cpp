#include "rules/mean_mode4_switch.h"
namespace slam {
namespace {
std::int16_t word(const MeanBallResetState &s, unsigned o) {
  return static_cast<std::int16_t>(unsigned(s.fields[o]) |
                                   unsigned(s.fields[o + 1]) << 8);
}
void put(MeanBallResetState &s, unsigned o, std::uint32_t n,
         unsigned size = 2) {
  for (unsigned i = 0; i < size; ++i)
    s.fields[o + i] = n >> (8 * i);
}
} // namespace
MeanMode4SwitchEvent mean_mode4_switch(MeanBallResetState &s, unsigned layer,
                                       unsigned mask, std::int32_t x,
                                       std::int32_t y) {
  MeanMode4SwitchEvent e;
  if (mask != 1 || s.table_mode != 4 || word(s, 0x3a6) != 0)
    return e;
  if (layer == 1 && y >= 390 * 65536 && x >= 150 * 65536) {
    put(s, 0x396, 0);
    put(s, 0x39e, 15);
    return e;
  }
  if (layer != 3 || y >= 64 * 65536)
    return e;
  e.score = static_cast<std::uint32_t>(std::int64_t(30000000) +
                                       std::int64_t(word(s, 0x1f4)) * 15000000);
  put(s, 0x050, e.score, 4);
  put(s, 0x1f4, static_cast<std::uint16_t>(word(s, 0x1f4)) + 1);
  s.table_mode = 2;
  e.callback = 0x41249c;
  e.service84 = word(s, 0x37a) >= 0;
  e.service80 = !e.service84;
  e.lamp_rebuild = true;
  e.service416fe0 = true;
  return e;
}
} // namespace slam
