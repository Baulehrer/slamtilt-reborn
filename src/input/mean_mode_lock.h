#pragma once
#include "mean_nudge_table.h"
#include <array>
namespace slam {
// Actual4172a8/4172e4/4175d4; caller owns service34 and40f754 effects.
struct MeanModeLock {
  std::int32_t service_1c=0, engine_30=2, engine_44=0;
  std::uint16_t field_384=0,field_3a6=0,field_39e=0,field_3a8=0;
  std::int32_t field_030=0,field_064=0,field_038=0;
  std::array<std::uint8_t,4> selected_lamp{};
  std::vector<MeanNudgeTableRequest> requests;
  void press(std::int32_t admission, std::int32_t indexed_438bdc);
};
}
