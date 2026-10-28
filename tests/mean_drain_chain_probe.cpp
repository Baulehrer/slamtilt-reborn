#include "dmd/mean_bonus_pixels.h"
#include "physics/mean_step.h"
#include "rules/mean_ball_reset.h"
#include "rules/mean_bonus_display.h"
#include "rules/mean_bonus_turn.h"
#include "rules/mean_turn_entry.h"
#include <iostream>
#include <nlohmann/json.hpp>
using nlohmann::json;
int main() {
  json input;
  std::cin >> input;
  auto output = json::array();
  for (const auto &c : input) {
    slam::MeanObject b;
    b.bytes = c.at("ball").get<decltype(b.bytes)>();
    slam::MeanBallResetState reset;
    reset.fields = c.at("fields").get<decltype(reset.fields)>();
    reset.engine_3c = c.at("engine3c");
    slam::MeanTurnEntry entry;
    entry.field_43f3ae = c.at("timer");
    slam::MeanBonusTurn turn;
    turn.field_player_08 = c.at("bonus");
    turn.field_player_10 = c.at("extra");
    turn.field_player_12 = c.at("multiplier");
    turn.field_player_14 = c.at("held");
    slam::MeanBonusDisplay display;
    slam::MeanBonusTableState table;
    unsigned mode = 2;
    std::uint32_t score = 0;
    auto rows = json::array();
    auto put = [&](unsigned off, std::uint32_t v) {
      for (unsigned j = 0; j < 4; ++j)
        reset.fields[off + j] = v >> (j * 8);
    };
    auto snapshot = [&]() {
      rows.push_back(json{
          {"ball", b.bytes},
          {"fields", reset.fields},
          {"record", reset.player_record},
          {"mode", mode},
          {"score", score},
          {"bonus", turn.field_player_08},
          {"ball_number", turn.field_player_0e},
          {"extra", turn.field_player_10},
          {"multiplier", turn.field_player_12},
          {"held", turn.field_player_14},
          {"display",
           {display.phase, display.timer, display.step, display.field_43e734,
            display.bonus_total, display.field_43e718}}});
    };
    const bool saved = slam::mean_turn_drain_intercept(b, entry, c.at("count"),
                                                       c.at("services"));
    reset.fields[0x3ae] = entry.field_43f3ae;
    reset.fields[0x3af] = std::uint16_t(entry.field_43f3ae) >> 8;
    std::copy(entry.command_43f260.begin(), entry.command_43f260.end(),
              reset.fields.begin() + 0x260);
    snapshot();
    if (saved) {
      slam::mean_initialize_ball(b, 0x1100000);
      snapshot();
      output.push_back(rows);
      continue;
    }
    slam::mean_ball_save(reset);
    mode = 3;
    b.put16(0x58, 0xffff);
    snapshot();
    if (c.value("fast", false)) {
      slam::mean_bonus_input_edge(display, false, true);
      slam::mean_bonus_input_edge(display, true, true);
    }
    bool finish = false;
    for (unsigned tick = 0; tick < 500 && !finish; ++tick) {
      slam::MeanBonusDisplayInput in;
      in.bonus = turn.field_player_08;
      in.multiplier = turn.field_player_12;
      in.suppressed = c.at("suppressed");
      const auto phase =
          display.field_43e734 == 3 && display.phase == 1 ? 2u : display.phase;
      if (phase == 0)
        slam::mean_bonus_table_callback(table, 0);
      if (phase <= 1)
        in.callback_result = slam::mean_bonus_table_callback(table, 1).result;
      else if (phase == 4)
        in.callback_result = slam::mean_bonus_table_callback(table, 2).result;
      auto event = slam::mean_bonus_display_step(display, in);
      if (event.award)
        score += event.score_argument;
      finish = event.finish;
      put(0x28, table.field_43f028);
      put(0x2c, table.field_43f02c);
      snapshot();
    }
    if (!finish)
      return 2;
    slam::mean_finish_bonus_turn(turn);
    reset.table_mode = 3;
    slam::MeanBallResetEvents events;
    slam::mean_ball_reset(reset, events);
    mode = 1;
    snapshot();
    slam::mean_initialize_ball(b, 0x1100000);
    snapshot();
    output.push_back(rows);
  }
  std::cout << output.dump() << '\n';
}
