#include "audio/mean_music_sequencer.h"
#include <algorithm>
#include <iostream>
#include <stdexcept>
using Bytes = std::vector<std::uint8_t>;
static Bytes module(bool stop) {
  Bytes b(406 + 8 + 768 + 4 + 8 + 32, 0);
  auto be16 = [&](int p, int v) {
    b[p] = v >> 8;
    b[p + 1] = v;
  };
  auto be32 = [&](int p, int v) {
    b[p] = v >> 24;
    b[p + 1] = v >> 16;
    b[p + 2] = v >> 8;
    b[p + 3] = v;
  };
  b[0] = 'S';
  b[1] = 'T';
  b[2] = 'I';
  b[3] = 'M';
  const int sample = 406 + 8 + 768;
  be32(4, sample);
  be16(16, 1);
  be16(18, 1);
  be16(20, 1);
  be32(150, 406 - 12);
  for (int ch = 0; ch < 4; ++ch) {
    const int pos = 414 + ch * 192;
    b[pos] = 1;
    b[pos + 1] = 24;
    if (stop) {
      b[pos + 18] = 0x60;
      b[pos + 19] = 0xc0;
    }
  }
  be16(sample + 4, 16);
  b[sample + 7] = 64;
  be16(sample + 10, 16);
  for (int i = 0; i < 32; ++i)
    b[sample + 12 + i] = (i % 8 < 4) ? 96 : 160;
  return b;
}
static void require(bool value, const char *message) {
  if (!value)
    throw std::runtime_error(message);
}
int main() {
  try {
    const auto base = module(false), event = module(true);
    slam::MeanMusicSequencer s({base, event});
    slam::StimPlayer reference(base, 0, slam::TrackerMix::RetailMono);
    std::vector<std::int16_t> a(400), b(400), upper(88200);
    s.request90(0, 0);
    slam::StimPlayer base_reference(base, 0, slam::TrackerMix::RetailMono);
    s.render(a.data(), 200);
    base_reference.render(b.data(), 200);
    require(a == b, "Base90 PCM mismatch");
    s.request84(0, 0);
    s.render(a.data(), 200);
    s.request88(1, 0);
    s.render(a.data(), 200);
    s.stop88();
    s.stop84();
    s.render(a.data(), 200);
    base_reference.render(b.data(), 200);
    require(a == b && s.foreground_service() == 0x90,
            "Base90 did not resume exact PCM");
    s.request88(1, 0);
    s.request84(0, 0);
    s.request90(0, 0);
    slam::StimPlayer new_base(base, 0, slam::TrackerMix::RetailMono);
    s.render(a.data(), 200);
    new_base.render(b.data(), 200);
    require(a == b && s.foreground_service() == 0x90,
            "Base90 replacement did not clear overlays");
    s.reset();
    s.request84(0, 0);
    s.render(a.data(), 200);
    reference.render_once(b.data(), 200);
    require(a == b, "Initial84 mismatch");
    s.request88(1, 0);
    s.render(a.data(), 200);
    require(s.foreground_service() == 0x88, "88 did not preempt");
    s.stop88();
    s.render(a.data(), 200);
    reference.render_once(b.data(), 200);
    require(a == b, "Paused84 did not resume exact PCM");
    s.request88(1, 0);
    s.request84(0, 0);
    s.stop88();
    slam::StimPlayer fresh(base, 0, slam::TrackerMix::RetailMono);
    s.render(a.data(), 200);
    fresh.render_once(b.data(), 200);
    require(a == b, "Pending84 did not replace saved84");
    s.request88(1, 0);
    s.stop84();
    s.render(upper.data(), 44100);
    require(s.foreground_service() == 0, "F00 completion failed");
    require(
        std::any_of(upper.begin(), upper.end(), [](auto v) { return v != 0; }),
        "Upper PCM silent");
    require(std::all_of(upper.end() - 1000, upper.end(),
                        [](auto v) { return v == 0; }),
            "Stop tail not silent");
    s.request84(0, 0);
    s.request88(1, 0);
    s.render(upper.data(), 44100);
    require(s.foreground_service() == 0x84,
            "Natural upper end did not resume84");
    slam::MeanMusicSequencer chunks({base, event});
    chunks.request84(0, 0);
    chunks.request88(1, 0);
    std::vector<std::int16_t> chunked(88200);
    for (std::size_t i = 0; i < 44100; i += 137)
      chunks.render(chunked.data() + i * 2,
                    std::min<std::size_t>(137, 44100 - i));
    require(upper == chunked,
            "Upper completion/resume changed with chunk size");
    s.reset();
    s.render(a.data(), 200);
    require(std::all_of(a.begin(), a.end(), [](auto v) { return v == 0; }),
            "Reset not silent");
    bool rejected = false;
    try {
      s.request84(2, 0);
    } catch (const std::exception &) {
      rejected = true;
    }
    require(rejected, "Invalidbank accepted");
    std::cout << "Mean audio priority/pause/pending/F00/reset verified\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
