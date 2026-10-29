#include "frontend/gamepad_overlay.h"
#include "dmd/mean_dmd_palette.h"
#include "frontend/port_options.h"
#ifdef SLAM_PIRATE_SESSION
#include "frontend/pirate_play.h"
#endif
#include "frontend/mean_highscores.h"
#include "renderer/display_layout.h"
#include "renderer/presentation.h"
#include <algorithm>
#include <map>
#include <cctype>
#include <fstream>
#include <nlohmann/json.hpp>
#include "assets/table_profile.h"
#include "assets/ball_mask.h"
#include "assets/mean_flippers.h"
#include "assets/mean_lamps.h"
#include "assets/mean_score_font.h"
#include "assets/windows_table.h"
#include "collision/mean_bitmap.h"
#include "physics/ball_trace.h"
#include "physics/mean_simulation.h"
#include "renderer/ball_display.h"
#include "renderer/mean_camera.h"
#include "core/mean_diagnostic_input.h"
#include <SDL3/SDL.h>
#include "frontend/window_mode.h"
#ifdef SLAM_AUDIO_XMP
#include "audio/mean_sound_assets.h"
#include "audio/native_audio.h"
#include <fstream>
#include <iterator>
#endif
#include <algorithm>
#include <map>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

int main(int argc, char **argv) {
#ifdef SLAM_PIRATE_SESSION
  if(argc>=3&&std::string(argv[2])=="--pirate-play")return slam::run_pirate_play(argc,argv);
#endif
  if (argc < 2) {
    std::cerr
        << "Usage: slamview TABLE.DAT [--amiga] [--export image.bmp] "
           "[--frames N] [--capture frame.bmp] [--trace JSON] "
           "[--visual-preset 0..5] [--menu-category 0..4] [--preview-size WIDTHxHEIGHT] [--require-gpu] [--presentation-report JSON] "
           "[--simulate PREPARED | --play "
           "PREPARED] [--collision] [--minigame-preview] [--minigame-win-preview] [--retail-minigame | --demo-minigame] "
           "[--multiball-preview] [--mode6-preview] "
           "[--game-over-preview] [--bonus-preview] [--music MODULE] "
           "[--short-mode-preview pit-stop|pit-jackpot|stock-car] [--material5-preview] [--award-bank-preview] "
           "[--shared-reward-preview] [--rally-reward-preview] [--mode4-upper-preview] [--extra-ball-preview] [--switch-reward-preview] [--music-order "
           "N] [--no-audio]\n"
           "Up/Down or mouse wheel: scroll; Home/End: table ends; "
           "Enter: launch; Shift: flippers; R: reset; Alt/Space: nudge; P: pause; "
           "Escape: options (native play) / quit (viewer)\n";
    return 2;
  }
  SDL_Window *window = nullptr;
  SDL_Renderer *renderer = nullptr;
  SDL_Texture *texture = nullptr;
  SDL_Texture *table_target = nullptr;
  SDL_Texture *dmd_target = nullptr;
  SDL_Texture *collision_texture = nullptr;
  SDL_Texture *ball_texture = nullptr;
  SDL_Texture *score_texture = nullptr;
  std::vector<SDL_Texture *> flipper_textures;
  std::vector<SDL_Texture *> lamp_textures;
  try {
    std::string output, capture, frontend_acceptance;
    int frames = 0, music_order = 0;
    int visual_preset=-1,menu_category=0,preview_width=0,preview_height=0;
    bool require_gpu=false;
    std::string presentation_report;
    bool options_preview=false, menu_preview=false, lane_saver_preview=false, skillshot_preview=false, mode_total_preview=false;
    std::string music_path;
    bool no_audio = false, audio_muted = false;
    bool amiga = false;
    bool collision = false, start_ready = false, mini_preview = false,
         multiball_preview = false, mode6_preview = false,
         mode4_preview = false, minigame2_preview = false,
         point_force_preview = false, ball_occlusion_preview = false, game_over_preview = false,
         bonus_preview = false, material5_preview = false,
         award_bank_preview = false, extra_ball_preview = false,
         switch_reward_preview = false, shared_reward_preview = false, rally_reward_preview = false, mode4_upper_preview = false;
    bool nudge_warning_preview=false, tilt_release_preview=false, mode5_award_preview=false;
    bool return_pass_preview = false, minigame_result_preview=false, minigame_win_preview=false, retail_minigame=false;
    std::string minigame2_result_preview, short_mode_preview;
    unsigned realtime_steps=0;bool session_exclusive=false;std::string session_replay,session_output;
    std::string trace_path, prepared_path, natural_mode_preview, idle_hud_preview, main_mode_hud_preview, player_hud_preview, overheat_preview, gear_cap_preview;
    unsigned skillshot_reward_preview=0;
    for (int i = 2; i < argc; ++i) {
      const std::string option = argv[i];
      if(option=="--realtime-steps"&&i+1<argc){realtime_steps=std::stoul(argv[++i]);if(!realtime_steps||realtime_steps>100000)throw std::runtime_error("Invalid realtime step count");}
      else if(option=="--replay"&&i+1<argc)session_replay=argv[++i];
      else if(option=="--replay-only")session_exclusive=true;
      else if(option=="--trace-output"&&i+1<argc)session_output=argv[++i];
      else if(option=="--visual-preset" && i+1<argc){visual_preset=std::stoi(argv[++i]);if(visual_preset<0 || visual_preset>5)throw std::runtime_error("Preset must be 0..5");options_preview=true;}
      else if(option=="--menu-category" && i+1<argc){menu_category=std::stoi(argv[++i]);if(menu_category<0 || menu_category>4)throw std::runtime_error("Category must be 0..4");menu_preview=true;options_preview=true;}
      else if(option=="--preview-size" && i+1<argc) {
        const std::string size=argv[++i];const auto split=size.find('x');
        if(split==std::string::npos)throw std::runtime_error("Preview size requires WIDTHxHEIGHT");
        preview_width=std::stoi(size.substr(0,split));preview_height=std::stoi(size.substr(split+1));
        if(preview_width<320 || preview_height<240 || preview_width>7680 || preview_height>4320)throw std::runtime_error("Preview size out of range");
        options_preview=true;
      }
      else if(option=="--require-gpu")require_gpu=true;
      else if(option=="--presentation-report" && i+1<argc)presentation_report=argv[++i];
      else if (option == "--skillshot-reward-preview" && i+1<argc) {
        skillshot_reward_preview=std::stoul(argv[++i]);
        if(skillshot_reward_preview<1 || skillshot_reward_preview>7)throw std::runtime_error("Skillshot reward preview requires1..7");
      }
      else if (option == "--gear-cap-preview" && i+1<argc) gear_cap_preview=argv[++i];
      else if (option == "--overheat-preview" && i+1<argc) overheat_preview=argv[++i];
      else if (option == "--player-hud-preview" && i+1<argc) player_hud_preview=argv[++i];
      else if (option == "--main-mode-hud-preview" && i+1<argc) main_mode_hud_preview=argv[++i];
      else if (option == "--idle-hud-preview" && i+1<argc) idle_hud_preview=argv[++i];
      else if (option == "--mode-total-preview") mode_total_preview=true;
      else if (option == "--frontend-acceptance" && i+1<argc) {
        frontend_acceptance=argv[++i];options_preview=true;game_over_preview=true;
      }
      else if (option == "--skillshot-choice-preview") player_hud_preview="choices";
      else if (option == "--skillshot-preview") skillshot_preview=true;
      else if (option == "--lane-saver-preview") lane_saver_preview=true;
      else if (option == "--music" && i + 1 < argc)
        music_path = argv[++i];
      else if (option == "--music-order" && i + 1 < argc) {
        std::size_t end = 0;
        const std::string value = argv[++i];
        music_order = std::stoi(value, &end);
        if (end != value.size() || music_order < 0)
          throw std::runtime_error("Music order must be nonnegative");
      } else if (option == "--no-audio")
        no_audio = true;
      else if (option == "--trace" && i + 1 < argc)
        trace_path = argv[++i];
      else if (option == "--play" && i + 1 < argc) {
        prepared_path = argv[++i];
        start_ready = true;
      } else if (option == "--simulate" && i + 1 < argc)
        prepared_path = argv[++i];
      else if(option=="--tilt-release-preview") tilt_release_preview=true;
      else if(option=="--menu-preview") {options_preview=true;menu_preview=true;}
      else if(option=="--options-preview") options_preview=true;
      else if(option=="--short-mode-preview" && i+1<argc) {
        short_mode_preview=argv[++i];
        if(short_mode_preview!="pit-stop" && short_mode_preview!="pit-jackpot" && short_mode_preview!="stock-car" && short_mode_preview!="speed-jackpot" && short_mode_preview!="cliff-jumper")
          throw std::runtime_error("Short mode preview: pit-stop, pit-jackpot, stock-car, speed-jackpot or cliff-jumper");
      }
      else if(option=="--mode5-award-preview") mode5_award_preview=true;
      else if(option=="--nudge-warning-preview") nudge_warning_preview=true;
      else if (option == "--natural-mode-preview" && i + 1 < argc) {
        natural_mode_preview = argv[++i];
        if(natural_mode_preview != "minigame2" && natural_mode_preview != "minigame" && natural_mode_preview != "multiball" && natural_mode_preview != "upper" && natural_mode_preview != "upper-mode" && natural_mode_preview != "cliff" && natural_mode_preview != "kickstart" && natural_mode_preview != "pit-stop" && natural_mode_preview != "stock-car" && natural_mode_preview != "speed" && natural_mode_preview != "monster" && natural_mode_preview != "rally" && natural_mode_preview != "offroad" && natural_mode_preview != "chicken" && natural_mode_preview != "gears" && natural_mode_preview != "kickback" && natural_mode_preview != "laps" && natural_mode_preview != "goals" && natural_mode_preview != "skull")
          throw std::runtime_error("Natural mode preview: minigame, minigame2, multiball, upper, upper-mode, cliff, kickstart, pit-stop, stock-car, speed, monster, rally, offroad, chicken, gears, kickback, laps, goals or skull");
      }
      else if (option == "--bonus-preview")
        bonus_preview = true;
      else if (option == "--minigame2-result-preview" && i+1<argc) {
        minigame2_result_preview=argv[++i];
        if(minigame2_result_preview!="success" && minigame2_result_preview!="failure")
          throw std::runtime_error("Second minigame result: success or failure");
      }
      else if (option == "--return-pass-preview")
        return_pass_preview = true;
      else if (option == "--switch-reward-preview")
        switch_reward_preview = true;
      else if (option == "--extra-ball-preview")
        extra_ball_preview = true;
      else if (option == "--award-bank-preview")
        award_bank_preview = true;
      else if (option == "--material5-preview")
        material5_preview = true;
      else if (option == "--game-over-preview")
        game_over_preview = true;
      else if (option == "--minigame2-preview")
        minigame2_preview = true;
      else if (option == "--mode4-upper-preview")
        mode4_upper_preview = true;
      else if (option == "--rally-reward-preview")
        rally_reward_preview = true;
      else if (option == "--shared-reward-preview")
        shared_reward_preview = true;
      else if (option == "--point-force-preview")
        point_force_preview = true;
      else if (option == "--ball-occlusion-preview")
        ball_occlusion_preview = true;
      else if (option == "--mode4-preview")
        mode4_preview = true;
      else if (option == "--mode6-preview")
        mode6_preview = true;
      else if (option == "--multiball-preview")
        multiball_preview = true;
      else if (option == "--demo-minigame")
        retail_minigame=false;
      else if (option == "--retail-minigame")
        retail_minigame=true;
      else if (option == "--minigame-win-preview")
        minigame_win_preview=true;
      else if (option == "--minigame-result-preview")
        minigame_result_preview=true;
      else if (option == "--minigame-preview")
        mini_preview = true;
      else if (option == "--collision")
        collision = true;
      else if (option == "--amiga")
        amiga = true;
      else if (option == "--capture" && i + 1 < argc)
        capture = argv[++i];
      else if (option == "--export" && i + 1 < argc)
        output = argv[++i];
      else if (option == "--frames" && i + 1 < argc) {
        std::size_t end = 0;
        const std::string value = argv[++i];
        frames = std::stoi(value, &end);
        if (end != value.size() || frames <= 0)
          throw std::runtime_error("Frames must be a positive integer");
      } else
        throw std::runtime_error("Unknown/incomplete option: " + option);
    }
    if (!capture.empty() && frames == 0 && !realtime_steps)
      throw std::runtime_error("--capture requires --frames");
    if (!prepared_path.empty() && (trace_path.empty() || amiga))
      throw std::runtime_error(
          "--simulate requires --trace initial state and Windows DAT");
    const auto image = amiga ? slam::load_amiga_table(argv[1])
                             : slam::load_windows_table(argv[1]);
    if (!output.empty()) {
      SDL_Surface *surface = SDL_CreateSurfaceFrom(
          image.width, image.height, SDL_PIXELFORMAT_RGBA32,
          const_cast<std::uint8_t *>(image.rgba.data()), image.width * 4);
      if (!surface)
        throw std::runtime_error(SDL_GetError());
      const bool saved = SDL_SaveBMP(surface, output.c_str());
      SDL_DestroySurface(surface);
      if (!saved)
        throw std::runtime_error(SDL_GetError());
      std::cout << "Exported " << image.width << 'x' << image.height
                << " table to " << output << '\n';
      if (frames == 0)
        return 0;
    }
    if (!SDL_Init(SDL_INIT_VIDEO))
      throw std::runtime_error(SDL_GetError());
    window=SDL_CreateWindow("Slamtilt - Reborn | Mean Machines",640,800,SDL_WINDOW_RESIZABLE|SDL_WINDOW_HIGH_PIXEL_DENSITY);
    if(!window)throw std::runtime_error(SDL_GetError());
    renderer=slam::create_presentation_renderer(window,options_preview || (frames==0 && !prepared_path.empty()));
    if(!renderer)throw std::runtime_error(SDL_GetError());
    slam::Presentation presentation(renderer);
    if(require_gpu && !presentation.available())throw std::runtime_error(presentation.status());
    slam::GamepadInput gamepad;
    PortOptions options;
    const bool new_layout=options_preview || (frames==0 && !prepared_path.empty());
    options.load(new_layout && !options_preview);
    options.shaders_available=presentation.available();options.shader_status=presentation.status();
    if(visual_preset>=0)slam::visual_preset(options.settings.visual,visual_preset);
    options.select_category(menu_category);
    if(preview_width){options.settings.window_width=preview_width;options.settings.window_height=preview_height;}
    slam::infer_asset_source(std::filesystem::path(argv[1]).parent_path());
    MeanHighscores highscores;highscores.load(new_layout && !options_preview);
    if(options_preview) options.settings.fullscreen=false;
    if(new_layout) {SDL_SetWindowMinimumSize(window,320,240);SDL_SetWindowSize(window,options.settings.window_width,options.settings.window_height);}
    const auto dmd_palette=slam::mean_dmd_original_palette(image.palette_rgba.data(),image.palette_rgba.size());
    std::vector<SDL_DisplayMode> display_modes;
    int mode_count=0;
    if(auto **modes=SDL_GetFullscreenDisplayModes(SDL_GetDisplayForWindow(window),&mode_count)) {
      for(int i=0;i<mode_count;++i) {
        display_modes.push_back(*modes[i]);
        const SDL_Point r{modes[i]->w,modes[i]->h};
        if(std::none_of(options.exclusive_resolutions.begin(),options.exclusive_resolutions.end(),[&](const SDL_Point&p){return p.x==r.x && p.y==r.y;}))options.exclusive_resolutions.push_back(r);
      }
      SDL_free(modes);
    }
    auto set_window_mode=[&](const PortSettings &s) {
      const SDL_DisplayMode *mode=nullptr;
      if(s.fullscreen && s.fullscreen_mode==1) {
        for(const auto &m:display_modes)if(m.w==s.window_width && m.h==s.window_height && (!mode || m.refresh_rate>mode->refresh_rate))mode=&m;
        if(!mode){options.error="Selected exclusive resolution unavailable";return false;}
      }
      return slam::apply_window_mode(window,s.fullscreen,mode,s.window_width,s.window_height);
    };
    PortSettings applied=options.settings;
    if(new_layout && !set_window_mode(applied)) {
      options.error=SDL_GetError();options.settings.fullscreen=false;options.settings.fullscreen_mode=0;
      applied=options.settings;set_window_mode(applied);
    }
    if(new_layout) {
      table_target=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_TARGET,320,400);
      if(!table_target) throw std::runtime_error(SDL_GetError());
      dmd_target=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_TARGET,96,20);
      if(!dmd_target)throw std::runtime_error(SDL_GetError());
      SDL_SetTextureScaleMode(dmd_target,SDL_SCALEMODE_NEAREST);
    }
    SDL_SetRenderVSync(renderer, frames&&!session_replay.empty()?0:1);
    if (!SDL_SetRenderLogicalPresentation(renderer, 320, 400,
                                          new_layout?SDL_LOGICAL_PRESENTATION_DISABLED:SDL_LOGICAL_PRESENTATION_LETTERBOX))
      throw std::runtime_error(SDL_GetError());
    texture =
        SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                          SDL_TEXTUREACCESS_STATIC, image.width, image.height);
    if (!texture ||
        !SDL_UpdateTexture(texture, nullptr, image.rgba.data(),
                           image.width * 4) ||
        !SDL_SetTextureScaleMode(texture, SDL_SCALEMODE_NEAREST))
      throw std::runtime_error(SDL_GetError());
    if(session_exclusive&&session_replay.empty())throw std::runtime_error("--replay-only requires --replay");
    const auto trace = trace_path.empty() ? std::vector<slam::BallState>{}
                                          : slam::load_ball_trace(trace_path);
    std::unique_ptr<slam::MeanSimulation> simulation;
    if (!prepared_path.empty())
      simulation = std::make_unique<slam::MeanSimulation>(
          argv[1], prepared_path, trace_path);
    if(simulation) simulation->set_retail_minigame(retail_minigame);
    if (simulation && start_ready)
      simulation->reset();
    if (material5_preview || award_bank_preview || extra_ball_preview ||
        switch_reward_preview) {
      if (!simulation)
        throw std::runtime_error("Material5 preview requires Mean simulation");
      simulation->reset();
      simulation->set_continuous_play(true);
      simulation->set_endless_play(true);
      bool reached = false;
      for (unsigned i = 0; i < ((award_bank_preview || extra_ball_preview ||
                                 switch_reward_preview)
                                    ? 800000u
                                    : 400000u);
           ++i) {
        simulation->set_launch(true);
        simulation->set_flippers(i % 100 < 40, i % 140 < 60);
        if (!simulation->step())
          throw std::runtime_error(simulation->status());
        if (simulation->material5_display_callback() ==
                (switch_reward_preview ? 0x40fdecu
                 : extra_ball_preview  ? 0x410e4cu
                 : award_bank_preview  ? 0x4107c8u
                                       : 0x413958u) &&
            simulation->material5_display_counter() ==
                (switch_reward_preview ? 56u
                 : extra_ball_preview  ? 8u
                                       : 7u)) {
          reached = true;
          break;
        }
      }
      simulation->set_endless_play(false);
      if (!reached)
        throw std::runtime_error(
            "Requested target preview did not reach its DMD callback");
    }
    if (bonus_preview) {
      if (!simulation)
        throw std::runtime_error("Bonus preview requires Mean simulation");
      simulation->reset();
      simulation->set_continuous_play(true);
      for (unsigned i = 0; i < 100000; ++i) {
        simulation->set_launch(true);
        simulation->set_flippers(i % 100 < 40, i % 140 < 60);
        if (!simulation->step())
          throw std::runtime_error(simulation->status());
        if (simulation->bonus_active() && simulation->bonus_phase() == 2) {
          for (unsigned j = 0; j < 32; ++j)
            simulation->step();
          break;
        }
      }
      if (!simulation->bonus_active())
        throw std::runtime_error("Bonus preview did not reach phase");
    }
    if (game_over_preview) {
      if (!simulation)
        throw std::runtime_error("Game-over preview requires Mean simulation");
      simulation->reset();
      simulation->set_continuous_play(true);
      for (unsigned i = 0; i < 100000 && !simulation->game_over(); ++i) {
        simulation->set_launch(true);
        simulation->set_flippers(i % 100 < 40, i % 140 < 60);
        if (!simulation->step() && !simulation->game_over())
          throw std::runtime_error(simulation->status());
      }
      if (!simulation->game_over())
        throw std::runtime_error("Game-over preview did not finish");
    }
    if (mode4_upper_preview) {
      if (!simulation) throw std::runtime_error("Mean simulation required");
      simulation->debug_start_mode4_upper();
      for (unsigned i = 0; i < 160; ++i)
        if (!simulation->step()) throw std::runtime_error(simulation->status());
      if (simulation->upper_captures() != 1 || simulation->releases() < 1)
        throw std::runtime_error("Mode4 upper capture did not release");
    }
    if (shared_reward_preview || rally_reward_preview) {
      if (!simulation) throw std::runtime_error("Mean simulation required");
      simulation->debug_start_shared_mode(rally_reward_preview ? 2 : 1);
      simulation->debug_place_shared_switch(rally_reward_preview ? simulation->shared_target() : 1);
      if (!simulation->step() || simulation->material5_display_callback() != (rally_reward_preview ? 0x411c60u : 0x412fa8u))
        throw std::runtime_error("Original shared reward did not start");
      for (unsigned i = 0; i < 40; ++i)
        if (!simulation->step()) throw std::runtime_error(simulation->status());
    }
    if(skillshot_reward_preview) {
      if(!simulation)throw std::runtime_error("Mean simulation required");
      simulation->set_retail_minigame(true);simulation->reset();
      simulation->set_continuous_play(true);simulation->set_endless_play(false);
      const auto path=std::filesystem::path(SLAM_MEAN_SKILLSHOT_REWARDS_DIR)/
          ("mean-skillshot-reward-"+std::to_string(skillshot_reward_preview)+"-input.json");
      nlohmann::json fixture;std::ifstream(path)>>fixture;
      bool found=false;unsigned tick=0;
      for(const auto &run:fixture.at("actions_rle")) {
        const unsigned a=run.at("actions");
        for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i) {
          simulation->set_launch(a&8);simulation->set_flippers(a&1,a&2);
          if(a&4)simulation->press_plunger();
          if(a&16)simulation->nudge(1,false);
          if(a&64)simulation->nudge(-1,false);
          if(a&32)simulation->nudge(0,true);
          if(!simulation->step())throw std::runtime_error(simulation->status());
          ++tick;
          if(tick>=fixture.at("award_tick").get<unsigned>() &&
             simulation->material5_display_callback()==0x40fdec &&
             simulation->material5_display_counter()>=72 &&
             std::any_of(simulation->material5_pixels().begin(),simulation->material5_pixels().end(),[](auto v){return v!=0;})) {found=true;break;}
        }
        if(found)break;
      }
      if(!found)throw std::runtime_error("Natural Skillshot reward display missing");
      simulation->set_flippers(false,false);
    }
    if(!gear_cap_preview.empty()) {
      const auto &name=gear_cap_preview;
      if(!simulation || (name!="cap" && name!="bonus"))throw std::runtime_error("Unknown Mean gear cap preview");
      simulation->set_retail_minigame(true);simulation->reset();
      simulation->set_continuous_play(true);simulation->set_endless_play(false);
      nlohmann::json fixture;std::ifstream(SLAM_MEAN_GEAR_CAP_TRACE_PATH)>>fixture;
      bool found=false;
      for(const auto &run:fixture.at("actions_rle")) {
        const unsigned a=run.at("actions");
        for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i) {
          simulation->set_launch(a&8);simulation->set_flippers(a&1,a&2);
          if(a&4)simulation->press_plunger();
          if(a&16)simulation->nudge(1,false);
          if(a&64)simulation->nudge(-1,false);
          if(a&32)simulation->nudge(0,true);
          if(!simulation->step())throw std::runtime_error(simulation->status());
          if(simulation->gear_stats().capped_awards==1 && simulation->gear_multiplier()==5 &&
             ((name=="cap" && ((simulation->idle_hud_visible() && simulation->idle_hud().score>=238041760) ||
                (simulation->main_mode_hud_visible() && simulation->main_mode_hud().score>=238041760))) ||
              (name=="bonus" && simulation->bonus_active() && simulation->last_bonus()==70000000 &&
               simulation->bonus_phase()==2 && simulation->bonus_display_ticks()>=150))) {found=true;break;}
        }
        if(found)break;
      }
      if(!found)throw std::runtime_error("Natural capped-gear display missing");
      simulation->set_flippers(false,false);
    }
    if(!overheat_preview.empty()) {
      const auto &name=overheat_preview;
      if(!simulation || (name!="collect" && name!="early" && name!="late" && name!="timeout"))
        throw std::runtime_error("Unknown Mean Overheat preview");
      simulation->set_retail_minigame(true);simulation->reset();
      simulation->set_continuous_play(true);simulation->set_endless_play(false);
      nlohmann::json fixture;std::ifstream(name=="collect"?SLAM_MEAN_OVERHEAT_TRACE_PATH:SLAM_MEAN_OVERHEAT_TIMEOUT_PATH)>>fixture;
      bool found=false;
      for(const auto &run:fixture.at("actions_rle")) {
        const unsigned a=run.at("actions");
        for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i) {
          simulation->set_launch(a&8);simulation->set_flippers(a&1,a&2);
          if(a&4)simulation->press_plunger();
          if(a&16)simulation->nudge(1,false);
          if(a&64)simulation->nudge(-1,false);
          if(a&32)simulation->nudge(0,true);
          if(!simulation->step())throw std::runtime_error(simulation->status());
          const auto cb=simulation->material5_display_callback(),counter=simulation->material5_display_counter();
          const auto &h=simulation->idle_hud();
          if((name=="collect" && cb==0x41062c && counter>=58 &&
              std::any_of(simulation->material5_pixels().begin(),simulation->material5_pixels().end(),[](auto v){return v!=0;})) ||
             (name=="early" && simulation->idle_hud_visible() && h.field_37a>3000) ||
             (name=="late" && simulation->idle_hud_visible() && h.field_37a>=0 && h.field_37a<=3000) ||
             (name=="timeout" && cb==0x410504 && counter>=2)) {found=true;break;}
        }
        if(found)break;
      }
      if(!found)throw std::runtime_error("Natural Overheat display missing");
      simulation->set_flippers(false,false);
    }
    if(!player_hud_preview.empty()) {
      const auto &name=player_hud_preview;
      if(!simulation || (name!="intro" && name!="choices" && name!="score" && name!="extra"))
        throw std::runtime_error("Unknown Mean player HUD preview");
      simulation->set_retail_minigame(true);simulation->reset();
      simulation->set_continuous_play(true);simulation->set_endless_play(false);
      if(name=="extra") {
        nlohmann::json fixture;std::ifstream(SLAM_MEAN_GOAL_LADDER_TRACE_PATH)>>fixture;
        bool earned=false;
        for(const auto &run:fixture.at("actions_rle")) {
          const unsigned a=run.at("actions");
          for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i) {
            simulation->set_launch(a&8);simulation->set_flippers(a&1,a&2);
            if(a&4)simulation->press_plunger();
            if(a&16)simulation->nudge(1,false);
            if(a&64)simulation->nudge(-1,false);
            if(a&32)simulation->nudge(0,true);
            if(!simulation->step())throw std::runtime_error(simulation->status());
            if(simulation->table_mode()==1 && simulation->player_hud().field_engine_60) {earned=true;break;}
          }
          if(earned)break;
        }
        simulation->set_launch(true);simulation->set_flippers(false,false);
        for(unsigned tail=0;!earned && tail<150000 && !simulation->game_over();++tail) {
          if(!simulation->step() && !simulation->game_over())throw std::runtime_error(simulation->status());
          earned=simulation->table_mode()==1 && simulation->player_hud().field_engine_60;
        }
        if(!earned)throw std::runtime_error("Natural extra turn missing");
      }
      simulation->set_launch(false);simulation->set_flippers(false,false);
      bool found=false;
      for(unsigned i=0;i<1200;++i) {
        if(!simulation->step())throw std::runtime_error(simulation->status());
        if(!simulation->player_hud_visible())continue;
        const auto &h=simulation->player_hud();
        const auto phase=h.counter&127u;
        if((name=="intro" && h.field_engine_5c) ||
           (name=="choices" && !h.field_engine_5c && h.counter && phase<=64 && (h.counter&2)) ||
           (name=="score" && !h.field_engine_5c && phase>64) ||
           (name=="extra" && h.field_engine_60 && h.field_360<=80 && h.field_360>=0 &&
            std::any_of(h.pixels.begin(),h.pixels.end(),[](auto pixel){return pixel!=0;}))) {found=true;break;}
      }
      if(!found)throw std::runtime_error("Natural player HUD page missing");
    }
    if(!main_mode_hud_preview.empty()) {
      const auto &name=main_mode_hud_preview;
      if(!simulation || (name!="chicken" && name!="monster" && name!="rally" && name!="offroad" && name!="speed"))
        throw std::runtime_error("Unknown Mean main-mode HUD preview");
      simulation->set_retail_minigame(true);simulation->reset();
      simulation->set_continuous_play(true);simulation->set_endless_play(false);
      nlohmann::json fixture;
      std::ifstream(name=="chicken"?SLAM_MEAN_CHICKEN_TRACE_PATH:name=="monster"?SLAM_MEAN_MONSTER_TRACE_PATH:name=="rally"?SLAM_MEAN_RALLY_TRACE_PATH:name=="offroad"?SLAM_MEAN_OFFROAD_TRACE_PATH:SLAM_MEAN_SPEED_TRACE_PATH)>>fixture;
      bool found=false;
      for(const auto &run:fixture.at("actions_rle")) {
        const unsigned a=run.at("actions");
        for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i) {
          simulation->set_launch(a&8);simulation->set_flippers(a&1,a&2);
          if(a&4)simulation->press_plunger();
          if(a&16)simulation->nudge(1,false);
          if(a&64)simulation->nudge(-1,false);
          if(a&32)simulation->nudge(0,true);
          if(!simulation->step())throw std::runtime_error(simulation->status());
          if(simulation->main_mode_hud_visible()) {
            const auto &h=simulation->main_mode_hud();
            const unsigned selected=name=="chicken"?0:name=="monster"?1:name=="rally"?2:4;
            if((name=="speed" && h.mode==6) || (name!="speed" && h.mode==5 && h.selected==selected)) {
              // Include the actual blinking direction arrow in Rally capture.
              if(name!="rally" || ((h.counter-1)&8)) {found=true;break;}
            }
          }
        }
        if(found)break;
      }
      if(!found)throw std::runtime_error("Natural main-mode HUD not reached");
      simulation->set_flippers(false,false);
    }
    if(!idle_hud_preview.empty()) {
      if(!simulation || (idle_hud_preview!="score" && idle_hud_preview!="pit-stop" && idle_hud_preview!="bank"))
        throw std::runtime_error("Mean idle HUD preview requires score, pit-stop or bank");
      simulation->reset();simulation->set_continuous_play(true);simulation->set_endless_play(false);
      nlohmann::json fixture;std::ifstream(idle_hud_preview=="bank"?SLAM_MEAN_OVERHEAT_TIMEOUT_PATH:SLAM_MEAN_PIT_TRACE_PATH)>>fixture;
      bool found=false;
      for(const auto &run:fixture.at("actions_rle")) {
        const unsigned a=run.at("actions");
        for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i) {
          simulation->set_launch(a&8);simulation->set_flippers(a&1,a&2);
          if(a&4)simulation->press_plunger();
          if(a&16)simulation->nudge(1,false);
          if(a&64)simulation->nudge(-1,false);
          if(a&32)simulation->nudge(0,true);
          if(!simulation->step())throw std::runtime_error(simulation->status());
          if(simulation->idle_hud_visible()) {
            const auto &h=simulation->idle_hud();
            const auto phase=(h.counter-1)&127u;
            const bool pit=h.field_398>=0 && (h.field_37a>=0 ? phase<64 : phase<80);
            const std::string page=pit?"pit-stop":h.field_37a>=0?"bank":"score";
            if(page==idle_hud_preview) {found=true;break;}
          }
        }
        if(found)break;
      }
      if(!found)throw std::runtime_error("Natural idle HUD page not reached");
      simulation->set_flippers(false,false);
    }
    if(mode_total_preview) {
      if(!simulation)throw std::runtime_error("Mean simulation required");
      simulation->reset();simulation->set_continuous_play(true);simulation->set_endless_play(false);
      nlohmann::json fixture;std::ifstream(SLAM_MEAN_COMBINED_MODES_TRACE_PATH)>>fixture;
      bool found=false;
      for(const auto&run:fixture.at("actions_rle")) {
        const unsigned a=run.at("actions");
        for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i) {
          simulation->set_launch(a&8);simulation->set_flippers(a&1,a&2);
          if(a&4)simulation->press_plunger();
          if(a&16)simulation->nudge(1,false);
          if(a&64)simulation->nudge(-1,false);
          if(a&32)simulation->nudge(0,true);
          if(!simulation->step())throw std::runtime_error(simulation->status());
          if(simulation->material5_display_callback()==0x410c8c && simulation->material5_display_counter()>=1){found=true;break;}
        }
        if(found)break;
      }
      if(!found || simulation->phase1_award_total()!=140208000)
        throw std::runtime_error("Natural mode-total page missing");
      simulation->set_flippers(false,false);
    }
    if (skillshot_preview) {
      if (!simulation) throw std::runtime_error("Mean simulation required");
      simulation->reset();
      simulation->set_continuous_play(true);
      simulation->set_endless_play(false);
      nlohmann::json fixture;
      std::ifstream(SLAM_MEAN_SKILLSHOT_TRACE_PATH) >> fixture;
      const unsigned target_ticks=600;
      unsigned ticks=0;
      for (const auto &run : fixture.at("actions_rle")) {
        const unsigned actions=run.at("actions");
        for (unsigned i=0;i<run.at("ticks").get<unsigned>() && ticks<target_ticks;++i) {
          simulation->set_launch(actions&8);
          simulation->set_flippers(actions&1,actions&2);
          if(actions&4) simulation->press_plunger();
          if(actions&16) simulation->nudge(1,false);
          if(actions&64) simulation->nudge(-1,false);
          if(actions&32) simulation->nudge(0,true);
          if(!simulation->step()) throw std::runtime_error(simulation->status());
          simulation->take_audio_requests();
          ++ticks;
        }
        if(ticks==target_ticks) break;
      }
      const auto &skill_fields=simulation->shared_raw_state().fields;
      const bool selection_locked=skill_fields[0x35c] || skill_fields[0x35d];
      if(ticks!=target_ticks || !simulation->material5_display_active() ||
         !selection_locked ||
         simulation->material5_display_callback())
        throw std::runtime_error("Natural Skillshot idle display missing");
      simulation->set_flippers(false,false);
    }
    const bool scripted_natural_preview = natural_mode_preview=="kickstart" || natural_mode_preview=="pit-stop" || natural_mode_preview=="stock-car" || natural_mode_preview=="speed" || natural_mode_preview=="monster" || natural_mode_preview=="rally" || natural_mode_preview=="offroad" || natural_mode_preview=="chicken" || natural_mode_preview=="gears" || natural_mode_preview=="kickback" || natural_mode_preview=="laps" || natural_mode_preview=="goals" || natural_mode_preview=="skull" || natural_mode_preview=="upper-mode" || natural_mode_preview=="multiball";
    if(natural_mode_preview=="upper-mode" || natural_mode_preview=="multiball") {
      if(!simulation) throw std::runtime_error("Mean simulation required");
      const bool eight=natural_mode_preview=="multiball";
      simulation->reset();simulation->set_continuous_play(true);
      simulation->set_endless_play(false);
      nlohmann::json fixture;
      std::ifstream(eight?SLAM_MEAN_SPEED_TRACE_PATH:SLAM_MEAN_MONSTER_TRACE_PATH)>>fixture;
      const auto target=[&] {
        if(eight) return simulation->ball_count()==8 && simulation->table_mode()==6;
        const auto cb=simulation->material5_display_callback();
        return simulation->table_mode()==5 &&
          (cb==0x412d24 || cb==0x411f10 || cb==0x412af8 || cb==0x412c58);
      };
      bool reached=false;unsigned remaining=eight?64:32;
      for(const auto &run:fixture.at("actions_rle")) {
        const unsigned a=run.at("actions");
        for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i) {
          simulation->set_launch(a&8);simulation->set_flippers(a&1,a&2);
          if(a&4) simulation->press_plunger();
          if(a&16) simulation->nudge(1,false);
          if(a&64) simulation->nudge(-1,false);
          if(a&32) simulation->nudge(0,true);
          if(!simulation->step()) throw std::runtime_error(simulation->status());
          if(!reached && target()) reached=true;
          else if(reached && --remaining==0) break;
        }
        if(reached && remaining==0) break;
      }
      if(!reached || remaining || !target())
        throw std::runtime_error("Recorded natural mode entry/continuation missing");
      simulation->set_flippers(false,false);
    } else if(scripted_natural_preview) {
      if(!simulation)throw std::runtime_error("Mean simulation required");
      simulation->reset();simulation->set_continuous_play(true);simulation->set_endless_play(false);
      const bool pit=natural_mode_preview=="pit-stop";
      const bool stock=natural_mode_preview=="stock-car";
      const bool speed=natural_mode_preview=="speed";
      const bool monster=natural_mode_preview=="monster";
      const bool rally=natural_mode_preview=="rally";
      const bool offroad=natural_mode_preview=="offroad";
      const bool skull=natural_mode_preview=="skull";
      const bool goals=natural_mode_preview=="goals";
      const bool laps=natural_mode_preview=="laps";
      const bool kickback=natural_mode_preview=="kickback";
      const bool gears=natural_mode_preview=="gears";
      const bool chicken=natural_mode_preview=="chicken";
      nlohmann::json fixture;std::ifstream(skull?SLAM_MEAN_SKULL_TRACE_PATH:goals?SLAM_MEAN_GOAL_LADDER_TRACE_PATH:laps?SLAM_MEAN_LAP_GOAL_TRACE_PATH:kickback?SLAM_MEAN_KICKBACK_TRACE_PATH:gears?SLAM_MEAN_GEARS_TRACE_PATH:chicken?SLAM_MEAN_CHICKEN_TRACE_PATH:offroad?SLAM_MEAN_OFFROAD_TRACE_PATH:rally?SLAM_MEAN_RALLY_TRACE_PATH:monster?SLAM_MEAN_MONSTER_TRACE_PATH:speed?SLAM_MEAN_SPEED_TRACE_PATH:stock?SLAM_MEAN_STOCK_TRACE_PATH:pit?SLAM_MEAN_PIT_TRACE_PATH:SLAM_MEAN_KICKSTART_TRACE_PATH)>>fixture;
      for(const auto&run:fixture.at("actions_rle"))for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i){
        const unsigned action=run.at("actions");simulation->set_launch(action&8);
        simulation->set_flippers(action&1,action&2);if(action&4)simulation->press_plunger();
        if(action&16)simulation->nudge(1,false);
        if(action&64)simulation->nudge(-1,false);
        if(action&32)simulation->nudge(0,true);
        if(!simulation->step())throw std::runtime_error(simulation->status());
        simulation->take_audio_requests();
      }
      const unsigned callback=skull?0x411544:goals?0x410d34:laps?0x410a34:kickback?0x411710:gears?0x41121c:chicken?0x412908:offroad?0x41041c:rally?0x411db4:monster?0x412fa8:speed?0x410158:stock?0x413770:pit?0x4131cc:0x4102c0;
      bool result_missing=false;
      if(skull)result_missing=simulation->skull_award_count()!=3;
      else if(goals)result_missing=simulation->lap_goal_fields()[1]!=0 || simulation->side_extra_balls()!=1 || simulation->gear_stats().upper_extras!=1;
      else if(laps)result_missing=simulation->lap_goal_fields()[1]!=1 || simulation->lap_goal_fields()[6]!=-1 || simulation->lane_saver_frame()!=2;
      else if(kickback)result_missing=simulation->kickback_consumptions()!=1 || simulation->kickback_armed();
      else if(gears)result_missing=simulation->gear_multiplier()!=5 || simulation->gear_stats().fifth_enables!=1 || simulation->pending_upper_extra_balls()!=1;
      else if(chicken)result_missing=simulation->chicken_stats().score!=140208000 || simulation->chicken_stats().races!=3 || simulation->chicken_stats().completions!=1;
      else if(offroad)result_missing=simulation->offroad_stats().score<15000000 || simulation->max_balls()!=4 || simulation->offroad_stats().starts!=1;
      else if(rally)result_missing=simulation->rally_stats().score!=112500000 || simulation->rally_stats().completions!=1;
      else if(monster)result_missing=simulation->monster_stats().score!=125000000 || simulation->monster_stats().completions!=1;
      else if(speed)result_missing=simulation->speed_stats().score!=260000000 || simulation->speed_stats().jackpots[3]!=1;
      else if(stock)result_missing=simulation->stock_car_stats().score!=75000000 || simulation->stock_car_stats().completions!=1;
      else if(pit)result_missing=simulation->pit_stop_stats().score!=65000000 || simulation->pit_stop_stats().completions!=1;
      else result_missing=simulation->phase1_award_total()!=60000000;
      if(result_missing || simulation->material5_display_callback()!=callback)
        throw std::runtime_error("Natural rule-chain result missing");
      simulation->set_flippers(false,false);
      while(simulation->material5_display_counter()<(skull?33u:goals?82u:laps?53u:kickback?35u:gears?119u:chicken?76u:offroad?44u:rally?126u:monster?81u:stock?57u:pit?54u:40u)){
        if(!simulation->step())throw std::runtime_error(simulation->status());
        if(simulation->material5_display_callback()!=callback)throw std::runtime_error("Natural result interrupted");
      }
    }
    if (!natural_mode_preview.empty() && !scripted_natural_preview) {
      if (!simulation) throw std::runtime_error("Mean simulation required");
      simulation->reset();
      simulation->set_continuous_play(true);
      simulation->set_endless_play(natural_mode_preview != "minigame2" && natural_mode_preview != "cliff"); // Existing previews explicitly span many balls.
      slam::MeanDiagnosticInput input(natural_mode_preview == "upper" || natural_mode_preview == "upper-mode" ? 13 : 27);
      const auto target_active = [&]() {
        if (natural_mode_preview == "minigame2") return simulation->minigame2_active();
        if (natural_mode_preview == "minigame") return simulation->minigame_active();
        const auto callback = simulation->material5_display_callback();
        if (natural_mode_preview == "cliff") return callback==0x41249c && simulation->material5_display_counter()>=61;
        if (natural_mode_preview == "upper") return callback == 0x411fdc;
        if (natural_mode_preview == "upper-mode")
          return callback == 0x412d24 || callback == 0x411f10 ||
                 callback == 0x412af8 || callback == 0x412c58;
        return simulation->ball_count() >= 8;
      };
      bool reached = false;
      const unsigned entry_budget = natural_mode_preview == "upper-mode" ? 2000000 : natural_mode_preview == "multiball" ? 1800000 : 400000;
      for(unsigned i=0;i<entry_budget;++i){
        auto keys=natural_mode_preview == "minigame2" ? slam::mean_finite_shot_input(i,simulation->ball().i32(4)>>16) : input.next();
        bool cliff_press=false;
        if(natural_mode_preview=="cliff") {
          const auto&f=simulation->shared_raw_state().fields;
          const auto word=[&](unsigned o){return unsigned(f[o])|(unsigned(f[o+1])<<8);};
          const auto action=slam::mean_cliff_input(i,simulation->table_mode(),word(0x3a6),word(0x39e),word(0x3a8));
          keys={action[0],action[1]};cliff_press=action[2];
        }
        simulation->set_launch(true);
        simulation->set_flippers(keys[0],keys[1]);
        if(cliff_press)simulation->press_plunger();
        if(!simulation->step()) throw std::runtime_error(simulation->status());
        reached = target_active();
        if(reached) break;
      }
      if(!reached) throw std::runtime_error("Natural mode entry was not reached");
      // Continue the same key stream through initial display/release work.
      const unsigned continuation = natural_mode_preview=="cliff" ? 0 : (natural_mode_preview == "minigame" || natural_mode_preview == "minigame2") ? 400 : (natural_mode_preview == "upper" || natural_mode_preview == "upper-mode") ? 32 : 64;
      for(unsigned i=0;i<continuation;++i){
        const auto keys=input.next();
        simulation->set_flippers(keys[0],keys[1]);
        if(!simulation->step()) throw std::runtime_error(simulation->status());
      }
      if (!target_active())
        throw std::runtime_error("Natural mode preview ended prematurely");
    }
    if(tilt_release_preview){
      if(!simulation)throw std::runtime_error("Mean simulation required");
      simulation->debug_tilt_capture(2);
      for(unsigned i=0;i<32;++i)if(!simulation->step())throw std::runtime_error(simulation->status());
    }
    if(!short_mode_preview.empty()) {
      if(!simulation)throw std::runtime_error("Mean simulation required");
      if(short_mode_preview=="cliff-jumper") simulation->debug_cliff_jump(0,false,false,true);
      else if(short_mode_preview=="speed-jackpot") simulation->debug_speed_jackpot(3,false,true);
      else {
        simulation->debug_start_short_mode(short_mode_preview=="stock-car",
                                            short_mode_preview=="pit-jackpot");
        const auto callback=short_mode_preview=="stock-car" ? 0x413770u
            : short_mode_preview=="pit-jackpot" ? 0x4131ccu : 0x413518u;
        if(simulation->material5_display_callback()!=callback)
          throw std::runtime_error("Short mode preview request was not admitted");
        for(unsigned i=0;i<360;++i)if(!simulation->step())throw std::runtime_error(simulation->status());
      }
    }
    if(mode5_award_preview){
      if(!simulation)throw std::runtime_error("Mean simulation required");
      simulation->debug_mode5_award(false,false);
      for(unsigned i=0;i<320;++i)if(!simulation->step())throw std::runtime_error(simulation->status());
    }
    if(nudge_warning_preview){
      if(!simulation)throw std::runtime_error("Mean simulation required");
      simulation->debug_nudge_warning();
      for(unsigned i=0;i<12;++i)if(!simulation->step())throw std::runtime_error(simulation->status());
    }
    if(return_pass_preview){
      if(!simulation) throw std::runtime_error("Mean simulation required");
      simulation->reset();
      for(unsigned i=0;i<3;++i){
        simulation->debug_place_return_pass();
        if(!simulation->step()) throw std::runtime_error(simulation->status());
      }
      // Move to a separate verified ramp switch before advancing the display.
      simulation->debug_place_shared_switch(5);
      for(unsigned i=0;i<21;++i)
        if(!simulation->step()) throw std::runtime_error(simulation->status());
      if(simulation->return_pass_awards()!=2 || simulation->material5_display_callback()!=0x41163c)
        throw std::runtime_error("Return-pass preview chain failed");
    }
    if(minigame_win_preview){
      if(!simulation || !simulation->debug_start_minigame())throw std::runtime_error("Mean mini-game cache required");
      std::ifstream input(std::filesystem::path(trace_path).parent_path()/"mean-minigame1-winning-input.json");
      nlohmann::json keys;input>>keys;
      for(const auto &key:keys.at("keys")){
        if(!simulation->minigame_active())break;
        const auto k=key.get<unsigned>();simulation->set_flippers(k==1,k==2);
        for(unsigned sub=0;sub<4;++sub)if(!simulation->step())throw std::runtime_error(simulation->status());
      }
      simulation->set_flippers(false,false);
      if(simulation->score()!=120000000 || simulation->material5_display_callback()!=0x40fb78)
        throw std::runtime_error("Original steering-only120M win not reached");
      for(unsigned i=0;i<600 && simulation->material5_display_counter()<125;++i)
        if(!simulation->step())throw std::runtime_error(simulation->status());
      if(simulation->material5_display_callback()!=0x40fb78)throw std::runtime_error("Winning result ended prematurely");
    }
    if(minigame_result_preview){
      if(!simulation || !simulation->debug_start_minigame()) throw std::runtime_error("Mean mini-game cache required");
      simulation->set_flippers(false,false);
      for(unsigned i=0;i<6000 && !simulation->minigame_completions();++i)
        if(!simulation->step()) throw std::runtime_error(simulation->status());
      if(simulation->material5_display_callback()!=0x40f994) throw std::runtime_error("First minigame result not reached");
      for(unsigned i=0;i<600 && simulation->material5_display_counter()<80;++i)
        if(!simulation->step()) throw std::runtime_error(simulation->status());
      if(simulation->material5_display_callback()!=0x40f994 || simulation->material5_display_counter()<80)
        throw std::runtime_error("First minigame result ended prematurely");
    }
    if(!minigame2_result_preview.empty()){
      if(!simulation) throw std::runtime_error("Mean simulation required");
      simulation->reset();simulation->debug_start_mode4_right(true);
      const unsigned period=minigame2_result_preview=="success"?5:20;
      for(unsigned i=0;i<12000 && !simulation->minigame_completions();++i){
        simulation->set_flippers((i/period)%2,((i/period)+1)%2);
        if(!simulation->step()) throw std::runtime_error(simulation->status());
      }
      const auto expected=minigame2_result_preview=="success"?0x4122ccu:0x41210cu;
      if(simulation->material5_display_callback()!=expected)
        throw std::runtime_error("Original minigame result not reached");
      simulation->set_flippers(false,false);
      const unsigned ticks=minigame2_result_preview=="success"?100:70;
      for(unsigned i=0;i<1600 && simulation->material5_display_counter()<ticks && simulation->material5_display_callback()==expected;++i)
        if(!simulation->step()) throw std::runtime_error(simulation->status());
      if(simulation->material5_display_callback()!=expected || simulation->material5_display_counter()<ticks)
        throw std::runtime_error("Original minigame result ended prematurely");
    }
    if (point_force_preview) {
      if (!simulation) throw std::runtime_error("Mean simulation required");
      simulation->debug_start_point_force();
      for (unsigned i = 0; i < 100; ++i)
        if (!simulation->step()) throw std::runtime_error(simulation->status());
      if (!simulation->point_force_updates())
        throw std::runtime_error("Original magnet did not affect preview ball");
    }
    if (minigame2_preview) {
      if (!simulation)
        throw std::runtime_error("Mean simulation required");
      simulation->debug_start_right_route();
      for (unsigned i = 0; i < 6000 && !simulation->minigame2_goal_text_seen(); ++i) {
        simulation->set_flippers(i % 40 < 20, false);
        if (!simulation->step())
          throw std::runtime_error(simulation->status());
      }
      if (!simulation->minigame_active() || !simulation->minigame2_goal_text_seen())
        throw std::runtime_error("Original second mini-game goal not reached");
    }
    if (mode4_preview) {
      if (!simulation)
        throw std::runtime_error("Mode4 preview requires Mean simulation");
      simulation->debug_start_mode4();
      unsigned steps = 0;
      while (simulation->ball().u16(0x58) != 7 && steps++ < 3000)
        if (!simulation->step())
          throw std::runtime_error(simulation->status());
      if (simulation->ball().u16(0x58) != 7)
        throw std::runtime_error("Original mode4 state7 not reached");
      for (unsigned i = 0; i < 7; ++i)
        if (!simulation->step())
          throw std::runtime_error(simulation->status());
    }
    if (multiball_preview || mode6_preview) {
      if (!simulation)
        throw std::runtime_error("Multiball preview requires Mean simulation");
      simulation->debug_start_multiball(false, mode6_preview);
      if (mode6_preview) {
        unsigned steps=0;
        while(simulation->material5_display_callback()!=0x410b00 && steps++<800)
          if(!simulation->step()) throw std::runtime_error(simulation->status());
        if(simulation->material5_display_callback()!=0x410b00)
          throw std::runtime_error("Original Mode6 announcement was not reached");
        for(unsigned i=0;i<200;++i)
          if(!simulation->step()) throw std::runtime_error(simulation->status());
      }

    }
    if (mini_preview && (!simulation || !simulation->debug_start_minigame()))
      throw std::runtime_error(
          "Mini-game preview requires prepared native simulation");
    if (!trace.empty())
      SDL_SetWindowTitle(
          window, "Slamtilt - Reborn — original demo state replay (debug marker)");
    if (collision) {
      std::string table_name = std::filesystem::path(argv[1]).stem().string();
      std::transform(table_name.begin(), table_name.end(), table_name.begin(),
                     [](unsigned char c) { return char(std::tolower(c)); });
      const auto profile = slam::load_table_profile(slam::default_table_profiles(), table_name);
      const auto overlay = slam::table_collision_overlay(argv[1], profile);
      collision_texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                                            SDL_TEXTUREACCESS_STATIC, 320, 600);
      if (!collision_texture ||
          !SDL_UpdateTexture(collision_texture, nullptr, overlay.data(),
                             320 * 4) ||
          !SDL_SetTextureBlendMode(collision_texture, SDL_BLENDMODE_BLEND))
        throw std::runtime_error(SDL_GetError());
      SDL_SetTextureScaleMode(collision_texture, SDL_SCALEMODE_NEAREST);
    }
    std::vector<std::array<std::uint8_t, 960>> ball_frames;
    slam::BallMask ball_outline;
    const auto main_dat =
        std::filesystem::path(argv[1]).parent_path() / "MAIN.DAT";
    if (!trace.empty() && !amiga && std::filesystem::exists(main_dat)) {
      const auto mask = slam::load_windows_ball_mask(main_dat);
      ball_outline = mask;
      for (int frame = 0; frame < 75; ++frame) {
        const auto pixels = slam::load_windows_ball_pixels(main_dat, frame * 8);
        std::array<std::uint8_t, 960> rgba{};
        for (std::size_t i = 0; i < 240; ++i) {
          for (int c = 0; c < 3; ++c)
            rgba[4 * i + c] = image.palette_rgba[pixels[i] * 4 + c];
          rgba[4 * i + 3] = 255 - mask.preserve_background[i];
        }
        ball_frames.push_back(rgba);
      }
      ball_texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                                       SDL_TEXTUREACCESS_STATIC, 16, 15);
      if (!ball_texture ||
          !SDL_SetTextureBlendMode(ball_texture, SDL_BLENDMODE_BLEND) ||
          !SDL_SetTextureScaleMode(ball_texture, SDL_SCALEMODE_NEAREST))
        throw std::runtime_error(SDL_GetError());
      SDL_SetWindowTitle(window,
                         "Slamtilt - Reborn — original demo ball trace (replay)");
    }
    if(lane_saver_preview){
      if(!simulation)throw std::runtime_error("Mean simulation required");
      simulation->debug_start_rule_capture(true);
      for(unsigned i=0;i<180;++i)if(!simulation->step())throw std::runtime_error(simulation->status());
      if(simulation->lane_saver_frame()!=2)throw std::runtime_error("Lane saver did not open");
    }
    if (ball_occlusion_preview) {
      if (!simulation)
        throw std::runtime_error("Mean simulation required");
      simulation->debug_ball_occlusion(ball_outline);
    }
    if (simulation)
      SDL_SetWindowTitle(
          window,
          "Slamtilt - Reborn | Mean Machines: Enter launch, Shift flippers, Alt/Space nudge, P pause, R reset");
    std::vector<slam::FlipperFrames> flipper_frames, contact_frames;
    if (simulation) {
      flipper_frames = slam::load_mean_flippers(argv[1], image);
      for (const auto &f : flipper_frames) {
        auto *t =
            SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                              SDL_TEXTUREACCESS_STATIC, f.width, f.height);
        if (!t)
          throw std::runtime_error(SDL_GetError());
        flipper_textures.push_back(t);
        if (!SDL_SetTextureBlendMode(t, SDL_BLENDMODE_BLEND) ||
            !SDL_SetTextureScaleMode(t, SDL_SCALEMODE_NEAREST))
          throw std::runtime_error(SDL_GetError());
      }
    }
    if (simulation) {
      contact_frames = slam::load_mean_contact_frames(argv[1], image);
      for (const auto &f : contact_frames) {
        auto *t =
            SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                              SDL_TEXTUREACCESS_STATIC, f.width, f.height);
        if (!t)
          throw std::runtime_error(SDL_GetError());
        flipper_textures.push_back(t);
        SDL_SetTextureScaleMode(t, SDL_SCALEMODE_NEAREST);
      }
    }
    std::vector<slam::MeanLampFrames> lamps;
    if (simulation) {
      lamps = slam::load_mean_lamps(argv[1], image);
      for (const auto &lamp : lamps) {
        auto *t = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                                    SDL_TEXTUREACCESS_STATIC, lamp.width,
                                    lamp.height);
        if (!t)
          throw std::runtime_error(SDL_GetError());
        lamp_textures.push_back(t);
        if (!SDL_SetTextureBlendMode(t, SDL_BLENDMODE_BLEND) ||
            !SDL_SetTextureScaleMode(t, SDL_SCALEMODE_NEAREST))
          throw std::runtime_error(SDL_GetError());
      }
    }
    std::unique_ptr<slam::MeanScoreFont> score_font;
    if (simulation) {
      score_font =
          std::make_unique<slam::MeanScoreFont>(slam::load_mean_score_font(
              std::filesystem::path(argv[1]).parent_path() / "MAIN.DAT"));
      score_texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                                        SDL_TEXTUREACCESS_STATIC, 96, 20);
      if (!score_texture ||
          !SDL_SetTextureScaleMode(score_texture, SDL_SCALEMODE_NEAREST))
        throw std::runtime_error(SDL_GetError());
    }
#ifdef SLAM_AUDIO_XMP
    std::unique_ptr<slam::NativeAudio> audio;
    if ((!music_path.empty() || simulation) && !no_audio) {
      try {
        if (!music_path.empty())
          audio = std::make_unique<slam::NativeAudio>(music_path, music_order);
        else {
          std::ifstream input(argv[1], std::ios::binary);
          std::vector<std::uint8_t> dat((std::istreambuf_iterator<char>(input)),
                                        {});
          auto banks = slam::mean_sound_banks(dat);
          audio = std::make_unique<slam::NativeAudio>(
              std::vector<std::vector<std::uint8_t>>{std::move(banks[0].stim),
                                                     std::move(banks[1].stim)});
          audio->set_mean_samples(dat);
        }
      } catch (const std::exception &error) {
        std::cerr << "Audio unavailable: " << error.what() << '\n';
      }
    }
#else
    if (!music_path.empty() && !no_audio)
      std::cerr << "Audio unavailable: build requires libxmp\n";
#endif
    std::size_t trace_step = 0;
    double trace_clock = 0;
    bool paused = simulation && (skillshot_reward_preview || !gear_cap_preview.empty() || !overheat_preview.empty() || !player_hud_preview.empty() || !main_mode_hud_preview.empty() || !idle_hud_preview.empty() || mode_total_preview || lane_saver_preview || !short_mode_preview.empty() || mode5_award_preview || tilt_release_preview || nudge_warning_preview || minigame_win_preview || minigame_result_preview || !minigame2_result_preview.empty() || return_pass_preview || !natural_mode_preview.empty() || simulation->game_over() || mode4_upper_preview || shared_reward_preview || rally_reward_preview || point_force_preview || mode4_preview ||
                                 minigame2_preview || ball_occlusion_preview || bonus_preview ||
                                 material5_preview || award_bank_preview ||
                                 extra_ball_preview || switch_reward_preview);
    bool running = true;
    float scroll = 200;
    slam::MeanCameraState camera;
    std::array<slam::MeanCameraBall, 8> camera_balls{};
    const auto reset_camera = [&] {
      if (!simulation) return;
      for (unsigned i = 0; i < simulation->ball_count(); ++i) {
        const auto &b = simulation->ball(i);
        const auto xy = slam::ball_display_position(b.i32(0), b.i32(4), b.i32(8), b.i32(12), 0);
        camera_balls[i] = {static_cast<std::int16_t>(xy[1]), b.u16(0x58)};
      }
      // Native startup policy; original startup camera context is not captured.
      const auto initial_scroll = std::clamp(int(camera_balls[0].render_y) - 100, 0, 200);
      camera = {(initial_scroll + 100) * 65536, 0, initial_scroll, initial_scroll};
    };
    const auto step_camera = [&] {
      for (unsigned i = 0; i < simulation->ball_count(); ++i)
        camera_balls[i].state = simulation->ball(i).u16(0x58);
      // Original4086b8 reads cached renderY but current state after physics.
      slam::mean_camera_step(camera, camera_balls.data(), simulation->ball_count(), 200, 400);
    };
    reset_camera();
    int rendered = 0;
    const auto restart_session=[&]{
      simulation->reset();highscores.reset_session();reset_camera();paused=false;
#ifdef SLAM_AUDIO_XMP
      if(audio)audio->restart();
#endif
    };
    unsigned displayed_ball = 0;
    if(menu_preview) {SDL_Event e{};e.type=SDL_EVENT_KEY_DOWN;e.key.key=SDLK_ESCAPE;options.handle(e);}
    bool dragging_dmd=false;
    float drag_dx=0,drag_dy=0;
    SDL_FRect last_dmd{};
    bool suppress_game_keys=false;
    bool input_focus=true, minimized=false;
    const bool trace_activity=std::getenv("SLAM_TRACE_ACTIVITY")!=nullptr;
    auto acceptance_frozen=simulation?simulation->shared_raw_state().fields:slam::MeanBallResetState{}.fields;
    std::vector<std::array<std::uint8_t,0x64>> acceptance_balls;
    const auto acceptance_score=simulation?simulation->score():0;
    std::filesystem::path acceptance_scores;
    if(!frontend_acceptance.empty()) {
      if(frames<14 || !simulation || !simulation->game_over() || !acceptance_score)
        throw std::runtime_error("Frontend acceptance requires fourteen frames and a scored GameOver");
      const auto report=std::filesystem::absolute(frontend_acceptance);
      std::filesystem::create_directories(report.parent_path());
      acceptance_scores=report.parent_path()/("scores-"+std::to_string(SDL_GetTicksNS())+".json");
      highscores.load_path(acceptance_scores);
#ifdef SLAM_AUDIO_XMP
      if(!no_audio && !audio)throw std::runtime_error("Frontend audio acceptance requires an open device");
#endif
    }
    std::map<unsigned,std::vector<nlohmann::json>> session_inputs;
    nlohmann::json session_states=nlohmann::json::array(),session_input_journal=nlohmann::json::array(),session_audio=nlohmann::json::array(),session_frames=nlohmann::json::array();
    unsigned session_tick=0,session_clamped=0,session_active_steps=0,session_game_over_waits=0;bool session_left=false,session_right=false,session_enter=false;std::string session_failure;
    if(realtime_steps&&!simulation)throw std::runtime_error("Realtime session requires gameplay");
    if(!session_replay.empty()){
      std::ifstream input(session_replay);auto schedule=nlohmann::json::parse(input);
      for(const auto&e:schedule.at("inputs"))session_inputs[e.at("tick").get<unsigned>()].push_back(e);
      if(!simulation)throw std::runtime_error("Replay requires gameplay");
      simulation->reset();simulation->set_continuous_play(true);reset_camera();
    }
    const auto presentation_started=SDL_GetTicksNS();
    std::vector<double> frame_ms;
    auto previous = SDL_GetTicks();
    while (running) {
      const auto frame_started=SDL_GetTicksNS();
      if(!frontend_acceptance.empty()) {
        const auto key=[&](SDL_Keycode k,SDL_Scancode sc,bool repeat=false) {
          SDL_Event e{};e.type=SDL_EVENT_KEY_DOWN;e.key.key=k;e.key.scancode=sc;e.key.repeat=repeat;
          if(!SDL_PushEvent(&e))throw std::runtime_error(SDL_GetError());
        };
        if(rendered==1) {key(SDLK_R,SDL_SCANCODE_R,true);key(SDLK_P,SDL_SCANCODE_P,true);}
        if(rendered==2) {key(SDLK_R,SDL_SCANCODE_R);key(SDLK_A,SDL_SCANCODE_A);key(SDLK_B,SDL_SCANCODE_B);key(SDLK_RETURN,SDL_SCANCODE_RETURN);}
        if(rendered==3) key(SDLK_R,SDL_SCANCODE_R);
        if(rendered==4) key(SDLK_ESCAPE,SDL_SCANCODE_ESCAPE);
        if(rendered==5)key(SDLK_RIGHT,SDL_SCANCODE_RIGHT);
        if(rendered==6) {options.select_option(PortOptions::Apply);key(SDLK_RETURN,SDL_SCANCODE_RETURN);key(SDLK_ESCAPE,SDL_SCANCODE_ESCAPE,true);}
        const auto window_event=[&](Uint32 type) {
          SDL_Event e{};e.type=type;e.window.windowID=SDL_GetWindowID(window);
          if(!SDL_PushEvent(&e))throw std::runtime_error(SDL_GetError());
        };
        if(rendered==7) {
          acceptance_frozen=simulation->shared_raw_state().fields;
          acceptance_balls.clear();
          for(unsigned i=0;i<simulation->ball_count();++i)acceptance_balls.push_back(simulation->ball(i).bytes);
          window_event(SDL_EVENT_WINDOW_FOCUS_LOST);
          key(SDLK_RETURN,SDL_SCANCODE_RETURN);key(SDLK_LALT,SDL_SCANCODE_LALT);key(SDLK_R,SDL_SCANCODE_R);
        }
        if(rendered==8)window_event(SDL_EVENT_WINDOW_MINIMIZED);
        if(rendered==9)window_event(SDL_EVENT_WINDOW_FOCUS_GAINED);
        if(rendered==10){window_event(SDL_EVENT_WINDOW_RESTORED);key(SDLK_P,SDL_SCANCODE_P);}
        if(rendered==11)window_event(SDL_EVENT_WINDOW_FOCUS_LOST);
        if(rendered==12)window_event(SDL_EVENT_WINDOW_FOCUS_GAINED);
        if(rendered==13)key(SDLK_P,SDL_SCANCODE_P);
      }
      SDL_Event event;
      while (gamepad.poll(event,options.settings.keys,options.settings.gamepad_buttons,options.open||paused,options.gamepad_binding())) {
        if (event.type == SDL_EVENT_QUIT || event.type==SDL_EVENT_WINDOW_CLOSE_REQUESTED)
          running = false;
        if(event.type==SDL_EVENT_WINDOW_FOCUS_LOST || event.type==SDL_EVENT_WINDOW_FOCUS_GAINED ||
           event.type==SDL_EVENT_WINDOW_MINIMIZED || event.type==SDL_EVENT_WINDOW_RESTORED) {
          if(event.type==SDL_EVENT_WINDOW_FOCUS_LOST)input_focus=false;
          if(event.type==SDL_EVENT_WINDOW_FOCUS_GAINED)input_focus=true;
          if(event.type==SDL_EVENT_WINDOW_MINIMIZED)minimized=true;
          if(event.type==SDL_EVENT_WINDOW_RESTORED)minimized=false;
          if(trace_activity)std::cerr<<"activity event="<<event.type<<" focus="<<input_focus<<" minimized="<<minimized
            <<" flags="<<SDL_GetWindowFlags(window)<<" manual_pause="<<paused<<" mute="<<audio_muted
            <<" gameover="<<(simulation && simulation->game_over())<<'\n';
          suppress_game_keys=true;dragging_dmd=false;trace_clock=0;options.suspend_interaction();
          if(simulation){simulation->set_flippers(false,false);simulation->set_launch(false);}
          continue;
        }
        if((!input_focus || minimized) && (event.type==SDL_EVENT_KEY_DOWN || event.type==SDL_EVENT_KEY_UP ||
           event.type==SDL_EVENT_MOUSE_BUTTON_DOWN || event.type==SDL_EVENT_MOUSE_BUTTON_UP ||
           event.type==SDL_EVENT_MOUSE_MOTION || event.type==SDL_EVENT_MOUSE_WHEEL))continue;
        if(new_layout&&options.main_menu_available&&event.type==SDL_EVENT_KEY_DOWN&&event.key.key==SDLK_F10){options.handle(event);continue;}
        if(new_layout && highscores.editing && highscores.handle(event)) {
          if(!highscores.editing)suppress_game_keys=true;
          continue;
        }
        if(new_layout) {
          const bool was_open=options.open;
          if(event.type==SDL_EVENT_WINDOW_RESIZED && !applied.fullscreen && !options.open) {
            options.settings.window_width=applied.window_width=std::max(320,event.window.data1);
            options.settings.window_height=applied.window_height=std::max(240,event.window.data2);
          }
          if(event.type==SDL_EVENT_MOUSE_BUTTON_DOWN || event.type==SDL_EVENT_MOUSE_BUTTON_UP) {
            int ww=0,wh=0,rw=0,rh=0;SDL_GetWindowSize(window,&ww,&wh);SDL_GetRenderOutputSize(renderer,&rw,&rh);
            if(ww && wh){event.button.x*=float(rw)/ww;event.button.y*=float(rh)/wh;}
          }
          if(event.type==SDL_EVENT_MOUSE_MOTION) {
            int ww=0,wh=0,rw=0,rh=0;SDL_GetWindowSize(window,&ww,&wh);SDL_GetRenderOutputSize(renderer,&rw,&rh);
            if(ww && wh){event.motion.x*=float(rw)/ww;event.motion.y*=float(rh)/wh;}
            if(dragging_dmd) {
              options.settings.overlay_x=std::clamp((event.motion.x-drag_dx)/std::max(1.f,rw-last_dmd.w),0.f,1.f);
              options.settings.overlay_y=std::clamp((event.motion.y-drag_dy)/std::max(1.f,rh-last_dmd.h),0.f,1.f);
              continue;
            }
          }
          if(options.open && options.settings.dmd_position==3 && event.type==SDL_EVENT_MOUSE_BUTTON_DOWN && event.button.button==SDL_BUTTON_LEFT) {
            const SDL_FPoint point{event.button.x,event.button.y};
            if(!options.contains_point(point.x,point.y) && SDL_PointInRectFloat(&point,&last_dmd)){dragging_dmd=true;drag_dx=point.x-last_dmd.x;drag_dy=point.y-last_dmd.y;continue;}
          }
          if(event.type==SDL_EVENT_MOUSE_BUTTON_UP && dragging_dmd){dragging_dmd=false;continue;}
          if(options.handle(event)) {
            if(was_open && !options.open)suppress_game_keys=true;
            if(options.open && simulation){simulation->set_flippers(false,false);simulation->set_launch(false);}
            continue;
          }
        }
        if(!session_replay.empty()&&(event.type==SDL_EVENT_KEY_DOWN||event.type==SDL_EVENT_KEY_UP)&&event.key.key!=SDLK_P&&event.key.key!=SDLK_M)continue;
        if (event.type == SDL_EVENT_KEY_DOWN && !event.key.repeat) {
          if (event.key.key == SDLK_ESCAPE)
            running = false;
          if (event.key.key == SDLK_M)
            audio_muted = !audio_muted;
          if (!event.key.repeat && (event.key.key == SDLK_P || (event.key.key == SDLK_SPACE && paused)))
            paused = !paused;
          else if (simulation && !paused && !suppress_game_keys && !event.key.repeat) {
            if (event.key.scancode == options.settings.key(PortAction::Plunger)) simulation->press_plunger();
            if (event.key.scancode == options.settings.key(PortAction::NudgeUp)) simulation->nudge(0,true);
            if (event.key.scancode == options.settings.key(PortAction::NudgeLeft)) simulation->nudge(-1);
            if (event.key.scancode == options.settings.key(PortAction::NudgeRight)) simulation->nudge(1);
          }
          if (event.key.key == SDLK_PERIOD && paused && !trace.empty()) {
            if (simulation) {
              if (simulation->step()) step_camera();
            }
            else
              trace_step = (trace_step + 1) % trace.size();
          }
          if (event.key.key == SDLK_R && simulation) {
            restart_session();
            SDL_SetWindowTitle(
                window, "Slamtilt - Reborn | Mean Machines: Enter launch, Shift flippers, Alt/Space nudge, P pause, R reset");
          }
          if (event.key.key == SDLK_C && collision_texture)
            collision = !collision;
          if (event.key.key == SDLK_HOME)
            scroll = 0;
          if (event.key.key == SDLK_END)
            scroll = 200;
        }
        if (event.type == SDL_EVENT_MOUSE_WHEEL)
          scroll -= event.wheel.y * 24;
      }
      if(!frontend_acceptance.empty()) {
        if(rendered==1 && (!highscores.editing || !simulation->game_over() || simulation->score()!=acceptance_score))
          throw std::runtime_error("Initials modal leaked repeated game shortcuts");
        if(rendered==2 && (highscores.editing || highscores.entries().size()!=1 || highscores.entries()[0].initials!="RAB" || highscores.entries()[0].score!=acceptance_score))
          throw std::runtime_error("SDL initials confirmation/save failed");
        if(rendered==3 && (simulation->game_over() || simulation->score() || highscores.entries().size()!=1))
          throw std::runtime_error("SDL new-game action lost score or failed reset");
        if(rendered==4 && !options.open)throw std::runtime_error("SDL options did not open");
        if(rendered==6 && (!running || options.open))throw std::runtime_error("Repeated Escape leaked after closing options");
        if(rendered>=7 && rendered<=13) {
          if(simulation->ball_count()!=acceptance_balls.size())throw std::runtime_error("Suspended ball count changed");
          for(unsigned i=0;i<acceptance_balls.size();++i)
            if(simulation->ball(i).bytes!=acceptance_balls[i])throw std::runtime_error("Suspended ball state changed");
        }
        if(rendered>=7 && rendered<=12 && simulation->shared_raw_state().fields!=acceptance_frozen)
          throw std::runtime_error("Focus/minimize/manual pause mutated frozen gameplay");
        if(rendered==7 && (input_focus || minimized || paused))throw std::runtime_error("Focus loss changed manual pause");
        if(rendered==9 && (!input_focus || !minimized))throw std::runtime_error("Focus gain bypassed minimized suspension");
        if(rendered>=10 && rendered<=12 && !paused)throw std::runtime_error("Focus cycle lost manual pause");
        if(rendered==13 && (paused || !input_focus || minimized))throw std::runtime_error("Focus return did not allow resume");
      }
      const auto now = SDL_GetTicks();
      const float raw_dt=static_cast<float>(now-previous)/1000.f;
      if(raw_dt>.1f && input_focus&&!minimized&&!paused&&!options.open)++session_clamped;
      const float dt=(!session_replay.empty()&&frames)?0.02f:std::min(.1f,raw_dt);
      previous = now;
      const bool *keys = gamepad.keyboard_state();
      scroll += (static_cast<int>(keys[SDL_SCANCODE_DOWN]) -
                 static_cast<int>(keys[SDL_SCANCODE_UP])) *
                dt * 240;
      if(suppress_game_keys && !keys[options.settings.key(PortAction::Plunger)] && !keys[options.settings.key(PortAction::NudgeUp)] && !keys[options.settings.key(PortAction::LeftFlipper)] && !keys[options.settings.key(PortAction::RightFlipper)] && !keys[options.settings.key(PortAction::NudgeLeft)] && !keys[options.settings.key(PortAction::NudgeRight)]) suppress_game_keys=false;
      if (simulation && session_replay.empty() && !paused && input_focus && !minimized && !options.open && !suppress_game_keys) {
        simulation->set_continuous_play(true);
        simulation->set_flippers(keys[options.settings.key(PortAction::LeftFlipper)],
                                 keys[options.settings.key(PortAction::RightFlipper)]);
        simulation->set_launch(keys[options.settings.key(PortAction::Plunger)]);
      }
      if (!trace.empty()) {
        // Demo timeGetTime accumulator consumes 5ms per gameplay step.
        const double step_seconds = simulation ? 0.005 : 1.0 / 60.0;
        if (!paused && input_focus && !minimized && !options.open) {
          const bool fixed_replay=!session_replay.empty()&&frames;
          unsigned fixed_steps=fixed_replay?4u:0u;
          if(!fixed_replay)trace_clock+=dt;
          while(fixed_replay?fixed_steps>0:trace_clock>=step_seconds){
            if(fixed_replay)--fixed_steps;else trace_clock-=step_seconds;
            if (simulation) {
              if(realtime_steps&&session_tick>=realtime_steps){running=false;break;}
              if(!session_replay.empty()){
                auto it=session_inputs.find(session_tick);if(it!=session_inputs.end())for(const auto&e:it->second){
                  const auto action=e.at("action").get<std::string>();const bool down=e.value("down",true);
                  if(simulation->game_over())highscores.begin(simulation->score());
                  if(highscores.editing){
                    SDL_Event modal{};modal.type=down?SDL_EVENT_KEY_DOWN:SDL_EVENT_KEY_UP;
                    modal.key.scancode=action=="enter"?SDL_SCANCODE_RETURN:action=="new_game"?SDL_SCANCODE_R:SDL_SCANCODE_UNKNOWN;
                    highscores.handle(modal);session_left=session_right=session_enter=false;session_input_journal.push_back(e);continue;
                  }
                  if(action=="left")session_left=down;else if(action=="right")session_right=down;else if(action=="enter"){session_enter=down;if(down)simulation->press_plunger();}
                  else if(action=="new_game"&&down){restart_session();session_left=session_right=session_enter=false;}
                  else if(action!="new_game")throw std::runtime_error("Unsupported Mean replay action: "+action);
                  session_input_journal.push_back(e);
                }
                simulation->set_continuous_play(true);simulation->set_flippers(session_left,session_right);simulation->set_launch(session_enter);
              }
              const bool waiting_game_over=!session_replay.empty()&&simulation->game_over();
              if(waiting_game_over)++session_game_over_waits;else ++session_active_steps;
              const bool stepped=waiting_game_over?false:simulation->step();
              if(!stepped){
                SDL_SetWindowTitle(window,simulation->status());
                if(!session_replay.empty()&&simulation->game_over())highscores.begin(simulation->score());
                else{
                  paused=true;if(realtime_steps||!session_replay.empty()){session_failure=simulation->status();running=false;}
                  break;
                }
              }
#ifdef SLAM_AUDIO_XMP
              if(!session_replay.empty())for(const auto&request:simulation->take_audio_requests()){
                if(!session_output.empty())session_audio.push_back({session_tick,request.service,request.bank,request.order,request.descriptor});
                if(audio)audio->request(request.service,request.bank,request.order,request.descriptor);
              }
#endif
              step_camera();++session_tick;
              if(!session_output.empty()){
                nlohmann::json balls=nlohmann::json::array();for(unsigned i=0;i<simulation->ball_count();++i)balls.push_back(simulation->ball(i).bytes);
                session_states.push_back({{"tick",session_tick},{"balls",balls},{"ball_count",simulation->ball_count()},{"score",simulation->score()},{"phase1_state",simulation->phase1_state()},{"game_over",simulation->game_over()},{"camera_scroll",camera.scroll}});
              }
              if(realtime_steps&&session_tick>=realtime_steps){running=false;break;}
            } else
              trace_step = (trace_step + 1) % trace.size();
          }
        }
        scroll = simulation ? float(camera.scroll)
                            : float(trace[trace_step].y) / 65536.0f - 200.0f;
      }
      if (simulation && simulation->ball_number() != displayed_ball) {
        displayed_ball = simulation->ball_number();
        const auto title = "Slamtilt - Reborn | Mean Machines - Ball " +
                           std::to_string(displayed_ball) +
                           ": Enter launch, Shift flippers, R reset";
        SDL_SetWindowTitle(window, simulation->game_over()
                                       ? simulation->status()
                                       : title.c_str());
      }
      if(lane_saver_preview || natural_mode_preview=="laps")scroll=200;
      scroll = std::clamp(scroll, 0.0f, 200.0f);
      if(new_layout) {
        const auto &s=options.settings;
        if(s.fullscreen!=applied.fullscreen || s.fullscreen_mode!=applied.fullscreen_mode || s.window_width!=applied.window_width || s.window_height!=applied.window_height) {
          if(set_window_mode(s))applied=s;
          else {
            const std::string err=options.error.empty()?SDL_GetError():options.error;
            set_window_mode(applied);
            options.settings.fullscreen=applied.fullscreen;options.settings.fullscreen_mode=applied.fullscreen_mode;
            options.settings.window_width=applied.window_width;options.settings.window_height=applied.window_height;
            options.error=err;
          }
        }
        SDL_SetRenderTarget(renderer,table_target);
      }
      const SDL_FRect source{0, scroll, 320, 400};
      SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
      if (!SDL_RenderClear(renderer) ||
          !SDL_RenderTexture(renderer, texture, &source, nullptr))
        throw std::runtime_error(SDL_GetError());
      for (unsigned i = 0; i < lamps.size(); ++i) {
        int on = simulation->lamp_state(i);
        if (on < 0)
          continue;
        const auto &lamp = lamps[i];
        const SDL_FRect dest{float(lamp.x), float(lamp.y) - scroll,
                             float(lamp.width), float(lamp.height)};
        if (!SDL_UpdateTexture(lamp_textures[i], nullptr, lamp.rgba[on].data(),
                               lamp.width * 4) ||
            !SDL_RenderTexture(renderer, lamp_textures[i], nullptr, &dest))
          throw std::runtime_error(SDL_GetError());
      }
      for (unsigned i = 0; i < contact_frames.size(); ++i) {
        const int frame = simulation->contact_frame(i);
        if (frame < 0)
          continue;
        const auto &f = contact_frames[i];
        auto *t = flipper_textures.at(flipper_frames.size() + i);
        const SDL_FRect dest{float(f.x), float(f.y) - scroll, float(f.width),
                             float(f.height)};
        if (!SDL_UpdateTexture(t, nullptr, f.rgba.at(frame).data(),
                               f.width * 4) ||
            !SDL_RenderTexture(renderer, t, nullptr, &dest))
          throw std::runtime_error(SDL_GetError());
      }
      for (unsigned i = 0; i < flipper_frames.size(); ++i) {
        const auto &f = flipper_frames[i];
        const auto &pixels = f.rgba[f.frame(simulation->flipper_pose(i))];
        SDL_FRect dest{float(f.x), float(f.y) - scroll, float(f.width),
                       float(f.height)};
        if (!SDL_UpdateTexture(flipper_textures[i], nullptr, pixels.data(),
                               f.width * 4) ||
            !SDL_RenderTexture(renderer, flipper_textures[i], nullptr, &dest))
          throw std::runtime_error(SDL_GetError());
      }
      if (collision && collision_texture)
        SDL_RenderTexture(renderer, collision_texture, &source, nullptr);
      const auto draw_ball = [&](int x_now, int y_now, int x_previous,
                                 int y_previous, unsigned milliseconds,
                                 unsigned object_index = 0) {
        const auto position = slam::ball_display_position(
            x_now, y_now, x_previous, y_previous, milliseconds);
        const float x = float(position[0]), y = float(position[1]) - scroll;
        if (ball_texture) {
          if (position[0] < 0 || position[0] >= 304 || position[1] < 0 ||
              position[1] >= 600)
            return;
          auto rgba = ball_frames[std::clamp(position[1] / 8, 0, 74)];
          if (simulation) {
            auto mask = simulation->ball_occlusion(ball_outline, position[0],
                                                   position[1], object_index);
            for (unsigned p = 0; p < 240; ++p)
              rgba[p * 4 + 3] = 255 - mask.preserve_background[p];
          }
          if (!SDL_UpdateTexture(ball_texture, nullptr, rgba.data(), 16 * 4))
            throw std::runtime_error(SDL_GetError());
          const SDL_FRect dest{x, y, 16, 15};
          if (!SDL_RenderTexture(renderer, ball_texture, nullptr, &dest))
            throw std::runtime_error(SDL_GetError());
        } else {
          SDL_SetRenderDrawColor(renderer, 255, 230, 0, 255);
          SDL_RenderLine(renderer, x + 2, y + 7, x + 14, y + 7);
          SDL_RenderLine(renderer, x + 8, y + 1, x + 8, y + 13);
        }
      };
      if (simulation) {
        const auto milliseconds =
            unsigned(std::clamp<long>(std::lround(trace_clock * 1000), 0, 5));
        for (unsigned i = 0; i < simulation->ball_count(); ++i) {
          const auto &ball = simulation->ball(i);
          const auto xy = slam::ball_display_position(ball.i32(0), ball.i32(4), ball.i32(8), ball.i32(12), milliseconds);
          camera_balls[i].render_y = static_cast<std::int16_t>(xy[1]);
          draw_ball(ball.i32(0), ball.i32(4), ball.i32(8), ball.i32(12),
                    milliseconds, i);
        }
      } else if (!trace.empty()) {
        const auto &ball = trace[trace_step];
        draw_ball(ball.x, ball.y, ball.x, ball.y, 5);
      }
      if (!new_layout && simulation &&
          (simulation->minigame_active() || simulation->bonus_active() ||
           simulation->material5_display_active())) {
        const auto &pixels =
            simulation->bonus_active()      ? simulation->bonus_pixels()
            : simulation->minigame_active() ? simulation->minigame_pixels()
                                            : simulation->material5_pixels();
        const SDL_FRect panel{12, 24, 296, 72};
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderFillRect(renderer, &panel);
        for (unsigned y = 0; y < 20; ++y)
          for (unsigned x = 0; x < 96; ++x) {
            const auto level = pixels[y * 96 + x];
            const auto &rgb=dmd_palette.at(level);
            SDL_SetRenderDrawColor(renderer,rgb[0],rgb[1],rgb[2],255);
            const SDL_FRect pixel{16.f + x * 3, 28.f + y * 3, 3, 3};
            SDL_RenderFillRect(renderer, &pixel);
          }
        SDL_SetRenderDrawColor(renderer, 255, 210, 100, 255);
        if (simulation->minigame_active())
          SDL_RenderDebugText(renderer, 16, 90,
                              simulation->minigame2_active()
                                  ? "MINI-GAME: SHIFT ACCELERATES"
                                  : "MINI-GAME: SHIFT STEERS");
      }
      if (simulation && !new_layout) {
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        const SDL_FRect score_bar{0, 0, 320, 22};
        SDL_RenderFillRect(renderer, &score_bar);
        SDL_SetRenderDrawColor(renderer, 255, 210, 100, 255);
        slam::WindowsDmdPixels digits{};
        slam::draw_mean_score_u64(*score_font, digits, simulation->score(), 24,
                                  1, 2);
        std::array<std::uint8_t, 96 * 20 * 4> rgba{};
        for (unsigned i = 0; i < digits.size(); ++i) {
          rgba[i * 4] = rgba[i * 4 + 1] = rgba[i * 4 + 2] = digits[i] * 85;
          rgba[i * 4 + 3] = 255;
        }
        const SDL_FRect score_dest{96, 1, 96, 20};
        if (!SDL_UpdateTexture(score_texture, nullptr, rgba.data(), 96 * 4) ||
            !SDL_RenderTexture(renderer, score_texture, nullptr, &score_dest))
          throw std::runtime_error(SDL_GetError());
        auto label = simulation->game_over()
                         ? std::string("GAME OVER")
                         : "BALL " + std::to_string(simulation->ball_number());
        if (simulation->game_over()) {
          SDL_SetRenderDrawColor(renderer, 0, 0, 0, 230);
          const SDL_FRect end_bar{0, 22, 320, 14};
          SDL_RenderFillRect(renderer, &end_bar);
          SDL_SetRenderDrawColor(renderer, 255, 210, 100, 255);
          if (!SDL_RenderDebugText(renderer, 80, 25, "R: NEW GAME"))
            throw std::runtime_error(SDL_GetError());
        }
        if (simulation->ball_count() > 1)
          if (!SDL_RenderDebugText(
                  renderer, 208, 3,
                  ("ACTIVE " + std::to_string(simulation->ball_count()))
                      .c_str()))
            throw std::runtime_error(SDL_GetError());
        if (!SDL_RenderDebugText(renderer, 4, 3, label.c_str()))
          throw std::runtime_error(SDL_GetError());
      }
      if(new_layout) {
        if(simulation && simulation->game_over())highscores.begin(simulation->score());
        SDL_SetRenderTarget(renderer,nullptr);
        int rw=0,rh=0;SDL_GetRenderOutputSize(renderer,&rw,&rh);
        const auto &o=options.settings;
        float bx=160,by=200;
        if(simulation){bx=simulation->ball().i32(0)/65536.f;by=simulation->ball().i32(4)/65536.f-scroll;}
        auto layout=slam::display_layout(rw,rh,o.dmd_position,o.dmd_size,o.zoom,o.aspect,bx,by);
        if(o.dmd_position==3){layout.dmd.x=o.overlay_x*(rw-layout.dmd.w);layout.dmd.y=o.overlay_y*(rh-layout.dmd.h);}
        last_dmd=layout.dmd;
        SDL_SetRenderDrawColor(renderer,0,0,0,255);SDL_RenderClear(renderer);
        SDL_SetTextureScaleMode(table_target,(o.smooth || o.visual.preset==1)?SDL_SCALEMODE_LINEAR:SDL_SCALEMODE_NEAREST);
        SDL_Rect clip{int(layout.viewport.x),int(layout.viewport.y),int(layout.viewport.w),int(layout.viewport.h)};
        SDL_SetRenderClipRect(renderer,&clip);presentation.draw(table_target,layout.table,o.visual);SDL_SetRenderClipRect(renderer,nullptr);
        if(simulation) {
          slam::WindowsDmdPixels idle{};slam::draw_mean_score_u64(*score_font,idle,simulation->score(),4,1,2);
          const auto &pixels=simulation->bonus_active()?simulation->bonus_pixels():simulation->minigame_active()?simulation->minigame_pixels():simulation->material5_display_active()?simulation->material5_pixels():idle;
          SDL_SetRenderTarget(renderer,dmd_target);
          for(unsigned y=0;y<20;++y)for(unsigned x=0;x<96;++x) {
            const unsigned level=pixels[y*96+x];
            const auto &rgb=dmd_palette.at(level);
            if(o.color==0)SDL_SetRenderDrawColor(renderer,rgb[0],rgb[1],rgb[2],255);
            else if(o.color==1)SDL_SetRenderDrawColor(renderer,level*85,level*53,0,255);
            else if(o.color==2)SDL_SetRenderDrawColor(renderer,level*85,level*85,level*85,255);
            else SDL_SetRenderDrawColor(renderer,level*o.custom_r/3,level*o.custom_g/3,level*o.custom_b/3,255);
            const SDL_FRect dot{float(x),float(y),1,1};SDL_RenderFillRect(renderer,&dot);
          }
        }
        SDL_SetRenderTarget(renderer,nullptr);
        if(simulation)presentation.draw(dmd_target,layout.dmd,o.visual,true);
        options.shaders_available=presentation.available();options.shader_status=presentation.status();
        if(simulation && simulation->game_over() && !options.open)highscores.draw(renderer,rw,rh);
        if(!options.open)slam::draw_gamepad_pull(renderer,gamepad,rh);
        options.draw(renderer,rw,rh);
      }
      if (!capture.empty()&&((frames&&rendered+1>=frames)||(realtime_steps&&session_tick==realtime_steps))) {
        SDL_Surface *shot = SDL_RenderReadPixels(renderer, nullptr);
        if (!shot)
          throw std::runtime_error(SDL_GetError());
        const bool saved = SDL_SaveBMP(shot, capture.c_str());
        SDL_DestroySurface(shot);
        if (!saved)
          throw std::runtime_error(SDL_GetError());
      }
#ifdef SLAM_AUDIO_XMP
      if (simulation) {
        for (const auto &request : simulation->take_audio_requests()) {
          if(!session_output.empty())session_audio.push_back({session_tick,request.service,request.bank,request.order,request.descriptor});
          if(audio)audio->request(request.service,request.bank,request.order,request.descriptor);
        }
      }
      if (audio) {
        audio->set_paused(paused || !input_focus || minimized || options.open || audio_muted ||
                          (simulation && simulation->game_over()));
        audio->set_levels(options.settings.volume,options.settings.music_volume,options.settings.sfx_volume);
        audio->pump();
        if(!frontend_acceptance.empty()) {
          const bool expected=paused || !input_focus || minimized || options.open || audio_muted || simulation->game_over();
          if(audio->device_paused()!=expected)throw std::runtime_error("SDL device pause disagrees with frontend suspension");
          if(rendered==13 && audio->queued_bytes()<=0)throw std::runtime_error("Resumed SDL audio queue is empty");
        }
      }
#endif
      if(!frontend_acceptance.empty() && rendered==1) {
        SDL_Surface *shot=SDL_RenderReadPixels(renderer,nullptr);
        if(!shot)throw std::runtime_error(SDL_GetError());
        const bool saved=SDL_SaveBMP(shot,(frontend_acceptance+".initials.bmp").c_str());
        SDL_DestroySurface(shot);
        if(!saved)throw std::runtime_error(SDL_GetError());
      }
      if (!SDL_RenderPresent(renderer))
        throw std::runtime_error(SDL_GetError());
      if(!frontend_acceptance.empty() && rendered==13) {
        MeanHighscores loaded;loaded.load_path(acceptance_scores);
        if(loaded.entries().size()!=1 || loaded.entries()[0].initials!="RAB" || loaded.entries()[0].score!=acceptance_score ||
           !options.settings.fullscreen || !(SDL_GetWindowFlags(window)&SDL_WINDOW_FULLSCREEN))
          throw std::runtime_error("Highscore reload/fullscreen SDL acceptance failed");
        std::ofstream report(frontend_acceptance);
        report<<nlohmann::json({{"scope","Real SDL event routing after native scored GameOver, modal repeats, RAB initials/save/reload, R newgame, options/fullscreen, repeated Escape, focus/minimize input suspension and preserved manual pause; isolated persistence"},{"score",acceptance_score},{"initials","RAB"},{"fullscreen",true},{"focus_minimize_resume",true},{"manual_pause_preserved",true},{"audio_requested",!no_audio},{"open_failures",0}}).dump(2)<<'\n';
        if(!report)throw std::runtime_error("Frontend acceptance report write failed");
        std::filesystem::remove(acceptance_scores);
      }
      if(!session_output.empty())session_frames.push_back({{"elapsed_ms",double(SDL_GetTicksNS()-presentation_started)/1e6},{"game_over",simulation?simulation->game_over():false},{"tick",session_tick},{"focused",input_focus},{"minimized",minimized},{"paused",paused},{"menu",options.open},
#ifdef SLAM_AUDIO_XMP
        {"audio_device_paused",audio?audio->device_paused():true},{"audio_queued_bytes",audio?audio->queued_bytes():0},
#endif
        {"fullscreen",bool(SDL_GetWindowFlags(window)&SDL_WINDOW_FULLSCREEN)}});
      if(!session_output.empty() && gamepad.connected() && simulation) {
        auto& frame=session_frames.back();
        frame["controller"]={{"left",gamepad.held(options.settings.keys[0])},{"right",gamepad.held(options.settings.keys[1])},{"pull",gamepad.pull()}};
        frame["flipper_poses"]={simulation->flipper_pose(0),simulation->flipper_pose(1),simulation->flipper_pose(2)};
      }
      frame_ms.push_back((SDL_GetTicksNS()-frame_started)/1e6);
      ++rendered;
      if (frames && rendered >= frames)
        running = false;
      SDL_Delay(1);
    }
    if(!session_output.empty()){
      int ow,oh;SDL_GetRenderOutputSize(renderer,&ow,&oh);std::ofstream report(session_output);
      report<<nlohmann::json{{"table","mean"},{"tick_count",session_tick},{"active_steps",session_active_steps},{"game_over_wait_ticks",session_game_over_waits},{"states",session_states},{"inputs",session_input_journal},{"audio_events",session_audio},{"ui_frames",session_frames},{"failure",session_failure},{"audio_driver",SDL_GetCurrentAudioDriver()?SDL_GetCurrentAudioDriver():"none"},{"fullscreen",bool(SDL_GetWindowFlags(window)&SDL_WINDOW_FULLSCREEN)},{"real_wall_ms",(SDL_GetTicksNS()-presentation_started)/1e6},{"clamped_frames",session_clamped},{"renderer",SDL_GetRendererName(renderer)},{"video_driver",SDL_GetCurrentVideoDriver()},{"output_width",ow},{"output_height",oh}}.dump()<<'\n';
      if(!report)throw std::runtime_error("Cannot write Mean session report");
    }
    if(!session_failure.empty())throw std::runtime_error(session_failure);
    if(!presentation_report.empty()) {
      auto sorted=frame_ms;
      if(sorted.size()>60)sorted.erase(sorted.begin(),sorted.begin()+30);
      std::sort(sorted.begin(),sorted.end());
      int output_w=0,output_h=0;SDL_GetRenderOutputSize(renderer,&output_w,&output_h);
      std::ofstream report(presentation_report);
      report<<nlohmann::json({{"renderer",SDL_GetRendererName(renderer)},{"gpu_effects",presentation.available()},
        {"status",presentation.status()},{"preset",slam::visual_preset_name(options.settings.visual.preset)},
        {"output_width",output_w},{"output_height",output_h},{"warmup_frames",rendered>60?30:0},{"frames",rendered},{"elapsed_ms",(SDL_GetTicksNS()-presentation_started)/1e6},
        {"median_frame_ms",sorted[sorted.size()/2]},{"p95_frame_ms",sorted[std::min(sorted.size()-1,sorted.size()*95/100)]}}).dump(2)<<'\n';
      if(!report)throw std::runtime_error("Cannot write presentation report");
    }
    std::cout << "Rendered " << rendered << " frames; palette offset 0x"
              << std::hex << image.palette_offset << '\n';
  } catch (const std::exception &error) {
    std::cerr << "slamview: " << error.what() << '\n';
    for (auto *t : lamp_textures)
      SDL_DestroyTexture(t);
    for (auto *t : flipper_textures)
      SDL_DestroyTexture(t);
    SDL_DestroyTexture(score_texture);
    SDL_DestroyTexture(ball_texture);
    SDL_DestroyTexture(collision_texture);
    SDL_DestroyTexture(dmd_target);
    SDL_DestroyTexture(table_target);
    SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 1;
  }
  for (auto *t : lamp_textures)
    SDL_DestroyTexture(t);
  for (auto *t : flipper_textures)
    SDL_DestroyTexture(t);
  SDL_DestroyTexture(score_texture);
  SDL_DestroyTexture(ball_texture);
  SDL_DestroyTexture(collision_texture);
  SDL_DestroyTexture(dmd_target);
  SDL_DestroyTexture(table_target);
  SDL_DestroyTexture(texture);
  SDL_DestroyRenderer(renderer);
  SDL_DestroyWindow(window);
  SDL_Quit();
  return 0;
}
