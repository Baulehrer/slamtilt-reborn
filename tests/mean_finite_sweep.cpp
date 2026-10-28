#include "core/mean_diagnostic_input.h"
#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
int main(int argc,char**argv){if(argc!=5)return 2;try{
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);json first,results=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){json games=json::array();std::uint64_t ticks=0,points=0;
  for(unsigned seed=0;seed<100;++seed){s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);s.set_launch(true);slam::MeanDiagnosticInput keys(seed);unsigned tick=0;std::array<unsigned,7> modes{};
   for(;tick<200000&&!s.game_over();++tick){const auto k=keys.next();s.set_flippers(k[0],k[1]);if(s.minigame_active()&&tick%240==0)s.press_plunger();if(!s.step()&&!s.game_over())throw std::runtime_error("seed"+std::to_string(seed)+": "+s.status());s.take_audio_requests();if(s.table_mode()>=0&&s.table_mode()<7)++modes[s.table_mode()];}
   if(!s.game_over()||s.ball_count()||s.bonus_completions()!=3)throw std::runtime_error("Finite sweep game did not finish seed"+std::to_string(seed));
   const auto score=s.score();const auto fields=s.shared_raw_state().fields;for(unsigned i=0;i<8;++i){s.press_plunger();s.set_flippers(true,true);if(s.step()||s.score()!=score||s.shared_raw_state().fields!=fields)throw std::runtime_error("Finite sweep GameOver changed");}
   ticks+=tick;points+=score;games.push_back({{"seed",seed},{"ticks",tick},{"score",score},{"bonuses",s.bonus_completions()},{"mode_ticks",modes}});
   s.reset();if(s.game_over()||s.score()||s.bonus_completions()||s.switch_rewards())throw std::runtime_error("Finite sweep newgame reset differs");
  }
  // Fresh constructor-per-seed verification: mean-reset-fresh-reference.json.
  // Old 691117830 included retained flipper input edges across new games.
  if(ticks!=792480||points!=671117830)throw std::runtime_error("Finite sweep aggregate reference differs");
  if(repeat&&games!=first)throw std::runtime_error("Finite sweep is nondeterministic");first=games;results.push_back({{"games",games},{"ticks",ticks},{"score_sum",points}});
 }
 std::ofstream(argv[4])<<json({{"scope","Two deterministic100-seed fresh legal-keyboard finite sweeps; three bonuses/GameOver/freeze/reset each; native regression, complete Original trajectories and all-mode completion in one game unclaimed"},{"runs",results}}).dump(2)<<'\n';std::cout<<"PASS 100 finite games twice / 1584960 native ticks / freeze and newgame reset\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
