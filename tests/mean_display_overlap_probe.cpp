#include "dmd/mean_material5_display.h"
#include <iostream>
#include <nlohmann/json.hpp>
using nlohmann::json;
int main(int argc, char **argv) {
  if (argc != 3 && argc != 4)
    return 2;
  const auto assets = slam::load_mean_material5_display(argv[1]);
  const auto font = slam::load_mean_score_font(argv[2]);
  json cases;
  std::cin >> cases;
  json out = json::array();
  for (auto &c : cases) {
    slam::MeanMaterial5Display s;
    int reward_gate=-1, mode6_gate=-1, afc=0;
    for (unsigned i = 0; i < s.pixels.size(); ++i) {
      s.pixels[i] = i % 4;
      s.restore_pixels[i] = i % 4;
    }
    json rows = json::array();
    for (auto &op : c) {
      int accepted = 0;
      if (op.contains("request")) {
        auto v = op["request"].get<std::vector<std::int32_t>>();
        accepted =
            s.request(
                {v[0], v[1], 2, 0, -1, -1, static_cast<std::uint32_t>(v[2])}, 0)
                ? -1
                : 0;
      } else {
        const auto callback=s.callback, counter=s.counter;
        const auto dispatch=slam::mean_material5_display_scheduled_step(s, assets, font, {});
        const auto e=slam::mean_display_callback_effects(callback,counter,dispatch);
        if(e.release_reward) reward_gate=0;
        if(e.release_mode6) mode6_gate=0;
        if(e.request_438afc) afc=1;
      }
      std::uint64_t hash = 14695981039346656037ull;
      for (auto v : s.pixels)
        hash = (hash ^ v) * 1099511628211ull;
      auto &g = s.scheduler;
      rows.push_back(
          {{"accepted", accepted},
           {"state",
            {g.field_780, g.field_784, g.field_788, g.field_78c, g.field_790}},
           {"fnv", std::to_string(hash)}});
      if(argc==4) rows.back()["gates"]={reward_gate,mode6_gate,afc};
    }
    out.push_back(rows);
  }
  std::cout << out.dump() << '\n';
}
