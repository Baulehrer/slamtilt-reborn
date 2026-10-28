#pragma once
#include <cstdint>
#include <string_view>
#include <vector>
namespace slam {
// Additional source objects; RC4's original bank decoder/profile remain supported.
void build_amiga_dmd_fragments_v2(std::string_view table,
 const std::vector<std::uint8_t>& bin,std::vector<std::uint8_t>& native);
}
