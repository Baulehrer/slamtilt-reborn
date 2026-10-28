#pragma once
#include "assets/table_profile.h"
#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

namespace slam {
// Readiness is separate from asset availability. In particular, validated
// component contacts do not imply an autonomous table simulation.
enum class TableGameplaySupport { ViewerOnly, PartialContacts, GameplayPreview, Playable };
struct TableCapabilities {
  bool original_playfield = false;
  bool collision_geometry = false;
  bool flipper_parameters = false;
  TableGameplaySupport gameplay = TableGameplaySupport::ViewerOnly;
};
struct TableBuildIdentity {
  std::string executable_sha256;
  std::uint32_t initializer = 0;
  std::uint32_t returned_descriptor = 0;
  std::uint32_t engine_descriptor = 0;
};
struct TableDefinition {
  std::string id;
  std::string display_name;
  std::string dat_filename;
  TableProfile geometry;
  TableBuildIdentity geometry_build;
  TableCapabilities capabilities;
  // Empty unless a complete native game is supported for this exact build.
  // Geometry evidence from Retail alone never enables gameplay for that build.
  std::string gameplay_executable_sha256;
};
TableDefinition load_table_definition(const std::filesystem::path &profiles,
                                      const std::string &id);
TableDefinition load_table_definition_for_data(const std::filesystem::path& profiles,
 const std::string& id, const std::filesystem::path& dat);
std::vector<TableDefinition>
load_table_definitions(const std::filesystem::path &profiles);
// Requires both the supported content hash and valid geometry bounds.
void validate_table_dat(const TableDefinition &,
                        const std::vector<std::uint8_t> &dat);
} // namespace slam
