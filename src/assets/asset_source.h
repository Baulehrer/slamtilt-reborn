#pragma once
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <nlohmann/json.hpp>
#include <stdexcept>
#include <string>
#include <string_view>
namespace slam {
enum class AssetSource { WindowsDat, AmigaAdf };
inline const char* asset_source_name(AssetSource source) {
  return source==AssetSource::AmigaAdf?"amiga":"windows";
}
inline const char* asset_source_label(AssetSource source) {
  return source==AssetSource::AmigaAdf?"Amiga · gemeinsame Regeln":"PC";
}
inline AssetSource parse_asset_source(std::string_view source) {
  if(source=="windows")return AssetSource::WindowsDat;
  if(source=="amiga")return AssetSource::AmigaAdf;
  throw std::runtime_error("Unsupported asset source");
}
inline AssetSource inferred_asset_source=AssetSource::WindowsDat;
inline void infer_asset_source(const std::filesystem::path& data_directory) {
  inferred_asset_source=AssetSource::WindowsDat;
  std::ifstream f(data_directory/"data.json");
  if(!f)return;
  const auto receipt=nlohmann::json::parse(f,nullptr,false);
  if(receipt.is_object()&&receipt.contains("asset_source")&&receipt["asset_source"]=="amiga")
    inferred_asset_source=AssetSource::AmigaAdf;
}
inline AssetSource current_asset_source() {
  const auto* source=std::getenv("SLAM_ASSET_SOURCE");
  return source?parse_asset_source(source):inferred_asset_source;
}
inline std::string highscore_filename(std::string_view table,AssetSource source) {
  return (source==AssetSource::AmigaAdf?"amiga-":"")+std::string(table)+"-highscores.json";
}
inline std::string highscore_filename(std::string_view table) {
  return highscore_filename(table,current_asset_source());
}
}
