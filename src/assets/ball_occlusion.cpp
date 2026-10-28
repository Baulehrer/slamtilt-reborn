#include "assets/ball_occlusion.h"
#include <stdexcept>

namespace slam {
BallMask windows_ball_occlusion(const BallMask &outline,
                                const std::vector<std::uint8_t> &table_dat,
                                std::size_t bitmap_offset, int left, int top) {
  if (left < 0 || left >= 304 || top < 0 || top >= 600)
    throw std::out_of_range(
        "Ball occlusion drawing position outside original bounds");
  const auto relative = static_cast<std::size_t>(top) * 40 + left / 8;
  // The original performs four-byte reads, including at the final bitmap edge.
  constexpr std::size_t tail = (BallMask::height - 1) * 40 + 4;
  if (bitmap_offset > table_dat.size() ||
      relative > table_dat.size() - bitmap_offset ||
      tail > table_dat.size() - bitmap_offset - relative)
    throw std::out_of_range("Truncated original ball occlusion bitmap");
  BallMask result = outline;
  auto offset = bitmap_offset + relative;
  for (int y = 0; y < BallMask::height; ++y, offset += 40) {
    const auto bits = (std::uint32_t(table_dat[offset]) << 24 |
                       std::uint32_t(table_dat[offset + 1]) << 16 |
                       std::uint32_t(table_dat[offset + 2]) << 8 |
                       std::uint32_t(table_dat[offset + 3])) >>
                      (16 - (left & 7));
    for (int x = 0; x < BallMask::width; ++x)
      if (bits & (1u << (15 - x)))
        result.preserve_background[y * BallMask::width + x] = 255;
  }
  return result;
}
} // namespace slam
