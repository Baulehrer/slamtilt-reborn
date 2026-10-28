#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>
#include <vector>
namespace slam {
// Original Game.exe hunk0:3d8e: literal runs / zero runs, then physical-dot LUT.
// This returns the logical two-plane bytes before that display-only LUT.
std::array<std::uint8_t,480> decode_amiga_dmd_frame(
 const std::vector<std::uint8_t>& source,std::size_t& cursor,std::size_t limit);
void build_amiga_dmd_frames(std::string_view table,
 const std::vector<std::uint8_t>& source,std::vector<std::uint8_t>& native);
}
