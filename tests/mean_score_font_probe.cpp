#include "assets/mean_score_font.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 2)
    return 2;
  auto font = slam::load_mean_score_font(argv[1]);
  nlohmann::json in, out = nlohmann::json::array();
  std::cin >> in;
  for (auto &c : in) {
    std::array<std::uint8_t, 1920> pixels{};
    slam::draw_mean_score_u64(font, pixels, c[0], c[1], c[2], c[3]);
    out.push_back(pixels);
  }
  std::cout << out.dump();
}
