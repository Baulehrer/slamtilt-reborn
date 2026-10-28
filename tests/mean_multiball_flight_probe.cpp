#include "physics/mean_simulation.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 4)
    return 2;
  slam::MeanSimulation s(argv[1], argv[2], argv[3]);
  s.debug_start_multiball(true);
  auto states = nlohmann::json::array();
  states.push_back(s.ball().bytes);
  for (int i = 0; i < 120; ++i) {
    if (!s.step())
      break;
    states.push_back(s.ball().bytes);
  }
  std::cout << states.dump();
}
