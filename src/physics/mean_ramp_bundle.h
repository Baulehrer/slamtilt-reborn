#pragma once
#include "mean_step.h"

namespace slam {
// Original ramp ball-object mutations only. External rules omitted.
// Layer3 switch1/116<=Y<270, layer2 fifth-layer entry and layer4 switches.
bool mean_ramp_bundle(MeanObject &ball, std::uint16_t mask,
                      std::uint32_t dat_base,
                      std::int32_t field_services_1c = 0);
} // namespace slam
