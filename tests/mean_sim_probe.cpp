#include "core/mean_diagnostic_input.h"
#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  try {
    if (argc < 5)
      return 2;
    slam::MeanSimulation simulation(argv[1], argv[2], argv[3]);
    if (argc >= 6) {
      simulation.reset();
      std::string scenario = argv[5];
      if (scenario == "point-force")
        simulation.debug_start_point_force();
      if (scenario == "mode4-upper")
        simulation.debug_start_mode4_upper();
      if (scenario == "mode4")
        simulation.debug_start_mode4();
      if (scenario == "mode4-right" || scenario == "minigame2")
        simulation.debug_start_mode4_right(scenario == "minigame2");
      if (scenario == "right-cancel")
        simulation.debug_start_right_cancel();
      if (scenario == "right-empty")
        simulation.debug_start_right_route(true);
      if (scenario == "right-route")
        simulation.debug_start_right_route();
      if (scenario == "mode6")
        simulation.debug_start_multiball(false, true);
      if (scenario == "multiball")
        simulation.debug_start_multiball();
      if (scenario == "mode5")
        simulation.debug_start_rule_capture(argc >= 7 &&
                                            std::stoi(argv[6]) != 0);
      if (scenario == "minigame")
        simulation.debug_start_minigame();
      simulation.set_continuous_play(true);
      simulation.set_endless_play(scenario != "finite");
    }
    std::ifstream file(argv[3]);
    nlohmann::json trace;
    file >> trace;
    bool route_trace = argc >= 8 && std::string(argv[7]) == "route-trace";
    bool advanced_trace = argc >= 8 && std::string(argv[7]) == "advanced-trace";
    bool summary = advanced_trace || route_trace ||
                   (argc >= 8 && std::string(argv[7]) == "summary"),
         active = true, bonus_ball_frozen = true;
    unsigned states = 0, bonus_frozen_steps = 0;
    const std::string input_profile = argc >= 9 ? argv[8] : "periodic";
    if (input_profile != "periodic" && input_profile != "random" &&
        input_profile != "held" && input_profile != "passive" &&
        input_profile != "alternating" && input_profile != "finite-shot" && input_profile != "periodic-no-bonus")
      throw std::runtime_error("Unknown test input profile");
    slam::MeanDiagnosticInput diagnostic_input(argc >= 7 ? std::stoul(argv[6])
                                                         : 0);
    std::uint64_t input_hash = 14695981039346656037ull;
    auto values = nlohmann::json::array();
    auto route_events = nlohmann::json::array();
    auto advanced_events = nlohmann::json::array();
    std::array<unsigned, 7> advanced_previous{};
    bool advanced_minigame_result=false;
    int advanced_mode = -1, advanced_selected = -1;
    unsigned old_arms = 0, old_markers = 0, old_captures = 0;
    bool old_armed = false;
    std::uint16_t old_mask = 0xffff, old_layer = 0xffff;
    for (int i = 0; i <= std::stoi(argv[4]); ++i) {
      if (argc >= 6) {
        simulation.set_launch(true);
        int seed = argc >= 7 ? std::stoi(argv[6]) : 0;
        if (std::string(argv[5]) == "point-force")
          simulation.set_flippers(false, false);
        else {
          bool left = (i + seed * 13) % (100 + seed * 7) < 40;
          bool right = (i + seed * 17) % (140 + seed * 11) < 60;
          if (input_profile == "random") {
            const auto keys = diagnostic_input.next();
            left = keys[0];
            right = keys[1];
          } else if (input_profile == "held")
            left = right = true;
          else if (input_profile == "passive")
            left = right = false;
          else if (input_profile == "alternating") {
            left = (i / (30 + seed * 3)) % 2;
            right = !left;
          }
          if (input_profile == "finite-shot") {
            const auto k = slam::mean_finite_shot_input(i, simulation.ball().i32(4) >> 16, seed);
            left = k[0]; right = k[1];
          }
          // Stable route tests isolate target/contact coverage from bonus skip
          // input.
          if (input_profile == "periodic-no-bonus" && simulation.bonus_active())
            right = false;
          simulation.set_flippers(left, right);
          input_hash =
              (input_hash ^ unsigned(left | (right << 1))) * 1099511628211ull;
        }
      }
      if (argc == 5 && i < int(trace.at("samples").size())) {
        auto &v = trace["samples"][i];
        if (v.contains("oracle_context")) {
          auto &c = v["oracle_context"];
          simulation.set_original_contact_context(
              c["flipper_words"].get<std::vector<std::uint32_t>>(),
              c["engine_global_words"].get<std::vector<std::uint32_t>>());
        }
      }
      const auto &b = simulation.ball();
      if (advanced_trace) {
        const std::array<unsigned, 7> counters{
            simulation.captures(),         simulation.releases(),
            simulation.minigame_starts(),  simulation.minigame_completions(),
            simulation.multiball_spawns(), simulation.mode6_starts(),
            simulation.ball_number()};
        const bool terminal_result=simulation.material5_display_callback()==0x40f994 || simulation.material5_display_callback()==0x40fb78;
        if (terminal_result!=advanced_minigame_result || counters != advanced_previous ||
            simulation.table_mode() != advanced_mode ||
            simulation.selected_mode() != advanced_selected) {
          auto e = nlohmann::json{{"step", i},
                                  {"counters", counters},
                                  {"mode", simulation.table_mode()},
                                  {"selected", simulation.selected_mode()},
                                  {"score", simulation.score()},
                                  {"ball", b.bytes},
                                  {"count", simulation.ball_count()},
                                  {"input_hash", input_hash}};
          const auto &d=simulation.display_scheduler();
          e["display"]={simulation.material5_display_callback(),simulation.material5_display_counter(),
              d.field_780,d.field_784,d.field_788,d.field_790,d.field_7b4};
          if (counters[2] != advanced_previous[2] ||
              counters[3] != advanced_previous[3] ||
              counters[4] != advanced_previous[4])
            e["cached_shared_fields"] = simulation.shared_raw_state().fields;
          advanced_events.push_back(e);
        }
        advanced_minigame_result=terminal_result;
        advanced_previous = counters;
        advanced_mode = simulation.table_mode();
        advanced_selected = simulation.selected_mode();
      }
      ++states;
      if (route_trace &&
          (simulation.right_route_armed() != old_armed ||
           simulation.right_arms() != old_arms ||
           simulation.right_markers() != old_markers ||
           simulation.right_captures() != old_captures ||
           ((simulation.right_route_armed() || old_armed) &&
            (b.u16(0x38) != old_mask || b.u16(0x48) != old_layer)))) {
        route_events.push_back(
            {{"step", i},
             {"x", b.i32(0)},
             {"y", b.i32(4)},
             {"vx", b.i32(0x14)},
             {"vy", b.i32(0x18)},
             {"mask", b.u16(0x38)},
             {"layer", b.u16(0x48)},
             {"field_5c", b.u16(0x5c)},
             {"armed", simulation.right_route_armed()},
             {"cancellations", simulation.right_cancellations()},
             {"mode", simulation.table_mode()},
             {"arms", simulation.right_arms()},
             {"markers", simulation.right_markers()},
             {"captures", simulation.right_captures()}});
      }
      old_armed = simulation.right_route_armed();
      old_arms = simulation.right_arms();
      old_markers = simulation.right_markers();
      old_captures = simulation.right_captures();
      old_mask = b.u16(0x38);
      old_layer = b.u16(0x48);
      if (!summary)
        values.push_back({{"step", i},
                          {"score", simulation.score()},
                          {"score_events", simulation.score_events()},
                          {"switch_mask", b.u16(0x38)},
                          {"x", b.i32(0)},
                          {"y", b.i32(4)},
                          {"vx", b.i32(0x14)},
                          {"vy", b.i32(0x18)},
                          {"layer", b.u16(0x48)},
                          {"state", b.u16(0x58)}});
      if (i < std::stoi(argv[4])) {
        auto old = b.bytes;
        bool bonus = simulation.bonus_active();
        active = simulation.step();
        if (bonus && simulation.bonus_active()) {
          ++bonus_frozen_steps;
          bonus_ball_frozen &= old == simulation.ball().bytes;
        }
        if (!active)
          break;
      }
    }
    const auto &b = simulation.ball();
    std::array<std::uint32_t, 25> raw{};
    for (unsigned i = 0; i < 25; ++i)
      raw[i] = b.i32(i * 4);
    nlohmann::json result = {
        {"active", active},
        {"states", states},
        {"samples", values},
        {"status", simulation.status()},
        {"final_raw_words", raw},
        {"final_x", b.i32(0)},
        {"final_y", b.i32(4)},
        {"field_38", b.u16(0x38)},
        {"layer", b.u16(0x48)},
        {"material", b.u16(0x3c)},
        {"lamp_updates", simulation.lamp_updates()},
        {"switch_reward_variants", simulation.switch_reward_variants()},
        {"bonus_ball_frozen", bonus_ball_frozen},
        {"bonus_frozen_steps", bonus_frozen_steps}};
    if (route_trace)
      result["route_events"] = route_events;
    result["input_profile"] = input_profile;
    result["input_fnv"] = std::to_string(input_hash);
    result["game_over"] = simulation.game_over();
    result["score"] = simulation.score();
    result["score_events"] = simulation.score_events();
    result["material5_display_callback"] =
        simulation.material5_display_callback();
    result["material5_display_counter"] =
        simulation.material5_display_counter();
    result["point_force_type"] = simulation.point_force_type();
    result["point_force_updates"] = simulation.point_force_updates();
    result["right_cancellations"] = simulation.right_cancellations();
    result["right_route_armed"] = simulation.right_route_armed();
    result["right_arms"] = simulation.right_arms();
    result["right_markers"] = simulation.right_markers();
    result["right_captures"] = simulation.right_captures();
    result["mode4_starts"] = simulation.mode4_starts();
    result["mode4_completions"] = simulation.mode4_completions();
    result["state7_steps"] = simulation.state7_steps();
    result["pending_mode4_rewards"] = simulation.pending_mode4_rewards();
    result["switch_rewards"] = simulation.switch_rewards();
    result["side_extra_balls"] = simulation.side_extra_balls();
    result["award_bank_starts"] = simulation.award_bank_starts();
    result["award_bank_awards"] = simulation.award_bank_awards();
    result["material5_hits"] = simulation.material5_hits();
    result["material5_groups"] = simulation.material5_groups();
    result["top_target_hits"] = simulation.top_target_hits();
    result["top_target_cycles"] = simulation.top_target_cycles();
    result["bonus_phase"] = simulation.bonus_phase();
    result["bonus_display_ticks"] = simulation.bonus_display_ticks();
    result["bonus_completions"] = simulation.bonus_completions();
    result["bonus_starts"] = simulation.bonus_starts();
    result["bonus_awards"] = simulation.bonus_awards();
    result["last_bonus"] = simulation.last_bonus();
    result["pending_bonus"] = simulation.pending_bonus();
    result["drains"] = simulation.drains();
    result["captures"] = simulation.captures();
    result["upper_captures"] = simulation.upper_captures();
    result["mode5_awards"] = simulation.mode5_awards();
    result["mode_resets"] = simulation.mode_resets();
    result["ball_saves"] = simulation.ball_saves();
    result["restart_gate"] = simulation.restart_gate();
    result["restart_initializations"] = simulation.restart_initializations();
    result["restart_waits"] = simulation.restart_waits();
    result["minigame_starts"] = simulation.minigame_starts();
    result["minigame_completions"] = simulation.minigame_completions();
    result["return_passes"] = simulation.return_passes();
    result["return_pass_awards"] = simulation.return_pass_awards();
    result["reward_requests"] = simulation.reward_requests();
    result["reward_completions"] = simulation.reward_completions();
    result["advanced_events"] = advanced_events;
    result["selected_mode"] = simulation.selected_mode();
    result["table_mode"] = simulation.table_mode();
    result["releases"] = simulation.releases();
    result["ball_number"] = simulation.ball_number();
    result["events"] = simulation.events();
    result["launches"] = simulation.launches();
    result["ball_count"] = simulation.ball_count();
    result["max_balls"] = simulation.max_balls();
    result["mode6_starts"] = simulation.mode6_starts();
    result["multiball_spawns"] = simulation.multiball_spawns();
    result["collisions"] = simulation.collisions();
    bool frozen = false, restored = false;
    if (simulation.game_over()) {
      auto old = simulation.ball().bytes;
      auto score = simulation.score();
      frozen = true;
      for (unsigned i = 0; i < 10; ++i) {
        simulation.step();
        frozen &= old == simulation.ball().bytes && score == simulation.score();
      }
      simulation.reset();
      restored = !simulation.game_over() && simulation.ball_count() == 1 &&
                 simulation.table_mode() == 1 && simulation.ball_number() == 1;
    }
    result["game_over_frozen"] = frozen;
    result["new_game_restored"] = restored;
    std::cout << result.dump();
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
