#include "physics/mean_point_force.h"
namespace slam {
namespace {
std::int32_t add(std::int32_t a, std::int32_t b) {
  return std::int32_t(std::uint32_t(a) + std::uint32_t(b));
}
std::int32_t sub(std::int32_t a, std::int32_t b) {
  return std::int32_t(std::uint32_t(a) - std::uint32_t(b));
}
std::int32_t mul(std::int32_t a, std::int32_t b) {
  return std::int32_t(std::uint32_t(a) * std::uint32_t(b));
}
std::int32_t sar(std::int32_t a, unsigned n) {
  auto u = std::uint32_t(a);
  return std::int32_t((u >> n) | (a < 0 ? (~std::uint32_t(0) << (32 - n)) : 0));
}
} // namespace
bool mean_point_force(MeanObject &ball,
                      const std::vector<MeanPointForceNode> &nodes,
                      const std::vector<std::uint16_t> &lookup,
                      bool suppressed) {
  if (suppressed)
    return true;
  auto b = ball;
  for (const auto &n : nodes) {
    if (n.type != -1 && n.type != 1 && n.type != 2)
      continue;
    std::int32_t x, y, d;
    auto z = sub(n.field_0a, sar(b.i32(0x1a), 16));
    if (n.type == -1) {
      x = sar(sub(b.i32(0),
                  std::int32_t((std::uint32_t(std::int32_t(n.field_06)) << 16) |
                               0x8000)),
              9);
      y = sar(sub(b.i32(4),
                  std::int32_t((std::uint32_t(std::int32_t(n.field_08)) << 16) |
                               0x8000)),
              9);
      auto ax = x < 0 ? sub(0, x) : x, ay = y < 0 ? sub(0, y) : y;
      if (ax >= 0x4000 || ay >= 0x4000)
        break;
      d = add(sar(add(mul(x, x), mul(y, y)), 16), mul(z, z));
    } else {
      x = sar(sub(sar(b.i32(0), 16), n.field_06), 1);
      y = sar(sub(sar(b.i32(4), 16), n.field_08), 1);
      d = add(add(mul(x, x), mul(y, y)), mul(z, z));
    }
    if (d > 9999)
      break;
    std::int32_t c;
    if (n.type == -1 && d <= 64)
      c = 0x7fff;
    else {
      if (d < 0 || std::size_t(d) >= lookup.size())
        return false;
      c = lookup[std::size_t(d)];
    }
    c = sub(c, 16);
    if (n.type == -1) {
      auto a = sar(mul(c, 7), 6);
      auto vx = sub(b.i32(0x14), sar(mul(sar(b.i32(0x14), 8), a), 8));
      auto vy = sub(b.i32(0x18), sar(mul(a, sar(b.i32(0x18), 8)), 8));
      b.put32(0x14, sub(vx, sar(mul(sar(x, 2), c), 8)));
      b.put32(0x18, sub(vy, sar(mul(sar(y, 2), c), 8)));
    } else {
      auto shift = n.type == 1 ? 4u : 5u;
      b.put32(0x14, add(b.i32(0x14), sar(mul(x, c), shift)));
      b.put32(0x18, add(b.i32(0x18), sar(mul(y, c), shift)));
    }
  }
  ball = b;
  return true;
}
} // namespace slam
