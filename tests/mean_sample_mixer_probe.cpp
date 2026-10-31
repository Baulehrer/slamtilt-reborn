#include "audio/mean_sample_mixer.h"
#include <algorithm>
#include <iostream>
#include <stdexcept>
static void require(bool x, const char *m) {
  if (!x)
    throw std::runtime_error(m);
}
int main() {
  try {
    std::vector<std::uint8_t> dat(0x6d40e + 0x16b0);
    for (std::size_t i = 0; i < 0x1941; ++i)
      dat[0x63a1d + i] = std::uint8_t(i % 256);
    for (std::size_t i = 0; i < 0xfee; ++i)
      dat[0x6535e + i] = std::uint8_t(255 - i % 256);
    slam::MeanSampleMixer a(dat), b(dat);
    a.request(9, 8);
    a.request(4, 3);
    b.request(9, 8);
    std::vector<std::int16_t> x(44100 * 2), y(x.size());
    a.mix(x.data(), 44100);
    for (std::size_t i = 0; i < 44100; i += 137)
      b.mix(y.data() + i * 2, std::min<std::size_t>(137, 44100 - i));
    require(x == y, "Chunk size or duplicate request changed PCM");
    {
      for (std::size_t i = 0; i < 8948; ++i)
        dat[0x38ef0 + i] = std::uint8_t((i * 37 + 19) & 255);
      slam::MeanSampleMixer queued(dat), latest(dat);
      queued.request(-1, 1, 0x437e10, 285, 48);
      queued.request(7, 9, 0x437e10, 428, 64);
      latest.request(-1, 1, 0x437e10, 428, 64);
      std::vector<std::int16_t> before(1024), after(1024);
      queued.mix(before.data(), 512);
      latest.mix(after.data(), 512);
      require(before == after && std::any_of(before.begin(), before.end(), [](auto v) { return v != 0; }),
              "Queued descriptor did not retain latest period/volume");
    }
    require(a.active() == 0, "Sample did not finish");
    require(x[2] == 0 && x[4] == 42,
            "Original integer frequency/signed PCM wrong");
    a.reset();
    b.reset();
    a.request(6, 5, 0x437d14);
    b.request(6, 5, 0x437d14);
    std::fill(x.begin(), x.end(), 0);
    std::fill(y.begin(), y.end(), 0);
    a.mix(x.data(), 44100);
    for (std::size_t i = 0; i < 44100; i += 137)
      b.mix(y.data() + i * 2, std::min<std::size_t>(137, 44100 - i));
    require(x == y && x[0] == -43 && a.active() == 0,
            "Second original profile or PCM chunk invariant failed");
    a.request(9, 8);
    a.mix(x.data(), 1);
    require(a.active() == 1, "First voice absent");
    a.request(4, 3);
    a.mix(x.data(), 1);
    require(a.active() == 2, "Second voice absent");
    a.request(2, 1);
    a.mix(x.data(), 1);
    require(a.active() == 2, "Rejected request changed voice count");
    a.reset();
    std::fill(x.begin(), x.end(), 0);
    a.mix(x.data(), 10);
    require(a.active() == 0 && x[0] == 0, "Reset not silent");
    bool bad = false;
    try {
      slam::MeanSampleMixer invalid({});
    } catch (...) {
      bad = true;
    }
    require(bad, "Truncated sample accepted");
    std::cout << "Sample duration/chunks/dedup/two voices/reset verified\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
