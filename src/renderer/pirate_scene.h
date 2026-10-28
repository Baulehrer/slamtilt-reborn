#pragma once
#include <algorithm>
#include <array>
#include <cstdint>

namespace slam {
// Retail4054a6/4054b5 feeds the source viewport consumed by402e58.
// Its fixed destination makes positive source displacement move the scene left/up.
// The backing surface has an eight-pixel border;4035bf clips Y to[0,max+8].
inline std::array<int,2> pirate_scene_origin(int camera_scroll,
    std::int32_t horizontal_pixels,std::int32_t vertical_fixed,int maximum_scroll=200) {
  const int vertical_pixels=vertical_fixed/65536-(vertical_fixed<0&&vertical_fixed%65536!=0);
  return {-horizontal_pixels,-std::clamp(camera_scroll+vertical_pixels,0,maximum_scroll+8)};
}
}
