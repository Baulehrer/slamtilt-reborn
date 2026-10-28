#include "mean_restart_gate.h"
#include <cstring>
namespace slam {
MeanRestartDecision mean_restart_gate(std::int32_t &gate, std::uint16_t state) {
  if (state != 0xffff)
    return MeanRestartDecision::Continue;
  if (gate > 0)
    return MeanRestartDecision::Wait;
  gate = 1;
  return MeanRestartDecision::Initialize;
}
void mean_restart_gate_exit(std::int32_t &gate) {
  const std::uint32_t bits = static_cast<std::uint32_t>(gate) - 1u;
  std::memcpy(&gate, &bits, sizeof gate);
}
} // namespace slam
