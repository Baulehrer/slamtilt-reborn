#include "physics/mean_minigame_lift.h"
#include "physics/mean_multiball.h"
#include "physics/mean_multiball_release.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
namespace slam {
void ball_pair_408bfc(MeanMinigameLift &);
}
std::vector<std::uint8_t> read(const char *p) {
  std::ifstream f(p, std::ios::binary);
  return {std::istreambuf_iterator<char>(f), {}};
}
int main(int argc, char **argv) {
  if (argc != 3)
    return 2;
  auto image = read(argv[1]), lut = read(argv[2]);
  nlohmann::json cases;
  std::cin >> cases;
  auto out = nlohmann::json::array();
  for (const auto &c : cases) {
    auto op = c["op"].get<std::string>();
    if (op == "guide") {
      slam::MeanObject b;
      for (unsigned j = 0; j < 100; ++j)
        b.bytes[j] = c["ball"][j];
      slam::mean_multiball_guide(b);
      out.push_back(b.bytes);
    } else if (op == "pair") {
      slam::MeanMinigameLift m;
      m.image = image;
      std::copy(lut.begin(), lut.end(), m.runtime.begin() + 0x6000);
      m.wr(0x43e728, 0x42c9fc, 4);
      m.wr(0x43e764, 0x1006000, 4);
      for (unsigned k = 0; k < 2; ++k) {
        m.wr(0x4298c8 + k * 4, 0x1000000 + k * 128, 4);
        for (unsigned j = 0; j < 100; ++j)
          m.runtime[k * 128 + j] = c["balls"][k][j];
      }
      m.r[0] = 0;
      m.r[2] = 1;
      m.r[4] = 0x200f000;
      m.push(0x200fff0);
      slam::ball_pair_408bfc(m);
      out.push_back({std::vector<std::uint8_t>(m.runtime.begin(),
                                               m.runtime.begin() + 100),
                     std::vector<std::uint8_t>(m.runtime.begin() + 128,
                                               m.runtime.begin() + 228)});
    } else if (op == "release") {
      slam::MeanObject b;
      for (unsigned j = 0; j < 100; ++j)
        b.bytes[j] = c["ball"][j];
      slam::MeanMultiballReleaseState s;
      s.mode = c["mode"];
      s.selected = c["selected"];
      s.bits = c["bits"];
      s.field_43f3a6 = c["flag"];
      s.field_43f382 = c["flag"];
      s.field_43f064 = 0x12345;
      s.slot = {19, c["secondary"], c["tertiary"]};
      auto states = nlohmann::json::array();
      for (unsigned i = 0; i < 8; ++i) {
        unsigned samples = 0;
        slam::mean_multiball_release(b, s, 0x1100000, c.value("tilt", false), &samples);
        states.push_back({{"tick", i + 1},
                          {"ball", b.bytes},
                          {"slot", s.slot},
                          {"bits", s.bits},
                          {"slot50", s.slot50}});
        if (c.contains("tilt"))
          states.back()["samples"] = samples;
        if (b.u16(0x58) == 2)
          break;
      }
      out.push_back(states);
    } else {
      slam::MeanBallPool p;
      p.count = c["count"];
      for (unsigned k = 0; k < 8; ++k)
        for (unsigned j = 0; j < 100; ++j)
          p.objects[k].bytes[j] = c["balls"][k][j];
      if (op == "allocate") {
        auto *b = p.allocate();
        out.push_back({{"count", p.count},
                       {"index", b ? int(b - p.objects.data()) : -1},
                       {"balls", nlohmann::json::array()}});
      } else if (op == "remove") {
        p.remove_drained();
        out.push_back({{"count", p.count}, {"balls", nlohmann::json::array()}});
      } else {
        slam::MeanCaptureTickState capture;
        slam::MeanMode5LeftState mode;
        mode.field_43f37e = 2;
        mode.field_43f36e = c["remaining"];
        std::array<std::int32_t, 3> slot{{c["primary"], 33, 44}};
        slam::mean_mode4_spawn(p, capture, mode, slot, 0x1100000);
        out.push_back({{"count", p.count},
                       {"remaining", mode.field_43f36e},
                       {"stage", mode.field_43f37e},
                       {"slot", slot},
                       {"slot50", capture.field_438b50},
                       {"balls", nlohmann::json::array()}});
      }
      for (auto &b : p.objects)
        out.back()["balls"].push_back(b.bytes);
    }
  }
  std::cout << out.dump();
}
