#include "mean_stock_car.h"
#include <algorithm>
#include <stdexcept>
namespace slam {
MeanStockCarEvent mean_stock_car_bumper(MeanBallResetState &s, unsigned material,
                                       bool suppressed, std::uint32_t handle) {
  MeanStockCarEvent e;
  if (suppressed || (material != 3 && material != 4)) return e;
  auto &f = s.fields;
  auto word = [&](unsigned o) { return std::uint16_t(f[o] | (unsigned(f[o+1]) << 8)); };
  auto put = [&](unsigned o, std::uint32_t v, unsigned n=2) {
    for (unsigned i=0;i<n;++i) f[o+i] = v >> (8*i);
  };
  // Actual419da4 changes selection/lamp commands, never engine mode or366.
  if (material == 3 && !word(0x384) && s.table_mode <= 4 &&
      !std::all_of(f.begin()+0x1e0,f.begin()+0x1e5,[](auto v){return v != 0;})) {
    const auto previous = static_cast<std::int16_t>(word(0x1e6));
    if (previous < 0 || previous >= 5) throw std::runtime_error("Invalid original mode selection");
    unsigned selected = previous;
    do { selected = (selected + 1) % 5; } while (f[0x1e0+selected]);
    put(0x1e6, selected);
    f[0x2bc+previous*4] = f[0x1e0+previous] ? 1 : 2;
    f[0x2bc+selected*4] = 4; f[0x2bd+selected*4] = 6;
    f[0x2be +selected*4] = f[0x2bf+selected*4] = 0;
    e.selected_changed = selected != unsigned(previous);
  }
  const auto remaining = static_cast<std::int16_t>(word(0x38a));
  if (remaining <= 0) return e;
  put(0x38a, std::uint16_t(remaining-1));
  if (remaining == 1) f[0x2a0] = 2;
  e.score = 5000000; e.callback = 0x413770;
  put(0x038, handle, 4);
  if (handle) put(0x024, 0, 4);
  return e;
}
}
