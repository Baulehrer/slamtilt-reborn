#pragma once
#include <cstdint>
namespace slam {
// Original 4186e5..418748: shared fields remain unnamed until input mapping is proved.
struct MeanMinigameInputState {
  std::uint32_t field_efe8 = 0x08000000;
  std::uint32_t field_eff8 = 0;
};
void mean_minigame_input_step(MeanMinigameInputState &state,
                              std::uint32_t shared_54,
                              std::uint32_t shared_58);
}
