#include "physics/mean_simulation.h"
#include "assets/mean_flippers.h"
#include "physics/mean_lane_saver.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
int main(int argc,char**argv){if(argc!=5)return 2;try{
 std::ifstream input(argv[1],std::ios::binary);std::vector<std::uint8_t> dat(std::istreambuf_iterator<char>(input),{});
 auto expected=[&](bool on){std::array<std::uint8_t,632> out{};unsigned n=0;for(unsigned y=0;y<30;++y)for(unsigned x=0;x<4;++x)out[n++]=dat.at((on?0x9436e:0x94b2e)+y*4+x);for(unsigned p=0;p<4;++p)for(unsigned y=0;y<32;++y)for(unsigned x=0;x<4;++x)out[n++]=dat.at((on?0x9472e:0x94eee)+p*128+y*4+x);return out;};
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){s.reset();s.set_continuous_play(true);s.set_endless_play(false);if(s.lane_saver_geometry()!=expected(false))throw std::runtime_error("Initial fence geometry differs");s.debug_start_rule_capture(true);json events=json::array();unsigned opened=0,closed=0,tick=0,bonus=0;bool changed=false;int frame=s.lane_saver_frame();
 while(tick<40000&&!s.game_over()) {if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;if(frame!=s.lane_saver_frame()){frame=s.lane_saver_frame();events.push_back({{"tick",tick},{"frame",frame}});}if(!opened&&s.lane_saver_geometry()==expected(true)){opened=tick;changed=true;events.push_back({{"event","opened"},{"tick",tick}});}if(opened&&!closed&&s.lane_saver_geometry()==expected(false)){closed=tick;events.push_back({{"event","closed"},{"tick",tick}});}bonus=s.bonus_completions();if(closed&&bonus)break;}
 if(!changed||!closed||!bonus||s.lane_saver_frame()!=0)throw std::runtime_error("Reward/fence/open/nextturn/close chain incomplete");s.reset();if(s.lane_saver_geometry()!=expected(false)||s.lane_saver_frame()!=0||s.lap_goal_fields()[6])throw std::runtime_error("Fence newgame reset differs");cases.push_back({{"events",events},{"opened_tick",opened},{"closed_tick",closed},{"bonus_completions",bonus}});}
 if(cases[0]!=cases[1])throw std::runtime_error("Fence gameplay nondeterministic");std::ofstream(argv[4])<<json({{"scope","Diagnostic original upper-capture reward boundary, native animation/normal+allfour hitplane patches/actual drain+nextturn closure/reset; not natural goal activation"},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS reward/fence/nextturn/reset twice\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
