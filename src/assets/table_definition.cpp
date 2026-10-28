#include "assets/table_definition.h"
#include "core/sha256.h"
#include "assets/amiga_data_profiles.h"
#include "assets/amiga_data_profiles_v2.h"
#include "assets/amiga_demon_read_profile.h"
#include <array>
#include <fstream>
#include <limits>
#include <nlohmann/json.hpp>
#include <stdexcept>

namespace slam {
namespace {
constexpr const char *retail_sha =
    "185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6";
constexpr const char *demo_sha =
    "31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00";
struct KnownTable {
  const char *id;
  const char *title;
  const char *filename;
  const char *dat_sha;
  TableGameplaySupport gameplay;
};
// Hashes: analysis/table-profiles.json, extracted by original Retail initializers.
// Code reference builds: Mean Demo and Pirate/Space/Demon Retail. Mean also
// imports Retail data normalized to its native data ABI; bounded acceptance
// is indexed in the corresponding analysis/*-completion-contract.json.
constexpr std::array<KnownTable, 4> tables{{
    {"mean", "Mean Machines", "MEAN.DAT",
     "1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f",
     TableGameplaySupport::Playable},
    {"pirate", "The Pirate", "PIRATE.DAT",
     "6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6",
     TableGameplaySupport::Playable},
    {"space", "Ace of Space", "SPACE.DAT",
     "18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b",
     TableGameplaySupport::Playable},
    {"demon", "Night of the Demon", "DEMON.DAT",
     "0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d",
     TableGameplaySupport::Playable},
}};
std::uint32_t address(const nlohmann::json &value) {
  const auto text = value.get<std::string>();
  std::size_t used = 0;
  const auto number = std::stoull(text, &used, 0);
  if (used != text.size() ||
      number > std::numeric_limits<std::uint32_t>::max())
    throw std::runtime_error("Invalid table build address");
  return static_cast<std::uint32_t>(number);
}
} // namespace
TableDefinition load_table_definition(const std::filesystem::path &profiles,
                                      const std::string &id) {
  const KnownTable *known = nullptr;
  for (const auto &table : tables)
    if (id == table.id)
      known = &table;
  if (!known)
    throw std::runtime_error("Unsupported table: " + id);
  std::ifstream input(profiles);
  if (!input)
    throw std::runtime_error("Missing table profiles: " + profiles.string());
  nlohmann::json metadata;
  input >> metadata;
  if (metadata.at("schema") != 1 ||
      metadata.at("build_sha256").get<std::string>() != retail_sha)
    throw std::runtime_error("Unsupported table geometry build");
  auto geometry = load_table_profile(profiles, id);
  if (geometry.dat_sha256 != known->dat_sha)
    throw std::runtime_error("Unsupported table DAT profile: " + id);
  const auto &row = metadata.at("tables").at(id);
  TableDefinition definition;
  definition.id = id;
  definition.display_name = known->title;
  definition.dat_filename = known->filename;
  definition.geometry = std::move(geometry);
  definition.geometry_build = {retail_sha, address(row.at("initializer")),
                               address(row.at("returned_descriptor")),
                               address(row.at("engine_descriptor"))};
  definition.capabilities = {true, true, true, known->gameplay};
  if (known->gameplay == TableGameplaySupport::Playable)
    definition.gameplay_executable_sha256 = id == "mean" ? demo_sha : retail_sha;
  return definition;
}
TableDefinition load_table_definition_for_data(const std::filesystem::path& profiles,
 const std::string& id, const std::filesystem::path& dat) {
 auto definition=load_table_definition(profiles,id);
 std::ifstream f(dat,std::ios::binary);
 if(!f)throw std::runtime_error("Missing table DAT: "+dat.string());
 std::vector<std::uint8_t> bytes{std::istreambuf_iterator<char>(f),{}};
 const auto hash=sha256(bytes);
 if(hash==amiga_table_sha256(id)||hash==amiga_v2_table_sha256(id)||(id=="demon"&&hash==amiga_demon_v3_sha256))definition.geometry.dat_sha256=hash;
 validate_table_dat(definition,bytes);
 return definition;
}
std::vector<TableDefinition>
load_table_definitions(const std::filesystem::path &profiles) {
  std::vector<TableDefinition> definitions;
  for (const auto &table : tables)
    definitions.push_back(load_table_definition(profiles, table.id));
  return definitions;
}
void validate_table_dat(const TableDefinition &definition,
                        const std::vector<std::uint8_t> &dat) {
  if (sha256(dat) != definition.geometry.dat_sha256)
    throw std::runtime_error("Unsupported DAT content for " + definition.id);
  validate_table_profile(definition.geometry, dat.size());
}
} // namespace slam
