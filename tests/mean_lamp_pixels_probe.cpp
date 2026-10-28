#include "assets/mean_lamps.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 2)
    return 2;
  auto table = slam::load_windows_table(argv[1]);
  auto result = nlohmann::json::array();
  for (auto &f : slam::load_mean_lamps(argv[1], table))
    result.push_back({{"x", f.x},
                      {"y", f.y},
                      {"w", f.width},
                      {"h", f.height},
                      {"mask", f.mask},
                      {"rgba", f.rgba}});
  std::cout << result.dump();
}
