#pragma once
#include <cstdint>
#include <vector>
namespace slam {
// Fill the four Mean contact frame slots from decoded original Amiga assets.
void build_amiga_mean_contact_frames(const std::vector<std::uint8_t>& raw,
                                    const std::vector<std::uint8_t>& bin,
                                    std::vector<std::uint8_t>& native);
}
