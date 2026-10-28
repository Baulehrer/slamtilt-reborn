#include "assets/table_profile.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json cases;
  std::cin >> cases;
  auto rows = nlohmann::json::array();
  for (const auto &c : cases) {
    auto p =
        slam::load_table_profile(slam::default_table_profiles(), c.at("table"));
    slam::MeanObject b;
    b.bytes = c.at("bytes").get<decltype(b.bytes)>();
    slam::table_set_layer(b, p, c.at("layer"), c.at("base"));
    rows.push_back(b.bytes);
  }
  std::cout << rows.dump() << '\n';
}
