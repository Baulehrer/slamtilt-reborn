#pragma once
#include "core/audio_request.h"
#include "input/mean_nudge.h"
#include "input/mean_nudge_tilt.h"
#include "assets/mean_point_forces.h"
#include "assets/ball_occlusion.h"
#include "dmd/mean_bonus_pixels.h"
#include "dmd/mean_material5_display.h"
#include "dmd/mean_skillshot_display.h"
#include "dmd/mean_idle_hud.h"
#include "dmd/mean_player_hud.h"
#include "dmd/mean_main_mode_hud.h"
#include "dmd/mean_mode4_idle.h"
#include "dmd/mean_mode4_phase1.h"
#include "dmd/windows_dmd.h"
#include "physics/mean_ball_pool.h"
#include "physics/mean_capture_tick.h"
#include "physics/mean_material_bundle.h"
#include "physics/mean_mode4_right_entry.h"
#include "physics/mean_mode5_left.h"
#include "physics/mean_mode6_side.h"
#include "physics/mean_multiball_release.h"
#include "physics/mean_reward_display.h"
#include "physics/mean_right_gate.h"
#include "physics/mean_step.h"
#include "physics/mean_upper_capture.h"
#include "physics/mean_upper_release.h"
#include "rules/mean_award_bank.h"
#include "rules/mean_ball_reset.h"
#include "rules/mean_bonus_display.h"
#include "rules/mean_bonus_turn.h"
#include "rules/mean_contact_animation.h"
#include "rules/mean_lamp_events.h"
#include "rules/mean_lamp_mode.h"
#include "rules/mean_lamps.h"
#include "rules/mean_score.h"
#include <filesystem>
#include <functional>
#ifdef SLAM_MEAN_FLIPPER_LIFT
#include "physics/flipper_lift.h"
#ifdef SLAM_MEAN_NORMAL_LIFT
#include "physics/mean_normal_lift.h"
#endif
#ifdef SLAM_MEAN_MINIGAME_LIFT
#include "physics/mean_minigame_lift.h"
#endif
#endif
namespace slam {
using MeanAudioRequest = AudioRequest;
struct MeanGearStats {
  std::array<unsigned,6> upshifts{};
  unsigned rotations=0,fifth_enables=0,upper_extras=0,capped_awards=0;
};
struct MeanChickenStats {
  std::array<std::uint32_t,3> awards{};
  unsigned starts=0,races=0,completions=0,max_finishes=0,timeouts=0;
  std::uint64_t score=0;
};
struct MeanOffroadStats {
  std::array<unsigned,6> hits{};
  unsigned starts=0,awards=0,repeats=0,ends=0;
  std::uint64_t score=0;
};
struct MeanRallyStats {
  std::array<unsigned,6> hits{};
  unsigned starts=0,correct=0,wrong=0,completions=0,timeouts=0;
  std::uint64_t score=0;
};
struct MeanMonsterStats {
  std::array<unsigned,6> hits{};
  unsigned starts=0,completions=0,timeouts=0;
  std::uint64_t score=0;
};
struct MeanSpeedStats {
  std::array<unsigned,4> jackpots{};
  std::uint64_t score=0;
};
struct MeanStockCarStats {
  unsigned starts=0,hits=0,completions=0;
  std::uint64_t score=0;
};
struct MeanPitStopStats {
  std::array<unsigned,4> punctures{},repairs{};
  unsigned starts=0,completions=0,timeouts=0;
  std::uint64_t score=0;
};
// Optional diagnostic boundary after integration/launch/drain, before408e70.
// Contains real live values; observer does not supply gameplay state.
struct MeanContactTrace {
  MeanObject before, dispatch, after;
  std::array<std::uint32_t,27> flipper_words{};
  std::array<std::uint32_t,40> engine_words{};
  std::array<std::int32_t,4> nudge{}; // 43e71c,43e410,43e724,43e564.
  MeanMaterialBundleState material;
  std::array<std::uint8_t,0x3c0> cached_fields{};
  std::array<std::uint8_t,8> fields_ee1c{};
  // Actual mutable DAT tiles, including reset/open and raised LaneSaver.
  std::array<std::uint8_t,120> lane_saver_normal{};
  std::array<std::uint8_t,512> lane_saver_hit{};
  std::uint32_t dat_base=0;
  unsigned ball_index=0,ball_count=0;
  int mode=0,selected=0;
  bool wall=false,ok=false;
};
struct MeanPairTrace {
  std::array<MeanObject,2> before,after;
  unsigned first=0,second=0,count=0;
  int mode=0;
  std::array<std::uint32_t,3> globals{}; // 43e728,43e764,43e75c.
};
class MeanSimulation {
public:
  MeanSimulation(const std::filesystem::path &dat,
                 const std::filesystem::path &prepared,
                 const std::filesystem::path &trace);
  void reset();
  void set_contact_observer(std::function<void(const MeanContactTrace&)> observer) {
    contact_observer_=std::move(observer);
  }
  void set_pair_observer(std::function<void(const MeanPairTrace&)> observer) {
    pair_observer_=std::move(observer);
  }
  std::vector<MeanAudioRequest> take_audio_requests() {
    auto result = std::move(audio_requests_);
    audio_requests_.clear();
    return result;
  }
  void set_continuous_play(bool enabled) { continuous_play_ = enabled; }
  // Explicit stress-test policy; normal play observes the original end
  // boundary.
  void set_endless_play(bool enabled) { endless_play_ = enabled; }
  bool game_over() const { return game_over_; }
  bool tilted() const { return field_43d864_; }
  std::int16_t field_43f380() const {return capture_state_.field_43f380;}
  void apply_tilt();
  void debug_tilt_capture(unsigned callback,unsigned mode=2,bool tilt=true);
  void debug_mode5_award(bool tilt,bool reject);
  std::array<std::int32_t,5> capture_delays() const;
  std::uint64_t score() const { return score_.value(); }
  int contact_frame(unsigned index) const {
    return index==3?lane_saver_frame_:contact_animations_.at(index).displayed_frame;
  }
  unsigned score_events() const { return score_events_; }
  const MeanDisplayScheduler &display_scheduler() const { return material5_display_.scheduler; }
  unsigned return_passes() const { return return_passes_; }
  unsigned return_pass_awards() const { return return_pass_awards_; }
  void set_retail_minigame(bool enabled) { retail_minigame_=enabled; }
  unsigned minigame_steps() const { return minigame_steps_; }
  bool minigame2_goal_text_seen() const { return minigame2_goal_seen_; }
  unsigned material5_display_callback() const {
    return material5_display_.callback;
  }
  unsigned material5_display_counter() const {
    return material5_display_.counter;
  }
  bool main_mode_hud_visible() const { return main_mode_hud_visible_; }
  const MeanMainModeHud &main_mode_hud() const { return main_mode_hud_; }
  bool player_hud_visible() const { return player_hud_visible_; }
  const MeanPlayerHud &player_hud() const { return player_hud_; }
  bool idle_hud_visible() const { return idle_hud_visible_; }
  const MeanIdleHud &idle_hud() const { return idle_hud_; }
  bool material5_display_active() const {
    return player_hud_visible_ || main_mode_hud_visible_ || idle_hud_visible_ || skillshot_display_visible_ || material5_display_.callback != 0 ||
           (capture_state_.table_mode == 4 &&
            multiball_release_.field_43f3a6 <= 1);
  }
  const WindowsDmdPixels &material5_pixels() const {
    return material5_display_.pixels;
  }
  const std::array<unsigned, 8> &switch_reward_variants() const {
    return switch_reward_variants_;
  }
  BallMask ball_occlusion(const BallMask &, int left, int top,
                          unsigned index) const;
  void set_original_point_force_context(std::int16_t type, bool suppressed) {
    point_force_context_ = true;
    point_force_suppressed_ = suppressed;
    ball_reset_state_.field_438a40 = type;
  }
  void debug_start_point_force(bool armed_route = false);
  void debug_place_phase1_switch(bool exit);
  void debug_start_shared_mode(unsigned selected);
  void debug_place_shared_switch(unsigned event_id);
  void debug_place_return_pass();
  void debug_nudge_warning();
  void debug_tilt_release();
  unsigned shared_target() const { return unsigned(mode5_state_.field_43f38c); }
  const MeanBallResetState &shared_raw_state() const { return ball_reset_state_; }
  std::uint16_t phase1_state() const { return unsigned(ball_reset_state_.fields[0x3aa]) | (unsigned(ball_reset_state_.fields[0x3ab]) << 8); }
  std::uint32_t phase1_award_total() const { return std::uint32_t(mode5_state_.field_43f058); }
  bool right_route_open() const { return ball_reset_state_.fields[0x3b8] || ball_reset_state_.fields[0x3b9]; }
  std::int16_t point_force_type() const { return ball_reset_state_.field_438a40; }
  unsigned point_force_updates() const { return point_force_updates_; }
  unsigned right_cancellations() const { return right_cancellations_; }
  bool right_route_armed() const { return lamp_mode_input_.field_3a2 != 0; }
  void debug_start_right_cancel();
  unsigned right_arms() const { return right_arms_; }
  unsigned right_markers() const { return right_markers_; }
  unsigned right_captures() const { return right_captures_; }
  unsigned mode4_starts() const { return mode4_starts_; }
  unsigned mode4_completions() const { return mode4_completions_; }
  unsigned state7_steps() const { return state7_steps_; }
  void debug_start_mode4();
  void debug_start_mode4_upper();
  void debug_start_mode4_right(bool capture);
  void debug_start_right_route(bool empty_switch = false);
  void debug_ball_occlusion(const BallMask &);
  unsigned pending_mode4_rewards() const { return pending_mode4_rewards_; }
  const MeanStockCarStats &stock_car_stats() const {return stock_stats_;}
  const MeanPitStopStats &pit_stop_stats() const {return pit_stats_;}
  unsigned switch_rewards() const { return switch_rewards_; }
  unsigned skull_award_count() const { return unsigned(ball_reset_state_.fields[0x39a]) | (unsigned(ball_reset_state_.fields[0x39b])<<8); }
  int skull_window_ticks() const { return lamp_mode_input_.field_3b0; }
  unsigned side_extra_balls() const { return side_extra_balls_; }
  std::array<int,7> lap_goal_fields() const { return {capture_state_.field_43f204,capture_state_.field_43f1fe,capture_state_.field_43f200,capture_state_.field_43f202,capture_state_.field_43f1fa,upper_state_.field_43f1fc,upper_state_.field_43f378}; }
  std::int16_t award_bank_timer() const { return lamp_mode_input_.field_37a; }
  std::uint32_t award_bank_value() const { return award_bank_054_; }
  unsigned award_bank_starts() const { return award_bank_starts_; }
  unsigned award_bank_awards() const { return award_bank_awards_; }
  unsigned material5_hits() const { return material5_hits_; }
  unsigned material5_groups() const { return material5_groups_; }
  bool kickback_armed() const { return material_state_.field_43f1da != 0; }
  int kickback_timer() const { return material_state_.field_43f390; }
  const std::array<std::uint8_t,4>& kick_letters() const { return lamp_mode_input_.field_1dc; }
  int lane_saver_frame() const { return lane_saver_frame_; }
  unsigned lane_saver_patches() const { return lane_saver_patches_; }
  std::array<std::uint8_t,632> lane_saver_geometry() const { std::array<std::uint8_t,632> out{};unsigned n=0;for(unsigned y=0;y<30;++y)for(unsigned x=0;x<4;++x)out[n++]=bits_.dat.at(0x959f6+0x49e1+y*40+x);for(unsigned p=0;p<4;++p)for(unsigned y=0;y<32;++y)for(unsigned x=0;x<4;++x)out[n++]=bits_.dat.at(0x9ba36+p*0x6040+0x49e1+y*40+x);return out; }
  unsigned kickback_consumptions() const { return kickback_consumptions_; }
  unsigned top_target_hits() const { return top_target_hits_; }
  unsigned top_target_cycles() const { return top_target_cycles_; }
  const WindowsDmdPixels &bonus_pixels() const { return bonus_dmd_; }
  unsigned bonus_phase() const { return bonus_display_.phase; }
  bool bonus_active() const { return bonus_active_; }
  unsigned bonus_display_ticks() const { return bonus_display_ticks_; }
  unsigned bonus_completions() const { return bonus_completions_; }
  unsigned bonus_starts() const { return bonus_starts_; }
  unsigned bonus_awards() const { return bonus_awards_; }
  std::uint32_t last_bonus() const { return last_bonus_; }
  std::uint32_t pending_bonus() const { return bonus_turn_.field_player_08; }
  int lamp_state(unsigned index) const { return lamp_visible_.at(index); }
  const std::array<unsigned, 63> &lamp_updates() const { return lamp_updates_; }
  unsigned drains() const { return drains_; }
  unsigned captures() const { return captures_; }
  unsigned upper_captures() const { return upper_captures_; }
  unsigned mode5_awards() const { return mode5_awards_; }
  unsigned mode_resets() const { return mode_resets_; }
  bool debug_start_minigame();
  void debug_start_rule_capture(bool reward);
  unsigned ball_saves() const { return ball_saves_; }
  std::int32_t restart_gate() const { return field_43e79c_; }
  unsigned restart_initializations() const { return restart_initializations_; }
  unsigned restart_waits() const { return restart_waits_; }
  void debug_start_multiball(bool released = false, bool mode6 = false,
                             int selected = 4);
  bool minigame_active() const { return minigame_active_; }
  bool minigame2_active() const {
#ifdef SLAM_MEAN_MINIGAME_LIFT
    return minigame_active_ && minigame_.image[0x3f3a4] == 2;
#else
    return false;
#endif
  }
#ifdef SLAM_MEAN_MINIGAME_LIFT
  const MeanMinigameLift &diagnostic_minigame_state() const { return minigame_; }
#endif
  unsigned minigame_starts() const { return minigame_starts_; }
  unsigned minigame_completions() const { return minigame_completions_; }
  const WindowsDmdPixels &minigame_pixels() const {
#ifdef SLAM_MEAN_MINIGAME_LIFT
    return minigame_.pixels;
#else
    static const WindowsDmdPixels empty{};
    return empty;
#endif
  }
  unsigned reward_requests() const { return reward_requests_; }
  unsigned reward_completions() const { return reward_completions_; }
  int selected_mode() const { return mode5_state_.field_43f1e6; }
  int table_mode() const { return capture_state_.table_mode; }
  unsigned releases() const { return releases_; }
  unsigned ball_number() const { return ball_number_; }
  unsigned pending_extra_ball_prizes() const {
    return static_cast<std::uint16_t>(capture_state_.field_43f1fa);
  }
  unsigned extra_ball_credits() const { return extra_balls_; }
  void debug_pit_stop_event(unsigned id) { apply_pit_stop(id); }
  void debug_stock_car_bumper(unsigned material) { apply_stock_car_bumper(material); }
  void debug_start_short_mode(bool stock, bool jackpot=false);
  void debug_left_progress(unsigned stage,unsigned letters,unsigned mode,bool reject);
  void debug_cliff_jump(unsigned previous, bool failure, bool reject, bool preview=false);
  void debug_speed_jackpot(unsigned locks, bool reject, bool preview=false);
  // Replay externally observed contact context, not fitted physics parameters.
  void set_original_contact_context(const std::vector<std::uint32_t> &poses,
                                    const std::vector<std::uint32_t> &globals);
  void set_launch(bool pressed) { launch_pressed_ = pressed; }
  std::uint16_t flipper_pose(unsigned index) const;
  unsigned events() const { return events_; }
  unsigned launches() const { return launches_; }
  void set_flippers(bool left, bool right);
  void press_plunger();
  bool mode_locked() const {return mode5_state_.field_43f384!=0;}
  void nudge(int horizontal, bool upward = false);
  const MeanNudge &nudge_state() const { return nudge_; }
  bool
  step(); // false: unsupported original branch or drain; never invent response.
  const MeanObject &ball() const { return pool_.objects[0]; }
  const MeanObject &ball(unsigned index) const {
    return pool_.objects.at(index);
  }
  unsigned ball_count() const { return pool_.count; }
  unsigned max_balls() const { return max_balls_; }
  const MeanGearStats &gear_stats() const {return gear_stats_;}
  unsigned gear_multiplier() const {return unsigned(target_reward_.field_player_12);}
  const std::array<std::uint8_t,3> &gear_lamps() const {return lamp_events_.field_43f1e8;}
  unsigned pending_upper_extra_balls() const {return unsigned(capture_state_.field_43f1fa);}
  const MeanChickenStats &chicken_stats() const {return chicken_stats_;}
  const MeanOffroadStats &offroad_stats() const {return offroad_stats_;}
  int offroad_stage() const {return mode5_state_.field_43f37e;}
  int offroad_ticks() const {return mode5_state_.field_43f376;}
  const MeanRallyStats &rally_stats() const {return rally_stats_;}
  int shared_mode_ticks() const {return mode5_state_.field_43f39c;}
  const MeanMonsterStats &monster_stats() const {return monster_stats_;}
  const MeanSpeedStats &speed_stats() const {return speed_stats_;}
  unsigned speed_letters() const {return unsigned(upper_state_.field_43f1f2);}
  std::array<std::int16_t,3> speed_lock_timers() const {return {mode5_state_.field_43f38e,mode5_state_.field_43f368,mode5_state_.field_43f36c};}
  unsigned mode6_starts() const { return mode6_starts_; }
  unsigned multiball_spawns() const { return multiball_spawns_; }
  const char *status() const { return status_; }
  unsigned collisions() const { return collisions_; }

private:
  MeanMode4IdleAssets mode4_idle_assets_;
  MeanMode4Phase1Assets mode4_phase1_assets_;
  MeanMainModeHudAssets main_mode_hud_assets_;
  MeanMainModeHud main_mode_hud_;
  bool main_mode_hud_visible_=false;
  MeanPlayerHudAssets player_hud_assets_;
  MeanPlayerHud player_hud_;
  bool player_hud_visible_=false;
  MeanIdleHudAssets idle_hud_assets_;
  MeanIdleHud idle_hud_;
  bool idle_hud_visible_=false;
  MeanMaterial5DisplayAssets material5_display_assets_;
  MeanSkillshotDisplayAssets skillshot_display_assets_;
  bool skillshot_display_visible_ = false;
  MeanMaterial5Display material5_display_;
  unsigned mean_display_sfx_cursor_ = 0;
  std::array<unsigned, 8> switch_reward_variants_{};
  unsigned pending_mode4_rewards_ = 0;
  unsigned mode4_starts_ = 0, mode4_completions_ = 0, state7_steps_ = 0;
  void apply_shared_reward(unsigned event_id, bool state_ready = false);
  void apply_pit_stop(unsigned event_id);
  void apply_stock_car_bumper(unsigned material);
  void finish_mode4(bool select_next);
  void load_mode4_fields();
  void step_mode4_display();
  void step_mode4_clock();
  void apply_left_progress();
  void apply_mode4_switch(unsigned layer,unsigned mask,std::int32_t x,std::int32_t y);
  void step_shared_display();
  void enter_minigame_display();
  void project_return_pass_fields();
  bool minigame2_goal_seen_=false;
  unsigned return_passes_=0, return_pass_awards_=0;
  bool request_material5_display(std::uint32_t callback, std::uint32_t score,
                                 bool save_page = false);
  unsigned switch_rewards_ = 0;
  unsigned side_extra_balls_ = 0;
  unsigned award_bank_starts_ = 0, award_bank_awards_ = 0;
  unsigned material5_hits_ = 0, material5_groups_ = 0;
  unsigned kickback_consumptions_ = 0;
  int lane_saver_frame_ = 0;
  unsigned lane_saver_patches_ = 0;
  bool retail_minigame_=false;
  unsigned minigame_steps_=0;
  std::vector<MeanAudioRequest> audio_requests_;
  bool start_minigame();
  bool start_minigame2();
  MeanMode4RightState mode4_right_;
  MeanRightGateState right_gate_;
  MeanPointForceData point_forces_;
  bool point_force_context_ = false, point_force_suppressed_ = false;
  unsigned point_force_updates_ = 0;
  unsigned right_cancellations_ = 0;
  unsigned right_arms_ = 0, right_markers_ = 0, right_captures_ = 0;
  void update_right_gate();
  bool step_minigame();
  void apply_capture_delay(bool accepted,const std::array<std::int32_t,5>&selectors,std::int32_t delay);
  bool step_impl();
  bool physics_step();
  bool contact_step();
  bool contact_step_impl(MeanContactTrace *trace);
  std::function<void(const MeanContactTrace&)> contact_observer_;
  std::function<void(const MeanPairTrace&)> pair_observer_;
  void sync_ball_reset_fields(bool load);
  void begin_bonus();
  bool step_bonus();
  void finish_turn();
  void rebuild_lamps();
  bool step_mode4_spawn();
  void collide_pair(unsigned, unsigned);
  bool switch_step();
  void configure_bits();
  MeanPitStopStats pit_stats_;
  MeanStockCarStats stock_stats_;
  MeanSpeedStats speed_stats_;
  MeanMonsterStats monster_stats_;
  MeanRallyStats rally_stats_;
  MeanOffroadStats offroad_stats_;
  MeanChickenStats chicken_stats_;
  MeanGearStats gear_stats_;
  MeanObject ball_, initial_ball_;
  MeanBallPool pool_;
  MeanMultiballReleaseState multiball_release_;
  unsigned current_ball_ = 0, max_balls_ = 1, multiball_spawns_ = 0;
  bool ball_drained_ = false;
  unsigned mode6_starts_ = 0;
  bool gameplay_ = false, continuous_play_ = false;
  bool endless_play_ = false, game_over_ = false;
  bool field_43d864_=false;
  MeanNudge nudge_;
  MeanNudgeTilt nudge_tilt_;
  unsigned nudge_ticks_=0;
  unsigned drains_ = 0, score_events_ = 0;
  MeanScore score_;
  MeanMaterialBundleState material_state_;
  MeanCaptureTickState capture_state_;
  MeanUpperCaptureState upper_state_;
  MeanRandomState random_state_;
  MeanMode5LeftState mode5_state_;
  std::array<std::array<std::uint8_t, 4>, 63> lamp_commands_{};
  std::array<bool, 63> lamp_on_{};
  std::array<int, 63> lamp_visible_{};
  std::array<unsigned, 63> lamp_updates_{};
  MeanLampEvents lamp_events_;
  MeanTopTargetReward target_reward_;
  MeanBallResetState ball_reset_state_;
  MeanBonusTurn bonus_turn_;
  MeanBonusDisplay bonus_display_;
  MeanBonusTableState bonus_table_;
  MeanBonusPixels bonus_font_;
  MeanBonusAnimation bonus_animation_;
  WindowsDmdPixels bonus_dmd_{};
  bool bonus_active_ = false;
  unsigned bonus_display_ticks_ = 0, bonus_starts_ = 0, bonus_completions_ = 0;
  unsigned bonus_awards_ = 0;
  unsigned mode5_awards_ = 0, ball_saves_ = 0;
  std::uint32_t last_bonus_ = 0;
  MeanLampModeInput lamp_mode_input_;
  std::uint32_t award_bank_054_ = 0;
  unsigned top_target_hits_ = 0, top_target_cycles_ = 0;
  MeanMode6SideState mode6_side_;
  bool mode6_display_pending_ = false;
  std::array<std::int32_t, 3> field_438afc_{};
  bool reward_display_pending_ = false;
  bool minigame_active_ = false, minigame_available_ = false;
  unsigned minigame_starts_ = 0, minigame_completions_ = 0;
#ifdef SLAM_MEAN_MINIGAME_LIFT
  MeanMinigameLift minigame_;
#ifdef SLAM_MEAN_BALL_PAIR_LIFT
  MeanMinigameLift ball_pair_;
#endif
  std::vector<std::uint8_t> minigame_initial_image_, minigame_initial_runtime_;
#endif
  unsigned reward_requests_ = 0, reward_completions_ = 0;
  unsigned mode_resets_ = 0;
  unsigned upper_captures_ = 0;
  unsigned captures_ = 0, releases_ = 0;
  std::array<MeanContactAnimation, 3> contact_animations_;
  unsigned display_ticks_ = 0;
  std::int32_t field_43e79c_ = 0;
  unsigned restart_initializations_ = 0, restart_waits_ = 0;
  std::uint16_t ball_number_ = 1, extra_balls_ = 0;
  unsigned events_ = 0;
  std::uint32_t dat_base_ = 0;
  bool launch_pressed_ = false;
  unsigned launches_ = 0;
#ifdef SLAM_MEAN_FLIPPER_LIFT
  FlipperLift flippers_;
#endif
  MeanLookup lookup_;
  MeanCollisionBits bits_;
  #ifdef SLAM_MEAN_NORMAL_LIFT
  MeanNormalLift normal_;
  #endif
  bool input_enabled_ = false, left_ = false, right_ = false;
  unsigned collisions_ = 0;
  const char *status_ = "running supported original slice";
};
} // namespace slam
