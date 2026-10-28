#pragma once
#include <cstdint>
namespace slam {
// Windows Full 4083a9..4083cb. Call after turn rotation and selection of the
// next player's record. Demo407808 has no corresponding finite boundary.
// field_454aa4 remains unnamed: zero selects threshold4, nonzero threshold6.
bool mean_game_end_required(std::uint16_t field_player_0e,
                            std::uint32_t field_454aa4);
} // namespace slam
