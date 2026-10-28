#pragma once
#include <cstdint>
namespace slam {
struct MeanDisplayAudioCommand {
  int service = 0, bank = 0, order = 0;
};
// Actual405f98 admitted display request audio side effects. active_flags is
// Original4297cc, not a display flag. Caller owns service88/8c queue semantics.
inline MeanDisplayAudioCommand mean_display_audio(std::int32_t old780,
    std::int32_t stack0, std::int32_t stack1, bool admitted,
    std::uint32_t active_flags) {
  if (!admitted) return {};
  if (stack0 >= 0) return {0x88, stack1, stack0};
  if (old780 == 4 && (active_flags & 2)) return {0x8c, 0, 0};
  return {};
}
}
