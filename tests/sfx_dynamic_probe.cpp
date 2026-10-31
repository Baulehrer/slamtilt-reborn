#include "audio/mean_sample_mixer.h"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>

int main(int argc, char **argv) {
  if (argc != 7) return 1;
  std::ifstream input(argv[1], std::ios::binary);
  if (!input) return 1;
  const std::vector<std::uint8_t> dat{std::istreambuf_iterator<char>(input), {}};
  const auto offset = std::stoul(argv[2]), length = std::stoul(argv[3]);
  const auto period = std::stoul(argv[4]), volume = std::stoul(argv[5]);
  const auto frames = std::stoul(argv[6]);
  if (period == 0 || volume > 64 || frames > 30000) return 1;
  slam::MeanSampleMixer mixer(dat, {{1, offset, length, 226}});
  mixer.request(-1, 1, 1, period, volume);
  std::vector<std::int16_t> out(frames * 2);
  for (std::size_t at = 0; at < frames; at += 137)
    mixer.mix(out.data() + at * 2, std::min<std::size_t>(137, frames - at));
  for (std::size_t i = 0; i < frames; ++i) {
    if (out[2*i] != out[2*i+1]) return 1;
    const auto value = static_cast<std::uint16_t>(out[2*i]);
    std::cout.put(static_cast<char>(value));
    std::cout.put(static_cast<char>(value >> 8));
  }
  return std::cout ? 0 : 1;
}
