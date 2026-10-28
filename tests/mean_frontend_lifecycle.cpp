#include "physics/mean_simulation.h"
#include "frontend/mean_highscores.h"
#include <chrono>
#include <iostream>
#include <stdexcept>
using json = nlohmann::json;
namespace {
void require(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}
struct TemporaryDirectory {
  std::filesystem::path path = std::filesystem::temp_directory_path() /
      ("slam-frontend-lifecycle-" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
  TemporaryDirectory() { require(std::filesystem::create_directory(path), "Cannot create isolated highscore directory"); }
  ~TemporaryDirectory() { std::error_code ignored; std::filesystem::remove_all(path, ignored); }
};
void key(MeanHighscores& scores, SDL_Scancode code, bool repeat = false) {
  SDL_Event event{};
  event.type = SDL_EVENT_KEY_DOWN;
  event.key.scancode = code;
  event.key.repeat = repeat;
  const bool consumed = scores.handle(event);
  require(consumed, "Highscore modal must consume repeated as well as fresh key events");
}
}
int main(int argc, char** argv) {
  if (argc != 6) return 2;
  try {
    json fixture; std::ifstream(argv[4]) >> fixture;
    TemporaryDirectory temporary;
    json cases = json::array();
    for (unsigned repeat = 0; repeat < 2; ++repeat) {
      // A fresh simulation and destination prevent session state leaking between cases.
      slam::MeanSimulation simulation(argv[1], argv[2], argv[3]);
      simulation.set_retail_minigame(true);
      simulation.reset();
      simulation.set_continuous_play(true);
      simulation.set_endless_play(false);
      const auto destination = temporary.path / ("case-" + std::to_string(repeat) + ".json");
      MeanHighscores highscores;
      highscores.load_path(destination);
      require(highscores.error.empty() && highscores.entries().empty(), "Fresh highscore destination differs");
      unsigned ticks = 0;
      auto step = [&](unsigned actions) {
        simulation.set_launch(actions & 8);
        simulation.set_flippers(actions & 1, actions & 2);
        if (actions & 4) simulation.press_plunger();
        if (actions & 16) simulation.nudge(1, false);
        if (actions & 64) simulation.nudge(-1, false);
        if (actions & 32) simulation.nudge(0, true);
        require(simulation.step() || simulation.game_over(), "Legal replay encountered gameplay guard");
        simulation.take_audio_requests();
        ++ticks;
      };
      for (const auto& run : fixture.at("actions_rle"))
        for (unsigned i = 0; i < run.at("ticks").get<unsigned>(); ++i)
          step(run.at("actions").get<unsigned>());
      require(ticks == 3486 && simulation.switch_rewards() == 2, "Skillshot entry replay differs");
      while (!simulation.game_over() && ticks < 15000) step(8);
      require(ticks == 7608 && simulation.game_over() && simulation.score() == 54200000 &&
                  simulation.bonus_completions() == 3 && simulation.ball_count() == 0,
              "Finite gameplay outcome differs");
      const auto final_score = simulation.score();
      const auto final_fields = simulation.shared_raw_state().fields;
      require(highscores.begin(final_score), "GameOver did not admit initials editor");
      key(highscores, SDL_SCANCODE_Z, true); // Held game input cannot become an initial.
      const std::string initials = repeat ? "RST" : "ABC";
      for (char letter : initials)
        key(highscores, SDL_Scancode(SDL_SCANCODE_A + letter - 'A'));
      key(highscores, SDL_SCANCODE_BACKSPACE);
      key(highscores, SDL_Scancode(SDL_SCANCODE_A + initials.back() - 'A'));
      // R is an ordinary initial while editing; no simulation reset or gameplay tick.
      require(simulation.game_over() && simulation.score() == final_score &&
                  simulation.shared_raw_state().fields == final_fields,
              "Initials input mutated gameplay");
      key(highscores, SDL_SCANCODE_RETURN, true);
      require(highscores.editing, "Repeated Return saved highscore");
      key(highscores, SDL_SCANCODE_RETURN);
      require(!highscores.editing && highscores.error.empty() && highscores.entries().size() == 1 &&
                  highscores.entries()[0].initials == initials && highscores.entries()[0].score == final_score,
              "Saved initials/score differ");
      for (unsigned i = 0; i < 64; ++i) {
        require(!highscores.begin(final_score), "GameOver admitted duplicate score");
        require(!simulation.step() && simulation.score() == final_score &&
                    simulation.shared_raw_state().fields == final_fields,
                "GameOver state changed after confirmation");
      }
      require(!std::filesystem::exists(destination.string() + ".tmp"), "Atomic save left temporary file");
      MeanHighscores loaded;
      loaded.load_path(destination);
      require(loaded.error.empty() && loaded.entries().size() == 1 &&
                  loaded.entries()[0].initials == initials && loaded.entries()[0].score == final_score,
              "Persisted highscore reload differs");
      simulation.reset();
      highscores.reset_session();
      require(!simulation.game_over() && simulation.score() == 0 && simulation.switch_rewards() == 0 &&
                  simulation.bonus_completions() == 0 && !highscores.editing && highscores.entries().size() == 1,
              "New game reset or retained highscore differs");
      require(!highscores.begin(simulation.score()), "Zero-point new game admitted a highscore");
      // Confirm that the fresh game actually advances after the modal lifecycle.
      simulation.set_launch(false);
      simulation.set_flippers(false, false);
      require(simulation.step() && !simulation.game_over(), "New game did not resume stepping");
      cases.push_back({{"name", repeat ? "rst-initial-includes-reset-key" : "abc-initials"},
                       {"legal_gameplay_ticks", ticks}, {"skillshot_rewards", 2},
                       {"bonus_completions", 3}, {"final_score", final_score},
                       {"initials", initials}, {"duplicate_gameover_frames", 64},
                       {"reloaded_entries", loaded.entries().size()}, {"new_game_advanced", true}});
    }
    std::ofstream report(argv[5]);
    report << json({{"scope", "Two fresh legal-input native Mean games through finite GameOver, actual SDL-scancode initials handler and isolated atomic highscore persistence, duplicate suppression and fresh-game step. This composes frontend APIs; main event-loop routing is tested separately."}, {"cases", cases}}).dump(2) << '\n';
    require(bool(report), "Cannot write frontend lifecycle report");
    std::cout << "PASS frontend lifecycle twice: legal GameOver / initials / persistence / new game\n";
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
