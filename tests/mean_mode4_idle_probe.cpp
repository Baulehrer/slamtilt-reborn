#include "dmd/mean_mode4_idle.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 2)
    return 2;
  auto a = slam::load_mean_mode4_idle(argv[1]);
  nlohmann::json cs, out = nlohmann::json::array();
  std::cin >> cs;
  for (auto &c : cs) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    s.field_438af8 = c["counter"];
    slam::WindowsDmdPixels px{};
    for (unsigned i = 0; i < px.size(); ++i)
      px[i] = i % 4;
    auto e = slam::mean_mode4_idle(s, a, px, c["lookup"], c["handle"]);
    out.push_back({{"fields", s.fields},
                   {"counter", s.field_438af8},
                   {"pixels", px},
                   {"callback", e.callback},
                   {"clear_slots", e.clear_slots},
                   {"displayed", e.displayed}});
  }
  std::cout << out.dump();
}
