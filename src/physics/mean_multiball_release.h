#pragma once
#include "mean_step.h"
namespace slam {
struct MeanMultiballReleaseState {
  std::array<std::int32_t, 3> slot{{-1, 0, 0}}, slot50{{0, 0, 0}};
  std::int32_t mode = 5;
  std::int16_t selected = 4, bits = 0, field_43f3a6 = 0, field_43f382 = 0;
  std::int32_t field_43f064 = 0;
};
void mean_multiball_guide(MeanObject &);
void mean_multiball_release(MeanObject &, MeanMultiballReleaseState &,
                            std::uint32_t, bool tilt = false, unsigned *sample_count = nullptr);
} // namespace slam
