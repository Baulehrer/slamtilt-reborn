#include "physics/mean_upper_capture.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **) {
  slam::MeanObject ball;
  ball.put16(0x58, 3);
  ball.put16(0x5a, 1);
  slam::MeanUpperCaptureState state;
  if (argc > 1)
    state.field_43f394 = -1;
  if (argc > 2) {
    state.table_mode = 5;
    state.field_43f394 = 0;
    state.field_43f1f2 = 1;
  }
  nlohmann::json result = nlohmann::json::array();
  for (int tick = 0; tick < 1000; ++tick) {
    slam::MeanUpperCaptureEvent event;
    if (!slam::mean_upper_capture_tick(ball, state, event))
      return 2;
    if (tick % 4 == 3 && state.field_438b5c[0] >= 0)
      --state.field_438b5c[0];
    result.push_back({{"timer", state.field_43f36a},
                      {"field394", state.field_43f394},
                      {"slot1", state.field_438b5c},
                      {"score", event.score_request},
                      {"release", event.release_requested},
                      {"transfer", event.transfer_requested},
                      {"mode", state.table_mode},
                      {"field1f2", state.field_43f1f2}});
    if (event.release_requested || event.transfer_requested)
      break;
  }
  std::cout << result.dump();
}
