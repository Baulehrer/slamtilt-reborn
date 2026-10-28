#include "physics/mean_simulation.h"
#include "dmd/mean_main_mode_hud.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <set>
#include <stdexcept>
using json=nlohmann::json;
static std::uint64_t hash_pixels(const slam::WindowsDmdPixels &p){std::uint64_t h=14695981039346656037ull;for(auto v:p){h^=v;h*=1099511628211ull;}return h;}
static json read_json(const std::filesystem::path&p){std::ifstream f(p);if(!f)throw std::runtime_error("Missing fixture "+p.string());json j;f>>j;return j;}
int main(int argc,char**argv){if(argc!=6)return 2;try{
 const std::filesystem::path root=argv[4];const auto assets=slam::load_mean_main_mode_hud(argv[1],std::filesystem::path(argv[1]).parent_path()/"MAIN.DAT");json routes=json::array();
 // Locked references from the passing MEAN-063 full regression; no reads of
 // generated reports that another parallel CTest may be rewriting.
 const std::array<unsigned,5> final_ticks={20872,23640,29268,35028,40380};
 const std::array<std::uint64_t,5> final_scores={156498980,147922810,159529640,249209410,482716240};
 const std::array<const char*,5> names={"chicken","monster","rally","offroad","speed"};const std::array<unsigned,5> selections={0,1,2,4,0};
 for(unsigned route=0;route<names.size();++route){const std::string name=names[route];const auto prefix=root/"analysis/traces"/("mean-"+name+"-natural-");const auto fixture=read_json(prefix.string()+"input.json");json cases=json::array();
  for(unsigned repeat=0;repeat<2;++repeat){slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);unsigned tick=0,nudges=0,visible=0,expected_visible=0,callback_ticks=0;std::set<std::uint32_t> counters;std::set<std::int16_t> timers,targets;std::set<std::uint64_t> pixel_hashes;std::uint64_t rolling=14695981039346656037ull;json first;
   auto observe=[&](){if(s.material5_display_callback())++callback_ticks;if(!s.main_mode_hud_visible())return;const auto&h=s.main_mode_hud();auto check=h;--check.counter;
    if(!slam::mean_main_mode_hud_step(check,assets)||!s.material5_display_active()||s.material5_pixels()!=h.pixels||check.counter!=h.counter||check.pixels!=h.pixels)throw std::runtime_error(name+" HUD differs from independent compositor at "+std::to_string(tick));
    ++visible;if(h.mode==(route==4?6u:5u)&&(route==4||h.selected==selections[route]))++expected_visible;counters.insert(h.counter);timers.insert(h.field_39c);targets.insert(h.field_38c);const auto hash=hash_pixels(h.pixels);pixel_hashes.insert(hash);rolling^=hash;rolling*=1099511628211ull;rolling^=tick;rolling*=1099511628211ull;
    if(first.is_null())first={{"tick",tick},{"mode",h.mode},{"selected",h.selected},{"counter",h.counter},{"field_39c",h.field_39c},{"field_38c",h.field_38c},{"pixel_fnv",std::to_string(hash)}};
   };
   auto step=[&](unsigned a){s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}if(!s.step()&&!s.game_over())throw std::runtime_error(name+": "+s.status());s.take_audio_requests();++tick;observe();};
   for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i)step(r.at("actions"));
   while(!s.game_over()&&tick<150000)step(8);
   if(!s.game_over()||s.ball_count()||s.bonus_completions()<3||!expected_visible||counters.size()<2||pixel_hashes.size()<2||!callback_ticks)throw std::runtime_error(name+" finite HUD lifecycle incomplete");
   if(tick!=final_ticks[route]||s.score()!=final_scores[route])throw std::runtime_error(name+" existing finite reference changed");
   const auto score=s.score();const auto raw=s.shared_raw_state().fields;for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw)throw std::runtime_error(name+" GameOver changed");}
   cases.push_back({{"visible_ticks",visible},{"expected_page_ticks",expected_visible},{"callback_ticks",callback_ticks},{"counter_values",counters.size()},{"timer_values",timers.size()},{"target_values",targets.size()},{"pixel_hash_values",pixel_hashes.size()},{"rolling_fnv",std::to_string(rolling)},{"first_page",first},{"final_tick",tick},{"final_score",score},{"bonuses",s.bonus_completions()},{"nudges",nudges}});
   s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.main_mode_hud_visible())throw std::runtime_error(name+" HUD reset incomplete");
  }
  if(cases[0]!=cases[1])throw std::runtime_error(name+" HUD replay nondeterministic");routes.push_back({{"route",name},{"cases",cases}});
 }
 std::ofstream(argv[5])<<json({{"scope","Two fresh legal-input finite runs per Chicken/Monster/Rally/Offroad/SPEED route; every visible HUD full pixels independently recomposed; existing finite totals, GameOver/freeze/reset. Formula uses separate minigame."},{"routes",routes}}).dump(2)<<'\n';std::cout<<"PASS ten finite main-mode/SPEED HUD pixel/lifecycle chains\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
