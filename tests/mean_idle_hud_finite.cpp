#include "physics/mean_simulation.h"
#include "dmd/mean_idle_hud.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <set>
#include <stdexcept>
using json=nlohmann::json;
static std::uint64_t hash_pixels(const slam::WindowsDmdPixels&p){std::uint64_t h=14695981039346656037ull;for(auto v:p){h^=v;h*=1099511628211ull;}return h;}
int main(int argc,char **argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;const auto assets=slam::load_mean_idle_hud(argv[1],std::filesystem::path(argv[1]).parent_path()/"MAIN.DAT");json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,nudges=0;std::array<unsigned,3> counts{};json first=json::array();std::array<bool,3> seen{};std::set<std::int16_t> pit_timers,bank_timers;std::set<std::uint64_t> scores;std::uint64_t rolling=14695981039346656037ull;bool pit_decreased=false;std::int16_t previous_pit=-1;
  auto observe=[&](){if(!s.idle_hud_visible())return;const auto &h=s.idle_hud();auto check=h;--check.counter;slam::mean_idle_hud_step(check,assets);if(!s.material5_display_active()||s.material5_pixels()!=h.pixels||check.counter!=h.counter||check.pixels!=h.pixels)throw std::runtime_error("Idle HUD differs from independent compositor");const auto phase=(h.counter-1)&127u;const bool pit=h.field_398>=0&&(h.field_37a>=0?phase<64:phase<80);const unsigned page=pit?1:h.field_37a>=0?2:0;const auto pixel_hash=hash_pixels(h.pixels);++counts[page];rolling^=pixel_hash;rolling*=1099511628211ull;rolling^=tick;rolling*=1099511628211ull;
   if(!seen[page]){seen[page]=true;first.push_back({{"page",std::array<const char*,3>{"score","pit_stop","bank"}[page]},{"tick",tick},{"counter",h.counter},{"field_398",h.field_398},{"field_37a",h.field_37a},{"field_3ac",h.field_3ac},{"field_054",h.field_054},{"score",h.score},{"pixel_fnv",std::to_string(pixel_hash)}});}
   if(page==0)scores.insert(h.score);if(page==1){if(previous_pit>=0&&h.field_398<previous_pit)pit_decreased=true;previous_pit=h.field_398;pit_timers.insert(h.field_398);}if(page==2)bank_timers.insert(h.field_37a);
  };
  auto step=[&](unsigned a){s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;observe();};
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i)step(r.at("actions"));
  if(tick!=fixture.at("pit_complete_tick")||s.pit_stop_stats().completions!=1||s.pit_stop_stats().score!=65000000||nudges!=2)throw std::runtime_error("Natural PitStop fixture changed");
  while(!s.game_over()&&tick<150000)step(8);
  if(!s.game_over()||s.ball_count()||s.bonus_completions()<3||!counts[0]||!counts[1]||scores.size()<2||pit_timers.size()<2||!pit_decreased)throw std::runtime_error("Finite idle HUD page/timer lifecycle incomplete");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw)throw std::runtime_error("Idle HUD GameOver changed");}
  cases.push_back({{"page_counts",counts},{"first_pages",first},{"pit_timer_values",pit_timers.size()},{"pit_timer_decreased",pit_decreased},{"bank_timer_values",bank_timers.size()},{"score_values",scores.size()},{"rolling_fnv",std::to_string(rolling)},{"final_tick",tick},{"final_score",score},{"bonuses",s.bonus_completions()},{"nudges",nudges}});
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.pit_stop_stats().completions||s.idle_hud_visible())throw std::runtime_error("Idle HUD reset incomplete");
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Idle HUD finite replay nondeterministic");std::ofstream(argv[5])<<json({{"scope","Two fresh legal input65M PitStop/idle HUD/finite GameOver/freeze/reset runs; full pixels recomposed independently each visible tick. Bank page counts report natural coverage without asserting occurrence."},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS two finite natural idle HUD score/PitStop pixel and timer chains\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
