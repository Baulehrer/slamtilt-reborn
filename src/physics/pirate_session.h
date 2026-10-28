#pragma once
#include "physics/pirate_step_lift.h"
#include "assets/table_profile.h"
#include "core/audio_request.h"
#include <array>
#include <filesystem>
namespace slam {
enum class PirateTickMode { PhysicsOnly, Full };
// Original gameplay timing; display interpolation is owned by the SDL renderer.
class PirateSession {
public:
  PirateSession(const std::filesystem::path& prepared,
                const std::filesystem::path& dat,
                PirateTickMode mode=PirateTickMode::PhysicsOnly);
  // Audio observer binds to this session; never copy or move that binding.
  PirateSession(const PirateSession&)=delete;
  PirateSession& operator=(const PirateSession&)=delete;
  PirateSession(PirateSession&&)=delete;
  PirateSession& operator=(PirateSession&&)=delete;
  void reset();
  bool new_game();
  void launch();
  // Original configurable left-special key (default left Ctrl).
  bool special_left();
  bool initials_active() const;
  bool initials_key(std::uint32_t original_scan);
  bool initials_character(char character);
  bool game_over() const;
  unsigned ball_number() const;
  std::array<std::uint32_t,15> lifecycle_state() const;
  std::array<std::uint8_t,50> highscores() const;
  void set_highscores(const std::array<std::uint8_t,50>& records);
  const std::vector<std::uint8_t>& executable_image() const {return machine_.image;}
  void flippers(bool left, bool right);
  // Original key-down actions: -1 left, +1 right, 0 upward.
  bool nudge(int direction);
  std::array<std::uint32_t,18> nudge_state() const;
  std::array<std::uint32_t,5> magnasaver_state() const;
  void step();
  void enable_lamps(bool enable);
  void enable_audio_events(bool enable);
  std::vector<AudioRequest> take_audio_requests();
  // Explicit diagnostic input only: reposition an already free ball. Never
  // injects rule/capture state, a trigger ID, scores, timers or callbacks.
  // Layer rebinding invalidates the previous switch cache normally.
  void diagnostic_waypoint(const TableProfile &,unsigned layer,int x,int y,unsigned ball_index=0);
  std::vector<std::uint8_t> rule_state() const;
  std::vector<std::uint8_t> video_state() const;
  std::vector<std::uint8_t> ball_pool_state() const;
  std::vector<std::uint8_t> lamp_states() const;
  std::array<std::uint8_t,100> ball(unsigned index=0) const;
  std::array<std::uint16_t,3> poses() const;
  unsigned phase() const;
  unsigned ball_count() const;
  std::array<std::uint32_t,11> timing_state() const;
  std::array<std::uint8_t,1920> dmd_pixels() const;
  std::array<std::uint8_t,4> dmd_palette_indices() const;
  const std::vector<std::uint8_t>& table_data() const {return machine_.dat;}
  std::uint64_t ticks() const {return ticks_;}
private:
  // Offline search may copy complete reachable silent states; never a live UI action.
  friend struct PirateSessionSearch;
  PirateStepLift machine_;
  std::vector<std::uint8_t> initial_image_,initial_runtime_,initial_dat_;
  bool left_=false,right_=false;
  std::uint64_t ticks_=0;
  PirateTickMode mode_;
  bool lamps_enabled_=false;
  bool audio_enabled_=false;
  std::vector<AudioRequest> audio_requests_;
};
}
