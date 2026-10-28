#pragma once
#include <array>
#include <cstdint>
namespace slam {
struct MeanMaterial5State {
  std::array<std::uint8_t, 4> field_1dc{};
  std::array<std::int16_t, 4> fields_ee1c{};
  std::array<std::array<std::uint8_t, 4>, 4> commands_26c{};
  std::array<std::uint8_t, 4> command_268{}, command_300{};
  std::int16_t field_1da = 0, field_37a = -1;
  std::int32_t mode = 2;
  std::uint32_t field_054 = 0;
};
struct MeanMaterial5Event {
  bool sample = false, group = false, stop84 = false;
  std::uint32_t score_add = 0, callback = 0;
};
// Original41e269..41e7fe after common50000score/normal response.
MeanMaterial5Event mean_material5_rules(std::int32_t x, std::int32_t y,
                                        MeanMaterial5State &);
} // namespace slam
