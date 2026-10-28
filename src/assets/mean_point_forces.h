#pragma once
#include "physics/mean_point_force.h"
#include <cstdint>
#include <vector>
namespace slam {
struct MeanPointForceData {
  std::vector<MeanPointForceNode> nodes;
  std::vector<std::uint16_t> lookup;
};
// Original demo descriptor from retained live snapshot; pointers are PE VAs.
MeanPointForceData load_mean_point_forces(const std::vector<std::uint8_t> &image,
                                         std::uint32_t descriptor);
} // namespace slam
