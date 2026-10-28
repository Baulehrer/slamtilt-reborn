#include "core/mean_diagnostic_input.h"
#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 5)
    return 2;
  try {
    slam::MeanSimulation s(argv[1], argv[2], argv[3]);
    s.reset();
    s.set_continuous_play(true);
    s.set_launch(true);
    std::array<bool, 2> last{};
    unsigned entry = 0;
    for (; entry < 80000 && !s.minigame_active(); ++entry) {
      last = slam::mean_finite_shot_input(entry, s.ball().i32(4) >> 16);
      s.set_flippers(last[0], last[1]);
      if (!s.step())
        throw std::runtime_error(s.status());
      s.take_audio_requests();
    }
    if (!s.minigame2_active() || s.minigame_steps() != 0)
      throw std::runtime_error("Natural entry unavailable or already stepped");
    const auto &m = s.diagnostic_minigame_state();
    std::filesystem::create_directories(argv[4]);
    std::ofstream(std::filesystem::path(argv[4]) / "image.bin",
                  std::ios::binary)
        .write(reinterpret_cast<const char *>(m.image.data()), m.image.size());
    std::ofstream(std::filesystem::path(argv[4]) / "runtime.bin",
                  std::ios::binary)
        .write(reinterpret_cast<const char *>(m.runtime.data()),
               m.runtime.size());
    const auto score = s.score();
    auto rows = nlohmann::json::array();
    auto rd = [&](unsigned a) {
      unsigned v = 0;
      for (unsigned i = 0; i < 4; ++i)
        v |= unsigned(a < 0x500000 ? m.image[a + i - 0x400000]
                                   : m.runtime[a + i - 0x1000000])
             << (8 * i);
      return v;
    };
    for (unsigned step = 0; step < 20000 && s.minigame_active(); ++step) {
      const bool left = (step / 5) % 2, right = !left;
      const auto tick = s.minigame_steps();
      const std::array<bool, 2> edges{left && !last[0], right && !last[1]};
      last = {left, right};
      s.set_flippers(left, right);
      if (!s.step())
        throw std::runtime_error(s.status());
      auto audio = nlohmann::json::array();
      for (const auto &q : s.take_audio_requests())
        audio.push_back({{"service", q.service},
                         {"descriptor", q.descriptor},
                         {"edx", q.bank},
                         {"ebx", q.order}});
      nlohmann::json row = {{"audio", audio},
                            {"edges", edges},
                            {"tick", s.minigame_steps() != tick}};
      if (s.minigame_steps() != tick) {
        auto fields = nlohmann::json::array();
        for (unsigned i = 0; i < 24; ++i)
          fields.push_back(rd(0x43efd8 + i * 4));
        std::uint64_t h = 14695981039346656037ull;
        for (unsigned i = 0; i < 480; ++i)
          h = (h ^ m.image[0x3ec3c + i]) * 1099511628211ull;
        row["state"] = {
            {"fields", fields},
            {"raw", std::vector<unsigned char>(m.image.begin() + 0x3f000,
                                               m.image.begin() + 0x3f3c0)},
            {"active", rd(0x1001044)},
            {"mode", rd(0x1001030)},
            {"points", s.score() - score},
            {"callback", m.requested_display_callback},
            {"packed_fnv", std::to_string(h)}};
      }
      rows.push_back(row);
    }
    if (s.minigame_active() || s.score() - score != 30000000 ||
        s.material5_display_callback() != 0x4122cc)
      throw std::runtime_error("Natural win failed");
    std::cout << nlohmann::json{{"entry_step", entry},
                                {"entry_ball", s.ball_number()},
                                {"score_before", score},
                                {"rows", rows}}
                     .dump()
              << '\n';
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
