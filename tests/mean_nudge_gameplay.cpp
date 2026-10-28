#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
#include <string>

using nlohmann::json;

static std::string raw(const slam::MeanObject &ball) {
  constexpr char digits[] = "0123456789abcdef";
  std::string result;
  for (auto byte : ball.bytes) {
    result += digits[byte >> 4];
    result += digits[byte & 15];
  }
  return result;
}

static json run(char **argv, unsigned entry, unsigned warmup, int horizontal,
                bool upward) {
  slam::MeanSimulation s(argv[1], argv[2], argv[3]);
  s.set_continuous_play(true);
  if (entry == 1)
    s.debug_start_point_force();
  else if (entry == 2)
    s.debug_start_right_route(true);
  s.set_launch(true);
  for (unsigned tick = 0; tick < warmup; ++tick)
    if (!s.step())
      throw std::runtime_error(std::string("Nudge warmup: ") + s.status());
  json states = json::array(), wave = json::array();
  const auto initial = raw(s.ball());
  // One key-down request. Holding a key must not become one request per tick.
  if (horizontal || upward)
    s.nudge(horizontal, upward);
  for (unsigned tick = 1; tick <= 100; ++tick) {
    if (!s.step())
      throw std::runtime_error(std::string("Nudge step: ") + s.status());
    if (s.tilted() || s.game_over())
      throw std::runtime_error("Single nudge unexpectedly tilted/ended game");
    const auto &n = s.nudge_state();
    states.push_back(raw(s.ball()));
    wave.push_back(
        {n.field_43e724, n.field_43e564, n.field_43e71c, n.field_43e410});
  }
  return {{"entry", entry},
          {"warmup_steps", warmup},
          {"horizontal", horizontal},
          {"upward", upward},
          {"initial_raw", initial},
          {"tick_count", 100},
          {"final_raw", raw(s.ball())},
          {"states", states},
          {"wave", wave},
          {"collisions", s.collisions()},
          {"score", s.score()}};
}

int main(int argc, char **argv) {
  if (argc != 4)
    return 2;
  try {
    json cases = json::array();
    for (unsigned direction = 0; direction < 3; ++direction) {
      bool influenced_ball = false;
      // Bounded observations around the established initial contact window.
      // No random search or fitted force constants.
      for (unsigned warmup : {48u, 64u, 96u}) {
        if (influenced_ball)
          break;
        for (unsigned entry = 0; entry < 3 && !influenced_ball; ++entry) {
          const int horizontal = direction == 2 ? 0 : direction == 0 ? -1 : 1;
          const bool upward = direction == 2;
          const auto baseline = run(argv, entry, warmup, 0, false);
          const auto baseline_repeat = run(argv, entry, warmup, 0, false);
          if (baseline != baseline_repeat)
            throw std::runtime_error("No-input baseline repeat differs");
          auto nudged = run(argv, entry, warmup, horizontal, upward);
          if (nudged != run(argv, entry, warmup, horizontal, upward))
            throw std::runtime_error("100-step nudge repeat differs");
          bool active_wave = false;
          for (const auto &w : nudged["wave"])
            for (const auto &value : w)
              active_wave |= value.get<int>() != 0;
          if (!active_wave)
            throw std::runtime_error("Nudge request never reached waveform");
          influenced_ball = baseline["states"] != nudged["states"];
          if (influenced_ball) {
            nudged["baseline_final_raw"] = baseline["final_raw"];
            nudged["ball_state_differs_from_baseline"] = true;
            cases.push_back(nudged);
          }
        }
      }
      if (!influenced_ball)
        throw std::runtime_error(
            "Nudge waveform never affected any tested ball entry");
    }
    slam::MeanSimulation tilt(argv[1], argv[2], argv[3]);
    tilt.debug_nudge_warning(); // Proven human mode2, not a pre-tilted setup.
    tilt.nudge(-1);
    if (tilt.tilted())
      throw std::runtime_error("First nudge tilted");
    tilt.nudge(1);
    if (tilt.tilted())
      throw std::runtime_error("Second nudge tilted");
    tilt.nudge(0, true);
    if (!tilt.tilted())
      throw std::runtime_error("Third rapid nudge did not tilt");
    tilt.reset();
    const auto &n = tilt.nudge_state();
    if (tilt.tilted() || n.field_43e724 || n.field_43e564 || n.field_43e71c ||
        n.field_43e410 || n.field_42985c != -1 || n.field_429810 != -1)
      throw std::runtime_error("Reset retained tilt/waveform state");
    json source_trace;
    std::ifstream(argv[3]) >> source_trace;
    std::ofstream("analysis/traces/mean-nudge-gameplay.json")
        << json{{"build_sha256", source_trace.at("build_sha256")},
                {"tick_hz", 200},
                {"original_wiring_evidence",
                 "analysis/traces/mean-nudge-wiring-original.json"},
                {"scope", "Native integration: finite 100-step entries, paired "
                          "deterministic repeats, waveform-to-ball coupling "
                          "and rapid-input Tilt/reset; NOT an original "
                          "whole-table trajectory"},
                {"entry_names",
                 {"launcher", "point_force", "right_empty_switch"}},
                {"wave_fields",
                 {"field_43e724", "field_43e564", "field_43e71c",
                  "field_43e410"}},
                {"rapid_nudges_to_tilt", 3},
                {"reset_cleared", true},
                {"cases", cases}}
               .dump(2)
        << '\n';
    std::cout << "PASS three nudge directions, deterministic 100-step ball "
                 "coupling, Tilt/reset\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
