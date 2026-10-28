#include "assets/table_sprites.h"
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
void require(bool value, const char *message) {
  if (!value)
    throw std::runtime_error(message);
}
} // namespace
int main(int argc, char **argv) {
  try {
    if (argc > 3)
      throw std::runtime_error("Usage: table_sprite_tests [DAT-directory [dump-directory]]");
    const auto definitions =
        slam::load_table_definitions(slam::default_table_profiles());
    const std::array<unsigned, 4> counts{{3, 3, 3, 2}};
    unsigned total_frames = 0;
    for (unsigned t = 0; t < definitions.size(); ++t) {
      const auto &definition = definitions[t];
      const auto sprites = slam::table_flipper_sprite_profiles(definition);
      require(sprites.size() == counts[t], "Incorrect flipper count");
      for (const auto &sprite : sprites)
        total_frames += sprite.frame_count;
      if (definition.id == "pirate") {
        require(sprites[0].x == 80 && sprites[0].y == 540 &&
                    sprites[1].x == 160 && sprites[1].y == 540 &&
                    sprites[2].x == 224 && sprites[2].y == 188,
                "Pirate original anchors changed");
        require(sprites[2].height == 51 && sprites[2].frame_count == 7,
                "Pirate upper flipper frame layout changed");
      }
      if (argc < 2)
        continue;
      const auto dat = std::filesystem::path(argv[1]) / definition.dat_filename;
      const auto image = slam::load_windows_table(dat);
      const auto frames = slam::load_table_flippers(dat, definition, image);
      require(frames.size() == sprites.size(), "Decoded flipper count changed");
      for (unsigned s = 0; s < frames.size(); ++s) {
        const auto &flipper = frames[s];
        require(flipper.rgba.size() == sprites[s].frame_count,
                "Decoded frame count changed");
        require(flipper.frame(0) == 0 &&
                    flipper.frame(512) == 1 && flipper.frame(511) == 0 &&
                    flipper.frame(0xffff) == flipper.rgba.size() - 1,
                "Original pose rounding/clamp changed");
        bool transparent = false, opaque = false;
        for (unsigned f = 0; f < flipper.rgba.size(); ++f) {
          const auto &pixels = flipper.rgba[f];
          require(pixels.size() == std::size_t(flipper.width * flipper.height * 4),
                  "Decoded RGBA size changed");
          for (std::size_t i = 3; i < pixels.size(); i += 4) {
            transparent |= pixels[i] == 0;
            opaque |= pixels[i] == 255;
            require(pixels[i] == 0 || pixels[i] == 255, "Invalid source mask");
          }
          if (argc == 3) {
            const auto directory = std::filesystem::path(argv[2]);
            std::filesystem::create_directories(directory);
            const auto name = definition.id + "-" + std::to_string(s) + "-" +
                              std::to_string(f) + ".rgba";
            std::ofstream output(directory / name, std::ios::binary);
            output.write(reinterpret_cast<const char *>(pixels.data()), pixels.size());
            require(bool(output), "Cannot write original-comparison frame");
          }
        }
        require(transparent && opaque, "Sprite mask missing visible/invisible pixels");
      }
    }
    require(total_frames == 103, "Four table animation corpus changed");
    std::cout << "Four tables, 11 flippers, 103 original frames verified\n";
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
