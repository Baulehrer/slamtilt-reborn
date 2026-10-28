#include "mean_flipper_actions.h"
#include <algorithm>
namespace slam {
std::uint32_t mean_flipper_actions(MeanBallResetState &s, std::int32_t mode,
                                   std::int32_t edge, bool right,
                                   std::int32_t service_1c) {
  if (service_1c || edge < 0)
    return 0;
  auto &f = s.fields;
  auto word = [&](unsigned o) { return std::uint16_t(f[o] | (f[o + 1] << 8)); };
  auto set = [&](unsigned o, std::uint16_t v) {
    f[o] = v;
    f[o + 1] = v >> 8;
  };
  std::rotate(f.begin() + 0x1e8, f.begin() + 0x1e9, f.begin() + 0x1eb);
  std::rotate(f.begin() + 0x1ec, f.begin() + 0x1ed, f.begin() + 0x1f1);
  for (unsigned i = 0; i < 3; ++i)
    f[0x280 + i * 4] = std::uint8_t(2 - f[0x1e8 + i]);
  for (unsigned i = 0; i < 5; ++i)
    f[0x28c + i * 4] = std::uint8_t(2 - f[0x1ec + i]);
  if (static_cast<std::int16_t>(word(0x1fc)) > 0) {
    f[0x1fc] ^= 3;
    f[0x2f8] = f[0x2fc] = 2;
    const auto index = static_cast<std::int16_t>(word(0x1fc));
    if (index >= 0 && index < 4) {
      const unsigned o = 0x208 + (59 + index) * 4;
      f[o] = 4;
      f[o + 1] = 5;
      f[o + 2] = 0;
      f[o + 3] = 0;
    }
  }
  if (right && mode == 1 && word(0x35c) == 0) {
    set(0x358, word(0x358) ^ 0x7fff);
    set(0x360, 0xffff);
  }
  return right ? 0x437d5c : 0x437d38;
}
} // namespace slam
