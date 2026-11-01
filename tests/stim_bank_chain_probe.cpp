#include "audio/mean_music_sequencer.h"
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
  if (argc != 9) return 1;
  try {
    slam::MeanMusicSequencer music({read_file(argv[1]), read_file(argv[2]), read_file(argv[3])});
    const int warm = std::stoi(argv[4]), middle = std::stoi(argv[5]), target = std::stoi(argv[6]);
    const auto middle_ticks = std::stoul(argv[7]), ticks = std::stoul(argv[8]);
    if (!middle_ticks || middle_ticks > 64 || !ticks || ticks > 2048) return 2;
    std::vector<std::int16_t> initial(882*2), between(middle_ticks*882*2), output(ticks*882*2);
    music.request90(0, warm); music.render(initial.data(), 882);
    music.request90(1, middle); music.render(between.data(), between.size()/2);
    music.request90(2, target); music.render(output.data(), output.size()/2);
    std::cout.write(reinterpret_cast<const char *>(output.data()), output.size()*sizeof(output[0]));
    return std::cout ? 0 : 3;
  } catch (const std::exception &e) { std::cerr << e.what() << '\n'; return 4; }
}
