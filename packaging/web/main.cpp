#include "assets/mean_import.h"
#include "assets/windows_table.h"
#include "physics/pirate_session.h"
#include <emscripten.h>
#include <SDL3/SDL.h>
#include <filesystem>
#include <cctype>
#include <fstream>
#include <nlohmann/json.hpp>
#include <string>
#include <vector>
namespace fs=std::filesystem;
int slam_native_view_main(int,char**);
int slam_native_slice_main(int,char**);
namespace {std::string error,root,source="windows";std::vector<std::uint8_t> preview;
const char* ids[]={"mean","pirate","space","demon"};
std::string dat_name(int id){return std::string(id==0?"MEAN":id==1?"PIRATE":id==2?"SPACE":"DEMON")+".DAT";}
}
extern "C" {
EMSCRIPTEN_KEEPALIVE const char* web_error(){return error.c_str();}
EMSCRIPTEN_KEEPALIVE void web_storage(){EM_ASM({
 try{FS.mkdir('/user');}catch(e){}
 FS.mount(IDBFS,{},'/user');
 FS.syncfs(true,function(err){window.webStorageReady(err?String(err):"");});
});}
EMSCRIPTEN_KEEPALIVE int web_restore(){try{std::ifstream f("/user/data.json");if(!f)return 0;nlohmann::json j;f>>j;root=j.at("root");source=j.at("source");return 1;}catch(...){return 0;}}
EMSCRIPTEN_KEEPALIVE int web_has_table(int id){return id>=0&&id<4&&fs::exists(fs::path(root)/ids[id]/dat_name(id));}
EMSCRIPTEN_KEEPALIVE int web_import(){try{
 error.clear();const auto destination="/user/import-"+std::to_string(static_cast<unsigned long long>(emscripten_get_now()*1000));bool amiga=false;
 for(const auto&e:fs::directory_iterator("/input")){auto s=e.path().extension().string();for(auto&c:s)c=char(std::tolower(static_cast<unsigned char>(c)));amiga|=s==".adf";}
 if(amiga){slam::import_amiga_adfs("/input",destination,"/meta","/meta/mean-data.sha256");source="amiga";}
 else{
  unsigned count=0;fs::create_directories(destination);
  try{for(int i=0;i<4;++i)if(fs::exists(fs::path("/input")/dat_name(i))){if(i==0)slam::import_mean({},"/input",fs::path(destination)/ids[i],"/meta/mean-demo-startup.json","/meta/mean-data.sha256");else slam::import_retail({},"/input",fs::path(destination)/ids[i],fs::path("/meta")/(std::string(ids[i])+"-retail-startup.json"));++count;}if(!count)throw std::runtime_error("Select MAIN.DAT and at least one table DAT, or all five supported Amiga ADFs.");}
  catch(...){fs::remove_all(destination);throw;}
  source="windows";
 }
 root=destination;std::ofstream("/user/data.json")<<nlohmann::json{{"root",root},{"source",source}}.dump();return 0;
 }catch(const std::exception&e){error=e.what();return 1;}}
EMSCRIPTEN_KEEPALIVE const std::uint8_t* web_preview(int id){try{if(!web_has_table(id))return nullptr;preview=slam::load_windows_table(fs::path(root)/ids[id]/dat_name(id)).rgba;return preview.data();}catch(...){return nullptr;}}
EMSCRIPTEN_KEEPALIVE int web_step_probe(unsigned steps){try{
 const auto data=fs::path(root)/"pirate";
 slam::PirateSession session(data/"pirate-prepared",data/"PIRATE.DAT",slam::PirateTickMode::Full);
 session.enable_lamps(true);for(unsigned i=0;i<steps;++i)session.step();return int(session.ticks());
 }catch(const std::exception&e){error=e.what();return -1;}}
EMSCRIPTEN_KEEPALIVE int web_play(int id,unsigned steps){try{
 if(!web_has_table(id))throw std::runtime_error("Import this table first.");setenv("SLAM_ASSET_SOURCE",source.c_str(),1);setenv("SLAM_FRONTEND_SESSION","1",1);setenv("SLAM_TABLE_PROFILES","/meta/table-profiles.json",1);
 const auto data=fs::path(root)/ids[id];std::vector<std::string> args;
 if(id<2){args={"slamview",(data/dat_name(id)).string(),id==0?"--play":"--pirate-play",(data/(std::string(ids[id])+"-prepared")).string()};if(id==0)args.insert(args.end(),{"--trace","/meta/initial-state.json","--retail-minigame"});}
 else args={"slamslice",ids[id],(data/(std::string(ids[id])+"-prepared")).string(),(data/dat_name(id)).string(),"--presentation","--windowed"};
 if(steps && EM_ASM_INT({return !!window.rebornTest.noAudio;}))args.push_back("--no-audio");
 if(steps || EM_ASM_INT({return !!window.rebornTest.trace;}))args.insert(args.end(),{id<2?"--trace-output":"--trace","/user/web-last-play.json"});
 if(steps){args.insert(args.end(),{"--frames",std::to_string(steps/4+1)});if(id!=1)args.insert(args.end(),{"--realtime-steps",std::to_string(steps)});}
 std::vector<char*> argv;for(auto&s:args)argv.push_back(s.data());argv.push_back(nullptr);error.clear();return id<2?slam_native_view_main(int(args.size()),argv.data()):slam_native_slice_main(int(args.size()),argv.data());
 }catch(const std::exception&e){error=e.what();return 1;}}
}
int main(){setenv("SLAM_TABLE_PROFILES","/meta/table-profiles.json",1);return 0;}
