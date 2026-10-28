#include "physics/mean_mode5_clock.h"
#include "physics/mean_mode6_capture.h"
#include "physics/mean_mode6_display.h"
#include <iostream>
#include <nlohmann/json.hpp>
using nlohmann::json;
int main() {
  json request;
  std::cin >> request;
  json result = json::array();
  if (request.at("kind") == "display") {
    slam::MeanRewardDisplay d;
    std::int16_t gate = -1;
    for (int i = 0; i < request.at("ticks").get<int>(); ++i) {
      slam::mean_mode6_display_tick(d, gate);
      result.push_back({{"tick", i + 1},
                        {"state", d.state},
                        {"active", d.active},
                        {"frame", d.frame},
                        {"gate", gate},
                        {"shared14", d.active}});
    }
    std::cout << result.dump();
    return 0;
  }
  for (const auto &c : request.at("cases")) {
    slam::MeanMode5LeftState m;
    slam::MeanUpperCaptureState u;
    slam::MeanObject b;
    if (request.at("kind") == "clock") {
      const auto &a = c.at("input");
      m.field_43f37e = a.at("stage");
      m.field_43f376 = a.at("timer");
      m.field_43f1e6 = a.at("selected");
      m.field_43f1e0 = a.at("flags").get<std::array<std::uint8_t, 5>>();
      m.field_43f366 = 77;
      slam::MeanCaptureTickState capture;
      capture.table_mode = 6;
      slam::mean_mode5_clock(m, capture, a.at("count").get<unsigned>());
      result.push_back({{"timer", m.field_43f376},
                        {"mode", capture.table_mode},
                        {"selected", m.field_43f1e6},
                        {"field366", m.field_43f366},
                        {"engine40", m.field_engine_40},
                        {"flags", m.field_43f1e0}});
    } else if (request.at("kind") == "entry") {
      const auto &s = c.at("initial");
      const auto data = s.at("ball").get<std::vector<unsigned char>>();
      for (unsigned i = 0; i < data.size(); ++i)
        b.bytes[i] = data[i];
      u.field_43f36a = s.at("timer");
      u.field_43f364 = s.at("gate");
      u.field_43f394 = s.at("field394");
      u.field_43f1f2 = s.at("field1f2");
      u.field_43f1e6 = s.at("selected");
      u.table_mode = s.at("mode");
      u.field_438b5c = s.at("slot_upper").get<std::array<std::int32_t, 3>>();
      auto f = s.at("fields");
      m.field_43f382 = f.at("0x382");
      m.field_43f37e = f.at("0x37e");
      m.field_43f376 = f.at("0x376");
      m.field_43f38e = f.at("0x38e");
      m.field_43f368 = f.at("0x368");
      m.field_43f36c = f.at("0x36c");
      m.field_43f36e = f.at("0x36e");
      m.field_43f35e = f.at("0x35e");
      m.field_43f058 = s.at("sum058");
      m.field_43f23c = s.at("data").get<std::array<std::uint8_t, 24>>();
      slam::MeanUpperCaptureEvent e;
      slam::mean_upper_capture_tick(b, u, e);
      if (!e.mode6_start_requested)
        return 2;
      slam::mean_mode6_begin(m);
      json out = s;
      out["timer"] = u.field_43f36a;
      out["gate"] = u.field_43f364;
      out["field394"] = u.field_43f394;
      out["field1f2"] = u.field_43f1f2;
      out["mode"] = u.table_mode;
      out["slot_upper"] = u.field_438b5c;
      out["sum058"] = m.field_43f058;
      out["data"] = m.field_43f23c;
      out["fields"] = {{"0x382", m.field_43f382}, {"0x37e", m.field_43f37e},
                       {"0x376", m.field_43f376}, {"0x38e", m.field_43f38e},
                       {"0x368", m.field_43f368}, {"0x36c", m.field_43f36c},
                       {"0x36e", m.field_43f36e}, {"0x35e", m.field_43f35e}};
      result.push_back(out);
    } else {
      const auto a = c.at("input").get<std::vector<int>>();
      b.put16(0x58, a[0]);
      b.put16(0x5a, a[1]);
      m.field_43f38e = a[2];
      m.field_43f368 = a[3];
      m.field_43f36c = a[4];
      u.field_43f36a = a[6];
      u.field_43f364 = 0;
      slam::MeanMode6CaptureEvent e;
      slam::mean_mode6_capture_tick(b, m, u, a[5], e);
      json calls = json::array();
      if (e.transfer)
        calls.push_back("0x417068");
      if (e.lamp_reset)
        calls.push_back("0x416fe0");
      result.push_back({{"output",
                         {b.u16(0x58), m.field_43f38e, m.field_43f368,
                          m.field_43f36c, u.field_43f36a}},
                        {"calls", calls}});
    }
  }
  std::cout << result.dump();
}
