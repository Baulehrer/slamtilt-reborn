#pragma once
#include "assets/table_profile.h"
#include "physics/mean_step.h"
namespace slam {
// Actual engine+4 contact directory: 438ea0 / 4397d0 / 439994.
// Addresses are Retail globals; layer-zero pointer values come from
// initializer.
struct PirateContactState {
  std::int32_t field_services_1c = 0;
  std::uint32_t layer0_hit = 0, layer0_normal = 0, layer0_render = 0;
  std::uint32_t layer0_stride = 0, layer0_planes = 0;
};
// Exact 40a884 transform plus supported Pirate callbacks; excludes separation.
// Rule-bearing cases layer0 material5/6, human-mode3/4 and layer1 material1
// return false without mutation, so callers must not silently treat them as
// walls.
bool pirate_contact(MeanObject &, const MeanLookup &,
                    const PirateContactState &, std::int32_t offset_x = 0,
                    std::int32_t offset_y = 0);
} // namespace slam
namespace slam {
// Compose the verified Pirate transform with shared original separation.
// bits must describe the current (possibly transferred) ball geometry.
bool pirate_wall_contact(MeanObject &, const MeanLookup &,
                         const PirateContactState &, MeanCollisionBits &,
                         const TableProfile &, std::uint32_t dat_base);
} // namespace slam
