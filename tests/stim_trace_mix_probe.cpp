#include "audio/mean_sample_mixer.h"
#include "audio/stim_player.h"
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <vector>

int main(int argc, char **argv) {
  if (argc != 7) {
    std::cerr << "Usage: stim_trace_mix_probe STIM DAT OFFSET LENGTH ORDER PRE_FRAMES\n";
    return 1;
  }
  try {
    std::ifstream file(argv[2], std::ios::binary);
    if (!file) throw std::runtime_error("Cannot read DAT");
    std::vector<std::uint8_t> data{std::istreambuf_iterator<char>(file), {}};
    const auto offset = std::stoul(argv[3]);
    const auto length = std::stoul(argv[4]);
    const auto order = std::stoi(argv[5]);
    const auto pre_frames = std::stoul(argv[6]);
    if (pre_frames > 44100 || !length)
      throw std::runtime_error("Invalid sample length or pre-roll");
    slam::StimPlayer player(argv[1], order, slam::TrackerMix::RetailMono);
    slam::MeanSampleMixer mixer(data, {{1, offset, length, 226}});
    mixer.request(2, 1, 1, 226, 64);
    std::vector<std::int16_t> prelude(pre_frames * 2), output(2646 * 2);
    mixer.mix(prelude.data(), pre_frames);
    player.render(output.data(), 2646);
    mixer.mix(output.data(), 2646);
    std::cout.write(reinterpret_cast<const char *>(output.data()), output.size() * sizeof(output[0]));
    return std::cout ? 0 : 2;
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 3;
  }
}
