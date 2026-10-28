#include "rules/mean_capture_delay.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 2)
    return 2;
  nlohmann::json j;
  std::ifstream(argv[1]) >> j;
  for (const auto &c : j["records"]) {
    std::array<std::int32_t, 5> d = {101, 102, 103, 104, 105};
    std::int32_t f = 77;
    slam::mean_capture_delay(c["handle"], f, d,
                             c["selectors"].get<decltype(d)>(), c["delay"]);
    if (d != c["result"].get<decltype(d)>() || f != c["field024"])
      return 1;
  }
  std::cout << "PASS " << j["cases"] << " original capture-delay contexts\n";
}
