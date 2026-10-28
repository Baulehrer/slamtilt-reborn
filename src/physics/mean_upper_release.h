#pragma once
#include "mean_step.h"
namespace slam {
// Original406840/422f40 state. Startup supplies original seed/field43e834.
struct MeanRandomState {
  std::uint32_t crt_seed = 1;
  std::uint32_t field_43e7a8 = 0;
  std::uint32_t field_43e834 = 0;
  std::uint32_t field_43e7ac = 0;
};
// Called before each original5ms gameplay tick, including paused ticks.
void mean_random_tick(MeanRandomState &state);
// Exact416be4 ball writes only. Caller owns release preconditions/sound event.
void mean_upper_release(MeanObject &ball, std::uint32_t dat_base,
                        std::uint32_t field_43e7ac);
// Exact417086..41712e ball writes; caller owns slot74/slot50 mutations.
void mean_upper_transfer(MeanObject &ball, std::uint32_t dat_base);
} // namespace slam
