#include "audio/mean_sound_assets.h"
#include "audio/native_audio.h"
#include <fstream>
#include <iostream>
int main(int argc, char **argv) {
  if (argc != 2)
    return 2;
  try {
    std::ifstream f(argv[1], std::ios::binary);
    std::vector<std::uint8_t> dat{std::istreambuf_iterator<char>(f), {}};
    auto b = slam::mean_sound_banks(dat);
    slam::NativeAudio audio(
        std::vector<std::vector<std::uint8_t>>{b[0].stim, b[1].stim});
    audio.request(0x90, 0, 4);
    audio.set_paused(false);
    audio.pump();
    audio.set_paused(true);
    const int base_queued=audio.queued_bytes();
    audio.request(0x8c, 0, 0);
    if (base_queued <= 0 || audio.queued_bytes() != base_queued)
      throw std::runtime_error("Inactive foreground cancellation discarded base PCM");
    audio.request(0x88, 1, 56);
    audio.request(0x8c, 0, 0);
    audio.request(0x84, 1, 52);
    audio.set_paused(false);
    audio.pump();
    if (audio.queued_bytes() <= 0)
      throw std::runtime_error("Tilt produced no SDL PCM");
    std::cout << "PASS foreground stop8c then Tilt bank1/order52 queued PCM\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
