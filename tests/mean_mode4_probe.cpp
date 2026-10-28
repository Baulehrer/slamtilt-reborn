#include "physics/mean_mode5_clock.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  slam::MeanMode5LeftState m;
  slam::MeanCaptureTickState c;
  m.field_43f366 = 0;
  m.field_43f1e6 = 4;
  c.table_mode = 5;
  if (!slam::mean_mode5_begin(m))
    return 2;
  auto result = nlohmann::json::array();
  auto snapshot = [&]() {
    return nlohmann::json{
        {"timer", m.field_43f376},    {"field36e", m.field_43f36e},
        {"field37e", m.field_43f37e}, {"field388", m.field_43f388},
        {"data", m.field_43f23c},     {"mode", c.table_mode},
        {"selected", m.field_43f1e6}, {"flags", m.field_43f1e0},
        {"field366", m.field_43f366}, {"engine40", m.field_engine_40},
        {"sum", m.field_43f058}};
  };
  result.push_back(snapshot());
  for (int i = 0; i < 801; ++i) {
    slam::mean_mode5_clock(m, c);
    result.push_back(snapshot());
  }
  std::cout << result.dump();
}
