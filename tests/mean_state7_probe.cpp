#include "physics/mean_state7.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
using namespace slam;
int main(int argc, char **argv) {
  MeanLookup l;
  std::ifstream f(argv[1], std::ios::binary);
  l.field_43e764.assign(std::istreambuf_iterator<char>(f), {});
  nlohmann::json j;
  std::cin >> j;
  auto out = nlohmann::json::array();
  for (auto &c : j) {
    MeanObject b;
    b.bytes = c["ball"].get<decltype(b.bytes)>();
    bool transitioned = false;
    if (c["boundary"].get<bool>())
      transitioned = mean_state7_boundary(b, 0x1100000);
    else {
      MeanState7Record r;
      r.words = c["record"].get<decltype(r.words)>();
      if (!mean_state7_step(b, r, l))
        return 2;
    }
    out.push_back({{"ball", b.bytes}, {"transitioned", transitioned}});
  }
  std::cout << out.dump() << '\n';
}
