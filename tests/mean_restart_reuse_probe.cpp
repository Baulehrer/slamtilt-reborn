#include "physics/mean_step.h"
#include "rules/mean_restart_gate.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json in;
  std::cin >> in;
  auto out = nlohmann::json::array();
  for (const auto &c : in) {
    slam::MeanObject b;
    b.bytes = c.at("ball").get<decltype(b.bytes)>();
    std::int32_t gate = c.at("gate");
    auto d = slam::mean_restart_gate(gate, b.u16(0x58));
    if (d == slam::MeanRestartDecision::Initialize)
      slam::mean_initialize_ball(b, 0x1100000);
    out.push_back(
        {{"ball", b.bytes}, {"gate", gate}, {"decision", static_cast<int>(d)}});
  }
  std::cout << out.dump() << '\n';
}
