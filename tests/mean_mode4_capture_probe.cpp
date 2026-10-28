#include "physics/mean_mode4_capture.h"
#include <iostream>
#include <nlohmann/json.hpp>
using namespace slam;
int main() {
  nlohmann::json j;
  std::cin >> j;
  auto out = nlohmann::json::array();
  for (auto &c : j) {
    MeanObject b;
    b.bytes = c["ball"].get<decltype(b.bytes)>();
    MeanCaptureTickState s;
    s.field_438b68 = c["slot2"].get<decltype(s.field_438b68)>();
    s.field_438b74 = c["slot3"].get<decltype(s.field_438b74)>();
    s.field_43f380 = c["timer"];
    s.field_43f364 = c["gate"];
    s.field_43f392 = c["armed"];
    s.table_mode = c["mode"];
    MeanBallResetState raw;
    raw.fields = c["raw"].get<decltype(raw.fields)>();
    raw.table_mode = s.table_mode;
    MeanMultiballReleaseState r;
    r.slot = c["slot5"].get<decltype(r.slot)>();
    MeanBallPool p;
    p.count = 1;
    p.objects[0] = b;
    if (c["blocked"].get<unsigned>()) {
      p.count = 2;
      p.objects[1].put16(0x58, 3);
      p.objects[1].put16(0x5a, c["blocked"]);
    }
    MeanCaptureTickEvent e;
    bool sample = false;
    bool ok = mean_mode4_capture(b, s, raw, r, p, 0x1100000, e, sample, c.value("tilt", false));
    raw.fields[0x380] = s.field_43f380;
    raw.fields[0x381] = static_cast<std::uint16_t>(s.field_43f380) >> 8;
    raw.fields[0x364] = s.field_43f364;
    raw.fields[0x365] = static_cast<std::uint16_t>(s.field_43f364) >> 8;
    nlohmann::json result = {{"ball", b.bytes},
                   {"raw", raw.fields},
                   {"mode", s.table_mode},
                   {"slot2", s.field_438b68},
                   {"slot3", s.field_438b74},
                   {"slot50", s.field_438b50},
                   {"sample", sample},
                   {"ok", ok}};
    if (c.contains("tilt")) result["tilt_samples"] = e.services_1c_samples;
    out.push_back(result);
  }
  std::cout << out.dump();
}
