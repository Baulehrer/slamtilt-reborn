#include "core/mean_diagnostic_input.h"
#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
int main(int argc, char **argv) {
  if (argc != 5)
    return 2;
  try {
    nlohmann::json input;
    std::ifstream(argv[4]) >> input;
    nlohmann::json palette_reference, original_trace;
    std::ifstream(std::filesystem::path(argv[4]).parent_path() /
        "mean-minigame-retail-terminal-pixels.json") >> palette_reference;
    std::ifstream(argv[3]) >> original_trace;
    auto cases = nlohmann::json::array();
    for (unsigned scenario = 0; scenario < 9; ++scenario)
      for (unsigned repeat = 0; repeat < 2; ++repeat) {
        const bool route = scenario >= 6, first_route = scenario >= 7,
                   second = scenario >= 4 && !first_route,
                   retail = route || (scenario >= 2 && !second),
                   abort = first_route ? scenario == 8 : scenario % 2;
        unsigned route_steps = 0;
        auto route_keys = nlohmann::json::array(), replay_keys = nlohmann::json::array();
        unsigned replay_index = 0, replay_remaining = 0, replay_action = 0;
        bool lock_key_released = false;
        if (first_route && repeat) {
          nlohmann::json replay;
          std::ifstream(std::filesystem::path(argv[4]).parent_path() /
              (abort ? "mean-first-minigame-natural-finite-abort.json" : "mean-first-minigame-natural-finite-win.json")) >> replay;
          replay_keys = replay.at("entry_actions_rle");
        }
        slam::MeanSimulation s(argv[1], argv[2], argv[3]);
        s.set_retail_minigame(retail);
        s.reset();
        const auto initial_ball_state = s.ball().bytes;
        if (route) {
          s.set_continuous_play(true);
          s.set_launch(true);
          for (unsigned step = 0; step < 80000 && !s.minigame_active();
               ++step) {
            auto k = first_route
                ? slam::mean_first_minigame_input(step, s.ball().i32(4) >> 16)
                : slam::mean_finite_shot_input(step, s.ball().i32(4) >> 16);
            bool lock = first_route && step >= 11612 && s.selected_mode() == 3 && !s.mode_locked() &&
                (s.table_mode() == 2 || s.table_mode() == 3);
            bool launch = true;
            // Return is also held launch: release one tick before a fresh lock edge.
            if (lock && !lock_key_released) {
              lock_key_released = true;
              lock = false; launch = false;
            }
            if (!replay_keys.empty()) {
              if (!replay_remaining) {
                if (replay_index == replay_keys.size())
                  throw std::runtime_error("Recorded entry inputs exhausted before capture");
                const auto &r = replay_keys.at(replay_index++);
                replay_remaining = r.at("ticks").get<unsigned>();
                replay_action = r.at("actions").get<unsigned>();
                if (!replay_remaining)
                  throw std::runtime_error("Invalid recorded launch/input run");
              }
              --replay_remaining;
              k = {bool(replay_action & 1u), bool(replay_action & 2u)};
              lock = replay_action & 4u;
              launch = replay_action & 8u;
            }
            if (first_route) s.set_launch(launch);
            if (lock) s.press_plunger();
            const unsigned action = unsigned(k[0]) | (unsigned(k[1]) << 1) | (unsigned(lock) << 2) | (unsigned(launch) << 3);
            if (first_route) {
              if (!route_keys.empty() && route_keys.back().at("actions") == action)
                route_keys.back()["ticks"] = route_keys.back().at("ticks").get<unsigned>() + 1;
              else route_keys.push_back({{"actions", action}, {"ticks", 1}});
            }
            ++route_steps;
            s.set_flippers(k[0], k[1]);
            if (!s.step())
              throw std::runtime_error("scenario " + std::to_string(scenario) + ": " + s.status());
            s.take_audio_requests();
          }
          if (!replay_keys.empty() && (replay_remaining || replay_index != replay_keys.size() || route_keys != replay_keys))
            throw std::runtime_error("Recorded key replay reached a different entry boundary");
          if (!s.minigame_active() || s.minigame2_active() != second || s.ball_number() > 3)
            throw std::runtime_error("Natural finite selected-minigame entry missing");
        } else if (second)
          s.debug_start_mode4_right(true);
        else if (!s.debug_start_minigame())
          throw std::runtime_error("scenario " + std::to_string(scenario) + ": " + s.status());
        s.set_continuous_play(true);
        s.set_endless_play(false);
        s.set_launch(true);
        const auto captured_ball_state = s.ball().bytes;
        const auto before = s.score();
        const auto entry_ball = s.ball_number();
        const unsigned award =
            route && second ? 30000000
            : second ? (abort ? 500000 : 30500000)
                     : (abort ? (retail ? 40000000 : 20000000) : 120000000);
        for (unsigned guard = 0; guard < 20000 && !s.minigame_completions();
             ++guard) {
          if (second) {
            const unsigned period = abort ? 20 : 5;
            s.set_flippers((guard / period) % 2, ((guard / period) + 1) % 2);
          } else {
            auto tick = s.minigame_steps();
            auto k = abort && tick >= 1082
                         ? 0u
                         : input.at("keys").at(tick).get<unsigned>();
            s.set_flippers(k == 1, k == 2);
          }
          if (!s.step())
            throw std::runtime_error("scenario " + std::to_string(scenario) + ": " + s.status());
          s.take_audio_requests();
        }
        if (s.minigame_active() || s.minigame_completions() != 1 ||
            s.score() != before + award)
          throw std::runtime_error(
              "Finite minigame award mismatch scenario=" +
              std::to_string(scenario) +
              " delta=" + std::to_string(s.score() - before) +
              " callback=" + std::to_string(s.material5_display_callback()));
        const auto callback = second ? (abort ? 0x41210cu : 0x4122ccu)
                                     : (abort ? 0x40f994u : 0x40fb78u);
        if (s.material5_display_callback() != callback)
          throw std::runtime_error("Result callback missing");
        const auto releases = s.releases();
        bool retired = false, released = false;
        unsigned steps = 0, frozen_bonus = 0, result_pixel_checks = 0;
        slam::MeanDiagnosticInput keys(0);
        for (; steps < 200000 && !s.game_over(); ++steps) {
          auto k = keys.next();
          s.set_flippers(k[0], k[1]);
          const bool bonus = s.bonus_active();
          const auto ball = s.ball().bytes;
          if (!s.step() && !s.game_over())
            throw std::runtime_error("scenario " + std::to_string(scenario) + ": " + s.status());
          s.take_audio_requests();
          if (first_route && s.material5_display_callback() == callback && s.material5_display_counter()) {
            const auto count = s.material5_display_counter();
            std::uint64_t hash = 14695981039346656037ull;
            for (auto v : s.material5_pixels()) hash = (hash ^ v) * 1099511628211ull;
            const auto &expected = palette_reference.at("expected").at(abort ? 1 : 5).at(count - 1);
            if (std::to_string(hash) != expected.at("fnv") || !expected.at("active").get<bool>())
              throw std::runtime_error("Natural finite result differs from original DMD pixels");
            ++result_pixel_checks;
          }
          if (bonus && s.bonus_active()) {
            if (ball != s.ball().bytes)
              throw std::runtime_error("Bonus moved ball");
            ++frozen_bonus;
          }
          retired |= s.material5_display_callback() != callback;
          released |= s.releases() > releases;
        }
        if (!s.game_over() || !retired || !released || !frozen_bonus ||
            s.ball_count() != 0 || s.table_mode() != 0 ||
            s.bonus_starts() < 3 || s.bonus_starts() != s.bonus_completions() ||
            s.bonus_completions() != s.bonus_awards())
          throw std::runtime_error(
              "Finite result/release/bonus/GameOver chain incomplete");
        if (first_route && !result_pixel_checks)
          throw std::runtime_error("Natural finite result pixels were not checked");
        const auto score = s.score();
        const auto ball = s.ball().bytes;
        for (unsigned i = 0; i < 40; ++i) {
          s.step();
          if (s.score() != score || s.ball().bytes != ball)
            throw std::runtime_error("GameOver not frozen");
        }
        nlohmann::json result = {{"natural_finite_entry", route},
                                 {"route_steps", route_steps},
                                 {"result_pixel_checks", result_pixel_checks},
                                 {"second_minigame", second},
                                 {"retail", retail},
                                 {"abort", abort},
                                 {"award", award},
                                 {"entry_ball", entry_ball},
                                 {"score_before", before},
                                 {"score", score},
                                 {"steps_after_result", steps},
                                 {"releases", s.releases()},
                                 {"bonus_completions", s.bonus_completions()},
                                 {"bonus_frozen_steps", frozen_bonus},
                                 {"ball_number", s.ball_number()}};
        if (repeat && result != cases.back())
          throw std::runtime_error("Finite lifecycle repeat differs");
        cases.push_back(result);
        if (first_route && !repeat) {
          std::ofstream(std::filesystem::path(argv[4]).parent_path() /
              (abort ? "mean-first-minigame-natural-finite-abort.json" : "mean-first-minigame-natural-finite-win.json"))
              << nlohmann::json{{"scope", "Native finite game from reset; SDL-equivalent keys only; no diagnostic placement, endless mode or original whole-table trajectory claim"},
                  {"table", "Mean Machines"}, {"mode", "Formula 1 Race"},
                  {"build_sha256", original_trace.at("build_sha256")},
                  {"initial_ball_bytes", initial_ball_state}, {"captured_ball_bytes", captured_ball_state},
                  {"final_ball_bytes", ball}, {"entry_actions_rle", route_keys}, {"action_bits", {{"left",1},{"right",2},{"mode_lock_press",4},{"launch_held",8}}},
                  {"result", result}, {"winning_input", "mean-minigame1-winning-input.json"},
                  {"completion_oracle", "mean-minigame-retail-original.json"}}.dump(2) << '\n';
        }
        s.reset();
        if (s.game_over() || s.score() != 0 || s.ball_count() != 1 ||
            s.ball_number() != 1 || s.table_mode() != 1 ||
            s.minigame_completions() != 0)
          throw std::runtime_error("New game restoration failed");
      }
    std::ofstream(std::filesystem::path(argv[4]).parent_path() /
                  "mean-minigame-finite.json")
        << nlohmann::
               json{{"scope",
                     "Twelve diagnostic entry cases plus six natural finite entries: "
                     "second-minigame win and first-minigame Retail win/abort, each repeated; "
                     "real steering then finite native lifecycle; no original whole-table trajectory claim"},
                    {"cases", cases}}
                   .dump(2)
        << '\n';
    std::cout << "PASS eighteen finite minigame win/abort lifecycle cases, "
                 "repeats, bonus freeze, GameOver and new-game reset\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
