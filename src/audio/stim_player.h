#pragma once
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <vector>
#include <xmp.h>
namespace slam {
enum class TrackerMix { Default, RetailMono };
class StimPlayer {
public:
  explicit StimPlayer(const std::filesystem::path &, int order = 0,
                      TrackerMix mix = TrackerMix::Default);
  StimPlayer(const std::vector<std::uint8_t> &, int order = 0,
             TrackerMix mix = TrackerMix::Default);
  ~StimPlayer();
  StimPlayer(const StimPlayer &) = delete;
  StimPlayer &operator=(const StimPlayer &) = delete;
  void render(std::int16_t *, std::size_t frames);
  void restart();
  void select_order(int);
  // Bounded STIM playback: stop at F00 or first module loop, zero the tail.
  // Use this API or render(), never alternate them on the same player.
  std::size_t render_once(std::int16_t *, std::size_t frames);
  bool ended() const { return ended_; }
  static constexpr int sample_rate = 44100;

private:
  xmp_context context_ = nullptr;
  int order_ = 0;
  TrackerMix mix_ = TrackerMix::Default;
  void initialize(int load_result);
  bool ended_ = false;
  std::vector<std::int16_t> frame_pcm_;
  std::size_t frame_offset_ = 0;
};
} // namespace slam
