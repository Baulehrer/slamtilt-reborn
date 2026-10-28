#pragma once
#include "mean_step.h"
namespace slam {
// Original table globals only; names remain offsets until semantics proven.
struct MeanMaterialBundleState {
  std::int32_t field_services_1c = 0;
  std::uint16_t field_43f1da = 0;
  std::int16_t field_43f390 = -1;
  std::array<std::uint8_t, 4> field_43f268{};
};
// 41e602/41e625: callback-local changes only. Return true for material6/7.
// Accepted material7 requests external audio/notification services; these are
// reported via requested_services and do not affect the returned ball state.
bool mean_material_bundle(MeanObject &ball, unsigned material,
                          std::int32_t &normal, std::int32_t &tangent,
                          MeanMaterialBundleState &state,
                          bool &requested_services);
} // namespace slam
