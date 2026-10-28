#pragma once
#include <cstdint>
#include <vector>

namespace slam {
// Construct the shared integer math tables used by the compiled native engine.
// Addresses identify the established Retail data ABI, not executable code.
void initialize_native_math(std::vector<std::uint8_t>& image);
}
