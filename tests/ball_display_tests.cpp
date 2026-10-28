#include "renderer/ball_display.h"
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
    unsigned count = 0;
    for (const auto &c : fixture.at("cases")) {
      auto fixed = [](const nlohmann::json &v) {
        return std::int32_t(v.get<double>() * 65536);
      };
      const auto got = slam::ball_display_position(
          fixed(c["current"][0]), fixed(c["current"][1]),
          fixed(c["previous"][0]), fixed(c["previous"][1]), c["residual_ms"]);
      if (got != c["original_render_xy"].get<std::array<int, 2>>())
        throw std::runtime_error(
            "Original render anchor/interpolation mismatch");
      ++count;
    }
    if (count != 7)
      throw std::runtime_error("Original cases missing");
    std::cout << count << " original x87 render fixtures match native\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
