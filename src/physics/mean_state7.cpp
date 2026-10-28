#include "physics/mean_state7.h"
#include <limits>
namespace slam {
namespace {
std::int32_t wrap(std::int64_t n) {
  return static_cast<std::int32_t>(static_cast<std::uint32_t>(n));
}
std::int32_t mul(std::int32_t a, std::int32_t b) {
  return wrap(std::int64_t(a) * b);
}
std::int16_t lut(const MeanLookup &l, std::size_t off) {
  return static_cast<std::int16_t>(unsigned(l.field_43e764.at(off)) |
                                   unsigned(l.field_43e764.at(off + 1)) << 8);
}
} // namespace
bool mean_state7_boundary(MeanObject &b, std::uint32_t dat_base) {
  if (b.u16(0x34) != 0)
    return false;
  if (b.i32(0x2c) < 0x30b1d6) {
    b.put32(0x2c, 0x30b1d6);
    b.put32(0x30, 0x20000);
    return false;
  }
  if (b.i32(0x2c) <= 0x6163ac)
    return false;
  mean_set_layer(b, 1, dat_base);
  b.put16(0x38, 0xffff);
  b.put16(0x3a, 0xffff);
  b.put16(0x22, 0);
  b.put16(0x2a, 0);
  b.put16(0x5c, 18);
  b.put16(0x1c, 10);
  b.put32(0x60, 0x40000);
  b.put32(0, 0xd0000);
  b.put32(4, 0x1320000);
  b.put32(8, 0xd0000);
  b.put32(12, 0x1320000);
  b.put16(0x5a, 5);
  b.put16(0x58, 3);
  b.put16(0x28, 0);
  b.put32(0x14, 0);
  b.put32(0x18, 0);
  return true;
}
bool mean_state7_step(MeanObject &b, const MeanState7Record &r,
                      const MeanLookup &l) {
  const auto radius = r.words[2];
  if (!radius || l.field_43e764.size() < 0x2800)
    return false;
  const auto phase = wrap(std::int64_t(b.i32(0x2c)) + b.i32(0x30));
  const auto index = static_cast<std::uint32_t>((phase / 101) / radius) & 0xfff;
  const auto angle = r.words[3];
  if (angle < 0 || std::size_t(angle) * 2 + 0x801 >= l.field_43e764.size())
    return false;
  const auto sine = lut(l, index * 2), cosine = lut(l, index * 2 + 0x800);
  const auto displacement = mul(sine, radius) >> 14;
  b.put32(8, b.i32(0));
  b.put32(12, b.i32(4));
  b.put32(0x2c, phase);
  b.put16(0x1c,
          static_cast<std::uint16_t>(
              (wrap(-std::int64_t(mul(cosine, radius))) >> 14) + r.words[5]));
  b.put32(0, wrap(std::int64_t(r.words[0] +
                               (mul(displacement,
                                    lut(l, std::size_t(angle) * 2 + 0x800)) >>
                                14)) *
                  65536));
  b.put32(4,
          wrap(std::int64_t(
                   r.words[1] +
                   (mul(displacement, lut(l, std::size_t(angle) * 2)) >> 14)) *
               65536));
  b.put32(0x30,
          wrap(std::int64_t(b.i32(0x30)) - (mul(sine, r.words[4]) >> 14)));
  return true;
}
} // namespace slam
