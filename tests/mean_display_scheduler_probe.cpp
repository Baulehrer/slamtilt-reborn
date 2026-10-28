#include "dmd/mean_display_scheduler.h"
#include <iostream>
#include <nlohmann/json.hpp>
using nlohmann::json;
using namespace slam;
int main() {
  json cases;
  std::cin >> cases;
  json out = json::array();
  for (auto &c : cases) {
    auto v = c.at("initial").get<std::vector<std::int32_t>>();
    MeanDisplayScheduler s{v[0],
                           v[1],
                           v[2],
                           v[3],
                           static_cast<std::uint32_t>(v[4]),
                           v[5],
                           v[6],
                           v[7],
                           v[8],
                           v[9],
                           v[10],
                           v[11],
                           v[12],
                           static_cast<std::uint8_t>(v[13])};
    if(c.contains("owner")) {
      const auto owner=c["owner"].get<std::string>();
      if(owner=="minigame") mean_display_minigame_enter(s);
      else if(owner=="bonus") mean_display_bonus_enter(s);
      else if(owner=="return") mean_display_bonus_return(s);
    }
    int result = 0;
    json actions = json::array();
    if (c.contains("request")) {
      auto r = c["request"].get<std::vector<std::int32_t>>();
      result = mean_display_request(s, {r[0], r[1], r[2], r[3], r[4], r[5],
                                        static_cast<std::uint32_t>(r[6])});
    }
    for (unsigned i = 0; i < c.value("ticks", 0u); ++i) {
      auto d = mean_display_scheduler_begin(s);
      int action = static_cast<int>(d);
      if (d == MeanDisplayDispatch::Callback) {
        ++s.field_78c;
        if (s.field_78c >= 3)
          s.field_784 = 0;
      }
      if (mean_display_scheduler_finish(s))
        action += 8;
      actions.push_back(action);
    }
    out.push_back(
        {{"result", result},
         {"actions", actions},
         {"state",
          {s.field_780, s.field_784, s.field_788, s.field_78c, s.field_790,
           s.field_7a0, s.field_7b0, s.field_7b4, s.field_81c, s.field_297a8,
           s.field_297ac, s.field_297b8, s.field_297bc, s.field_297cc}}});
  }
  std::cout << out.dump() << '\n';
}
