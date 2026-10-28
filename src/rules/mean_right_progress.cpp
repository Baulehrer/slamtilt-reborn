#include "mean_right_progress.h"
#include <cstring>
namespace slam {
MeanRightProgressEvent mean_right_progress(MeanBallResetState &s,
    const std::function<void(MeanBallResetState &)> &common_reward) {
  MeanRightProgressEvent e;
  auto &f = s.fields;
  auto w = [&](unsigned o) { return std::uint16_t(f[o] | (f[o + 1] << 8)); };
  auto put = [&](unsigned o, std::uint32_t v, unsigned n = 2) {
    for (unsigned i = 0; i < n; ++i)
      f[o + i] = v >> (8 * i);
  };
  auto command = [&](unsigned o, unsigned a, unsigned b, unsigned c,
                     unsigned d) {
    f[o] = a;
    f[o + 1] = b;
    f[o + 2] = c;
    f[o + 3] = d;
  };
  if (static_cast<std::int16_t>(w(0x3b0)) >= 0) {
    auto count = std::uint16_t(w(0x39a) + 1);
    put(0x39a, count);
    e.score = std::uint32_t(static_cast<std::int16_t>(count)) * 5000000u;
    put(0x050, e.score, 4);
    put(0x038, 0, 4);
    e.callback = 0x411544;
  }
  put(0x3b0, 400);
  command(0x258, 4, 4, 1, 0);
  // Actual41cbc4 sits between combo writes and the new-mode progression test.
  if (common_reward) common_reward(s);
  if (s.table_mode > 4)
    return e;
  auto old = static_cast<std::int16_t>(w(0x3bc));
  if (old < 0 || old > 2)
    return e; // Invalid originallampindex domain, no fabricated commands.
  auto next = std::uint16_t(old + 1);
  put(0x3bc, next);
  f[0x224 + old * 4] = 2;
  if (static_cast<std::int16_t>(next) >= 3) {
    next = 0;
    put(0x3bc, 0);
  }
  command(0x224 + next * 4, 4, 6, 1, 0);
  if (next == 2) {
    put(0x3a2, 0xffff);
    e.reset_right_gate = true;
    command(0x238, 4, 6, 3, 0);
    command(0x254, 4, 6, 5, 0);
  }
  if (next == 0) {
    put(0x3a2, 0);
    f[0x238] = f[0x254] = 2;
    e.reset_right_gate = true;
    auto count = static_cast<std::int16_t>(w(0x1f2));
    if (count >= 0 && count < 5) {
      put(0x1f2, count + 1);
      command(0x2a4 + count * 4, 5, 1, 0, 32);
      if (count + 1 == 5)
        command(0x2b8, 4, 4, 1, 0);
    }
    put(0x038, 0, 4);
    e.callback = 0x412df0;
  }
  return e;
}
} // namespace slam
