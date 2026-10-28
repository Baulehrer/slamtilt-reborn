#pragma once
#include <array>
#include <cstdint>
#include <vector>
namespace slam {
// Exact Windows Mean demo DAT bank offsets from 40f0e3/40f0f5.
// Rewraps original tracker events and shared PCM in standard STIM headers.
// Rejects incompatible layouts; does not invent sounds or event mappings.
struct MeanSoundBank {
  std::vector<std::uint8_t> stim;
  unsigned orders = 0;
  unsigned patterns = 0;
};
std::array<MeanSoundBank, 2>
mean_sound_banks(const std::vector<std::uint8_t> &dat);
MeanSoundBank table_sound_bank(const std::vector<std::uint8_t>& dat, std::size_t offset);
// Shared stripped-STIM layout; offsets are verified separately per table.
std::array<MeanSoundBank, 2>
table_sound_banks(const std::vector<std::uint8_t> &dat,
                  const std::array<std::size_t,2>& offsets);
} // namespace slam
