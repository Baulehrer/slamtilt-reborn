#include "audio/native_audio.h"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
int main(int argc, char **argv) {
  try {
    if (argc != 2 && argc != 3)
      return 2;
    slam::NativeAudio audio(argv[1]);
    if (argc == 3) {
      std::ifstream input(argv[2], std::ios::binary);
      std::vector<std::uint8_t> dat((std::istreambuf_iterator<char>(input)),
                                    {});
      audio.set_mean_samples(dat);
      audio.request(0x5c, 9, 8, 0x437cf0);
      audio.request(0x5c, 6, 5, 0x437d14);
      for(auto descriptor : {0x437fe4u,0x438008u,0x43802cu,0x438050u})
        audio.request(0x5c,255,245,descriptor);
    }
    audio.set_paused(false);
    audio.pump();
    const auto initial = audio.queued_bytes();
    if (initial <= 0 || initial > 44100 * 4 / 10 + 4096)
      throw std::runtime_error("Unbounded or empty SDL queue");
    SDL_Delay(80);
    const auto consumed = audio.queued_bytes();
    if (consumed >= initial)
      throw std::runtime_error("SDL device consumed no PCM");
    audio.set_paused(true);
    const auto paused = audio.queued_bytes();
    SDL_Delay(20);
    if (audio.queued_bytes() != paused)
      throw std::runtime_error("Paused audio advances");
    audio.restart();
    if (audio.queued_bytes() != 0)
      throw std::runtime_error("Restart retained old PCM");
    audio.set_paused(false);
    audio.pump();
    if (audio.queued_bytes() <= 0)
      throw std::runtime_error("Restart produced no audio");
    std::cout << "SDL queue consumed, paused, cleared and restarted\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
