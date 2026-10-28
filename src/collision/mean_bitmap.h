#pragma once
#include <cstdint>
#include <filesystem>
#include <vector>
namespace slam {
// Original demo consumer0x408e70: bitmap+40*y+x/8, MSB first.
std::vector<std::uint8_t>
load_mean_collision_overlay(const std::filesystem::path &dat);
} // namespace slam
