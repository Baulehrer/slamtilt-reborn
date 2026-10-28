#include "assets/windows_table.h"
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

int main() {
  const auto path =
      std::filesystem::temp_directory_path() /
      ("slam-assets-test-" +
       std::to_string(
           std::chrono::steady_clock::now().time_since_epoch().count()) +
       ".dat");
  try {
    auto write = [&](const std::vector<std::uint8_t> &bytes) {
      std::ofstream f(path, std::ios::binary);
      f.write(reinterpret_cast<const char *>(bytes.data()), bytes.size());
      if (!f)
        throw std::runtime_error("fixture write failed");
    };
    auto rejected = [&]() {
      try {
        (void)slam::load_windows_table(path);
      } catch (const std::runtime_error &) {
        return;
      }
      throw std::runtime_error("Malformed input accepted");
    };
    write({0, 0, 0, 124});
    rejected();
    std::vector<std::uint8_t> bytes(1622024, 0);
    constexpr auto palette = 0x1590c8;
    bytes[palette + 4 + 1] = 241;
    bytes[palette + 4 + 2] = 71;
    bytes[palette + 4 + 3] = 19;
    bytes[palette + 1024] = 1;
    bytes[palette + 1024 + 320 * 599 + 319] = 1;
    write(bytes);
    const auto image = slam::load_windows_table(path);
    if (image.rgba.size() != 320 * 600 * 4 || image.rgba[0] != 241 ||
        image.rgba[1] != 71 || image.rgba[2] != 19 || image.rgba[3] != 255 ||
        image.rgba[4] != 0 || image.rgba[image.rgba.size() - 4] != 241)
      throw std::runtime_error("Palette, row order or extent incorrect");
    bytes[palette + 4] = 1;
    write(bytes);
    rejected();
    std::filesystem::remove(path);
    std::cout << "Palette colors, row order, extent and malformed-input checks "
                 "passed\n";
  } catch (const std::exception &e) {
    std::filesystem::remove(path);
    std::cerr << e.what() << '\n';
    return 1;
  }
}
