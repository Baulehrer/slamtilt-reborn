#include "audio/audio_gain.h"
#include "audio/mean_sample_mixer.h"

#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char **argv) {
  const bool voice = argc == 2 && std::string(argv[1]) == "--voice";
  if (argc > 1 && !voice) return 1;
  int mono, left, right;
  while (std::cin >> mono >> left >> right) {
    if (mono < -32768 || mono > 32767 || left < -32768 || left > 32767 ||
        right < -32768 || right > 32767)
      return 1;
    if (voice) {
      if (mono < -128 || mono > 127) return 1;
      const std::vector<std::uint8_t> pcm{static_cast<std::uint8_t>(mono)};
      slam::MeanSampleMixer mixer(pcm, {{1, 0, 1, 428}});
      mixer.request(-1, 1, 1);
      std::int16_t output[] = {static_cast<std::int16_t>(left),
                               static_cast<std::int16_t>(right)};
      mixer.mix(output, 1);
      std::cout << output[0] << ' ' << output[1] << '\n';
      continue;
    }
    const auto m = static_cast<std::int16_t>(mono);
    std::cout << slam::mix_audio_levels(static_cast<std::int16_t>(left), m, 1, 1)
              << ' '
              << slam::mix_audio_levels(static_cast<std::int16_t>(right), m, 1, 1)
              << '\n';
  }
  return std::cin.eof() ? 0 : 1;
}
