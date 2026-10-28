#include "physics/mean_mode5_left.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  auto result = nlohmann::json::array();
  for (int all = 0; all < 2; ++all)
    for (unsigned value : {0u, 16u, 32u})
      for (int selection = 0; selection < 3; ++selection) {
        slam::MeanMode5LeftState s;
        s.field_43f1e6 = selection;
        s.field_43f044.fill(11);
        s.field_43f372 = 12;
        s.field_43f38c = 13;
        s.field_43f386 = 14;
        s.field_43f3b4 = 15;
        s.field_43f39c = 16;
        s.field_43f05c = 17;
        s.field_43f058 = 18;
        s.field_43f384 = 19;
        if (all)
          s.field_43f1e0.fill(1);
        if (!slam::mean_mode5_begin(s, value))
          return 2;
        result.push_back({{"044", s.field_43f044},
                          {"372", s.field_43f372},
                          {"38c", s.field_43f38c},
                          {"386", s.field_43f386},
                          {"3b4", s.field_43f3b4},
                          {"39c", s.field_43f39c},
                          {"05c", s.field_43f05c},
                          {"058", s.field_43f058},
                          {"384", s.field_43f384},
                          {"1e0", s.field_43f1e0}});
      }
  std::cout << result.dump();
}
