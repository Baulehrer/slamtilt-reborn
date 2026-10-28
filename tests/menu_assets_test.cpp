#ifdef NDEBUG
#undef NDEBUG
#endif
#include "assets/menu_assets.h"
#include "core/sha256.h"
#include <cassert>
int main(int argc, char **argv) {
  assert(argc == 2);
  auto image = slam::load_windows_menu(argv[1]);
  assert(image.width == 640 && image.height == 480 &&
         image.rgba.size() == 640 * 480 * 4);
  std::vector<std::uint8_t> rgb;
  for (std::size_t i = 0; i < image.rgba.size(); i += 4) {
    rgb.insert(rgb.end(), image.rgba.begin() + i, image.rgba.begin() + i + 3);
    assert(image.rgba[i + 3] == 255);
  }
  assert(slam::sha256(rgb) ==
         "f04a774e60b1f56bb77d9bfda4690fd55f432709cab284717f0b4cd94453e946");
}
