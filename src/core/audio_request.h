#pragma once
namespace slam {
// Shared original sound-service ABI. For5c, bank/order carry field_1c/20.
struct AudioRequest {
  int service, bank, order;
  unsigned descriptor = 0;
};
}
