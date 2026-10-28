#include "input/mean_nudge.h"
#include <iostream>
#include <type_traits>
int main() {
  static_assert(std::is_trivially_copyable<slam::MeanNudge>::value,
                "binary probe");
  slam::MeanNudge n;
  unsigned operation;
  while (std::cin.read(reinterpret_cast<char *>(&operation), 4)) {
    if (!std::cin.read(reinterpret_cast<char *>(&n), sizeof(n)))
      return 2;
    if (operation == 0)
      n.step();
    else
      n.accept_pending();
    std::cout.write(reinterpret_cast<const char *>(&n), sizeof(n));
  }
}
