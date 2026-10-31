#include "audio/stim_player.h"
#include <algorithm>
#include <iostream>
#include <vector>
int main(int argc, char **argv) {
  try {
    if (argc < 4 || argc > 7 || (argc == 7 && std::string(argv[6]) != "retail"))
      return 2;
    slam::StimPlayer player(argv[1], argc >= 6 ? std::stoi(argv[5]) : 0,
                            argc == 7 ? slam::TrackerMix::RetailMono
                                      : slam::TrackerMix::Default);
    const auto frames = std::stoul(argv[2]), chunk = std::stoul(argv[3]);
    if (frames > 44100 * 60 || chunk == 0)
      return 2;
    std::vector<std::int16_t> pcm(frames * 2);
    auto render = [&] {
      for (std::size_t i = 0; i < frames; i += chunk)
        player.render(pcm.data() + i * 2, std::min(chunk, frames - i));
    };
    render();
    if (argc >= 5 && std::string(argv[4]) == "restart") {
      const auto first = pcm;
      player.restart();
      render();
      if (first != pcm)
        throw std::runtime_error("Music restart changed PCM");
    }
    std::cout.write(reinterpret_cast<const char *>(pcm.data()), pcm.size() * 2);
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
