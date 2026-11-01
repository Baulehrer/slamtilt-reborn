#include "audio/mean_music_sequencer.h"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <vector>

static std::vector<std::uint8_t> read_file(const char *path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) throw std::runtime_error("Cannot read STIM bank");
  return {std::istreambuf_iterator<char>(file), {}};
}
int main(int argc, char **argv) {
  if (argc != 10) return 1;
  try {
    slam::MeanMusicSequencer music({read_file(argv[1]), read_file(argv[2])});
    const int base_order = std::stoi(argv[3]), upper_order = std::stoi(argv[4]);
    const int lower_bank = std::stoi(argv[5]), lower_order = std::stoi(argv[6]);
    const auto warm = std::stoul(argv[7]), queued = std::stoul(argv[8]), ticks = std::stoul(argv[9]);
    if (!warm || queued >= ticks || ticks > 2048 || warm > 2048 || lower_bank < 0 || lower_bank > 1) return 2;
    std::vector<std::int16_t> before(warm * 882 * 2), result(ticks * 882 * 2);
    music.request90(0, base_order);
    music.render(before.data(), warm * 882);
    music.request88(1, upper_order);
    music.render(result.data(), queued * 882);
    music.request84(lower_bank, lower_order);
    music.render(result.data() + queued * 882 * 2, (ticks - queued) * 882);
    std::cout.write(reinterpret_cast<const char *>(result.data()), result.size() * sizeof(result[0]));
    return std::cout ? 0 : 3;
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 4;
  }
}
