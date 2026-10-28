#include "physics/mean_simulation.h"
#include "frontend/mean_highscores.h"
#include <chrono>
#include "audio/mean_music_sequencer.h"
#include "audio/mean_sample_mixer.h"
#include "audio/mean_sound_assets.h"
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json = nlohmann::json;
namespace {
void require(bool b, const char *message) { if (!b) throw std::runtime_error(message); }
void hash(std::uint64_t &h, unsigned v) { for (unsigned i=0;i<4;++i) { h ^= (v>>(8*i))&255; h *= 1099511628211ull; } }
json replay(const char *dat_path, const char *prepared, const char *flight,
            const char *fixture, const std::vector<std::uint8_t> &dat,
            const std::vector<std::vector<std::uint8_t>> &banks) {
  json input; std::ifstream(fixture) >> input;
  slam::MeanSimulation sim(dat_path, prepared, flight);
  sim.set_retail_minigame(true); sim.reset();
  sim.set_continuous_play(true); sim.set_endless_play(false);
  slam::MeanMusicSequencer music(banks);
  slam::MeanSampleMixer samples(dat), effects_only(dat);
  std::map<unsigned, unsigned> counts;
  std::uint64_t pcm_hash=1469598103934665603ull, request_hash=pcm_hash;
  std::uint64_t frames_total=0, nonzero_music=0, nonzero_sfx=0, nonzero_mixed=0;
  unsigned tick=0, max_voices=0;
  auto route = [&] {
    for (const auto &q : sim.take_audio_requests()) {
      ++counts[q.service]; hash(request_hash,q.service); hash(request_hash,q.bank);
      hash(request_hash,q.order); hash(request_hash,q.descriptor); hash(request_hash,tick);
      switch(q.service) {
      case 0x5c: samples.request(q.bank,q.order,q.descriptor); effects_only.request(q.bank,q.order,q.descriptor); break;
      case 0x80: music.stop84(); break;
      case 0x84: music.request84(q.bank,q.order); break;
      case 0x88: music.request88(q.bank,q.order); break;
      case 0x8c: music.stop88(); break;
      case 0x90: music.request90(q.bank,q.order); break;
      default: throw std::runtime_error("Unknown native sound request");
      }
    }
  };
  auto step = [&](unsigned a) {
    sim.set_launch(a&8); sim.set_flippers(a&1,a&2);
    if(a&4)sim.press_plunger();
    if(a&16)sim.nudge(1,false);
    if(a&64)sim.nudge(-1,false);
    if(a&32)sim.nudge(0,true);
    require(sim.step() || sim.game_over(), sim.status());
    route();
    // Exactly 44100 stereo frames/second at 200 simulation steps/second.
    const unsigned frames = ((std::uint64_t(tick)+1)*44100/200) - (std::uint64_t(tick)*44100/200);
    std::array<std::int16_t,442> mixed{}, effects{};
    music.render(mixed.data(),frames);
    effects_only.mix(effects.data(),frames);
    for(unsigned i=0;i<frames*2;++i) { nonzero_music += mixed[i]!=0; nonzero_sfx += effects[i]!=0; }
    samples.mix(mixed.data(),frames); // Exact NativeAudio default-gain path.
    for(unsigned i=0;i<frames*2;++i) {
      nonzero_mixed += mixed[i]!=0; hash(pcm_hash, std::uint16_t(mixed[i]));
    }
    max_voices=std::max(max_voices,unsigned(samples.active()));
    frames_total+=frames; ++tick;
  };
  route(); // reset emits the original base-track request before step one.
  for(const auto &r:input.at("actions_rle"))
    for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i) step(r.at("actions"));
  while(!sim.game_over() && tick<150000)step(8);
  require(sim.game_over() && !sim.ball_count(),"Audio replay did not reach finite GameOver");
  require(counts[0x90] && counts[0x5c],"Missing base/sample sound coverage");
  require(nonzero_music && nonzero_sfx && nonzero_mixed && max_voices,"Silent audio replay");
  require(frames_total==std::uint64_t(tick)*44100/200,"Audio cadence drift");
  const auto final_score=sim.score(); const auto bonuses=sim.bonus_completions();
  // Keep the same live game across audio playback, modal input and persistence.
  const auto frozen=sim.shared_raw_state().fields;
  const auto directory=std::filesystem::temp_directory_path()/
    ("slam-audio-lifecycle-"+std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
  require(std::filesystem::create_directory(directory),"Cannot create isolated score destination");
  struct Cleanup { std::filesystem::path path; ~Cleanup() { std::error_code e; std::filesystem::remove_all(path,e); } } cleanup{directory};
  const auto destination=directory/"scores.json";
  MeanHighscores scores; scores.load_path(destination);
  require(scores.begin(final_score),"Audio game did not admit highscore modal");
  auto key=[&](SDL_Scancode code,bool repeat=false) {
    SDL_Event event{}; event.type=SDL_EVENT_KEY_DOWN; event.key.scancode=code; event.key.repeat=repeat;
    require(scores.handle(event),"Highscore modal leaked input");
  };
  key(SDL_SCANCODE_Z,true);
  key(SDL_SCANCODE_R); key(SDL_SCANCODE_A); key(SDL_SCANCODE_B);
  key(SDL_SCANCODE_RETURN,true);
  require(scores.editing,"Repeated confirmation saved score");
  key(SDL_SCANCODE_RETURN);
  require(!scores.editing && scores.error.empty(),"Highscore save failed");
  MeanHighscores loaded; loaded.load_path(destination);
  require(loaded.error.empty() && loaded.entries().size()==1 &&
    loaded.entries()[0].score==final_score && loaded.entries()[0].initials=="RAB" &&
    !std::filesystem::exists(destination.string()+".tmp"),"Atomic highscore reload differs");
  for(unsigned i=0;i<64;++i) {
    require(!scores.begin(final_score),"Duplicate highscore admission");
    require(!sim.step() && sim.score()==final_score && sim.shared_raw_state().fields==frozen,
      "GameOver changed during modal lifecycle");
    require(sim.take_audio_requests().empty(),"Frozen GameOver emitted audio requests");
  }

  music.reset(); samples.reset();
  std::array<std::int16_t,442> silent{};
  music.render(silent.data(),221); samples.mix(silent.data(),221);
  require(!music.foreground_service() && !samples.active() &&
          std::all_of(silent.begin(),silent.end(),[](auto v){return v==0;}),"Audio reset not silent");
  sim.reset(); scores.reset_session();
  require(!sim.game_over() && !sim.score() && !scores.begin(0) && scores.entries().size()==1,"Gameplay/highscore reset failed");
  const auto startup=sim.take_audio_requests();
  require(startup.size()==1 && startup[0].service==0x90 && startup[0].bank==0 && startup[0].order==4,"Newgame startup music differs");
  music.request90(startup[0].bank,startup[0].order);
  std::array<std::int16_t,442> restart{}, fresh_pcm{};
  slam::MeanMusicSequencer fresh(banks); fresh.request90(0,4);
  music.render(restart.data(),221); fresh.render(fresh_pcm.data(),221);
  require(restart==fresh_pcm,"Reset/newgame music retained old decoder state");
  sim.set_launch(false); sim.set_flippers(false,false);
  require(sim.step() && !sim.game_over() && scores.entries()[0].score==final_score,
    "Newgame failed to advance or lost saved score");
  json services=json::object(); for(const auto &[service,count]:counts)services[std::to_string(service)]=count;
  return {{"ticks",tick},{"final_score",final_score},{"bonus_completions",bonuses},
    {"highscore_reload",true},{"initials","RAB"},{"gameover_frozen_steps",64},{"pcm_frames",frames_total},{"pcm_hash",pcm_hash},{"request_hash",request_hash},
    {"services_decimal",services},{"nonzero_music_samples",nonzero_music},
    {"nonzero_sfx_samples",nonzero_sfx},{"nonzero_mixed_samples",nonzero_mixed},{"max_sfx_voices",max_voices}};
}
}
int main(int argc,char **argv) {
  if(argc!=7 && argc!=6)return 2;
  try {
    std::ifstream file(argv[1],std::ios::binary);
    require(bool(file),"Cannot open Mean DAT");
    const std::vector<std::uint8_t> dat((std::istreambuf_iterator<char>(file)),{});
    const auto assets=slam::mean_sound_banks(dat);
    const std::vector<std::vector<std::uint8_t>> banks={assets[0].stim,assets[1].stim};
    json cases=json::array();
    json routes=json::array();
    if(argc==7) {
      routes.push_back({{"input",argv[4]},{"ticks",7608},{"score",54200000u},{"bonuses",3}});
      routes.push_back({{"input",argv[5]},{"ticks",40380},{"score",482716240u},{"bonuses",4}});
    } else {
      json manifest; std::ifstream(argv[4])>>manifest;
      const unsigned ticks[]={13160,27656,14576,31452,37452,20320,49216};
      const unsigned score[]={14513660,195364960,61923660,90402710,152616370,8347810,312905420};
      require(manifest.at("cases").size()==7,"Expected all seven reward routes");
      unsigned seen=0;
      for(const auto &entry:manifest.at("cases")) {
        const unsigned variant=entry.at("variant"); require(variant>=1 && variant<=7,"Invalid reward variant");
        require(!(seen & (1u<<variant)),"Duplicate reward variant"); seen |= 1u<<variant;
        auto path=std::filesystem::path(argv[4]).parent_path().parent_path().parent_path()/entry.at("input").get<std::string>();
        routes.push_back({{"input",path.string()},{"ticks",ticks[variant-1]},
          {"score",score[variant-1]},{"bonuses",variant==7?5:3}});
      }
    }
    for(const auto &route:routes) {
      const auto fixture=route.at("input").get<std::string>();
      const auto a=replay(argv[1],argv[2],argv[3],fixture.c_str(),dat,banks);
      const auto b=replay(argv[1],argv[2],argv[3],fixture.c_str(),dat,banks);
      require(a==b,"Gameplay requests/decoded PCM are nondeterministic");
      require(a.at("ticks")==route.at("ticks") && a.at("final_score")==route.at("score") &&
              a.at("bonus_completions")==route.at("bonuses"),"Known finite gameplay outcome changed during audio replay");
      require(a.at("services_decimal").contains("136"),"Missing foreground88 event coverage");
      if(route.at("ticks")==40380)require(a.at("services_decimal").contains("132"),"Missing queued84 event coverage");
      cases.push_back({{"fixture",fixture},{"fresh_repeats",2},{"result",a}});
    }
    std::ofstream report(argc==7?argv[6]:argv[5]);
    report<<json({{"scope","Fresh native legal-input finite gameplay requests routed through real Mean DAT/STIM/libxmp and sample mixer at exact 200Hz/44100Hz cadence; deterministic PCM, GameOver/modal SDL-scancode input/isolated atomic highscore reload/newgame reset. Component integration; main event routing tested separately. Not a full Original audio timeline comparison."},{"cases",cases}}).dump(2)<<'\n';
    require(bool(report),"Cannot write lifecycle report");
    std::cout<<"PASS finite gameplay/audio/highscore routes twice, real banks/PCM/cadence/persistence/reset\n";
  } catch(const std::exception &e) {std::cerr<<e.what()<<'\n';return 1;}
}
