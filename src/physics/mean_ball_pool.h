#pragma once
#include "mean_step.h"
namespace slam {
struct MeanBallPool {
  std::array<MeanObject, 8> objects{};
  unsigned count = 1;
  // Original408050: preserve all bytes except state58 and append one slot.
  MeanObject *allocate() {
    if (count >= objects.size())
      return nullptr;
    auto &b = objects[count++];
    b.put16(0x58, 0xffff);
    return &b;
  }
  void remove_drained() {
    for (unsigned i = 0; i < count; ++i) {
      if (objects[i].u16(0x58) == 5 && count > 1) {
        objects[i] = objects[count - 1];
        --count;
        objects[count].put16(0x58, 5);
      }
    }
  }
  bool can_spawn(std::int32_t slot) const {
    if (slot >= 0)
      return false;
    for (unsigned i = 0; i < count; ++i)
      if (objects[i].u16(0x5a) == 5 &&
          (objects[i].u16(0x58) == 3 || objects[i].u16(0x58) == 6))
        return false;
    return true;
  }
};
} // namespace slam
