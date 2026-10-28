#include "dmd/mean_bonus_pixels.h"
#include <cstdlib>
#include <iostream>
int main(int argc, char **argv) {
  if (argc == 3) {
    slam::MeanBonusTableState state{};
    for (unsigned n = 0; n < 66; ++n) {
      auto r = slam::mean_bonus_table_callback(state, n ? 1 : 0, 2);
      std::cout << state.field_43f028 << ' ' << state.field_43f02c << ' '
                << r.result << ' ' << r.score_add << '\n';
    }
    return 0;
  }
  if (argc == 4) {
    auto a = slam::load_mean_bonus_animation(argv[1]);
    auto out = slam::render_mean_bonus_intro(a, std::atoi(argv[2]));
    std::cout.write(reinterpret_cast<const char *>(out.data()), out.size());
    return 0;
  }
  if (argc != 5)
    return 2;
  auto f = slam::load_mean_bonus_pixels(argv[1]);
  slam::WindowsDmdPixels out;
  slam::mean_bonus_background(out, std::atoi(argv[2]));
  slam::draw_mean_bonus_text(f, out, argv[3], std::atoi(argv[4]), 1);
  std::cout.write(reinterpret_cast<const char *>(out.data()), out.size());
}
