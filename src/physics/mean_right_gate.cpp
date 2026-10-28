#include "physics/mean_right_gate.h"
namespace slam {
namespace {
std::int16_t w(const MeanBallResetState &s, unsigned o) {
  return std::int16_t(unsigned(s.fields[o]) | (unsigned(s.fields[o + 1]) << 8));
}
std::uint32_t d(const MeanBallResetState &s, unsigned o) {
  std::uint32_t n = 0;
  for (unsigned i = 0; i < 4; ++i)
    n |= std::uint32_t(s.fields[o + i]) << (i * 8);
  return n;
}
void marker(MeanObject &b, const MeanBallResetState &s, std::uint32_t occlusion,
            bool variant) {
  b.put32(0x40, d(s, 0x078));
  b.put32(0x44, d(s, 0x074));
  b.put32(0x50, variant ? std::int16_t(d(s, 0x06a) >> 16) : w(s, 0x06c));
  b.put32(0x4c, d(s, 0x070));
  b.put16(0x38, 0xffff);
  b.put16(0x3a, 0xffff);
  b.put16(0x48, 0);
  b.put16(0x28, 40);
  b.put16(0x22, 0);
  b.put16(0x2a, 0);
  b.put16(0x5c, 20);
  b.put16(0x1c, 0);
  b.put32(0x60, 0x100001);
  b.put32(0x54, occlusion);
}
} // namespace
bool mean_right_gate(MeanBallResetState &s, MeanRightGateState &g, unsigned active_count) {
  if (s.table_mode == 6) {
    // Actual416fe0→417bb8: right lock is available only with another free ball.
    auto &f=s.fields;
    f[0x250]=4; f[0x251]=6; f[0x252]=1; f[0x253]=0;
    const int locks=(w(s,0x38e)>=0)+(w(s,0x368)>=0)+(w(s,0x36c)>=0);
    const bool armed=w(s,0x36c)<0 && std::int64_t(locks)-active_count < -1;
    if (armed) f[0x250]=2;
    g.field_438b2c=0; g.field_438b34=armed ? 1 : -1;
    f[0x3b8]=f[0x3b9]=armed ? 255 : 0;
    return true;
  }
  if (s.table_mode < 1 || s.table_mode > 4)
    return false;
  bool armed = s.table_mode < 4 && w(s, 0x3a2) != 0;
  g.field_438b2c = 0;
  g.field_438b34 = armed ? 1 : -1;
  s.fields[0x3b8] = s.fields[0x3b9] = armed ? 255 : 0;
  return true;
}
bool mean_right_marker20_a(MeanObject &b, const MeanBallResetState &s,
                           std::uint32_t occlusion) {
  if (b.i32(4) >= 340 * 65536 || !w(s, 0x3b8))
    return false;
  marker(b, s, occlusion, false);
  return true;
}
void mean_right_marker20_b(MeanObject &b, const MeanBallResetState &s,
                           std::uint32_t occlusion) {
  if (w(s, 0x3b8) && b.u16(0x5c) == 0) {
    marker(b, s, occlusion, true);
    return;
  }
  if (w(s, 0x3b8) && b.u16(0x5c) == 20)
    return;
  b.put16(0x22, 0);
  b.put16(0x2a, 170);
  b.put16(0x5c, 11);
  b.put16(0x1c, 10);
  b.put32(0x60, 0x1801);
  b.put16(0x28, 120);
}
} // namespace slam
