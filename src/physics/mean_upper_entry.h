#pragma once
#include "mean_upper_capture.h"
namespace slam {
// Exact upper capture branch41d954..41d9de. Caller reports41db1c blockedball.
bool mean_upper_entry(MeanObject &ball, MeanUpperCaptureState &state,
                      std::int32_t field_services_1c, bool blocked);
} // namespace slam
