#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace slam {
// Original demo callback object bytes. Unknown fields retain original offsets.
struct MeanObject {
  std::array<std::uint8_t, 0x64> bytes{};
  std::uint16_t u16(std::size_t offset) const;
  std::int32_t i32(std::size_t offset) const;
  void put16(std::size_t offset, std::uint16_t value);
  void put32(std::size_t offset, std::int32_t value);
};
struct MeanLookup {
  // Exact memory backing demo global0x43e764; caller supplies original data.
  std::vector<std::uint8_t> field_43e764;
  std::vector<std::uint8_t> field_43e744;
  std::vector<std::uint8_t> field_43e728;
};
struct MeanCollisionBits {
  // Original Mean DAT owns the bytes; no asset copying into the repository.
  std::vector<std::uint8_t> dat;
  std::size_t hit_offset = 0x9ba36, stride = 0x6040;
  unsigned extra_planes = 3;
  bool sample(std::int32_t x, std::int32_t y, unsigned plane = 0) const;
  std::uint16_t extra_plane_mask(std::int32_t x, std::int32_t y) const;
  // Original byte addressing, including crossing row/plane boundaries.
  bool sample_linear(std::int32_t x,std::int32_t y,unsigned plane=0) const;
  std::uint16_t extra_plane_mask_linear(std::int32_t x,std::int32_t y) const;
};
// Single-player part4077bb..4077e4; bonus/DMD presentation is external.
void mean_advance_ball(std::uint16_t &number, std::uint16_t &extra);
// Geometry descriptors from the verified Mean profile.
void mean_set_layer(MeanObject &ball, unsigned layer, std::uint32_t dat_base);
// Scalar reset only; retained records require the complete initializer below.
void mean_reset_ball(MeanObject &ball);
void mean_initialize_ball(MeanObject &ball, std::uint32_t dat_base);
// Exact ball mutation in Mean frame callback41ac30; notification is external.
bool mean_launch_kick(MeanObject &ball, bool pressed);
// 41ce03..41d0fa lower switch4: ball unchanged in initial mode; rules external.
bool mean_lower_switch(const MeanObject &ball);
// Base score request41ce23/41cec7/41cf5d/41cff2/41d07c; mode bonuses external.
std::uint32_t mean_lower_switch_points(const MeanObject &ball);
// Exact default integration branch0x40a022..0x40a0dd, after point forces.
void mean_integrate(MeanObject &ball);
// Exact0x409e18; directed mode requires the original atan lookup.
// Returns false for unavailable lookup or original divide-by-zero direction.
bool mean_free_velocity(MeanObject &ball, const MeanLookup &lookup);
// Exact ordinary Mean response409bec and callback41e00c materials0..5 (human
// mode; base score only). Excludes separation409d78; caller supplies original
// moving-surface offsets. Unsupported callback/material returns false without
// modifying the object.
struct MeanMaterialBundleState;
struct MeanContactEvent {
  bool material5_rules = false;
  unsigned sample_descriptor = 0;
  std::uint32_t points = 0;
  std::uint32_t field_438b_state = 0;
};
bool mean_wall_response(MeanObject &ball, const MeanLookup &lookup,
                        std::int32_t field_43e724, std::int32_t field_43e564,
                        MeanContactEvent *event = nullptr,
                        MeanMaterialBundleState *material_state = nullptr);
// Exact bounded separation loop0x409d78, with original supplied direction.
unsigned mean_separate(MeanObject &ball, const MeanCollisionBits &bits,
                       std::int16_t table_43e744_value,
                       std::int16_t table_43e764_value,
                       std::int32_t field_43e71c, std::int32_t field_43e410);
} // namespace slam
