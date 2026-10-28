#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json stats(const slam::MeanSimulation&s){return {{"chicken_starts",s.chicken_stats().starts},{"chicken_completions",s.chicken_stats().completions},{"chicken_score",s.chicken_stats().score},{"rally_starts",s.rally_stats().starts},{"rally_correct",s.rally_stats().correct},{"rally_completions",s.rally_stats().completions},{"rally_timeouts",s.rally_stats().timeouts},{"rally_score",s.rally_stats().score}};}
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
 unsigned tick=0,nudges=0,started_mask=0;json events=json::array(),totals=json::array();auto previous=stats(s);unsigned previous_cb=0;bool total_nonzero=false;
 for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());const auto audio=s.take_audio_requests();++tick;
 const auto&f=s.shared_raw_state().fields;for(unsigned k=0;k<5;++k)if(f[0x1e0+k])started_mask|=1u<<k;
 if(stats(s)!=previous){previous=stats(s);events.push_back({{"tick",tick},{"state",previous},{"ball",s.ball_number()},{"started_mask",started_mask}});}
 const auto cb=s.material5_display_callback();if(cb==0x410c8c&&cb!=previous_cb){unsigned voices=0;for(const auto&q:audio)voices+=q.service==0x88&&q.bank==1&&q.order==30;if(voices!=1||f[0x366]||f[0x367]||tick!=15968||s.phase1_award_total()!=140208000)throw std::runtime_error("Mode-total admission/voice/flag differs");totals.push_back({{"tick",tick},{"counter",s.material5_display_counter()},{"field_058",s.phase1_award_total()}});if(s.phase1_award_total())total_nonzero=true;}previous_cb=cb;
 }
 const auto final=stats(s);if(tick!=27116||tick!=fixture.at("ticks")||!s.game_over()||s.ball_count()||s.bonus_completions()!=3||s.score()!=194839960||s.tilted()||s.chicken_stats().starts!=1||s.chicken_stats().completions!=1||s.chicken_stats().score!=140208000||s.rally_stats().starts!=1||s.rally_stats().correct!=2||s.rally_stats().completions||s.rally_stats().timeouts||s.rally_stats().score!=30000000||started_mask!=5||!total_nonzero||totals.size()!=1||nudges!=2)throw std::runtime_error("Combined Chicken/Rally finite outcome differs");
 const auto score=s.score();const auto raw=s.shared_raw_state().fields;for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||stats(s)!=final)throw std::runtime_error("Combined GameOver changed");}
 cases.push_back({{"events",events},{"mode_total_displays",totals},{"final_tick",tick},{"final_score",score},{"started_mask",started_mask},{"completed_main_modes",1},{"stats",final},{"nudges",nudges}});
 s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.chicken_stats().starts||s.chicken_stats().completions||s.rally_stats().starts||s.rally_stats().correct||s.phase1_award_total())throw std::runtime_error("Combined newgame reset differs");
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Combined replay nondeterministic");std::ofstream(argv[5])<<json({{"scope","Two fresh finite legalinput Chicken completion followed by Rally two correct turns/drain/GameOver/freeze/newgame. Original started-record mask is not mode-completion evidence; only one main mode completed."},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS two finite combined Chicken/Rally chains\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
