#include "audio/mean_sound_assets.h"
#include <fstream>
#include <iostream>
#include <iterator>
int main(int argc, char **argv) {
  if (argc != 3)
    return 2;
  try {
    std::ifstream input(argv[1], std::ios::binary);
    std::vector<std::uint8_t> data((std::istreambuf_iterator<char>(input)), {});
    const auto banks = slam::mean_sound_banks(data);
    for (unsigned i = 0; i < 2; ++i) {
      std::ofstream out(std::string(argv[2]) + std::to_string(i) + ".stim",
                        std::ios::binary);
      out.write(reinterpret_cast<const char *>(banks[i].stim.data()),
                banks[i].stim.size());
      if (!out)
        return 1;
    }
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
