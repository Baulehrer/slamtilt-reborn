#include "mean_sound_assets.h"
#include <algorithm>
#include <stdexcept>
namespace slam {
namespace {
unsigned be16(const std::vector<std::uint8_t> &d, std::size_t p) {
  if (p + 2 > d.size())
    throw std::runtime_error("Truncated Mean audio data");
  return (unsigned(d[p]) << 8) | d[p + 1];
}
unsigned be32(const std::vector<std::uint8_t> &d, std::size_t p) {
  return (be16(d, p) << 16) | be16(d, p + 2);
}
void put32(std::vector<std::uint8_t> &d, std::size_t p, unsigned value) {
  for (unsigned n = 0; n < 4; ++n)
    d.at(p + n) = std::uint8_t(value >> (24 - 8 * n));
}
MeanSoundBank bank(const std::vector<std::uint8_t> &d, std::size_t base) {
  const auto samples = be16(d, base + 4);
  MeanSoundBank result;
  result.orders = be16(d, base + 6);
  result.patterns = be16(d, base + 8);
  if (samples != 31 || !result.orders || result.orders > 128 ||
      !result.patterns || result.patterns > 64 || base + 394 > d.size())
    throw std::runtime_error("Unsupported Mean audio bank layout");
  for (unsigned n = 0; n < result.orders; ++n)
    if (d[base + 10 + n] >= result.patterns)
      throw std::runtime_error("Invalid Mean audio order");
  auto end = base + 394;
  for (unsigned n = 0; n < result.patterns; ++n) {
    const auto pattern = base + be32(d, base + 138 + n * 4);
    auto cursor = pattern + 8;
    for (unsigned channel = 0; channel < 4; ++channel) {
      if (pattern + be16(d, pattern + channel * 2) != cursor)
        throw std::runtime_error("Unsupported Mean audio channel layout");
      unsigned row = 0;
      while (row < 64) {
        if (cursor >= d.size())
          throw std::runtime_error("Truncated Mean audio pattern");
        const auto first = d[cursor++];
        if (first & 128)
          row += (first & 127) + 1;
        else {
          cursor += 2;
          ++row;
        }
      }
      if (row != 64 || cursor > d.size())
        throw std::runtime_error("Invalid Mean audio pattern");
    }
    end = std::max(end, cursor);
  }
  auto &out = result.stim;
  out.resize(12);
  out[0] = 'S';
  out[1] = 'T';
  out[2] = 'I';
  out[3] = 'M';
  out.insert(out.end(), d.begin() + base, d.begin() + end);
  const auto sample_address = out.size();
  put32(out, 4, unsigned(sample_address));
  out.resize(out.size() + samples * 4);
  for (unsigned n = 0; n < samples; ++n) {
    const auto sample = be32(d, n * 4);
    const std::size_t size = 8 + be16(d, sample) * 2;
    if (std::size_t(sample) + size > d.size())
      throw std::runtime_error("Truncated Mean audio sample");
    put32(out, sample_address + n * 4, unsigned(out.size() - sample_address));
    out.insert(out.end(), d.begin() + sample, d.begin() + sample + size);
  }
  return result;
}
} // namespace
MeanSoundBank table_sound_bank(const std::vector<std::uint8_t>& dat, std::size_t offset) { return bank(dat,offset); }
std::array<MeanSoundBank, 2>
mean_sound_banks(const std::vector<std::uint8_t> &dat) {
  return table_sound_banks(dat,{0x5c2d2,0x61590});
}
std::array<MeanSoundBank, 2>
table_sound_banks(const std::vector<std::uint8_t> &dat,
                  const std::array<std::size_t,2>& offsets) {
  return {bank(dat, offsets[0]),bank(dat, offsets[1])};
}
} // namespace slam
