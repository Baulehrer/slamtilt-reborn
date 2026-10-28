#include "assets/mean_point_forces.h"
#include <set>
#include <stdexcept>
namespace slam {
MeanPointForceData load_mean_point_forces(const std::vector<std::uint8_t> &image,
                                         std::uint32_t descriptor) {
  auto offset = [&](std::uint32_t address, unsigned length) -> std::size_t {
    if (address < 0x400000 || std::uint64_t(address - 0x400000) + length > image.size())
      throw std::runtime_error("Mean point-force pointer outside original image");
    return address - 0x400000;
  };
  auto word = [&](std::uint32_t address) {
    const auto o = offset(address, 2);
    return std::uint16_t(image[o] | (unsigned(image[o + 1]) << 8));
  };
  auto dword = [&](std::uint32_t address) {
    const auto o = offset(address, 4);
    std::uint32_t v = 0;
    for (unsigned i = 0; i < 4; ++i) v |= std::uint32_t(image[o + i]) << (i * 8);
    return v;
  };
  MeanPointForceData result;
  auto address = dword(dword(descriptor)); // Original404598..4045c9.
  std::set<std::uint32_t> seen;
  while (address) {
    if (seen.size() >= 256 || !seen.insert(address).second)
      throw std::runtime_error("Invalid cyclic Mean point-force list");
    result.nodes.push_back({std::int16_t(word(address + 4)),
                           std::int16_t(word(address + 6)),
                           std::int16_t(word(address + 8)),
                           std::int16_t(word(address + 10))});
    address = dword(address);
  }
  // Original404fd7/405011: ESI=432ecc is retained across40e840.
  for (unsigned i = 0; i < 10000; ++i)
    result.lookup.push_back(word(0x432ecc + i * 2));
  return result;
}
} // namespace slam
