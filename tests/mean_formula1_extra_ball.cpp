#include "core/mean_diagnostic_input.h"
#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json = nlohmann::json;
int main(int argc, char **argv) {
  if (argc != 6) return 2;
  try {
    json fixture, steering;
    std::ifstream(argv[4]) >> fixture;
    std::ifstream(std::filesystem::path(argv[4]).parent_path() /
                  "mean-minigame1-winning-input.json") >> steering;
    const auto phase = std::stoul(argv[5]);
    slam::MeanSimulation s(argv[1], argv[2], argv[3]);
    s.set_retail_minigame(true); s.reset(); s.set_continuous_play(true);
    unsigned total = 0;
    for (const auto &run : fixture.at("entry_actions_rle")) {
      const unsigned actions = run.at("actions");
      for (unsigned i = 0; i < run.at("ticks").get<unsigned>(); ++i) {
        s.set_launch(actions & 8);
        if (actions & 4) s.press_plunger();
        s.set_flippers(actions & 1, actions & 2);
        if (!s.step()) throw std::runtime_error(s.status());
        s.take_audio_requests(); ++total;
      }
    }
    if (!s.minigame_active() || s.minigame2_active() || s.ball_number() != 3)
      throw std::runtime_error("Recorded finite Formula1 entry missing");
    const auto entry_prizes = s.pending_extra_ball_prizes(), entry_credits = s.extra_ball_credits();
    const auto before_score = s.score();
    while (s.minigame_active()) {
      const unsigned key = steering.at("keys").at(s.minigame_steps());
      s.set_flippers(key == 1, key == 2);
      if (!s.step()) throw std::runtime_error(s.status());
      s.take_audio_requests(); ++total;
    }
    if (s.score() != before_score + 120000000 ||
        s.pending_extra_ball_prizes() != entry_prizes + 1 ||
        s.extra_ball_credits() != entry_credits)
      throw std::runtime_error("Original win pending-prize transition missing");
    json events = json::array();
    events.push_back({{"event","win"},{"step",total},{"ball",s.ball_number()},
      {"pending",s.pending_extra_ball_prizes()},{"credits",s.extra_ball_credits()},
      {"score",s.score()}});
    bool collected = false, replayed = false;
    s.set_launch(true);
    for (unsigned after = 0; after < 100000 && !s.game_over(); ++after) {
      const auto k = slam::mean_finite_shot_input(total, s.ball().i32(4) >> 16, phase);
      s.set_flippers(k[0], k[1]);
      const auto pending = s.pending_extra_ball_prizes(), credits = s.extra_ball_credits();
      const auto bonus = s.bonus_completions(), ball = s.ball_number();
      if (!s.step() && !s.game_over()) throw std::runtime_error(s.status());
      s.take_audio_requests(); ++total;
      if (s.pending_extra_ball_prizes() < pending && s.extra_ball_credits() == credits + 1) {
        if (s.pending_extra_ball_prizes() != pending - 1 ||
            s.material5_display_callback() != 0x410d34 || s.ball().u16(0x58) != 3 || s.ball().u16(0x5a) != 1)
          throw std::runtime_error("Original upper-trap reward3 admission missing");
        collected = true;
        events.push_back({{"event","collected"},{"step",total},{"ball",s.ball_number()},
          {"pending",s.pending_extra_ball_prizes()},{"credits",s.extra_ball_credits()},
          {"callback",s.material5_display_callback()},{"ball_state",s.ball().bytes},
          {"score",s.score()}});
      }
      if (s.bonus_completions() > bonus && credits && s.extra_ball_credits() == credits - 1 &&
          s.ball_number() == ball && !s.game_over()) {
        replayed = true;
        events.push_back({{"event","replayed"},{"step",total},{"ball",ball},
          {"credits",s.extra_ball_credits()},{"score",s.score()}});
      }
    }
    if (!s.game_over()) throw std::runtime_error("Finite game did not finish");
    const auto score = s.score();
    const auto final_ball_number = s.ball_number();
    const auto final_ball_state = s.ball().bytes;
    const auto bonus_completions = s.bonus_completions();
    for (unsigned i = 0; i < 40; ++i) {
      s.step();
      if (s.score() != score || s.ball().bytes != final_ball_state)
        throw std::runtime_error("GameOver changed ball or score");
    }
    s.reset();
    if (s.game_over() || s.ball_number() != 1 || s.score() || s.extra_ball_credits() ||
        s.pending_extra_ball_prizes())
      throw std::runtime_error("New game retains Formula1 credit/prize");
    std::cout << json{{"phase",phase},{"collected",collected},{"replayed",replayed},
      {"game_over",true},{"steps",total},{"bonus_completions",bonus_completions},
      {"ball_number",final_ball_number},{"events",events},{"score",score},
      {"final_ball_bytes",final_ball_state},{"new_game_restored",true}}.dump() << '\n';
  } catch (const std::exception &e) { std::cerr << e.what() << '\n'; return 1; }
}
