#include "assets/table_sprites.h"
#include "assets/table_lamps.h"
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
std::vector<std::uint8_t> read(const std::filesystem::path &path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) throw std::runtime_error("Cannot read " + path.string());
  return {std::istreambuf_iterator<char>(file), {}};
}
}
int main(int argc, char **argv) {
  try {
    if (argc != 5)
      throw std::runtime_error("Usage: probe DAT IMAGE CURRENT_DAT OUTPUT_DIRECTORY");
    const auto definition = slam::load_table_definition(slam::default_table_profiles(), "pirate");
    const auto table = slam::load_windows_table(argv[1]);
    const auto sprites = slam::load_table_flippers(argv[1], definition, table);
    const auto profiles = slam::table_flipper_sprite_profiles(definition);
    const auto image = read(argv[2]), dat = read(argv[3]);
    const auto output = std::filesystem::path(argv[4]);
    std::filesystem::create_directories(output);
    auto canvas=table.rgba;
    for(const auto& lamp:slam::load_table_lamps(argv[1],definition,table,image)){
      const auto& rgba=lamp.rgba[lamp.frame(image)];
      for(int y=0;y<lamp.height;++y)for(int x=0;x<lamp.width;++x){
        const auto source=std::size_t(y*lamp.width+x)*4;
        const auto target=std::size_t((lamp.y+y)*320+lamp.x+x)*4;
        if(rgba[source+3])for(unsigned c=0;c<4;++c)canvas[target+c]=rgba[source+c];
      }
    }
    {std::ofstream file(output/"lamp-canvas.rgba",std::ios::binary);
      file.write(reinterpret_cast<const char*>(canvas.data()),canvas.size());
      if(!file)throw std::runtime_error("Cannot write lamp canvas");}
    for (unsigned side = 0; side < sprites.size(); ++side) {
      for (unsigned frame=0;frame<profiles[side].frame_count;++frame) {
        const auto pixels = slam::compose_table_flipper(profiles[side], sprites[side], frame, table, image, dat);
        std::ofstream file(output / ("frame" + std::to_string(side) + "-" + std::to_string(frame) + ".rgba"), std::ios::binary);
        file.write(reinterpret_cast<const char *>(pixels.data()), pixels.size());
        if (!file) throw std::runtime_error("Cannot write composited sprite");
      }
    }
    auto broken = image;
    const auto mask = profiles[0].descriptor - 0x400000 + 0x20;
    for (unsigned i = 0; i < 4; ++i) broken.at(mask + i) = 0xff;
    bool rejected = false;
    try { slam::compose_table_flipper(profiles[0], sprites[0], 0, table, broken, dat); }
    catch (const std::runtime_error &) { rejected = true; }
    if (!rejected) throw std::runtime_error("Out-of-range parent mask accepted");
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
