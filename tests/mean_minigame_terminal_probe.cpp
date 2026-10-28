#include "physics/mean_minigame_lift.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
namespace slam {
void minigame_4192d0(MeanMinigameLift &);
}
std::vector<std::uint8_t> read(const char *p) {
  std::ifstream f(p, std::ios::binary);
  return {std::istreambuf_iterator<char>(f), {}};
}
int main(int argc, char **argv) {
  if (argc != 4)
    return 2;
  const auto image = read(argv[1]), runtime = read(argv[2]),
             dat = read(argv[3]);
  nlohmann::json input;
  std::cin >> input;
  auto out = nlohmann::json::array();
  for (const auto &c : input) {
    slam::MeanMinigameLift m;
    m.image = image;
    m.dat = dat;
    std::copy(runtime.begin(), runtime.end(), m.runtime.begin());
    m.wr(0x43f00c, c[0].get<unsigned>(), 4);
    m.wr(0x43f010, c[0].get<unsigned>(), 4);
    m.wr(0x43efdc, c[1].get<unsigned>(), 4);
    m.wr(0x43efe0, c[2].get<unsigned>(), 4);
    m.wr(0x43efe4, c[3].get<unsigned>(), 4);
    m.wr(0x43f1fa, c[4].get<unsigned>(), 2);
    m.r[4] = 0x200f000;
    m.push(0x200fff0);
    slam::minigame_4192d0(m);
    out.push_back({m.rd(0x43f00c, 4), m.rd(0x43f010, 4), m.rd(0x43efdc, 4),
                   m.rd(0x1001044, 4), m.rd(0x1001030, 4), m.rd(0x43f1e6, 2),
                   m.rd(0x43f1fa, 2), m.rd(0x438b64, 4), m.rd(0x438b70, 4),
                   m.rd(0x438b7c, 4), m.points});
  }
  std::cout << out.dump();
}
