#include "audio/mean_sound_assets.h"
#include "audio/pirate_sound_assets.h"
#include "audio/space_sound_assets.h"
#include "audio/demon_sound_assets.h"
#include "audio/stim_player.h"
#include "core/sha256.h"
#include <xmp.h>
#include <filesystem>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using Bytes = std::vector<std::uint8_t>;
struct Context {
  xmp_context value = xmp_create_context();
  ~Context() { if (value) { xmp_end_player(value); xmp_release_module(value); xmp_free_context(value); } }
};
void check(bool value, const std::string& message) { if (!value) throw std::runtime_error(message); }
Bytes load(const std::filesystem::path& p) {
  std::ifstream input(p, std::ios::binary);
  check(bool(input), "Missing DAT: " + p.string());
  return {std::istreambuf_iterator<char>(input), {}};
}
}
int main(int argc, char** argv) {
  try {
    check(argc == 2, "Usage: music_order_position DAT_DIRECTORY");
    const std::filesystem::path dir(argv[1]);
    struct Table { const char* id; const char* filename; const char* sha; std::vector<unsigned> offsets; };
    const std::vector<Table> tables = {
      {"mean", "MEAN.DAT", "1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f", {0x5c2d2, 0x61590}},
      {"pirate", "PIRATE.DAT", "6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6", {0x51876, 0x568e8}},
      {"space", "SPACE.DAT", "18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b", {0x53642, 0x5b8e0, 0x5fef8}},
      {"demon", "DEMON.DAT", "0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d", {0x6ffb4, 0x6b2bc, 0x6e2ce}},
    };
    unsigned total = 0;
    for (const auto& table : tables) {
      const auto dat = load(dir / table.filename);
      check(slam::sha256(dat) == table.sha, std::string("Unsupported ") + table.id + " DAT");
      std::vector<slam::MeanSoundBank> banks;
      const std::string id(table.id);
      if (id == "mean") { auto a = slam::mean_sound_banks(dat); banks.assign(a.begin(), a.end()); }
      else if (id == "pirate") { auto a = slam::pirate_sound_banks(dat); banks.assign(a.begin(), a.end()); }
      else if (id == "space") banks = slam::space_sound_banks(dat);
      else banks = slam::demon_sound_banks(dat);
      check(banks.size() == table.offsets.size(), id + ": bank count");
      for (unsigned b = 0; b < banks.size(); ++b) {
        for (unsigned order = 0; order < banks[b].orders; ++order) {
          const auto label = id + " bank " + std::to_string(b) + " order " + std::to_string(order);
          Context ctx; check(ctx.value != nullptr, label + ": allocation");
          check(xmp_load_module_from_memory(ctx.value, banks[b].stim.data(), long(banks[b].stim.size())) == 0, label + ": load");
          xmp_module_info info{}; xmp_get_module_info(ctx.value, &info);
          const auto pattern = dat.at(table.offsets[b] + 10 + order);
          // The Retail STIM patch retains valid order entries beyond the
          // header count. Every advertised order must still map exactly.
          check(info.mod && info.mod->len >= int(banks[b].orders) && info.mod->xxo[order] == pattern, label + ": order mapping");
          check(xmp_start_player(ctx.value, 44100, 0) == 0, label + ": start");
          if (order) check(xmp_set_position(ctx.value, int(order)) == int(order), label + ": seek");
          check(xmp_play_frame(ctx.value) == 0, label + ": render");
          xmp_frame_info frame{}; xmp_get_frame_info(ctx.value, &frame);
          check(frame.pos == int(order) && frame.pattern == int(pattern), label + ": rendered wrong order/pattern");
          // Exercise the actual port wrapper too, not just the raw libxmp API.
          // Compare its first samples to the independently positioned context.
          constexpr std::size_t samples = 256;
          check(frame.buffer && frame.buffer_size >= int(samples * sizeof(std::int16_t)), label + ": short frame");
          slam::StimPlayer player(banks[b].stim, int(order));
          std::vector<std::int16_t> pcm(samples);
          player.render(pcm.data(), samples / 2);
          check(std::memcmp(pcm.data(), frame.buffer, samples * sizeof(std::int16_t)) == 0,
                label + ": native wrapper starts at different PCM");
          Context retail; check(retail.value != nullptr, label + ": Retail allocation");
          check(xmp_load_module_from_memory(retail.value, banks[b].stim.data(), long(banks[b].stim.size())) == 0,
                label + ": Retail load");
          check(xmp_start_player(retail.value, 44100, 0) == 0, label + ": Retail start");
          check(xmp_set_player(retail.value, XMP_PLAYER_MIX, 0) == 0 &&
                xmp_set_player(retail.value, XMP_PLAYER_INTERP, XMP_INTERP_NEAREST) == 0 &&
                xmp_set_player(retail.value, XMP_PLAYER_VOLUME, 66) == 0,
                label + ": Retail mix options");
          if (order) check(xmp_set_position(retail.value, int(order)) == int(order), label + ": Retail seek");
          check(xmp_play_frame(retail.value) == 0, label + ": Retail render");
          xmp_frame_info retail_frame{}; xmp_get_frame_info(retail.value, &retail_frame);
          check(retail_frame.buffer && retail_frame.buffer_size >= int(samples * sizeof(std::int16_t)),
                label + ": Retail short frame");
          slam::StimPlayer retail_player(banks[b].stim, int(order), slam::TrackerMix::RetailMono);
          retail_player.render(pcm.data(), samples / 2);
          check(std::memcmp(pcm.data(), retail_frame.buffer, samples * sizeof(std::int16_t)) == 0,
                label + ": Retail wrapper differs from configured context");
          for (std::size_t i = 0; i < samples; i += 2)
            check(pcm[i] == pcm[i + 1], label + ": Retail channels differ");
          retail_player.restart();
          std::vector<std::int16_t> restarted(samples);
          retail_player.render(restarted.data(), samples / 2);
          check(restarted == pcm, label + ": Retail options lost on restart");
          ++total;
        }
        std::cout << id << " bank " << b << ": " << banks[b].orders << " positions\n";
      }
    }
    check(total == 563, "Unexpected total order count");
    std::cout << total << " original DAT order/pattern mappings and first rendered frames verified\n";
    return 0;
  } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
