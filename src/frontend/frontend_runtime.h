#pragma once
#include "assets/mean_import.h"
#include "assets/asset_source.h"
#include "core/sha256.h"
#include <SDL3/SDL.h>
#include <array>
#include <filesystem>
#include <fstream>
#include <memory>
#include <nlohmann/json.hpp>
#include <optional>
#include <stdexcept>
#include <vector>
namespace slam::frontend {
namespace fs = std::filesystem;
using json = nlohmann::json;
struct TableLocation {
  fs::path data, prepared;
};
struct Table {
  const char *id;
  const char *title;
  const char *dat;
  AssetSource source=AssetSource::WindowsDat;
  std::array<TableLocation,2> locations{};
  const TableLocation& location()const{return locations[source==AssetSource::AmigaAdf?1:0];}
  TableLocation& location(){return locations[source==AssetSource::AmigaAdf?1:0];}
  const TableLocation& location(AssetSource selected)const{return locations[selected==AssetSource::AmigaAdf?1:0];}
  void set_location(AssetSource selected,fs::path data,fs::path prepared,bool select=true){locations[selected==AssetSource::AmigaAdf?1:0]={std::move(data),std::move(prepared)};if(select)source=selected;}
  bool select_source(AssetSource selected){if(location(selected).data.empty()||location(selected).prepared.empty())return false;source=selected;return true;}
};
inline std::array<Table, 4> catalog() {
  return {{{"mean", "Mean Machines", "MEAN.DAT"},
           {"pirate", "The Pirate", "PIRATE.DAT"},
           {"space", "Ace of Space", "SPACE.DAT"},
           {"demon", "Night of the Demon", "DEMON.DAT"}}};
}
inline void restore_table(Table& table,const json& value) {
  if(value.contains("sources")) {
    for(const auto& entry:value.at("sources").items()) {
      const auto source=parse_asset_source(entry.key());
      table.set_location(source,entry.value().value("data",std::string{}),entry.value().value("prepared",std::string{}),false);
    }
    const auto selected=parse_asset_source(value.value("source",std::string("windows")));
    if(!table.select_source(selected))table.source=AssetSource::WindowsDat;
  }else table.set_location(AssetSource::WindowsDat,value.value("data",std::string{}),value.value("prepared",std::string{}));
}
inline json table_preferences(const Table& table) {
  json sources=json::object();
  for(auto source:{AssetSource::WindowsDat,AssetSource::AmigaAdf}){
    const auto& location=table.location(source);
    sources[asset_source_name(source)]={{"data",location.data.string()},{"prepared",location.prepared.string()}};
  }
  return {{"source",asset_source_name(table.source)},{"data",table.location().data.string()},
          {"prepared",table.location().prepared.string()},{"sources",sources}};
}
inline fs::path binary_directory() {
  const char *base = SDL_GetBasePath();
  if (!base)
    throw std::runtime_error(SDL_GetError());
  fs::path p = base;
  if (p.filename().empty())
    p = p.parent_path();
  return p;
}
inline json preferences(const fs::path &file, std::string &warning) {
  if (!fs::exists(file))
    return json::object();
  try {
    std::ifstream f(file);
    if (!f)
      throw std::runtime_error("Cannot read menu preferences");
    auto j = json::parse(f);
    if (!j.is_object() || !j.value("tables", json::object()).is_object())
      throw std::runtime_error("Invalid preferences");
    j.value("selected", 0);
    j.value("menu", std::string{});
    const auto table_values = j.value("tables", json::object());
    for (const auto &i : table_values.items()) {
      i.value().value("data", std::string{});
      i.value().value("prepared", std::string{});
      parse_asset_source(i.value().value("source",std::string("windows")));
      if(i.value().contains("sources"))for(const auto& entry:i.value().at("sources").items()){
        parse_asset_source(entry.key());entry.value().value("data",std::string{});entry.value().value("prepared",std::string{});
      }
    }
    return j;
  } catch (const std::exception &) {
    auto backup = file;
    backup += ".invalid-" + std::to_string(SDL_GetTicksNS());
    fs::copy_file(file, backup, fs::copy_options::none);
    warning =
        "Invalid menu preferences preserved as " + backup.filename().string();
    return json::object();
  }
}
inline fs::path runtime_executable(const fs::path& bin, const char* name) {
  auto path=bin/name;
#ifdef _WIN32
  path += ".exe";
#endif
  return path;
}
inline std::vector<std::string>
launch_arguments(const Table &t, unsigned selected, const fs::path &bin,
                 const fs::path &initial, unsigned frames) {
  std::vector<std::string> a;
  if (selected == 0)
    a = {runtime_executable(bin, "slamview").string(),
         (t.location().data / t.dat).string(),
         "--play",
         t.location().prepared.string(),
         "--trace",
         initial.string(),
         "--retail-minigame"};
  else if (selected == 1)
    a = {runtime_executable(bin, "slamview").string(), (t.location().data / t.dat).string(),
         "--pirate-play", t.location().prepared.string()};
  else
    a = {runtime_executable(bin, "slamslice").string(),
         t.id,
         t.location().prepared.string(),
         (t.location().data / t.dat).string(),
         "--presentation",
         "--persist-options",
         "--audio"};
  if (frames) {
    a.push_back("--frames");
    a.push_back(std::to_string(frames));
  }
  return a;
}
class ChildSession {
  SDL_Process *process_ = nullptr;

public:
  ChildSession() = default;
  ChildSession(const ChildSession &) = delete;
  ChildSession &operator=(const ChildSession &) = delete;
  ~ChildSession() { stop(); }
  explicit operator bool() const { return process_ != nullptr; }
  bool start(const std::vector<std::string> &args, const fs::path &profiles,AssetSource source=AssetSource::WindowsDat) {
    if (process_)
      throw std::runtime_error("A table is already running");
    std::vector<const char *> p;
    for (auto &a : args)
      p.push_back(a.c_str());
    p.push_back(nullptr);
    auto props = SDL_CreateProperties();
    auto *env = SDL_CreateEnvironment(true);
    if (!props || !env) {
      if (props)
        SDL_DestroyProperties(props);
      if (env)
        SDL_DestroyEnvironment(env);
      throw std::runtime_error(SDL_GetError());
    }
    const bool configured =
        SDL_SetEnvironmentVariable(env,"SLAM_ASSET_SOURCE",asset_source_name(source),true)&&
        SDL_SetEnvironmentVariable(env, "SLAM_FRONTEND_SESSION", "1", true) &&
        SDL_SetEnvironmentVariable(env, "SLAM_TABLE_PROFILES",
                                   profiles.string().c_str(), true) &&
        SDL_SetPointerProperty(
            props, SDL_PROP_PROCESS_CREATE_ENVIRONMENT_POINTER, env) &&
        SDL_SetPointerProperty(props, SDL_PROP_PROCESS_CREATE_ARGS_POINTER,
                               p.data());
    if (configured)
      process_ = SDL_CreateProcessWithProperties(props);
    SDL_DestroyEnvironment(env);
    SDL_DestroyProperties(props);
    return process_ != nullptr;
  }
  std::optional<int> poll() {
    if (!process_)
      return {};
    int code;
    if (!SDL_WaitProcess(process_, false, &code))
      return {};
    SDL_DestroyProcess(process_);
    process_ = nullptr;
    return code;
  }
  void stop() noexcept {
    if (!process_)
      return;
    SDL_KillProcess(process_, false);
    const auto until = SDL_GetTicks() + 1000;
    while (SDL_GetTicks() < until) {
      if (poll())
        return;
      SDL_Delay(10);
    }
    SDL_KillProcess(process_, true);
    int code;
    SDL_WaitProcess(process_, true, &code);
    SDL_DestroyProcess(process_);
    process_ = nullptr;
  }
};
struct ImportResult {
  std::array<Table, 4> tables;
  fs::path menu;
  unsigned count = 0;
  std::vector<fs::path> created;
};
inline ImportResult
import_tables(const std::array<Table, 4> &current, const fs::path &exe,
              const fs::path &dat, const fs::path &prefs,
              const fs::path &mean_recipe, const fs::path &mean_profile,
              const std::array<fs::path, 3> &retail_recipes) {
  const bool dat_only=exe.empty();
  std::string hash;
  if(!dat_only){
    std::ifstream in(exe,std::ios::binary);
    if(!in)throw std::runtime_error("Cannot read original executable");
    std::vector<std::uint8_t> bytes((std::istreambuf_iterator<char>(in)),{});
    hash=slam::sha256(bytes);
  }
  const bool
      demo = hash ==
             "31192e0b316bf6fe0a4a41336a5ef6ae53ac659c04edf001607a8de63239fc00",
      retail = dat_only ||
          hash ==
          "185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6";
  if (!demo && !retail)
    throw std::runtime_error("Unsupported original executable revision");
  ImportResult result;
  result.tables = current;
  try {
    for (unsigned i = 0; i < 4; ++i) {
      if ((i == 0 && !demo && !retail) || (i > 0 && !retail))
        continue;
      auto &t = result.tables[i];
      if (!fs::is_regular_file(dat / t.dat))
        continue;
      auto dest = prefs / (std::string(t.id) + "-menu-data-" +
                           std::to_string(SDL_GetTicksNS()));
      if (i == 0)
        import_mean(exe, dat, dest, mean_recipe, mean_profile);
      else
        import_retail(exe, dat, dest, retail_recipes[i - 1]);
      result.created.push_back(dest);
      t.set_location(AssetSource::WindowsDat,dest,dest / (std::string(t.id) + "-prepared"));
      ++result.count;
    }
  } catch (...) {
    for (auto &p : result.created) {
      std::error_code ec;
      fs::remove_all(p, ec);
    }
    throw;
  }
  if (!result.count)
    throw std::runtime_error(
        "No supported table data found. Choose a DAT folder with MAIN.DAT and table DAT files.");
  return result;
}
inline void rollback_import(const ImportResult &r) {
  for (auto &p : r.created) {
    std::error_code ec;
    fs::remove_all(p, ec);
  }
}
} // namespace slam::frontend
