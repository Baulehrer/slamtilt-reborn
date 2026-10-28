#pragma once
#include <cstddef>
#include <cstdint>
namespace slam {
struct MeanCameraBall {
  std::int16_t render_y = 0;
  std::uint16_t state = 0;
};
// Original429aec/429af0/43e77c/4297f4. Caller supplies viewport geometry.
struct MeanCameraState {
  std::int32_t field_429aec = 0, field_429af0 = 0;
  std::int32_t scroll = 0, previous_scroll = 0;
};
void mean_camera_step(MeanCameraState &, const MeanCameraBall *, std::size_t,
                      std::int32_t max_scroll, std::int32_t field_frontend_1c);
} // namespace slam
