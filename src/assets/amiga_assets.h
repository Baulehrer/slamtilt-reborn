#pragma once
#include <cstdint>
#include <map>
#include <string>
#include <vector>
namespace slam {
struct AmigaNativeAssets {
  std::map<std::string,std::vector<std::uint8_t>> files;
};
// Input consists exclusively of decoded original Amiga files. Output is a
// private data ABI for the shared native engine, not an original Windows DAT.
AmigaNativeAssets build_amiga_assets(
    const std::map<std::string,std::vector<std::uint8_t>>& decoded_files);
}
