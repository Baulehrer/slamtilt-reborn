#include "rules/mean_stock_car.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json in; std::cin >> in; auto out=nlohmann::json::array();
  for (const auto &c:in) {
    slam::MeanBallResetState s; s.fields=c.at("fields").get<decltype(s.fields)>();
    s.table_mode=c.at("mode");
    const auto e=slam::mean_stock_car_bumper(s,c.at("material"),c.at("suppressed"),c.at("handle"));
    out.push_back({{"fields",s.fields},{"mode",s.table_mode},{"score",e.score},{"callback",e.callback}});
  }
  std::cout<<out.dump();
}
