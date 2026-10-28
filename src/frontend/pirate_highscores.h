#pragma once

#include <array>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>

// Native-only storage. The frontend supplies a private destination; this class
// never discovers, reads or rewrites original STTF / SLAMTILT.CFG assets.
class PirateHighscores {
public:
  using Records = std::array<std::uint8_t, 50>;

  // Missing files return nullopt with an empty error. Invalid files return
  // nullopt with an error and are left untouched; no default scores are made
  // up.
  std::optional<Records> load(const std::filesystem::path &path);
  bool save(const std::filesystem::path &path, const Records &records);

  std::string error;
};
