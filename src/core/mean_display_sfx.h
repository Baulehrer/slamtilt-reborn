#pragma once
#include "audio_request.h"
#include <cstdint>
#include <optional>

namespace slam {
// Original 40f834/41c274 shares a cursor across these sound tables.
inline std::optional<AudioRequest> mean_display_sfx(std::uint32_t callback,
    std::uint32_t tick, unsigned &cursor) {
  struct Row { unsigned tick, descriptor, period, volume; };
  static constexpr Row pit[] = {{16,0x437e10,285,48},{20,0x437e10,428,64},{24,0x437e34,856,64}};
  static constexpr Row jackpot[] = {{0,0x437e58,428,64},{24,0x437e7c,428,64},{44,0x437ea0,214,0}};
  static constexpr Row monster[] = {{12,0x437ec4,480,64},{20,0x437ee8,480,64},{72,0x437ea0,214,0}};
  static constexpr Row wrong[] = {{0,0x437f30,320,64},{20,0x437ee8,339,64},{60,0x437ea0,214,0}};
  static constexpr Row offroad[] = {{0,0x437f0c,339,64}};
  static constexpr Row mode6[] = {{0,0x437e58,428,64},{12,0x437fc0,285,64},{35,0x437fc0,285,16}};
  const Row *rows = nullptr;
  unsigned size = 0;
  switch (callback) {
  case 0x4133d4: case 0x413518: rows=pit; size=3; break;
  case 0x4131cc: case 0x4132d4: rows=jackpot; size=3; break;
  case 0x412fa8: rows=monster; size=3; break;
  case 0x411824: rows=wrong; size=3; break;
  case 0x41041c: rows=offroad; size=1; break;
  case 0x410158: rows=mode6; size=3; break;
  default: return std::nullopt;
  }
  if (tick == 0) cursor = 0;
  if (cursor >= size || rows[cursor].tick != tick) return std::nullopt;
  const auto &row = rows[cursor++];
  return AudioRequest{0x5c,-1,256,row.descriptor,row.period,row.volume};
}
} // namespace slam
