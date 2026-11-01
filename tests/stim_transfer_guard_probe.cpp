#include "audio/stim_player.h"
#include <cstdint>
#include <iostream>
#include <vector>

int main(int argc, char **argv) {
  if (argc != 4) return 1;
  try {
    const int target_order = std::stoi(argv[3]);
    slam::StimPlayer target(argv[2], target_order, slam::TrackerMix::RetailMono);
    slam::StimPlayer reference(argv[2], target_order, slam::TrackerMix::RetailMono);
    {
      slam::StimPlayer source(argv[1], 5, slam::TrackerMix::RetailMono);
      std::vector<std::int16_t> warm(882 * 2);
      source.render(warm.data(), 882);
      if (source.inherit_history(source) || target.inherit_history(source) ||
          source.resume_history(source) || target.resume_history(source)) return 2;
      // A failed resume must also leave a running, snapshotted destination
      // untouched, including after the incompatible source is destroyed.
      std::vector<std::int16_t> target_warm(882 * 2), reference_warm(882 * 2);
      target.render(target_warm.data(), 882);
      reference.render(reference_warm.data(), 882);
      if (target_warm != reference_warm || target.resume_history(source)) return 5;
    }
    std::vector<std::int16_t> actual(2646 * 2), expected(2646 * 2);
    target.render(actual.data(), 2646);
    reference.render(expected.data(), 2646);
    if (actual != expected) return 3;
    std::cout << "PASS: incompatible and self transfers and resumes leave target unchanged\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 4;
  }
}
