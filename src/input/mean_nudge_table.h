#pragma once
#include <cstdint>
#include <vector>
namespace slam {
// Bounded417ae0..417b5a. Services remain caller-owned, including40f754.
struct MeanNudgeTableRequest {
  std::uint32_t target, eax, edx, ecx, ebx;
  std::vector<std::int32_t> stack;
};
struct MeanNudgeTable {
  std::int32_t field_038 = 0, engine_field_14 = 0;
  std::vector<MeanNudgeTableRequest> requests;
  // service34_result is the actual shared-DMD admission result.
  void callback(std::int32_t eax, std::int32_t service34_result);
};
} // namespace slam
