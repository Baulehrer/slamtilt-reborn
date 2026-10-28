#pragma once
#include "mean_step.h"
namespace slam {
// Initial rule state only:419b12 initializesfield43f3b8=0.
bool mean_switch_bundle(MeanObject &ball, std::uint16_t mask,
                        std::uint32_t dat_base, std::uint32_t &points);
} // namespace slam
