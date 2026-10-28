// Bounded table-independent Retail vertical slice. Original code runs as static
// C++; unsupported calls throw. No replacement physics or rule fields.
#include "physics/pirate_step_lift.h"
#include "assets/asset_source.h"
#include "assets/table_definition.h"
#include "assets/table_sprites.h"
#include "assets/table_lamps.h"
#include "assets/ball_mask.h"
#include "assets/ball_occlusion.h"
#include "core/sha256.h"
#include "renderer/ball_display.h"
#include "renderer/display_layout.h"
#include "renderer/presentation.h"
#include "frontend/port_options.h"
#include "frontend/pirate_highscores.h"
#include <SDL3/SDL.h>
#include "frontend/window_mode.h"
#ifdef SLAM_AUDIO_XMP
#include "audio/native_audio.h"
#include "audio/space_sound_assets.h"
#include "audio/demon_sound_assets.h"
#endif
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <memory>
#include <map>
#include <algorithm>
using json=nlohmann::json;
namespace {
std::vector<std::uint8_t> read(const std::filesystem::path& p){
 std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("Missing file: "+p.string());
 return {std::istreambuf_iterator<char>(f),{}};
}
json read_json(const std::filesystem::path& p){std::ifstream f(p);json j;f>>j;return j;}
template<class T,auto destroy>using Owner=std::unique_ptr<T,decltype(destroy)>;
void check(bool ok){if(!ok)throw std::runtime_error(SDL_GetError());}
struct SDLGuard{~SDLGuard(){SDL_Quit();}};
}
int main(int argc,char** argv){
 try{
  if(argc<4)throw std::runtime_error("Usage: slamslice TABLE PREPARED DAT [--frames N] [--replay JSON] [--trace JSON] [--capture BMP]");
  const std::string table=argv[1];const std::filesystem::path prepared=argv[2],dat_path=argv[3];
  unsigned frames=0,realtime_steps=0;bool replay_only=false,fullscreen=false,no_audio=false,force_audio=false,force_presentation=false,windowed=false,menu_at_start=false,persist_options=false;std::filesystem::path replay,trace,capture,diagnostics,audio_trace,highscore_path,ui_events_path;
  for(int i=4;i<argc;++i){const std::string a=argv[i];if(a=="--replay-only"){replay_only=true;continue;}if(a=="--persist-options"){persist_options=true;continue;}if(a=="--presentation"){force_presentation=true;continue;}if(a=="--windowed"){windowed=true;continue;}if(a=="--menu"){force_presentation=true;menu_at_start=true;continue;}if(a=="--no-audio"){no_audio=true;continue;}if(a=="--audio"){force_audio=true;continue;}if(a=="--fullscreen"){fullscreen=true;continue;}if(i+1>=argc)throw std::runtime_error("Missing argument");
   if(a=="--frames")frames=std::stoul(argv[++i]);else if(a=="--realtime-steps")realtime_steps=std::stoul(argv[++i]);else if(a=="--replay")replay=argv[++i];else if(a=="--trace")trace=argv[++i];else if(a=="--diagnostic-shots")diagnostics=argv[++i];else if(a=="--audio-trace")audio_trace=argv[++i];else if(a=="--highscore-file")highscore_path=argv[++i];else if(a=="--ui-events")ui_events_path=argv[++i];else if(a=="--capture")capture=argv[++i];else throw std::runtime_error("Unknown argument: "+a);
  }
  if(replay_only&&replay.empty())throw std::runtime_error("--replay-only requires --replay");
  slam::infer_asset_source(dat_path.parent_path());
  auto definition=slam::load_table_definition_for_data(slam::default_table_profiles(),table,dat_path);
  auto metadata=read_json(prepared/"summary.json");
  if(metadata.at("build_sha256")!=definition.geometry_build.executable_sha256||metadata.at("dat_sha256")!=definition.geometry.dat_sha256)throw std::runtime_error("Unsupported original table context");
  slam::PirateStepLift m;
  m.image=read(prepared/"human-image.bin");m.runtime=read(prepared/"human-runtime.bin");m.dat=read(dat_path);
  for(auto item:{std::pair{"human-image.bin",&m.image},std::pair{"human-runtime.bin",&m.runtime},std::pair{"human-dat.bin",&m.dat}})
   if(slam::sha256(*item.second)!=metadata.at("context_hashes").at(item.first))throw std::runtime_error("Context SHA mismatch: "+std::string(item.first));
  slam::validate_table_dat(definition,m.dat);

  std::map<unsigned,std::vector<json>> inputs;
  if(!replay.empty()){const auto schedule=read_json(replay);for(const auto&e:schedule.at("inputs"))inputs[e.at("tick")].push_back(e);}
  std::map<unsigned,json> shots;
  if(!diagnostics.empty()){const auto schedule=read_json(diagnostics);for(const auto&e:schedule.at("diagnostic_shots")){const unsigned tick=e.at("tick");if(!shots.emplace(tick,e).second)throw std::runtime_error("Duplicate diagnostic shot");}}
  auto diagnostic=[&](const json&e){
   const unsigned index=e.value("ball",0u),layer=e.at("layer");const int x=e.at("x"),y=e.at("y");
   if(index>=std::min(8u,m.rd(0x46c67c,4))||layer>=definition.geometry.layers.size()||x<0||x>=320||y<0||y>=600)throw std::runtime_error("Invalid diagnostic shot");
   const unsigned b=0x46c15c+100*index;if(m.rd(b+0x58,2)!=2)throw std::runtime_error("Diagnostic shot requires a FREE ball");const auto&l=definition.geometry.layers[layer];
   for(const auto&v:std::array<std::array<unsigned,3>,14>{{{0,unsigned(x)<<16,4},{4,unsigned(y)<<16,4},{8,unsigned(x)<<16,4},{12,unsigned(y)<<16,4},{20,0,4},{24,0,4},{0x40,0x1100000+l.hit_offset,4},{0x44,0x1100000+l.normal_offset,4},{0x54,0x1100000+l.render_offset,4},{0x4c,l.stride,4},{0x50,l.planes,4},{0x48,layer,2},{0x38,65535,2},{0x3a,65535,2}}})m.wr(b+v[0],v[1],v[2]);
  };
  const auto image=slam::load_windows_table(dat_path);
  const auto sprites=slam::load_table_flippers(dat_path,definition,image);
  const auto flipper_profiles=slam::table_flipper_sprite_profiles(definition);
  const auto lamps=slam::load_table_lamps(dat_path,definition,image,m.image);
  const auto outline=slam::load_windows_ball_mask(dat_path.parent_path()/"MAIN.DAT");
  const auto pixel_bank=slam::load_windows_ball_pixel_bank(dat_path.parent_path()/"MAIN.DAT");
  if(!diagnostics.empty()&&!highscore_path.empty())throw std::runtime_error("Diagnostic shots use no persistent highscore profile");
  check(SDL_Init(SDL_INIT_VIDEO));SDLGuard sdl;
  const bool presenting=force_presentation||(!frames&&(table=="space"||table=="demon"));
  const bool persistent=!frames&&!realtime_steps&&replay.empty()&&diagnostics.empty();
  PortOptions boot_options;boot_options.full_controls=false;boot_options.space_specials=table=="space";boot_options.load(presenting&&(persistent||persist_options));
  if(fullscreen)boot_options.settings.fullscreen=true;
  if(windowed||frames||realtime_steps)boot_options.settings.fullscreen=fullscreen&&!windowed;
  PirateHighscores score_store;bool scores_loaded=false;
  if(highscore_path.empty()&&persistent){if(char*pref=SDL_GetPrefPath("SlamTiltNative","SlamTilt")){highscore_path=std::filesystem::path(pref)/slam::highscore_filename(table);SDL_free(pref);}}
  auto records=[&](){PirateHighscores::Records b{};const auto ptr=m.rd(0x46c498,4);for(unsigned i=0;i<b.size();++i)b[i]=m.rd(ptr+i,1);return b;};
  if(!highscore_path.empty()){
   const auto stored=score_store.load(highscore_path);
   if(stored){const auto ptr=m.rd(0x46c498,4);for(unsigned i=0;i<stored->size();++i)m.wr(ptr+i,(*stored)[i],1);scores_loaded=true;}
   else if(!score_store.error.empty()){boot_options.error=score_store.error;std::cerr<<score_store.error<<'\n';highscore_path.clear();}
  }
  auto saved_records=records();const auto initial_image=m.image,initial_runtime=m.runtime,initial_dat=m.dat;
  std::map<unsigned,std::vector<json>> ui_events;if(!ui_events_path.empty()){const auto schedule=read_json(ui_events_path);for(const auto&e:schedule.at("events"))ui_events[e.at("frame")].push_back(e);}
  Owner<SDL_Window,SDL_DestroyWindow> window(SDL_CreateWindow(("Slamtilt - Reborn | "+definition.display_name+(presenting?"":" — Native Vertical Slice")).c_str(),640,900,SDL_WINDOW_RESIZABLE),SDL_DestroyWindow);check(bool(window));
  if(presenting){check(SDL_SetWindowSize(window.get(),boot_options.settings.window_width,boot_options.settings.window_height));if(boot_options.settings.fullscreen)check(SDL_SetWindowFullscreen(window.get(),true));}
  else if(fullscreen)check(SDL_SetWindowFullscreen(window.get(),true));
  check(SDL_StartTextInput(window.get()));
  Owner<SDL_Renderer,SDL_DestroyRenderer> renderer(presenting?slam::create_presentation_renderer(window.get(),true):SDL_CreateRenderer(window.get(),nullptr),SDL_DestroyRenderer);check(bool(renderer));
  PortOptions options=std::move(boot_options);
  if(!frames)(void)SDL_SetRenderVSync(renderer.get(),1);
  if(!presenting)check(SDL_SetRenderLogicalPresentation(renderer.get(),320,680,SDL_LOGICAL_PRESENTATION_LETTERBOX));
  slam::Presentation presentation(renderer.get());options.shaders_available=presentation.available();options.shader_status=presentation.status();
  std::vector<SDL_DisplayMode> display_modes;int mode_count=0;
  if(auto**modes=SDL_GetFullscreenDisplayModes(SDL_GetDisplayForWindow(window.get()),&mode_count)){for(int i=0;i<mode_count;++i){display_modes.push_back(*modes[i]);const SDL_Point size{modes[i]->w,modes[i]->h};if(std::none_of(options.exclusive_resolutions.begin(),options.exclusive_resolutions.end(),[&](const auto&p){return p.x==size.x&&p.y==size.y;}))options.exclusive_resolutions.push_back(size);}SDL_free(modes);}
  auto applied=options.settings;
  if(menu_at_start){SDL_Event e{};e.type=SDL_EVENT_KEY_DOWN;e.key.key=SDLK_ESCAPE;options.handle(e);}
  Owner<SDL_Texture,SDL_DestroyTexture> scene(presenting?SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_TARGET,320,600):nullptr,SDL_DestroyTexture);
  if(presenting)check(bool(scene));
  std::unique_ptr<slam::UiSkin> pause_skin;
  auto texture=[&](int w,int h){Owner<SDL_Texture,SDL_DestroyTexture> t(SDL_CreateTexture(renderer.get(),SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STREAMING,w,h),SDL_DestroyTexture);check(bool(t));check(SDL_SetTextureBlendMode(t.get(),SDL_BLENDMODE_BLEND));return t;};
  auto background=texture(320,600);check(SDL_UpdateTexture(background.get(),nullptr,image.rgba.data(),1280));
  auto ball_texture=texture(16,15);auto dmd_texture=texture(96,20);
  std::vector<Owner<SDL_Texture,SDL_DestroyTexture>> lamp_textures;
  for(const auto&l:lamps)lamp_textures.push_back(texture(l.width,l.height));
  std::vector<Owner<SDL_Texture,SDL_DestroyTexture>> flipper_textures;
  for(const auto&s:sprites)flipper_textures.push_back(texture(s.width,s.height));
  constexpr std::array<unsigned,3> pose_addresses={0x46c786,0x46c76c,0x46c752};
  unsigned tick=0;bool running=true;json states=json::array(),globals=json::array(),poses_trace=json::array(),lifecycle=json::array(),scores=json::array(),lamp_states=json::array(),raw_states=json::array(),ball_pools=json::array(),aux_states=json::array(),weapon_states=json::array(),clock_states=json::array(),mode_aux_states=json::array(),video_states=json::array(),variant_states=json::array(),ui_frames=json::array();bool paused=false;
  bool audio_enabled=false,audio_focus=true,audio_device_paused=false;unsigned audio_requests=0;int audio_queued=0;json audio_events=json::array();
#ifdef SLAM_AUDIO_XMP
  std::unique_ptr<slam::NativeAudio> audio;
  if((table=="space"||table=="demon")&&!no_audio&&(!frames||force_audio)){
   try{auto banks=table=="demon"?slam::demon_sound_banks(m.dat):slam::space_sound_banks(m.dat);std::vector<std::vector<std::uint8_t>> modules;for(auto&b:banks)modules.push_back(std::move(b.stim));audio=std::make_unique<slam::NativeAudio>(std::move(modules));audio->set_samples(m.dat,table=="demon"?slam::demon_sample_profiles():slam::space_sample_profiles());audio_enabled=true;}
   catch(const std::exception& e){if(force_audio)throw;std::cerr<<table<<" audio unavailable: "<<e.what()<<'\n';}
  }
#else
  (void)no_audio;(void)force_audio;(void)audio_focus;
#endif
  auto send_audio=[&](unsigned at,int service,int bank,int order,unsigned descriptor){
   ++audio_requests;if(!audio_trace.empty())audio_events.push_back(json::array({at,service,bank,order,descriptor}));
#ifdef SLAM_AUDIO_XMP
   if(audio)audio->request(service,bank,order,descriptor);
#endif
  };
  if(audio_enabled||!audio_trace.empty()){
   send_audio(0,0x90,int(m.rd(0x454a68,4)),int(m.rd(0x454a64,4)),0);
   m.call_observer=[&](slam::PirateStepLift& state,unsigned address){
    int service=0;switch(address){case 0x406600:service=0x5c;break;case 0x406268:service=0x80;break;case 0x406240:service=0x84;break;case 0x40621c:service=0x88;break;case 0x4061f8:service=0x8c;break;case 0x4061c4:service=0x90;break;default:return;}
    if(service==0x5c)send_audio(tick+1,service,int(std::int32_t(state.r[2])),int(std::int32_t(state.r[3])),state.r[0]);
    else if(service==0x80||service==0x8c)send_audio(tick+1,service,0,0,0);
    else send_audio(tick+1,service,int(std::int32_t(state.r[2])),int(std::int32_t(state.r[0])),0);
   };
  }
  auto state=[&](){std::vector<std::uint8_t>b(100);for(unsigned i=0;i<100;++i)b[i]=m.rd(m.rd(0x454b68,4)+i,1);return b;};
  auto memory_hash=[&](unsigned address,unsigned count){std::vector<std::uint8_t>b(count);for(unsigned i=0;i<count;++i)b[i]=m.rd(address+i,1);return slam::sha256(b);};
  auto sample=[&](){return json{{"previous_ms",m.rd(0x46c734,4)},{"physics_accumulator",m.rd(0x46c744,4)},{"frame_accumulator",m.rd(0x46c740,4)},{"frame_count",m.rd(0x46c704,4)},{"crt_seed",m.rd(0x100900c,4)},{"rng_b4",m.rd(0x46c6b4,4)},{"rng_b8",m.rd(0x46c6b8,4)},{"phase",m.rd(0x46c6ac,4)},{"dmd_state",m.rd(0x46c68c,4)},{"dmd_sha256",memory_hash(m.rd(0x46c47c,4),1920)}};};
  auto mode_aux_sample=[&](){std::vector<std::uint8_t> b;for(auto block:{std::pair{0x463b54u,0x100u},std::pair{0x46ceecu,0x20u}})for(unsigned i=0;i<block.second;++i)b.push_back(m.rd(block.first+i,1));return slam::sha256(b);};
  auto variant_sample=[&](){return json::array({m.rd(0x463ae4,2),m.rd(0x46b764,4),m.rd(m.rd(0x46b758,4)+8,4),m.rd(0x463bc0,4),m.rd(0x463bc8,4),m.rd(0x46d5f0,4),m.rd(0x46d5d0,4)});};
  auto video_sample=[&](){const auto p=m.rd(0x46d60c,4);return json::array({m.rd(p+0x10,4),m.rd(p+0x14,4),m.rd(p+0x18,4),m.rd(p+0x20,4),m.rd(p+0x44,4)});};
  auto clock_sample=[&](){const auto p=m.rd(0x46d60c,4);return json::array({m.rd(p,4),m.rd(p+0x34,4),m.rd(0x46d658,4),m.rd(0x46d6c0,4),m.rd(0x46d6c4,4)});};
  auto weapon_sample=[&](){return json::array({m.rd(0x46ed2e,2),m.rd(0x46ed30,2),m.rd(0x46ed32,2),m.rd(0x46ed36,2),m.rd(0x46ee5c,2),m.rd(0x466568,2),m.rd(m.rd(0x46b758,4)+18,2)});};
  auto pose_sample=[&](){return json::array({m.rd(pose_addresses[0],2),m.rd(pose_addresses[1],2),m.rd(pose_addresses[2],2)});};
  auto life_sample=[&](){const auto p=m.rd(0x46b758,4);json v=json::array({m.rd(0x46c6ac,4),m.rd(0x46c67c,4),m.rd(0x46c680,4),m.rd(0x46c684,4),m.rd(p+14,2),m.rd(p+16,2),m.rd(0x46c61c,4),m.rd(0x46c620,4)});for(unsigned i=0;i<6;++i)v.push_back(m.rd(p+i,1));v.push_back(m.rd(0x46c60c,4));return v;};
  auto lamp_sample=[&](){std::vector<std::uint8_t>b;const auto n=m.rd(0x46c6a4,4);if(n>256)throw std::runtime_error("Invalid lamp count");for(unsigned i=0;i<n;++i){const auto p=m.rd(m.rd(0x46b74c,4)+i*4,4);b.push_back(m.rd(p+8,1));b.push_back(m.rd(p+9,1));}return slam::sha256(b);};
  auto key=[&](const json&e){const std::string action=e.at("action");const unsigned scan=action=="key"?e.at("scan").get<unsigned>():action=="new_game"?0x3b:action=="enter"?0x1c:action=="left"?0x2a:action=="right"?0x36:throw std::runtime_error("Unsupported slice input");m.r[2]=scan;m.invoke(0x40404c,e.at("down").get<bool>()?0:1);};
  std::map<unsigned,std::vector<json>> physical_inputs;
  auto live_key=[&](const json&e){key(e);if(!trace.empty())physical_inputs[tick].push_back(e);};
  if(!trace.empty())states.push_back(state());
  const auto started=SDL_GetTicksNS();auto before=started;std::uint64_t accumulator=0;unsigned clamped=0;
  for(unsigned frame=0;running&&(!frames||frame<frames)&&(!realtime_steps||tick<realtime_steps);++frame){
   if(const auto it=ui_events.find(frame);it!=ui_events.end())for(const auto&entry:it->second){SDL_Event event{};const std::string type=entry.at("type");
    if(type=="key"){event.type=entry.value("down",true)?SDL_EVENT_KEY_DOWN:SDL_EVENT_KEY_UP;event.key.key=SDL_GetKeyFromName(entry.at("key").get<std::string>().c_str());event.key.scancode=SDL_GetScancodeFromKey(event.key.key,nullptr);}
    else if(type=="focus_lost")event.type=SDL_EVENT_WINDOW_FOCUS_LOST;else if(type=="focus_gained")event.type=SDL_EVENT_WINDOW_FOCUS_GAINED;else throw std::runtime_error("Invalid UI event");
    check(SDL_PushEvent(&event));
   }
   SDL_Event e;while(SDL_PollEvent(&e)){
    if(e.type==SDL_EVENT_QUIT)running=false;
    if(e.type==SDL_EVENT_WINDOW_FOCUS_LOST||e.type==SDL_EVENT_WINDOW_MINIMIZED)audio_focus=false;
    if(e.type==SDL_EVENT_WINDOW_FOCUS_GAINED||e.type==SDL_EVENT_WINDOW_RESTORED)audio_focus=true;
    const bool lost=e.type==SDL_EVENT_WINDOW_FOCUS_LOST||e.type==SDL_EVENT_WINDOW_MINIMIZED;
    if(presenting&&(lost||options.handle(e))){if(!replay_only){live_key({{"action","left"},{"down",false}});live_key({{"action","right"},{"down",false}});live_key({{"action","enter"},{"down",false}});live_key({{"action","key"},{"scan",0x1d},{"down",false}});live_key({{"action","key"},{"scan",0x9d},{"down",false}});}if(lost)options.suspend_interaction();continue;}
    if(presenting&&(options.open||!audio_focus))continue;
    if(replay_only&&(e.type==SDL_EVENT_KEY_DOWN||e.type==SDL_EVENT_KEY_UP||e.type==SDL_EVENT_TEXT_INPUT)&&!(e.type!=SDL_EVENT_TEXT_INPUT&&e.key.key==SDLK_P))continue;
    if(e.type==SDL_EVENT_TEXT_INPUT&&m.rd(0x46c6ac,4)==3&&m.rd(0x46c61c,4)==6){
     for(const unsigned char* c=reinterpret_cast<const unsigned char*>(e.text.text);*c;++c){const unsigned value=*c>='a'&&*c<='z'?*c-'a'+'A':*c;for(unsigned p=0x454b88;m.rd(p,4);p+=8)if(m.rd(p+4,4)==value){live_key({{"action","key"},{"scan",m.rd(p,4)},{"down",true}});break;}}
    }
    if((e.type==SDL_EVENT_KEY_DOWN||e.type==SDL_EVENT_KEY_UP)&&!e.key.repeat){
     const bool down=e.type==SDL_EVENT_KEY_DOWN;
     if(m.rd(0x46c6ac,4)==3&&m.rd(0x46c61c,4)==6){if(e.key.key==SDLK_RETURN)live_key({{"action","enter"},{"down",down}});else if(e.key.key==SDLK_BACKSPACE&&down)live_key({{"action","key"},{"scan",0x0e},{"down",true}});continue;}
     if(presenting&&e.key.key==SDLK_P&&down&&!(m.rd(0x46c6ac,4)==3&&m.rd(0x46c61c,4)==6))paused=!paused;
     else if(e.key.key==SDLK_ESCAPE&&down)running=false;
     else if(e.key.scancode==(presenting?options.settings.key(PortAction::Plunger):SDL_SCANCODE_RETURN))live_key({{"action","enter"},{"down",down}});
     else if(e.key.scancode==(presenting?options.settings.key(PortAction::LeftFlipper):SDL_SCANCODE_LSHIFT))live_key({{"action","left"},{"down",down}});
     else if(e.key.key==SDLK_BACKSPACE&&down)live_key({{"action","key"},{"scan",0x0e},{"down",true}});
     else if((e.key.key==SDLK_F1||e.key.key==SDLK_R)&&down&&m.rd(0x46c6ac,4)==0)live_key({{"action","new_game"},{"down",true}});
     else if(table=="space"&&e.key.scancode==(presenting?options.settings.key(PortAction::SpecialLeft):SDL_SCANCODE_LCTRL))live_key({{"action","key"},{"scan",0x1d},{"down",down}});
     else if(table=="space"&&e.key.scancode==(presenting?options.settings.key(PortAction::SpecialRight):SDL_SCANCODE_RCTRL))live_key({{"action","key"},{"scan",0x9d},{"down",down}});
     else if(e.key.scancode==(presenting?options.settings.key(PortAction::RightFlipper):SDL_SCANCODE_RSHIFT))live_key({{"action","right"},{"down",down}});
    }
   }
   unsigned steps=4;
   if(!frames){const auto now=SDL_GetTicksNS();if(now-before>100000000)++clamped;accumulator+=std::min<std::uint64_t>(now-before,100000000);before=now;steps=unsigned(accumulator/5000000);accumulator%=5000000;}
   if(presenting&&(options.open||!audio_focus||paused)){steps=0;accumulator=0;}
   if(realtime_steps)steps=std::min(steps,realtime_steps-tick);
   for(unsigned i=0;i<steps;++i){
    if(const auto it=inputs.find(tick);it!=inputs.end())for(const auto&event:it->second)key(event);
    if(const auto it=shots.find(tick);it!=shots.end())diagnostic(it->second);
    m.invoke(0x405234,(tick+1)*5);++tick;
    if(tick%4==0){m.invoke(0x408da8);m.invoke(0x408674);}
    if(!trace.empty()){states.push_back(state());if(table=="demon"){clock_states.push_back(clock_sample());mode_aux_states.push_back(mode_aux_sample());video_states.push_back(video_sample());variant_states.push_back(variant_sample());}if(table=="space")weapon_states.push_back(weapon_sample());ball_pools.push_back(memory_hash(0x46c15c,800));aux_states.push_back(memory_hash(0x466b6c,256));globals.push_back(sample());poses_trace.push_back(pose_sample());lifecycle.push_back(life_sample());scores.push_back(memory_hash(m.rd(0x46c498,4),50));lamp_states.push_back(lamp_sample());if(table=="demon"||(!diagnostics.empty()&&table=="space"))raw_states.push_back(memory_hash(table=="demon"?0x46d400:0x46e970,table=="demon"?0x400:0x600));}
   }
#ifdef SLAM_AUDIO_XMP
   if(audio){audio->set_paused(!audio_focus||(presenting&&(options.open||paused)));if(presenting)audio->set_levels(options.settings.volume,options.settings.music_volume,options.settings.sfx_volume);audio->pump();audio_queued=audio->queued_bytes();audio_device_paused=audio->device_paused();}
#endif
   if(m.rd(0x46c6ac,4)==0&&!highscore_path.empty()&&records()!=saved_records){const auto current=records();if(score_store.save(highscore_path,current))saved_records=current;else options.error=score_store.error;}
   if(presenting)check(SDL_SetRenderTarget(renderer.get(),scene.get()));
   const float field_y=presenting?0.f:80.f;
   check(SDL_SetRenderDrawColor(renderer.get(),0,0,0,255));check(SDL_RenderClear(renderer.get()));const SDL_FRect field{0,field_y,320,600};check(SDL_RenderTexture(renderer.get(),background.get(),nullptr,&field));
   for(unsigned i=0;i<lamps.size();++i){const auto&l=lamps[i];const auto&rgba=l.rgba.at(l.frame(m.image));check(SDL_UpdateTexture(lamp_textures[i].get(),nullptr,rgba.data(),l.width*4));const SDL_FRect d{float(l.x),float(l.y)+field_y,float(l.width),float(l.height)};check(SDL_RenderTexture(renderer.get(),lamp_textures[i].get(),nullptr,&d));}
   for(unsigned i=0;i<sprites.size();++i){const auto&s=sprites[i];const auto pose=m.rd(pose_addresses[i],2);const auto rgba=slam::compose_table_flipper(flipper_profiles[i],s,s.frame(pose),image,m.image,m.dat);check(SDL_UpdateTexture(flipper_textures[i].get(),nullptr,rgba.data(),s.width*4));const SDL_FRect d{float(s.x),float(s.y)+field_y,float(s.width),float(s.height)};check(SDL_RenderTexture(renderer.get(),flipper_textures[i].get(),nullptr,&d));}
   const auto ball_count=m.rd(0x46c67c,4);if(ball_count>8)throw std::runtime_error("Invalid original ball count");
   std::vector<std::pair<unsigned,std::array<int,2>>> visible_balls;
   for(unsigned ball_index=0;ball_index<ball_count;++ball_index){
    const auto b=m.rd(0x454b68,4)+100*ball_index;
    visible_balls.push_back({b,slam::ball_display_position(std::int32_t(m.rd(b,4)),std::int32_t(m.rd(b+4,4)),std::int32_t(m.rd(b+8,4)),std::int32_t(m.rd(b+12,4)),frames?0:unsigned(accumulator/1000000))});
   }
   std::stable_sort(visible_balls.begin(),visible_balls.end(),[](const auto&a,const auto&b){return a.second[1]<b.second[1];});
   for(const auto& shown:visible_balls){
   const auto b=shown.first;const auto& point=shown.second;
   if(m.rd(b+88,2)!=65535&&point[0]>=0&&point[0]<=303&&point[1]>=0&&point[1]<600){
    auto mask=outline;const auto bitmap=m.rd(b+84,4);if(bitmap>=0x1100000)mask=slam::windows_ball_occlusion(mask,m.dat,bitmap-0x1100000,point[0],point[1]);
    const auto&pixels=pixel_bank[unsigned(point[1])/8];std::array<std::uint8_t,960>rgba{};
    for(unsigned i=0;i<240;++i){for(unsigned c=0;c<3;++c)rgba[i*4+c]=image.palette_rgba[pixels[i]*4+c];rgba[i*4+3]=255-mask.preserve_background[i];}
    check(SDL_UpdateTexture(ball_texture.get(),nullptr,rgba.data(),64));const SDL_FRect d{float(point[0]),float(point[1])+field_y,16,15};check(SDL_RenderTexture(renderer.get(),ball_texture.get(),nullptr,&d));
   }
   }
   std::array<std::uint8_t,1920*4>dmd{};const auto colors=m.rd(m.rd(0x46c644,4)+8,4)+0x20;
   for(unsigned i=0;i<1920;++i){const auto level=m.rd(m.rd(0x46c47c,4)+i,1);if(level>3)throw std::runtime_error("Invalid original DMD level");const auto color=m.rd(colors+level,1);for(unsigned c=0;c<3;++c){const auto&settings=options.settings;if(!presenting||settings.color==0)dmd[i*4+c]=image.palette_rgba[color*4+c];else if(settings.color==1)dmd[i*4+c]=level*(c==0?85:c==1?53:0);else if(settings.color==2)dmd[i*4+c]=level*85;else dmd[i*4+c]=level*(c==0?settings.custom_r:c==1?settings.custom_g:settings.custom_b)/3;}dmd[i*4+3]=255;}
   check(SDL_UpdateTexture(dmd_texture.get(),nullptr,dmd.data(),96*4));const SDL_FRect dmd_rect{16,10,288,60};if(!presenting)check(SDL_RenderTexture(renderer.get(),dmd_texture.get(),nullptr,&dmd_rect));
   else{
    check(SDL_SetRenderTarget(renderer.get(),nullptr));const auto&settings=options.settings;
    if(settings.fullscreen!=applied.fullscreen||settings.fullscreen_mode!=applied.fullscreen_mode||settings.window_width!=applied.window_width||settings.window_height!=applied.window_height){
     const SDL_DisplayMode*mode=nullptr;if(settings.fullscreen&&settings.fullscreen_mode==1)for(const auto&candidate:display_modes)if(candidate.w==settings.window_width&&candidate.h==settings.window_height&&(!mode||candidate.refresh_rate>mode->refresh_rate))mode=&candidate;
     if((!settings.fullscreen||settings.fullscreen_mode!=1||mode)&&slam::apply_window_mode(window.get(),settings.fullscreen,mode,settings.window_width,settings.window_height))applied=settings;else options.error=SDL_GetError();
    }
    int width=0,height=0;check(SDL_GetRenderOutputSize(renderer.get(),&width,&height));check(SDL_SetRenderDrawColor(renderer.get(),8,12,20,255));check(SDL_RenderClear(renderer.get()));
    const auto b=m.rd(0x454b68,4);const float bx=float(std::int32_t(m.rd(b,4)))/65536+8,by=float(std::int32_t(m.rd(b+4,4)))/65536+7;
    auto layout=slam::display_layout(width,height,settings.dmd_position,settings.dmd_size,settings.zoom,settings.aspect,bx,by,600);
    if(settings.dmd_position==3){layout.dmd.x=(width-layout.dmd.w)*settings.overlay_x;layout.dmd.y=(height-layout.dmd.h)*settings.overlay_y;}
    check(SDL_SetTextureScaleMode(scene.get(),settings.smooth?SDL_SCALEMODE_LINEAR:SDL_SCALEMODE_NEAREST));const SDL_Rect clip{int(layout.viewport.x),int(layout.viewport.y),int(layout.viewport.w),int(layout.viewport.h)};
    check(SDL_SetRenderClipRect(renderer.get(),&clip));presentation.draw(scene.get(),layout.table,settings.visual);check(SDL_SetRenderClipRect(renderer.get(),nullptr));presentation.draw(dmd_texture.get(),layout.dmd,settings.visual,true);options.draw(renderer.get(),width,height);
    if(paused&&!options.open){if(!pause_skin)pause_skin=std::make_unique<slam::UiSkin>();pause_skin->text(renderer.get(),"Paused · P to resume",20,20,20,{255,220,160,255},true);}
    if(!trace.empty())ui_frames.push_back({{"elapsed_ms",double(SDL_GetTicksNS()-started)/1e6},{"frame",frame},{"tick",tick},{"menu",options.open},{"focused",audio_focus},{"paused",paused},{"audio_device_paused",audio_device_paused},{"zoom",settings.zoom},{"aspect",settings.aspect},{"dmd_position",settings.dmd_position},{"viewport",{layout.viewport.x,layout.viewport.y,layout.viewport.w,layout.viewport.h}},{"table",{layout.table.x,layout.table.y,layout.table.w,layout.table.h}},{"dmd",{layout.dmd.x,layout.dmd.y,layout.dmd.w,layout.dmd.h}}});
   }
   if(!capture.empty()&&((frames&&frame+1==frames)||(realtime_steps&&tick==realtime_steps))){Owner<SDL_Surface,SDL_DestroySurface> s(SDL_RenderReadPixels(renderer.get(),nullptr),SDL_DestroySurface);check(bool(s));check(SDL_SaveBMP(s.get(),capture.string().c_str()));}
   check(SDL_RenderPresent(renderer.get()));
#ifdef __EMSCRIPTEN__
   SDL_Delay(1);
#else
   if(!frames)SDL_Delay(1);
#endif
  }
  if(!trace.empty()){std::ofstream f(trace);f<<json{{"tick_count",tick},{"replay_only",replay_only},{"physical_inputs",physical_inputs},{"video_driver",SDL_GetCurrentVideoDriver()},{"renderer",SDL_GetRendererName(renderer.get())},{"fullscreen",bool(SDL_GetWindowFlags(window.get())&SDL_WINDOW_FULLSCREEN)},{"real_wall_ms",double(SDL_GetTicksNS()-started)/1000000.0},{"clamped_frames",clamped},{"states",states},{"globals",globals},{"poses",poses_trace},{"lifecycle",lifecycle},{"highscore_sha256",scores},{"lamp_sha256",lamp_states},{"raw_state_sha256",raw_states},{"ball_pool_sha256",ball_pools},{"aux_state_sha256",aux_states},{"weapon_state",weapon_states},{"clock_state",clock_states},{"mode_aux_sha256",mode_aux_states},{"video_state",video_states},{"variant_state",variant_states},{"presentation",presenting},{"ui_frames",ui_frames},{"highscore_loaded",scores_loaded},{"highscore_file",highscore_path.string()}}.dump()<<'\n';if(!f)throw std::runtime_error("Cannot write trace");}
  if(!audio_trace.empty()){std::ofstream f(audio_trace);f<<json{{"events",audio_events},{"enabled",audio_enabled},{"queued_bytes",audio_queued},{"requests",audio_requests},{"driver",audio_enabled?SDL_GetCurrentAudioDriver():"none"}}.dump()<<'\n';if(!f)throw std::runtime_error("Cannot write audio trace");}
  // Independent native reset/replay of the same frozen keyboard schedule.
  if(!trace.empty()&&!replay.empty()){
   m=slam::PirateStepLift{};m.image=initial_image;m.runtime=initial_runtime;m.dat=initial_dat;
   if(state()!=states.at(0).get<std::vector<std::uint8_t>>())throw std::runtime_error("Reset state differs");
   for(unsigned i=0;i<tick;++i){if(const auto live=physical_inputs.find(i);live!=physical_inputs.end())for(const auto&event:live->second)key(event);if(const auto it=inputs.find(i);it!=inputs.end())for(const auto&event:it->second)key(event);if(const auto shot=shots.find(i);shot!=shots.end())diagnostic(shot->second);m.invoke(0x405234,(i+1)*5);if((i+1)%4==0){m.invoke(0x408da8);m.invoke(0x408674);}if((!variant_states.empty()&&variant_sample()!=variant_states.at(i))||(!video_states.empty()&&video_sample()!=video_states.at(i))||(!mode_aux_states.empty()&&mode_aux_sample()!=mode_aux_states.at(i))||(!clock_states.empty()&&clock_sample()!=clock_states.at(i))||(!weapon_states.empty()&&weapon_sample()!=weapon_states.at(i))||memory_hash(0x466b6c,256)!=aux_states.at(i)||memory_hash(0x46c15c,800)!=ball_pools.at(i)||state()!=states.at(i+1).get<std::vector<std::uint8_t>>()||sample()!=globals.at(i)||pose_sample()!=poses_trace.at(i)||life_sample()!=lifecycle.at(i)||memory_hash(m.rd(0x46c498,4),50)!=scores.at(i)||lamp_sample()!=lamp_states.at(i)||(!raw_states.empty()&&memory_hash(table=="demon"?0x46d400:0x46e970,table=="demon"?0x400:0x600)!=raw_states.at(i)))throw std::runtime_error("Native reset differs at "+std::to_string(i));}
  }
  std::cout<<table<<": "<<tick<<" native original steps\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
