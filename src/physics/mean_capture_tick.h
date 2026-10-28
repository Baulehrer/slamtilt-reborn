#pragma once
#include "mean_step.h"

namespace slam {
struct MeanCaptureTickState {
  std::array<std::int32_t, 3> field_438b68{{-1, 100, 0}};
  std::array<std::int32_t, 3> field_438b74{{-1, 0, 0}};
  std::array<std::int32_t, 3> field_438b50{{0, 0, 0}};
  std::int16_t field_43f380 = 50, field_43f364 = 0;
  std::int16_t field_43f204 = 0, field_43f392 = 0;
  std::int16_t field_43f1fe = 0, field_43f200 = 0, field_43f202 = 0;
  std::int16_t field_43f1fa = 0;
  std::int32_t table_mode = 2;
};
struct MeanCaptureTickEvent {
  std::uint32_t score_request = 0, field_player_08_add = 0;
  bool rule_service_request = false;
  unsigned services_1c_samples = 0;
};
// Initial human mode1..3, single ball, field43f392==0, including sixth award.
// Exact415fd7/416440/417068/4164a4/416db8 local state. False is unsupported.
bool mean_capture_tick(MeanObject &ball, MeanCaptureTickState &state,
                       std::uint32_t dat_base, MeanCaptureTickEvent &event,
                       bool services_1c = false);
} // namespace slam
