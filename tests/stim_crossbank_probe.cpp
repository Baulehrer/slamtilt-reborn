#include "audio/mean_music_sequencer.h"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <vector>

static std::vector<std::uint8_t> read_file(const char *path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) throw std::runtime_error("Cannot read STIM bank");
  return {std::istreambuf_iterator<char>(file), {}};
}

int main(int argc, char **argv) {
  if (argc < 7 || argc > 9) return 1;
  try {
    slam::MeanMusicSequencer music({read_file(argv[1]), read_file(argv[2])});
    const int warm = std::stoi(argv[3]), target = std::stoi(argv[4]);
    const auto ticks = std::stoul(argv[5]);
    const auto warm_ticks = argc == 9 ? std::stoul(argv[8]) : 1;
    const int service = std::stoi(argv[6]);
    if (!ticks || ticks > 2048 || !warm_ticks || warm_ticks > 2048) return 2;
    auto request = [&](int bank, int order) {
      if (service == 0x90) music.request90(bank, order);
      else if (service == 0x84) music.request84(bank, order);
      else if (service == 0x88) music.request88(bank, order);
      else throw std::runtime_error("Invalid music service");
    };
    std::vector<std::int16_t> warm_pcm(warm_ticks*882*2), pcm(ticks*882*2);
    if (argc >= 8 && std::string(argv[7]) == "preempt") {
      if (service == 0x90) return 2;
      music.request90(0, warm);
    } else {
      request(0, warm);
    }
    music.render(warm_pcm.data(), warm_pcm.size()/2);
    request(1, target);
    music.render(pcm.data(), pcm.size()/2);
    std::cout.write(reinterpret_cast<const char *>(pcm.data()), pcm.size()*sizeof(pcm[0]));
    return std::cout ? 0 : 3;
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 4;
  }
}
