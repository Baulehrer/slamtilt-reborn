#include "assets/ball_mask.h"
#include <fstream>
#include <stdexcept>

namespace slam {
namespace {
std::array<std::uint8_t, 240> read_block(const std::filesystem::path &path,
                                         std::streamoff offset) {
  std::ifstream stream(path, std::ios::binary | std::ios::ate);
  // Full and Mean-demo MAIN.DAT revision used by the recovered routines.
  if (!stream || stream.tellg() != 0xf028)
    throw std::runtime_error("Unsupported or unreadable MAIN.DAT revision");
  std::array<std::uint8_t, 240> bytes{};
  stream.seekg(offset);
  if (!stream.read(reinterpret_cast<char *>(bytes.data()), bytes.size()))
    throw std::runtime_error("Truncated original ball asset");
  return bytes;
}
} // namespace

BallMask load_windows_ball_mask(const std::filesystem::path &main_dat) {
  BallMask result;
  // Full RIP 0x40b876; combined with table occlusion in 0x40b902..0x40b975.
  result.preserve_background = read_block(main_dat, 0x88a4);
  for (auto byte : result.preserve_background)
    if (byte != 0 && byte != 255)
      throw std::runtime_error("Invalid original ball preservation mask");
  return result;
}

std::array<std::uint8_t, 240>
load_windows_ball_pixels(const std::filesystem::path &main_dat, int screen_y) {
  if (screen_y < 0 || screen_y >= 600)
    throw std::runtime_error("Original ball screen Y outside 0..599");
  // Full RIP 0x40b990..0x40b9cc, drawn by 0x40ba7f..0x40ba9f:
  // (sprite & ~preserve_mask) | (background & preserve_mask).
  return read_block(main_dat, 0x3da4 + (screen_y / 8) * 256);
}
BallPixelBank load_windows_ball_pixel_bank(const std::filesystem::path& path) {
  std::ifstream stream(path,std::ios::binary|std::ios::ate);
  if(!stream||stream.tellg()!=0xf028)throw std::runtime_error("Unsupported or unreadable MAIN.DAT revision");
  BallPixelBank bank{};
  for(unsigned i=0;i<bank.size();++i){
    stream.seekg(0x3da4+i*256);
    if(!stream.read(reinterpret_cast<char*>(bank[i].data()),bank[i].size()))throw std::runtime_error("Truncated original ball bank");
  }
  return bank;
}
} // namespace slam
