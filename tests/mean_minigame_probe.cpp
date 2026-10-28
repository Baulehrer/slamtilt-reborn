#include "physics/mean_minigame_lift.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
std::vector<std::uint8_t> read(const char *p) {
  std::ifstream f(p, std::ios::binary);
  return {std::istreambuf_iterator<char>(f), {}};
}
int main(int argc, char **argv) {
  try {
    if (argc != 6)
      return 2;
    slam::MeanMinigameLift m;
    m.image = read(argv[1]);
    auto v = read(argv[2]);
    std::copy(v.begin(), v.end(), m.runtime.begin());
    m.dat = read(argv[3]);
    const int seed = std::stoi(argv[4]), limit = std::stoi(argv[5]);
    auto out = nlohmann::json::array();
    for (int tick = 0; tick < limit; ++tick) {
      m.wr(0x1001054,
           seed == 1                      ? 0xffffffffu
           : seed == 3 && tick % 100 < 50 ? 0xffffffffu
                                          : 0,
           4);
      m.wr(0x1001058,
           seed == 2                       ? 0xffffffffu
           : seed == 3 && tick % 100 >= 50 ? 0xffffffffu
                                           : 0,
           4);
      m.r[4] = 0x200f000;
      m.push(0x200fff0);
      slam::minigame_4180d0(m);
      std::array<std::uint32_t, 24> fields{};
      for (unsigned i = 0; i < fields.size(); ++i)
        fields[i] = m.rd(0x43efd8 + i * 4, 4);
      std::array<std::uint8_t, 480> frame{};
      for (unsigned i = 0; i < 480; ++i)
        frame[i] = m.byte(0x43ec3c + i);
      out.push_back({{"fields", fields},
                     {"active", m.rd(0x1001044, 4)},
                     {"mode", m.rd(0x1001030, 4)},
                     {"selected", m.rd(0x43f1e6, 2)},
                     {"frame", frame},
                     {"points", m.points}});
      if (!m.rd(0x1001044, 4))
        break;
    }
    std::cout << out.dump();
  } catch (const std::exception &e) {
    std::cerr << e.what();
    return 1;
  }
}
