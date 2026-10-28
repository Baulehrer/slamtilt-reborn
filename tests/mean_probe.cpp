#include "physics/mean_step.h"
#include "physics/mean_switch_bundle.h"
#include "rules/mean_contact_animation.h"
#include "rules/mean_score.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  try {
    if (argc != 3 && argc != 4)
      return 2;
    std::ifstream f(argv[1]);
    nlohmann::json cases;
    f >> cases;
    std::ifstream lut(argv[2], std::ios::binary);
    slam::MeanLookup lookup;
    lookup.field_43e764 =
        std::vector<std::uint8_t>(std::istreambuf_iterator<char>(lut), {});
    if (lookup.field_43e764.size() != 0x2800)
      throw std::runtime_error("Invalid LUT size");
    lookup.field_43e744.assign(lookup.field_43e764.begin() + 0x800,
                               lookup.field_43e764.end());
    if (argc == 4) {
      std::ifstream pe(argv[3], std::ios::binary);
      const std::vector<std::uint8_t> bytes(std::istreambuf_iterator<char>(pe),
                                            {});
      lookup.field_43e728.assign(bytes.begin() + 0x2c9fc,
                                 bytes.begin() + 0x2d1fe);
    }
    auto results = nlohmann::json::array();
    for (const auto &item : cases) {
      slam::MeanObject b;
      b.bytes = item.at("bytes").get<std::array<std::uint8_t, 0x64>>();
      const auto operation = item.at("operation").get<std::string>();
      if (operation == "switch_bundle") {
        std::uint32_t points = 0;
        const bool handled =
            slam::mean_switch_bundle(b, b.u16(0x38), 0x1100000, points);
        results.push_back(
            {{"bytes", b.bytes}, {"points", points}, {"handled", handled}});
        continue;
      }
      if (operation == "animation") {
        slam::MeanContactAnimation animation;
        animation.trigger(item.at("repetitions"));
        auto sequence = nlohmann::json::array();
        for (bool available :
             item.at("availability").get<std::vector<bool>>()) {
          const auto emitted = animation.tick(available);
          sequence.push_back({animation.countdown, animation.cursor,
                              animation.repetitions, emitted});
        }
        results.push_back(sequence);
        continue;
      }
      if (operation == "score" || operation == "lower_score") {
        slam::MeanScore score(item.at("initial_score").get<std::uint64_t>());
        score.add(operation == "score" ? item.at("points").get<std::uint32_t>()
                                       : slam::mean_lower_switch_points(b));
        results.push_back(score.value());
        continue;
      }
      if (operation == "advance_ball") {
        auto number = b.u16(0x0e), extra = b.u16(0x10);
        slam::mean_advance_ball(number, extra);
        b.put16(0x0e, number);
        b.put16(0x10, extra);
      } else if (operation == "lower_switch") {
        if (!slam::mean_lower_switch(b))
          throw std::runtime_error("Unsupported lower switch");
      } else if (operation == "reset") {
        slam::mean_set_layer(b, 0, 0x1100000);
        slam::mean_reset_ball(b);
      } else if (operation == "kick")
        slam::mean_launch_kick(b, item.at("pressed"));
      else if (operation == "integrate")
        slam::mean_integrate(b);
      else if (operation == "free") {
        if (!slam::mean_free_velocity(b, lookup))
          throw std::runtime_error("Unsupported free branch");
      } else if (operation == "wall" || operation == "wall_event") {
        slam::MeanContactEvent event;
        if (!slam::mean_wall_response(b, lookup, item.at("offset_x"),
                                      item.at("offset_y"), &event))
          throw std::runtime_error("Unsupported response");
        if (operation == "wall_event") {
          results.push_back({{"bytes", b.bytes},
                             {"points", event.points},
                             {"field_438b_state", event.field_438b_state}});
          continue;
        }
      } else
        throw std::runtime_error("Unknown operation");
      results.push_back(b.bytes);
    }
    std::cout << results.dump() << '\n';
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
