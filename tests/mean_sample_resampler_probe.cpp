#include "audio/mean_sample_mixer.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  try {
    if (argc != 2)
      return 2;
    std::ifstream f(argv[1]);
    nlohmann::json fixture;
    f >> fixture;
    std::vector<std::uint8_t> dat(0x6d40e + 0x16b0);
    for (std::size_t n = 0; n < 0x1941; ++n)
      dat[0x63a1d + n] = std::uint8_t(n);
    for (std::size_t n = 0; n < 0xfee; ++n)
      dat[0x6535e + n] = std::uint8_t(n);
    for (std::size_t n = 0; n < 0xbd2; ++n)
      dat[0x6aaa4 + n] = std::uint8_t(n);
    for (std::size_t n = 0; n < 0x118a; ++n)
      dat[0x6634c + n] = std::uint8_t(n);
    for (std::size_t n = 0; n < 0xfac; ++n)
      dat[0x674d6 + n] = std::uint8_t(n);
    for (std::size_t n = 0; n < 0x16b0; ++n)
      dat[0x6d40e + n] = std::uint8_t(n);
    for (std::size_t n = 0; n < 0x1d98; ++n)
      dat[0x6b676 + n] = std::uint8_t(n);
    for (const auto profile : {std::pair<unsigned,unsigned>{0x27b66,2747}, {0x286ea,2882}, {0x292f5,3395}, {0x2a100,4536}})
      for (unsigned n=0;n<profile.second;++n) dat[profile.first+n]=std::uint8_t(n);
    for (const auto &test : fixture.at("cases")) {
      slam::MeanSampleMixer mixer(dat);
      mixer.request(9, 8, test.at("descriptor").get<unsigned>());
      std::vector<std::int16_t> pcm(test.at("frames").get<unsigned>() * 2);
      mixer.mix(pcm.data(), pcm.size() / 2);
      std::uint64_t hash = 14695981039346656037ull;
      for (std::size_t n = 0; n < pcm.size(); n += 2) {
        if (pcm[n] != pcm[n + 1])
          throw std::runtime_error("Stereo mono mismatch");
        const auto v = std::uint16_t(pcm[n]);
        for (unsigned byte = 0; byte < 2; ++byte) {
          hash ^= (v >> (byte * 8)) & 255;
          hash *= 1099511628211ull;
        }
      }
      if (std::to_string(hash) != test.at("pcm_fnv64"))
        throw std::runtime_error("Original mono PCM mismatch");
    }
    std::cout << fixture.at("cases").size()
              << " native mono PCM hashes match original420120/LUT\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
