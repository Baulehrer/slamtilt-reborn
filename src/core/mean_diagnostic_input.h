#pragma once
#include <array>
#include <cstdint>
namespace slam {
// Deterministic diagnostic key schedule, not gameplay logic or physics.
// Mirrors the retained native random-input fixtures; user seed initializes
// seed+1.
class MeanDiagnosticInput {
public:
  explicit MeanDiagnosticInput(std::uint32_t seed) : state_(seed + 1) {}
  std::array<bool, 2> next() {
    for (unsigned side = 0; side < 2; ++side) {
      if (!wait_[side]) {
        pressed_[side] = !pressed_[side];
        state_ ^= state_ << 13;
        state_ ^= state_ >> 17;
        state_ ^= state_ << 5;
        wait_[side] = 10 + state_ % 191;
      }
      --wait_[side];
    }
    return pressed_;
  }

private:
  std::uint32_t state_;
  std::array<unsigned, 2> wait_{};
  std::array<bool, 2> pressed_{};
};
// Native diagnostic shot schedule, selected by bounded flipper-timing trials.
// Only SDL-equivalent key actions; does not modify ball or rule state.
inline std::array<bool, 2> mean_finite_shot_input(unsigned step, int ball_y,
                                                  unsigned phase = 4) {
  const bool below = ball_y >= 470;
  const bool left = ((step + phase) / 16) % 2;
  return {below && left, below && !left};
}
// Finite first-minigame diagnostic route: fixed SDL-equivalent key prefix,
// then lower-table timing. Production physics/rules are not modified.
inline std::array<bool, 2> mean_first_minigame_input(unsigned step, int ball_y) {
  if (step < 11612) {
    const bool left = (step / 81) % 2;
    return {left, !left};
  }
  return mean_finite_shot_input(step, ball_y, 2);
}
// Recorded natural Cliff route: only keyboard actions; field names retain offsets.
inline std::array<bool,3> mean_cliff_input(unsigned step,int mode,unsigned field_3a6,
                                          unsigned field_39e,unsigned field_3a8) {
  if(mode==4 && field_3a6==0)
    return {false,false,field_39e==3 && (field_3a8&127)==64};
  const bool left=(step/51)%2;
  return {left,!left,false};
}
} // namespace slam
