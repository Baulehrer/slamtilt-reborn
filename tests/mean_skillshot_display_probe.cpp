#include "dmd/mean_skillshot_display.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 2) return 2;
  try {
    auto assets = slam::load_mean_skillshot_display(argv[1]);
    nlohmann::json cases; std::cin >> cases;
    auto out = nlohmann::json::array();
    for (const auto &c : cases) {
      auto counter = c.at("counter").get<std::int32_t>();
      slam::WindowsDmdPixels pixels{};
      bool pair = c.value("pair", false);
      if (pair) for (unsigned i=0;i<pixels.size();++i) pixels[i]=(i*13+i/96)%4;
      bool valid = pair ? slam::mean_skillshot_choice_pair(counter, assets, pixels,
          c.at("selection"), c.at("tier"), c.at("reward")) :
          slam::mean_skillshot_display(counter, assets, pixels,
          c.at("selection"), c.at("tier"), c.at("reward"));
      out.push_back({{"counter",counter},{"pixels",pixels},{"valid",valid}});
    }
    std::cout << out.dump() << '\n';
  } catch(const std::exception &e) { std::cerr << e.what() << '\n'; return 1; }
}
