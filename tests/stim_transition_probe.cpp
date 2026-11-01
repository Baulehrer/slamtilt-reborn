#include "audio/stim_player.h"
#include "audio/mean_music_sequencer.h"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>

int main(int argc, char **argv) {
  if (argc != 5 && argc != 6) return 1;
  try {
    const int warm = std::stoi(argv[2]);
    const int target = std::stoi(argv[3]);
    const auto ticks = std::stoul(argv[4]);
    if (ticks == 0 || ticks > 2048) return 2;
    std::vector<std::int16_t> first(882 * 2), pcm(ticks * 882 * 2);
    if (argc == 5) {
      slam::StimPlayer player(argv[1], warm, slam::TrackerMix::RetailMono);
      player.render(first.data(), 882);
      player.select_order(target);
      player.render(pcm.data(), pcm.size() / 2);
    } else {
      std::ifstream file(argv[1], std::ios::binary);
      if (!file) return 5;
      std::vector<std::uint8_t> data((std::istreambuf_iterator<char>(file)), {});
      slam::MeanMusicSequencer music({std::move(data)});
      const int service = std::stoi(argv[5]);
      auto request = [&](int order) {
        if (service == 0x90) music.request90(0, order);
        else if (service == 0x84) music.request84(0, order);
        else if (service == 0x88) music.request88(0, order);
        else throw std::runtime_error("Invalid music service");
      };
      request(warm);
      music.render(first.data(), 882);
      request(target);
      music.render(pcm.data(), pcm.size() / 2);
    }
    std::cout.write(reinterpret_cast<const char *>(pcm.data()), pcm.size() * sizeof(pcm[0]));
    return std::cout ? 0 : 3;
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 4;
  }
}
