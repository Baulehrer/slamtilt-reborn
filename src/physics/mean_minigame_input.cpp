#include "mean_minigame_input.h"
namespace slam {
namespace {
std::uint32_t asr2(std::uint32_t v) {
  return (v >> 2) | ((v & 0x80000000u) ? 0xc0000000u : 0u);
}
}
void mean_minigame_input_step(MeanMinigameInputState &s,
                              std::uint32_t a,
                              std::uint32_t b) {
  const auto target = ((b - a) << 16) * 40u;
  s.field_eff8 += asr2(target - s.field_eff8);
  s.field_efe8 += s.field_eff8;
}
}
