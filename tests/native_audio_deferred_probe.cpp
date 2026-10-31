#include "audio/native_audio.h"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <vector>

// A tiny valid STIM module keeps the SDL queue regression independent of
// copyrighted game files. The original x86 comparison is a separate test.
static std::vector<std::uint8_t> test_module() {
  std::vector<std::uint8_t> b(406 + 8 + 768 + 4 + 8 + 32, 0);
  auto be16 = [&](int p, int v) { b[p] = v >> 8; b[p+1] = v; };
  auto be32 = [&](int p, int v) { b[p] = v >> 24; b[p+1] = v >> 16; b[p+2] = v >> 8; b[p+3] = v; };
  b[0]='S'; b[1]='T'; b[2]='I'; b[3]='M';
  const int sample = 406 + 8 + 768;
  be32(4,sample); be16(16,1); be16(18,1); be16(20,1); be32(150,406-12);
  for(int ch=0;ch<4;++ch) { const int pos=414+ch*192; b[pos]=1; b[pos+1]=24; }
  be16(sample+4,16); b[sample+7]=64; be16(sample+10,16);
  for(int i=0;i<32;++i)b[sample+12+i]=(i%8<4)?96:160;
  return b;
}

int main(int argc, char** argv) {
  try {
    if (argc > 2) throw std::runtime_error("Usage: native_audio_deferred_probe [STIM]");
    auto module = test_module();
    if (argc == 2) {
      std::ifstream in(argv[1], std::ios::binary);
      if (!in) throw std::runtime_error("Missing STIM module");
      module.assign(std::istreambuf_iterator<char>(in), {});
    }
    slam::NativeAudio audio(std::vector<std::vector<std::uint8_t>>{module, module});
    audio.request(0x90, 0, 0);
    audio.request(0x88, 1, 0);
    audio.set_paused(false);
    audio.pump();
    // Freeze device consumption so that only the command can change the queue.
    audio.set_paused(true);
    const auto queued = audio.queued_bytes();
    if (queued <= 0) throw std::runtime_error("Expected queued upper-track PCM");
    audio.request(0x84, 0, 0);
    if (audio.queued_bytes() != queued)
      throw std::runtime_error("Deferred lower request discarded foreground PCM");
    audio.request(0x80, 0, 0);
    if (audio.queued_bytes() != queued)
      throw std::runtime_error("Lower cancellation discarded foreground PCM");
    audio.request(0x8c, 0, 0);
    if (audio.queued_bytes() != 0)
      throw std::runtime_error("Upper cancellation did not clear old foreground");
    audio.pump();
    // A base-only lower cancellation is also inaudible.
    audio.set_paused(false); audio.pump(); audio.set_paused(true);
    const auto base_queued = audio.queued_bytes();
    if (base_queued <= 0) throw std::runtime_error("Expected queued base PCM");
    audio.request(0x80, 0, 0);
    if (audio.queued_bytes() != base_queued)
      throw std::runtime_error("Inactive lower cancellation discarded base PCM");
    audio.request(0x84, 0, 0);
    if (audio.queued_bytes() != 0)
      throw std::runtime_error("New foreground did not clear old base PCM");
    audio.set_paused(false); audio.pump(); audio.set_paused(true);
    if (audio.queued_bytes() <= 0) throw std::runtime_error("Expected queued lower PCM");
    audio.request(0x80, 0, 0);
    if (audio.queued_bytes() != 0)
      throw std::runtime_error("Active lower cancellation did not clear old PCM");
    std::cout << "Deferred music commands preserve the foreground SDL queue\n";
  } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
