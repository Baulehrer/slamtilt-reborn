#include "assets/mean_lamps.h"
#include "assets/table_lamps.h"
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
void require(bool value, const char *message) {
  if (!value)
    throw std::runtime_error(message);
}
std::vector<std::uint8_t> read(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  require(bool(input), "Missing original lamp fixture image");
  return {std::istreambuf_iterator<char>(input), {}};
}
void put(std::vector<std::uint8_t> &image, std::uint32_t address,
         std::uint32_t value, unsigned size = 4) {
  for (unsigned i = 0; i < size; ++i)
    image.at(address - 0x400000 + i) = std::uint8_t(value >> (8 * i));
}
template <typename Function> void rejects(Function function) {
  bool rejected = false;
  try {
    function();
  } catch (const std::exception &) {
    rejected = true;
  }
  require(rejected, "Invalid lamp descriptor was accepted");
}
void bounds_tests() {
  slam::TableDefinition definition;
  definition.geometry_build.executable_sha256 =
      "185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6";
  definition.geometry_build.returned_descriptor = 0x400040;
  std::vector<std::uint8_t> image(0x70000);
  put(image, 0x46c644, 0x400040);
  put(image, 0x400048, 0x400080);
  put(image, 0x400090, 0x400100);
  put(image, 0x46c6a4, 1);
  put(image, 0x400100, 0x400200);
  put(image, 0x400200, 16, 2);
  put(image, 0x400202, 22, 2);
  put(image, 0x400204, 2, 2);
  put(image, 0x400206, 3, 2);
  put(image, 0x400210, 0x1100008);
  auto profiles = slam::table_lamp_sprite_profiles(definition, image);
  require(profiles.size() == 1 && profiles[0].width == 32 &&
              profiles[0].x == 16 && profiles[0].y == 22 &&
              profiles[0].height == 3 && profiles[0].dat_offset == 8,
          "Original lamp field layout changed");
  auto invalid = image;
  put(invalid, 0x400090, 0xffffffff);
  rejects([&] { slam::table_lamp_sprite_profiles(definition, invalid); });
  invalid = image;
  put(invalid, 0x46c6a4, 257);
  rejects([&] { slam::table_lamp_sprite_profiles(definition, invalid); });
  invalid = image;
  put(invalid, 0x400200, 319, 2);
  rejects([&] { slam::table_lamp_sprite_profiles(definition, invalid); });
  invalid = image;
  put(invalid, 0x400210, 0);
  rejects([&] { slam::table_lamp_sprite_profiles(definition, invalid); });
  slam::TableLampFrames frame{0x400200, 16, 22, 32, 3, {}, {}};
  require(frame.frame(image) == 0, "Original lamp off state changed");
  put(image, 0x400208, 0xffff, 2);
  require(frame.frame(image) == 1, "Original lamp on state changed");
  put(image, 0x400208, 1, 2);
  rejects([&] { frame.frame(image); });
}
} // namespace

int main(int argc, char **argv) {
  try {
    if (argc != 1 && argc != 3 && argc != 4)
      throw std::runtime_error(
          "Usage: table_lamp_tests [DAT-directory prepared-image-directory "
          "[dump-directory]]");
    bounds_tests();
    if (argc == 1) {
      std::cout << "Lamp descriptor bounds and visible state verified\n";
      return 0;
    }
    const auto definitions =
        slam::load_table_definitions(slam::default_table_profiles());
    constexpr std::array<unsigned, 4> counts{63, 53, 48, 52};
    unsigned total = 0;
    for (unsigned t = 0; t < definitions.size(); ++t) {
      const auto &definition = definitions[t];
      auto image =
          read(std::filesystem::path(argv[2]) / (definition.id + "-image.bin"));
      const auto dat = std::filesystem::path(argv[1]) / definition.dat_filename;
      const auto table = slam::load_windows_table(dat);
      const auto lamps = slam::load_table_lamps(dat, definition, table, image);
      require(lamps.size() == counts[t], "Original table lamp count changed");
      if (definition.id == "pirate")
        require(lamps.front().descriptor == 0x465270 &&
                    lamps.front().x == 112 && lamps.front().y == 293 &&
                    lamps.front().width == 32 && lamps.front().height == 15 &&
                    lamps.back().x == 272 && lamps.back().y == 52,
                "Original Pirate lamp anchors changed");
      const auto mean = definition.id == "mean"
                            ? slam::load_mean_lamps(dat, table)
                            : std::vector<slam::MeanLampFrames>{};
      for (unsigned i = 0; i < lamps.size(); ++i) {
        const auto &lamp = lamps[i];
        const auto pixels = std::size_t(lamp.width) * lamp.height;
        require(lamp.mask.size() == pixels && lamp.frame(image) == 0,
                "Original lamp initial state/mask size changed");
        if (!mean.empty())
          require(lamp.x == mean[i].x && lamp.y == mean[i].y &&
                      lamp.width == mean[i].width &&
                      lamp.height == mean[i].height &&
                      lamp.mask == mean[i].mask && lamp.rgba == mean[i].rgba,
                  "Generic parser differs from existing Mean lamp assets");
        for (unsigned on = 0; on < 2; ++on) {
          const auto &rgba = lamp.rgba[on];
          require(rgba.size() == pixels * 4, "Invalid decoded lamp RGBA size");
          bool opaque = false;
          for (std::size_t pixel = 0; pixel < pixels; ++pixel) {
            require(lamp.mask[pixel] <= 1 &&
                        rgba[pixel * 4 + 3] == lamp.mask[pixel] * 255,
                    "Lamp mask/alpha disagreement");
            opaque |= lamp.mask[pixel] != 0;
          }
          require(opaque, "Empty original lamp mask");
          if (argc == 4) {
            const auto directory = std::filesystem::path(argv[3]);
            std::filesystem::create_directories(directory);
            const auto name = definition.id + "-" + std::to_string(i) + "-" +
                              std::to_string(on) + ".rgba";
            std::ofstream output(directory / name, std::ios::binary);
            output.write(reinterpret_cast<const char *>(rgba.data()),
                         std::streamsize(rgba.size()));
            require(bool(output), "Cannot write original lamp comparison");
          }
        }
      }
      total += unsigned(lamps.size());
    }
    require(total == 216, "Four-table lamp corpus changed");
    std::cout << "Four tables, 216 lamps, 432 frames verified\n";
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
