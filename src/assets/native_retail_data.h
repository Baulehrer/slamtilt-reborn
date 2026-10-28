#pragma once
#include <cstdint>
#include <vector>
namespace slam {
// Construct a zero-based native data ABI for compiled gameplay routines.
// User graphics/audio/DAT state and startup scalars are applied separately.
std::vector<std::uint8_t> native_retail_data_image();
}
