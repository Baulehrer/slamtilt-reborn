#pragma once
#include <array>
#include <cstdint>
namespace slam {
struct MeanNudge {
  // Raw original globals, names retained until their entire lifecycle is
  // proven.
  std::int32_t field_429858 = 0, field_42985c = -1, field_42980c = 0,
               field_429808 = 0, field_429810 = -1;
  std::int32_t field_43e564 = 0, field_43e410 = 0, field_43e724 = 0,
               field_43e71c = 0, field_43e70c = 0;
  std::array<std::int32_t, 17> horizontal{}, vertical{};
  void accept_pending(); // Original404b48..404b82 with EDX=0.
  void step();           // Original40671c..406804, after each5ms physics step.
};
} // namespace slam
