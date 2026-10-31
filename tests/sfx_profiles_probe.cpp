#include "audio/mean_sample_mixer.h"
#include "audio/pirate_sound_assets.h"
#include "audio/space_sound_assets.h"
#include "audio/demon_sound_assets.h"
#include <nlohmann/json.hpp>
#include <iostream>

int main() {
  nlohmann::json result = nlohmann::json::object();
  const auto add = [&](const char *name, const std::vector<slam::SampleProfile> &profiles) {
    auto &entries = result[name];
    entries = nlohmann::json::array();
    for (const auto &p : profiles)
      entries.push_back({{"descriptor", p.descriptor}, {"offset", p.offset},
                         {"length", p.length}, {"period", p.period}});
  };
  add("mean", slam::mean_sample_profiles());
  add("pirate", slam::pirate_sample_profiles());
  add("space", slam::space_sample_profiles());
  add("demon", slam::demon_sample_profiles());
  std::cout << result.dump() << '\n';
}
