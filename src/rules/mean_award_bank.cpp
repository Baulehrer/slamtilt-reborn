#include "mean_award_bank.h"
#include <algorithm>
namespace slam {
bool mean_award_bank_target(std::int32_t x, std::int32_t mode,
                            std::array<std::uint8_t, 5> &flags,
                            std::int16_t &timer, std::uint32_t &value,
                            MeanLampCommands &commands) {
  if (mode > 4 || timer >= 0)
    return false;
  unsigned index = x < 23 * 65536    ? 0
                   : x < 45 * 65536  ? 1
                   : x < 160 * 65536 ? 2
                   : x < 275 * 65536 ? 3
                                     : 4;
  flags[index] = 1;
  commands[33 + index] = {5, 1, 0, 25};
  if (!std::all_of(flags.begin(), flags.end(), [](auto v) { return v == 1; }))
    return false;
  flags.fill(0);
  timer = 6000;
  value = 60000000;
  for (unsigned i = 0; i < 5; ++i)
    commands[33 + i] = {6, 2, std::uint8_t(i % 2 + 1), 25};
  commands[62] = {4, 6, 1, 0};
  return true;
}
std::uint32_t mean_award_bank_tick(std::int16_t &timer, std::uint32_t &value,
                                   MeanLampCommands &commands) {
  timer = static_cast<std::int16_t>(static_cast<std::uint16_t>(timer) - 1);
  if (timer < 0) {
    commands[62][0] = 2;
    return 0x410504;
  }
  value = std::max(10000000u, static_cast<std::uint32_t>(timer / 4) * 40000u);
  return timer == 3000 ? 0x41086c : 0;
}
} // namespace slam

namespace slam {
bool mean_side_extra_ball(std::int32_t x, std::int16_t &field_1fc,
                          std::uint16_t &player_10,
                          MeanLampCommands &commands) {
  if (!((x < 23 * 65536 && field_1fc == 1) ||
        (x >= 275 * 65536 && field_1fc == 2)))
    return false;
  field_1fc = 0;
  player_10 = static_cast<std::uint16_t>(player_10 + 1);
  commands[23][0] = 1;
  commands[60][0] = commands[61][0] = 2;
  return true;
}
} // namespace slam
