#include "dmd/mean_material5_display.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 3)
    return 2;
  try {
    auto assets = slam::load_mean_material5_display(argv[1]);
    auto font = slam::load_mean_score_font(argv[2]);
    nlohmann::json input;
    std::cin >> input;
    auto out = nlohmann::json::array();
    for (const auto &c : input) {
      slam::MeanMaterial5Display s;
      s.start(c.at("callback"), c.at("score"));
      s.minigame_lap_points=c.value("minigame_lap_points",20000000u);
      s.field_43efdc = c.value("field_43efdc",1u);
      s.field_43efcc = c.value("field_43efcc",0u);
      s.field_1d8=c.value("field1d8",4);
      s.field_38a=c.value("field38a",0);
      s.field_358 = c.value("field358", 0);
      s.field_362 = c.value("field362", 0);
      s.field_1fe = c.value("field1fe", 0);
      s.field_1f2 = c.value("field1f2", 0);
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        s.pixels[i] = i % 4;
      if (c.value("restore", 0))
        for (unsigned i = 0; i < s.restore_pixels.size(); ++i)
          s.restore_pixels[i] = i % 4;
      auto flags = c.at("flags").get<std::array<std::uint8_t, 4>>();
      auto frames = nlohmann::json::array();
      for (unsigned n = 0; n < c.at("steps"); ++n) {
        slam::mean_material5_display_step(s, assets, font, flags);
        std::uint64_t hash = 14695981039346656037ull;
        for (auto v : s.pixels) {
          hash ^= v;
          hash *= 1099511628211ull;
        }
        frames.push_back({{"active", s.callback != 0},
                          {"counter", s.counter},
                          {"fnv", std::to_string(hash)}});
      }
      out.push_back(frames);
    }
    std::cout << out.dump() << '\n';
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
