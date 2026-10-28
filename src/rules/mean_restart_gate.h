#pragma once
#include <cstdint>
namespace slam {
enum class MeanRestartDecision { Continue = 0, Initialize = 1, Wait = 2 };
// Original408915..408943: gate is shared by the entire ball pool.
// Initialize requires caller to invoke table+10 and set ball state0 afterward.
MeanRestartDecision mean_restart_gate(std::int32_t &field_43e79c,
                                      std::uint16_t ball_state);
// Original41b1f8, every layer3/switch1 exit; independent of table mode.
void mean_restart_gate_exit(std::int32_t &field_43e79c);
} // namespace slam
