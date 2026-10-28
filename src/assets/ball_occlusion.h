#pragma once
#include "assets/ball_mask.h"
#include <cstddef>
#include <cstdint>
#include <vector>

namespace slam {
// Demo 40abc8..40aceb: object+54 is a 320-bit-wide preservation bitmap,
// including any signed displacement already present in that object pointer.
// left/top are the original signed drawing words at object+10/+12.
BallMask windows_ball_occlusion(const BallMask &outline,
                                const std::vector<std::uint8_t> &table_dat,
                                std::size_t bitmap_offset, int left, int top);
} // namespace slam
