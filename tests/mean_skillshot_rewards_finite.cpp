#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json read(const std::filesystem::path&p){json j;std::ifstream f(p);if(!f)throw std::runtime_error("Missing reward fixture");f>>j;return j;}
int main(int argc,char **argv){if(argc!=6)return 2;try{
 const std::filesystem::path root=argv[4];const auto manifest=read(root/"analysis/traces/mean-skillshot-rewards-input.json");json routes=json::array();
 for(const auto&item:manifest.at("cases")){const unsigned variant=item.at("variant");const auto input=read(root/item.at("input").get<std::string>());json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);unsigned tick=0,hits=0;json event;
 auto word=[&](unsigned o){const auto&f=s.shared_raw_state().fields;return unsigned(f[o])|(unsigned(f[o+1])<<8);};
 for(const auto&r:input.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){const unsigned a=r.at("actions"),before=s.switch_reward_variants()[variant],pending=s.pending_upper_extra_balls(),old_goal=word(0x1f2),old_extra=word(0x1fe);const auto score=s.score();
  s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16)s.nudge(1,false);if(a&64)s.nudge(-1,false);if(a&32)s.nudge(0,true);
  if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());++tick;const auto audio=s.take_audio_requests();
  if(s.switch_reward_variants()[variant]!=before){++hits;if(tick!=input.at("award_tick")||word(0x362)!=variant-1||!word(0x358)||word(0x35c)||s.score()!=score)throw std::runtime_error("Reward selection/score/launchlock differs");
   int voice=-1,music=-1;for(unsigned k=0;k<audio.size();++k){if(audio[k].service==0x88&&audio[k].bank==1&&audio[k].order==48)voice=k;if(audio[k].service==0x84&&audio[k].bank==0&&audio[k].order==62)music=k;}
   const bool admitted=s.material5_display_callback()==0x40fdec;if(admitted&&voice<0)throw std::runtime_error("Missing reward voice");
   switch(variant){
    case 1:if(s.award_bank_timer()!=6000||s.award_bank_value()!=60000000||music<0||(admitted&&voice>=music))throw std::runtime_error("Reward bank/audio order differs");break;
    case 2:if(s.pending_upper_extra_balls()!=pending+1)throw std::runtime_error("Reward pending extra differs");break;
    case 3:if(word(0x394)!=65535)throw std::runtime_error("Reward MODE LIT differs");break;
    // Original same right-lane event advances reward3bc1->2 after dispatcher.
    case 4:if(word(0x392)!=65535||word(0x3ba)!=2||word(0x3bc)!=2||word(0x3a2)!=65535)throw std::runtime_error(json({{"error","Reward branch3 differs"},{"tick",tick},{"392",word(0x392)},{"3ba",word(0x3ba)},{"3bc",word(0x3bc)}}).dump());break;
    case 5:if(word(0x398)<1499||word(0x398)>1500||word(0x3ac)||word(0x1d8)!=4)throw std::runtime_error("Reward PitStop differs");break;
    case 6:if(word(0x1fe)!=(old_extra+1)%3||word(0x204))throw std::runtime_error("Reward rotating extra selector differs");break;
    case 7:if(word(0x1f2)!=(old_goal<5?old_goal+1:old_goal))throw std::runtime_error("Reward goal progress differs");break;
   }
   event={{"tick",tick},{"variant",variant},{"reward_362",word(0x362)},{"ball",s.ball_number()},{"score",s.score()},{"admitted",admitted},{"voice_index",voice},{"music_index",music},{"fields",{{"1fa",word(0x1fa)},{"394",word(0x394)},{"392",word(0x392)},{"3ba",word(0x3ba)},{"3bc",word(0x3bc)},{"398",word(0x398)},{"1fe",word(0x1fe)},{"1f2",word(0x1f2)}}}};
  }
 }
 if(hits!=1||!s.game_over()||s.ball_count()||tick!=input.at("final_tick")||s.score()!=input.at("final_score")||s.bonus_completions()!=input.at("bonus_completions"))throw std::runtime_error("Reward finite outcome differs");
 const auto score=s.score();const auto raw=s.shared_raw_state().fields;for(unsigned i=0;i<64;++i){s.press_plunger();s.set_flippers(true,true);if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw)throw std::runtime_error("Reward GameOver changed");}
 cases.push_back({{"award",event},{"final_tick",tick},{"final_score",score},{"bonuses",s.bonus_completions()}});
 s.reset();if(s.game_over()||s.score()||s.switch_rewards()||s.switch_reward_variants()!=std::array<unsigned,8>{}||s.award_bank_timer()!=-1||s.pending_upper_extra_balls())throw std::runtime_error("Reward newgame reset differs");
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Reward replay nondeterministic");routes.push_back({{"variant",variant},{"cases",cases}});
 }
 std::ofstream(argv[5])<<json({{"scope","Fourteen fresh finite legal input games: seven reward effects/selection/launchlock/DMDvoice/Originalbankaudioorder/GameOverfreeze/reset; no state injections, no wholeOriginaltrajectory claim"},{"routes",routes}}).dump(2)<<'\n';std::cout<<"PASS all7 Skillshot rewards,14fresh finite games\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
