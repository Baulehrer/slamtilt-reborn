#include "physics/mean_capture_tick.h"
#include "physics/mean_reward_display.h"
#include "physics/mean_upper_capture.h"
#include "physics/mean_upper_release.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  slam::MeanObject ball;
  ball.put32(0, 14 * 65536);
  ball.put32(4, 14 * 65536);
  ball.put16(0x58, 3);
  ball.put16(0x5a, 1);
  slam::MeanUpperCaptureState upper;
  slam::MeanCaptureTickState lower;
  const bool reward2 = argc > 1;
  if (reward2)
    upper.field_43f202 = -1;
  else
    upper.field_43f200 = -1;
  slam::MeanRewardDisplay display;
  bool display_started = false;
  auto result = nlohmann::json::array();
  for (int tick = 0; tick < 1200 && ball.u16(0x58) == 3; ++tick) {
    std::uint32_t points = 0;
    if (ball.u16(0x5a) == 1) {
      slam::MeanUpperCaptureEvent event;
      if (!slam::mean_upper_capture_tick(ball, upper, event))
        return 2;
      points = event.score_request;
      if (event.reward_request) {
        display = {};
        display.last_frame = reward2 ? 159 : 168;
        display_started = true;
      }
      if (event.release_requested)
        slam::mean_upper_release(ball, 0x1100000, 0);
      if (event.transfer_requested) {
        slam::mean_upper_transfer(ball, 0x1100000);
        lower.field_438b50 = {0, 0, 5};
        lower.field_438b74[1] = 100;
      }
    } else {
      slam::MeanCaptureTickEvent event;
      lower.table_mode = upper.table_mode;
      if (!slam::mean_capture_tick(ball, lower, 0x1100000, event))
        return 3;
      points = event.score_request;
    }
    if (tick % 4 == 3)
      for (auto *slot :
           {&upper.field_438b5c, &lower.field_438b68, &lower.field_438b74})
        if ((*slot)[0] >= 0)
          --(*slot)[0];
    if (tick % 4 == 3 && display_started && upper.field_43f364 != 0)
      slam::mean_reward_display_tick(display, upper.field_43f364);
    result.push_back({{"ball", ball.bytes},
                      {"slot2", lower.field_438b68},
                      {"slot3", lower.field_438b74},
                      {"slot50", lower.field_438b50},
                      {"timer", upper.field_43f36a},
                      {"mode", upper.table_mode},
                      {"field1f2", upper.field_43f1f2},
                      {"field394", upper.field_43f394},
                      {"slot1", upper.field_438b5c},
                      {"gate", upper.field_43f364},
                      {"field204", lower.field_43f204},
                      {"score", points},
                      {"field200", upper.field_43f200},
                      {"field202", upper.field_43f202},
                      {"field378", upper.field_43f378},
                      {"field1fc", upper.field_43f1fc}});
  }
  std::cout << result.dump() << '\n';
}
