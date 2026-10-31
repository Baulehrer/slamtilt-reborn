#include "audio/mean_sample_mixer.h"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>

int main(int argc, char** argv) {
  if (argc != 11) return 1;
  std::ifstream in(argv[1], std::ios::binary);
  if (!in) return 1;
  const std::vector<std::uint8_t> dat{std::istreambuf_iterator<char>(in), {}};
  std::vector<slam::SampleProfile> profiles;
  for (int i = 0; i < 2; ++i) {
    const auto base = 2 + i * 4;
    profiles.push_back({unsigned(i + 1), std::stoul(argv[base]), std::stoul(argv[base + 1]),
                        unsigned(std::stoul(argv[base + 2]))});
  }
  const auto frames = std::stoul(argv[10]);
  if (frames > 30000) return 1;
  slam::MeanSampleMixer mixer(dat, profiles);
  for (int i = 0; i < 2; ++i) mixer.request(2, 1, i + 1, 0, std::stoul(argv[5 + i * 4]));
  std::vector<std::int16_t> out(frames * 2);
  for (std::size_t at = 0; at < frames; at += 137)
    mixer.mix(out.data() + at * 2, std::min<std::size_t>(137, frames - at));
  for (std::size_t i = 0; i < frames; ++i) {
    if (out[2 * i] != out[2 * i + 1]) return 1;
    auto value = static_cast<std::uint16_t>(out[2 * i]);
    std::cout.put(static_cast<char>(value));
    std::cout.put(static_cast<char>(value >> 8));
  }
  return std::cout ? 0 : 1;
}
