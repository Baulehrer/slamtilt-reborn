#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <stdexcept>

namespace slam {
using MeanDmdPalette = std::array<std::array<std::uint8_t, 4>, 4>;

// Demo 438a18+20, installed at40459e;40576c maps intensity bytes through
// these table-palette indices. Load RGB from the user's decoded palette.
inline MeanDmdPalette mean_dmd_original_palette(const std::uint8_t *rgba,
                                                std::size_t bytes) {
  if (!rgba || bytes < 256 * 4)
    throw std::runtime_error("Truncated Mean DMD table palette");
  constexpr std::array<unsigned, 4> indices{{0x51, 0x50, 0xdf, 0x10}};
  MeanDmdPalette result{};
  for (unsigned level = 0; level < result.size(); ++level) {
    const auto offset = indices[level] * 4;
    result[level] = {{rgba[offset], rgba[offset + 1], rgba[offset + 2], 255}};
  }
  return result;
}
} // namespace slam
