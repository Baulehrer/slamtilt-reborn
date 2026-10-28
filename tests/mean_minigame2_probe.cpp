#include "physics/mean_minigame_lift.h"
#include "dmd/mean_minigame_text.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
std::vector<std::uint8_t> read(const char *p) {
  std::ifstream f(p, std::ios::binary);
  return {std::istreambuf_iterator<char>(f), {}};
}
int main(int argc, char **argv) {
  try {
    if (argc != 6 && argc != 7 && argc != 8 && argc != 9)
      return 2;
    slam::MeanMinigameLift m;
    m.image = read(argv[1]);
    auto v = read(argv[2]);
    std::copy(v.begin(), v.end(), m.runtime.begin());
    m.dat = read(argv[3]);
    if (argc >= 7)
      m.wr(0x43f1f6, std::stoul(argv[6]), 2);
    slam::MeanBonusPixels font;
    if(argc==9){
      font=slam::load_mean_bonus_pixels(argv[8]);
      m.text_service=[&](slam::MeanMinigameLift &q,std::uint32_t target){
        slam::mean_minigame_text_service(font,q.pixels,target,q.r,[&](std::uint32_t a,unsigned n){return q.rd(a,n);});
      };
    }
    const int seed = std::stoi(argv[4]), limit = std::stoi(argv[5]);
    auto out = nlohmann::json::array();
    for (int tick = 0; tick < limit; ++tick) {
      if (seed == 1)
        m.wr(0x43f034, 0x2800, 4);
      if (seed == 2)
        m.wr(0x43f034, 0x40000, 4);
      if (seed == 3)
        m.wr(0x43f034, tick % 100 < 50 ? 0x40000 : 0, 4);
      if (seed == 4 && m.rd(0x43f01c, 4) == 2) {
        auto n = m.rd(0x43f034, 4);
        m.wr(0x43f034, n + ((0x140000 - n) >> 7), 4);
      }
      m.r[4] = 0x200f000;
      m.push(0x200fff0);
      slam::minigame_4180d0(m);
      if(argc==9){
        std::uint64_t h=14695981039346656037ull;for(auto p:m.pixels)h=(h^p)*1099511628211ull;
        out.push_back({{"tick",tick},{"pixels",std::to_string(h)}});
        if (!m.rd(0x1001044,4)) break;
        continue;
      }
      if(argc==8){
        for(const auto &q:m.audio_requests) out.push_back({{"tick",tick},{"service",q.service},{"descriptor",q.descriptor},{"edx",q.edx},{"ebx",q.ebx}});
        m.audio_requests.clear();
        if (!m.rd(0x1001044,4)) break;
        continue;
      }
      std::array<std::uint32_t, 24> fields{};
      for (unsigned i = 0; i < fields.size(); ++i)
        fields[i] = m.rd(0x43efd8 + i * 4, 4);
      std::array<std::uint32_t, 10> extra{};
      unsigned addresses[] = {0x43efcc, 0x43efd4, 0x43f040, 0x43f050, 0x43f1f6,
                              0x43f3a4, 0x43f3a6, 0x43f3b8, 0x438b2c, 0x438b34};
      for (unsigned i = 0; i < extra.size(); ++i)
        extra[i] = m.rd(addresses[i], 4);
      std::uint64_t hash = 14695981039346656037ull;
      for (unsigned i = 0; i < 480; ++i) {
        hash ^= m.byte(0x43ec3c + i);
        hash *= 1099511628211ull;
      }
      out.push_back({{"fields", fields},
                     {"extra", extra},
                     {"active", m.rd(0x1001044, 4)},
                     {"mode", m.rd(0x1001030, 4)},
                     {"frame_hash", hash},
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
