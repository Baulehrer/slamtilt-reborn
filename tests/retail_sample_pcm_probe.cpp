#include "audio/mean_sample_mixer.h"
#include "audio/pirate_sound_assets.h"
#include "audio/space_sound_assets.h"
#include "audio/demon_sound_assets.h"
#include "core/sha256.h"
#include <nlohmann/json.hpp>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <set>
#include <stdexcept>

int main(int argc, char **argv) {
  try {
    if (argc != 4) throw std::runtime_error("TABLE DAT ORIGINAL_PCM_JSON");
    const std::string table = argv[1];
    std::ifstream input(argv[2], std::ios::binary), fixture_file(argv[3]);
    if (!input || !fixture_file) throw std::runtime_error("Missing DAT or PCM fixture");
    std::vector<std::uint8_t> dat{std::istreambuf_iterator<char>(input), {}};
    nlohmann::json fixture; fixture_file >> fixture;
    if (fixture.at("table") != table || fixture.at("dat_sha256") != slam::sha256(dat))
      throw std::runtime_error("PCM fixture does not match DAT and table");
    const auto profiles = table == "mean" ? slam::mean_sample_profiles()
                         : table == "pirate" ? slam::pirate_sample_profiles()
                         : table == "space" ? slam::space_sample_profiles()
                         : table == "demon" ? slam::demon_sample_profiles()
                         : throw std::runtime_error("Unknown table");
    if (fixture.at("profile_count") != profiles.size())
      throw std::runtime_error("PCM fixture does not cover every native descriptor");
    std::set<std::pair<unsigned, unsigned>> covered;
    for (const auto &entry : fixture.at("cases")) {
      const auto descriptor = entry.at("descriptor").get<unsigned>();
      const auto found = std::find_if(profiles.begin(), profiles.end(),
          [&](const auto &p) { return p.descriptor == descriptor; });
      if (found == profiles.end() || found->offset != entry.at("offset") ||
          found->length != entry.at("length") || found->period != entry.at("period"))
        throw std::runtime_error("Native and original sample profile mismatch");
      const auto frames = entry.at("frames").get<unsigned>();
      if ((frames != 1 && frames != 221 && frames != 2048 && frames != 30000) ||
          !covered.emplace(descriptor, frames).second)
        throw std::runtime_error("Unexpected or duplicate PCM case");
      slam::MeanSampleMixer mixer(dat, profiles);
      mixer.request(-1, 1, descriptor);
      std::vector<std::int16_t> stereo(frames * 2);
      for (unsigned at = 0; at < frames; at += 137)
        mixer.mix(stereo.data() + at * 2, std::min(137u, frames - at));
      std::vector<std::uint8_t> mono; mono.reserve(frames * 2);
      for (unsigned i = 0; i < frames; ++i) {
        if (stereo[2*i] != stereo[2*i+1]) throw std::runtime_error("Channel mismatch");
        const auto value = std::uint16_t(stereo[2*i]);
        mono.push_back(std::uint8_t(value)); mono.push_back(std::uint8_t(value >> 8));
      }
      if (slam::sha256(mono) != entry.at("mono_sha256")) {
        std::cerr << table << " descriptor=" << std::hex << descriptor << std::dec
                  << " frames=" << frames << '\n';
        throw std::runtime_error("Original/native PCM differs");
      }
    }
    if (covered.size() != profiles.size() * 4)
      throw std::runtime_error("PCM fixture is missing descriptor/frame combinations");
    std::cout << table << ": " << fixture.at("cases").size()
              << " original/native one-shot PCM comparisons passed\n";
    return 0;
  } catch (const std::exception &e) { std::cerr << e.what() << '\n'; return 1; }
}
