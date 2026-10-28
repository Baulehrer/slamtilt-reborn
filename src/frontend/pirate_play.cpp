#include "frontend/window_mode.h"
#include "frontend/pirate_play.h"
#include "assets/asset_source.h"
#include "frontend/pirate_timing.h"
#include "frontend/port_options.h"
#include "assets/ball_mask.h"
#include "assets/ball_occlusion.h"
#include "assets/table_sprites.h"
#include "assets/table_lamps.h"
#include "physics/pirate_session.h"
#include "core/sha256.h"
#include "core/pirate_input_replay.h"
#include "core/pirate_shot_replay.h"
#include "frontend/pirate_highscores.h"
#include "renderer/ball_display.h"
#include "renderer/pirate_scene.h"
#include "renderer/pirate_camera.h"
#include "renderer/display_layout.h"
#include "renderer/presentation.h"
#ifdef SLAM_AUDIO_XMP
#include "audio/native_audio.h"
#include "audio/pirate_sound_assets.h"
#endif
#include <iostream>

namespace slam {
namespace {
template<class T,void(*Destroy)(T*)> using Owner=std::unique_ptr<T,decltype(Destroy)>;
SDL_Texture* texture(SDL_Renderer* renderer,int width,int height,bool target=false) {
  auto* result=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_RGBA32,
    target?SDL_TEXTUREACCESS_TARGET:SDL_TEXTUREACCESS_STREAMING,width,height);
  if(!result)throw std::runtime_error(SDL_GetError());
  SDL_SetTextureBlendMode(result,target?SDL_BLENDMODE_NONE:SDL_BLENDMODE_BLEND);
  return result;
}
std::int32_t value(const std::array<std::uint8_t,100>& state,unsigned offset) {
  std::uint32_t result=0;
  for(unsigned i=0;i<4;++i)result|=std::uint32_t(state.at(offset+i))<<(8*i);
  return std::int32_t(result);
}
}
int run_pirate_play(int argc,char**argv) {
  try {
    if(argc<4)throw std::runtime_error("Usage: slamview PIRATE.DAT --pirate-play PREPARED [--frames N] [--autoplay] [--capture FILE] [--trace-output FILE]");
    const std::filesystem::path dat=argv[1],prepared=argv[3];
    unsigned frames=0,realtime_ms=0,realtime_steps=0;bool timing_inputs=false;std::string timing_path;
    bool replay_only=false;
    bool autoplay=false,windowed=false,fullscreen=false,physics_only=false,autoplay_flippers=false,lamps_enabled=true,no_audio=false,full_state_trace=false;
    std::string capture,trace_path,replay_path,highscore_path,shot_path,audio_trace_path,audio_acceptance_path,nudge_acceptance_path,special_acceptance_path;
    for(int i=4;i<argc;++i){
      const std::string arg=argv[i];
      if(arg=="--realtime-steps"&&i+1<argc){realtime_steps=std::stoul(argv[++i]);if(!realtime_steps||realtime_steps>100000)throw std::runtime_error("Invalid realtime step count");}
      else if(arg=="--realtime-ms"&&i+1<argc){realtime_ms=std::stoul(argv[++i]);if(!realtime_ms||realtime_ms>600000)throw std::runtime_error("Invalid realtime duration");}
      else if(arg=="--timing-output"&&i+1<argc)timing_path=argv[++i];
      else if(arg=="--timing-inputs")timing_inputs=true;
      else if(arg=="--autoplay")autoplay=true;
      else if(arg=="--autoplay-flippers")autoplay_flippers=true;
      else if(arg=="--physics-only")physics_only=true;
      else if(arg=="--full-state-trace")full_state_trace=true;
      else if(arg=="--no-lamps")lamps_enabled=false;
      else if(arg=="--no-audio")no_audio=true;
      else if(arg=="--replay-only")replay_only=true;
      else if(arg=="--windowed")windowed=true;
      else if(arg=="--fullscreen")fullscreen=true;
      else if(arg=="--frames"&&i+1<argc){frames=std::stoul(argv[++i]);if(!frames||frames>100000)throw std::runtime_error("Invalid frame count");}
      else if(arg=="--capture"&&i+1<argc)capture=argv[++i];
      else if(arg=="--trace-output"&&i+1<argc)trace_path=argv[++i];
      else if(arg=="--replay"&&i+1<argc)replay_path=argv[++i];
      else if(arg=="--diagnostic-shots"&&i+1<argc)shot_path=argv[++i];
      else if(arg=="--highscore-file"&&i+1<argc)highscore_path=argv[++i];
      else if(arg=="--audio-trace"&&i+1<argc)audio_trace_path=argv[++i];
      else if(arg=="--audio-acceptance"&&i+1<argc)audio_acceptance_path=argv[++i];
      else if(arg=="--nudge-acceptance"&&i+1<argc)nudge_acceptance_path=argv[++i];
      else if(arg=="--special-acceptance"&&i+1<argc)special_acceptance_path=argv[++i];
      else throw std::runtime_error("Unknown Pirate option: "+arg);
    }
    if(realtime_steps){if(frames||replay_path.empty()||timing_inputs)throw std::runtime_error("Realtime steps require a replay and no fixed frames/timing inputs");if(!realtime_ms)realtime_ms=realtime_steps*5+30000;}
    if(timing_inputs&&(!realtime_ms||timing_path.empty()))throw std::runtime_error("Timing inputs require realtime duration and timing output");
    if(windowed&&fullscreen)throw std::runtime_error("Choose either --windowed or --fullscreen");
    if(!shot_path.empty()&&!highscore_path.empty())throw std::runtime_error("Diagnostic shots use no persistent highscore profile");
    if(!capture.empty()&&!frames&&!realtime_ms)throw std::runtime_error("--capture requires --frames");
    if(!nudge_acceptance_path.empty()&&(frames!=14||physics_only||!audio_acceptance_path.empty()))throw std::runtime_error("Nudge acceptance requires14full frames and no audio acceptance");
    if(!audio_acceptance_path.empty()&&frames!=14)throw std::runtime_error("Audio acceptance requires14frames");
    if(!special_acceptance_path.empty()&&(frames!=14||physics_only||!audio_acceptance_path.empty()||!nudge_acceptance_path.empty()))throw std::runtime_error("Special acceptance requires14full frames and no other event acceptance");
    infer_asset_source(dat.parent_path());
    PirateSession session(prepared,dat,physics_only?PirateTickMode::PhysicsOnly:PirateTickMode::Full);
    const auto definition=load_table_definition_for_data(default_table_profiles(),"pirate",dat);
    const auto image=load_windows_table(dat);
    const auto flippers=load_table_flippers(dat,definition,image);
    const auto flipper_profiles=table_flipper_sprite_profiles(definition);
    const auto lamps=physics_only||!lamps_enabled?std::vector<TableLampFrames>{}:load_table_lamps(dat,definition,image,session.executable_image());
    session.enable_lamps(!lamps.empty());
    const auto main_dat=dat.parent_path()/"MAIN.DAT";
    const auto outline=load_windows_ball_mask(main_dat);
    const auto ball_pixels=load_windows_ball_pixel_bank(main_dat);
    if(!SDL_Init(SDL_INIT_VIDEO))throw std::runtime_error(SDL_GetError());
    struct Quit {~Quit(){SDL_Quit();}} quit;
#ifdef SLAM_AUDIO_XMP
    std::unique_ptr<NativeAudio> audio;
    if(!no_audio&&!physics_only){
      try{
        auto banks=pirate_sound_banks(session.table_data());
        audio=std::make_unique<NativeAudio>(std::vector<std::vector<std::uint8_t>>{std::move(banks[0].stim),std::move(banks[1].stim)});
        audio->set_samples(session.table_data(),pirate_sample_profiles());
      }catch(const std::exception& error){audio.reset();std::cerr<<"Pirate audio unavailable: "<<error.what()<<'\n';}
    }
    session.enable_audio_events(bool(audio));
#else
    (void)no_audio;
#endif
    PirateHighscores score_store;
    if(highscore_path.empty()&&!frames&&!realtime_ms&&shot_path.empty()){
      if(auto* path=SDL_GetPrefPath("SlamTiltNative","SlamTilt")){
        highscore_path=(std::filesystem::path(path)/slam::highscore_filename("pirate")).string();
        SDL_free(path);
      }
    }
    if(!highscore_path.empty()){
      const auto records=score_store.load(highscore_path);
      if(records)session.set_highscores(*records);
      else if(!score_store.error.empty()){std::cerr<<score_store.error<<'\n';highscore_path.clear();}
    }
    auto saved_records=session.highscores();
    PirateInputReplay replay;if(!replay_path.empty())replay.load(replay_path);
    PirateShotReplay shots;if(!shot_path.empty())shots.load(shot_path);
    Owner<SDL_Window,SDL_DestroyWindow> window(SDL_CreateWindow("Slamtilt - Reborn | The Pirate",960,800,SDL_WINDOW_RESIZABLE|SDL_WINDOW_HIGH_PIXEL_DENSITY),SDL_DestroyWindow);
    if(!window)throw std::runtime_error(SDL_GetError());
    Owner<SDL_Renderer,SDL_DestroyRenderer> renderer(create_presentation_renderer(window.get(),!frames||realtime_ms),SDL_DestroyRenderer);
    if(!renderer)throw std::runtime_error(SDL_GetError());
    Presentation presentation(renderer.get());
    PortOptions options;options.load(!frames&&!realtime_ms);
    options.shaders_available=presentation.available();options.shader_status=presentation.status();
    if(fullscreen)options.settings.fullscreen=true;
    else if(windowed||frames||realtime_ms)options.settings.fullscreen=false;
    SDL_SetWindowMinimumSize(window.get(),320,240);
    bool applied_fullscreen=false;int applied_width=960,applied_height=800;
    int applied_fullscreen_mode=-1;
    std::vector<SDL_DisplayMode> display_modes;
    int mode_count=0;
    if(auto** modes=SDL_GetFullscreenDisplayModes(SDL_GetDisplayForWindow(window.get()),&mode_count)){
      for(int i=0;i<mode_count;++i){
        display_modes.push_back(*modes[i]);const SDL_Point size{modes[i]->w,modes[i]->h};
        if(std::none_of(options.exclusive_resolutions.begin(),options.exclusive_resolutions.end(),[&](const auto& p){return p.x==size.x&&p.y==size.y;}))options.exclusive_resolutions.push_back(size);
      }
      SDL_free(modes);
    }
    Owner<SDL_Texture,SDL_DestroyTexture> table(texture(renderer.get(),320,600),SDL_DestroyTexture);
    Owner<SDL_Texture,SDL_DestroyTexture> target(texture(renderer.get(),320,400,true),SDL_DestroyTexture);
    Owner<SDL_Texture,SDL_DestroyTexture> ball_texture(texture(renderer.get(),16,15),SDL_DestroyTexture);
    Owner<SDL_Texture,SDL_DestroyTexture> dmd_texture(texture(renderer.get(),96,20),SDL_DestroyTexture);
    SDL_UpdateTexture(table.get(),nullptr,image.rgba.data(),320*4);
    std::vector<Owner<SDL_Texture,SDL_DestroyTexture>> flipper_textures;
    for(const auto& sprite:flippers)flipper_textures.emplace_back(texture(renderer.get(),sprite.width,sprite.height),SDL_DestroyTexture);
    std::vector<Owner<SDL_Texture,SDL_DestroyTexture>> lamp_textures;
    for(const auto& sprite:lamps)lamp_textures.emplace_back(texture(renderer.get(),sprite.width,sprite.height),SDL_DestroyTexture);
    PirateTiming timing_profile;unsigned input_index=0;
    const auto upload=[&](SDL_Texture* tex,const void* pixels,int pitch){++timing_profile.uploads;SDL_UpdateTexture(tex,nullptr,pixels,pitch);};
    std::vector<int> uploaded_lamps(lamps.size(),-1);
    std::vector<std::vector<std::uint8_t>> uploaded_flippers(flippers.size());
    std::array<std::uint8_t,1920*4> uploaded_dmd{};bool have_dmd=false;
    UiSkin ui;
    bool running=true,paused=false,focused=true,left=false,right=false,minimized=false,audio_muted=false;
    std::string failure;
    PirateCamera camera;std::vector<PirateCamera::Ball> camera_balls;
    unsigned rendered=0;
    std::uint64_t last=SDL_GetTicksNS(),accumulator=0;
    nlohmann::json states=nlohmann::json::array(),scene_origins=nlohmann::json::array();
    nlohmann::json audio_events=nlohmann::json::array(),audio_checks=nlohmann::json::array(),audio_window_events=nlohmann::json::array();
    std::uint64_t audio_tick=0;
    int audio_queued=0;bool audio_enabled=false;
    const auto deliver_audio=[&]{
      for(const auto& request:session.take_audio_requests()){
        if(!audio_trace_path.empty())audio_events.push_back({audio_tick,request.service,request.bank,request.order,request.descriptor});
#ifdef SLAM_AUDIO_XMP
        if(audio)audio->request(request.service,request.bank,request.order,request.descriptor);
#endif
      }
    };
    deliver_audio();
    nlohmann::json nudge_states=nlohmann::json::array(),nudge_checks=nlohmann::json::array();
    nlohmann::json magnasaver_states=nlohmann::json::array();
    nlohmann::json special_checks=nlohmann::json::array();
    nlohmann::json timing=nlohmann::json::array(),session_ui_frames=nlohmann::json::array();
    const auto session_ui_started=SDL_GetTicksNS();
    nlohmann::json dmd_hashes=nlohmann::json::array();
    nlohmann::json lifecycle=nlohmann::json::array(),score_hashes=nlohmann::json::array(),lamp_hashes=nlohmann::json::array(),rule_hashes=nlohmann::json::array(),video_hashes=nlohmann::json::array(),ball_pool_hashes=nlohmann::json::array();
    if(!trace_path.empty())states.push_back(session.ball());
    while(running){
      const auto frame_begin=SDL_GetTicksNS();
      const auto ticks_begin=session.ticks();
      if(realtime_steps){if(frames||replay_path.empty()||timing_inputs)throw std::runtime_error("Realtime steps require a replay and no fixed frames/timing inputs");if(!realtime_ms)realtime_ms=realtime_steps*5+30000;}
    if(timing_inputs&&input_index<16&&session.ticks()>=360+input_index*20){
        SDL_PumpEvents();SDL_Event e{};e.type=input_index%2?SDL_EVENT_KEY_UP:SDL_EVENT_KEY_DOWN;
        e.key.scancode=(input_index/2)%2?SDL_SCANCODE_RSHIFT:SDL_SCANCODE_LSHIFT;
        e.key.key=SDL_GetKeyFromScancode(e.key.scancode,SDL_KMOD_NONE,false);SDL_PushEvent(&e);++input_index;
      }
      // SDL_PollEvent pumps platform events before dequeueing. Collect those
      // before appending scripted events, so startup focus gain cannot overtake
      // the same frame's synthetic focus loss. Ordinary play is unchanged.
      if(!audio_acceptance_path.empty()||!nudge_acceptance_path.empty()||!special_acceptance_path.empty())SDL_PumpEvents();
      if(!audio_acceptance_path.empty()){
        SDL_Event injected{};
        const auto key=[&](SDL_Scancode scan){injected.type=SDL_EVENT_KEY_DOWN;injected.key.scancode=scan;injected.key.key=SDL_GetKeyFromScancode(scan,SDL_KMOD_NONE,false);SDL_PushEvent(&injected);};
        switch(rendered){
          case 2:injected.type=SDL_EVENT_WINDOW_FOCUS_LOST;break;
          case 3:injected.type=SDL_EVENT_WINDOW_FOCUS_GAINED;break;
          case 4:injected.type=SDL_EVENT_WINDOW_MINIMIZED;break;
          case 5:injected.type=SDL_EVENT_WINDOW_RESTORED;break;
          case 6:case 7:key(SDL_SCANCODE_P);break;
          case 8:case 9:key(SDL_SCANCODE_ESCAPE);break;
          case 10:case 11:key(SDL_SCANCODE_M);break;
          case 12:key(SDL_SCANCODE_R);break;
          default:break;
        }
        if(injected.type&&injected.type!=SDL_EVENT_KEY_DOWN)SDL_PushEvent(&injected);
      }
      if(!nudge_acceptance_path.empty()){
        const auto window_event=[](Uint32 type){SDL_Event e{};e.type=type;SDL_PushEvent(&e);};
        const auto key=[](SDL_Scancode scan,bool down=true,bool repeat=false){SDL_Event e{};e.type=down?SDL_EVENT_KEY_DOWN:SDL_EVENT_KEY_UP;e.key.scancode=scan;e.key.key=SDL_GetKeyFromScancode(scan,SDL_KMOD_NONE,false);e.key.repeat=repeat;SDL_PushEvent(&e);};
        switch(rendered){
          case 1:key(SDL_SCANCODE_LALT);break;
          case 2:key(SDL_SCANCODE_LALT,true,true);break;
          case 3:key(SDL_SCANCODE_LALT,false);break;
          case 4:window_event(SDL_EVENT_WINDOW_FOCUS_LOST);key(SDL_SCANCODE_RALT);break;
          case 5:window_event(SDL_EVENT_WINDOW_FOCUS_GAINED);key(SDL_SCANCODE_RALT);break;
          case 6:key(SDL_SCANCODE_P);key(SDL_SCANCODE_SPACE);break;
          case 7:key(SDL_SCANCODE_P);key(SDL_SCANCODE_SPACE);break;
          case 8:key(SDL_SCANCODE_ESCAPE);key(SDL_SCANCODE_LALT);break;
          case 9:key(SDL_SCANCODE_ESCAPE);key(SDL_SCANCODE_LALT);break;
          case 10:window_event(SDL_EVENT_WINDOW_MINIMIZED);key(SDL_SCANCODE_SPACE);break;
          case 11:window_event(SDL_EVENT_WINDOW_RESTORED);key(SDL_SCANCODE_SPACE);break;
          case 12:options.settings.keys[static_cast<unsigned>(PortAction::NudgeLeft)]=SDL_SCANCODE_Z;key(SDL_SCANCODE_LALT);key(SDL_SCANCODE_Z);break;
          default:break;
        }
      }
      if(!special_acceptance_path.empty()){
        const auto window_event=[](Uint32 type){SDL_Event e{};e.type=type;SDL_PushEvent(&e);};
        const auto key=[](SDL_Scancode scan,bool down=true,bool repeat=false){SDL_Event e{};e.type=down?SDL_EVENT_KEY_DOWN:SDL_EVENT_KEY_UP;e.key.scancode=scan;e.key.key=SDL_GetKeyFromScancode(scan,SDL_KMOD_NONE,false);e.key.repeat=repeat;SDL_PushEvent(&e);};
        switch(rendered){
          case 1:key(SDL_SCANCODE_LCTRL);break;
          case 2:key(SDL_SCANCODE_LCTRL,true,true);break;
          case 3:key(SDL_SCANCODE_LCTRL,false);break;
          case 4:window_event(SDL_EVENT_WINDOW_FOCUS_LOST);key(SDL_SCANCODE_LCTRL);break;
          case 5:window_event(SDL_EVENT_WINDOW_FOCUS_GAINED);key(SDL_SCANCODE_LCTRL);break;
          case 6:key(SDL_SCANCODE_P);key(SDL_SCANCODE_LCTRL);break;
          case 7:key(SDL_SCANCODE_P);key(SDL_SCANCODE_LCTRL);break;
          case 8:key(SDL_SCANCODE_ESCAPE);key(SDL_SCANCODE_LCTRL);break;
          case 9:key(SDL_SCANCODE_ESCAPE);key(SDL_SCANCODE_LCTRL);break;
          case 10:window_event(SDL_EVENT_WINDOW_MINIMIZED);key(SDL_SCANCODE_LCTRL);break;
          case 11:window_event(SDL_EVENT_WINDOW_RESTORED);key(SDL_SCANCODE_LCTRL);break;
          case 12:options.settings.keys[static_cast<unsigned>(PortAction::SpecialLeft)]=SDL_SCANCODE_Z;key(SDL_SCANCODE_LCTRL);key(SDL_SCANCODE_Z);break;
          case 13:key(SDL_SCANCODE_RCTRL);break;
          default:break;
        }
      }
      SDL_Event event;
      while(SDL_PollEvent(&event)){
        if(!audio_acceptance_path.empty()&&(event.type==SDL_EVENT_WINDOW_FOCUS_LOST||event.type==SDL_EVENT_WINDOW_FOCUS_GAINED||event.type==SDL_EVENT_WINDOW_MINIMIZED||event.type==SDL_EVENT_WINDOW_RESTORED))
          audio_window_events.push_back({{"frame",rendered},{"type",event.type},{"window_id",event.window.windowID},{"time",event.common.timestamp}});
        if(event.type==SDL_EVENT_QUIT)running=false;
        if(event.type==SDL_EVENT_WINDOW_FOCUS_LOST){focused=false;left=right=false;session.flippers(false,false);}
        if(event.type==SDL_EVENT_WINDOW_FOCUS_GAINED)focused=true;
        if(event.type==SDL_EVENT_WINDOW_MINIMIZED){minimized=true;left=right=false;session.flippers(false,false);}
        if(event.type==SDL_EVENT_WINDOW_RESTORED)minimized=false;
        if(options.handle(event)){left=right=false;session.flippers(false,false);continue;}
        if(replay_only&&(event.type==SDL_EVENT_KEY_DOWN||event.type==SDL_EVENT_KEY_UP||event.type==SDL_EVENT_TEXT_INPUT)&&!(event.type!=SDL_EVENT_TEXT_INPUT&&(event.key.key==SDLK_P||event.key.key==SDLK_M)))continue;
        if(event.type!=SDL_EVENT_KEY_DOWN&&event.type!=SDL_EVENT_KEY_UP)continue;
        const bool down=event.type==SDL_EVENT_KEY_DOWN;
        if(event.key.repeat)continue;
        if(!timing_path.empty()&&down&&(event.key.scancode==options.settings.key(PortAction::LeftFlipper)||event.key.scancode==options.settings.key(PortAction::RightFlipper))){
          const unsigned side=event.key.scancode==options.settings.key(PortAction::LeftFlipper)?0:1;
          timing_profile.input(side,event.common.timestamp,session.poses()[side]);
        }
        if(session.initials_active()&&failure.empty()){
          if(down){
            if(event.key.key==SDLK_RETURN)session.initials_character('\r');
            else if(event.key.key==SDLK_BACKSPACE)session.initials_character('\b');
            else if(event.key.key>=32&&event.key.key<=126)session.initials_character(char(event.key.key));
          }
          continue;
        }
        if(event.key.scancode==options.settings.key(PortAction::LeftFlipper))left=down;
        if(event.key.scancode==options.settings.key(PortAction::RightFlipper))right=down;
        if(down&&event.key.scancode==SDL_SCANCODE_P)paused=!paused;
        if(down&&event.key.scancode==SDL_SCANCODE_M)audio_muted=!audio_muted;
        if(down&&(event.key.scancode==SDL_SCANCODE_R||event.key.scancode==SDL_SCANCODE_F1)){
          const bool reset=!session.new_game()&&event.key.scancode==SDL_SCANCODE_R;
          if(reset){camera=PirateCamera{};camera_balls.clear();const auto records=session.highscores();session.reset();session.set_highscores(records);replay.reset();shots.reset();}
          failure.clear();left=right=false;
#ifdef SLAM_AUDIO_XMP
          if(audio&&reset)audio->restart();
#endif
        }
        if(down&&!paused&&!options.open&&focused&&!minimized&&failure.empty()&&!physics_only){
          try{
            const auto nudge=[&](int direction){
              const bool accepted=session.nudge(direction);
              if(!nudge_acceptance_path.empty())nudge_checks.push_back({{"frame",rendered},{"direction",direction},{"accepted",accepted}});
            };
            if(event.key.scancode==options.settings.key(PortAction::NudgeLeft))nudge(-1);
            if(event.key.scancode==options.settings.key(PortAction::NudgeRight))nudge(1);
            if(event.key.scancode==options.settings.key(PortAction::NudgeUp))nudge(0);
          }catch(const std::exception& error){failure=error.what();std::cerr<<failure<<'\n';}
        }
        if(down&&!paused&&!options.open&&focused&&!minimized&&failure.empty()){
          try{
            if(event.key.scancode==options.settings.key(PortAction::Plunger))session.launch();
            if(!physics_only&&event.key.scancode==options.settings.key(PortAction::SpecialLeft)){
              const bool accepted=session.special_left();
              if(!special_acceptance_path.empty())special_checks.push_back({{"frame",rendered},{"scancode",event.key.scancode},{"accepted",accepted}});
            }
          }catch(const std::exception& error){failure=error.what();std::cerr<<failure<<'\n';}
        }
      }
      const auto now=SDL_GetTicksNS();
      const auto raw_delta=now-last;
      const auto accepted_delta=frames&&!realtime_ms?20000000:std::min<std::uint64_t>(raw_delta,100000000);
      accumulator+=accepted_delta;last=now;
      const bool advancing=!paused&&!options.open&&focused&&!minimized&&failure.empty();
      if(!advancing)accumulator=0;
      const auto sim_begin=SDL_GetTicksNS();
      try {
        if(advancing)session.flippers(left,right);
        audio_tick=session.ticks();deliver_audio();
        while(advancing&&accumulator>=5000000){
          if(!replay_path.empty())replay.apply(session,session.ticks(),left,right);
          else if(autoplay&&session.ticks()==200)session.launch();
          if(autoplay_flippers&&(session.ticks()==400||session.ticks()==440||session.ticks()==600||session.ticks()==640)){
            left=session.ticks()>=400&&session.ticks()<440;
            right=session.ticks()>=600&&session.ticks()<640;session.flippers(left,right);
          }
          if(!shot_path.empty())shots.apply(session,definition.geometry);
          const auto camera_phase=session.phase();
          audio_tick=session.ticks();session.step();deliver_audio();accumulator-=5000000;
          camera.step(camera_phase,camera_balls);
          if(!timing_path.empty())timing_profile.observe(session.poses(),session.ticks());
          if(!trace_path.empty()&&(full_state_trace||!shot_path.empty())){magnasaver_states.push_back(session.magnasaver_state());rule_hashes.push_back(sha256(session.rule_state()));video_hashes.push_back(sha256(session.video_state()));ball_pool_hashes.push_back(sha256(session.ball_pool_state()));}
          if(!trace_path.empty())states.push_back(session.ball());
          if(!trace_path.empty()){timing.push_back(session.timing_state());nudge_states.push_back(session.nudge_state());}
          if(!trace_path.empty()&&!physics_only){const auto pixels=session.dmd_pixels();dmd_hashes.push_back(sha256({pixels.begin(),pixels.end()}));}
          if(!trace_path.empty()&&!physics_only){lifecycle.push_back(session.lifecycle_state());const auto records=session.highscores();score_hashes.push_back(sha256({records.begin(),records.end()}));}
          if(!trace_path.empty()&&!physics_only)lamp_hashes.push_back(sha256(session.lamp_states()));
          if(realtime_steps&&session.ticks()%2000==0)std::cerr<<"Pirate realtime "<<session.ticks()<<'/'<<realtime_steps<<" phase="<<session.phase()<<'\n';
          if(realtime_steps&&session.ticks()>=realtime_steps)break;
        }
#ifdef SLAM_AUDIO_XMP
        if(audio){
          audio->set_paused(!advancing||audio_muted);
          audio->set_levels(options.settings.volume,options.settings.music_volume,options.settings.sfx_volume);
          audio->pump();audio_queued=audio->queued_bytes();audio_enabled=true;
          if(!audio_acceptance_path.empty())audio_checks.push_back({{"frame",rendered},{"ticks",session.ticks()},
            {"paused",audio->device_paused()},{"expected_paused",!advancing||audio_muted},{"queued_bytes",audio_queued}});
        }
#endif
      }catch(const std::exception& error){failure=error.what();std::cerr<<"Pirate step "<<session.ticks()<<": "<<failure<<'\n';}
      if(session.highscores()!=saved_records){
        const auto records=session.highscores();
        if(highscore_path.empty()||score_store.save(highscore_path,records))saved_records=records;
        else options.error=score_store.error;
      }
      const auto render_begin=SDL_GetTicksNS();
      const auto ball=session.ball();
      const auto position=ball_display_position(value(ball,0),value(ball,4),value(ball,8),value(ball,12),unsigned(accumulator/1000000)%5);
      std::vector<std::pair<std::array<std::uint8_t,100>,std::array<int,2>>> balls;
      for(unsigned i=0;i<std::min(8u,session.ball_count());++i){
        const auto state=session.ball(i);
        balls.push_back({state,ball_display_position(value(state,0),value(state,4),value(state,8),value(state,12),unsigned(accumulator/1000000)%5)});
      }
      std::stable_sort(balls.begin(),balls.end(),[](const auto&a,const auto&b){return a.second[1]<b.second[1];});
      // Original camera consumes the previous rendered projected coordinates,
      // not a new physics center on every5ms tick. Its state stays outside the
      // verified gameplay machine, whose integer fixtures omit render writes.
      const int scroll=camera.scroll(unsigned(accumulator/1000000)%5);
      camera_balls.clear();
      for(const auto& shown:balls)camera_balls.push_back({shown.second[1],unsigned(value(shown.first,0x58))&0xffff});
      const auto nudge=session.nudge_state();
      const auto origin=pirate_scene_origin(scroll,std::int32_t(nudge[9]),std::int32_t(nudge[7]));
      nlohmann::json camera_inputs=nlohmann::json::array();
      if(!trace_path.empty())for(const auto& b:camera_balls)camera_inputs.push_back({b.y,b.state});
      if(!trace_path.empty())scene_origins.push_back({{"tick",session.ticks()},{"camera_scroll",scroll},
        {"horizontal_pixels",std::int32_t(nudge[9])},{"vertical_fixed",std::int32_t(nudge[7])},{"origin",origin},{"camera_state",camera.state()},{"projected_balls",camera_inputs}});
      SDL_SetRenderTarget(renderer.get(),target.get());
      SDL_SetRenderDrawColor(renderer.get(),0,0,0,255);SDL_RenderClear(renderer.get());
      const SDL_FRect table_destination{float(origin[0]),float(origin[1]),320,600};
      SDL_RenderTexture(renderer.get(),table.get(),nullptr,&table_destination);
      for(std::size_t i=0;i<lamps.size();++i){
        const auto& lamp=lamps[i];const auto frame=lamp.frame(session.executable_image());const auto& pixels=lamp.rgba[frame];
        if(uploaded_lamps[i]!=int(frame)){upload(lamp_textures[i].get(),pixels.data(),lamp.width*4);uploaded_lamps[i]=int(frame);}
        const SDL_FRect destination{float(lamp.x+origin[0]),float(lamp.y+origin[1]),float(lamp.width),float(lamp.height)};
        SDL_RenderTexture(renderer.get(),lamp_textures[i].get(),nullptr,&destination);
      }
      const auto poses=session.poses();
      for(std::size_t i=0;i<flippers.size();++i){
        const auto& sprite=flippers[i];
        const auto pixels=lamps.empty()?sprite.rgba.at(sprite.frame(poses[i])):
          compose_table_flipper(flipper_profiles[i],sprite,sprite.frame(poses[i]),image,session.executable_image(),session.table_data());
        if(uploaded_flippers[i]!=pixels){upload(flipper_textures[i].get(),pixels.data(),sprite.width*4);uploaded_flippers[i]=pixels;}
        const SDL_FRect destination{float(sprite.x+origin[0]),float(sprite.y+origin[1]),float(sprite.width),float(sprite.height)};
        SDL_RenderTexture(renderer.get(),flipper_textures[i].get(),nullptr,&destination);
      }
      for(const auto& displayed:balls){
        const auto& state=displayed.first;const auto& point=displayed.second;
        if(point[0]<0||point[0]>303||point[1]<0||point[1]>=600)continue;
        auto mask=outline;
        const auto bitmap=std::uint32_t(value(state,0x54));
        if(bitmap>=0x1100000)mask=windows_ball_occlusion(outline,session.table_data(),bitmap-0x1100000,point[0],point[1]);
        const auto& pixels=ball_pixels[unsigned(point[1])/8];
        std::array<std::uint8_t,16*15*4> rgba{};
        for(std::size_t i=0;i<pixels.size();++i){
          for(unsigned c=0;c<3;++c)rgba[i*4+c]=image.palette_rgba[pixels[i]*4+c];
          rgba[i*4+3]=255-mask.preserve_background[i];
        }
        upload(ball_texture.get(),rgba.data(),16*4);
        const SDL_FRect destination{float(point[0]+origin[0]),float(point[1]+origin[1]),16,15};
        SDL_RenderTexture(renderer.get(),ball_texture.get(),nullptr,&destination);
      }
      SDL_SetRenderTarget(renderer.get(),nullptr);
      const auto& settings=options.settings;
      if(settings.fullscreen!=applied_fullscreen||settings.fullscreen_mode!=applied_fullscreen_mode||settings.window_width!=applied_width||settings.window_height!=applied_height){
        const SDL_DisplayMode* mode=nullptr;
        if(settings.fullscreen&&settings.fullscreen_mode==1){
          for(const auto& candidate:display_modes)
            if(candidate.w==settings.window_width&&candidate.h==settings.window_height&&(!mode||candidate.refresh_rate>mode->refresh_rate))mode=&candidate;
        }
        const bool available=!settings.fullscreen||settings.fullscreen_mode!=1||mode;
        if(available&&apply_window_mode(window.get(),settings.fullscreen,mode,settings.window_width,settings.window_height)){
          applied_fullscreen=settings.fullscreen;applied_fullscreen_mode=settings.fullscreen_mode;
          applied_width=settings.window_width;applied_height=settings.window_height;
        }else options.error=available?SDL_GetError():"Selected exclusive resolution unavailable";
      }
      int width=0,height=0;SDL_GetRenderOutputSize(renderer.get(),&width,&height);
      SDL_SetRenderDrawColor(renderer.get(),8,12,20,255);SDL_RenderClear(renderer.get());
      auto layout=display_layout(width,height,physics_only?3:settings.dmd_position,settings.dmd_size,settings.zoom,settings.aspect,float(position[0]+7),float(position[1]-scroll+7));
      if(settings.dmd_position==3){layout.dmd.x=(width-layout.dmd.w)*settings.overlay_x;layout.dmd.y=(height-layout.dmd.h)*settings.overlay_y;}
      SDL_SetTextureScaleMode(target.get(),settings.smooth?SDL_SCALEMODE_LINEAR:SDL_SCALEMODE_NEAREST);
      const SDL_Rect clip{int(layout.viewport.x),int(layout.viewport.y),int(layout.viewport.w),int(layout.viewport.h)};
      SDL_SetRenderClipRect(renderer.get(),&clip);
      presentation.draw(target.get(),layout.table,settings.visual);
      SDL_SetRenderClipRect(renderer.get(),nullptr);
      if(!physics_only){
        const auto pixels=session.dmd_pixels();const auto colors=session.dmd_palette_indices();
        std::array<std::uint8_t,1920*4> rgba{};
        for(unsigned i=0;i<pixels.size();++i){
          const auto level=pixels[i];
          for(unsigned c=0;c<3;++c){
            if(settings.color==0)rgba[i*4+c]=image.palette_rgba[colors[level]*4+c];
            else if(settings.color==1)rgba[i*4+c]=level*(c==0?85:c==1?53:0);
            else if(settings.color==2)rgba[i*4+c]=level*85;
            else rgba[i*4+c]=level*(c==0?settings.custom_r:c==1?settings.custom_g:settings.custom_b)/3;
          }
          rgba[i*4+3]=255;
        }
        if(!have_dmd||uploaded_dmd!=rgba){upload(dmd_texture.get(),rgba.data(),96*4);uploaded_dmd=rgba;have_dmd=true;}
        presentation.draw(dmd_texture.get(),layout.dmd,settings.visual,true);
      }
      if(!failure.empty()||paused){
        const SDL_FRect panel{16,16,float(width)-32,90};UiSkin::round_rect(renderer.get(),panel,12,{8,12,20,240});
        ui.text(renderer.get(),failure.empty()?"Paused":"Gameplay stopped — R to restart",28,28,20,{255,220,160,255},true);
        if(!failure.empty())ui.text(renderer.get(),failure,28,60,14,{255,180,180,255});
      }
      if(session.game_over()&&failure.empty()){
        const SDL_FRect panel{16,float(height)-64,float(width)-32,48};UiSkin::round_rect(renderer.get(),panel,12,{8,12,20,235});
        ui.text(renderer.get(),"GAME OVER  ·  R / F1: New Game",28,float(height)-53,20,{255,220,160,255},true);
      }
      if(!shot_path.empty())ui.text(renderer.get(),"DIAGNOSTIC SHOTS",20,16,16,{255,220,160,255},true);
      options.draw(renderer.get(),width,height);
      ++rendered;
      if((realtime_steps&&session.ticks()>=realtime_steps)||(frames&&rendered>=frames)||(realtime_ms&&SDL_GetTicksNS()-timing_profile.start>=std::uint64_t(realtime_ms)*1000000)){
        if(!capture.empty()){
          Owner<SDL_Surface,SDL_DestroySurface> shot(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);
          if(!shot||!SDL_SaveBMP(shot.get(),capture.c_str()))throw std::runtime_error(SDL_GetError());
        }
        running=false;
      }
      if(!trace_path.empty())session_ui_frames.push_back({{"frame",rendered},{"tick",session.ticks()},{"elapsed_ms",double(SDL_GetTicksNS()-session_ui_started)/1e6},{"focused",focused},{"paused",paused},{"menu",options.open},
#ifdef SLAM_AUDIO_XMP
        {"audio_device_paused",audio?audio->device_paused():true},
#endif
        {"audio_queued_bytes",audio_queued}});
      const auto present_begin=SDL_GetTicksNS();SDL_RenderPresent(renderer.get());
      if(!timing_path.empty())timing_profile.frames.push_back({frame_begin-timing_profile.start,SDL_GetTicksNS()-frame_begin,render_begin-sim_begin,present_begin-render_begin,SDL_GetTicksNS()-present_begin,session.ticks(),session.ticks()-ticks_begin,advancing,audio_queued,accepted_delta,raw_delta});
#ifdef __EMSCRIPTEN__
      // Even bounded replays must let the browser drain rendering and input work.
      SDL_Delay(1);
#else
      if(!frames||realtime_ms)SDL_Delay(1);
#endif
    }
    if(!timing_path.empty())timing_profile.write(timing_path,failure,window.get(),renderer.get());
    if(!nudge_acceptance_path.empty()){std::ofstream out(nudge_acceptance_path);out<<nudge_checks.dump()<<'\n';if(!out)throw std::runtime_error("Cannot write nudge acceptance");}
    if(!special_acceptance_path.empty()){std::ofstream out(special_acceptance_path);out<<special_checks.dump()<<'\n';if(!out)throw std::runtime_error("Cannot write special acceptance");}
    if(!trace_path.empty()){
      nlohmann::json trace={{"ui_frames",session_ui_frames},{"table","pirate"},{"presentation_origins",scene_origins},{"tick_count",session.ticks()},{"phase",session.phase()},{"states",states},{"timing",timing},{"nudge",nudge_states},{"dmd_sha256",dmd_hashes},{"lifecycle",lifecycle},{"highscore_sha256",score_hashes},{"lamp_sha256",lamp_hashes},{"rule_sha256",rule_hashes},{"video_sha256",video_hashes},{"ball_pool_sha256",ball_pool_hashes},{"error",failure}};
      if(full_state_trace||!shot_path.empty())trace["magnasaver_state"]=magnasaver_states;
      std::ofstream out(trace_path);out<<trace.dump()<<'\n';
      if(!out)throw std::runtime_error("Cannot write Pirate rendering trace");
    }
    if(!audio_trace_path.empty()){
      std::ofstream out(audio_trace_path);out<<nlohmann::json({{"events",audio_events},{"enabled",audio_enabled},{"queued_bytes",audio_queued},{"error",failure}}).dump()<<'\n';
      if(!out)throw std::runtime_error("Cannot write Pirate audio trace");
    }
    if(!audio_acceptance_path.empty()){
      bool passed=audio_enabled&&audio_checks.size()==14&&failure.empty();
      for(std::size_t i=0;i<audio_checks.size();++i){
        const auto& check=audio_checks[i];passed=passed&&check["paused"]==check["expected_paused"];
        if(!check["paused"].get<bool>())passed=passed&&check["queued_bytes"].get<int>()>0;
        if(i==2||i==4||i==6||i==8)passed=passed&&check["ticks"]==audio_checks[i-1]["ticks"];
        if(i==3||i==5||i==7||i==9||i==11)passed=passed&&check["ticks"].get<unsigned>()>audio_checks[i-1]["ticks"].get<unsigned>();
      }
      std::ofstream out(audio_acceptance_path);out<<nlohmann::json({{"passed",passed},{"checks",audio_checks},{"window_events",audio_window_events},{"game_window_id",SDL_GetWindowID(window.get())},{"fullscreen",bool(SDL_GetWindowFlags(window.get())&SDL_WINDOW_FULLSCREEN)},{"video_driver",SDL_GetCurrentVideoDriver()?SDL_GetCurrentVideoDriver():""},{"audio_driver",SDL_GetCurrentAudioDriver()?SDL_GetCurrentAudioDriver():""},{"error",failure}}).dump()<<'\n';
      if(!out||!passed)throw std::runtime_error("Pirate SDL audio acceptance failed");
    }
    return failure.empty()?0:1;
  }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
}
