#include "physics/ball_trace.h"
#include <fstream>
#include <limits>
#include <nlohmann/json.hpp>
#include <stdexcept>
namespace slam {
std::vector<BallState> load_ball_trace(const std::filesystem::path &path) {
  std::ifstream input(path);
  if (!input)
    throw std::runtime_error("Cannot open original ball trace");
  nlohmann::json trace;
  input >> trace;
  if (trace.at("build_sha256") !=
      "31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00")
    throw std::runtime_error("Unsupported ball trace build");
  const auto &samples = trace.at("samples");
  if (!samples.is_array() || samples.empty() || samples.size() > 100000)
    throw std::runtime_error("Invalid ball trace length");
  auto signed32 = [](const nlohmann::json &v) {
    const auto n = v.get<std::int64_t>();
    if (n < std::numeric_limits<std::int32_t>::min() ||
        n > std::numeric_limits<std::int32_t>::max())
      throw std::runtime_error("Ball trace value outside signed32");
    return static_cast<std::int32_t>(n);
  };
  std::vector<BallState> result;
  for (const auto &sample : samples) {
    if (sample.at("step").get<std::size_t>() != result.size())
      throw std::runtime_error("Nonconsecutive trace steps");
    const auto field = sample.at("field_58").get<int>();
    if (field < 0 || field > 65535)
      throw std::runtime_error("Invalid trace field_58");
    result.push_back({signed32(sample.at("x")), signed32(sample.at("y")),
                      signed32(sample.at("vx")), signed32(sample.at("vy")),
                      static_cast<std::uint16_t>(field)});
  }
  if (trace.at("tick_count").get<std::size_t>() + 1 != result.size())
    throw std::runtime_error("Trace count mismatch");
  return result;
}
void integrate_position(BallState &s) {
  // Avoid signed overflow UB; original x86 ADD wraps modulo2^32.
  const auto wrap = [](std::int32_t a, std::int32_t b) {
    const std::uint32_t u = std::uint32_t(a) + std::uint32_t(b);
    const std::int64_t n =
        u >= 0x80000000u ? std::int64_t(u) - 0x100000000LL : std::int64_t(u);
    return static_cast<std::int32_t>(n);
  };
  s.x = wrap(s.x, s.vx);
  s.y = wrap(s.y, s.vy);
}
} // namespace slam
