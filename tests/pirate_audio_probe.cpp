#include "physics/pirate_session.h"
#include "core/pirate_input_replay.h"
#include "core/pirate_shot_replay.h"
#include "core/sha256.h"
#include "audio/pirate_sound_assets.h"
#include "audio/native_audio.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
using json=nlohmann::json;
namespace {
void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
json read(const std::filesystem::path& path){std::ifstream in(path);if(!in)throw std::runtime_error("Missing audio fixture");json data;in>>data;return data;}
std::uint64_t hash_pcm(std::uint64_t hash,const std::int16_t* data,std::size_t count){
  for(std::size_t i=0;i<count;++i){
    for(unsigned b=0;b<2;++b){hash^=(std::uint16_t(data[i])>>(8*b))&255;hash*=1099511628211ull;}
  }
  return hash;
}
constexpr std::uint64_t FNV=14695981039346656037ull;
}
int main(int argc,char**argv){
  if(argc!=5)return 2;
  try{
    slam::PirateSession session(argv[1],argv[2],slam::PirateTickMode::Full);
    session.enable_lamps(true);session.enable_audio_events(true);
    const auto fixture=read(argv[3]);
    const auto& dat=session.table_data();
    require(slam::sha256(dat)==fixture.at("dat_sha256"),"Wrong audio DAT");
    const auto banks=slam::pirate_sound_banks(dat);
    require(banks[0].orders==68&&banks[0].patterns==62&&banks[0].stim.size()==354540&&
            banks[1].orders==55&&banks[1].patterns==53&&banks[1].stim.size()==343949,"Wrong Pirate banks");
    const std::vector<std::vector<std::uint8_t>> music_banks{banks[0].stim,banks[1].stim};
    const auto profiles=slam::pirate_sample_profiles();require(profiles.size()==15,"Wrong sample count");
    const auto pcm_fixture=read("analysis/traces/pirate-audio-pcm.json");
    for(const auto& item:pcm_fixture.at("cases")){
      slam::MeanSampleMixer sample(dat,profiles);sample.request(-1,1,item.at("descriptor"));
      const auto frames=item.at("frames").get<unsigned>();std::vector<std::int16_t> pcm(frames*2),mono(frames);
      // Deliberately vary chunks; sample phase must match the original monolithic call.
      for(unsigned i=0;i<frames;i+=137)sample.mix(pcm.data()+2*i,std::min(137u,frames-i));
      for(unsigned i=0;i<frames;++i){require(pcm[2*i]==pcm[2*i+1],"SFX channel differs");mono[i]=pcm[2*i];}
      require(std::to_string(hash_pcm(FNV,mono.data(),mono.size()))==item.at("pcm_fnv64"),"Original Pirate PCM differs");
    }
    json reports=json::array();
    for(const auto& item:fixture.at("cases")){
      json first;
      for(unsigned pass=0;pass<2;++pass){
        session.reset();
        slam::PirateInputReplay input;input.load(item.at("replay").get<std::string>());
        slam::PirateShotReplay shots;const auto replay=read(item.at("replay").get<std::string>());
        require(slam::sha256([&]{std::ifstream in(item.at("replay").get<std::string>(),std::ios::binary);return std::vector<std::uint8_t>{std::istreambuf_iterator<char>(in),{}};}())==item.at("replay_sha256"),"Audio replay changed");
        if(replay.contains("diagnostic_shots"))shots.load(item.at("replay").get<std::string>());
        const auto profile=slam::load_table_profile(slam::default_table_profiles(),"pirate");
        slam::MeanMusicSequencer music(music_banks);slam::MeanSampleMixer samples(dat,profiles);
        json events=json::array();bool left=false,right=false;
        std::uint64_t music_hash=FNV,sfx_hash=FNV,music_nonzero=0,sfx_nonzero=0,frames_total=0;
        unsigned tick=0;
        const auto deliver=[&]{for(const auto& request:session.take_audio_requests()){
          events.push_back({tick,request.service,request.bank,request.order,request.descriptor});
          switch(request.service){
            case 0x5c:samples.request(request.bank,request.order,request.descriptor);break;
            case 0x80:music.stop84();break;
            case 0x84:music.request84(request.bank,request.order);break;
            case 0x88:music.request88(request.bank,request.order);break;
            case 0x8c:music.stop88();break;
            case 0x90:music.request90(request.bank,request.order);break;
            default:throw std::runtime_error("Unexpected sound service");
          }
        }};
        deliver();
        for(;tick<item.at("tick_count").get<unsigned>();++tick){
          input.apply(session,tick,left,right);if(replay.contains("diagnostic_shots"))shots.apply(session,profile);
          session.step();deliver();
          const unsigned frames=((std::uint64_t(tick)+1)*44100/200)-(std::uint64_t(tick)*44100/200);
          std::array<std::int16_t,442> music_pcm{},sfx_pcm{};
          music.render(music_pcm.data(),frames);samples.mix(sfx_pcm.data(),frames);
          for(unsigned i=0;i<2*frames;++i){music_nonzero+=music_pcm[i]!=0;sfx_nonzero+=sfx_pcm[i]!=0;}
          music_hash=hash_pcm(music_hash,music_pcm.data(),2*frames);sfx_hash=hash_pcm(sfx_hash,sfx_pcm.data(),2*frames);frames_total+=frames;
        }
        if(events!=item.at("events")){
          const auto& expected=item.at("events");std::size_t i=0;while(i<std::min(events.size(),expected.size())&&events[i]==expected[i])++i;
          std::cerr<<item.at("case")<<" event "<<i<<" actual "<<(i<events.size()?events[i]:json{})<<" expected "<<(i<expected.size()?expected[i]:json{})<<'\n';
          throw std::runtime_error("Original/native audio events differ");
        }
        require(slam::sha256(session.ball_pool_state())==item.at("final_ball_pool_sha256"),"Audio observer changed ball state");
        require(slam::sha256(session.rule_state())==item.at("final_rule_sha256"),"Audio observer changed rules");
        require(music_nonzero&&sfx_nonzero&&frames_total==std::uint64_t(tick)*44100/200,"Silent audio or cadence drift");
        json result={{"case",item.at("case")},{"events",events.size()},{"ticks",tick},{"frames",frames_total},
          {"music_hash",std::to_string(music_hash)},{"sfx_hash",std::to_string(sfx_hash)},
          {"music_nonzero",music_nonzero},{"sfx_nonzero",sfx_nonzero}};
        if(!pass)first=result;else require(result==first,"Audio reset/replay differs");
      }
      reports.push_back(first);std::cout<<first.at("case")<<": original events/native reset/music/SFX exact\n";
    }
    slam::NativeAudio output(music_banks);output.set_samples(dat,profiles);
    output.request(0x90,0,0);output.request(0x5c,6,5,0x465110);
    output.set_levels(.8f,.6f,.7f);output.set_paused(false);output.pump();
    require(!output.device_paused()&&output.queued_bytes()>0,"SDL audio not running");
    output.set_paused(true);require(output.device_paused(),"SDL audio did not pause");
    output.set_paused(false);output.pump();require(!output.device_paused()&&output.queued_bytes()>0,"SDL audio did not resume");
    output.restart();require(output.queued_bytes()==0,"Restart retained old audio");
    output.request(0x90,0,0);output.pump();require(output.queued_bytes()>0,"Restart did not resume audio");
    std::ofstream out(argv[4]);out<<json({{"cases",reports},{"pcm_cases",pcm_fixture.at("cases").size()},
      {"scope","Original service events + bounded mono resampler; native libxmp PCM deterministic, not original mixed-output equivalence"}}).dump(2)<<'\n';
    require(bool(out),"Cannot write audio report");
  }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
