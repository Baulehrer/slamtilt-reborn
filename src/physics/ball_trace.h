#pragma once
#include <cstdint>
#include <filesystem>
#include <vector>
namespace slam {
struct BallState {
  std::int32_t x, y, vx, vy;
  std::uint16_t field_58;
};
std::vector<BallState> load_ball_trace(const std::filesystem::path &path);
// Exact wrapping adds at demo0x40a0d2/0x40a0dd; force/collision stages are
// separate.
void integrate_position(BallState &state);
} // namespace slam
