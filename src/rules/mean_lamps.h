#pragma once
#include <array>
#include <cstdint>
namespace slam {
// Original408110 four-byte command, persistent descriptorWORD+8 on/off.
// Returns true only when the original requested a pixel update.
inline bool mean_lamp_tick(std::array<std::uint8_t, 4> &s, bool &on) {
  const auto command = s[0];
  if (command == 1 || command == 2 || command == 3) {
    on = command == 1 ? true : command == 2 ? false : !on;
    s[0] = 0;
    return true;
  }
  if (command < 4 || command > 6) {
    s[0] = 0;
    return false;
  }
  if (command >= 5) {
    --s[3];
    if (s[3] == 0) {
      on = command == 5;
      s[0] = 0;
      return true;
    }
  }
  --s[2];
  if (static_cast<std::int8_t>(s[2]) > 0)
    return false;
  s[2] = s[1];
  on = !on;
  return true;
}
} // namespace slam
