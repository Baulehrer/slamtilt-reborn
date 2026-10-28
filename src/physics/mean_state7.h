#pragma once
#include "physics/mean_step.h"
namespace slam {
// Original408a18 12-byte directory record; signed WORDs retain offset names.
struct MeanState7Record {
  std::array<std::int16_t, 6> words{};
};
// Original417148 before408a18. Returns true on state7->held state3 transition.
// Slot globals are projected by caller:438b58=15,438b90=100,438b50/54=0.
bool mean_state7_boundary(MeanObject &ball, std::uint32_t dat_base);
// Original408a18; no wall/point forces while state7. False for invalid
// divisor/LUT.
bool mean_state7_step(MeanObject &ball, const MeanState7Record &record,
                      const MeanLookup &lookup);
} // namespace slam
