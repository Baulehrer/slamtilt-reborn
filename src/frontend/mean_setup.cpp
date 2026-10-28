#include "frontend/ui_skin.h"
#include "assets/mean_import.h"
#include <SDL3/SDL.h>
#include <atomic>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;
namespace {
#ifdef SLAM_SETUP_PIRATE
constexpr bool pirate=true;
#else
constexpr bool pirate=false;
#endif
#ifdef SLAM_SETUP_SPACE
constexpr bool space=true;
#else
constexpr bool space=false;
#endif
#ifdef SLAM_SETUP_DEMON
constexpr bool demon=true;
#else
constexpr bool demon=false;
#endif
constexpr bool retail=demon||space||pirate;
const char* title=demon?"NIGHT OF THE DEMON":space?"ACE OF SPACE":pirate?"THE PIRATE":"MEAN MACHINES";
const char* pref_file=demon?"demon-data-path.txt":space?"space-data-path.txt":pirate?"pirate-data-path.txt":"mean-data-path.txt";
const char* pref_temp=demon?"demon-data-path.tmp":space?"space-data-path.tmp":pirate?"pirate-data-path.tmp":"mean-data-path.tmp";

struct Dialog {
  std::string path, error;
  std::atomic<bool> done{false};
};
void SDLCALL selected(void* context, const char* const* files, int) {
  auto& dialog = *static_cast<Dialog*>(context);
  if (!files) dialog.error = SDL_GetError();
  else if (files[0]) dialog.path = files[0];
  dialog.done.store(true);
}

// Argument arrays avoid shell interpretation of user-selected file names.
SDL_Process* process(const std::vector<std::string>& args, const fs::path& cwd = {}) {
  std::vector<const char*> pointers;
  for (const auto& arg : args) pointers.push_back(arg.c_str());
  pointers.push_back(nullptr);
  const auto props = SDL_CreateProperties();
  SDL_SetPointerProperty(props, SDL_PROP_PROCESS_CREATE_ARGS_POINTER, pointers.data());
  if (!cwd.empty()) SDL_SetStringProperty(props, SDL_PROP_PROCESS_CREATE_WORKING_DIRECTORY_STRING, cwd.c_str());
  SDL_SetNumberProperty(props, SDL_PROP_PROCESS_CREATE_STDOUT_NUMBER, SDL_PROCESS_STDIO_NULL);
  SDL_SetNumberProperty(props, SDL_PROP_PROCESS_CREATE_STDERR_NUMBER, SDL_PROCESS_STDIO_NULL);
  auto* child = SDL_CreateProcessWithProperties(props);
  SDL_DestroyProperties(props);
  if (!child) throw std::runtime_error(SDL_GetError());
  return child;
}
bool valid(const fs::path& data, const fs::path& profile) {
  return retail?slam::verify_retail_data(data,profile):slam::verify_mean_data(data,profile);
}
fs::path child_named(const fs::path& parent, const std::string& name) {
  if (!fs::is_directory(parent)) return {};
  for (const auto& item : fs::directory_iterator(parent)) {
    auto candidate = item.path().filename().string();
    for (char& c : candidate) if (c >= 'a' && c <= 'z') c -= 'a' - 'A';
    if (candidate == name) return item.path();
  }
  return {};
}
struct Setup {
  fs::path prefs, importer, profile, result;
  SDL_Process* importing = nullptr;
  std::string status = demon?"Choose original Windows DAT files or prepared Demon data.":space?"Choose original Windows DAT files or prepared Space data.":pirate?"Choose original Windows DAT files or prepared Pirate data.":"Choose original Windows DAT files or prepared game data.";
  bool failed = false;
  explicit Setup(fs::path tool, fs::path hashes) : importer(std::move(tool)), profile(std::move(hashes)) {
    char* directory = SDL_GetPrefPath("SlamTiltNative", "SlamTilt");
    if (!directory) throw std::runtime_error(SDL_GetError());
    prefs = directory;
    SDL_free(directory);
  }
  ~Setup() {
    if (importing) {
      int code;
      SDL_WaitProcess(importing, true, &code);
      SDL_DestroyProcess(importing);
    }
  }
  fs::path saved() const {
    std::ifstream input(prefs / pref_file);
    std::string path;
    std::getline(input, path);
    return path;
  }
  void remember() {
    if (result.string().find_first_of("\r\n") != std::string::npos)
      throw std::runtime_error("Please use a folder without line breaks in its name.");
    const auto temp = prefs / pref_temp;
    { std::ofstream output(temp); output << result.string() << '\n';
      if (!output) throw std::runtime_error("Cannot save the selected data folder."); }
    fs::rename(temp, prefs / pref_file);
  }
  void choose(fs::path path) {
    path = fs::absolute(path);
    failed = false;
    if (valid(path, profile)) { result = path; remember(); return; }
    bool has_adfs=false;
    for(const auto& entry:fs::directory_iterator(path)) {
      auto ext=entry.path().extension().string();
      for(auto& c:ext)if(c>='A'&&c<='Z')c+=('a'-'A');
      has_adfs=has_adfs||(entry.is_regular_file()&&ext==".adf");
    }
    if(has_adfs) {
      const auto root=prefs/("amiga-data-"+std::to_string(SDL_GetTicksNS()));
      auto metadata=profile.parent_path();
      auto mean_profile=metadata/"mean-data.sha256";
      if(!fs::exists(metadata/"mean-retail-startup.json"))metadata=SLAM_ADF_METADATA;
      if(!fs::exists(mean_profile))mean_profile=SLAM_ADF_PROFILE;
      slam::import_amiga_adfs(path,root,metadata,mean_profile);
      result=root/(demon?"demon":space?"space":pirate?"pirate":"mean");
      try {remember();}catch(...){result.clear();std::error_code ignored;fs::remove_all(root,ignored);throw;}
      return;
    }
    auto dat = child_named(path, "DAT");
    if(dat.empty()&&!child_named(path,"MAIN.DAT").empty())dat=path;
    if (dat.empty())
      throw std::runtime_error("No supported data found. Select a DAT folder containing MAIN.DAT and table DAT files.");
    // Unique destinations preserve existing imports, including interrupted attempts.
    result = prefs / (std::string(demon?"demon-data-":space?"space-data-":pirate?"pirate-data-":"mean-data-") + std::to_string(SDL_GetTicksNS()));
    importing = process({importer.string(), dat.string(), result.string()});
    status = demon?"Importing and verifying Night of the Demon data...":space?"Importing and verifying Ace of Space data...":pirate?"Importing and verifying original Pirate data...":"Importing and verifying original Mean Machines data...";
  }
  bool poll() {
    if (!importing) return !result.empty();
    int code = 1;
    if (!SDL_WaitProcess(importing, false, &code)) return false;
    SDL_DestroyProcess(importing); importing = nullptr;
    if (code != 0 || !valid(result, profile)) {
      result.clear();
      throw std::runtime_error(retail?"Import failed. Select supported unchanged Windows DAT files.":"Import failed. Select supported unchanged Windows DAT files.");
    }
    remember();
    return true;
  }
};
}

int main(int argc, char** argv) {
  try {
    fs::path importer, profile, selection, capture;
    bool saved = false;
    int frames = 0;
    for (int i = 1; i < argc; ++i) {
      const std::string arg = argv[i];
      if (arg == "--saved") saved = true;
      else if (i + 1 < argc && arg == "--importer") importer = fs::absolute(argv[++i]);
      else if (i + 1 < argc && arg == "--profile") profile = fs::absolute(argv[++i]);
      else if (i + 1 < argc && arg == "--select") selection = argv[++i];
      else if (i + 1 < argc && arg == "--capture") capture = argv[++i];
      else if (i + 1 < argc && arg == "--frames") frames = std::stoi(argv[++i]);
      else throw std::runtime_error("Invalid setup argument: " + arg);
    }
    if (importer.empty() || profile.empty()) throw std::runtime_error("Missing setup metadata.");
    Setup setup(importer, profile);
    if (saved) {
      const auto path = setup.saved();
      if (path.empty() || !valid(path, profile)) return 2;
      std::cout << path.string() << '\n';
      return 0;
    }
    if (!SDL_Init(SDL_INIT_VIDEO)) throw std::runtime_error(SDL_GetError());
    auto* window = SDL_CreateWindow(demon?"Slam Tilt - Night of the Demon":space?"Slam Tilt - Ace of Space":pirate?"Slam Tilt - The Pirate":"Slam Tilt - Mean Machines", 920, 560, SDL_WINDOW_HIGH_PIXEL_DENSITY);
    if (!window) throw std::runtime_error(SDL_GetError());
    auto* renderer = SDL_CreateRenderer(window, nullptr);
    if (!renderer) throw std::runtime_error(SDL_GetError());
    SDL_SetRenderLogicalPresentation(renderer, 920, 560, SDL_LOGICAL_PRESENTATION_LETTERBOX);
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
    int exit_code = 0;
    {
      slam::UiSkin skin;
      auto dialog = std::make_unique<Dialog>();
      bool dialog_open = false, running = true, ready = false, cancelled = false;
      int frame = 0;
      auto choose = [&](const fs::path& path) {
        try { setup.choose(path); }
        catch (const std::exception& error) { setup.result.clear(); setup.status = error.what(); setup.failed = true; }
      };
      if (!selection.empty()) choose(selection);
      while (running) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
          if (event.type == SDL_EVENT_QUIT || (event.type == SDL_EVENT_KEY_DOWN && event.key.key == SDLK_ESCAPE)) { running = false; cancelled = true; }
          if (event.type == SDL_EVENT_DROP_FILE && event.drop.data && !setup.importing && !dialog_open) choose(event.drop.data);
          bool activate = event.type == SDL_EVENT_KEY_DOWN && (event.key.key == SDLK_RETURN || event.key.key == SDLK_SPACE);
          if (event.type == SDL_EVENT_MOUSE_BUTTON_DOWN && event.button.button == SDL_BUTTON_LEFT) {
            SDL_ConvertEventToRenderCoordinates(renderer, &event);
            activate = event.button.x >= 48 && event.button.x <= 872 && event.button.y >= 285 && event.button.y <= 357;
          }
          if (activate && !dialog_open && !setup.importing) {
            dialog->done.store(false); dialog->path.clear(); dialog->error.clear();
            dialog_open = true;
            SDL_ShowOpenFolderDialog(selected, dialog.get(), window, nullptr, false);
          }
        }
        if (dialog_open && dialog->done.load()) {
          dialog_open = false;
          if (!dialog->error.empty()) { setup.failed = true; setup.status = "Folder dialog unavailable. You can also drop the folder here."; }
          else if (!dialog->path.empty()) choose(dialog->path);
        }
        try { ready = setup.poll(); }
        catch (const std::exception& error) { setup.status = error.what(); setup.failed = true; }
        SDL_SetRenderDrawColor(renderer, 9, 14, 24, 255); SDL_RenderClear(renderer);
        slam::UiSkin::round_rect(renderer, {48, 46, 180, 32}, 8, {35, 52, 69, 255});
        skin.text(renderer, "SLAM TILT NATIVE", 62, 53, 16, {117, 223, 231, 255}, true);
        skin.text(renderer, title, 48, 104, 50, {245, 247, 252, 255}, true);
        skin.text(renderer, "Your table. Your original game data.", 50, 174, 23, {163, 181, 203, 255});
        skin.text(renderer, retail?"Choose the DAT folder or its parent game folder,":"Choose the DAT folder or its parent game folder,", 50, 226, 19, {195, 205, 221, 255});
        skin.text(renderer, "or five Amiga ADFs / already prepared native data.", 50, 252, 19, {195, 205, 221, 255});
        slam::UiSkin::round_rect(renderer, {48, 285, 824, 72}, 14, {24, 145, 163, 255});
        skin.text(renderer, setup.importing ? "PREPARING YOUR TABLE..." : dialog_open ? "SELECT A FOLDER..." : "CHOOSE GAME DATA", 76, 309, 24, {255, 255, 255, 255}, true);
        // Split long diagnostic text into readable lines without exposing raw tool output.
        std::string line;
        float y = 387;
        for (const char c : setup.status + ' ') {
          line += c;
          if (c == ' ' && skin.width(line, 17) > 720) {
            skin.text(renderer, line, 50, y, 17, setup.failed ? SDL_Color{255, 169, 121, 255} : SDL_Color{166, 188, 206, 255});
            y += 25; line.clear();
          }
        }
        if (!line.empty()) skin.text(renderer, line, 50, y, 17, setup.failed ? SDL_Color{255, 169, 121, 255} : SDL_Color{166, 188, 206, 255});
        skin.text(renderer, "Import and play natively. Original files stay untouched.", 50, 504, 16, {126, 148, 170, 255});
        if (!capture.empty() && (ready || (frames > 0 && frame + 1 >= frames))) {
          if (auto* surface = SDL_RenderReadPixels(renderer, nullptr)) { SDL_SaveBMP(surface, capture.c_str()); SDL_DestroySurface(surface); }
        }
        SDL_RenderPresent(renderer);
        ++frame;
        if (ready) running = false;
        if (frames > 0 && frame >= frames) running = false;
        if (!selection.empty() && setup.failed) running = false;
        SDL_Delay(16);
      }
      // Dialog callbacks may run on another thread after closing the window.
      // Keep their tiny context alive if the native dialog is still outstanding.
      if (dialog_open && !dialog->done.load()) dialog.release();
      if (ready && !cancelled) std::cout << setup.result.string() << '\n';
      else exit_code = setup.failed ? 2 : 1;
      if (setup.failed && !selection.empty()) std::cerr << (demon?"Demon setup: ":space?"Space setup: ":pirate?"Pirate setup: ":"Mean setup: ") << setup.status << '\n';
    }
    SDL_DestroyRenderer(renderer); SDL_DestroyWindow(window); SDL_Quit();
    return exit_code;
  } catch (const std::exception& error) {
    std::cerr << (demon?"Demon setup: ":space?"Space setup: ":pirate?"Pirate setup: ":"Mean setup: ") << error.what() << '\n';
    return 2;
  }
}
