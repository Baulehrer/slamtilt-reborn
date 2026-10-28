#include "rules/mean_restart_gate.h"
#include <iostream>
int main() {
  unsigned op, state;
  std::int32_t gate;
  while (std::cin >> op >> gate >> state) {
    unsigned decision = 0;
    if (op == 1)
      slam::mean_restart_gate_exit(gate);
    else
      decision = static_cast<unsigned>(slam::mean_restart_gate(gate, state));
    std::cout << decision << ' ' << gate << '\n';
  }
}
