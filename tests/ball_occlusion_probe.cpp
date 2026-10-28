#include "assets/ball_occlusion.h"
#include <fstream>
#include <iostream>
#include <iterator>
#include <nlohmann/json.hpp>
using namespace slam;
int main(int argc, char **argv) {
  if (argc != 3)
    return 2;
  const auto outline = load_windows_ball_mask(argv[1]);
  std::ifstream f(argv[2], std::ios::binary);
  std::vector<std::uint8_t> dat((std::istreambuf_iterator<char>(f)), {});
  nlohmann::json cases;
  std::cin >> cases;
  auto output = nlohmann::json::array();
  for (const auto &c : cases) {
    auto result = outline;
    auto flag = c.at("flag").get<int>();
    const auto x = c.at("x").get<int>(), y = c.at("y").get<int>();
    if (flag == 1 && x >= 0 && y >= 0 && x < 304 && y < 600) {
      result = windows_ball_occlusion(outline, dat, c.at("offset"), x, y);
      flag = 2;
    }
    output.push_back({{"flag", flag}, {"mask", result.preserve_background}});
  }
  std::cout << output.dump();
}
