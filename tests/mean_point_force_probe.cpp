#include "physics/mean_point_force.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json cases;
  std::cin >> cases;
  auto out = nlohmann::json::array();
  for (const auto &c : cases) {
    slam::MeanObject b;
    b.bytes = c.at("ball").get<decltype(b.bytes)>();
    std::vector<slam::MeanPointForceNode> nodes;
    for (const auto &n : c.at("nodes"))
      nodes.push_back({n[0].get<std::int16_t>(), n[1].get<std::int16_t>(),
                       n[2].get<std::int16_t>(), n[3].get<std::int16_t>()});
    bool ok = slam::mean_point_force(
        b, nodes, c.at("lookup").get<std::vector<std::uint16_t>>(),
        c.at("suppressed").get<bool>());
    out.push_back({{"ball", b.bytes}, {"ok", ok}});
  }
  std::cout << out.dump() << '\n';
}
