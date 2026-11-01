#include "audio/mean_sample_mixer.h"
#include "audio/stim_player.h"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>
int main(int argc,char **argv){
 if(argc!=16)return 1;
 try{
  std::ifstream f(argv[2],std::ios::binary);if(!f)return 2;
  std::vector<std::uint8_t> dat{std::istreambuf_iterator<char>(f),{}};
  const int order=std::stoi(argv[3]); std::vector<slam::SampleProfile> samples;
  for(int i=0;i<2;++i){int a=4+i*5; samples.push_back({unsigned(i+1),std::stoul(argv[a]),std::stoul(argv[a+1]),unsigned(std::stoul(argv[a+2]))});}
  const auto frames=std::stoul(argv[14]),chunk=std::stoul(argv[15]);if(!frames||frames>2646||!chunk)return 3;
  slam::StimPlayer player(argv[1],order,slam::TrackerMix::RetailMono);slam::MeanSampleMixer mixer(dat,samples);
  for(int i=0;i<2;++i){int a=4+i*5;mixer.request(std::stoi(argv[a+3]),std::stoi(argv[a+4]),i+1,samples[i].period,64);}
  std::vector<std::int16_t> pcm(frames*2);
  for(std::size_t at=0;at<frames;at+=chunk){const auto count=std::min(chunk,frames-at);player.render(pcm.data()+at*2,count);mixer.mix(pcm.data()+at*2,count);}
  std::cout.write(reinterpret_cast<const char*>(pcm.data()),pcm.size()*sizeof(pcm[0]));return std::cout?0:4;
 }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 5;}
}
