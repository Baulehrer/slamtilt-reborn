#pragma once
#include "assets/mean_flippers.h"
#include "assets/table_definition.h"
#include <cstddef>
#include <cstdint>
#include <vector>

namespace slam {
struct TableFlipperSprite {
  std::uint32_t descriptor;
  std::size_t dat_offset;
  int x, y, width, height;
  unsigned frame_count;
  unsigned geometry_layer;
};
// Order matches native flipper pose indices: left, right, optional upper.
// These are supported Retail descriptor/initializer records, not a DAT scan.
std::vector<TableFlipperSprite>
table_flipper_sprite_profiles(const TableDefinition &);
// Uses the active table palette, index<=1 transparency, and the original
// table-foreground bitmap. Does not modify pristine DAT sprite pixels.
std::vector<FlipperFrames>
load_table_flippers(const std::filesystem::path &dat,
                    const TableDefinition &, const TableImage &table);
// Original40b518: frame-indexed source AND NOT parent lamp mask. Alpha is
// retained from the pristine sprite/foreground decoder, before palette masking.
std::vector<std::uint8_t> compose_table_flipper(
    const TableFlipperSprite &, const FlipperFrames &, unsigned frame,
    const TableImage &, const std::vector<std::uint8_t> &mapped_image,
    const std::vector<std::uint8_t> &current_dat,
    std::uint32_t dat_base = 0x1100000);
} // namespace slam
