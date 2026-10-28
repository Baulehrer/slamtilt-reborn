#include "mean_switch_bundle.h"
namespace slam {
bool mean_switch_bundle(MeanObject &ball, std::uint16_t mask,
                        std::uint32_t base, std::uint32_t &points) {
  points = 0;
  const auto y = ball.i32(4), x = ball.i32(0);
  const auto layer = ball.u16(0x48);
  if (layer == 0 && mask == 4) {
    if (y < 80 * 65536) {
      // 41c99a..41cab7: three top targets request25000 base points.
      points = 25000;
      return true;
    }
    if (y >= 120 * 65536 && y < 450 * 65536) {
      // 41cd50: field43f3b8==0 exits;340..450 also exits without ball writes.
      return true;
    }
  }
  if (layer == 2 && mask == 1 && y < 60 * 65536) {
    // 41be36..41be5a, human mode: preserve signed arithmetic-quarter rounding.
    // Subsequent timer/rule/score calls remain external to this ball-local
    // slice.
    for (const auto offset : {0x14, 0x18}) {
      const auto value = ball.i32(offset);
      const auto quarter = value / 4 - (value < 0 && value % 4 != 0 ? 1 : 0);
      ball.put32(offset, value - quarter);
    }
    return true;
  }
  if (layer == 2 && mask == 1 && y >= 60 * 65536 && y < 150 * 65536 &&
      x >= 160 * 65536 && x < 234 * 65536) {
    // 41c00c..41c03c: original directed target, no external rule calls.
    ball.put16(0x22, 1);
    ball.put16(0x5c, 15);
    ball.put16(0x1c, 60);
    ball.put32(0x60, 0x1c000);
    ball.put16(0x28, 120);
    ball.put16(0x24, 227);
    ball.put16(0x26, 101);
    return true;
  }
  if (layer == 2 && mask == 1 && y >= 60 * 65536 && y < 150 * 65536 &&
      x >= 234 * 65536) {
    // 41c047..41c09f: ball-local part; player+8/rule services excluded.
    mean_set_layer(ball, 3, base);
    ball.put16(0x22, 0);
    ball.put16(0x2a, 0);
    ball.put16(0x5c, 17);
    ball.put16(0x1c, 60);
    ball.put32(0x60, 0x30000);
    ball.put16(0x28, 40);
    return true;
  }
  if (layer == 2 && mask == 1 && x < 160 * 65536 && y >= 150 * 65536) {
    // 41c16c..41c22f.
    mean_set_layer(ball, y < 200 * 65536 ? 3 : 0, base);
    if (y >= 200 * 65536) {
      ball.put16(0x22, 0);
      ball.put16(0x2a, 0);
      ball.put16(0x5c, 0);
      ball.put16(0x1c, 0);
      ball.put32(0x60, 0xaa1);
      ball.put16(0x28, 40);
    }
    return true;
  }
  if (layer == 2 && mask == 0) {
    // 41c3dc..41c463.
    const auto field = ball.u16(0x5c);
    if (field == 3 || field == 8 || field == 9 || field == 10)
      return true;
    if (field == 16 || (field == 15 && y < 100 * 65536)) {
      if (field == 15)
        ball.put16(0x5c, 16);
      ball.put16(0x1c, 60);
      ball.put32(0x60, 0x38000);
    } else {
      ball.put16(0x22, 0);
      ball.put16(0x2a, 0);
      ball.put16(0x5c, 14);
      ball.put16(0x1c, 40);
      ball.put32(0x60, 0xc000);
      ball.put16(0x28, 40);
    }
    return true;
  }
  return false;
}
} // namespace slam
