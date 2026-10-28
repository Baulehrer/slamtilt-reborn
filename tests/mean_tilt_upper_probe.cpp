#include "physics/mean_upper_capture.h"
#include "physics/mean_upper_release.h"
#include <iostream>
#include <nlohmann/json.hpp>
using namespace slam;
int main() {
  nlohmann::json cases; std::cin >> cases; auto out=nlohmann::json::array();
  for (const auto &c:cases) {
    MeanObject b; b.bytes=c["ball"].get<decltype(b.bytes)>();
    MeanUpperCaptureState s; s.table_mode=c["mode"]; s.field_43f36a=c["timer"];
    s.field_43f364=c["gate"]; s.field_43f394=0;s.field_43f1f2=0;
    s.field_438b5c=c["slot"].get<decltype(s.field_438b5c)>();
    MeanUpperCaptureEvent e;
    if (!mean_upper_capture_tilt_tick(b,s,e,0x1100000,c["random"])) return 2;
    unsigned samples=e.early_release_count;
    if(e.release_requested){mean_upper_release(b,0x1100000,c["random"]);++samples;}
    out.push_back({{"ball",b.bytes},{"timer",s.field_43f36a},{"gate",s.field_43f364},
      {"field394",s.field_43f394},{"field1f2",s.field_43f1f2},{"mode",s.table_mode},
      {"slot",s.field_438b5c},{"score",e.score_request},{"bonus",e.field_player_08_add},{"samples",samples}});
  }
  std::cout << out.dump();
}
