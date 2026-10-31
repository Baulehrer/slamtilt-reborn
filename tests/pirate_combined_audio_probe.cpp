#include "audio/mean_sample_mixer.h"
#include "audio/pirate_sound_assets.h"
#include "audio/stim_player.h"
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>

int main(int argc, char **argv) {
  if (argc != 4) return 2;
  std::ifstream file(argv[2], std::ios::binary);
  if (!file) return 2;
  std::vector<std::uint8_t> dat{std::istreambuf_iterator<char>(file), {}};
  constexpr std::size_t frames = 882;
  std::vector<std::int16_t> pcm(frames * 2);
  if (std::string(argv[3]) == "original-input") {
    std::cin.read(reinterpret_cast<char *>(pcm.data()), pcm.size() * sizeof(pcm[0]));
    if (std::cin.gcount() != static_cast<std::streamsize>(pcm.size() * sizeof(pcm[0]))) return 2;
  } else if (std::string(argv[3]) == "native-tracker") {
    slam::StimPlayer player(argv[1], 34, slam::TrackerMix::RetailMono);
    player.render(pcm.data(), frames);
  } else return 2;
  slam::MeanSampleMixer mixer(dat, slam::pirate_sample_profiles());
  mixer.request(2, 1, 0x464f60);
  mixer.request(2, 1, 0x464f84);
  mixer.mix(pcm.data(), frames);
  std::cout.write(reinterpret_cast<const char *>(pcm.data()), pcm.size() * sizeof(pcm[0]));
  return std::cout ? 0 : 1;
}
