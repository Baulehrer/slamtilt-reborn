#include "dmd/mean_mode4_phase1.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 2 && argc != 3)
    return 2;
  auto a = slam::load_mean_mode4_phase1(argv[1]);
  slam::MeanScoreFont font;
  if (argc == 3) font = slam::load_mean_score_font(std::filesystem::path(argv[1]).parent_path() / "MAIN.DAT");
  nlohmann::json cs, out = nlohmann::json::array();
  std::cin >> cs;
  for (auto &c : cs) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    slam::WindowsDmdPixels px{};
    auto e = argc == 3 ? slam::render_mean_mode4_phase1(s, a, font, px)
                       : slam::mean_mode4_phase1(s, a, px);
    out.push_back({{"fields", s.fields},
                   {"pixels", px},
                   {"audio", e.bank1_order50},
                   {"service8c", e.service8c},
                   {"number", e.number},
                   {"value", e.value},
                   {"eax", e.eax},
                   {"edx", e.edx},
                   {"ecx", e.ecx}});
  }
  std::cout << out.dump();
}
