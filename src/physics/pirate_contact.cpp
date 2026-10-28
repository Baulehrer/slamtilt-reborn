#include "physics/pirate_contact.h"
#include <algorithm>
#include <cstring>
#include <stdexcept>
namespace slam {
namespace {
std::int32_t bits(std::uint32_t x) {
  std::int32_t v;
  std::memcpy(&v, &x, 4);
  return v;
}
std::int32_t add(std::int32_t a, std::int32_t b) {
  return bits(std::uint32_t(a) + std::uint32_t(b));
}
std::int32_t sub(std::int32_t a, std::int32_t b) {
  return bits(std::uint32_t(a) - std::uint32_t(b));
}
std::int32_t mul(std::int32_t a, std::int32_t b) {
  return bits(std::uint32_t(a) * std::uint32_t(b));
}
std::int32_t sar(std::int32_t a, unsigned n) {
  return bits((std::uint32_t(a) >> n) |
              (a < 0 ? (~std::uint32_t(0) << (32 - n)) : 0));
}
std::int32_t word(const std::vector<std::uint8_t> &v, unsigned a) {
  if (a + 1 >= v.size())
    throw std::out_of_range("Pirate contact lookup");
  std::uint16_t u = v[a] | std::uint16_t(v[a + 1]) << 8;
  return u >= 0x8000 ? int(u) - 65536 : int(u);
}
void transfer(MeanObject &b, const PirateContactState &s, std::uint16_t marker,
              std::uint32_t field60, std::uint16_t field28) {
  b.put32(0x40, bits(s.layer0_hit));
  b.put32(0x44, bits(s.layer0_normal));
  b.put32(0x54, bits(s.layer0_render));
  b.put32(0x4c, bits(s.layer0_stride));
  b.put32(0x50, bits(s.layer0_planes));
  for (auto o : {0x38, 0x3a})
    b.put16(o, 0xffff);
  for (auto o : {0x22, 0x2a, 0x48})
    b.put16(o, 0);
  b.put16(0x1c, 1);
  b.put16(0x5c, marker);
  b.put32(0x60, bits(field60));
  b.put16(0x28, field28);
}
} // namespace
bool pirate_contact(MeanObject &b, const MeanLookup &l,
                    const PirateContactState &s, std::int32_t ox,
                    std::int32_t oy) {
  const int layer = sar(b.i32(0x46), 16), material = sar(b.i32(0x3a), 16),
            angle = sar(b.i32(0x1c), 16);
  if (layer < 0 || layer > 2 || material < 0 ||
      (layer == 0 &&
       (material == 5 || material == 6 ||
        ((material == 3 || material == 4) && s.field_services_1c == 0))) ||
      (layer == 1 && material == 1))
    return false;
  if (angle < 0 || angle > 4095)
    throw std::out_of_range("Pirate contact angle");
  const auto sn = word(l.field_43e764, angle * 2),
             cs = word(l.field_43e744, angle * 2);
  const auto vx = sar(add(b.i32(0x14), ox), 8),
             vy = sar(add(b.i32(0x18), oy), 8);
  const auto m = [&](int factor, std::int32_t value) {
    return sar(sub(0, mul(value, factor)), 8);
  };
  auto tangent = sub(sar(mul(sn, vx), 14), sar(mul(cs, vy), 14));
  auto normal = add(sar(mul(cs, vx), 14), sar(mul(sn, vy), 14));
  if (layer == 0) {
    if (material > 6)
      normal = 0;
    else if (material == 2)
      normal = std::max(m(200, normal), -512);
    else
      normal = m(material == 1 ? 32 : 80, normal);
  } else if (layer == 1) {
    if (material > 3)
      normal = 0;
    else if (material == 0)
      normal = m(16, normal);
    else if (material == 3)
      normal = std::max(m(200, normal), -512);
    else if (b.i32(4) > 300 * 65536) {
      transfer(b, s, 0, 0x10823, 40);
      normal = m(32, normal);
      tangent = 0;
    } else
      normal = m(80, normal);
  } else {
    if (material > 3)
      normal = 0;
    else if (material == 3)
      normal = std::max(m(200, normal), -512);
    else if (material <= 1)
      normal = m(16, normal);
    else {
      normal = m(8, normal);
      tangent = 0;
      if (b.i32(4) > 199 * 65536)
        transfer(b, s, 0, 0x10823, 40);
      else
        transfer(b, s, 11, 0x1801, 80);
    }
  }
  if (normal > 0)
    return true;
  if (angle < 0x800) {
    tangent = sub(tangent, sar(mul(cs, 5), 14));
    normal = add(normal, sar(mul(sn, 5), 14));
    if (normal > 0)
      normal = 0;
  }
  const unsigned inv = (-angle) & 4095;
  const auto isn = word(l.field_43e764, inv * 2),
             ics = word(l.field_43e744, inv * 2);
  const auto outx = sub(sar(mul(normal, ics), 14), sar(mul(tangent, isn), 14)),
             outy = sub(
                 0, add(sar(mul(tangent, ics), 14), sar(mul(normal, isn), 14)));
  b.put32(0x14, sub(bits(std::uint32_t(outx) << 8), ox));
  b.put32(0x18, sub(bits(std::uint32_t(outy) << 8), oy));
  return true;
}
} // namespace slam

namespace slam {
bool pirate_wall_contact(MeanObject &ball, const MeanLookup &lookup,
                         const PirateContactState &state,
                         MeanCollisionBits &bits, const TableProfile &profile,
                         std::uint32_t base) {
  const auto angle = ball.u16(0x1e);
  const auto original = ball;
  if (!pirate_contact(ball, lookup, state))
    return false;
  try {
    table_configure_bits(ball, profile, base, bits);
    mean_separate(
        ball, bits,
        static_cast<std::int16_t>(word(lookup.field_43e744, angle * 2)),
        static_cast<std::int16_t>(word(lookup.field_43e764, angle * 2)), 0, 0);
  } catch (...) {
    ball = original;
    throw;
  }
  return true;
}
} // namespace slam
