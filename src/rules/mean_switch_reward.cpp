#include "mean_switch_reward.h"
namespace slam {
MeanSwitchRewardEvent mean_switch_reward(MeanBallResetState &s) {
  auto &f = s.fields;
  auto word = [&](unsigned o) { return std::uint16_t(f[o] | (f[o + 1] << 8)); };
  auto set = [&](unsigned o, std::uint32_t v, unsigned n = 2) {
    for (unsigned i = 0; i < n; ++i)
      f[o + i] = v >> (i * 8);
  };
  auto command = [&](unsigned i, std::uint8_t a, std::uint8_t b, std::uint8_t c,
                     std::uint8_t d) {
    unsigned o = 0x208 + i * 4;
    f[o] = a;
    f[o + 1] = b;
    f[o + 2] = c;
    f[o + 3] = d;
  };
  MeanSwitchRewardEvent e;
  set(0x35c, 0);
  if (!word(0x358)) {
    auto v = static_cast<std::int16_t>(word(0x206));
    if (v < 7)
      set(0x206, word(0x206) + 1);
    e.score = static_cast<std::uint32_t>(v) * 10000000u + 20000000u;
    set(0x050, e.score, 4);
    return e;
  }
  switch (word(0x362)) {
  case 0:
    for (unsigned i = 0; i < 5; ++i)
      f[0x1ec + i] = 0;
    set(0x37a, 6000);
    set(0x054, 60000000, 4);
    for (unsigned i = 0; i < 5; ++i)
      command(33 + i, 6, 2, i % 2 + 1, 25);
    command(62, 4, 6, 1, 0);
    e.service84 = true;
    break;
  case 1:
    command(59, 4, 6, 1, 0);
    set(0x1fa, word(0x1fa) + 1);
    break;
  case 2:
    set(0x394, 0xffff);
    command(29, 4, 6, 1, 0);
    break;
  case 3:
    set(0x3ba, 2);
    set(0x3bc, 1);
    set(0x392, 0xffff);
    f[0x218] = f[0x21c] = f[0x224] = f[0x22c] = 2;
    command(6, 4, 6, 1, 0);
    command(8, 4, 6, 1, 0);
    command(10, 4, 6, 5, 0);
    command(11, 4, 6, 3, 0);
    break;
  case 4:
    for (unsigned i = 0; i < 4; ++i)
      f[0x1d4 + i] = f[0x060 + i] = 0;
    set(0x398, 1500);
    set(0x3ac, 0);
    set(0x1d8, 4);
    s.field_438af8 = 0;
    command(0, 4, 4, 1, 0);
    command(1, 4, 4, 3, 0);
    command(2, 4, 4, 5, 0);
    command(3, 4, 4, 7, 0);
    break;
  case 5: {
    const auto index = static_cast<std::int16_t>(word(0x1fe));
    set(0x204, 0);
    for (unsigned i = 52; i <= 55; ++i)
      f[0x208 + i * 4] = 2;
    command(51, 4, 6, 1, 0);
    auto next = static_cast<std::int16_t>(std::uint16_t(word(0x1fe) + 1));
    set(0x1fe, next >= 3 ? 0 : static_cast<std::uint16_t>(next));
    if (index == 0) {
      command(57, 4, 6, 1, 0);
      set(0x200, 0xffff);
    }
    if (index == 1) {
      command(58, 4, 6, 1, 0);
      set(0x202, 0xffff);
    }
    if (index == 2) {
      command(59, 4, 6, 1, 0);
      set(0x1fa, word(0x1fa) + 1);
    }
    break;
  }
  case 6: {
    auto count = static_cast<std::int16_t>(word(0x1f2));
    if (count >= 5)
      break;
    // Valid original progress indices0..4; reject corrupt negative geometry.
    if (count < 0)
      break;
    command(39 + count, 5, 1, 0, 32);
    set(0x1f2, count + 1);
    if (count + 1 == 5)
      command(44, 4, 4, 1, 0);
    break;
  }
  }
  return e;
}
} // namespace slam
