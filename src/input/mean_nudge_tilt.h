#pragma once
#include <array>
#include <cstdint>
namespace slam {
// Original40554c common engine effects. Table callback+4 remains caller-owned.
struct MeanNudgeTilt {
  std::int32_t field_43d864 = 0, field_43e7a0 = 2, field_43e7d4 = 0;
  std::int32_t field_43e7c4 = 0, field_43e7c8 = 0;
  std::int32_t field_4298b8 = 0, field_4298bc = 0, field_4298c0 = 0;
  std::array<std::uint8_t, 8> ball_status{};
  unsigned count = 1;
  int key_event(); // -1=no callback,0=warning,1=tilt.
  void outer_tick() {
    if (field_43e7d4 > 0)
      --field_43e7d4;
  } // 404b43,50Hz.
};
} // namespace slam
