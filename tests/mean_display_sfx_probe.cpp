#include "core/mean_display_sfx.h"
#include <nlohmann/json.hpp>
#include <iostream>
#include <string>
#include <utility>

int main(int argc, char **argv) {
  nlohmann::json result = nlohmann::json::array();
  unsigned cursor = 0;
  if (argc == 2 && std::string(argv[1]) == "--interrupt") {
    for (const auto [callback, tick] : {std::pair{0x4133d4u,0u}, {0x4133d4u,16u},
        {0x4131ccu,0u}, {0x4133d4u,20u}, {0x4131ccu,24u},
        {0x413518u,0u}, {0x413518u,20u}, {0x413518u,16u}}) {
      if (const auto e = slam::mean_display_sfx(callback, tick, cursor))
        result.push_back({{"tick",tick},{"descriptor",e->descriptor},
                          {"period",e->period},{"volume",e->volume}});
    }
    std::cout << result.dump() << '\n';
    return 0;
  }
  if (argc != 1) return 1;
  for (const unsigned callback : {0x4133d4u, 0x413518u, 0x4131ccu, 0x4132d4u,
                                  0x412fa8u, 0x411824u, 0x41041cu, 0x410158u,
                                  0x4102c0u})
    for (unsigned tick = 0; tick < 140; ++tick)
      if (const auto event = slam::mean_display_sfx(callback, tick, cursor))
        result.push_back({{"callback", callback}, {"tick", tick},
            {"service", event->service}, {"field_1c", event->bank},
            {"field_20", event->order}, {"descriptor", event->descriptor},
            {"period", event->period}, {"volume", event->volume}});
  std::cout << result.dump() << '\n';
}
