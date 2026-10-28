#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 5)
    return 2;
  std::ifstream f(argv[4]);
  nlohmann::json cases;
  f >> cases;
  auto result = nlohmann::json::array();
  for (const auto &c : cases) {
    slam::MeanSimulation s(argv[1], argv[2], c.at("trace").get<std::string>());
    s.set_original_contact_context(
        c.at("poses").get<std::vector<std::uint32_t>>(),
        c.at("globals").get<std::vector<std::uint32_t>>());
    if (c.contains("point_force_type"))
      s.set_original_point_force_context(
          c.at("point_force_type"), c.value("point_force_suppressed", false));
    auto rows = nlohmann::json::array();
    rows.push_back(s.ball().bytes);
    for (int i = 0; i < c.at("steps").get<int>(); ++i) {
      if (!s.step()) {
        if (c.value("include_terminal", false))
          rows.push_back(s.ball().bytes);
        break;
      }
      rows.push_back(s.ball().bytes);
    }
    result.push_back(rows);
  }
  std::cout << result.dump() << '\n';
}
