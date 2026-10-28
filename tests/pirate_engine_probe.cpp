#include "physics/mean_step.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 3) return 2;
  std::ifstream f(argv[1]); nlohmann::json cases; f >> cases;
  std::ifstream dat(argv[2], std::ios::binary);
  slam::MeanCollisionBits bits;
  bits.dat.assign(std::istreambuf_iterator<char>(dat), {});
  auto rows = nlohmann::json::array();
  for (const auto &c : cases) {
    slam::MeanObject b;
    b.bytes = c.at("bytes").get<std::array<std::uint8_t, 100>>();
    bits.hit_offset = c.at("hit_offset");
    bits.stride = c.at("stride");
    bits.extra_planes = c.at("planes");
    slam::mean_separate(b, bits, c.at("direction_x"), c.at("direction_y"), 0, 0);
    rows.push_back(b.bytes);
  }
  std::cout << rows.dump() << '\n';
}
