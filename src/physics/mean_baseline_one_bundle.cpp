#include "mean_baseline_one_bundle.h"
namespace slam {
bool mean_baseline_one_bundle(MeanObject &ball, std::uint32_t dat_base,
                              std::uint16_t field_43f3b8) {
  if (ball.i32(0) <= 230 * 65536 || ball.i32(4) < 225 * 65536)
    return false;
  if (field_43f3b8 != 0) {
    if (ball.u16(0x5c) == 0) {
      mean_set_layer(ball, 0, dat_base);
      ball.put16(0x22, 0);
      ball.put16(0x2a, 0);
      ball.put16(0x5c, 20);
      ball.put16(0x1c, 0);
      ball.put32(0x60, 0x100001);
      ball.put16(0x28, 40);
      ball.put32(0x54, static_cast<std::int32_t>(dat_base + 0xcbb96 - 14));
      return true;
    }
    if (ball.u16(0x5c) == 20)
      return true;
  }
  ball.put16(0x22, 0);
  ball.put16(0x2a, 0xaa);
  ball.put16(0x5c, 11);
  ball.put16(0x1c, 10);
  ball.put32(0x60, 0x1801);
  ball.put16(0x28, 120);
  return true;
}
} // namespace slam
