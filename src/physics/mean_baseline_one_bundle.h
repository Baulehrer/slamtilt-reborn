#pragma once
#include "mean_step.h"
namespace slam {
// Missing part41de71..41df37 of baseline switch1. Returns false outside
// x>230,y>=225. field_43f3b8 is an unclassified original table gate.
bool mean_baseline_one_bundle(MeanObject &ball, std::uint32_t dat_base,
                              std::uint16_t field_43f3b8 = 0);
} // namespace slam
