#pragma once
#include "physics/flipper_lift.h"
#include <array>
#include <cstdint>
#include <vector>
namespace slam {
// Original graphics+0c/10/14 parameter records, NOT graphics+04 motion paths.
struct TableFlipperParameters {
  std::array<std::array<std::uint8_t, 12>, 3>
      records{}; // left, right, optional upper
  std::uint16_t field_1c = 0;
};
TableFlipperParameters
load_table_flipper_parameters(const std::vector<std::uint8_t> &mapped_image,
                              std::uint32_t graphics_address);
// Applies the original 405079..405153 parameter-copy layout to the existing
// Demo bounded lift. Requires its initialized engine globals and trig lookup.
void configure_table_flippers(FlipperLift &, const TableFlipperParameters &);
// Original per-step edge protocol: +1 press, -1 release, 0 unchanged.
void step_table_flipper_pose(FlipperLift &, std::int32_t left_edge,
                             std::int32_t right_edge);
// Requires a prepared Retail image, runtime parameters and explicit lookup
// context. Returns the original contact result; zero also applies the original
// response.
std::uint32_t retail_table_flipper_contact(FlipperLift &, unsigned index);
} // namespace slam
