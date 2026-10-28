#pragma once
#include "physics/mean_step.h"
#include <filesystem>
#include <string>
#include <vector>
namespace slam {
struct TableLayer {
  std::uint32_t normal_offset, hit_offset, render_offset, stride;
  unsigned planes;
  std::uint32_t switch_callback;
};
struct TableProfile {
  std::string name, dat_sha256;
  std::vector<TableLayer> layers;
  std::uint32_t graphics_descriptor = 0;
};
// Directory records extracted by actual original table initializer execution.
TableProfile load_table_profile(const std::filesystem::path &,
                                const std::string &);
std::filesystem::path default_table_profiles();
const TableProfile &
mean_table_profile(); // Includes separately verified transient layer4.
void validate_table_profile(const TableProfile &, std::size_t dat_size);
void table_set_layer(MeanObject &, const TableProfile &, unsigned layer,
                     std::uint32_t dat_base);
void table_configure_bits(const MeanObject &, const TableProfile &,
                          std::uint32_t dat_base, MeanCollisionBits &);
std::vector<std::uint8_t>
table_collision_overlay(const std::filesystem::path &dat, const TableProfile &,
                        unsigned layer = 0, unsigned height = 600);
} // namespace slam
