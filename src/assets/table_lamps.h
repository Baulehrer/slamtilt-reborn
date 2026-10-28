#pragma once
#include "assets/table_definition.h"
#include "assets/windows_table.h"
#include <array>
#include <cstdint>
#include <vector>

namespace slam {
struct TableLampSprite {
  std::uint32_t descriptor;
  std::size_t dat_offset;
  int x, y, width, height;
};
struct TableLampFrames {
  std::uint32_t descriptor;
  int x, y, width, height;
  std::vector<std::uint8_t> mask;
  std::array<std::vector<std::uint8_t>, 2> rgba; // off, on
  // Original consumers 40b0b4/40b2ec write WORD descriptor+08.
  // Command bytes in metadata+04/+0c are not a visible frame index.
  unsigned frame(const std::vector<std::uint8_t> &mapped_image) const;
};
// Requires the selected table's initialized Retail image at image base400000.
// Reads returned_descriptor+08 -> metadata+10 -> lamp descriptors. No DAT scan.
std::vector<TableLampSprite>
table_lamp_sprite_profiles(const TableDefinition &,
                           const std::vector<std::uint8_t> &mapped_image,
                           std::uint32_t dat_base = 0x1100000);
// Static playfield masks and two palette-bit7 variants from the user's DAT.
// Original dynamic object links at descriptor+0c are outside these overlays.
std::vector<TableLampFrames>
load_table_lamps(const std::filesystem::path &dat, const TableDefinition &,
                 const TableImage &table,
                 const std::vector<std::uint8_t> &mapped_image,
                 std::uint32_t dat_base = 0x1100000);
} // namespace slam
