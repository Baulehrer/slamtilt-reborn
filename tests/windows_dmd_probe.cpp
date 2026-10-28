#include "dmd/windows_dmd.h"
#include <iostream>
int main() {
  std::array<std::uint8_t, 480> input{};
  std::cin.read(reinterpret_cast<char *>(input.data()), input.size());
  if (std::cin.gcount() != 480)
    return 2;
  const auto pixels = slam::decode_windows_dmd(input);
  std::cout.write(reinterpret_cast<const char *>(pixels.data()), pixels.size());
}
