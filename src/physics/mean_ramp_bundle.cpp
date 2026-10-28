#include "mean_ramp_bundle.h"

namespace slam {
bool mean_ramp_bundle(MeanObject &ball, std::uint16_t mask,
                      std::uint32_t dat_base, std::int32_t field_services_1c) {
  const auto x = ball.i32(0), y = ball.i32(4);
  if (ball.u16(0x48) == 1 && mask == 1 && x >= 230 * 65536 &&
      y >= 160 * 65536 && y < 280 * 65536) {
    if (y < 240 * 65536) {
      // 41c78c..41c7d0: rule-only counter/service effects remain external.
      if (field_services_1c == 0) {
        ball.put16(0x5c, 13);
        ball.put16(0x1c, 20);
        ball.put32(0x60, 0x3000);
      }
    } else {
      // 41c7db..41c84d.
      mean_set_layer(ball, 0, dat_base);
      ball.put16(0x22, 0);
      ball.put16(0x2a, 0xaa);
      ball.put16(0x5c, 11);
      ball.put16(0x1c, 10);
      ball.put32(0x60, 0x1801);
      ball.put16(0x28, 120);
    }
    return true;
  }
  if (ball.u16(0x48) == 2 && mask == 1 && y >= 150 * 65536 &&
      x >= 160 * 65536 && x < 212 * 65536) {
    // 41c300..41c341: fifth bitmap layer, no other object mutation.
    ball.put32(0x40, dat_base + 0xd5466);
    ball.put32(0x44, dat_base + 0xd20d6);
    ball.put32(0x54, dat_base + 0xdb406);
    ball.put32(0x4c, 0x3390);
    ball.put32(0x50, 1);
    ball.put16(0x48, 4);
    ball.put16(0x38, 0xffff);
    ball.put16(0x3a, 0xffff);
    return true;
  }
  if (ball.u16(0x48) == 4) {
    if (mask == 0) {
      // 41ac94..41acae, including40f7d4 with angle argument zero.
      ball.put16(0x28, 40);
      ball.put16(0x22, 0);
      ball.put16(0x2a, 0);
      ball.put16(0x5c, 8);
      ball.put16(0x1c, 40);
      ball.put32(0x60, 0x180);
    } else if (mask == 1) {
      // 41acb9..41accf calls40f8a0 with one-based layer3 or4.
      mean_set_layer(ball, x < 204 * 65536 ? 2 : 3, dat_base);
    }
    // 41ac85..41ac93 ignores other masks.
    return true;
  }
  if (ball.u16(0x48) != 3 || mask != 1 || y < 116 * 65536 || y >= 270 * 65536)
    return false;
  if (y < 140 * 65536) {
    mean_set_layer(ball, 2, dat_base);
    ball.put16(0x5c, 9);
    ball.put16(0x1c, 10);
    ball.put32(0x60, 0x601);
  } else if (y < 160 * 65536) {
    // 41b2c9..41b491 touches player+8/rules/lamps, never the ball object.
  } else if (x < 175 * 65536) {
    if (x > 100 * 65536) {
      mean_set_layer(ball, 2, dat_base);
    } else if (y < 230 * 65536) {
      mean_set_layer(ball, 0, dat_base);
      ball.put16(0x22, 0);
      ball.put16(0x2a, 0xf8e);
      ball.put16(0x5c, 7);
      ball.put16(0x1c, 10);
      ball.put32(0x60, 0x181);
      ball.put16(0x28, 120);
    } else {
      mean_set_layer(ball, 1, dat_base);
      ball.put16(0x5c, 6);
      ball.put16(0x1c, 20);
      ball.put32(0x60, 0x60);
    }
  } else {
    mean_set_layer(ball, 2, dat_base);
    ball.put16(0x22, 0);
    ball.put16(0x2a, 0);
    ball.put16(0x5c, 3);
    ball.put16(0x1c, 0);
    ball.put32(0x60, 0x1c);
    ball.put16(0x28, 40);
  }
  return true;
}
} // namespace slam
