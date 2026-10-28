#include "mean_material_bundle.h"
#include <cstring>
namespace slam {
namespace {
std::int32_t scaled(std::int32_t value, std::uint32_t factor) {
  const auto bits = 0u - std::uint32_t(value) * factor;
  const auto shifted = (bits >> 8) | (bits & 0x80000000u ? 0xff000000u : 0u);
  std::int32_t result;
  std::memcpy(&result, &shifted, sizeof result);
  return result;
}
} // namespace
bool mean_material_bundle(MeanObject &ball, unsigned material,
                          std::int32_t &normal, std::int32_t &tangent,
                          MeanMaterialBundleState &state,
                          bool &requested_services) {
  requested_services = false;
  if (material != 6 && material != 7)
    return false;
  if (state.field_services_1c != 0 ||
      (material == 7 && state.field_43f1da == 0 && state.field_43f390 < 0)) {
    normal = scaled(normal, 80);
    return true;
  }
  if (material == 6) {
    normal = scaled(normal, 64);
    return true;
  }
  if (state.field_43f1da != 0) {
    state.field_43f1da = 0;
    state.field_43f268 = {4, 3, 1, 0};
    state.field_43f390 = 250;
  }
  const auto x = (std::uint32_t(ball.i32(0)) & 0xffffu) + 0xc0000u;
  const auto y = (std::uint32_t(ball.i32(4)) & 0xffffu) + 0x2060000u;
  ball.put32(0, static_cast<std::int32_t>(x));
  ball.put32(8, static_cast<std::int32_t>(x));
  ball.put32(4, static_cast<std::int32_t>(y));
  ball.put32(0xc, static_cast<std::int32_t>(y));
  ball.put32(0x14, 0);
  ball.put32(0x18, -0x34000);
  normal = 1;
  tangent = 0;
  requested_services = true;
  return true;
}
} // namespace slam
