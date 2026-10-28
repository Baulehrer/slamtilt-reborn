#include "mean_upper_release.h"
namespace slam {
void mean_random_tick(MeanRandomState &state) {
  auto word = [&]() {
    std::uint32_t value = 0;
    for (unsigned i = 0; i < 4; ++i) {
      state.crt_seed = state.crt_seed * 0x41c64e6du + 0x3039u;
      value = (value << 8) | ((state.crt_seed >> 16) & 0xffu);
    }
    return value;
  };
  state.field_43e7a8 += word() ^ state.field_43e834;
  state.field_43e7ac = word() ^ state.field_43e7a8;
}
void mean_upper_release(MeanObject &ball, std::uint32_t dat_base,
                        std::uint32_t field_43e7ac) {
  mean_set_layer(ball, 0, dat_base);
  ball.put16(0x22, 0);
  ball.put16(0x2a, 0);
  ball.put16(0x5c, 0);
  ball.put16(0x1c, 0);
  ball.put32(0x60, 0xaa1);
  ball.put32(0, 14 * 65536);
  ball.put32(4, 14 * 65536);
  ball.put16(0x28, 40);
  ball.put32(0x18, 0);
  ball.put16(0x58, 2);
  ball.put32(0x14, (field_43e7ac & 0x7fff) + 0x6000);
}
void mean_upper_transfer(MeanObject &ball, std::uint32_t dat_base) {
  mean_set_layer(ball, 1, dat_base);
  ball.put32(0x40, ball.i32(0x40) + 7);
  ball.put32(0x44, ball.i32(0x44) + 7);
  ball.put32(0x54, dat_base + 0xb3b36);
  ball.put16(0x22, 0);
  ball.put16(0x2a, 0);
  ball.put16(0x5c, 19);
  ball.put16(0x1c, 5);
  ball.put32(0x60, 0xaa1);
  ball.put16(0x28, 40);
  ball.put32(0, 34 * 65536);
  ball.put32(4, 391 * 65536);
  ball.put16(0x5a, 3);
  ball.put16(0x58, 3);
}
} // namespace slam
