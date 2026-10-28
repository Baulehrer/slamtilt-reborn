#pragma once
#include <array>
#include <cstdint>
namespace slam {
// Actual40f754: selectors in order stack_arg1,ECX,EBX,EDX,entryEAX.
inline void mean_capture_delay(std::int32_t handle, std::int32_t &field_024,
                               std::array<std::int32_t, 5> &delays,
                               const std::array<std::int32_t, 5> &selectors,
                               std::int32_t delay) {
  if (!handle)
    return;
  field_024 = 0;
  for (unsigned i = 0; i < 5; ++i)
    delays[i] = selectors[i] ? 0 : delay;
}
} // namespace slam
