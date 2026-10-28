#include "mean_minigame_lift.h"
namespace slam {
void MeanMinigameLift::service(std::uint32_t target) {
  const auto draw_text=[&](){
    if(!text_service) return;
    // Lifted external calls omit the hardware return address; text ABI includes it.
    const auto stack=r[4];r[4]-=4;
    text_service(*this,target);r[4]=stack;
  };
  if (target == 0x406680 || target == 0x406574 || target == 0x40f91c) {
    auto source = r[0], mask = r[2];
    if (target == 0x40f91c) {
      source = r[0];
      mask = r[2] + r[3] * 480;
    }
    std::array<std::uint8_t, 480> data{};
    for (unsigned i = 0; i < data.size(); ++i)
      data[i] = byte(source + i);
    auto decoded = decode_windows_dmd(data);
    if (target == 0x406680)
      pixels = decoded;
    else
      for (unsigned i = 0; i < pixels.size(); ++i)
        if ((byte(mask + i / 8) >> (7 - i % 8)) & 1)
          pixels[i] = decoded[i];
  } else if (target == 0x40560c)
    points += r[0];
  else if (target == 0x405c60)
    audio_requests.push_back({r[0], r[2], r[3]});
  else if (target == 0x40587c || target == 0x4058a0)
    // Original wrappers: EAX order, EDX bank. Queue preserves event order.
    audio_requests.push_back({0,r[2],r[0],target==0x40587c ? 0x88u : 0x84u});
  else if (target == 0x4058c8)
    audio_requests.push_back({0,0,0,0x80});
  else if (target == 0x405f98) {
    requested_display_callback=rd(r[4]+8,4);
    r[0] = 1;
    r[4] += 12;
  } else if (target == 0x406280) {
    draw_text();
    r[4] += 4;
  }
  else if (target == 0x4060a4)
    mean_clear_windows_dmd(pixels,static_cast<std::int32_t>(r[0]));
  else if (target == 0x40617c) {
    draw_text();
    r[4] += 8;
  }
  else if (target == 0x4060f8) {
    draw_text();
  } else if (target == 0x405814)
    wr(0x43942c + r[0] * 0xac, r[2], 4);
  else if (target == 0x416fe0) {
    if (rd(rd(0x43f068, 4) + 0x30, 4) != 2 || rd(0x43f3a2, 2) != 0)
      throw std::runtime_error("Unsupported mini-game lamp reset");
    wr(0x438b2c, 0, 4);
    wr(0x438b34, 0xffffffff, 4);
    wr(0x43f3b8, 0, 2);
  } else if (target != 0x419f6c && target != 0x405824 &&
             target != 0x405858)
    throw std::runtime_error("Unknown mini-game service" +
                             std::to_string(target));
}
} // namespace slam
