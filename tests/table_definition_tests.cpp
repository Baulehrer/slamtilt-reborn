#include "assets/table_definition.h"
#include "assets/windows_table.h"
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
void require(bool condition, const char *message) {
  if (!condition)
    throw std::runtime_error(message);
}
template <class F> void rejects(F operation, const char *message) {
  bool rejected = false;
  try {
    operation();
  } catch (const std::exception &) {
    rejected = true;
  }
  require(rejected, message);
}
} // namespace
int main(int argc, char **argv) {
  try {
    if (argc > 2)
      throw std::runtime_error("Usage: table_definition_tests [DAT-directory]");
    const auto profiles = slam::default_table_profiles();
    const auto definitions = slam::load_table_definitions(profiles);
    require(definitions.size() == 4, "Expected four supported tables");
    const auto &mean = definitions[0];
    const auto &pirate = definitions[1];
    require(mean.id == "mean" && pirate.id == "pirate" &&
                definitions[2].id == "space" && definitions[3].id == "demon",
            "Unexpected table identities");
    require(mean.capabilities.gameplay == slam::TableGameplaySupport::Playable,
            "Mean native session missing");
    require(mean.gameplay_executable_sha256 ==
                "31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00",
            "Mean gameplay must remain bound to the supported Demo build");
    require(pirate.capabilities.gameplay ==
                slam::TableGameplaySupport::Playable &&
                pirate.gameplay_executable_sha256 ==
                    "185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6",
            "Pirate native gameplay must remain bound to the supported Retail build");
    require(definitions[2].capabilities.gameplay == slam::TableGameplaySupport::Playable &&
                definitions[2].gameplay_executable_sha256 == pirate.gameplay_executable_sha256,
            "Space playable RC must remain bound to supported Retail");
    require(definitions[3].capabilities.gameplay == slam::TableGameplaySupport::Playable &&
                definitions[3].gameplay_executable_sha256 == pirate.gameplay_executable_sha256,
            "Demon playable RC must remain bound to supported Retail");
    require(pirate.geometry_build.initializer == 0x42b390 &&
                pirate.geometry_build.engine_descriptor == 0x465784 &&
                pirate.geometry.graphics_descriptor == 0x465938,
            "Pirate Retail anchors differ from original initializer evidence");
    for (const auto &table : definitions) {
      require(table.capabilities.original_playfield &&
                  table.capabilities.collision_geometry &&
                  table.capabilities.flipper_parameters,
              "Verified shared asset capability missing");
      require(table.geometry_build.executable_sha256 ==
                  "185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6",
              "Geometry build identity changed");
      require(!table.geometry.layers.empty(), "Missing original geometry");
      rejects([&] { slam::validate_table_dat(table, {}); },
              "Empty DAT incorrectly accepted");
      if (argc == 2) {
        const auto path = std::filesystem::path(argv[1]) / table.dat_filename;
        std::ifstream input(path, std::ios::binary);
        require(bool(input), "Missing original DAT for content validation");
        std::vector<std::uint8_t> bytes{std::istreambuf_iterator<char>(input), {}};
        slam::validate_table_dat(table, bytes);
        const auto image = slam::load_windows_table(path);
        require(image.width == 320 && image.height == 600 &&
                    image.rgba.size() == 320 * 600 * 4,
                "Original playfield decoding failed");
        bytes[bytes.size() / 2] ^= 1;
        rejects([&] { slam::validate_table_dat(table, bytes); },
                "Mutated DAT incorrectly accepted");
      }
    }
    rejects([&] { slam::load_table_definition(profiles, "PIRATE"); },
            "Unsupported table spelling accepted");
    rejects([&] { slam::load_table_definition(profiles, "unknown"); },
            "Unknown table accepted");
    std::cout << "Four table identities/capabilities verified"
              << (argc == 2 ? "; original DATs decoded and mutation rejected" : "")
              << '\n';
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
