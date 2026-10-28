#include "physics/mean_simulation.h"
#include <array>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <set>
#include <stdexcept>
using json=nlohmann::json;
static std::uint64_t hash_pixels(const slam::WindowsDmdPixels &p){std::uint64_t h=14695981039346656037ull;for(auto v:p){h^=v;h*=1099511628211ull;}return h;}
int main(int argc,char **argv){if(argc!=7)return 2;try{
 json all=json::array();
 // A legal idle input segment exposes the complete prelaunch phase cycle.
 slam::MeanSimulation waiting(argv[1],argv[2],argv[3]);
 waiting.reset();waiting.set_continuous_play(true);waiting.set_endless_play(false);
 waiting.set_launch(false);waiting.set_flippers(false,false);
 std::array<unsigned,3> waiting_pages{};
 for(unsigned tick=0;tick<1000;++tick) {
   if(!waiting.step())throw std::runtime_error(waiting.status());
   waiting.take_audio_requests();
   if(waiting.player_hud_visible()) {
     const auto &h=waiting.player_hud();
     if(waiting.material5_pixels()!=h.pixels || h.player_0e!=1 || h.field_35c)
       throw std::runtime_error("Waiting player HUD presentation differs");
     ++waiting_pages[h.field_engine_5c || !h.counter ? 0 : (h.counter&127)<=64 ? 1 : 2];
   }
 }
 if(!waiting_pages[0]||!waiting_pages[1]||!waiting_pages[2]||waiting.ball_number()!=1||waiting.score())
   throw std::runtime_error("Waiting prelaunch cycle incomplete");
 for(unsigned route=0;route<2;++route){json fixture;std::ifstream(argv[4+route])>>fixture;json cases=json::array();
  for(unsigned repeat=0;repeat<2;++repeat){
   slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
   unsigned tick=0,nudges=0,extra_decrements=0;std::array<unsigned,5> counts{};std::array<bool,5> seen{};json first=json::array();std::set<unsigned> balls;std::set<std::uint64_t> score_values;std::set<std::uint32_t> counters;std::uint64_t rolling=14695981039346656037ull;bool have_extra=false;std::int16_t previous_extra=0;
   auto observe=[&](){if(!s.player_hud_visible()){have_extra=false;return;}const auto &h=s.player_hud();if(!s.material5_display_active()||s.material5_pixels()!=h.pixels||h.player_0e!=s.ball_number())throw std::runtime_error("Player HUD presentation/ball mismatch");
    const bool extra=h.field_engine_60!=0&&h.field_360>=-1&&!h.field_35c;
    const unsigned page=h.field_35c?0:extra?1:h.field_engine_5c?2:(h.counter&127u)<=64?3:4;
    ++counts[page];balls.insert(h.player_0e);counters.insert(h.counter);if(page==4)score_values.insert(h.score);
    if(extra){if(have_extra&&h.field_360==previous_extra-1)++extra_decrements;have_extra=true;previous_extra=h.field_360;}else have_extra=false;
    auto hash=hash_pixels(h.pixels);rolling^=hash;rolling*=1099511628211ull;rolling^=tick;rolling*=1099511628211ull;
    if(!seen[page]){seen[page]=true;first.push_back({{"page",std::array<const char*,5>{"skillshot","extra_ball","engine5c","player_ball","score_choices"}[page]},{"tick",tick},{"counter",h.counter},{"field_360",h.field_360},{"field_engine_5c",h.field_engine_5c},{"field_engine_60",h.field_engine_60},{"ball",h.player_0e},{"score",h.score},{"pixel_fnv",std::to_string(hash)}});}
   };
   auto step=[&](unsigned a){s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;observe();};
   for(const auto &r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i)step(r.at("actions"));
   while(!s.game_over()&&tick<150000)step(8);
   const unsigned expected_tick=route?67340:7608,expected_bonuses=route?5:3;const std::uint64_t expected_score=route?230621370:54200000;
   if(!s.game_over()||s.ball_count()||tick!=expected_tick||s.score()!=expected_score||s.bonus_completions()!=expected_bonuses||!counts[2]||balls.size()!=3||counters.size()<2)throw std::runtime_error(json({{"error","Player HUD finite lifecycle differs"},{"route",route},{"tick",tick},{"score",s.score()},{"pages",counts},{"balls",balls},{"counters",counters},{"bonuses",s.bonus_completions()},{"ball_count",s.ball_count()},{"game_over",s.game_over()}}).dump());
   if(counts[1]>1&&!extra_decrements)throw std::runtime_error("Visible extra-ball countdown did not decrement");
   const auto score=s.score();const auto raw=s.shared_raw_state().fields;const auto pixels=s.material5_pixels();for(unsigned i=0;i<64;++i){s.press_plunger();s.set_flippers(true,true);if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||s.material5_pixels()!=pixels)throw std::runtime_error("Player HUD GameOver changed");}
   cases.push_back({{"page_counts",counts},{"first_pages",first},{"balls",balls},{"counter_values",counters.size()},{"score_values",score_values.size()},{"extra_countdown_decrements",extra_decrements},{"rolling_fnv",std::to_string(rolling)},{"final_tick",tick},{"final_score",score},{"bonuses",s.bonus_completions()},{"nudges",nudges}});
   s.reset();if(s.game_over()||s.score()||s.ball_number()!=1||s.player_hud_visible()||s.player_hud().field_engine_5c!=50||s.player_hud().field_engine_60||s.player_hud().field_360!=100)throw std::runtime_error("Player HUD newgame reset incomplete");
  }
  if(cases[0]!=cases[1])throw std::runtime_error("Player HUD route nondeterministic");all.push_back({{"route",route?"goal_ladder":"skillshot"},{"cases",cases}});
 }
 std::ofstream(argv[6])<<json({{"waiting_page_counts",waiting_pages},{"scope","Two fresh finite runs each of legal Skillshot and three-goal ladder inputs; Original player/ball/score choice pages, earned extra-ball countdown, fixed scores/ticks, GameOver freeze/reset; bounded Original pixel oracle separate"},{"routes",all}}).dump(2)<<'\n';std::cout<<"PASS four finite player HUD/extra-ball/Skillshot/goal routes\n";
}catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}}
