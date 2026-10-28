#include "collision/mean_bitmap.h"
#include "assets/table_profile.h"
namespace slam {
std::vector<std::uint8_t> load_mean_collision_overlay(const std::filesystem::path &path) {
  return table_collision_overlay(path, mean_table_profile());
}
} // namespace slam
