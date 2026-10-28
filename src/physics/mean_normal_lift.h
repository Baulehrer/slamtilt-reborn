#pragma once
#include "physics/flipper_lift.h"
namespace slam {
// Temporary bounded static intermediate for original 0x40e1d0.
// User DAT is borrowed, never copied into distributed source.
struct MeanNormalLift : FlipperLift {
  const std::vector<std::uint8_t>* dat = nullptr;
  std::uint32_t rd(std::uint32_t address, unsigned size) {
    if (address >= 0x1100000 && dat && address - 0x1100000 < dat->size()) {
      const auto offset = address - 0x1100000;
      if (size > dat->size() - offset)
        throw std::out_of_range("Mean normal DAT read");
      std::uint32_t value = 0;
      for (unsigned i = 0; i < size; ++i)
        value |= std::uint32_t((*dat)[offset + i]) << (8 * i);
      return value;
    }
    return FlipperLift::rd(address, size);
  }
};
void flipper_40e1d0(MeanNormalLift&);
} // namespace slam
