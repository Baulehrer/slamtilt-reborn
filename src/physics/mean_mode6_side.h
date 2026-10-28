#pragma once
#include "mean_step.h"
namespace slam {
struct MeanMode6SideState {
  std::int16_t field_43f380 = 0, field_43f370 = 0, field_43f364 = 0;
  std::int16_t field_43f38e = -1, field_43f368 = -1, field_43f36c = -1;
  std::int32_t active_count = 1, field_438b40 = 0, field_438b38 = 0;
  std::array<std::int32_t, 3> field_438b68{}, field_438b80{};
  std::array<std::int32_t, 3> field_438b74{{-1, 100, 0}}, field_438b50{};
  bool callback3_occupied = false;
};
struct MeanMode6SideEvent {
  bool transfer_requested = false, lamp_reset_requested = false;
  unsigned services_1c_samples = 0, early_transfer_count = 0;
  std::uint32_t score_request = 0, field_player_08_add = 0;
};
// Original415fd7/4164e1 mode6 state3 callbacks2/4.
bool mean_mode6_side_tick(MeanObject &, MeanMode6SideState &,
                          MeanMode6SideEvent &, bool services_1c = false,
                          std::uint32_t dat_base = 0x1100000);
} // namespace slam
