#pragma once
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <map>
#include <string>
#include <vector>
namespace slam {
using AmigaFiles = std::map<std::string, std::vector<std::uint8_t>>;
// Read a complete standard DD retail set without executing or extracting files.
// All files have slam1/... through slam5/... keys. Game .bin/.raw/.dat assets
// additionally have merged root-relative aliases; conflicting aliases fail.
AmigaFiles read_amiga_adf_set(const std::filesystem::path& folder);
std::vector<std::uint8_t> decode_slam(const std::vector<std::uint8_t>& data,
                                    std::size_t max_output = 64 * 1024 * 1024);
}
