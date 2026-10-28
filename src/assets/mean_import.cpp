#include "assets/mean_import.h"
#include "assets/native_retail_data.h"
#include "assets/amiga_assets.h"
#include "assets/amiga_disk.h"
#include "core/sha256.h"
#include <nlohmann/json.hpp>
#include <algorithm>
#include <array>
#include <chrono>
#include <fstream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace fs=std::filesystem;
namespace slam {
namespace {
using Bytes=std::vector<std::uint8_t>;
using Hashes=std::map<std::string,std::string>;
using json=nlohmann::json;
constexpr std::array<const char*,8> names{{"MEAN.DAT","MAIN.DAT","mean-prepared/pe-data.bin",
  "mean-prepared/engine-globals.bin","mean-prepared/flipper-state.bin","mean-prepared/lookup.bin",
  "mean-minigame-prepared/image.bin","mean-minigame-prepared/runtime.bin"}};
Bytes read(const fs::path& path) {
  std::ifstream input(path,std::ios::binary|std::ios::ate);
  if(!input) throw std::runtime_error("Cannot read "+path.string());
  const auto size=input.tellg();
  if(size<0||size>64*1024*1024) throw std::runtime_error("Invalid input size: "+path.string());
  Bytes data(static_cast<std::size_t>(size));input.seekg(0);
  if(!data.empty()&&!input.read(reinterpret_cast<char*>(data.data()),size)) throw std::runtime_error("Cannot read "+path.string());
  return data;
}
void write(const fs::path& path,const Bytes& data) {
  fs::create_directories(path.parent_path());
  std::ofstream output(path,std::ios::binary);
  if(!output.write(reinterpret_cast<const char*>(data.data()),static_cast<std::streamsize>(data.size())))
    throw std::runtime_error("Cannot write "+path.string());
  output.close();if(!output) throw std::runtime_error("Cannot finish writing "+path.string());
}
// The destination was exclusively reserved by this import. Windows cannot
// rename a directory over that reservation; publish its children before the
// frontend records the new location. Rollback removes only our reservation.
void publish_stage(const fs::path& stage,const fs::path& destination) {
#ifdef _WIN32
  try {
    for(const auto& entry:fs::directory_iterator(stage))
      fs::rename(entry.path(),destination/entry.path().filename());
    fs::remove(stage);
  } catch(...) {
    std::error_code ignored;fs::remove_all(destination,ignored);throw;
  }
#else
  fs::rename(stage,destination);
#endif
}
Hashes hashes(const fs::path& path) {
  const auto data=read(path);std::istringstream input(std::string(data.begin(),data.end()));
  Hashes result;std::string line;
  while(std::getline(input,line)) {
    if(line.find_first_not_of(" \r\t")==std::string::npos)continue;
    std::istringstream row(line);std::string hash,name,extra;
    if(!(row>>hash>>name)||(row>>extra))throw std::runtime_error("Invalid Mean data profile row");
    if(std::find(names.begin(),names.end(),name)==names.end()||hash.size()!=64||
       hash.find_first_not_of("0123456789abcdef")!=std::string::npos||!result.emplace(name,hash).second)
      throw std::runtime_error("Invalid Mean data profile");
  }
  if(result.size()!=names.size()) throw std::runtime_error("Incomplete Mean data profile");
  return result;
}
std::uint32_t integer(const Bytes& data,std::size_t offset,unsigned length=4) {
  if(offset>data.size()||length>data.size()-offset) throw std::runtime_error("Invalid PE range");
  std::uint32_t value=0;
  for(unsigned i=0;i<length;++i) value|=std::uint32_t(data[offset+i])<<(i*8);
  return value;
}
void copy(const Bytes& from,std::size_t offset,Bytes& to,std::size_t destination,std::size_t length) {
  if(offset>from.size()||length>from.size()-offset||destination>to.size()||length>to.size()-destination)
    throw std::runtime_error("Invalid image range");
  std::copy_n(from.begin()+offset,length,to.begin()+destination);
}
void words(Bytes& data,const json& entries) {
  for(const auto& entry:entries) {
    const auto offset=entry.at(0).get<std::size_t>();const auto value=entry.at(1).get<std::uint32_t>();
    if(offset>data.size()||4>data.size()-offset) throw std::runtime_error("Invalid startup state range");
    for(unsigned i=0;i<4;++i)data[offset+i]=static_cast<std::uint8_t>(value>>(i*8));
  }
}
Bytes map_pe(const Bytes& exe,std::size_t size) {
  const auto pe=integer(exe,0x3c);const auto optional=std::size_t(pe)+24;
  if(integer(exe,0,2)!=0x5a4d||integer(exe,pe)!=0x4550||integer(exe,pe+4,2)!=0x14c||
     integer(exe,optional,2)!=0x10b||integer(exe,optional+28)!=0x400000||size>0x100000)
    throw std::runtime_error("Unsupported PE32 image");
  Bytes image(size);copy(exe,0,image,0,integer(exe,optional+60));
  const auto sections=optional+integer(exe,pe+20,2);
  for(unsigned i=0;i<integer(exe,pe+6,2);++i) {
    const auto section=sections+i*40;const auto source=integer(exe,section+20);
    if(source)copy(exe,source,image,integer(exe,section+12),integer(exe,section+16));
  }
  return image;
}
struct Stage {
  fs::path path;
  explicit Stage(const fs::path& parent) {
    const auto stamp=std::chrono::steady_clock::now().time_since_epoch().count();
    for(unsigned n=0;n<100;++n) {
      auto candidate=parent/(".mean-import-"+std::to_string(stamp)+"-"+std::to_string(n));
      if(fs::create_directory(candidate)) { path=candidate;return; }
    }
    throw std::runtime_error("Cannot create import staging directory");
  }
  ~Stage() { if(!path.empty()) { std::error_code ignored;fs::remove_all(path,ignored); } }
};
}
bool verify_mean_data(const fs::path& data,const fs::path& profile,std::string* error) {
  std::vector<fs::path> profiles{profile};
  const auto retail_profile=profile.parent_path()/"mean-retail-data.sha256";
  if(retail_profile!=profile&&fs::is_regular_file(retail_profile))profiles.push_back(retail_profile);
  const auto amiga_profile=profile.parent_path()/"mean-amiga-data.sha256";
  if(amiga_profile!=profile&&fs::is_regular_file(amiga_profile))profiles.push_back(amiga_profile);
  const auto amiga_v2_profile=profile.parent_path()/"mean-amiga-v2-data.sha256";
  if(amiga_v2_profile!=profile&&fs::is_regular_file(amiga_v2_profile))profiles.push_back(amiga_v2_profile);
  for(const auto& candidate:profiles) {
  try {
    const auto expected=hashes(candidate);
    for(const auto& entry:expected) if(sha256(read(data/entry.first))!=entry.second)
      throw std::runtime_error("Unsupported or corrupt "+entry.first);
    if(fs::exists(data/"data.sha256")&&hashes(data/"data.sha256")!=expected)
      throw std::runtime_error("Private data manifest differs from supported profile");
    return true;
  } catch(const std::exception& failure) { if(error)*error=failure.what(); }
  }
  return false;
}
void import_mean(const fs::path& exe_path,const fs::path& dat,const fs::path& output,
                      const fs::path& recipe_path,const fs::path& profile,AssetSource asset_source) {
  const bool dat_only=exe_path.empty();
  const auto exe=dat_only?Bytes{}:read(exe_path);
  const auto build_sha=dat_only?std::string("185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6"):sha256(exe);
  const bool retail=build_sha=="185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6";
  const auto selected_recipe=retail?recipe_path.parent_path()/"mean-retail-startup.json":recipe_path;
  const auto amiga_v2_profile=profile.parent_path()/"mean-amiga-v2-data.sha256";
  const auto selected_profile=asset_source==AssetSource::AmigaAdf?(fs::is_regular_file(amiga_v2_profile)?amiga_v2_profile:profile.parent_path()/"mean-amiga-data.sha256"):retail?profile.parent_path()/"mean-retail-data.sha256":profile;
  const auto recipe=json::parse(read(selected_recipe));
  const auto expected=hashes(selected_profile);
  if(build_sha!=recipe.at("build_sha256")) throw std::runtime_error("Unsupported SLAMTILT.EXE revision; supported Windows Retail or Mean Demo required");
  std::map<std::string,Bytes> files;
  for(auto name:{"MEAN.DAT","MAIN.DAT"}) {
    auto bytes=read(dat/name);
    if(sha256(bytes)!=expected.at(name)) throw std::runtime_error(std::string("Unsupported or corrupt ")+name);
    files.emplace(name,std::move(bytes));
  }
  const auto size=recipe.at("image_size").get<std::size_t>();
  if(size>0x100000) throw std::runtime_error("Invalid prepared image size");
  const auto source_size=recipe.value("source_image_size",size);
  if(source_size>0x100000)throw std::runtime_error("Invalid source image size");
  Bytes image=dat_only?native_retail_data_image():map_pe(exe,source_size);
  if(retail) {
    Bytes normalized(size);
    for(const auto& entry:recipe.at("data_copies"))
      copy(image,entry.at(0).get<std::size_t>(),normalized,entry.at(1).get<std::size_t>(),entry.at(2).get<std::size_t>());
    for(const auto& entry:recipe.at("pointer_fixups")) {
      const auto offset=entry.at(0).get<std::size_t>();
      if(integer(normalized,offset)!=entry.at(1).get<std::uint32_t>())throw std::runtime_error("Retail Mean pointer mismatch");
      words(normalized,json::array({json::array({offset,entry.at(2)})}));
    }
    image=std::move(normalized);
  }
  const auto bss=recipe.at("bss").at(0).get<std::size_t>(),bss_size=recipe.at("bss").at(1).get<std::size_t>();
  if(bss>image.size()||bss_size>image.size()-bss)
    throw std::runtime_error("Invalid BSS range");
  if(std::any_of(image.begin()+bss,image.begin()+bss+bss_size,[](auto byte){return byte!=0;}))
    throw std::runtime_error("Uninitialized PE section was not cleared");
  const auto lookup_size=recipe.at("lookup").at(1).get<std::size_t>();
  if(lookup_size>0x10000)throw std::runtime_error("Invalid lookup size");
  Bytes lookup(lookup_size);
  copy(image,recipe.at("lookup").at(0).get<std::size_t>(),lookup,0,lookup.size());
  auto mini=image;mini.resize(0x100000);words(mini,recipe.at("minigame_image"));
  Bytes runtime(0x10000);words(runtime,recipe.at("minigame_runtime"));copy(lookup,0,runtime,0x6000,lookup.size());
  Bytes globals(160),flippers(108);words(globals,recipe.at("engine_globals"));words(flippers,recipe.at("flipper_state"));
  files["mean-prepared/pe-data.bin"]=std::move(image);files["mean-prepared/lookup.bin"]=std::move(lookup);
  files["mean-prepared/engine-globals.bin"]=std::move(globals);files["mean-prepared/flipper-state.bin"]=std::move(flippers);
  files["mean-minigame-prepared/image.bin"]=std::move(mini);files["mean-minigame-prepared/runtime.bin"]=std::move(runtime);
  for(const auto& entry:files) if(sha256(entry.second)!=expected.at(entry.first))
    throw std::runtime_error("Prepared profile mismatch: "+entry.first);
  const auto destination=fs::absolute(output);
  if(fs::exists(destination)||fs::is_symlink(destination)) throw std::runtime_error("Destination already exists: "+destination.string());
  fs::create_directories(destination.parent_path());Stage stage(destination.parent_path());
  for(const auto& entry:files) write(stage.path/entry.first,entry.second);
  write(stage.path/"data.sha256",read(selected_profile));
  const auto report=json{{"format",1},{"table","Mean Machines"},{"build_sha256",build_sha},{"files",expected},
    {"method",dat_only?"Native engine/table initialization + user assets":retail?"Retail data-only extraction + canonical native Mean data ABI + verified startup scalars":"PE section extraction + verified startup scalar recipe"},{"asset_source",asset_source_name(asset_source)},{"gameplay_profile","shared_native"},{"input_executable_provided",!dat_only},{"requires_wine_or_emulator",false},{"native_importer",true}}.dump(2)+"\n";
  write(stage.path/"data.json",Bytes(report.begin(),report.end()));
  // Exclusive reservation preserves even empty directories and dangling symlinks.
  if(!fs::create_directory(destination)) throw std::runtime_error("Destination already exists: "+destination.string());
  try { publish_stage(stage.path,destination);stage.path.clear(); }
  catch(...) { std::error_code ignored;fs::remove(destination,ignored);throw; }
}
void import_mean_demo(const fs::path& exe,const fs::path& dat,const fs::path& output,
                      const fs::path& recipe,const fs::path& profile) {
  import_mean(exe,dat,output,recipe,profile);
}
bool verify_retail_data(const fs::path& data,const fs::path& recipe_path,std::string* error) {
  std::vector<fs::path> recipes{recipe_path};
  auto dat_recipe=recipe_path;
  auto name=dat_recipe.filename().string();const auto at=name.find("-retail-startup.json");
  if(at!=std::string::npos){name.replace(at,std::string("-retail-startup.json").size(),"-dat-startup.json");dat_recipe=dat_recipe.parent_path()/name;if(fs::is_regular_file(dat_recipe))recipes.push_back(dat_recipe);}
  name=recipe_path.filename().string();const auto amiga_at=name.find("-retail-startup.json");if(amiga_at!=std::string::npos){name.replace(amiga_at,std::string("-retail-startup.json").size(),"-amiga-startup.json");const auto amiga_recipe=recipe_path.parent_path()/name;if(fs::is_regular_file(amiga_recipe))recipes.push_back(amiga_recipe);}
  name=recipe_path.filename().string();
  const auto v2_at=name.find("-retail-startup.json");
  if(v2_at!=std::string::npos){name.replace(v2_at,std::string("-retail-startup.json").size(),"-amiga-v2-startup.json");const auto v2=recipe_path.parent_path()/name;if(fs::is_regular_file(v2))recipes.push_back(v2);}
  if(recipe_path.filename()=="demon-retail-startup.json"){
    const auto v3=recipe_path.parent_path()/"demon-amiga-v3-startup.json";
    if(fs::is_regular_file(v3))recipes.push_back(v3);
  }
  for(const auto& candidate:recipes) {
  try {
    const auto recipe=json::parse(read(candidate));
    const auto table=recipe.at("table").get<std::string>();
    if(table!="Ace of Space"&&table!="The Pirate"&&table!="Night of the Demon")throw std::runtime_error("Unsupported Retail table");
    const bool space=table=="Ace of Space", demon=table=="Night of the Demon";
    const std::string prepared=demon?"demon-prepared/":space?"space-prepared/":"pirate-prepared/";
    const std::vector<std::string> names=(space||demon)?std::vector<std::string>{demon?"DEMON.DAT":"SPACE.DAT","MAIN.DAT",prepared+"human-image.bin",prepared+"human-runtime.bin",prepared+"summary.json"}:std::vector<std::string>{"PIRATE.DAT","MAIN.DAT",prepared+"human-image.bin",prepared+"human-runtime.bin"};
    if(recipe.at("files_sha256").size()!=names.size())throw std::runtime_error("Invalid Retail manifest");
    for(const auto& name:names)
      if(sha256(read(data/name))!=recipe.at("files_sha256").at(name))throw std::runtime_error("Unsupported or corrupt "+name);
    return true;

  }catch(const std::exception& e){if(error)*error=e.what();}
  }
  return false;
}
void import_retail(const fs::path& exe_path,const fs::path& dat,const fs::path& output,const fs::path& recipe_path,AssetSource asset_source) {
  const bool dat_only=exe_path.empty();
  auto selected_recipe=recipe_path;
  if(dat_only){auto name=selected_recipe.filename().string();const auto at=name.find("-retail-startup.json");if(at==std::string::npos)throw std::runtime_error("Missing native DAT import recipe");name.replace(at,std::string("-retail-startup.json").size(),asset_source==AssetSource::AmigaAdf?"-amiga-startup.json":"-dat-startup.json");selected_recipe=selected_recipe.parent_path()/name;}
  if(dat_only&&asset_source==AssetSource::AmigaAdf){
    auto name=selected_recipe.filename().string();const auto pos=name.find("-amiga-startup.json");
    if(pos!=std::string::npos){name.replace(pos,std::string("-amiga-startup.json").size(),"-amiga-v2-startup.json");const auto v2=selected_recipe.parent_path()/name;if(fs::is_regular_file(v2))selected_recipe=v2;}
  }
  if(asset_source==AssetSource::AmigaAdf&&selected_recipe.filename()=="demon-amiga-v2-startup.json"){
    const auto v3=selected_recipe.parent_path()/"demon-amiga-v3-startup.json";
    if(fs::is_regular_file(v3))selected_recipe=v3;
  }
  const auto recipe=json::parse(read(selected_recipe));
  const auto table=recipe.at("table").get<std::string>();
  if(table!="Ace of Space"&&table!="The Pirate"&&table!="Night of the Demon")throw std::runtime_error("Unsupported Retail table");
  const bool space=table=="Ace of Space", demon=table=="Night of the Demon";
  const std::string table_dat=demon?"DEMON.DAT":space?"SPACE.DAT":"PIRATE.DAT";
  const std::string prepared=demon?"demon-prepared/":space?"space-prepared/":"pirate-prepared/";
  const auto exe=dat_only?Bytes{}:read(exe_path);
  if(!dat_only&&sha256(exe)!=recipe.at("build_sha256"))throw std::runtime_error("Unsupported Retail executable");
  std::map<std::string,Bytes> files;
  for(const auto& name:std::array<std::string,2>{table_dat,"MAIN.DAT"}) {
    auto bytes=read(dat/name);
    if(sha256(bytes)!=recipe.at("input_sha256").at(name))throw std::runtime_error(std::string("Unsupported or corrupt ")+name);
    files.emplace(name,std::move(bytes));
  }
  if(recipe.at("image_size")!=0x100000)throw std::runtime_error("Invalid Retail image size");
  Bytes image=dat_only?native_retail_data_image():map_pe(exe,0x100000);
  const auto canvas=recipe.at("canvas").get<std::array<std::size_t,3>>();
  copy(files.at(table_dat),canvas[1],image,canvas[0],canvas[2]);
  copy(files.at("MAIN.DAT"),0,image,recipe.at("main_offset").get<std::size_t>(),files.at("MAIN.DAT").size());
  for(const auto& entry:recipe.at("image_words")){
    const auto offset=entry.at(0).get<std::size_t>();
    if(offset<0x52000||offset>=0x70000)throw std::runtime_error("Invalid Retail scalar range");
  }
  words(image,recipe.at("image_words"));Bytes runtime(0x10000);
  for(unsigned i=0;i<600;++i){runtime[0xc000+i*4]=0x40;runtime[0xc001+i*4]=1;}
  words(runtime,recipe.at("runtime_words"));
  files[prepared+"human-image.bin"]=std::move(image);
  files[prepared+"human-runtime.bin"]=std::move(runtime);
  if(space||demon){const auto metadata=recipe.at("summary").dump()+"\n";
    files[prepared+"summary.json"]=Bytes(metadata.begin(),metadata.end());}
  for(const auto& entry:files)if(sha256(entry.second)!=recipe.at("files_sha256").at(entry.first))
    throw std::runtime_error("Retail prepared profile mismatch: "+entry.first);
  const auto destination=fs::absolute(output);
  if(fs::exists(destination)||fs::is_symlink(destination))throw std::runtime_error("Destination already exists: "+destination.string());
  fs::create_directories(destination.parent_path());Stage stage(destination.parent_path());
  for(const auto& entry:files)write(stage.path/entry.first,entry.second);
  const auto report=json{{"format",1},{"table",recipe.at("table")},{"build_sha256",recipe.at("build_sha256")},
    {"files",recipe.at("files_sha256")},{"method",dat_only?"Native engine/table initialization + user assets":"Native PE mapping + original asset copies + bounded startup scalars"},{"asset_source",asset_source_name(asset_source)},{"gameplay_profile","shared_native"},{"input_executable_provided",!dat_only},
    {"requires_wine_or_emulator",false},{"native_importer",true}}.dump(2)+"\n";
  write(stage.path/"data.json",Bytes(report.begin(),report.end()));
  if(!fs::create_directory(destination))throw std::runtime_error("Destination already exists: "+destination.string());
  try{publish_stage(stage.path,destination);stage.path.clear();}
  catch(...){std::error_code ignored;fs::remove(destination,ignored);throw;}
}

bool verify_pirate_data(const fs::path& data,const fs::path& recipe,std::string* error){return verify_retail_data(data,recipe,error);}
void import_amiga_adfs(const fs::path& folder,const fs::path& output,const fs::path& metadata,const fs::path& mean_profile){
 const auto destination=fs::absolute(output);
 if(fs::exists(destination)||fs::is_symlink(destination))throw std::runtime_error("Destination already exists");
 auto inputs=read_amiga_adf_set(folder);
 for(auto& entry:inputs)if(entry.second.size()>=4&&std::equal(entry.second.begin(),entry.second.begin()+4,"SLAM"))entry.second=decode_slam(entry.second,4*1024*1024);
 const auto assets=build_amiga_assets(inputs);
 fs::create_directories(destination.parent_path());Stage stage(destination.parent_path());
 const auto data=stage.path/"normalized";
 for(const auto& entry:assets.files)write(data/entry.first,entry.second);
 import_mean({},data,stage.path/"mean",metadata/"mean-retail-startup.json",mean_profile,AssetSource::AmigaAdf);
 for(const auto* table:{"pirate","space","demon"})import_retail({},data,stage.path/table,metadata/(std::string(table)+"-retail-startup.json"),AssetSource::AmigaAdf);
 fs::remove_all(data);
 json input_hashes=json::object();
 for(const auto& entry:inputs)input_hashes[entry.first]=sha256(entry.second);
 const auto manifest=json{{"version",1},{"decoded_input_sha256",input_hashes},{"asset_revision",3},{"table_asset_revisions",{{"mean",2},{"pirate",2},{"space",2},{"demon",3}}},{"asset_source","amiga"},{"gameplay_profile","shared_native"},{"windows_files_required",false},{"presentation_limits",{"unmapped original DMD scenes are not PC replacements"}}}.dump(2)+"\n";
 write(stage.path/"amiga-import.json",Bytes(manifest.begin(),manifest.end()));
 if(!fs::create_directory(destination))throw std::runtime_error("Destination already exists");
 try{publish_stage(stage.path,destination);stage.path.clear();}catch(...){std::error_code ignored;fs::remove(destination,ignored);throw;}
}
void import_pirate_retail(const fs::path& exe,const fs::path& dat,const fs::path& out,const fs::path& recipe){import_retail(exe,dat,out,recipe);}

}
