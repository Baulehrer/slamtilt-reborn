#include "physics/mean_simulation.h"
#include "core/mean_diagnostic_input.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <stdexcept>
int main(int argc,char **argv){
 if(argc!=6 && argc!=7)return 2;
 try{
  std::ifstream f(argv[4]),p(argv[5]);nlohmann::json input,expected;f>>input;p>>expected;
  const bool retail=argc==7,abort=retail && std::string(argv[6])=="retail-abort";
  const unsigned award=abort?40000000u:120000000u,callback=abort?0x40f994u:0x40fb78u;
  auto results=nlohmann::json::array();
  for(unsigned repeat=0;repeat<4;++repeat){
   slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(retail);
   if(repeat<2){if(!s.debug_start_minigame())throw std::runtime_error(s.status());}
   else{
    s.reset();s.set_continuous_play(true);s.set_endless_play(true);slam::MeanDiagnosticInput keys(27);
    for(unsigned step=0;step<400000 && !s.minigame_active();++step){
     s.set_launch(true);const auto k=keys.next();s.set_flippers(k[0],k[1]);if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();
    }
    if(!s.minigame_active() || s.minigame_steps()>1)throw std::runtime_error("Unforced minigame entry missing");
   }
   const auto initial_score=s.score();const auto releases=s.releases();
   for(unsigned guard=0;guard<20000 && s.minigame_active();++guard){
    const auto tick=s.minigame_steps();if(tick>=input.at("keys").size())throw std::runtime_error("Winning steering sequence exhausted");
    const auto k=abort && tick>=1082?0u:input.at("keys").at(tick).get<unsigned>();s.set_flippers(k==1,k==2);
    if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();
   }
   if(s.minigame_active() || s.minigame_completions()!=1 || s.score()!=initial_score+award || s.material5_display_callback()!=callback || s.table_mode()!=2)
    throw std::runtime_error("Native steering-only120M completion mismatch");
   s.set_flippers(false,false);const auto score=s.score();unsigned checked=0;
   const auto &pixels=expected.at("expected").at(abort?1:retail?5:10); //40fb78 raw43efdc7,6completedlaps.
   for(unsigned i=0;i<1250 && s.material5_display_callback()==callback;++i){
    if(!s.step())throw std::runtime_error(s.status());
    const auto count=s.material5_display_counter();if(!count)continue;
    std::uint64_t h=14695981039346656037ull;for(auto v:s.material5_pixels())h=(h^v)*1099511628211ull;
    const auto &e=pixels.at(count-1);
    if(std::to_string(h)!=e.at("fnv") || (s.material5_display_callback()!=0)!=e.at("active"))
      throw std::runtime_error("Winning result pixels/ownerretirement mismatch");
    if(s.score()!=score && (repeat<2 || s.releases()==releases))
      throw std::runtime_error("Result display awarded points before ball release");
    ++checked;
   }
   if(repeat>=2 && s.releases()<=releases)throw std::runtime_error("Unforced winning capture did not release ball");
   if(checked<(abort?168u:301u) || s.material5_display_callback()==callback)throw std::runtime_error("Winning result retained owner");
   results.push_back({{"score_before",initial_score},{"score_after_win",score},{"score_after_result",s.score()},{"releases_before",releases},{"releases_after",s.releases()},{"ticks",s.minigame_steps()},{"selected",s.selected_mode()},{"result_checks",checked}});
  }
  if(results[0]!=results[1] || results[2]!=results[3])throw std::runtime_error("Winning lifecycle not deterministic");
  std::ofstream output(std::filesystem::path(argv[4]).parent_path()/(abort?"mean-minigame-retail-abort-gameplay.json":retail?"mean-minigame-retail-gameplay.json":"mean-minigame1-winning-gameplay.json"));
  output<<nlohmann::json{{"award",award},{"scope","Two diagnostic selected3-capture entries plus two unforced endless seed27 entries; real key pairs only,revision-specific award/result pixels/ballrelease/ownerretirement; not original whole-table trajectory or finite3-ball proof"},{"cases",results}}.dump(2)<<'\n';
  std::cout<<"Steering-only award="<<award<<" callback="<<std::hex<<callback<<std::dec<<"; exact repeats,unforced seed27 entry/ballrelease/ownerretirement\n";
 }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
