#include "mean_camera.h"
namespace slam {
namespace {
std::int32_t sub(std::int32_t a, std::int32_t b) {
  return std::int32_t(std::uint32_t(a) - std::uint32_t(b));
}
std::int32_t shl16(std::int32_t a) {
  return std::int32_t(std::uint32_t(a) << 16);
}
std::int32_t sar(std::int32_t a, unsigned n) {
  const auto v = std::int64_t(a);
  return std::int32_t(
      v >= 0 ? v / (std::int64_t(1) << n)
             : -((-v + (std::int64_t(1) << n) - 1) / (std::int64_t(1) << n)));
}
} // namespace
void mean_camera_step(MeanCameraState &s, const MeanCameraBall *balls,
                      std::size_t count, std::int32_t max_scroll,
                      std::int32_t frontend_1c) {
  s.previous_scroll = s.scroll;
  std::int32_t y = -1;
  for (std::size_t i = 0; i < count; ++i)
    if (balls[i].state != 6 && balls[i].render_y >= y)
      y = balls[i].render_y;
  if (y == -1)
    for (std::size_t i = 0; i < count; ++i)
      if (balls[i].render_y >= y)
        y = balls[i].render_y;
  auto velocity = sar(sub(s.field_429aec, shl16(y)), 3);
  const auto delta = sub(s.field_429af0, velocity);
  if (delta > 0x20000)
    velocity = sub(s.field_429af0, 0x20000);
  if (delta < -0x20000)
    velocity = sub(s.field_429af0, -0x20000);
  s.field_429af0 = velocity;
  s.field_429aec = sub(s.field_429aec, velocity);
  const auto offset = frontend_1c / 4;
  s.scroll = sub(sar(s.field_429aec, 16), offset);
  if (s.scroll < 0) {
    s.scroll = 0;
    s.field_429aec = shl16(offset);
  }
  if (s.scroll > max_scroll) {
    s.scroll = max_scroll;
    s.field_429aec =
        shl16(std::int32_t(std::uint32_t(offset) + std::uint32_t(max_scroll)));
  }
}
} // namespace slam
