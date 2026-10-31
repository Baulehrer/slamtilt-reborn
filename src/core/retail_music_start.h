#pragma once
#include <cstdint>

namespace slam {
// Retail 0x40841c..0x408454: the retained post-F1 images predate the
// table-specific music bindings. Recover them from the original table data.
template <typename Machine> void initialize_retail_music_start(Machine &machine) {
  const auto descriptor = machine.rd(0x46c644, 4);
  const auto config = machine.rd(descriptor + 0x0c, 4);
  const auto bank = machine.rd(config + 0x08, 4);
  const auto order = machine.rd(config + 0x0c, 4);
  machine.wr(0x454a64, order, 4);
  machine.wr(0x454a3c, order, 4);
  machine.wr(0x454a68, bank, 4);
  machine.wr(0x454a38, bank, 4);
  machine.wr(0x454a54, 0, 4);
}
} // namespace slam
