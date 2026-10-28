#include "rules/mean_capture_delay.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 2) return 2;
  nlohmann::json j; std::ifstream(argv[1]) >> j;
  for (const auto &c : j["records"]) {
    std::array<std::int32_t,5> delays{101,102,103,104,105};
    std::int32_t field024=77;
    slam::mean_capture_delay(c["handle"],field024,delays,
      c["selectors"].get<decltype(delays)>(),c["delay"]);
    if (field024!=c["field024"] || delays!=c["result"].get<decltype(delays)>()) return 1;
  }
  std::cout << "PASS " << j["cases"] << " Overheat capture admission contexts\n";
}
