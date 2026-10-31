#include <optional>
#include "core/mean_display_sfx.h"
#include "rules/mean_skull_clock.h"
#include "rules/mean_mode_total_idle.h"
#include "audio/mean_display_audio.h"
#include "physics/mean_lane_saver.h"
#include "input/mean_nudge_table.h"
#include "input/mean_mode_lock.h"
#include "rules/mean_capture_delay.h"
#include "assets/table_profile.h"
#include "physics/mean_simulation.h"
#include "physics/mean_baseline_one_bundle.h"
#include "physics/mean_baseline_three_bundle.h"
#include "physics/mean_capture_bundle.h"
#include "physics/mean_mode4_capture.h"
#include "physics/mean_mode5_clock.h"
#include "physics/mean_mode6_capture.h"
#include "physics/mean_mode6_display.h"
#include "rules/mean_return_pass.h"
#include "rules/mean_return_pass_dispatch.h"
#include "rules/mean_player_record.h"
#include "dmd/mean_minigame_text.h"
#include "physics/mean_multiball.h"
#include "physics/mean_ramp_bundle.h"
#include "physics/mean_state7.h"
#include "physics/mean_switch_bundle.h"
#include "physics/mean_upper_entry.h"
#include "rules/mean_flipper_actions.h"
#include "rules/mean_game_end.h"
#include "rules/mean_material5.h"
#include "rules/mean_minigame2_input.h"
#include "rules/mean_mode4_clock.h"
#include "rules/mean_mode4_events.h"
#include "rules/mean_mode4_input.h"
#include "rules/mean_stock_car.h"
#include "rules/mean_pit_stop.h"
#include "rules/mean_mode4_switch.h"
#include "rules/mean_restart_gate.h"
#include "rules/mean_right_progress.h"
#include "rules/mean_left_progress.h"
#include "rules/mean_right_cancel.h"
#include "rules/mean_switch_reward.h"
#include "rules/mean_shared_reward.h"
#include "rules/mean_turn_clock.h"
#include "rules/mean_turn_entry.h"
#include <algorithm>
#include <fstream>
#include <nlohmann/json.hpp>
#include <stdexcept>
#include <type_traits>
namespace slam {
namespace {
void queue_display_audio(std::vector<MeanAudioRequest> &out, int old780,
                         const MeanDisplayRequest &request, bool admitted) {
  const auto command = mean_display_audio(old780, request.stack_0,
                                          request.stack_1, admitted, 0);
  if (command.service)
    out.push_back({command.service, command.bank, command.order});
  else if (admitted && old780 == 4 && request.stack_0 < 0)
    // Conditional cancellation: playback owns the actual active88 flag.
    // NativeAudio ignores this command, including queued PCM, if88 is inactive.
    out.push_back({0x8c, 0, 0});
}
std::vector<std::uint8_t> read(const std::filesystem::path &p) {
  std::ifstream f(p, std::ios::binary);
  if (!f)
    throw std::runtime_error("Missing Mean simulation input: " + p.string());
  return std::vector<std::uint8_t>(std::istreambuf_iterator<char>(f), {});
}
std::int16_t word(const std::vector<std::uint8_t> &b, std::size_t o) {
  const auto v = unsigned(b.at(o)) | (unsigned(b.at(o + 1)) << 8);
  return static_cast<std::int16_t>(v < 32768 ? int(v) : int(v) - 65536);
}
} // namespace
MeanSimulation::MeanSimulation(const std::filesystem::path &dat,
                               const std::filesystem::path &prepared,
                               const std::filesystem::path &trace) {
  bonus_font_ = load_mean_bonus_pixels(dat.parent_path() / "MAIN.DAT");
  bonus_animation_ = load_mean_bonus_animation(dat);
  main_mode_hud_assets_ = load_mean_main_mode_hud(dat,dat.parent_path()/"MAIN.DAT");
  player_hud_assets_ = load_mean_player_hud(dat,dat.parent_path()/"MAIN.DAT");
  idle_hud_assets_ = load_mean_idle_hud(dat,dat.parent_path()/"MAIN.DAT");
  material5_display_assets_ = load_mean_material5_display(dat);
  skillshot_display_assets_ = load_mean_skillshot_display(dat);
  mode4_idle_assets_ = load_mean_mode4_idle(dat);
  mode4_phase1_assets_ = load_mean_mode4_phase1(dat);
  lamp_visible_.fill(-1);
#ifdef SLAM_MEAN_FLIPPER_LIFT
  flippers_.image = read(prepared / "pe-data.bin");
  point_forces_ = load_mean_point_forces(flippers_.image, 0x438ae4);
  if (point_forces_.nodes.size() != 1)
    throw std::runtime_error("Unsupported original Mean point-force list");
  for (unsigned i=0;i<17;++i) {
    nudge_.horizontal[i]=static_cast<std::int32_t>(flippers_.rd(0x429814+i*4,4));
    nudge_.vertical[i]=static_cast<std::int32_t>(flippers_.rd(0x429860+i*4,4));
  }
  flippers_.image.resize(0x100000);
  lookup_.field_43e728.assign(flippers_.image.begin() + 0x2c9fc,
                              flippers_.image.begin() + 0x2d1fe);
  const auto globals = read(prepared / "engine-globals.bin"),
             poses = read(prepared / "flipper-state.bin");
  if (globals.size() != 160 || poses.size() != 108)
    throw std::runtime_error("Invalid captured flipper state");
  std::copy(globals.begin(), globals.end(), flippers_.image.begin() + 0x3e700);
  std::copy(poses.begin(), poses.end(), flippers_.image.begin() + 0x3e850);
#endif
#ifndef SLAM_MEAN_FLIPPER_LIFT
  throw std::runtime_error(
      "Generate the bounded Mean flipper lift before native simulation");
#endif
#ifdef SLAM_MEAN_BALL_PAIR_LIFT
  ball_pair_.image = flippers_.image;
  ball_pair_.wr(0x4298c8, 0x1000000, 4);
  ball_pair_.wr(0x4298cc, 0x1000080, 4);
  ball_pair_.wr(0x43e728, 0x42c9fc, 4);
  ball_pair_.wr(0x43e764, 0x1006000, 4);
  const auto pair_lut = read(prepared / "lookup.bin");
  std::copy(pair_lut.begin(), pair_lut.end(),
            ball_pair_.runtime.begin() + 0x6000);
#endif
  bits_.dat = read(dat);
#ifdef SLAM_MEAN_MINIGAME_LIFT
  const auto mini_cache = prepared.parent_path() / "mean-minigame-prepared";
  if (std::filesystem::exists(mini_cache / "image.bin") &&
      std::filesystem::exists(mini_cache / "runtime.bin")) {
    minigame_initial_image_ = read(mini_cache / "image.bin");
    minigame_initial_runtime_ = read(mini_cache / "runtime.bin");
    minigame_.dat = bits_.dat;
    minigame_.text_service=[this](MeanMinigameLift &m,std::uint32_t target){
      if(target==0x40617c && m.rd(0x43f3a4,2)==2 && m.r[3]==m.rd(0x43f1f6,2))
        minigame2_goal_seen_=true;
      mean_minigame_text_service(bonus_font_,m.pixels,target,m.r,
          [&](std::uint32_t a,unsigned n){return m.rd(a,n);});
    };
    minigame_available_ = minigame_initial_image_.size() == 0x100000 &&
                          minigame_initial_runtime_.size() == 0x10000;
  }
#endif
  if (bits_.dat.size() != 1622024)
    throw std::runtime_error("Mean DAT layout unsupported");
  lookup_.field_43e764 = read(prepared / "lookup.bin");
  if (lookup_.field_43e764.size() != 0x2800)
    throw std::runtime_error("Invalid original LUT");
  lookup_.field_43e744.assign(lookup_.field_43e764.begin() + 0x800,
                              lookup_.field_43e764.end());
#ifdef SLAM_MEAN_NORMAL_LIFT
  normal_.image=read(prepared / "pe-data.bin");normal_.image.resize(0x100000);
  normal_.dat=&bits_.dat;
#else
  throw std::runtime_error("Generate bounded Mean normal decoder before native simulation");
#endif
  std::ifstream f(trace);
  nlohmann::json j;
  f >> j;
  const auto w =
      j.at("initial_state").at("raw_words").get<std::vector<std::uint32_t>>();
  if (w.size() != 25)
    throw std::runtime_error("Missing original initial state");
  for (std::size_t i = 0; i < w.size(); ++i)
    for (unsigned k = 0; k < 4; ++k)
      ball_.bytes[i * 4 + k] = (w[i] >> (k * 8)) & 255;
  if (ball_.u16(0x48) != 0 || ball_.i32(0x4c) != 0x6040 || ball_.u16(0x22) != 0)
    throw std::runtime_error(
        "Initial trace uses an unsupported table layer/force/callback");
  initial_ball_ = ball_;
  pool_.objects[0] = ball_;
  dat_base_ = std::uint32_t(ball_.i32(0x40)) - 0x9ba36;
}
void MeanSimulation::set_original_contact_context(
    const std::vector<std::uint32_t> &poses,
    const std::vector<std::uint32_t> &globals) {
  if (poses.size() != 27 || globals.size() != 40)
    throw std::runtime_error("Invalid original contact context");
#ifdef SLAM_MEAN_FLIPPER_LIFT
  for (std::size_t i = 0; i < poses.size(); ++i)
    flippers_.wr(0x43e850 + i * 4, poses[i], 4);
  for (std::size_t i = 0; i < globals.size(); ++i)
    flippers_.wr(0x43e700 + i * 4, globals[i], 4);
  // At4088f0 entry the original outer-loop pose update has already happened.
  input_enabled_ = false;
#endif
}
void MeanSimulation::reset() {
  // A new native game starts with fresh input edges, independent of held keys
  // in the preceding session (including GameOver and repeated resets).
  left_ = right_ = launch_pressed_ = false;
  audio_requests_.clear();
  minigame_steps_=0;
  material5_hits_ = material5_groups_ = 0;
  award_bank_starts_ = award_bank_awards_ = 0;
  side_extra_balls_ = 0;
  switch_rewards_ = 0;
  pending_mode4_rewards_ = 0;
  mode4_starts_ = mode4_completions_ = state7_steps_ = 0;
  switch_reward_variants_.fill(0);
  pit_stats_={};
  stock_stats_={};
  speed_stats_={};
  monster_stats_={};
  rally_stats_={};
  offroad_stats_={};
  chicken_stats_={};
  gear_stats_={};
  kickback_consumptions_=0;
  lane_saver_frame_=0;lane_saver_patches_=0;
  mean_lane_saver_patch(bits_.dat,0x959f6,0x9ba36,false);
  game_over_ = false;
  field_43d864_=false;
  const auto h=nudge_.horizontal,v=nudge_.vertical;
  nudge_=MeanNudge{}; nudge_.horizontal=h; nudge_.vertical=v;
  nudge_tilt_=MeanNudgeTilt{}; nudge_ticks_=0;
  return_passes_=return_pass_awards_=0;
  material5_display_ = {};
  mean_display_sfx_cursor_ = 0;
  idle_hud_visible_=false;
  idle_hud_={};
  player_hud_={};player_hud_.field_engine_5c=50;
  player_hud_visible_=false;
  main_mode_hud_={};
  main_mode_hud_visible_=false;
  skillshot_display_visible_ = false;
  bonus_active_ = false;
  bonus_display_ = {};
  bonus_table_ = {};
  bonus_dmd_ = {};
  bonus_display_ticks_ = bonus_starts_ = bonus_completions_ = 0;
  field_43e79c_ = 1; // Explicit direct initial table+10 call, original40893a.
  restart_initializations_ = restart_waits_ = 0;
  ball_ = initial_ball_;
  mean_initialize_ball(ball_, dat_base_);
  pool_ = {};
  multiball_release_ = {};
  lamp_commands_ = {};
  for (auto &command : lamp_commands_)
    command[0] = 2;
  lamp_on_.fill(false);
  lamp_updates_.fill(0);
  lamp_events_ = {};
  target_reward_ = {};
  ball_reset_state_ = {};
  mean_initialize_player_record(ball_reset_state_.player_record);
  auto put = [&](unsigned o, std::uint32_t v) {
    for (unsigned i = 0; i < 4; ++i)
      ball_reset_state_.fields[o + i] = v >> (8 * i);
  };
  put(0x06c, 3);
  put(0x070, 0x6040);
  put(0x074, dat_base_ + 0x959f6);
  put(0x078, dat_base_ + 0x9ba36);
  put(0x07c, dat_base_ + 0xb3b36);
  put(0x090, dat_base_ + 0xcbb96);
  bonus_turn_ = {};
  bonus_awards_ = last_bonus_ = 0;
  lamp_mode_input_ = {};
  award_bank_054_ = 0;
  top_target_hits_ = top_target_cycles_ = 0;
  lamp_visible_.fill(-1);
  mode6_starts_ = 0;
  mode6_side_ = {};
  pool_.objects[0] = ball_;
  current_ball_ = 0;
  max_balls_ = 1;
  multiball_spawns_ = 0;
  drains_ = 0;
  score_ = MeanScore{};
  material_state_ = {};
  capture_state_ = {};
  capture_state_.field_438b68 = {0, 0, 0};
  capture_state_.field_438b74 = {0, 0, 0};
  capture_state_.field_43f380 = 0;
  captures_ = releases_ = upper_captures_ = 0;
  mode_resets_ = 0;
  mode5_awards_ = ball_saves_ = 0;
  mode5_state_ = {};
  for (unsigned i = 0; i < 6; ++i)
    mode5_state_.field_43f23c[i * 4] = 2;
  mode5_state_.field_43f260[0] = 2;
  field_438afc_ = {};
  reward_display_pending_ = false;
  mode6_display_pending_ = false;
  reward_requests_ = reward_completions_ = 0;
  minigame_active_ = false;
  mode4_right_ = {};
  right_gate_ = {};
  point_force_context_ = point_force_suppressed_ = false;
  point_force_updates_ = 0;
  right_cancellations_ = 0;
  right_arms_ = right_markers_ = right_captures_ = 0;
  minigame_starts_ = minigame_completions_ = 0;
  minigame2_goal_seen_=false;
  upper_state_ = {};
  upper_state_.field_438b5c = {0, 0, 0};
  upper_state_.field_43f36a = 0;
  // Native deterministic seed policy; original startup seed was time-dependent.
  random_state_ = {};
  mean_random_tick(random_state_); // Original startup404593.
  score_events_ = 0;
  contact_animations_ = {};
  display_ticks_ = 0;
  ball_number_ = 1;
  extra_balls_ = 0;
  collisions_ = 0;
  launches_ = 0;
  events_ = 0;
  gameplay_ = true;
  // Original419e68 defaults, then the verified419b00 table reset.
  sync_ball_reset_fields(false);
  MeanBallResetEvents reset_event;
  mean_ball_reset(ball_reset_state_, reset_event);
  audio_requests_.push_back({0x90, 0, 4});
  sync_ball_reset_fields(true);
  capture_state_.table_mode = upper_state_.table_mode = 1;
  rebuild_lamps();
  status_ = "ready: Enter launches, Shift flippers, R resets";
}
void MeanSimulation::set_flippers(bool left, bool right) {
  if(field_43d864_)left=right=false;
  // Original input changes734 on key edges;4080dc clears it at bonus entry.
  // Holding keys across drain therefore does not synthesize a fresh press.
  if (bonus_active_) {
    if (left != left_) mean_bonus_input_edge(bonus_display_, false, left);
    if (right != right_) mean_bonus_input_edge(bonus_display_, true, right);
  }
#ifdef SLAM_MEAN_MINIGAME_LIFT
  if (minigame_active_ && minigame_.rd(0x43f3a4, 2) == 2) {
    const auto edge = [&] {
      MeanBallResetState raw;
      for (unsigned i = 0; i < raw.fields.size(); ++i)
        raw.fields[i] = minigame_.byte(0x43f000 + i);
      auto e = mean_minigame2_input(raw, 1);
      for (auto o : {0x01cu, 0x034u, 0x040u})
        for (unsigned i = 0; i < 4; ++i)
          minigame_.byte(0x43f000 + o + i) = raw.fields[o + i];
      if (e.descriptor)
        audio_requests_.push_back({0x5c, int(e.edx), int(e.ebx), e.descriptor});
    };
    if (left && !left_)
      edge();
    if (right && !right_)
      edge();
  }
#endif
  if (gameplay_ && !game_over_ && !bonus_active_ && !minigame_active_) {
    const auto action = [&](bool side) {
      sync_ball_reset_fields(false);
      const auto gear_before=lamp_events_.field_43f1e8;
      const auto sample = mean_flipper_actions(
          ball_reset_state_, capture_state_.table_mode, 1, side);
      // Project only writes belonging to the original input callbacks.
      // Full reset projection also touches unrelated capture slots.
      if (capture_state_.table_mode == 4) {
        ball_reset_state_.table_mode = 4;
        const auto &raw = ball_reset_state_.fields;
        const auto index = (raw[0x3a8] | (raw[0x3a9] << 8)) & 127;
        const auto value =
            static_cast<std::int32_t>(flippers_.rd(0x438bdc + index * 4, 4));
        auto probe = ball_reset_state_;
        const auto request = mean_mode4_input(probe, side, value, 0);
        const bool admitted = request.callback &&
            request_material5_display(request.callback, 0, true);
        const auto effect = mean_mode4_input(ball_reset_state_, side, value,
                                             admitted ? 1u : 0u);
        load_mode4_fields();
        if (effect.callback)
          apply_capture_delay(admitted, {1, 1, 1, 1, 1}, 0);
        if (effect.exit_to_mode2) {
          const auto display = material5_display_;
          finish_mode4(true);
          material5_display_ = display;
        }
      }
      const auto &f = ball_reset_state_.fields;
      for (unsigned i = 0; i < 3; ++i)
        lamp_events_.field_43f1e8[i] = f[0x1e8 + i];
      if(lamp_events_.field_43f1e8!=gear_before)++gear_stats_.rotations;
      for (unsigned i = 0; i < 5; ++i)
        lamp_mode_input_.field_1ec[i] = f[0x1ec + i];
      upper_state_.field_43f1fc =
          static_cast<std::int16_t>(f[0x1fc] | (f[0x1fd] << 8));
      for (unsigned i = 0; i < 63; ++i)
        std::copy_n(f.begin() + 0x208 + i * 4, 4, lamp_commands_[i].begin());
      if (sample)
        audio_requests_.push_back({0x5c, 2, 1, sample});
    };
    // Original40425d/40436c key-down edges, not held-key ticks.
    if (left && !left_)
      action(false);
    if (right && !right_)
      action(true);
  }
#ifdef SLAM_MEAN_FLIPPER_LIFT
  input_enabled_ = true;
  if (left != left_)
    flippers_.wr(0x4298b8, left ? 1 : 0xffffffffu, 4);
  if (right != right_) {
    flippers_.wr(0x4298bc, right ? 1 : 0xffffffffu, 4);
    flippers_.wr(0x4298c0, right ? 1 : 0xffffffffu, 4);
  }

#else
  (void)left;
  (void)right;
#endif
  left_ = left;
  right_ = right;
}
std::uint16_t MeanSimulation::flipper_pose(unsigned index) const {
#ifdef SLAM_MEAN_FLIPPER_LIFT
  if (index > 2)
    throw std::out_of_range("flipper index");
  const unsigned offset = 0x3e850 +
                          (index == 0   ? 52
                           : index == 1 ? 26
                                        : 0) +
                          0xa;
  return flippers_.image.at(offset) |
         (std::uint16_t(flippers_.image.at(offset + 1)) << 8);
#else
  (void)index;
  return 0;
#endif
}
void MeanSimulation::configure_bits() {
  table_configure_bits(ball_, mean_table_profile(), dat_base_, bits_);
}
void MeanSimulation::nudge(int horizontal, bool upward) {
  if (horizontal < -1 || horizontal > 1) throw std::invalid_argument("Nudge direction");
  if (game_over_) return;
  if (upward) nudge_.field_429858=-1;
  if (horizontal) nudge_.field_42980c=horizontal;
  nudge_tilt_.field_43d864=field_43d864_;
  nudge_tilt_.field_43e7a0=capture_state_.table_mode;
  nudge_tilt_.count=pool_.count;
  const int action=nudge_tilt_.key_event();
  if (action==1) apply_tilt();
  if (action==0) apply_capture_delay(request_material5_display(0x40f93c,0),{1,1,1,1,1},0);
}
bool MeanSimulation::step() {
  if (game_over_) return false;
#ifdef SLAM_MEAN_FLIPPER_LIFT
  flippers_.wr(0x43e724,std::uint32_t(nudge_.field_43e724),4);
  flippers_.wr(0x43e564,std::uint32_t(nudge_.field_43e564),4);
  flippers_.wr(0x43e71c,std::uint32_t(nudge_.field_43e71c),4);
  flippers_.wr(0x43e410,std::uint32_t(nudge_.field_43e410),4);
#endif
  const bool result=step_impl();
  nudge_.step(); //404a48/404a7c: also during bonus and minigame.
  if (++nudge_ticks_%4==0) { nudge_tilt_.outer_tick(); nudge_.accept_pending(); }
  return result;
}
void MeanSimulation::apply_capture_delay(bool accepted,const std::array<std::int32_t,5>&selectors,std::int32_t delay) {
  auto &f=ball_reset_state_.fields;
  std::int32_t field024=std::uint32_t(f[0x024]) | (std::uint32_t(f[0x025])<<8) | (std::uint32_t(f[0x026])<<16) | (std::uint32_t(f[0x027])<<24);
  std::array<std::int32_t,5> delays={upper_state_.field_438b5c[2],capture_state_.field_438b68[2],capture_state_.field_438b74[2],mode4_right_.field_438b80[2],multiball_release_.slot[2]};
  mean_capture_delay(accepted,field024,delays,selectors,delay);
  for(unsigned i=0;i<4;++i) { f[0x024+i]=std::uint32_t(field024)>>(i*8); f[0x038+i]=accepted?255:0; }
  upper_state_.field_438b5c[2]=delays[0];capture_state_.field_438b68[2]=delays[1];capture_state_.field_438b74[2]=delays[2];mode4_right_.field_438b80[2]=delays[3];multiball_release_.slot[2]=delays[4];
}
bool MeanSimulation::step_impl() {
  if (game_over_)
    return false;
  mean_random_tick(random_state_); // 404a6d: before each5ms gameplay step.
  if (bonus_active_) {
#ifdef SLAM_MEAN_FLIPPER_LIFT
    // 404a3e..404a4d: RNG and flipper input continue during mode3.
    if (input_enabled_) {
      flippers_.r[4] = 0x200f000;
      flippers_.push(0x2100000);
      flipper_4084bc(flippers_);
    }
#endif
    return step_bonus();
  }
  if (minigame_active_) {
#ifdef SLAM_MEAN_FLIPPER_LIFT
    if (input_enabled_) {
      flippers_.r[4] = 0x200f000;
      flippers_.push(0x2100000);
      flipper_4084bc(flippers_);
    }
#endif
    // 404a12: shared+44 skips408874;40721c invokes table+28 at50Hz.
    if (++display_ticks_ % 4 == 0)
      return step_minigame();
    return true;
  }
  if (gameplay_ && capture_state_.table_mode == 4) {
    step_mode4_clock();
  }
  if (!step_mode4_spawn())
    return false;
  // Original408898 table callback+30 precedes every per-ball callback.
  // 414cfa..414d20: original pre-ball table tick,200Hz; service1c native0.
  if (gameplay_ && capture_state_.table_mode < 4 &&
      lamp_mode_input_.field_37a >= 0) {
    const auto callback = mean_award_bank_tick(lamp_mode_input_.field_37a,
                                               award_bank_054_, lamp_commands_);
    if (callback) {
      const bool admitted=request_material5_display(callback,0);
      apply_capture_delay(admitted,{1,1,1,1,1},0);
    }
    if (callback == 0x410504)
      audio_requests_.push_back({0x80, 0, 0});
  }
  const bool monster_clock = capture_state_.table_mode==5 && mode5_state_.field_43f1e6==1;
  const bool rally_clock = capture_state_.table_mode==5 && mode5_state_.field_43f1e6==2;
  const bool offroad_clock = capture_state_.table_mode==5 && mode5_state_.field_43f1e6==4;
  const bool chicken_clock = capture_state_.table_mode==5 && mode5_state_.field_43f1e6==0;
  if (gameplay_ &&
      mean_mode5_clock(mode5_state_, capture_state_, pool_.count)) {
    if(monster_clock)++monster_stats_.timeouts;
    if(rally_clock)++rally_stats_.timeouts;
    if(offroad_clock)++offroad_stats_.ends;
    if(chicken_clock)++chicken_stats_.timeouts;
    ++mode_resets_;
    rebuild_lamps();
    // Actual4194e4 after timed mode return: resume bank music or cancel84.
    audio_requests_.push_back({lamp_mode_input_.field_37a >= 0 ? 0x84 : 0x80,
                              0, lamp_mode_input_.field_37a >= 0 ? 62 : 0});
  }
  upper_state_.field_43f1e6 = mode5_state_.field_43f1e6;
  upper_state_.table_mode = capture_state_.table_mode;
#ifdef SLAM_MEAN_FLIPPER_LIFT
  if (input_enabled_) {
    flippers_.r[4] = 0x200f000;
    flippers_.push(0x2100000);
    flipper_4084bc(flippers_);
  }
#endif
  for (current_ball_ = 0; current_ball_ < pool_.count; ++current_ball_) {
    ball_ = pool_.objects[current_ball_];
    ball_drained_ = false;
    configure_bits();
    if (!physics_step()) {
      pool_.objects[current_ball_] = ball_;
      return false;
    }
    if (gameplay_ && !ball_drained_ && ball_.u16(0x58) <= 2 && !switch_step()) {
      pool_.objects[current_ball_] = ball_;
      return false;
    }
    pool_.objects[current_ball_] = ball_;
    if (game_over_)
      return false;
    if (bonus_active_)
      return step_bonus();
    for (unsigned j = current_ball_ + 1; j < pool_.count; ++j)
      collide_pair(current_ball_, j);
  }
  ball_ = pool_.objects[0];
  // 404a88..404b15: table display callback419890 runs at20ms intervals.
  if (++display_ticks_ % 4 == 0) {
    // Original removal occurs in404d60 render preparation. Native deterministic
    // presentation cadence is50Hz; original variable frame timing is
    // unverified.
    pool_.remove_drained();
    if (minigame_active_)
      return step_minigame();
    // Original438b38/3c/40 is the SAME triplet used by418030 and callback4.
    // Preserve capture-side countdown writes before the50Hz renderer tick.
    auto &right_animation=contact_animations_[2];
    right_animation.countdown=mode4_right_.field_438b38;
    right_animation.cursor=mode4_right_.field_438b3c;
    right_animation.repetitions=mode4_right_.field_438b40;
    for (auto &animation : contact_animations_) animation.tick();
    // Original417dd4/438b44: descriptor draws complete immediately in SDL.
    const auto fence=mean_lane_saver_tick(upper_state_.field_438b44,true);
    ball_reset_state_.field_438b44=upper_state_.field_438b44[0];
    ball_reset_state_.field_438b4c=upper_state_.field_438b44[2];
    if(fence.draw_requested)lane_saver_frame_=fence.drawn_frame;
    if(fence.patch_requested){
      mean_lane_saver_patch(bits_.dat,0x959f6,0x9ba36,fence.enabled);
      ++lane_saver_patches_;
    }
    mode4_right_.field_438b38=right_animation.countdown;
    mode4_right_.field_438b3c=right_animation.cursor;
    mode4_right_.field_438b40=right_animation.repetitions;
    // 4198b3..4198cc, once per50Hz table-display tick.
    for (auto *slot : {&upper_state_.field_438b5c, &capture_state_.field_438b68,
                       &capture_state_.field_438b74, &multiball_release_.slot,
                       &mode4_right_.field_438b80})
      if ((*slot)[0] >= 0)
        --(*slot)[0];
    // Original419903..419912: same50Hz/service1c0 timer gate.
    auto &saved_fields = ball_reset_state_.fields;
    auto timer_3b6 = static_cast<std::int16_t>(saved_fields[0x3b6] |
                                               (saved_fields[0x3b7] << 8));
    if (timer_3b6 >= 0) {
      --timer_3b6;
      saved_fields[0x3b6] = timer_3b6;
      saved_fields[0x3b7] = std::uint16_t(timer_3b6) >> 8;
    }
    sync_ball_reset_fields(false);
    const auto pit_before=static_cast<std::int16_t>(ball_reset_state_.fields[0x398] |
        unsigned(ball_reset_state_.fields[0x399])<<8);
    mean_pit_stop_tick(ball_reset_state_, field_43d864_);
    if(pit_before==0 && !field_43d864_)++pit_stats_.timeouts;
    lamp_mode_input_.field_398 = static_cast<std::int16_t>(
        ball_reset_state_.fields[0x398] | (unsigned(ball_reset_state_.fields[0x399]) << 8));
    for (unsigned i=0;i<4;++i)
      std::copy_n(ball_reset_state_.fields.begin()+0x208+i*4,4,lamp_commands_[i].begin());
    if(!field_43d864_){
      auto count=std::uint16_t(ball_reset_state_.fields[0x39a]|(unsigned(ball_reset_state_.fields[0x39b])<<8));
      mean_skull_clock(lamp_mode_input_.field_3b0,count,lamp_commands_[20]);
      ball_reset_state_.fields[0x39a]=count;ball_reset_state_.fields[0x39b]=count>>8;
    }
    mean_return_pass_tick(ball_reset_state_);
    project_return_pass_fields();
    MeanTurnClockState clock;
    clock.field_3ae = mode5_state_.field_43f3ae;
    clock.field_390 = material_state_.field_43f390;
    clock.field_35a =
        static_cast<std::int16_t>(ball_reset_state_.fields[0x35a] |
                                  (ball_reset_state_.fields[0x35b] << 8));
    clock.field_3b0 = lamp_mode_input_.field_3b0;
    clock.field_af4 = ball_reset_state_.field_438af4;
    for (unsigned i = 0; i < 4; ++i)
      clock.fields_ee1c[i] = static_cast<std::int16_t>(
          ball_reset_state_.field_43ee1c[i * 2] |
          (ball_reset_state_.field_43ee1c[i * 2 + 1] << 8));
    clock.field_260 = mode5_state_.field_43f260;
    clock.field_268 = lamp_commands_[24];
    clock.field_258 = lamp_commands_[20];
    mean_turn_clock(clock);
    mode5_state_.field_43f3ae = clock.field_3ae;
    material_state_.field_43f390 = clock.field_390;
    ball_reset_state_.fields[0x35a] = clock.field_35a;
    ball_reset_state_.fields[0x35b] =
        static_cast<std::uint16_t>(clock.field_35a) >> 8;
    ball_reset_state_.field_438af4 = clock.field_af4;
    for (unsigned i = 0; i < 4; ++i) {
      ball_reset_state_.field_43ee1c[i * 2] = clock.fields_ee1c[i];
      ball_reset_state_.field_43ee1c[i * 2 + 1] =
          static_cast<std::uint16_t>(clock.fields_ee1c[i]) >> 8;
    }
    mode5_state_.field_43f260 = clock.field_260;
    lamp_commands_[24] = clock.field_268;
    lamp_commands_[20] = clock.field_258;
    // Native lamp consumption at the deterministic presentation cadence.
    // Preserve untouched base pixels; commands come from proven rule writes.
    for (unsigned i = 0; i < 6; ++i)
      std::copy_n(mode5_state_.field_43f23c.begin() + i * 4, 4,
                  lamp_commands_[13 + i].begin());
    lamp_commands_[22] = mode5_state_.field_43f260;
    for (unsigned i = 0; i < lamp_commands_.size(); ++i)
      if (mean_lamp_tick(lamp_commands_[i], lamp_on_[i])) {
        lamp_visible_[i] = lamp_on_[i] ? 1 : 0;
        ++lamp_updates_[i];
      }
    for (unsigned i = 0; i < 6; ++i)
      std::copy_n(lamp_commands_[13 + i].begin(), 4,
                  mode5_state_.field_43f23c.begin() + i * 4);
    mode5_state_.field_43f260 = lamp_commands_[22];
    if (capture_state_.table_mode == 4)
      step_mode4_display();
    // 404b18: scheduler4071e8 follows419890, at50Hz.
    if (!minigame_active_) step_shared_display();

  }
  return true;
}
void MeanSimulation::debug_start_multiball(bool released, bool mode6,
                                           int selected) {
  reset();
  field_43e79c_ = 0; // Original capture/release fixtures have left launch lane.
  if (released) {
    pool_.objects[0] = {};
    MeanMultiballReleaseState release;
    release.slot = {0, 0, 0};
    mean_multiball_release(pool_.objects[0], release, dat_base_);
    capture_state_.table_mode = 5;
    mode5_state_.field_43f1e6 = 4;
    mode5_state_.field_43f37e = 0;
  } else {
    auto &b = pool_.objects[0];
    b.put32(0, 14 * 65536);
    b.put32(4, 14 * 65536);
    b.put32(8, 14 * 65536);
    b.put32(12, 14 * 65536);
    b.put32(0x14, 0);
    b.put32(0x18, 0);
    b.put16(0x58, 3);
    b.put16(0x5a, 1);
    upper_state_.field_43f36a = -1;
    upper_state_.field_43f394 = -1;
    if (mode6)
      upper_state_.field_43f1f2 = 5;
    upper_state_.field_438b5c = {-1, 100, 0};
    mode5_state_.field_43f1e6 = selected;
    capture_state_.table_mode = upper_state_.table_mode = 2;
    captures_ = upper_captures_ = 1;
  }
  ball_ = pool_.objects[0];
}
void MeanSimulation::debug_start_rule_capture(bool reward) {
  debug_start_multiball(false, false, 0);
  if (reward) {
    // Existing original upper reward fixture: callback1/timer0/player reward1.
    upper_state_.field_43f36a = 0;
    upper_state_.field_43f200 = capture_state_.field_43f200 = 1;
  } else {
    // Original verify_mean_mode5_left.py fixture: (26,279), callback2, timer50.
    ball_.put32(0, 26 * 65536);
    ball_.put32(4, 279 * 65536);
    ball_.put32(8, ball_.i32(0));
    ball_.put32(12, ball_.i32(4));
    ball_.put16(0x5a, 2);
    capture_state_.field_43f380 = 50;
    capture_state_.table_mode = upper_state_.table_mode = 5;
    mean_mode5_begin(mode5_state_);
    capture_state_.field_438b74[0] = -1;
  }
  pool_.objects[0] = ball_;
}
bool MeanSimulation::debug_start_minigame() {
  // Diagnostic entry from the original selected3 capture fixture; no new
  // physics.
  reset();
  field_43e79c_ = 0; // Original captured-ball fixture is beyond ramp exit.
  ball_.put32(0, 14 * 65536);
  ball_.put32(4, 14 * 65536);
  ball_.put32(8, 14 * 65536);
  ball_.put32(12, 14 * 65536);
  ball_.put32(0x14, 0);
  ball_.put32(0x18, 0);
  ball_.put16(0x58, 3);
  ball_.put16(0x5a, 1);
  upper_state_ = {};
  upper_state_.field_43f36a = -2;
  upper_state_.field_43f1f2 = 1;
  upper_state_.field_43f1e6 = 3;
  mode5_state_.field_43f1e6 = 3;
  captures_ = upper_captures_ = 1;
  pool_.objects[0] = ball_;
  return start_minigame();
}
bool MeanSimulation::start_minigame() {
#ifdef SLAM_MEAN_MINIGAME_LIFT
  if (minigame_available_) {
    minigame_.revision=retail_minigame_?MeanMinigameRevision::Retail:MeanMinigameRevision::Demo;
    minigame_.image = minigame_initial_image_;
    std::copy(minigame_initial_runtime_.begin(),
              minigame_initial_runtime_.end(), minigame_.runtime.begin());
    minigame_steps_=0;
    minigame_.points = 0;
    minigame_.requested_display_callback = 0;
  minigame_.audio_requests.clear();
  minigame2_goal_seen_=false;
    minigame_.pixels = {};
    mode5_state_.field_43f384 = 0;
    mode5_state_.field_43f1e0[3] = 1;
    bool all = true;
    for (auto value : mode5_state_.field_43f1e0)
      all = all && value != 0;
    if (all)
      mode5_state_.field_43f1e0.fill(0);
    for (unsigned i = 0; i < 5; ++i)
      minigame_.wr(0x43f1e0 + i, mode5_state_.field_43f1e0[i], 1);
    minigame_.wr(0x43f200, capture_state_.field_43f200, 2);
    minigame_.wr(0x43f202, capture_state_.field_43f202, 2);
    minigame_.wr(0x43f1fa, capture_state_.field_43f1fa, 2);
    minigame_.wr(0x43f1e6, 3, 2);
    minigame_.wr(0x43f384, 0, 2);
    for (unsigned i = 0; i < 3; ++i) {
      minigame_.wr(0x438b5c + i * 4, upper_state_.field_438b5c[i], 4);
      minigame_.wr(0x438b68 + i * 4, capture_state_.field_438b68[i], 4);
      minigame_.wr(0x438b74 + i * 4, capture_state_.field_438b74[i], 4);
    }
    audio_requests_.push_back({0x88, 1, 53});
    audio_requests_.push_back({0x84, 0, 23});
    enter_minigame_display();
    minigame_active_ = true;
    ++minigame_starts_;
    status_ = "Mean mini-game: Shift steers";
    return true;
  }
#endif
  status_ = "Missing native mini-game cache";
  return false;
}
bool MeanSimulation::start_minigame2() {
#ifdef SLAM_MEAN_MINIGAME_LIFT
  if (!minigame_available_)
    return false;
  minigame_.revision=retail_minigame_?MeanMinigameRevision::Retail:MeanMinigameRevision::Demo;
    minigame_.image = minigame_initial_image_;
  std::copy(minigame_initial_runtime_.begin(), minigame_initial_runtime_.end(),
            minigame_.runtime.begin());
  sync_ball_reset_fields(false);
  for (unsigned i = 0; i < ball_reset_state_.fields.size(); ++i)
    if (i < 0x068 || i >= 0x1d4)
      minigame_.byte(0x43f000 + i) = ball_reset_state_.fields[i];
  for (auto o : {0x10u, 0x14u, 0x20u})
    minigame_.wr(0x1001000 + o, 0, 4);
  minigame_.wr(0x1001018, 0xffffffffu, 4);
  minigame_.wr(0x1001044, 1, 4);
  minigame_.wr(0x1001030, 4, 4);
  minigame_.wr(0x43efd4, 0, 4);
  minigame_.wr(0x43efcc, 0, 4);
  for (unsigned i = 0; i < 3; ++i) {
    minigame_.wr(0x438b5c + i * 4, upper_state_.field_438b5c[i], 4);
    minigame_.wr(0x438b68 + i * 4, capture_state_.field_438b68[i], 4);
    minigame_.wr(0x438b74 + i * 4, capture_state_.field_438b74[i], 4);
    minigame_.wr(0x438b80 + i * 4, mode4_right_.field_438b80[i], 4);
  }
  minigame_.wr(0x1002044, 0x40617c, 4);
  minigame_.wr(0x1002048, 0x4060f8, 4);
  minigame_.wr(0x100204c, 0x4060a4, 4);
  minigame_steps_=0;
  minigame_.points = 0;
  minigame_.requested_display_callback = 0;
  minigame_.audio_requests.clear();
  minigame_.pixels = {};
  enter_minigame_display();
  minigame_active_ = true;
  ++minigame_starts_;
  audio_requests_.push_back({0x88, 1, 56});
  audio_requests_.push_back({0x84, 0, 73});
  status_ = "original Mean second mini-game: Shift accelerates";
  return true;
#else
  return false;
#endif
}
bool MeanSimulation::step_minigame() {
#ifdef SLAM_MEAN_MINIGAME_LIFT
  minigame_.wr(0x1001054, left_ ? 0xffffffffu : 0, 4);
  minigame_.wr(0x1001058, right_ ? 0xffffffffu : 0, 4);
  minigame_.r[4] = 0x200f000;
  minigame_.push(0x200fff0);
  ++minigame_steps_;
  minigame_4180d0(minigame_);
  for (const auto &request : minigame_.audio_requests)
    audio_requests_.push_back({int(request.service), int(request.edx), int(request.ebx), request.descriptor});
  minigame_.audio_requests.clear();
  if (minigame_.points) {
    score_.add(minigame_.points);
    ++score_events_;
    minigame_.points = 0;
  }
  if (!minigame_.rd(0x1001044, 4)) {
    minigame_active_ = false;
    auto &display=material5_display_.scheduler;
    display.field_780=static_cast<std::int32_t>(minigame_.rd(0x1001010,4));
    display.field_784=static_cast<std::int32_t>(minigame_.rd(0x1001014,4));
    display.field_788=static_cast<std::int32_t>(minigame_.rd(0x1001018,4));
    display.field_78c=static_cast<std::int32_t>(minigame_.rd(0x100101c,4));
    display.field_790=minigame_.rd(0x1001020,4);
    display.field_7b4=static_cast<std::int32_t>(minigame_.rd(0x1001044,4));
    material5_display_.counter=static_cast<std::uint32_t>(display.field_78c);
    capture_state_.table_mode = minigame_.rd(0x1001030,4);
    if(minigame_.requested_display_callback==0x40f994 || minigame_.requested_display_callback==0x40fb78 || minigame_.requested_display_callback==0x41210c || minigame_.requested_display_callback==0x4122cc){
      const auto score=minigame_.rd(0x43f050,4);
      material5_display_.minigame_lap_points=minigame_.lap_award();
      material5_display_.field_43efdc=minigame_.rd(0x43efdc,4);
      material5_display_.field_43efcc=minigame_.rd(0x43efcc,4);
      request_material5_display(minigame_.requested_display_callback,score);
    }
    ++minigame_completions_;
    if (minigame_.rd(0x43f3a4, 2) == 2) {
      for (unsigned i = 0; i < ball_reset_state_.fields.size(); ++i)
        if (i < 0x068 || i >= 0x1d4)
          ball_reset_state_.fields[i] = minigame_.byte(0x43f000 + i);
      ball_reset_state_.table_mode = minigame_.rd(0x1001030, 4);
      load_mode4_fields();
      for (unsigned i = 0; i < 3; ++i)
        mode4_right_.field_438b80[i] = minigame_.rd(0x438b80 + i * 4, 4);
      ++mode4_completions_;
    }
    capture_state_.field_43f1fa =
        static_cast<std::int16_t>(minigame_.rd(0x43f1fa, 2));
    capture_state_.table_mode = minigame_.rd(0x1001030, 4);
    upper_state_.table_mode = capture_state_.table_mode;
    mode5_state_.field_43f1e6 = minigame_.rd(0x43f1e6, 2);
    rebuild_lamps();
    upper_state_.field_43f1e6 = mode5_state_.field_43f1e6;
    for (unsigned i = 0; i < 3; ++i) {
      upper_state_.field_438b5c[i] = minigame_.rd(0x438b5c + i * 4, 4);
      capture_state_.field_438b68[i] = minigame_.rd(0x438b68 + i * 4, 4);
      capture_state_.field_438b74[i] = minigame_.rd(0x438b74 + i * 4, 4);
    }
    status_ = "Mean mini-game complete; returning to table";
  }
  return true;
#else
  return false;
#endif
}
void MeanSimulation::sync_ball_reset_fields(bool load) {
  auto &f = ball_reset_state_.fields;
  auto field = [&](unsigned o, auto &v) {
    using T = std::remove_reference_t<decltype(v)>;
    if (load) {
      std::uint32_t value = 0;
      for (unsigned i = 0; i < sizeof(T); ++i)
        value |= std::uint32_t(f[o + i]) << (i * 8);
      v = static_cast<T>(value);
    } else {
      auto value = static_cast<std::uint32_t>(v);
      for (unsigned i = 0; i < sizeof(T); ++i)
        f[o + i] = value >> (i * 8);
    }
  };
  field(0x054, award_bank_054_);
  for (unsigned i = 0; i < 4; ++i) {
    field(0x1d4 + i, lamp_mode_input_.field_1d4[i]);
    field(0x060 + i, lamp_mode_input_.field_060[i]);
    field(0x1dc + i, lamp_mode_input_.field_1dc[i]);
  }
  for (unsigned i = 0; i < 5; ++i)
    field(0x1ec + i, lamp_mode_input_.field_1ec[i]);
  field(0x1da, material_state_.field_43f1da);
  field(0x390, material_state_.field_43f390);
  field(0x380, capture_state_.field_43f380);
  field(0x364, capture_state_.field_43f364);
  field(0x204, capture_state_.field_43f204);
  field(0x392, capture_state_.field_43f392);
  field(0x1fe, capture_state_.field_43f1fe);
  field(0x200, capture_state_.field_43f200);
  field(0x202, capture_state_.field_43f202);
  field(0x1fa, capture_state_.field_43f1fa);
  field(0x36a, upper_state_.field_43f36a);
  field(0x394, upper_state_.field_43f394);
  field(0x1f2, upper_state_.field_43f1f2);
  field(0x378, upper_state_.field_43f378);
  field(0x1fc, upper_state_.field_43f1fc);
  field(0x1e6, mode5_state_.field_43f1e6);
  field(0x384, mode5_state_.field_43f384);
  field(0x366, mode5_state_.field_43f366);
  field(0x064, multiball_release_.field_43f064);
  field(0x39e, multiball_release_.bits);
  field(0x3a6, multiball_release_.field_43f3a6);
  field(0x3b4, mode5_state_.field_43f3b4);
  field(0x39c, mode5_state_.field_43f39c);
  field(0x372, mode5_state_.field_43f372);
  field(0x38c, mode5_state_.field_43f38c);
  field(0x386, mode5_state_.field_43f386);
  field(0x376, mode5_state_.field_43f376);
  field(0x36e, mode5_state_.field_43f36e);
  field(0x37e, mode5_state_.field_43f37e);
  field(0x388, mode5_state_.field_43f388);
  field(0x3ae, mode5_state_.field_43f3ae);
  field(0x382, mode5_state_.field_43f382);
  field(0x38e, mode5_state_.field_43f38e);
  field(0x368, mode5_state_.field_43f368);
  field(0x36c, mode5_state_.field_43f36c);
  field(0x35e, mode5_state_.field_43f35e);
  field(0x050, mode5_state_.field_43f050);
  field(0x058, mode5_state_.field_43f058);
  field(0x05c, mode5_state_.field_43f05c);
  field(0x398, lamp_mode_input_.field_398);
  field(0x3ba, lamp_mode_input_.field_3ba);
  field(0x3bc, lamp_mode_input_.field_3bc);
  field(0x3a2, lamp_mode_input_.field_3a2);
  field(0x3b0, lamp_mode_input_.field_3b0);
  field(0x374, lamp_mode_input_.field_374);
  field(0x37c, lamp_mode_input_.field_37c);
  field(0x38a, lamp_mode_input_.field_38a);
  field(0x37a, lamp_mode_input_.field_37a);
  for (unsigned i = 0; i < 5; ++i)
    field(0x1e0 + i, mode5_state_.field_43f1e0[i]);
  for (unsigned i = 0; i < 3; ++i)
    field(0x1e8 + i, lamp_events_.field_43f1e8[i]);
  for (unsigned i = 0; i < 6; ++i)
    field(0x044 + i * 2, mode5_state_.field_43f044[i]);
  for (unsigned i = 0; i < 63; ++i)
    for (unsigned j = 0; j < 4; ++j)
      field(0x208 + i * 4 + j, lamp_commands_[i][j]);
  if(!load){
    ball_reset_state_.field_438b44=upper_state_.field_438b44[0];
    ball_reset_state_.field_438b4c=upper_state_.field_438b44[2];
  }
  if (load) {
    for (unsigned i = 0; i < 6; ++i)
      std::copy_n(lamp_commands_[13 + i].begin(), 4,
                  mode5_state_.field_43f23c.begin() + i * 4);
    mode5_state_.field_43f260 = lamp_commands_[22];
    upper_state_.field_43f1e6 = mode5_state_.field_43f1e6;
    upper_state_.field_43f1fa = capture_state_.field_43f1fa;
    upper_state_.field_43f200 = capture_state_.field_43f200;
    upper_state_.field_43f202 = capture_state_.field_43f202;
    multiball_release_.field_43f382 = mode5_state_.field_43f382;
    upper_state_.field_438b44[0] = ball_reset_state_.field_438b44;
    upper_state_.field_438b44[2] = ball_reset_state_.field_438b4c;
  }
}
void MeanSimulation::begin_bonus() {
  // 4080b4..4080e0: save before presentation, retain the current player.
  sync_ball_reset_fields(false);
  mean_ball_save(ball_reset_state_);
  capture_state_.table_mode = upper_state_.table_mode = 3;
  mode5_state_.field_engine_40 = 6;
  bonus_turn_.field_player_0e = ball_number_;
  bonus_turn_.field_player_10 = extra_balls_;
  bonus_turn_.field_player_12 = target_reward_.field_player_12;
  bonus_display_ = {};
  bonus_active_ = true;
  material5_display_.callback = 0;
  mean_display_bonus_enter(material5_display_.scheduler);
  ++bonus_starts_;
  ball_.put16(0x58, 0xffff);
  status_ = "original Mean bonus display";
}
bool MeanSimulation::step_bonus() {
  if (++display_ticks_ % 4 != 0)
    return true;
  ++bonus_display_ticks_;
  // Original4072de fast-forward skips phase1 before table+38 dispatch.
  const auto phase = bonus_display_.field_43e734 == 3 && bonus_display_.phase == 1
                         ? 2u : bonus_display_.phase;
  const auto old_timer = bonus_display_.timer;
  MeanBonusDisplayInput input;
  input.bonus = bonus_turn_.field_player_08;
  input.suppressed=field_43d864_;
  input.multiplier = bonus_turn_.field_player_12;
  if (phase == 0) {
    audio_requests_.push_back({0x88, 1, 49});
    mean_bonus_table_callback(bonus_table_, 0);
  } // Unknown player+0c uses0.
  if (phase <= 1)
    input.callback_result = mean_bonus_table_callback(bonus_table_, 1).result;
  else if (phase == 4)
    input.callback_result = mean_bonus_table_callback(bonus_table_, 2).result;
  const auto event = mean_bonus_display_step(bonus_display_, input);
  if (event.award) {
    last_bonus_ = event.score_argument;
    if (last_bonus_) {
      score_.add(last_bonus_);
      ++score_events_;
    }
    ++bonus_awards_;
  }
  if (phase <= 1 && bonus_table_.field_43f028 < 65)
    bonus_dmd_ =
        render_mean_bonus_intro(bonus_animation_, bonus_table_.field_43f028);
  else if (phase == 2 && bonus_display_.timer != 0) {
    const auto timer = bonus_display_.timer;
    if (timer <= 62)
      bonus_dmd_ = render_mean_bonus_pixels(
          bonus_font_,
          input.bonus ? MeanBonusScreen::Bank : MeanBonusScreen::NoBonus,
          std::max(0, 6 - int(timer / 2)), input.bonus, input.multiplier,
          score_.value());
    else if (input.bonus && input.multiplier != 1 && timer <= 124)
      bonus_dmd_ = render_mean_bonus_pixels(
          bonus_font_, MeanBonusScreen::Multiplier,
          std::max(0, 6 - int((timer - 62) / 2)), input.bonus, input.multiplier,
          score_.value());
  } else if (phase == 3)
    bonus_dmd_ = render_mean_bonus_pixels(
        bonus_font_, MeanBonusScreen::Held, 0, bonus_display_.bonus_total,
        input.multiplier, score_.value(), (old_timer & 16) == 0);
  else if (phase == 5)
    bonus_dmd_ =
        render_mean_bonus_pixels(bonus_font_, MeanBonusScreen::Total,
                                 std::max(0, 6 - int(old_timer / 2)),
                                 input.bonus, input.multiplier, score_.value());
  if (event.finish) {
    bonus_active_ = false;
    ++bonus_completions_;
    finish_turn();
    pool_.objects[0] = ball_;
    return !game_over_;
  }
  return true;
}
void MeanSimulation::finish_turn() {
  const bool extra_turn=mean_finish_bonus_turn(bonus_turn_);
  player_hud_.field_engine_60=extra_turn ? 0xffffffffu : 0;
  ball_number_ = bonus_turn_.field_player_0e;
  extra_balls_ = bonus_turn_.field_player_10;
  target_reward_.field_player_12 = bonus_turn_.field_player_12;
  // Full4083a9: native default selects field454aa4=0; the demo lacks this
  // finite boundary. Long-running diagnostic sweeps explicitly bypass it.
  if (!endless_play_ && mean_game_end_required(ball_number_, 0)) {
    game_over_ = true;
    capture_state_.table_mode = upper_state_.table_mode = 0;
    mode5_state_.field_engine_40 = 3;
    bonus_turn_.player_count = 0;
    pool_.count = 0;
    status_ = "GAME OVER: R starts a new game";
    return;
  }
  ball_reset_state_.table_mode = 3;
  ball_reset_state_.engine_3c = random_state_.field_43e7ac;
  MeanBallResetEvents event;
  mean_ball_reset(ball_reset_state_, event);
  audio_requests_.push_back({0x90, 0, 4});
  sync_ball_reset_fields(true);
  material5_display_.callback = 0;
  mean_display_bonus_return(material5_display_.scheduler);
  field_43d864_=false; // Original40786a, after table callbacks.
  capture_state_.table_mode = 1; // Original4078a0 after table callbacks.
  upper_state_.table_mode = 1;
  reward_display_pending_ = mode6_display_pending_ = false;
  // Original4080e0 marks first ballFFFF beforebonus;407808 leaves it for
  // the next408915 initializer, retaining the shared launch-lane gate.
  ball_.put16(0x58, 0xffff);
  rebuild_lamps();
  status_ = "next ball: Enter launches";
}
void MeanSimulation::rebuild_lamps() {
  // Only the original419f6c event boundaries. Unported input fields retain
  // explicit native defaults rather than guessed semantics.
  auto &s = lamp_mode_input_;
  s.field_1e0 = mode5_state_.field_43f1e0;
  s.field_1e8 = lamp_events_.field_43f1e8;
  s.field_1e6 = mode5_state_.field_43f1e6;
  s.field_384 = mode5_state_.field_43f384;
  s.field_3ae = mode5_state_.field_43f3ae;
  s.field_1f2 = upper_state_.field_43f1f2;
  s.field_394 = upper_state_.field_43f394;
  s.field_392 = capture_state_.field_43f392;
  s.field_204 = capture_state_.field_43f204;
  s.field_1fa = capture_state_.field_43f1fa;
  s.field_200 = capture_state_.field_43f200;
  s.field_202 = capture_state_.field_43f202;
  s.field_1fc = upper_state_.field_43f1fc;
  s.field_1da = material_state_.field_43f1da;
  s.service10_field10 = static_cast<std::int16_t>(extra_balls_);
  s.table_mode = capture_state_.table_mode;
  mean_lamp_mode_reset(s, lamp_commands_);
  for (unsigned i = 0; i < 6; ++i)
    std::copy_n(lamp_commands_[13 + i].begin(), 4,
                mode5_state_.field_43f23c.begin() + i * 4);
  mode5_state_.field_43f260 = lamp_commands_[22];
}
bool MeanSimulation::step_mode4_spawn() {
  if ((capture_state_.table_mode != 6 &&
       (capture_state_.table_mode != 5 || mode5_state_.field_43f1e6 != 4)) ||
      mode5_state_.field_43f37e != 2)
    return true;
#ifndef SLAM_MEAN_BALL_PAIR_LIFT
  status_ = "Generate original ball-pair response before multiball";
  return false;
#else
  if (mean_mode4_spawn(pool_, capture_state_, mode5_state_,
                       multiball_release_.slot, dat_base_)) {
    ++multiball_spawns_;
    ++captures_; // Newly allocated balls enter the verified held callback5.
    max_balls_ = std::max(max_balls_, pool_.count);
    status_ = "Mean original multiball spawn";
  }
  return true;
#endif
}
#ifdef SLAM_MEAN_BALL_PAIR_LIFT
void ball_pair_408bfc(MeanMinigameLift &);
#endif
void MeanSimulation::collide_pair(unsigned i, unsigned j) {
#ifdef SLAM_MEAN_BALL_PAIR_LIFT
  std::optional<MeanPairTrace> trace;
  if(pair_observer_){
    trace.emplace();
    trace->before={pool_.objects[i],pool_.objects[j]};
    trace->first=i;trace->second=j;trace->count=pool_.count;
    trace->mode=capture_state_.table_mode;
    trace->globals={ball_pair_.rd(0x43e728,4),ball_pair_.rd(0x43e764,4),ball_pair_.rd(0x43e75c,4)};
  }
  for (unsigned k = 0; k < 2; ++k) {
    const auto &b = pool_.objects[k ? j : i];
    std::copy(b.bytes.begin(), b.bytes.end(),
              ball_pair_.runtime.begin() + k * 128);
  }
  ball_pair_.r[0] = 0;
  ball_pair_.r[2] = 1;
  ball_pair_.r[4] = 0x200f000;
  ball_pair_.push(0x200fff0);
  ball_pair_408bfc(ball_pair_);
  for (unsigned k = 0; k < 2; ++k)
    std::copy_n(ball_pair_.runtime.begin() + k * 128, 100,
                pool_.objects[k ? j : i].bytes.begin());
  if(trace){trace->after={pool_.objects[i],pool_.objects[j]};pair_observer_(*trace);}
#else
  (void)i;
  (void)j;
#endif
}
bool MeanSimulation::switch_step() {
  configure_bits();
  const int x = ball_.i32(0) >> 16, y = ball_.i32(4) >> 16;
  if (bits_.sample_linear(x, y))
    return true;
  const auto mask = bits_.extra_plane_mask_linear(x, y), previous = ball_.u16(0x38);
  ball_.put16(0x3a, previous);
  ball_.put16(0x38, mask);
  if (mask == previous)
    return true;
  ++events_;
  const auto layer = ball_.u16(0x48);
  if (capture_state_.table_mode == 4) {
    apply_mode4_switch(layer, mask, ball_.i32(0), ball_.i32(4));
  }
  const auto mode4_post = [&] {
    if (layer == 2 && mask == 1 && capture_state_.table_mode == 4) {
      const auto branch = y < 60                             ? 0x41bf0cu
                          : y < 150 && x >= 234              ? 0x41c0dfu
                          : y >= 150 && x >= 212 && x <= 296 ? 0x41c39eu
                                                             : 0u;
      if (branch) {
        sync_ball_reset_fields(false);
        ball_reset_state_.table_mode = 4;
        auto probe=ball_reset_state_;
        const auto request=mean_mode4_event(probe,branch,0);
        const bool admitted=request.callback && request_material5_display(request.callback,request.score_add,true);
        const auto e=mean_mode4_event(ball_reset_state_,branch,admitted ? 1u : 0u);
        load_mode4_fields();
        if (e.score_add) {
          score_.add(e.score_add);
          ++score_events_;
        }
        if (e.callback) apply_capture_delay(admitted,{1,1,1,1,1},0);
        if (e.exit_to_mode2) {
          const auto display=material5_display_;
          finish_mode4(true);
          material5_display_=display;
        }
      }
    }
  };
  std::uint32_t bundle_points = 0;
  if (layer == 0 && mask == 1 && ball_.i32(0) > 230 * 65536 &&
      ball_.i32(4) >= 225 * 65536) {
    const auto before = ball_.u16(0x5c);
    mean_right_marker20_b(ball_, ball_reset_state_, dat_base_ + 0xcbb96 - 14);
    if (before != 20 && ball_.u16(0x5c) == 20)
      ++right_markers_;
    return true;
  }
  if (layer == 0 && mask == 4 && y >= 120 && y < 340) {
    if (mean_right_marker20_a(ball_, ball_reset_state_,
                              dat_base_ + 0xcbb96 - 14)) {
      ++right_markers_;
      return true;
    }
  }
  if (layer == 0 && mask == 1 && mean_baseline_one_bundle(ball_, dat_base_)) {
    return true;
  }
  if (layer == 0 && mask == 3 && ball_.i32(0) <= 60 * 65536 &&
      ball_.i32(4) < 170 * 65536) {
    if (mean_upper_entry(ball_, upper_state_, field_43d864_, false)) {
      ++captures_;
      ++upper_captures_;
      status_ = "original upper capture";
    }
    return true;
  }
  if (layer == 0 && mask == 3 && ball_.i32(0) <= 60 * 65536 &&
      ball_.i32(4) >= 170 * 65536) {
    MeanLeftCaptureState entry;
    entry.field_438b68 = capture_state_.field_438b68[0];
    entry.field_438b6c = capture_state_.field_438b68[1];
    entry.field_43f380 = std::uint16_t(capture_state_.field_43f380);
    bool captured = false;
    if (!mean_left_capture(ball_, entry, field_43d864_, false, captured))
      return false;
    capture_state_.field_438b68[0] = entry.field_438b68;
    capture_state_.field_438b68[1] = entry.field_438b6c;
    capture_state_.field_43f380 = std::int16_t(entry.field_43f380);
    if (captured) {
      ++captures_;
      status_ = "original capture callback2";
    }
    return true;
  }
  // Actual41da51 has no mode filter: a surviving marker20 can enter in mode5.
  if (layer == 0 && mask == 3 && ball_.i32(0) >= 260 * 65536 &&
      ball_.u16(0x5c) == 20) {
    sync_ball_reset_fields(false);
    ball_reset_state_.table_mode = capture_state_.table_mode;
    MeanMode4RightEvent e;
    if (!field_43d864_ && mean_mode4_right_capture_entry(ball_, ball_reset_state_, mode4_right_,
                                       pool_, e)) {
      ++captures_;
      ++right_captures_;
      // Original41dad9..41dae6 closes the gate immediately on entry.
      right_gate_.field_438b2c=0; right_gate_.field_438b34=-1;
      ball_reset_state_.fields[0x3b8]=ball_reset_state_.fields[0x3b9]=0;
      audio_requests_.push_back({0x5c, 6, 5, 0x437dc8});
    }
    return true;
  }
  if (layer == 0 && mask == 3 && mean_baseline_three_noop(ball_)) {
    return true;
  }
  if (mean_ramp_bundle(ball_, mask, dat_base_)) {
    if (layer == 3 && mask == 1 && y >= 140 && y < 160 &&
        ball_.i32(0) < 160 * 65536) {
      bonus_turn_.field_player_08 += 500000; // Original41b2e8 player+8.
      apply_pit_stop(0); // Original41b2f1.
      apply_shared_reward(1); // Original41b300.
      apply_left_progress(); // Original41b305..41b491, after shared reward.
    }
    if (layer == 1 && mask == 1 && ball_.i32(0) >= 230 * 65536 &&
        ball_.i32(4) >= 160 * 65536 && ball_.i32(4) < 240 * 65536) {
      bonus_turn_.field_player_08 += 500000;
      apply_pit_stop(3); // Original41c7c6.
      apply_shared_reward(5); // Original41c7d0.
    }
    return true;
  }
  std::array<std::array<std::uint8_t, 4>, 3> target_commands;
  std::copy_n(lamp_commands_.begin() + 30, 3, target_commands.begin());
  const auto target_event = mean_top_target_lamps(
      lamp_events_, target_commands, ball_.i32(0), ball_.i32(4), layer, mask);
  if (target_event.handled) {
    std::copy(target_commands.begin(), target_commands.end(),
              lamp_commands_.begin() + 30);
    ++top_target_hits_;
    if (target_event.request_41d153) {
      ++top_target_cycles_;
      target_reward_.field_43f1fa = capture_state_.field_43f1fa;
      target_reward_.command_43f2f4 = lamp_commands_[59];
      const auto old_gear=target_reward_.field_player_12;
      const auto reward = mean_top_target_reward(target_reward_);
      if(target_reward_.field_player_12!=old_gear){
        const auto gear=unsigned(target_reward_.field_player_12);
        if(gear<gear_stats_.upshifts.size())++gear_stats_.upshifts[gear];
        if(gear==5)++gear_stats_.fifth_enables;
      }
      if(reward.score_points==10000000)++gear_stats_.capped_awards;
      if (!reward.handled) {
        status_ = "unsupported top-target reward index";
        return false;
      }
      capture_state_.field_43f1fa = target_reward_.field_43f1fa;
      lamp_commands_[59] = target_reward_.command_43f2f4;
      if(reward.services_pending){
        const auto callback=target_reward_.field_player_12==5?0x41121cu:0x410fccu;
        const bool accepted=request_material5_display(callback,0,true);
        apply_capture_delay(accepted,{1,1,1,1,1},0);
      }
      if (reward.score_points) {
        score_.add(reward.score_points);
        ++score_events_;
      }
    }
  }
  if (mean_switch_bundle(ball_, mask, dat_base_, bundle_points)) {
    if (layer==2 && mask==1 && ball_.i32(4)<60*65536) {
      sync_ball_reset_fields(false);
      const auto event=mean_return_pass_hit(ball_reset_state_);
      project_return_pass_fields();
      ++return_passes_;
      if(event.announcement){
        score_.add(event.score); ++score_events_; ++return_pass_awards_;
        std::array<std::int32_t,5> timers{upper_state_.field_438b5c[2],
            capture_state_.field_438b68[2],capture_state_.field_438b74[2],
            mode4_right_.field_438b80[2],multiball_release_.slot[2]};
        mean_return_pass_dispatch(ball_reset_state_,material5_display_,event,timers);
        upper_state_.field_438b5c[2]=timers[0];capture_state_.field_438b68[2]=timers[1];
        capture_state_.field_438b74[2]=timers[2];mode4_right_.field_438b80[2]=timers[3];
        multiball_release_.slot[2]=timers[4];
      }
    }
    if (layer == 2 && mask == 1 && ball_.i32(0) >= 234 * 65536 &&
        y >= 60 && y < 150) {
      bonus_turn_.field_player_08 += 500000;
      apply_pit_stop(2); // Original41c0c1.
      apply_shared_reward(3); // Original41c0cb, before mode4 post-processing.
    }
    if (bundle_points) {
      score_.add(bundle_points);
      ++score_events_;
    }
    mode4_post();
    return true;
  }
  if (layer == 0 && mask == 0) {
    mean_set_layer(ball_, 0, dat_base_);
    const auto field = ball_.u16(0x5c);
    if (field != 20) {
      ball_.put16(0x22, 0);
      ball_.put16(0x2a, 0);
      ball_.put16(0x28, 40);
      if (field != 1 && field != 6) {
        ball_.put16(0x5c, 0);
        ball_.put16(0x1c, 0);
        ball_.put32(0x60, 0xaa1);
      }
    }
  } else if (layer == 0 && mask == 1 &&
             (ball_.i32(0) <= 230 * 65536 || y < 225)) {
    if (ball_.i32(0) > 230 * 65536 && ball_.i32(4) < 225 * 65536 &&
        ball_.u16(0x5c) == 0) {
      // Original41de3d, before original ball-state mutation.
      ball_reset_state_.fields[0x3b6] = 100;
      ball_reset_state_.fields[0x3b7] = 0;
    }
    if (x < 140 || ball_.i32(0) > 230 * 65536) {
      ball_.put16(0x22, 0);
      ball_.put16(0x2a, x < 140 ? 0xf8e : 0);
      ball_.put16(0x5c, x < 140 ? 7 : 5);
      ball_.put16(0x1c, 10);
      ball_.put16(0x28, x < 140 ? 120 : 150);
      ball_.put32(0x60, x < 140 ? 0x181 : 0x61);
    }
  } else if (layer == 0 && mask == 2 && ball_.i32(4) > 250 * 65536 &&
             x >= 160) {
    if (static_cast<std::int16_t>(ball_.u16(0x58)) < 2)
      ball_.put16(0x58, 1);
    mean_set_layer(ball_, 1, dat_base_);
    ball_.put16(0x5c, 2);
    ball_.put16(0x1c, 0);
    ball_.put32(0x60, 14);
  } else if (layer == 0 && mask == 2) {
    if (ball_.i32(4) > 250 * 65536)
      mean_set_layer(ball_, 3, dat_base_);
    else if (x < 80) {
      mean_set_layer(ball_, 3, dat_base_);
      ball_.put16(0x22, 0);
      ball_.put16(0x2a, 0);
      ball_.put16(0x5c, 8);
      ball_.put16(0x1c, 40);
      ball_.put32(0x60, 0x180);
      ball_.put16(0x28, 40);
    } else if (x < 140) {
      mean_set_layer(ball_, 2, dat_base_);
      ball_.put16(0x22, 0);
      ball_.put16(0x2a, 0);
      ball_.put16(0x5c, 9);
      ball_.put16(0x1c, 10);
      ball_.put32(0x60, 0x601);
      ball_.put16(0x28, 100);
    } else {
      mean_set_layer(ball_, 1, dat_base_);
      if (x >= 240) {
        ball_.put16(0x5c, 12);
        ball_.put16(0x1c, 20);
        ball_.put32(0x60, 0x3800);
      }
    }
  } else if (layer == 1 && mask == 1 && (y >= 390 || y < 60)) {
    mean_set_layer(ball_, 0, dat_base_);
    if (y < 60) {
      sync_ball_reset_fields(false);
      // Original41c607 service1c==0 path; DMD scheduler return is a bounded
      // presentation adapter, not a reconstructed queue pointer.
      auto preview = ball_reset_state_;
      auto gate = right_gate_;
      const auto request = field_43d864_ ? MeanRightCancelEvent{} : mean_right_cancel(preview, gate, 0);
      const bool accepted = request.cancelled && request_material5_display(request.callback, 0, true);
      const auto e = field_43d864_ ? MeanRightCancelEvent{} : mean_right_cancel(ball_reset_state_, right_gate_, accepted ? 1u : 0u);
      if (e.cancelled) {
        ++stock_stats_.starts;
        apply_capture_delay(accepted, {1,1,1,1,1}, 0);
        load_mode4_fields();
        const auto &f = ball_reset_state_.fields;
        capture_state_.field_43f364 = std::int16_t(f[0x364] | (f[0x365] << 8));
        lamp_mode_input_.field_38a = std::int16_t(f[0x38a] | (f[0x38b] << 8));
        ++right_cancellations_;
      }
    }
    if (y >= 390) {
      ball_.put16(0x22, 0);
      ball_.put16(0x2a, 0);
      ball_.put16(0x5c, 0);
      ball_.put16(0x1c, 0);
      ball_.put16(0x28, 40);
      if (x >= 150)
        ball_.put32(0x60, 0xaa1);
    }
  } else if (layer == 1 && mask == 1 && y >= 280 && y < 310 && x >= 230) {
    mean_set_layer(ball_, 2, dat_base_);
    ball_.put16(0x5c, 3);
    ball_.put16(0x1c, 0);
    ball_.put32(0x60, 0x1c);
  } else if (layer == 1 && mask == 1 && y >= 60 && y < 160) {
    mean_set_layer(ball_, 0, dat_base_);
  } else if (layer == 1 && mask == 1 && y >= 160 && y < 390 && x < 230) {
    mean_set_layer(ball_, 0, dat_base_);
  } else if (layer == 1 && mask == 1 && y >= 310 && y < 390) {
    // Original41c85d falls through to return.
  } else if (layer == 2 && mask == 1 && y >= 150 &&
             ball_.i32(0) > 296 * 65536) {
    mean_set_layer(ball_, y >= 250 ? 1 : 3, dat_base_);
    ball_.put16(0x5c, y >= 250 ? 2 : 4);
    ball_.put16(0x1c, y >= 250 ? 0 : 20);
    ball_.put32(0x60, y >= 250 ? 14 : 0x18);
    if (y < 250) {
      ball_.put16(0x22, 0);
      ball_.put16(0x2a, 0);
      ball_.put16(0x28, 100);
    }
  } else if (layer == 2 && mask == 1 && y >= 150 &&
             ball_.i32(0) >= 212 * 65536 && ball_.i32(0) <= 296 * 65536) {
    // 41c34c..41c38f: upper return ramp.
    mean_set_layer(ball_, 3, dat_base_);
    ball_.put16(0x5c, 8);
    ball_.put16(0x1c, 40);
    ball_.put32(0x60, 0x180);
  } else if (layer == 2 && mask == 1 && y >= 60 && y < 150 && x < 160) {
    // 41bfb6..41bff9: exit into upper ramp layer.
    mean_set_layer(ball_, 3, dat_base_);
    ball_.put16(0x5c, 10);
    ball_.put16(0x1c, 50);
    ball_.put32(0x60, 0x600);
  } else if (layer == 3 && mask == 1 && y < 64) {
    // 41ae95..41aefb: upper transfer; ordinary acceleration resumes next step.
    mean_set_layer(ball_, 2, dat_base_);
    ball_.put16(0x22, 0);
    ball_.put16(0x2a, 0);
    ball_.put16(0x5c, 14);
    ball_.put16(0x1c, 40);
    ball_.put32(0x60, 0xc000);
    ball_.put32(0x14, 0);
    ball_.put32(0x18, 0);
    ball_.put16(0x28, 40);
    bonus_turn_.field_player_08 += 500000;
    apply_pit_stop(1); // Original41af1d.
    apply_shared_reward(2); // Original41af27, before the mode4 entry test.
    sync_ball_reset_fields(false);
    ball_reset_state_.table_mode = capture_state_.table_mode;
    const auto entry =
        mean_mode4_right_ramp(ball_reset_state_, layer, mask, y * 65536);
    load_mode4_fields();
    if (entry.callback) {
      ++mode4_starts_;
      update_right_gate(); // Original41b0c6 before service34.
      apply_capture_delay(request_material5_display(entry.callback,0,true),{1,1,1,1,1},0);
      status_ = "original mode4 right ramp";
    }
  } else if (layer == 3 && mask == 1 && y >= 64 && y < 90) {
    // 41b10d..41b17a: original directed force toward (227,101).
    mean_set_layer(ball_, 2, dat_base_);
    ball_.put16(0x22, 1);
    ball_.put16(0x24, 227);
    ball_.put16(0x26, 101);
    ball_.put16(0x5c, 16);
    ball_.put16(0x1c, 60);
    ball_.put32(0x60, 0x38000);
    ball_.put16(0x28, 120);
  } else if (layer == 3 && mask == 1 && y >= 90 && y < 116) {
    mean_restart_gate_exit(field_43e79c_); // 41b1f8, independent of mode.
    MeanTurnEntry entry;
    entry.mode = capture_state_.table_mode;
    entry.field_43f3ae = mode5_state_.field_43f3ae;
    entry.command_43f258 = lamp_commands_[20];
    entry.command_43f260 = mode5_state_.field_43f260;
    if (mean_turn_playfield_entry(entry)) {
      capture_state_.table_mode = upper_state_.table_mode = entry.mode;
      mode5_state_.field_43f3ae = entry.field_43f3ae;
      ball_reset_state_.fields[0x35a] = entry.field_43f35a;
      ball_reset_state_.fields[0x35b] =
          static_cast<std::uint16_t>(entry.field_43f35a) >> 8;
      lamp_commands_[20] = entry.command_43f258;
      mode5_state_.field_43f260 = entry.command_43f260;
    }
    mean_set_layer(ball_, 0, dat_base_);
    ball_.put16(0x22, 0);
    ball_.put16(0x2a, 0);
    ball_.put16(0x5c, 5);
    ball_.put16(0x1c, 10);
    ball_.put32(0x60, 0x61);
    ball_.put16(0x28, 150);
    ball_.put16(0x58, 2);
  } else if (layer == 3 && mask == 1 && y >= 270) {
    mean_set_layer(ball_, x < 160 ? 0 : 1, dat_base_);
    if (x >= 160) {
      ball_.put16(0x5c, 13);
      ball_.put16(0x1c, 20);
      ball_.put32(0x60, 0x3000);
    }
  } else if (layer == 0 && mask == 4 && y >= 80 && y < 120) {
    // 41cadb..41cae7: minimal ball-state side of this table event.
    bonus_turn_.field_player_08 += 500000; // Original41cad4, deferredbonus.
    auto &f = ball_reset_state_.fields;
    const auto word = [&](unsigned o) {
      return static_cast<std::int16_t>(f[o] | (f[o + 1] << 8));
    };
    if (word(0x3b6) >= 0) {
      f[0x3b6] = f[0x3b7] = 0xff;
      if (word(0x35a) >= 0) {
        f[0x35a] = f[0x35b] = 0xff;
        sync_ball_reset_fields(false);
        const auto reward = mean_switch_reward(ball_reset_state_);
        sync_ball_reset_fields(true);
        ++switch_rewards_;
        const auto variant = (f[0x358] | (f[0x359] << 8))
                                 ? 1u + (f[0x362] | (f[0x363] << 8))
                                 : 0u;
        if (variant < switch_reward_variants_.size())
          ++switch_reward_variants_[variant];
        // Original41d412/41d429 admission precedes reward audio/score effects.
        const bool admitted=request_material5_display(0x40fdec,reward.score);
        apply_capture_delay(admitted,{1,1,1,1,1},0);
        if (reward.score) {
          score_.add(reward.score);
          ++score_events_;
        }
        if (reward.service84) {
          audio_requests_.push_back({0x84, 0, 62});
          ++award_bank_starts_;
        }
        material5_display_.field_358 = f[0x358] | (f[0x359] << 8);
        material5_display_.field_362 = f[0x362] | (f[0x363] << 8);
        material5_display_.field_1fe = f[0x1fe] | (f[0x1ff] << 8);
        material5_display_.field_1f2 = f[0x1f2] | (f[0x1f3] << 8);
        lamp_commands_[20][0] = 2;
      }
      sync_ball_reset_fields(false);
      ball_reset_state_.table_mode = capture_state_.table_mode;
      const auto before_armed = lamp_mode_input_.field_3a2;
      const bool skull_repeat=lamp_mode_input_.field_3b0>=0;
      const auto progress = mean_right_progress(ball_reset_state_,
          [&](MeanBallResetState &state) {
            if(skull_repeat){
              std::uint32_t points=0;for(unsigned i=0;i<4;++i)points|=std::uint32_t(state.fields[0x050+i])<<(i*8);
              const bool admitted=request_material5_display(0x411544,points,true);
              apply_capture_delay(admitted,{1,1,1,1,1},0);
            }
            apply_shared_reward(4, true);
          });
      load_mode4_fields();
      if (progress.score) {
        score_.add(progress.score);
        ++score_events_;
      }
      if (!before_armed && lamp_mode_input_.field_3a2)
        ++right_arms_;
      if (progress.reset_right_gate)
        update_right_gate();
      if(progress.callback==0x412df0) {
        // Original41cd0e right request5/4; the left ramp uses6/5.
        material5_display_.scheduler.field_7a0=capture_state_.table_mode;
        const MeanDisplayRequest request{5,4,2,0,11,1,0x412df0};
        const auto old780=material5_display_.scheduler.field_780;
        const bool admitted=material5_display_.request(request,0,true);
        queue_display_audio(audio_requests_,old780,request,admitted);
        apply_capture_delay(admitted,{1,1,1,1,1},0);
      }
      // Original combo request precedes shared reward and lap progression.
    }
    ball_.put16(0x5c, 6);
    ball_.put16(0x1c, 20);
    ball_.put32(0x60, 0x60);
  } else if (layer == 0 && mask == 4 && mean_lower_switch(ball_)) {
    score_.add(mean_lower_switch_points(ball_));
    ++score_events_;
    if (mean_side_extra_ball(ball_.i32(0), upper_state_.field_43f1fc,
                             extra_balls_, lamp_commands_)) {
      ++side_extra_balls_;
      status_ = "original side-target extra ball";
      request_material5_display(0x410e4c, 0);
    }
    if (mean_award_bank_target(
            ball_.i32(0), capture_state_.table_mode, lamp_mode_input_.field_1ec,
            lamp_mode_input_.field_37a, award_bank_054_, lamp_commands_)) {
      ++award_bank_starts_;
      const bool admitted=request_material5_display(0x4107c8,0);
      apply_capture_delay(admitted,{1,1,1,1,1},0);
      if (capture_state_.table_mode <= 3)
        audio_requests_.push_back({0x84, 0, 62});
    }

  } else if (layer == 0 && mask > 4) {
    // 41c93d: values above4 return without a table callback.
  } else if (mask != 0) {
    status_ = layer == 0 && mask == 3 && ball_.i32(0) <= 60 * 65536 &&
                      ball_.i32(4) < 170 * 65536
                  ? "upper capture rules pending; R resets"
                  : "unsupported Mean switch callback; R resets";
    return false;
  }
  mode4_post();
  return true;
}
bool MeanSimulation::physics_step() {
  mean_multiball_guide(ball_);
  const auto restart = mean_restart_gate(field_43e79c_, ball_.u16(0x58));
  if (restart == MeanRestartDecision::Wait) {
    ++restart_waits_;
    return true;
  }
  if (restart == MeanRestartDecision::Initialize) {
    ++restart_initializations_;
    mean_initialize_ball(ball_, dat_base_); // Original408943 continues integration this tick.
    configure_bits();
  }

  if (ball_.u16(0x58) == 5) {
    ball_drained_ = true;
    if (pool_.count == 1 && continuous_play_) {
      begin_bonus();
      ball_drained_ = false;
    }
    return true;
  }
  if (capture_state_.table_mode == 6 &&
      (ball_.u16(0x58) == 6 ||
       (ball_.u16(0x58) == 3 && ball_.u16(0x5a) == 1 &&
        upper_state_.field_43f36a == -1 && capture_state_.field_43f364 == 0))) {
    MeanMode6CaptureEvent event;
    upper_state_.field_43f364 = capture_state_.field_43f364;
    if (!mean_mode6_capture_tick(ball_, mode5_state_, upper_state_, pool_.count,
                                 event)) {
      status_ = "Unsupported Mean mode6 capture";
      return false;
    }
    if (event.transfer && capture_state_.field_438b74[0] < 0) {
      mean_upper_transfer(ball_, dat_base_);
      capture_state_.field_438b50 = {0, 0, 5};
      capture_state_.field_438b74[1] = 100;
    }
    if (event.lamp_reset) update_right_gate();
    if (ball_.u16(0x58) == 6 || ball_.u16(0x58) == 3) {
      ball_.put32(8, ball_.i32(0));
      ball_.put32(12, ball_.i32(4));
      ball_.put32(0x14, 0);
      ball_.put32(0x18, 0);
      return true;
    }
  }
  if (capture_state_.table_mode == 6 && ball_.u16(0x58) == 3 &&
      (ball_.u16(0x5a) == 2 || ball_.u16(0x5a) == 4)) {
    auto &side = mode6_side_;
    side.field_43f380 = capture_state_.field_43f380;
    side.field_43f364 = capture_state_.field_43f364;
    side.field_438b68 = capture_state_.field_438b68;
    side.field_43f38e = mode5_state_.field_43f38e;
    side.field_43f368 = mode5_state_.field_43f368;
    side.field_43f36c = mode5_state_.field_43f36c;
    side.active_count = pool_.count;
    side.field_43f370=static_cast<std::int16_t>(ball_reset_state_.fields[0x370] | (unsigned(ball_reset_state_.fields[0x371])<<8));
    side.field_438b80=mode4_right_.field_438b80;
    side.field_438b38=mode4_right_.field_438b38;
    side.field_438b40=mode4_right_.field_438b40;
    side.field_438b74=capture_state_.field_438b74;
    side.field_438b50=capture_state_.field_438b50;
    side.callback3_occupied=false;
    for(unsigned i=0;i<pool_.count;++i)
      if(i!=current_ball_ && (pool_.objects[i].u16(0x58)==3 || pool_.objects[i].u16(0x58)==6) && pool_.objects[i].u16(0x5a)==3)
        side.callback3_occupied=true;
    MeanMode6SideEvent event;
    if (!mean_mode6_side_tick(ball_, side, event,field_43d864_,dat_base_))
      return false;
    for(unsigned i=0;i<event.services_1c_samples;++i) audio_requests_.push_back({0x5c,6,5,0x437dec});
    capture_state_.field_438b74=side.field_438b74;
    capture_state_.field_438b50=side.field_438b50;
    mode4_right_.field_438b80=side.field_438b80;
    mode4_right_.field_438b38=side.field_438b38;
    mode4_right_.field_438b40=side.field_438b40;
    ball_reset_state_.fields[0x370]=std::uint16_t(side.field_43f370)&255;
    ball_reset_state_.fields[0x371]=std::uint16_t(side.field_43f370)>>8;
    capture_state_.field_43f380 = side.field_43f380;
    capture_state_.field_43f364 = side.field_43f364;
    capture_state_.field_438b68 = side.field_438b68;
    mode5_state_.field_43f38e = side.field_43f38e;
    mode5_state_.field_43f368 = side.field_43f368;
    mode5_state_.field_43f36c = side.field_43f36c;
    if (event.lamp_reset_requested) update_right_gate();
    bonus_turn_.field_player_08 += event.field_player_08_add;
    if (event.score_request) {
      score_.add(event.score_request);
      ++score_events_;
    }
    if (event.transfer_requested && capture_state_.field_438b74[0] < 0) {
      mean_upper_transfer(ball_, dat_base_);
      capture_state_.field_438b50 = {0, 0, 5};
      capture_state_.field_438b74[1] = 100;
    }
    if(ball_.u16(0x58)==3 || ball_.u16(0x58)==6) {
      ball_.put32(8, ball_.i32(0));
      ball_.put32(12, ball_.i32(4));
      ball_.put32(0x14, 0);
      ball_.put32(0x18, 0);
      return true;
    }
    ++releases_;
  }
  if (ball_.u16(0x58) == 7) {
    if (ball_.u16(0x34) != 0) {
      status_ = "unsupported original state7 directory index";
      return false;
    }
    if (mean_state7_boundary(ball_, dat_base_)) {
      capture_state_.field_438b50 = {0, 0, 15};
      multiball_release_.slot[1] = 100;
      // Original4088f0 state3 wrapper holds; do not run table callback twice.
      return true;
    } else {
      MeanState7Record record;
      for (unsigned i = 0; i < 6; ++i)
        record.words[i] =
            static_cast<std::int16_t>(flippers_.rd(0x438a48 + i * 2, 2));
      ++state7_steps_;
      return mean_state7_step(ball_, record, lookup_);
    }
  }
  if (ball_.u16(0x58) == 3) {
    std::uint32_t points = 0;
    if (ball_.u16(0x5a) == 1) {
      const auto prior_delays=capture_delays();
      const auto prior_mode=capture_state_.table_mode;
      bool delay_admitted=false;
      MeanUpperCaptureEvent event;
      upper_state_.field_43f37e = mode5_state_.field_43f37e;
      upper_state_.field_43f364 = capture_state_.field_43f364;
      upper_state_.table_mode = capture_state_.table_mode;
      upper_state_.field_43f200 = capture_state_.field_43f200;
      upper_state_.field_43f202 = capture_state_.field_43f202;
      upper_state_.field_43f1fa = capture_state_.field_43f1fa;
      if (!(field_43d864_ ? mean_upper_capture_tilt_tick(ball_,upper_state_,event,dat_base_,random_state_.field_43e7ac) : mean_upper_capture_tick(ball_, upper_state_, event))) {
        status_ = "unsupported upper capture rule phase";
        return false;
      }
      capture_state_.table_mode=upper_state_.table_mode;
      for(unsigned i=0;i<event.early_release_count;++i)audio_requests_.push_back({0x5c,6,5,0x437dec});
      if (event.rule_service_request && upper_state_.table_mode < 4) {
        // Original415727: first ordinary upper capture announcement.
        delay_admitted=request_material5_display(0x411fdc, 0, true);
        lamp_commands_[29] = {4, 6, 1, 0}; // 43f27c..43f27f.
      }
      if (event.rule_service_request && upper_state_.table_mode == 5) {
        // Original4158b5/415985/415b39/415c9a service34 requests.
        constexpr std::uint32_t callbacks[] = {0x412d24, 0x411f10, 0x412af8, 0, 0x412c58};
        const auto selected = upper_state_.field_43f1e6;
        if (selected >= 0 && selected < 5 && callbacks[selected]) {
          delay_admitted=request_material5_display(callbacks[selected], 0, true);
        }
      }
      bonus_turn_.field_player_08 += event.field_player_08_add;
      if (event.mode6_start_requested) {
        mean_mode6_begin(mode5_state_);
        multiball_release_.field_43f382 = -1;
        delay_admitted=request_material5_display(0x410b00, 0);
        mode6_display_pending_ = true;
        ++mode6_starts_;
        audio_requests_.push_back({0x84, 0, 29}); // Actual415710.
      }
      if(event.capture_delay_request) {
        upper_state_.field_438b5c[2]=prior_delays[0];capture_state_.field_438b68[2]=prior_delays[1];
        capture_state_.field_438b74[2]=prior_delays[2];mode4_right_.field_438b80[2]=prior_delays[3];multiball_release_.slot[2]=prior_delays[4];
        apply_capture_delay(delay_admitted,event.capture_delay_selectors,event.capture_delay);
        if(event.field_024_minus_one_after_delay)for(unsigned i=0;i<4;++i)ball_reset_state_.fields[0x024+i]=255;
      }
      if (event.selected3_start_requested && !start_minigame())
        return false;
      if(event.reward_request==3 && event.field_player_10_add)gear_stats_.upper_extras+=event.field_player_10_add;
      if (event.reward_request != 0) {
        if (event.reward_request > 3) {
          status_ = "unsupported Mean reward display callback";
          return false;
        }
        constexpr std::uint32_t reward_callbacks[] = {0, 0x410a34, 0x410910, 0x410d34};
        request_material5_display(reward_callbacks[event.reward_request], 0);
        reward_display_pending_ = true;
        ++reward_requests_;
        status_ = "original reward display: ball held";
      }
      capture_state_.field_43f364 = upper_state_.field_43f364;
      capture_state_.field_43f200 = upper_state_.field_43f200;
      capture_state_.field_43f202 = upper_state_.field_43f202;
      capture_state_.field_43f1fa = upper_state_.field_43f1fa;
      extra_balls_ =
          static_cast<std::uint16_t>(extra_balls_ + event.field_player_10_add);
      if (prior_mode != upper_state_.table_mode &&
          upper_state_.table_mode == 5) {
        if (!mean_mode5_begin(mode5_state_, random_state_.field_43e7a8)) {
          status_ = "unsupported Mean mode initialization";
          return false;
        }
        if(mode5_state_.field_43f1e6==1)++monster_stats_.starts;
        if(mode5_state_.field_43f1e6==2)++rally_stats_.starts;
        if(mode5_state_.field_43f1e6==4)++offroad_stats_.starts;
        if(mode5_state_.field_43f1e6==0)++chicken_stats_.starts;
        // Actual415969/415ac6/415b83/415dba, after the mode announcement.
        constexpr int orders[] = {51, 46, 40, 0, 2};
        audio_requests_.push_back({0x84, 0, orders[mode5_state_.field_43f1e6]});
      }
      capture_state_.table_mode = upper_state_.table_mode;
      points = event.score_request;
      if (event.release_requested)
        mean_upper_release(ball_, dat_base_, random_state_.field_43e7ac);
      if (event.mode4_transfer_requested) {
        const auto previous_stage = mode5_state_.field_43f37e;
        mean_mode4_transfer(ball_, capture_state_, mode5_state_, dat_base_);
        if (capture_state_.table_mode == 6 && previous_stage == 1)
          mode5_state_.field_43f3ae = 1000;
        multiball_release_.slot[1] = mode5_state_.field_438b90;
      } else if (event.transfer_requested &&
                 capture_state_.field_438b74[0] < 0) {
        mean_upper_transfer(ball_, dat_base_);
        capture_state_.field_438b50 = {0, 0, 5};
        capture_state_.field_438b74[1] = 100;
      }
    } else if (ball_.u16(0x5a) == 4 && capture_state_.table_mode <= 5) {
      sync_ball_reset_fields(false);
      ball_reset_state_.table_mode = capture_state_.table_mode;
      MeanMode4RightEvent e;
      if (!mean_mode4_right_capture(ball_, ball_reset_state_, mode4_right_,
                                    capture_state_, pool_, dat_base_, e,field_43d864_))
        return false;
      load_mode4_fields();
      bonus_turn_.field_player_08 += e.field_player_08_add;
      points = e.score;
      if (e.start_shared44) {
        ++mode4_starts_;
        if (!start_minigame2())
          return false;
      }
    } else if (ball_.u16(0x5a) == 5) {
      multiball_release_.mode = capture_state_.table_mode;
      multiball_release_.selected = mode5_state_.field_43f1e6;
      multiball_release_.slot50 = capture_state_.field_438b50;
      unsigned samples=0;
      mean_multiball_release(ball_, multiball_release_, dat_base_,field_43d864_,&samples);
      if(field_43d864_)for(unsigned i=0;i<samples;++i)audio_requests_.push_back({0x5c,6,5,0x437dec});
      capture_state_.field_438b50 = multiball_release_.slot50;
    } else {
      MeanCaptureTickEvent event;
      const auto previous_mode = capture_state_.table_mode;
      const auto awards_before = mode5_state_.field_43f3b4;
      const bool chicken_capture=previous_mode==5 && mode5_state_.field_43f1e6==0;
      bool handled;
      if (ball_.u16(0x5a) == 2 && (capture_state_.table_mode == 4 ||
                                   (capture_state_.table_mode <= 3 &&
                                    capture_state_.field_43f392 != 0))) {
        sync_ball_reset_fields(false);
        ball_reset_state_.table_mode = capture_state_.table_mode;
        bool sample = false;
        handled = mean_mode4_capture(ball_, capture_state_, ball_reset_state_,
                                     multiball_release_, pool_, dat_base_,
                                     event, sample,field_43d864_);
        load_mode4_fields();
        if (previous_mode != 4 && capture_state_.table_mode == 4)
          ++mode4_starts_;
        if (sample)
          audio_requests_.push_back({0x5c, 6, 5, 0x437dec});
      } else {
        bool award_accepted=true;
        if(capture_state_.table_mode==5 && ball_.u16(0x5a)==2 && capture_state_.field_43f380==-1 && mode5_state_.field_43f1e6==0) {
          award_accepted=request_material5_display(0x412908,mode5_state_.field_43f05c,true);
          apply_capture_delay(award_accepted,{1,1,1,1,1},0);
        }
        handled =
            capture_state_.table_mode == 5 && ball_.u16(0x5a) == 2
                ? mean_mode5_left(ball_, capture_state_, mode5_state_,
                                  dat_base_, event,field_43d864_,award_accepted)
                : mean_capture_tick(ball_, capture_state_, dat_base_, event,field_43d864_);
      }
      if(handled && previous_mode<=3 && ball_.u16(0x5a)==2 &&
          event.score_request==500000 && event.rule_service_request){
        const bool admitted=request_material5_display(0x4119e0,0,true);
        apply_capture_delay(admitted,{1,1,1,1,1},0);
      }
      if(handled && previous_mode<=3 && ball_.u16(0x5a)==2 &&
          event.score_request==25500000 && event.rule_service_request){
        const bool admitted=request_material5_display(0x413608,0,true);
        apply_capture_delay(admitted,{1,1,1,0,1},740);
        for(unsigned i=0;i<4;++i)ball_reset_state_.fields[0x024+i]=255;
      }
      if(chicken_capture && handled && event.rule_service_request && event.score_request){
        if(chicken_stats_.races<3)chicken_stats_.awards[chicken_stats_.races]=event.score_request;
        ++chicken_stats_.races;chicken_stats_.score+=event.score_request;
        if(capture_state_.table_mode==2){++chicken_stats_.completions;if(event.score_request==75000000)++chicken_stats_.max_finishes;}
      }
      for(unsigned i=0;i<event.services_1c_samples;++i)audio_requests_.push_back({0x5c,6,5,0x437dec});
      if (mode5_state_.field_43f3b4 > awards_before)
        mode5_awards_ += mode5_state_.field_43f3b4 - awards_before;
      if (previous_mode == 5 && capture_state_.table_mode == 2) {
        ++mode_resets_;
        rebuild_lamps();
        // Actual41637a/4163c1: Chicken completion also calls4194e4.
        audio_requests_.push_back({lamp_mode_input_.field_37a >= 0 ? 0x84 : 0x80,
                                  0, lamp_mode_input_.field_37a >= 0 ? 62 : 0});
      }
      if (handled && ball_.u16(0x5a) == 2 &&
          capture_state_.field_43f380 == -2)
        apply_shared_reward(0); // Original416230 timer transition.
      upper_state_.field_43f1e6 = mode5_state_.field_43f1e6;
      upper_state_.table_mode = capture_state_.table_mode;
      if (!handled) {
        status_ = "unsupported captured-ball rule state";
        return false;
      }
      bonus_turn_.field_player_08 += event.field_player_08_add;
      points = event.score_request;
    }
    if (points) {
      score_.add(points);
      ++score_events_;
    }
    if (ball_.u16(0x58) == 3) {
      // Original4089a4..4089c2; held balls skip integration/contacts/switches.
      ball_.put32(8, ball_.i32(0));
      ball_.put32(12, ball_.i32(4));
      ball_.put32(0x14, 0);
      ball_.put32(0x18, 0);
      return true;
    }
    ++releases_;
    status_ = "original capture release";
    if (ball_.u16(0x58) == 7) {
      MeanState7Record record;
      for (unsigned i = 0; i < 6; ++i)
        record.words[i] =
            static_cast<std::int16_t>(flippers_.rd(0x438a48 + i * 2, 2));
      ++state7_steps_;
      return mean_state7_step(ball_, record, lookup_);
    }
  }
  if (ball_.u16(0x58) == 0)
    ball_.put32(0x14, 0x10000);
  if (gameplay_ || point_force_context_) {
    // Original40a010 calls40a0e8 before integration. Existing phase1 clock,
    // input and switch helpers already own this exact438a40 node-type field.
    point_forces_.nodes.front().type = ball_reset_state_.field_438a40;
    const auto vx = ball_.i32(0x14), vy = ball_.i32(0x18);
    if (!mean_point_force(ball_, point_forces_.nodes, point_forces_.lookup, (point_force_suppressed_ || field_43d864_))) {
      status_ = "missing original point-force lookup entry";
      return false;
    }
    if (vx != ball_.i32(0x14) || vy != ball_.i32(0x18)) ++point_force_updates_;
  }
  mean_integrate(ball_);
  // 4089c9: table action callback is dispatched after position integration.
  if (ball_.u16(0x58) == 1 && mean_launch_kick(ball_, launch_pressed_)) {
    ++launches_;
    audio_requests_.push_back({0x5c, 9, 8});
    // Actual41ac6f: lock the chosen Skillshot on a successful launch.
    ball_reset_state_.fields[0x35c] = 0xff;
    ball_reset_state_.fields[0x35d] = 0xff;
  }
  const int y = ball_.i32(4) >> 16;
  if (ball_.u16(0x48) == 0 && y >= 608) {
    if (gameplay_ && continuous_play_) {
      MeanTurnEntry entry;
      entry.field_43f3ae = mode5_state_.field_43f3ae;
      entry.command_43f260 = mode5_state_.field_43f260;
      if (mean_turn_drain_intercept(ball_, entry, pool_.count, field_43d864_)) {
        mode5_state_.field_43f3ae = entry.field_43f3ae;
        mode5_state_.field_43f260 = entry.command_43f260;
        ++ball_saves_;
        status_ = "original ball save: Enter launches";
        return true;
      }
      ++drains_;
      if (pool_.count > 1) {
        // Removal policy is verified separately before enabling this path.
        ball_.put16(0x58, 5);
        ball_drained_ = true;
        return true;
      }
      begin_bonus();
      return true;
    }
    status_ = "BALL_DRAIN: original y>=608 threshold";
    return false;
  }
  return contact_step();
}
bool MeanSimulation::contact_step() {
  if(!contact_observer_)return contact_step_impl(nullptr);
  MeanContactTrace trace;
  trace.before=ball_;
  trace.dat_base=dat_base_;
  trace.ball_index=current_ball_;trace.ball_count=pool_.count;
  trace.mode=capture_state_.table_mode;trace.selected=mode5_state_.field_43f1e6;
  trace.nudge={nudge_.field_43e71c,nudge_.field_43e410,nudge_.field_43e724,nudge_.field_43e564};
  trace.material=material_state_;
  trace.cached_fields=ball_reset_state_.fields;
  trace.fields_ee1c=ball_reset_state_.field_43ee1c;
  for(unsigned y=0;y<30;++y)
    std::copy_n(bits_.dat.begin()+0x959f6+0x49e1+y*40,4,trace.lane_saver_normal.begin()+y*4);
  for(unsigned plane=0;plane<4;++plane)
    for(unsigned y=0;y<32;++y)
      std::copy_n(bits_.dat.begin()+0x9ba36+0x49e1+plane*0x6040+y*40,4,trace.lane_saver_hit.begin()+plane*128+y*4);
#ifdef SLAM_MEAN_FLIPPER_LIFT
  for(unsigned i=0;i<trace.flipper_words.size();++i)trace.flipper_words[i]=flippers_.rd(0x43e850+i*4,4);
  for(unsigned i=0;i<trace.engine_words.size();++i)trace.engine_words[i]=flippers_.rd(0x43e700+i*4,4);
#endif
  trace.ok=contact_step_impl(&trace);
  trace.after=ball_;
  if(!trace.wall)trace.dispatch=ball_;
  contact_observer_(trace);
  return trace.ok;
}
bool MeanSimulation::contact_step_impl(MeanContactTrace *trace) {
  ball_.put16(0x1e, 65535);
  const auto qx=static_cast<std::int32_t>(std::uint32_t(ball_.i32(0))+std::uint32_t(nudge_.field_43e71c))>>16;
  const auto qy=static_cast<std::int32_t>(std::uint32_t(ball_.i32(4))+std::uint32_t(nudge_.field_43e410))>>16;
  const bool bitmap_hit = bits_.sample_linear(qx, qy);
  if (bitmap_hit) {
    ball_.put16(0x3e, ball_.u16(0x3c));
    ball_.put16(0x3c, bits_.extra_plane_mask_linear(qx, qy));
  }
  bool flipper_hit = false;
#ifdef SLAM_MEAN_FLIPPER_LIFT
  std::uint32_t descriptor = 0;
  for (auto address : {0x43e884u, 0x43e86au, 0x43e850u}) {
    flippers_.ball = ball_.bytes;
    flippers_.r[0] = 0x1000000;
    flippers_.r[2] = address;
    flippers_.r[4] = 0x200f000;
    flippers_.push(0x2100000);
    flipper_409050(flippers_);
    ball_.bytes = flippers_.ball;
    if (flippers_.r[0] == 0) {
      flipper_hit = true;
      descriptor = address;
      break;
    }
    if (static_cast<std::int32_t>(flippers_.r[0]) > 0)
      break;
  }
  const auto flipper_response = [&]() {
    const auto angle = ball_.u16(0x1e);
    ball_.put32(0, static_cast<std::uint32_t>(ball_.i32(0)) -
                       word(lookup_.field_43e744, angle * 2));
    ball_.put32(4, static_cast<std::uint32_t>(ball_.i32(4)) -
                       word(lookup_.field_43e764, angle * 2));
    flippers_.ball = ball_.bytes;
    flippers_.r[0] = 0x1000000;
    flippers_.r[2] = descriptor;
    flippers_.r[4] = 0x200f000;
    flippers_.push(0x2100000);
    flipper_4096e8(flippers_);
    ball_.bytes = flippers_.ball;
    ++collisions_;
    return true;
  };
  if (flipper_hit && !bitmap_hit)
    return flipper_response();
#endif
  if (!bitmap_hit)
    return mean_free_velocity(ball_, lookup_);
  // Direct original40e1d0: preserve byte-pointer shifts and fractional/Nudge input.
  int normal=-1;
#ifdef SLAM_MEAN_NORMAL_LIFT
  normal_.ball=ball_.bytes;
  const auto pointer=std::uint32_t(ball_.i32(0x44));
  if(pointer<dat_base_ || pointer-dat_base_>=bits_.dat.size()) {
    status_="invalid original normal DAT pointer";return false;
  }
  normal_.wr(0x1000044,0x1100000+pointer-dat_base_,4);
  normal_.wr(0x43e71c,std::uint32_t(nudge_.field_43e71c),4);
  normal_.wr(0x43e410,std::uint32_t(nudge_.field_43e410),4);
  normal_.r[0]=0x1000000;normal_.r[4]=0x200f000;normal_.push(0);
  flipper_40e1d0(normal_);
  normal=static_cast<std::int32_t>(normal_.r[0]);
#endif
  if(normal < -1 || normal>4095){status_="invalid original normal value";return false;}
  if (normal < 0) {
#ifdef SLAM_MEAN_FLIPPER_LIFT
    if (flipper_hit)
      return flipper_response();
#endif
    return mean_free_velocity(ball_, lookup_);
  }
  if (flipper_hit) {
    const int a = ball_.u16(0x1e);
    ball_.put16(0x1e,
                ((a + normal) / 2 + (std::abs(normal - a) >= 2048 ? 2048 : 0)) &
                    4095);
  } else
    ball_.put16(0x1e, normal);
  MeanContactEvent contact;
  if(trace){trace->wall=true;trace->dispatch=ball_;}
  const auto old_field_1da = material_state_.field_43f1da;
  if (!mean_wall_response(ball_, lookup_, nudge_.field_43e724, nudge_.field_43e564, &contact, &material_state_)) {
    status_ = "unsupported table collision callback/material";
    return false;
  }
  if (old_field_1da != 0 && material_state_.field_43f1da == 0) {
    ++kickback_consumptions_;
    lamp_commands_[24] = material_state_.field_43f268;
  }
  if (contact.material5_rules) {
    MeanMaterial5State state;
    state.field_1dc = lamp_mode_input_.field_1dc;
    for (unsigned i = 0; i < 4; ++i) {
      state.fields_ee1c[i] = static_cast<std::int16_t>(
          ball_reset_state_.field_43ee1c[i * 2] |
          (ball_reset_state_.field_43ee1c[i * 2 + 1] << 8));
      state.commands_26c[i] = lamp_commands_[25 + i];
    }
    state.command_268 = lamp_commands_[24];
    state.command_300 = lamp_commands_[62];
    state.field_1da = material_state_.field_43f1da;
    state.field_37a = lamp_mode_input_.field_37a;
    state.mode = capture_state_.table_mode;
    state.field_054 = award_bank_054_;
    const auto event = mean_material5_rules(ball_.i32(0), ball_.i32(4), state);
    lamp_mode_input_.field_1dc = state.field_1dc;
    lamp_mode_input_.field_37a = state.field_37a;
    material_state_.field_43f1da = state.field_1da;
    for (unsigned i = 0; i < 4; ++i) {
      ball_reset_state_.field_43ee1c[i * 2] = state.fields_ee1c[i];
      ball_reset_state_.field_43ee1c[i * 2 + 1] =
          std::uint16_t(state.fields_ee1c[i]) >> 8;
      lamp_commands_[25 + i] = state.commands_26c[i];
    }
    lamp_commands_[24] = state.command_268;
    lamp_commands_[62] = state.command_300;
    if (event.callback) {
      const bool admitted=request_material5_display(event.callback,event.score_add);
      if(event.callback==0x41062c)apply_capture_delay(admitted,{1,1,1,1,1},0);
    }
    if (event.sample)
      ++material5_hits_;
    if (event.group)
      ++material5_groups_;
    if (event.sample)
      audio_requests_.push_back({0x5c, 3, 3, 0x437da4});
    if (event.stop84)
      audio_requests_.push_back({0x80, 0, 0});
    if (event.score_add) {
      ++award_bank_awards_;
      score_.add(event.score_add);
      ++score_events_;
    }
  }
  if (contact.sample_descriptor == 0x437cf0) {
    const bool accepted=request_material5_display(0x411710,0,true);
    apply_capture_delay(accepted,{1,1,1,1,1},0);
  }
  if (contact.sample_descriptor)
    audio_requests_.push_back(
        contact.sample_descriptor == 0x437cf0
            ? MeanAudioRequest{0x5c, 4, 3, 0x437cf0}
            : MeanAudioRequest{0x5c, 6, 5, contact.sample_descriptor});
  if (contact.field_438b_state)
    apply_stock_car_bumper(ball_.u16(0x3c));
  if (contact.field_438b_state) {
    const unsigned index = contact.field_438b_state == 0x438b08   ? 0
                           : contact.field_438b_state == 0x438b14 ? 1
                                                                  : 2;
    contact_animations_[index].trigger(index == 2 ? 2 : 3);
    if(index==2) {
      mode4_right_.field_438b38=mode4_right_.field_438b3c=0;
      mode4_right_.field_438b40=2;
    }
  }
  if (contact.points) {
    score_.add(contact.points);
    ++score_events_;
  }
  configure_bits();
  mean_separate(ball_, bits_, word(lookup_.field_43e744, normal * 2),
                word(lookup_.field_43e764, normal * 2), nudge_.field_43e71c, nudge_.field_43e410);
  ++collisions_;
  return true;
}
} // namespace slam

namespace slam {
void MeanSimulation::update_right_gate() {
  sync_ball_reset_fields(false);
  ball_reset_state_.table_mode = capture_state_.table_mode;
  mean_right_gate(ball_reset_state_, right_gate_, pool_.count);
  if (capture_state_.table_mode==6)
    std::copy_n(ball_reset_state_.fields.begin()+0x250,4,lamp_commands_[18].begin());
}
void MeanSimulation::load_mode4_fields() {
  const auto &f = ball_reset_state_.fields;
  auto w = [&](unsigned o) {
    return static_cast<std::int16_t>(f[o] | (f[o + 1] << 8));
  };
  capture_state_.field_43f392 = w(0x392);
  lamp_mode_input_.field_3a2 = w(0x3a2);
  lamp_mode_input_.field_3bc = w(0x3bc);
  mode5_state_.field_43f366 = w(0x366);
  upper_state_.field_43f1f2 = w(0x1f2);
  lamp_mode_input_.field_3b0 = w(0x3b0);
  std::memcpy(&mode5_state_.field_43f050, f.data() + 0x050, 4);
  std::memcpy(&mode5_state_.field_43f058, f.data() + 0x058, 4);
  multiball_release_.bits = w(0x39e);
  multiball_release_.field_43f3a6 = w(0x3a6);
  multiball_release_.field_43f064 = static_cast<std::int32_t>(
      std::uint32_t(f[0x064]) | (std::uint32_t(f[0x065]) << 8) |
      (std::uint32_t(f[0x066]) << 16) | (std::uint32_t(f[0x067]) << 24));
  lamp_mode_input_.field_3ba = w(0x3ba);
  capture_state_.table_mode = upper_state_.table_mode =
      ball_reset_state_.table_mode;
  for (unsigned i = 0; i < 63; ++i)
    std::copy_n(f.begin() + 0x208 + i * 4, 4, lamp_commands_[i].begin());
}
void MeanSimulation::apply_shared_reward(unsigned event_id, bool state_ready) {
  if (!state_ready) {
    sync_ball_reset_fields(false);
    ball_reset_state_.table_mode = capture_state_.table_mode;
  }
  // Service34 scheduling and reward DMD callbacks remain presentation adapters.
  // A zero return is explicit, rather than a guessed original queue pointer.
  const bool offroad_repeat=ball_reset_state_.table_mode==5 && mode5_state_.field_43f1e6==4 && event_id<6 && int(event_id)==mode5_state_.field_43f388;
  const auto e = mean_shared_reward(ball_reset_state_, event_id, 0);
  if(offroad_repeat)++offroad_stats_.repeats;
  if(e.callback==0x41041c){
    ++offroad_stats_.awards;if(event_id<6)++offroad_stats_.hits[event_id];
    for(auto points:e.scores)offroad_stats_.score+=points;
  }
  if (e.service_4169e4) {
    auto table = [&](unsigned address, unsigned count) {
      std::vector<std::uint32_t> values;
      for (unsigned i = 0; i < count; ++i) {
        std::uint32_t v = 0;
        for (unsigned j = 0; j < 4; ++j)
          v |= std::uint32_t(flippers_.image.at(address - 0x400000 + i * 4 + j)) << (8 * j);
        values.push_back(v);
      }
      return values;
    };
    if (!mean_rally_target(ball_reset_state_, random_state_.field_43e7a8,
                          table(0x438ddc, 6), table(0x438df4, 19)))
      throw std::runtime_error("Invalid original Rally target table");
  }
  if(e.callback==0x411c60 || e.callback==0x411db4){
    ++rally_stats_.correct;if(event_id<6)++rally_stats_.hits[event_id];
    for(auto points:e.scores)rally_stats_.score+=points;
    if(e.service_419da4)++rally_stats_.completions;
  }
  if(e.callback==0x411824)++rally_stats_.wrong;
  if(e.callback==0x412fa8 && !e.scores.empty()){
    if(event_id<6)++monster_stats_.hits[event_id];
    for(auto points:e.scores)monster_stats_.score+=points;
    if(e.service_419da4)++monster_stats_.completions;
  }
  load_mode4_fields();
  const auto &f = ball_reset_state_.fields;
  auto w = [&](unsigned o) { return static_cast<std::int16_t>(f[o] | (f[o + 1] << 8)); };
  for (unsigned i = 0; i < 6; ++i) mode5_state_.field_43f044[i] = w(0x044 + i * 2);
  mode5_state_.field_43f372 = w(0x372);
  mode5_state_.field_43f386 = w(0x386);
  mode5_state_.field_43f388 = w(0x388);
  mode5_state_.field_43f38c = w(0x38c);
  mode5_state_.field_43f39c = w(0x39c);
  mode5_state_.field_43f35e = w(0x35e);
  capture_state_.field_43f364 = w(0x364);
  for (unsigned i = 0; i < 6; ++i)
    std::copy_n(lamp_commands_[13 + i].begin(), 4,
                mode5_state_.field_43f23c.begin() + i * 4);
  for (auto points : e.scores) {
    score_.add(points); ++score_events_;
    if(e.callback==0x410158 && points>=10000000 && points<=40000000 && points%10000000==0){
      ++speed_stats_.jackpots[points/10000000-1];speed_stats_.score+=points;
    }
  }
  if (e.service_419da4) {
    mean_mode_reset(mode5_state_, capture_state_.table_mode);
    upper_state_.table_mode = ball_reset_state_.table_mode = capture_state_.table_mode;
    upper_state_.field_43f1e6 = mode5_state_.field_43f1e6;
    ++mode_resets_;
  }
  if (e.service_419f6c) rebuild_lamps();
  if (e.service_4194e4)
    audio_requests_.push_back({lamp_mode_input_.field_37a >= 0 ? 0x84 : 0x80,
                              0, lamp_mode_input_.field_37a >= 0 ? 62 : 0});
  // Apply original405f98 admission after mode reset so the award is not erased.
  if (e.callback == 0x412fa8 || e.callback == 0x41041c || e.callback == 0x410158 ||
      e.callback == 0x411c60 || e.callback == 0x411db4 || e.callback == 0x411824) {
    const bool admitted=request_material5_display(e.callback, mode5_state_.field_43f050);
    // Actual41bcd5..41bce9 SPEED request then40f754(allselectors1,delay0).
    if (e.callback==0x410158 && e.control)
      apply_capture_delay(admitted,{1,1,1,1,1},0);
  }
}
void MeanSimulation::step_mode4_clock() {
  sync_ball_reset_fields(false);
  ball_reset_state_.table_mode=4;
  auto probe=ball_reset_state_;
  auto engine=mode5_state_.field_engine_40;
  const auto request=mean_mode4_clock(probe,engine,0);
  // Original414d72 sets mode2 before service34 admission.
  if (request.exit_to_mode2) capture_state_.table_mode=2;
  const bool admitted=request.callback && request_material5_display(request.callback,0,true);
  const auto e=mean_mode4_clock(ball_reset_state_,mode5_state_.field_engine_40,admitted ? 1u : 0u);
  load_mode4_fields();
  if (e.callback) apply_capture_delay(admitted,{1,1,1,1,1},0);
  if (e.bank_order62) audio_requests_.push_back({0x84,0,62});
  if (e.stop80) audio_requests_.push_back({0x80,0,0});
  if (e.exit_to_mode2) {
    const auto display=material5_display_;
    finish_mode4(false);
    material5_display_=display;
  }
}
void MeanSimulation::apply_mode4_switch(unsigned layer,unsigned mask,std::int32_t x,std::int32_t y) {
  sync_ball_reset_fields(false);
  ball_reset_state_.table_mode=capture_state_.table_mode;
  const auto e=mean_mode4_switch(ball_reset_state_,layer,mask,x,y);
  load_mode4_fields();
  if (e.score) {score_.add(e.score);++score_events_;}
  if (e.callback) apply_capture_delay(request_material5_display(e.callback,e.score,true),{1,1,1,1,1},0);
  if (e.service84) audio_requests_.push_back({0x84,0,62});
  if (e.service80) audio_requests_.push_back({0x80,0,0});
  if (e.lamp_rebuild) {
    const auto display=material5_display_;
    finish_mode4(false);
    material5_display_=display;
  }
}
void MeanSimulation::finish_mode4(bool select_next) {
  capture_state_.table_mode = upper_state_.table_mode =
      ball_reset_state_.table_mode = 2;
  if (select_next)
    mean_mode_reset(mode5_state_, capture_state_.table_mode);
  ++mode4_completions_;
  rebuild_lamps();
  // Original416fe0 decides from the preserved armed field in the new mode.
  update_right_gate();
  material5_display_.callback = 0;
  material5_display_.scheduler = {};
  status_ = "original mode4 completed";
}
void MeanSimulation::step_mode4_display() {
  if (multiball_release_.field_43f3a6 == 1) {
    // Actual40726f/413ba6: phase1 idle only after shared display retirement.
    if(material5_display_.scheduler.field_780!=0 || material5_display_.callback ||
       reward_display_pending_ || mode6_display_pending_)return;
    sync_ball_reset_fields(false);
    ball_reset_state_.table_mode = 4;
    const auto e = render_mean_mode4_phase1(ball_reset_state_, mode4_phase1_assets_,
                                            bonus_font_.score, material5_display_.pixels);
    load_mode4_fields();
    if (e.bank1_order50)
      audio_requests_.push_back({0x84, 1, 50});
    // Original 0x4141d9..0x4141e4 queues the new lower track before
    // cancelling the upper track, so the sequencer can resume the new track.
    if (e.service8c)
      audio_requests_.push_back({0x8c, 0, 0});
    return;
  }
  // Mode4 idle stays behind native reward/mode6 presentation boundaries.
  if (material5_display_.callback || reward_display_pending_ ||
      mode6_display_pending_)
    return;
  if (multiball_release_.field_43f3a6 == 0) {
    sync_ball_reset_fields(false);
    ball_reset_state_.table_mode=capture_state_.table_mode;
    const auto &f = ball_reset_state_.fields;
    const auto index = (f[0x3a8] | (f[0x3a9] << 8)) & 127;
    const auto value =
        static_cast<std::int32_t>(flippers_.rd(0x438bdc + index * 4, 4));
    auto probe = ball_reset_state_;
    auto pixels = material5_display_.pixels;
    const auto request = mean_mode4_idle(probe, mode4_idle_assets_, pixels, value, 0);
    const bool admitted = request.callback && request_material5_display(request.callback, 0, true);
    const auto e = mean_mode4_idle(ball_reset_state_, mode4_idle_assets_,
                                   material5_display_.pixels, value, admitted ? 1u : 0u);
    load_mode4_fields();
    if (e.callback) apply_capture_delay(admitted, {1,1,1,1,1}, 0);
  }
  capture_state_.field_43f364 =
      0; // Actual413b60 onlyatidle, not arbitrary timer.
}
void MeanSimulation::debug_start_mode4() {
  debug_start_rule_capture(false);
  capture_state_.table_mode = upper_state_.table_mode = 2;
  capture_state_.field_43f392 = -1;
  capture_state_.field_43f380 = 50;
  status_ = "original mode4 armed capture";
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_start_mode4_right(bool capture) {
  if (capture) {
    lamp_mode_input_.field_3a2 = -1;
    mean_set_layer(ball_, 0, dat_base_);
    ball_.put32(0, 280 * 65536);
    ball_.put32(4, 285 * 65536);
    ball_.put16(0x5c, 20);
    ball_.put16(0x58, 2);
  } else {
    capture_state_.field_43f392 = -1;
    sync_ball_reset_fields(false);
    ball_reset_state_.table_mode = capture_state_.table_mode;
    const auto e = mean_mode4_right_ramp(ball_reset_state_, 3, 1, 50 * 65536);
    load_mode4_fields();
    if (e.callback)
      ++mode4_starts_;
    ball_.put16(0x58, 0);
  }
  field_43e79c_ = 0;
  pool_.objects[0] = ball_;
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_start_right_route(bool empty_switch) {
  capture_state_.table_mode = upper_state_.table_mode = 1;
  lamp_mode_input_.field_3bc = 0;
  for (unsigned i = 0; i < 2; ++i) {
    sync_ball_reset_fields(false);
    ball_reset_state_.table_mode = 1;
    mean_right_progress(ball_reset_state_);
    load_mode4_fields();
  }
  update_right_gate();
  mean_set_layer(ball_, 0, dat_base_);
  configure_bits();
  bool found = false;
  for (int y = 225; y < 340 && !found; ++y)
    for (int x = 260; x < 310; ++x)
      if (!bits_.sample(x, y) &&
          bits_.extra_plane_mask(x, y) == (empty_switch ? 0 : 1)) {
        ball_.put32(0, x * 65536);
        ball_.put32(4, y * 65536);
        found = true;
        break;
      }
  if (!found)
    throw std::runtime_error("Original right capture switch coordinate absent");
  ball_.put32(0x14, 0);
  ball_.put32(0x18, 0);
  ball_.put16(0x5c, empty_switch ? 20 : 0);
  ball_.put16(0x58, 2);
  ball_.put16(0x38, 0xffff);
  field_43e79c_ = 0;
  pool_.objects[0] = ball_;
}
} // namespace slam

namespace slam {
BallMask MeanSimulation::ball_occlusion(const BallMask &outline, int left,
                                        int top, unsigned index) const {
  const auto pointer =
      static_cast<std::uint32_t>(pool_.objects.at(index).i32(0x54));
  if (pointer < dat_base_)
    throw std::runtime_error("Invalid original ball occlusion pointer");
  return windows_ball_occlusion(outline, bits_.dat, pointer - dat_base_, left,
                                top);
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_ball_occlusion(const BallMask &outline) {
  for (int top = 150; top < 340; ++top)
    for (int left = 220; left < 290; ++left) {
      const auto mask =
          windows_ball_occlusion(outline, bits_.dat, 0xb3b36, left, top);
      unsigned hidden = 0;
      for (unsigned p = 0; p < 240; ++p)
        if (!outline.preserve_background[p] && mask.preserve_background[p])
          ++hidden;
      if (hidden < 45 || hidden > 100)
        continue;
      ball_ = initial_ball_;
      mean_set_layer(ball_, 0, dat_base_);
      ball_.put32(0, (left + 7) * 65536);
      ball_.put32(4, (top + 7) * 65536);
      ball_.put32(8, ball_.i32(0));
      ball_.put32(12, ball_.i32(4));
      ball_.put16(0x58, 2);
      pool_.objects[0] = ball_;
      status_ = "original ball/table occlusion preview";
      return;
    }
  throw std::runtime_error("No partially occluded original ball position");
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_start_right_cancel() {
  debug_start_right_route();
  mean_set_layer(ball_, 1, dat_base_);
  configure_bits();
  bool found = false;
  for (int y = 8; y < 59 && !found; ++y)
    for (int x = 8; x < 312; ++x)
      if (!bits_.sample(x, y) && !bits_.sample(x, y + 1) &&
          bits_.extra_plane_mask(x, y) == 1) {
        ball_.put32(0, x * 65536);
        ball_.put32(4, y * 65536);
        found = true;
        break;
      }
  if (!found) throw std::runtime_error("Original armed-route cancellation switch absent");
  pool_.objects[0] = ball_;
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_start_point_force(bool armed_route) {
  if (armed_route) lamp_mode_input_.field_3a2 = -1;
  debug_start_mode4_right(false);
  mean_set_layer(ball_, 2, dat_base_);
  configure_bits();
  bool found = false;
  for (int y = 190; y < 212 && !found; ++y)
    for (int x = 238; x < 255; ++x)
      if (!bits_.sample(x, y) && bits_.extra_plane_mask(x, y) == 0) {
        ball_.put32(0, x * 65536); ball_.put32(4, y * 65536);
        found = true; break;
      }
  if (!found) throw std::runtime_error("No free original magnet preview coordinate");
  ball_.put32(8, ball_.i32(0)); ball_.put32(12, ball_.i32(4));
  ball_.put32(0x14, 0); ball_.put32(0x18, 0);
  ball_.put16(0x58, 2); ball_.put16(0x5c, 0);
  ball_.put16(0x22, 0); ball_.put16(0x1c, 0);
  pool_.objects[0] = ball_;
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_place_phase1_switch(bool exit) {
  mean_set_layer(ball_, 2, dat_base_);
  configure_bits();
  bool found = false;
  for (int y = exit ? 60 : 8; y < (exit ? 150 : 60) && !found; ++y)
    for (int x = exit ? 234 : 8; x < 312; ++x)
      if (!bits_.sample(x, y) && bits_.extra_plane_mask(x, y) == 1) {
        ball_.put32(0, x * 65536); ball_.put32(4, y * 65536);
        found = true; break;
      }
  if (!found) throw std::runtime_error("Original phase1 reward switch absent");
  ball_.put32(8, ball_.i32(0)); ball_.put32(12, ball_.i32(4));
  ball_.put32(0x14, 0); ball_.put32(0x18, 0);
  ball_.put16(0x58, 2); ball_.put16(0x22, 0);
  pool_.objects[0] = ball_;
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_start_shared_mode(unsigned selected) {
  if (selected != 1 && selected != 2 && selected != 4)
    throw std::runtime_error("Unsupported shared reward preview mode");
  reset();
  capture_state_.table_mode = upper_state_.table_mode = 5;
  mode5_state_.field_43f1e6 = selected;
  mean_mode5_begin(mode5_state_, random_state_.field_43e7a8);
  if(selected==1)++monster_stats_.starts;
  if(selected==2)++rally_stats_.starts;
  if(selected==4)++offroad_stats_.starts;
  // The original initializer changes the six commands before their first hit.
  if (selected == 4)
    for (unsigned i = 0; i < 6; ++i)
      std::copy_n(mode5_state_.field_43f23c.begin() + i * 4, 4,
                  lamp_commands_[13 + i].begin());
  sync_ball_reset_fields(false);
}
void MeanSimulation::debug_place_shared_switch(unsigned id) {
  if (id > 5) throw std::runtime_error("Invalid original shared event ID");
  if (id == 0) {
    mean_set_layer(ball_, 0, dat_base_);
    ball_.put16(0x58, 3); ball_.put16(0x5a, 2);
    capture_state_.field_43f380 = -1;
  } else {
    // These bounds come from the five actual switch consumers, not visual guesses.
    const unsigned layer[] = {0, 3, 3, 2, 0, 1};
    const unsigned x0[] = {0, 8, 8, 234, 8, 230};
    const unsigned x1[] = {0, 160, 312, 312, 312, 312};
    const unsigned y0[] = {0, 140, 8, 60, 80, 160};
    const unsigned y1[] = {0, 160, 64, 150, 120, 240};
    mean_set_layer(ball_, layer[id], dat_base_); configure_bits();
    bool found = false;
    for (unsigned y = y0[id]; y < y1[id] && !found; ++y)
      for (unsigned x = x0[id]; x < x1[id]; ++x)
        if (!bits_.sample(x, y) && bits_.extra_plane_mask(x, y) == (id == 4 ? 4 : 1)) {
          ball_.put32(0, x * 65536); ball_.put32(4, y * 65536);
          found = true; break;
        }
    if (!found) throw std::runtime_error("Original shared switch bitmap pixel absent");
    ball_.put16(0x58, 2); ball_.put16(0x5a, 0);
    ball_.put16(0x22, 0); ball_.put16(0x2a, 0);
    if (id == 4) {
      ball_reset_state_.fields[0x3b6] = 100;
      ball_reset_state_.fields[0x3b7] = 0;
      ball_reset_state_.fields[0x35a] = ball_reset_state_.fields[0x35b] = 0xff;
      lamp_mode_input_.field_3b0 = -1; // Explicitly exclude the separate combo reward.
    }
  }
  ball_.put32(8, ball_.i32(0)); ball_.put32(12, ball_.i32(4));
  ball_.put32(0x14, 0); ball_.put32(0x18, 0);
  pool_.objects[0] = ball_;
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_start_mode4_upper() {
  reset();
  debug_start_mode4_right(false); // Existing original phase1 ramp initializer.
  upper_state_.field_438b5c = {-1, 100, 0}; // Explicit original available-slot fixture.
  mean_set_layer(ball_, 0, dat_base_);
  configure_bits();
  bool found = false;
  for (int y = 8; y < 170 && !found; ++y)
    for (int x = 8; x <= 60; ++x)
      if (!bits_.sample(x, y) && bits_.extra_plane_mask(x, y) == 3) {
        ball_.put32(0, x * 65536); ball_.put32(4, y * 65536);
        found = true; break;
      }
  if (!found) throw std::runtime_error("Original upper capture bitmap absent");
  ball_.put32(8, ball_.i32(0)); ball_.put32(12, ball_.i32(4));
  ball_.put32(0x14, 0); ball_.put32(0x18, 0);
  ball_.put16(0x58, 2); ball_.put16(0x5a, 0);
  ball_.put16(0x22, 0); ball_.put16(0x2a, 0);
  pool_.objects[0] = ball_;
}
} // namespace slam

namespace slam {
bool MeanSimulation::request_material5_display(std::uint32_t callback,
                                               std::uint32_t score,
                                               bool save_page) {
  material5_display_.scheduler.field_7a0=capture_state_.table_mode;
  int eax = 0, edx = 0, stack0 = -1, stack1 = -1;
  switch (callback) {
  case 0x411544: eax=6; edx=5; stack0=0x2f; stack1=1; break;
  case 0x410c8c: eax=8; edx=7; stack0=30; stack1=1; break;
  case 0x4119e0: eax=8; edx=7; stack0=14; stack1=1; break;
  case 0x413608: eax=8; edx=7; stack0=22; stack1=1; break;
  case 0x411710: eax=7; edx=6; stack0=23; stack1=1; break;
  case 0x410fcc: eax=7; edx=6; stack0=0x19; stack1=1; break;
  case 0x41121c: eax=8; edx=7; stack0=0x1a; stack1=1; break;
  case 0x411908: eax=7; edx=6; stack0=15; stack1=1; break;
  case 0x412908: eax=7; edx=6; stack0=3; stack1=1; break;
  case 0x40f93c: eax=6; edx=1; break;
  case 0x40f994: eax=8; edx=7; stack0=55; stack1=1; break;
  case 0x40fb78: eax=8; edx=7; stack0=54; stack1=1; break;
  case 0x41210c: eax=8; edx=7; stack0=8; stack1=1; break;
  case 0x4122cc: eax=8; edx=7; stack0=44; stack1=1; break;
  case 0x41163c: eax=5; edx=4; stack0=45; stack1=1; break;
  case 0x410a34: eax=8; edx=7; stack0=33; stack1=1; break;
  case 0x410910: eax=8; edx=7; stack0=34; stack1=1; break;
  case 0x410d34: eax=8; edx=7; stack0=29; stack1=1; break;
  case 0x410b00: eax=10; edx=9; stack0=31; stack1=1; break;
  case 0x413a2c:
    eax = 5;
    edx = 2;
    break;
  case 0x413958:
    eax = 7;
    edx = 6;
    stack0 = 35;
    stack1 = 1;
    break;
  case 0x41062c:
    eax = 7;
    edx = 6;
    stack0 = 36;
    stack1 = 1;
    break;
  case 0x412574:
    eax = 8;
    edx = 7;
    stack0 = 20;
    stack1 = 1;
    break;
  case 0x4130cc:
    eax=8; edx=7; stack0=5; stack1=1; break;
  case 0x4102c0:
    eax=8; edx=7; stack0=57; stack1=1; break;
  case 0x412df0:
    eax=6; edx=5; stack0=11; stack1=1; break;
  case 0x41249c:
    eax=8; edx=7; stack0=6; stack1=1; break;
  case 0x4126ec:
    eax=8; edx=7; stack0=4; stack1=1; break;
  case 0x4114cc:
    eax = 7; edx = 6; stack0 = 24; stack1 = 1; break;
  case 0x41265c:
    eax = 8;
    edx = 7;
    stack0 = 19;
    stack1 = 1;
    break;
  case 0x412d24:
    eax = 8;
    edx = 7;
    stack0 = 1;
    stack1 = 1;
    break;
  case 0x411f10:
    eax = 8;
    edx = 7;
    stack0 = 7;
    stack1 = 1;
    break;
  case 0x412af8:
    eax = 8;
    edx = 7;
    stack0 = 18;
    stack1 = 1;
    break;
  case 0x412c58:
    eax = 8;
    edx = 7;
    break;
  case 0x411fdc:
    eax = 7;
    edx = 6;
    stack0 = 21;
    stack1 = 1;
    break;
  case 0x411c60:
    eax = 7;
    edx = 6;
    stack0 = 12;
    stack1 = 1;
    break;
  case 0x411db4:
    eax = 7;
    edx = 6;
    stack0 = 41;
    stack1 = 1;
    break;
  case 0x412fa8:
  case 0x41041c:
  case 0x410158:
    eax = 7;
    edx = 6;
    break;
  case 0x40fdec:
    eax = 7;
    edx = 6;
    stack0 = 48;
    stack1 = 1;
    break;
  case 0x410e4c:
    eax = 7;
    edx = 6;
    stack0 = 28;
    stack1 = 1;
    break;
  case 0x411824:
    eax = 6;
    edx = 5;
    break;
  case 0x4133d4: eax=4; edx=3; break;
  case 0x413518:
  case 0x4132d4:
  case 0x4131cc: eax=5; edx=4; break;
  case 0x413770: eax=4; edx=0; stack0=9; stack1=1; break;
  case 0x413490: eax=5; edx=4; stack0=10; stack1=1; break;
  case 0x4107c8:
  case 0x41086c:
    eax = 6;
    edx = 5;
    stack0 = 39;
    stack1 = 1;
    break;
  case 0x410504:
    eax = 6;
    edx = 5;
    stack0 = 37;
    stack1 = 1;
    break;
  default:
    // Remaining unclassified/debug display paths retain explicit native policy.
    if (save_page)
      material5_display_.restore_pixels = material5_display_.pixels;
    material5_display_.start(callback, score);
    return true;
  }
  const MeanDisplayRequest request{eax, edx, 2, 0, stack0, stack1, callback};
  const auto old780=material5_display_.scheduler.field_780;
  const bool admitted=material5_display_.request(request,score,save_page);
  queue_display_audio(audio_requests_,old780,request,admitted);
  return admitted;
}
} // namespace slam

namespace slam {
void MeanSimulation::step_shared_display() {
  player_hud_visible_=false;
  main_mode_hud_visible_=false;
  idle_hud_visible_ = false;
  skillshot_display_visible_ = false;
  const bool idle_gate = capture_state_.field_43f364 != 0;
  material5_display_.field_058 = mode5_state_.field_43f058;
  material5_display_.gear=target_reward_.field_player_12;
  material5_display_.field_204=capture_state_.field_43f204;
  material5_display_.field_1fe=capture_state_.field_43f1fe;
  material5_display_.field_1f2=std::uint16_t(upper_state_.field_43f1f2);
  material5_display_.field_1d8 = std::uint16_t(ball_reset_state_.fields[0x1d8] |
      (unsigned(ball_reset_state_.fields[0x1d9]) << 8));
  material5_display_.field_38a = std::uint16_t(lamp_mode_input_.field_38a);
  const auto callback=material5_display_.callback;
  const auto counter=material5_display_.counter;
  const auto dispatch=mean_material5_display_scheduled_step(material5_display_,
      material5_display_assets_, bonus_font_.score, lamp_mode_input_.field_1dc);
  if (dispatch == MeanDisplayDispatch::Callback)
    if (const auto sound = mean_display_sfx(callback, counter, mean_display_sfx_cursor_))
      audio_requests_.push_back(*sound);
  // Actual413b04 ->414970/4146ac ->41455c, only on eligible idle ticks.
  const auto &f = ball_reset_state_.fields;
  const auto w = [&](unsigned o) { return std::uint16_t(f[o] | (unsigned(f[o+1]) << 8)); };
  const int mode = capture_state_.table_mode;
  if (dispatch == MeanDisplayDispatch::Callback && material5_display_.stop_audio_8c)
    audio_requests_.push_back({0x8c,0,0});
  if (dispatch == MeanDisplayDispatch::Idle && !field_43d864_ && !idle_gate &&
      mode == 2 && mean_mode_total_idle(mode5_state_.field_43f366,mode5_state_.field_engine_40)) {
    // Actual4146ac: consume pending total before admission, then40f754.
    ball_reset_state_.fields[0x366]=ball_reset_state_.fields[0x367]=0;
    const bool admitted=request_material5_display(0x410c8c,0,true);
    apply_capture_delay(admitted,{1,1,1,1,1},0);
  } else if (dispatch == MeanDisplayDispatch::Idle && !field_43d864_ && !idle_gate &&
      w(0x35c) && (mode == 1 || mode == 3 ||
                   (mode == 2 && static_cast<std::int16_t>(w(0x35a)) >= 0))) {
    skillshot_display_visible_ = mean_skillshot_display(
        ball_reset_state_.field_438af8, skillshot_display_assets_,
        material5_display_.pixels, w(0x358), w(0x206), w(0x362));
  } else if (dispatch == MeanDisplayDispatch::Idle && !field_43d864_ &&
             !idle_gate && (mode == 1 || mode == 3)) {
    auto &hud=player_hud_;
    hud.counter=static_cast<std::uint32_t>(ball_reset_state_.field_438af8);
    hud.field_35c=w(0x35c);hud.field_358=w(0x358);
    hud.field_206=w(0x206);hud.field_362=w(0x362);
    hud.field_360=static_cast<std::int16_t>(w(0x360));
    hud.player_0e=ball_number_;hud.score=score_.value();
    hud.pixels=material5_display_.pixels;
    if(mean_player_hud_step(hud,player_hud_assets_)) {
      ball_reset_state_.field_438af8=static_cast<std::int32_t>(hud.counter);
      ball_reset_state_.fields[0x360]=static_cast<std::uint16_t>(hud.field_360);
      ball_reset_state_.fields[0x361]=static_cast<std::uint16_t>(hud.field_360)>>8;
      material5_display_.pixels=hud.pixels;player_hud_visible_=true;
    }
  } else if (dispatch == MeanDisplayDispatch::Idle && !field_43d864_ && !idle_gate &&
             mode == 2) {
    MeanIdleHud hud;
    hud.counter=static_cast<std::uint32_t>(ball_reset_state_.field_438af8);
    hud.field_398=lamp_mode_input_.field_398;
    hud.field_37a=lamp_mode_input_.field_37a;
    hud.field_3ac=static_cast<std::int16_t>(w(0x3ac));
    hud.field_054=award_bank_054_;
    hud.score=score_.value();
    mean_idle_hud_step(hud,idle_hud_assets_);
    ball_reset_state_.field_438af8=static_cast<std::int32_t>(hud.counter);
    idle_hud_=hud;
    material5_display_.pixels=hud.pixels;
    idle_hud_visible_=true;
  }
  if (dispatch == MeanDisplayDispatch::Idle && !field_43d864_ && !idle_gate &&
      (mode==5 || mode==6)) {
    MeanMainModeHud hud;
    hud.counter=static_cast<std::uint32_t>(ball_reset_state_.field_438af8);
    hud.mode=mode;hud.selected=mode5_state_.field_43f1e6;
    hud.field_39c=mode5_state_.field_43f39c;
    hud.field_38c=mode5_state_.field_43f38c;
    hud.field_05c=mode5_state_.field_43f05c;
    hud.field_38e=mode5_state_.field_43f38e;
    hud.field_368=mode5_state_.field_43f368;
    hud.field_36c=mode5_state_.field_43f36c;
    hud.score=score_.value();
    if(mean_main_mode_hud_step(hud,main_mode_hud_assets_)) {
      main_mode_hud_=hud;
      ball_reset_state_.field_438af8=static_cast<std::int32_t>(hud.counter);
      material5_display_.pixels=hud.pixels;
      main_mode_hud_visible_=true;
    }
  }
  if(player_hud_.field_engine_5c) --player_hud_.field_engine_5c; // Actual404b2a, after display.
  const auto effects=mean_display_callback_effects(callback,counter,dispatch);
  if(effects.request_438afc) field_438afc_={1,0,0};
  if(effects.release_mode6) mode5_state_.field_43f382=0;
  // Actual413b04+413b60: reward release occurs on idle, not callback completion.
  if(effects.release_reward && capture_state_.field_43f364!=0)
    capture_state_.field_43f364=0;
  if(mode6_display_pending_){
    upper_state_.field_438b44[0]=ball_reset_state_.field_438b44;
    upper_state_.field_438b44[2]=ball_reset_state_.field_438b4c;
  }
  multiball_release_.field_43f382=mode5_state_.field_43f382;
  if(mode6_display_pending_ && mode5_state_.field_43f382==0)
    mode6_display_pending_=false;
  if(reward_display_pending_ && capture_state_.field_43f364==0){
    reward_display_pending_=false;
    ++reward_completions_;
  }
}
} // namespace slam

namespace slam {
void MeanSimulation::enter_minigame_display() {
#ifdef SLAM_MEAN_MINIGAME_LIFT
  auto &s=material5_display_.scheduler;
  mean_display_minigame_enter(s);
  material5_display_.callback=0;
  for(auto pair : {std::pair<unsigned,std::uint32_t>{0x10,static_cast<std::uint32_t>(s.field_780)},
      {0x14,static_cast<std::uint32_t>(s.field_784)},
      {0x18,static_cast<std::uint32_t>(s.field_788)},
      {0x1c,static_cast<std::uint32_t>(s.field_78c)},
      {0x20,s.field_790},{0x44,static_cast<std::uint32_t>(s.field_7b4)}})
    minigame_.wr(0x1001000+pair.first,pair.second,4);
#endif
}
} // namespace slam

namespace slam {
void MeanSimulation::project_return_pass_fields() {
  const auto &f=ball_reset_state_.fields;
  const auto w=[&](unsigned o){return static_cast<std::int16_t>(f[o]|(unsigned(f[o+1])<<8));};
  lamp_mode_input_.field_374=w(0x374); lamp_mode_input_.field_37c=w(0x37c);
  mode5_state_.field_43f1e6=w(0x1e6);
  upper_state_.field_43f1e6=mode5_state_.field_43f1e6;
  mode5_state_.field_43f050=std::uint32_t(f[0x50])|(std::uint32_t(f[0x51])<<8)|
      (std::uint32_t(f[0x52])<<16)|(std::uint32_t(f[0x53])<<24);
  std::copy_n(f.begin()+0x25c,4,lamp_commands_[21].begin());
  for(unsigned i=45;i<50;++i)
    std::copy_n(f.begin()+0x208+i*4,4,lamp_commands_[i].begin());
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_place_return_pass() {
  capture_state_.table_mode=upper_state_.table_mode=2; // Explicit human-mode fixture.
  mean_set_layer(ball_,2,dat_base_); configure_bits();
  bool found=false;
  for(int y=8;y<60 && !found;++y)
    for(int x=8;x<312;++x)
      if(!bits_.sample(x,y) && bits_.extra_plane_mask(x,y)==1){
        ball_.put32(0,x*65536); ball_.put32(4,y*65536); found=true; break;
      }
  if(!found) throw std::runtime_error("Original return-pass bitmap absent");
  ball_.put32(8,ball_.i32(0));ball_.put32(12,ball_.i32(4));
  ball_.put32(0x14,0);ball_.put32(0x18,0);
  ball_.put16(0x58,2);ball_.put16(0x5a,0);
  ball_.put16(0x22,0);ball_.put16(0x2a,0);ball_.put16(0x5c,0);
  pool_.objects[0]=ball_;
}
} // namespace slam

namespace slam {
void MeanSimulation::debug_nudge_warning() {
  reset();capture_state_.table_mode=upper_state_.table_mode=2;
  if(!request_material5_display(0x40f93c,0))throw std::runtime_error("Warning DMD admission failed");
  // Actual417ae0 accepted40f754(1,1,1,1;stack1,0) clears all five delays.
  apply_capture_delay(true,{1,1,1,1,1},0);
}
}

namespace slam {
void MeanSimulation::debug_tilt_release() {
  // Diagnostic callback2 entry, followed by one actual service1c continuation.
  // No persistent game Tilt state or invented nudge forces.
  reset();field_43e79c_=0;
  capture_state_.table_mode=upper_state_.table_mode=2;
  ball_.put16(0x58,3);ball_.put16(0x5a,2);
  capture_state_.field_43f380=50;capture_state_.field_43f392=0;
  MeanCaptureTickEvent e;
  if(!mean_capture_tick(ball_,capture_state_,dat_base_,e,true) || e.services_1c_samples!=1 || capture_state_.field_43f380!=49)
    throw std::runtime_error("Tilt release fixture failed");
  for(unsigned i=0;i<e.services_1c_samples;++i)audio_requests_.push_back({0x5c,6,5,0x437dec});
  pool_.objects[0]=ball_;captures_=releases_=1;
  status_="diagnostic original Tilt callback2 release";
}
}

namespace slam {
void MeanSimulation::apply_tilt() {
  if(field_43d864_ || game_over_ || capture_state_.table_mode<=1 || capture_state_.table_mode==3)return;
  field_43d864_=true;
  // Common40554c releases flipper actions;417ae0 stops88,starts84 bank1/order52.
  set_flippers(false,false);
#ifdef SLAM_MEAN_FLIPPER_LIFT
  for(auto a:{0x4298b8u,0x4298bcu,0x4298c0u})flippers_.wr(a,0xffffffffu,4);
#endif
  MeanNudgeTable table;
  table.engine_field_14=material5_display_.scheduler.field_784;
  table.callback(1,0);
  material5_display_.callback=0;material5_display_.scheduler.field_784=table.engine_field_14;
  for(const auto &q:table.requests)audio_requests_.push_back({int(q.target),int(q.edx),int(q.eax)});
}
void MeanSimulation::debug_tilt_capture(unsigned callback,unsigned mode,bool tilt) {
  if(callback<1 || callback>5)throw std::runtime_error("Invalid Tilt capture fixture");
  reset();field_43e79c_=0;capture_state_.table_mode=upper_state_.table_mode=mode;
  ball_.put16(0x58,3);ball_.put16(0x5a,callback);
  upper_state_.field_43f36a=50;capture_state_.field_43f380=50;
  upper_state_.field_438b5c={-1,100,0};capture_state_.field_438b68={-1,100,0};capture_state_.field_438b74={-1,100,0};
  mode4_right_.field_438b80={-1,100,0};mode4_right_.field_438b38=10;mode4_right_.field_438b40=0;
  multiball_release_.slot={-1,100,0};
  sync_ball_reset_fields(false);ball_reset_state_.table_mode=mode;ball_reset_state_.fields[0x370]=50;ball_reset_state_.fields[0x371]=0;
  ball_reset_state_.fields[0x3a2]=ball_reset_state_.fields[0x3a3]=0;load_mode4_fields();
  pool_.objects[0]=ball_;captures_=1;upper_captures_=callback==1;
  bonus_turn_.field_player_08=10000000; // Explicit nonzero diagnostic bonus bank.
  set_continuous_play(true);if(tilt)apply_tilt();
}
}

namespace slam {
std::array<std::int32_t,5> MeanSimulation::capture_delays() const {
  return {upper_state_.field_438b5c[2],capture_state_.field_438b68[2],capture_state_.field_438b74[2],mode4_right_.field_438b80[2],multiball_release_.slot[2]};
}
void MeanSimulation::debug_mode5_award(bool tilt,bool reject) {
  debug_tilt_capture(2,5,tilt);
  capture_state_.field_43f380=-1;
  mode5_state_.field_43f1e6=0;mode5_state_.field_43f39c=1000;mode5_state_.field_43f05c=65000000;
  upper_state_.field_438b5c[2]=101;capture_state_.field_438b68[2]=102;
  capture_state_.field_438b74[2]=103;mode4_right_.field_438b80[2]=104;
  multiball_release_.slot[2]=105;
  if(reject && !request_material5_display(0x410b00,0,true))
    throw std::runtime_error("Diagnostic high-priority DMD admission failed");
}
}

namespace slam {
void MeanSimulation::press_plunger() {
  if(game_over_ || bonus_active_ || minigame_active_)return;
  ball_reset_state_.table_mode=capture_state_.table_mode;
  sync_ball_reset_fields(false);
  auto &f=ball_reset_state_.fields;
  auto word=[&](unsigned o){return std::uint16_t(f[o] | (unsigned(f[o+1])<<8));};
  auto dword=[&](unsigned o){std::uint32_t v=0;for(unsigned i=0;i<4;++i)v|=std::uint32_t(f[o+i])<<(i*8);return std::int32_t(v);};
  auto writeword=[&](unsigned o,std::uint16_t v){f[o]=v&255;f[o+1]=v>>8;};
  auto writedword=[&](unsigned o,std::uint32_t v){for(unsigned i=0;i<4;++i)f[o+i]=v>>(i*8);};
  MeanModeLock s;s.engine_30=capture_state_.table_mode;s.engine_44=0;s.service_1c=field_43d864_;
  s.field_384=word(0x384);s.field_3a6=word(0x3a6);s.field_39e=word(0x39e);s.field_3a8=word(0x3a8);
  s.field_030=dword(0x030);s.field_064=dword(0x064);s.field_038=dword(0x038);
  std::int32_t indexed=0;
#ifdef SLAM_MEAN_FLIPPER_LIFT
  if(s.engine_30==4 && s.field_3a6==0 && s.field_39e==3)
    indexed=static_cast<std::int32_t>(flippers_.rd(0x438bdc+static_cast<std::int16_t>(s.field_3a8)*4,4));
#endif
  const auto entry=s;s.press(0,indexed);
  if(s.requests.empty())return;
  const auto callback=s.requests.front().stack.at(2);
  const bool accepted=request_material5_display(callback,0,true);
  s=entry;s.press(accepted?-1:0,indexed);
  writeword(0x384,s.field_384);writeword(0x39e,s.field_39e);writedword(0x064,s.field_064);writedword(0x038,s.field_038);
  const auto selected=static_cast<std::int16_t>(word(0x1e6));
  if(s.field_384!=entry.field_384 && selected>=0 && selected<5)
    std::copy(s.selected_lamp.begin(),s.selected_lamp.end(),f.begin()+0x2bc+selected*4);
  sync_ball_reset_fields(true);load_mode4_fields();
  apply_capture_delay(accepted,{1,1,1,1,1},0);
}
}

namespace slam {
void MeanSimulation::apply_pit_stop(unsigned id) {
  if (field_43d864_) return;
  sync_ball_reset_fields(false);
  ball_reset_state_.table_mode=capture_state_.table_mode;
  const auto e=mean_pit_stop(ball_reset_state_,id,[&](const MeanPitStopRequest &r) {
    const bool accepted=request_material5_display(r.callback,0,true);
    apply_capture_delay(accepted,{1,1,1,1,1},0);
    return accepted ? 1u : 0u;
  });
  sync_ball_reset_fields(true);
  load_mode4_fields();
  for (const auto &request:e.requests) if(request.callback==0x413518)++pit_stats_.starts;
  for (auto score:e.scores) {
    score_.add(score);++score_events_;pit_stats_.score+=score;
    if(id<4 && score==2500000)++pit_stats_.punctures[id];
    if(id<4 && score==10000000)++pit_stats_.repairs[id];
    if(score==15000000)++pit_stats_.completions;
  }
}
void MeanSimulation::apply_stock_car_bumper(unsigned material) {
  sync_ball_reset_fields(false);
  ball_reset_state_.table_mode=capture_state_.table_mode;
  auto preview=ball_reset_state_;
  const auto request=mean_stock_car_bumper(preview,material,field_43d864_,0);
  const bool accepted=request.callback && request_material5_display(request.callback,request.score,true);
  const auto e=mean_stock_car_bumper(ball_reset_state_,material,field_43d864_,accepted ? 1u : 0u);
  sync_ball_reset_fields(true);
  load_mode4_fields();
  if (e.callback) apply_capture_delay(accepted,{1,1,1,1,1},0);
  if (e.score) {
    score_.add(e.score); ++score_events_;
    ++stock_stats_.hits; stock_stats_.score+=e.score;
    const auto &f=ball_reset_state_.fields;
    if ((unsigned(f[0x38a]) | (unsigned(f[0x38b])<<8))==0) ++stock_stats_.completions;
  }
}
}

namespace slam {
void MeanSimulation::debug_start_short_mode(bool stock, bool jackpot) {
  // Explicit diagnostic idle-play context; never used by normal gameplay.
  reset();
  if (!step()) throw std::runtime_error(status_);
  capture_state_.table_mode=upper_state_.table_mode=2;
  idle_hud_visible_=false;
  material5_display_={};
  if (stock) {
    // Known original initial StockCar count from41c69a/mean_right_cancel.
    lamp_mode_input_.field_38a=15;
    apply_stock_car_bumper(4);
  } else {
    for (unsigned id=0;id<4;++id) apply_pit_stop(id);
    if (jackpot) for (unsigned id=0;id<4;++id) apply_pit_stop(id);
  }
}
}

namespace slam {
void MeanSimulation::debug_speed_jackpot(unsigned locks, bool reject, bool preview) {
  if (locks>3) throw std::runtime_error("Invalid SPEED diagnostic lock count");
  reset();
  capture_state_.table_mode=upper_state_.table_mode=6;
  mode5_state_.field_43f38e=locks>=1 ? 2000 : -1;
  mode5_state_.field_43f368=locks>=2 ? 2000 : -1;
  mode5_state_.field_43f36c=locks>=3 ? 2000 : -1;
  upper_state_.field_438b5c[2]=101;capture_state_.field_438b68[2]=102;
  capture_state_.field_438b74[2]=103;mode4_right_.field_438b80[2]=104;multiball_release_.slot[2]=105;
  for (unsigned i=0;i<4;++i) ball_reset_state_.fields[0x024+i]=0x1234u>>(8*i);
  if(reject && !request_material5_display(0x410b00,0,true))
    throw std::runtime_error("SPEED diagnostic high-priority request rejected");
  apply_shared_reward(1);
  // Explicit display-only preview; no claim of naturally reached three locks.
  if (preview) for (unsigned i=0;i<76;++i) step_shared_display();
}
}

namespace slam {
void MeanSimulation::debug_cliff_jump(unsigned previous,bool failure,bool reject,bool preview) {
  if(previous>5) throw std::runtime_error("Invalid Cliff diagnostic count");
  reset();
  capture_state_.table_mode=upper_state_.table_mode=4;
  multiball_release_.field_43f3a6=0;multiball_release_.bits=0;
  ball_reset_state_.fields[0x1f4]=previous;ball_reset_state_.fields[0x1f5]=0;
  step_mode4_display();
  if(material5_display_.callback!=0x412574) throw std::runtime_error("Cliff instruction admission failed");
  for(unsigned i=0;i<167;++i) step_shared_display();
  // Explicit fixture boundary: the original held-ball release has reachedbits3.
  multiball_release_.bits=3;
  set_flippers(true,false);
  if(multiball_release_.bits!=7 || material5_display_.callback!=0x41265c)
    throw std::runtime_error("Cliff rev input failed: bits="+std::to_string(multiball_release_.bits)+" callback="+std::to_string(material5_display_.callback)+" mode="+std::to_string(capture_state_.table_mode));
  upper_state_.field_438b5c[2]=101;capture_state_.field_438b68[2]=102;
  capture_state_.field_438b74[2]=103;mode4_right_.field_438b80[2]=104;multiball_release_.slot[2]=105;
  for(unsigned i=0;i<4;++i) ball_reset_state_.fields[0x024+i]=0x1234u>>(8*i);
  if(reject && !request_material5_display(0x410b00,0,true))
    throw std::runtime_error("Cliff diagnostic priority admission failed");
  if(failure) {
    apply_mode4_switch(1,1,150*65536,390*65536);
    for(unsigned i=0;i<350;++i) step_mode4_clock();
  } else apply_mode4_switch(3,1,150*65536,63*65536);
  if(preview) for(unsigned i=0;i<61;++i) step_shared_display();
}
}

namespace slam {
void MeanSimulation::apply_left_progress() {
  // Original41b305..41b315 precedes the human-mode guard.
  mode4_right_.field_438b38=0;
  mode4_right_.field_438b3c=0;
  mode4_right_.field_438b40=4;
  sync_ball_reset_fields(false);
  ball_reset_state_.table_mode=capture_state_.table_mode;
  auto probe=ball_reset_state_;
  const auto request=mean_left_progress(probe,0);
  const bool admitted=request.display_request && request_material5_display(request.callback,0,true);
  const auto e=mean_left_progress(ball_reset_state_,admitted ? 1u : 0u);
  load_mode4_fields();
  if(e.capture_delay_request)apply_capture_delay(admitted,{1,1,1,1,1},0);
}
}

namespace slam {
void MeanSimulation::debug_left_progress(unsigned stage,unsigned letters,unsigned mode,bool reject) {
  if(stage>2||letters>5||mode<1||mode>6)throw std::runtime_error("Invalid left progression fixture");
  reset();capture_state_.table_mode=upper_state_.table_mode=mode;
  lamp_mode_input_.field_3ba=stage;upper_state_.field_43f1f2=letters;
  capture_state_.field_43f392=stage==2?-1:0;
  upper_state_.field_438b5c[2]=101;capture_state_.field_438b68[2]=102;
  capture_state_.field_438b74[2]=103;mode4_right_.field_438b80[2]=104;multiball_release_.slot[2]=105;
  for(unsigned i=0;i<4;++i)ball_reset_state_.fields[0x024+i]=0x1234u>>(8*i);
  if(reject) {
    capture_state_.table_mode=2; // Seed an existing owner before the tested mode.
    const bool seeded=request_material5_display(0x410b00,0,true);
    capture_state_.table_mode=mode;
    if(!seeded)throw std::runtime_error("Left progression priority fixture rejected");
  }
  apply_left_progress();
}
}
