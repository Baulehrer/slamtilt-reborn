#include "rules/mean_ball_reset.h"
#include <iostream>
#include <nlohmann/json.hpp>
using nlohmann::json;
int main() {
  json batch;
  std::cin >> batch;
  json out = json::array();
  for (auto &c : batch) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    s.player_record = c["record"].get<decltype(s.player_record)>();
    s.field_43ee1c = c["ee1c"].get<decltype(s.field_43ee1c)>();
    s.field_438a40 = c["a40"];
    s.field_438af4 = c["af4"];
    s.field_438af8 = c["af8"];
    s.field_438b44 = c["b44"];
    s.field_438b4c = c["b4c"];
    s.table_mode = c["mode"];
    s.engine_3c = c["engine3c"];
    slam::MeanBallResetEvents e;
    slam::mean_ball_reset(s, e);
    slam::mean_ball_save(s);
    out.push_back(json{{"saved_record", s.player_record},
                       {"fields", s.fields},
                       {"ee1c", s.field_43ee1c},
                       {"a40", s.field_438a40},
                       {"af4", s.field_438af4},
                       {"af8", s.field_438af8},
                       {"b44", s.field_438b44},
                       {"b4c", s.field_438b4c},
                       {"calls", {"0x416fe0", "0x100fff4"}}});
  }
  std::cout << out.dump() << '\n';
}
