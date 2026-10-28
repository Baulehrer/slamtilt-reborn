#pragma once
#include "physics/mean_step.h"
namespace slam {
struct MeanPointForceNode {
  std::int16_t type = 0, field_06 = 0, field_08 = 0, field_0a = 0;
};
// Exact40a0e8..40a35b; vector order is original linked-list order.
// false means missing lookup/domain unavailable; ball then remains unchanged.
// Distance rejection exits the entire list, exactly as the original.
bool mean_point_force(MeanObject &, const std::vector<MeanPointForceNode> &,
                      const std::vector<std::uint16_t> &, bool suppressed);
} // namespace slam
