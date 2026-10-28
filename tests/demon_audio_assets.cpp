#include "audio/demon_sound_assets.h"
#include "audio/stim_player.h"
#include "core/sha256.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <algorithm>
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("Usage: demon_audio_assets DAT EVIDENCE");
 std::ifstream input(argv[1],std::ios::binary),evidence(argv[2]);std::vector<std::uint8_t>d{std::istreambuf_iterator<char>(input),{}};nlohmann::json e;evidence>>e;
 if(slam::sha256(d)!=e.at("dat").at("sha256"))throw std::runtime_error("DAT SHA mismatch");
 auto banks=slam::demon_sound_banks(d);if(banks.size()!=3)throw std::runtime_error("Three banks required");
 for(unsigned i=0;i<3;++i){const auto&r=e.at("banks").at(i);if(slam::sha256(banks[i].stim)!=r.at("stim_sha256")||banks[i].orders!=r.at("orders")||banks[i].patterns!=r.at("patterns"))throw std::runtime_error("Original bank mismatch");
  slam::StimPlayer a(banks[i].stim,i?0:32),b(banks[i].stim,i?0:32);std::vector<std::int16_t>x(8192),y(8192);a.render(x.data(),4096);b.render(y.data(),4096);if(x!=y||std::none_of(x.begin(),x.end(),[](auto v){return v!=0;}))throw std::runtime_error("Bank PCM not deterministic/nonzero");
 }
 auto profiles=slam::demon_sample_profiles();if(profiles.size()!=14)throw std::runtime_error("Fourteen samples required");
 for(unsigned i=0;i<profiles.size();++i){const auto&p=profiles[i];const auto&r=e.at("sample_profiles").at(i);if(p.descriptor!=std::stoul(r.at("descriptor").get<std::string>(),nullptr,0)||p.offset!=std::stoul(r.at("offset").get<std::string>(),nullptr,0)||p.length!=r.at("length")||p.period!=r.at("period"))throw std::runtime_error("Sample profile mismatch");
  if(slam::sha256({d.begin()+p.offset,d.begin()+p.offset+p.length})!=r.at("pcm_sha256"))throw std::runtime_error("Original PCM mismatch");
  slam::MeanSampleMixer a(d,profiles),b(d,profiles);a.request(-1,1,p.descriptor);b.request(-1,1,p.descriptor);std::vector<std::int16_t>x(8192),y(8192);a.mix(x.data(),4096);b.mix(y.data(),4096);if(x!=y||std::none_of(x.begin(),x.end(),[](auto v){return v!=0;}))throw std::runtime_error("Sample mix not deterministic/nonzero");
 }
 std::cout<<"3originalbanks/14sampleprofiles/34PCMpasses exact/nonzero\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
