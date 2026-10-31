#include "assets/mean_import.h"
#include "core/atomic_file.h"
#include "assets/menu_assets.h"
#include "frontend/frontend_runtime.h"
#include "frontend/port_options.h"
#include "frontend/reborn_menu.h"
#include "frontend/ui_skin.h"
#include <SDL3/SDL.h>
#include <array>
#include <atomic>
#include <cctype>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json = nlohmann::json;
namespace fs = std::filesystem;
namespace {
using slam::frontend::Table;
struct Dialog {
  std::atomic<bool> done{false};
  std::string path, error;
};
void SDLCALL chosen(void *p, const char *const *files, int) {
  std::unique_ptr<std::shared_ptr<Dialog>> ownership(
      static_cast<std::shared_ptr<Dialog> *>(p));
  auto d = *ownership;
  if (!files)
    d->error = SDL_GetError();
  else if (files[0])
    d->path = files[0];
  d->done = true;
}
fs::path child(const fs::path &p, std::string name) {
  if (!fs::is_directory(p))
    return {};
  for (const auto &e : fs::directory_iterator(p)) {
    auto n = e.path().filename().string();
    for (auto &c : n)
      c = char(std::toupper(static_cast<unsigned char>(c)));
    if (n == name)
      return e.path();
  }
  return {};
}
json read(const fs::path &p) {
  std::ifstream f(p);
  if (!f)
    return json::object();
  return json::parse(f);
}
void check(bool ok) {
  if (!ok)
    throw std::runtime_error(SDL_GetError());
}
} // namespace
int main(int argc, char **argv) {
  try {
    fs::path bin = slam::frontend::binary_directory();
    fs::path source = SLAM_MENU_SOURCE,
             share = bin.parent_path() / "share/slamtilt";
    bool bundled = fs::exists(share / "table-profiles.json");
    if (!bundled)
      share = source / "analysis";
    auto recipe = [&](const std::string &id) {
      return bundled ? share / (id + "-retail-startup.json")
                     : share / "import" / (id + "-retail-startup.json");
    };
    check(SDL_Init(SDL_INIT_VIDEO));
    struct SDLGuard {
      ~SDLGuard() { SDL_Quit(); }
    } sdl_guard;
    char *preference = SDL_GetPrefPath("SlamTiltNative", "SlamTilt");
    check(preference != nullptr);
    fs::path prefs = preference;
    SDL_free(preference);
    fs::path config = prefs / "frontend.json", menu_path, import_path, capture,
             trace, events_path, session_reports;
    unsigned frames = 0, child_frames = 0;
    int preview_width = 1280, preview_height = 800;
    bool preview_size = false;
    bool fullscreen = true, fullscreen_explicit = false, exercise = false;
    for (int i = 1; i < argc; ++i) {
      std::string a = argv[i];
      if (a == "--windowed") {
        fullscreen = false;
        fullscreen_explicit = true;
        continue;
      }
      if (a == "--fullscreen") {
        fullscreen = true;
        fullscreen_explicit = true;
        continue;
      }
      if (a == "--exercise-all") {
        exercise = true;
        continue;
      }
      if (a == "--help") {
        std::cout
            << "slamtilt-reborn [--fullscreen|--windowed] [--import "
               "DAT_OR_GAME_FOLDER] [--config FILE]\nArrows/Enter select, F2 "
               "import data, O options, F10 return from a table.\n";
        return 0;
      }
      if (i + 1 >= argc)
        throw std::runtime_error("Missing argument: " + a);
      if (a == "--config")
        config = argv[++i];
      else if (a == "--menu")
        menu_path = argv[++i];
      else if (a == "--import")
        import_path = argv[++i];
      else if (a == "--preview-size") {
        const std::string size = argv[++i];
        const auto split = size.find('x');
        if (split == std::string::npos)
          throw std::runtime_error("Size must be WIDTHxHEIGHT");
        std::size_t used_w = 0, used_h = 0;
        preview_width = std::stoi(size.substr(0, split), &used_w);
        preview_height = std::stoi(size.substr(split + 1), &used_h);
        if (used_w != split || used_h != size.size() - split - 1 ||
            preview_width < 640 || preview_width > 7680 ||
            preview_height < 480 || preview_height > 4320)
          throw std::runtime_error("Invalid preview dimensions");
        preview_size = true;
      } else if (a == "--frames")
        frames = std::stoul(argv[++i]);
      else if (a == "--child-frames")
        child_frames = std::stoul(argv[++i]);
      else if (a == "--capture")
        capture = argv[++i];
      else if (a == "--trace")
        trace = argv[++i];
      else if (a == "--session-reports")
        session_reports = fs::absolute(argv[++i]);
      else if (a == "--ui-events")
        events_path = argv[++i];
      else
        throw std::runtime_error("Unknown argument: " + a);
    }
    if (exercise && !child_frames)
      throw std::runtime_error("--exercise-all requires --child-frames");
    auto tables = slam::frontend::catalog();
    std::string preference_warning;
    auto saved = slam::frontend::preferences(config, preference_warning);
    int selected = saved.value("selected", 0);
    selected = std::clamp(selected, 0, 3);
    int last_table = selected;
    int source_table=selected;
    if (menu_path.empty())
      menu_path = saved.value("menu", std::string{});
    for (auto &t : tables) {
      if (saved.contains("tables") && saved["tables"].contains(t.id)) {
        auto v = saved["tables"][t.id];
        slam::frontend::restore_table(t,v);
      } else {
        std::ifstream f(prefs / (std::string(t.id) + "-data-path.txt"));
        std::string p;
        std::getline(f, p);
        if (!p.empty()) {
          t.location().data = p;
          t.location().prepared = t.location().data / (std::string(t.id) + "-prepared");
        }
      }
    }
    if (!bundled) {
      auto game = source / "build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/"
                           "Game Files/SLAMTILT";
      if (menu_path.empty())
        menu_path = game / "DAT/MENU.DAT";
      for (auto &t : tables)
        if (t.location().data.empty()) {
          if (std::string(t.id) == "mean") {
            t.location().data = source / "build/corpus/win95/demo-1997/Slam Tilt Demo "
                              "(Windows, 1996) - SLAMTILT/DAT";
            t.location().prepared = source / "build/mean-prepared";
          } else if (std::string(t.id) == "pirate") {
            t.location().data = source / "build/imported/pirate-retail";
            t.location().prepared = t.location().data / "pirate-prepared";
          } else {
            t.location().data = game / "DAT";
            t.location().prepared =
                source / "build/oracle" / (std::string(t.id) + "-full-game");
          }
        }
    }
    auto save = [&]() {
      json x{{"version", 1},
             {"selected", last_table},
             {"menu", menu_path.string()}};
      for (auto &t : tables)
        x["tables"][t.id] = slam::frontend::table_preferences(t);
      fs::create_directories(fs::absolute(config).parent_path());
      auto tmp = config;
      tmp += ".tmp";
      {
        std::ofstream f(tmp);
        f << x.dump(2) << '\n';
        if (!f)
          throw std::runtime_error("Cannot save menu preferences");
      }
      slam::atomic_replace_file(tmp, config);
    };
    std::string status = preference_warning.empty()
                             ? "Choose a table · F2 imports your original data"
                             : preference_warning;
    auto import = [&](fs::path folder) {
      bool adfs=false;
      for(const auto& entry:fs::directory_iterator(folder)) {
        auto ext=entry.path().extension().string();
        for(auto& c:ext)c=static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        adfs=adfs||(entry.is_regular_file()&&ext==".adf");
      }
      if(adfs) {
        auto destination=prefs/"amiga-import";
        for(unsigned n=1;fs::exists(destination);++n)destination=prefs/("amiga-import-"+std::to_string(n));
        const auto previous=tables;
        bool imported=false;
        try {
          slam::import_amiga_adfs(folder,destination,
            bundled?share:share/"import",
            bundled?share/"mean-data.sha256":source/"packaging/mean-data.sha256");
          imported=true;
          for(auto& t:tables)t.set_location(slam::AssetSource::AmigaAdf,
            destination/t.id,destination/t.id/(std::string(t.id)+"-prepared"));
          save();
        } catch(...) {
          tables=previous;
          std::error_code ignored;if(imported)fs::remove_all(destination,ignored);
          throw;
        }
        status="4 Amiga tables imported · shared native rules";
        return;
      }
      auto dat = child(folder, "DAT");
      if(dat.empty()&&!child(folder,"MAIN.DAT").empty())dat=folder;
      if (dat.empty())
        throw std::runtime_error(
            "Choose a DAT folder containing MAIN.DAT and table DAT files");
      auto result = slam::frontend::import_tables(
          tables, {}, dat, prefs,
          bundled ? share / "mean-demo-startup.json"
                  : share / "import/mean-demo-startup.json",
          bundled ? share / "mean-data.sha256"
                  : source / "packaging/mean-data.sha256",
          {recipe("pirate"), recipe("space"), recipe("demon")});
      auto previous_tables = tables;
      auto previous_menu = menu_path;
      try {
        tables = result.tables;
        auto m = child(dat, "MENU.DAT");
        if (!m.empty()) {
          try {
            slam::load_windows_menu(m);
            menu_path = m;
          } catch (const std::exception &) {
          }
        }
        save();
      } catch (...) {
        tables = previous_tables;
        menu_path = previous_menu;
        slam::frontend::rollback_import(result);
        throw;
      }
      status = std::to_string(result.count) +
               " table(s) imported.";
    };
    if (!import_path.empty())
      import(fs::absolute(import_path));
    auto *window =
        SDL_CreateWindow("Slamtilt - Reborn", preview_width, preview_height,
                         SDL_WINDOW_RESIZABLE | SDL_WINDOW_HIGH_PIXEL_DENSITY);
    check(window != nullptr);
    std::unique_ptr<SDL_Window, decltype(&SDL_DestroyWindow)> window_owner(
        window, SDL_DestroyWindow);
    auto *renderer = SDL_CreateRenderer(window, nullptr);
    check(renderer != nullptr);
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)>
        renderer_owner(renderer, SDL_DestroyRenderer);
    SDL_SetRenderVSync(renderer, 1);

    slam::GamepadInput gamepad;
    json controller_frames=json::array();
    PortOptions options;
    options.full_controls = false;
    options.load(true);
    options.main_menu_available = false;
    if (fullscreen_explicit)
      options.settings.fullscreen = fullscreen;
    bool applied_fullscreen = false;
    int applied_width = preview_width, applied_height = preview_height;
    if (preview_size) {
      options.settings.window_width = preview_width;
      options.settings.window_height = preview_height;
    }
    slam::RebornMenu menu_view;
    SDL_Texture *background = nullptr;
    std::unique_ptr<SDL_Texture, decltype(&SDL_DestroyTexture)>
        background_owner(nullptr, SDL_DestroyTexture);
    auto load_menu = [&]() {
      if (background) {
        background_owner.reset();
        background = nullptr;
      }
      if (menu_path.empty() || !fs::exists(menu_path))
        return;
      try {
        auto image = slam::load_windows_menu(menu_path);
        background = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32,
                                       SDL_TEXTUREACCESS_STATIC, image.width,
                                       image.height);
        check(background != nullptr);
        background_owner.reset(background);
        check(SDL_UpdateTexture(background, nullptr, image.rgba.data(),
                                image.width * 4));
        SDL_SetTextureScaleMode(background, SDL_SCALEMODE_LINEAR);
      } catch (const std::exception &e) {
        background_owner.reset();
        background = nullptr;
        status = e.what();
      }
    };
    load_menu();
    auto dialog = std::make_shared<Dialog>();
    bool dialog_open = false, running = true;
    slam::frontend::ChildSession process;
    json journal = json::array(), scheduled = json::array();
    if (!events_path.empty())
      scheduled = read(events_path).at("events");
    unsigned exercise_index = 0;
    const auto menu_started = SDL_GetTicksNS();
    unsigned menu_frames = 0;
    auto start = [&]() {
      last_table = selected;
      auto &t = tables[selected];
      if (!fs::exists(t.location().data / t.dat) || !fs::is_directory(t.location().prepared)) {
        status = std::string(t.title) + ": import original data with F2";
        return;
      }
      auto args = slam::frontend::launch_arguments(
          t, unsigned(selected), bin,
          bundled ? share / "initial-state.json"
                  : source / "analysis/traces/mean-flight-100.json",
          child_frames);
      try {
        save();
      } catch (const std::exception &e) {
        status = e.what();
        journal.push_back(
            {{"event", "launch_failed"}, {"table", t.id}, {"error", status}});
        return;
      }
      if (!session_reports.empty()) {
        fs::create_directories(session_reports);
        const auto stem = session_reports / (std::string(t.id) + "-" +
                                             std::to_string(SDL_GetTicksNS()));
        args.push_back(selected < 2 ? "--trace-output" : "--trace");
        args.push_back(stem.string() + ".json");
        if (selected == 1)
          args.push_back("--full-state-trace");
        if (selected > 0) {
          args.push_back("--audio-trace");
          args.push_back(stem.string() + "-audio.json");
        }
      }
      if (!process.start(args, share / "table-profiles.json",t.source)) {
        status = SDL_GetError();
        journal.push_back(
            {{"event", "launch_failed"}, {"table", t.id}, {"error", status}});
        return;
      }
      journal.push_back({{"event", "launched"}, {"table", t.id}});
      SDL_HideWindow(window);
    };
    auto choose_source=[&](slam::AssetSource source){
      const int i=selected<4?selected:source_table;auto& table=tables[i];const auto previous=table.source;
      if(!table.select_source(source)){status=std::string(table.title)+": import "+slam::asset_source_label(source)+" data with F2";return;}
      try{save();status=std::string(table.title)+" · "+slam::asset_source_label(source);}
      catch(const std::exception&e){table.source=previous;status=e.what();}
    };
    for (unsigned frame = 0; running && (!frames || frame < frames); ++frame) {
      if (process) {
        auto completed = process.poll();
        if (completed) {
          const int code = *completed;
          journal.push_back({{"event", "returned"},
                             {"table", tables[selected].id},
                             {"exit_code", code}});
          if (exercise && code)
            throw std::runtime_error("Table smoke test failed");
          SDL_ShowWindow(window);
          SDL_RaiseWindow(window);
          options.load(true);
          status = code ? "Table exited with an error. Your data is preserved."
                        : "Choose your next table";
        } else {
          SDL_Event pending;
          while (SDL_PollEvent(&pending))
            if (pending.type == SDL_EVENT_QUIT ||
                pending.type == SDL_EVENT_WINDOW_CLOSE_REQUESTED)
              running = false;
          if (!running)
            break;
          SDL_Delay(10);
          continue;
        }
      }
      if (exercise) {
        if (exercise_index == 4) {
          running = false;
          break;
        }
        selected = int(exercise_index++);
        start();
        if (!process)
          throw std::runtime_error(status);
        continue;
      }
      for (const auto &e : scheduled)
        if (e.at("frame") == frame) {
          SDL_Event event{};
          if(e.value("type",std::string("key"))=="click"){
            event.type=SDL_EVENT_MOUSE_BUTTON_DOWN;event.button.button=SDL_BUTTON_LEFT;
            event.button.x=e.at("x").get<float>();event.button.y=e.at("y").get<float>();
          }else{
            event.type = SDL_EVENT_KEY_DOWN;
            event.key.key =SDL_GetKeyFromName(e.at("key").get<std::string>().c_str());
          }
          SDL_PushEvent(&event);
        }
      if (dialog_open && dialog->done) {
        dialog_open = false;
        if (!dialog->error.empty())
          status = dialog->error;
        else if (!dialog->path.empty()) {
          try {
            import(dialog->path);
            load_menu();
          } catch (const std::exception &e) {
            status = e.what();
          }
        }
      }
      if (!frames && (options.settings.fullscreen != applied_fullscreen ||
                      options.settings.window_width != applied_width ||
                      options.settings.window_height != applied_height)) {
        check(SDL_SetWindowFullscreen(window, false));
        check(SDL_SetWindowSize(window, options.settings.window_width,
                                options.settings.window_height));
        check(SDL_SetWindowFullscreen(window, options.settings.fullscreen));
        applied_fullscreen = options.settings.fullscreen;
        applied_width = options.settings.window_width;
        applied_height = options.settings.window_height;
      }
      int w, h;
      SDL_GetRenderOutputSize(renderer, &w, &h);
      const auto boxes =
          slam::RebornMenu::regions(w, h, !options.settings.modern_menu);
      const auto source_boxes=slam::RebornMenu::source_regions(w,h,!options.settings.modern_menu);
      SDL_Event e;
      while (gamepad.poll(e,options.settings.keys,options.settings.gamepad_buttons,true,options.gamepad_binding())) {
        if (e.type == SDL_EVENT_QUIT ||
            e.type == SDL_EVENT_WINDOW_CLOSE_REQUESTED)
          running = false;
        if (options.handle(e))
          continue;
        if (options.open)
          continue;
        bool activate = false;
        if (e.type == SDL_EVENT_KEY_DOWN && !e.key.repeat) {
          if (e.key.key >= SDLK_1 && e.key.key <= SDLK_4)
            selected = int(e.key.key - SDLK_1);
          else if (e.key.key == SDLK_UP)
            selected = (selected + 6) % 7;
          else if (e.key.key == SDLK_DOWN)
            selected = (selected + 1) % 7;
          else if (e.key.key == SDLK_LEFT)
            selected = selected == 4 ? 5 : std::max(0, selected - 1);
          else if (e.key.key == SDLK_RIGHT)
            selected = selected == 5 ? 4 : std::min(6, selected + 1);
          else if (e.key.key == SDLK_RETURN || e.key.key == SDLK_SPACE ||
                   (e.key.key == SDLK_R && SDL_getenv("SLAMTILT_CABINET_KEYBOARD")))
            activate = true;
          else if (e.key.key == SDLK_V) {
            menu_view.preview_open = !menu_view.preview_open;
          } else if (e.key.key == SDLK_O) {
            selected = 4;
            activate = true;
          } else if(e.key.key==SDLK_F3){
            const auto source=tables[selected<4?selected:source_table].source;
            choose_source(source==slam::AssetSource::WindowsDat?slam::AssetSource::AmigaAdf:slam::AssetSource::WindowsDat);
          } else if (e.key.key == SDLK_F2 && !dialog_open) {
            dialog->done = false;
            dialog->path.clear();
            dialog->error.clear();
            dialog_open = true;
            SDL_ShowOpenFolderDialog(chosen,
                                     new std::shared_ptr<Dialog>(dialog),
                                     window, nullptr, false);
          }
        }
        if (e.type == SDL_EVENT_MOUSE_MOTION ||
            e.type == SDL_EVENT_MOUSE_BUTTON_DOWN) {
          float x = (e.type == SDL_EVENT_MOUSE_MOTION ? e.motion.x
                                                      : e.button.x),
                y = (e.type == SDL_EVENT_MOUSE_MOTION ? e.motion.y
                                                      : e.button.y);
          int ww, wh;
          SDL_GetWindowSize(window, &ww, &wh);
          if (ww <= 0 || wh <= 0)
            continue;
          SDL_FPoint p{x * w / ww, y * h / wh};
          if(e.type==SDL_EVENT_MOUSE_BUTTON_DOWN&&e.button.button==SDL_BUTTON_LEFT){
            auto preview_box = boxes[6];
            preview_box.y -= 29.f * (preview_box.h / 25.f);
            preview_box.h *= 22.f / 25.f;
            if(options.settings.modern_menu && SDL_PointInRectFloat(&p,&preview_box)) {
              menu_view.preview_open = !menu_view.preview_open;
              continue;
            }
            bool handled=false;for(unsigned i=0;i<2;++i)if(SDL_PointInRectFloat(&p,&source_boxes[i])){choose_source(i?slam::AssetSource::AmigaAdf:slam::AssetSource::WindowsDat);handled=true;}
            if(handled)continue;
          }
          for (int i = 0; i < 7; ++i)
            if (SDL_PointInRectFloat(&p, &boxes[i])) {
              selected = i;
              activate = e.type == SDL_EVENT_MOUSE_BUTTON_DOWN &&
                         e.button.button == SDL_BUTTON_LEFT;
            }
        }
        if (activate) {
          if (selected < 4) {
            start();
            if (process)
              break;
          } else if (selected == 4) {
            SDL_Event key{};
            key.type = SDL_EVENT_KEY_DOWN;
            key.key.key = SDLK_ESCAPE;
            options.handle(key);
          } else if (selected == 6 && !dialog_open) {
            dialog = std::make_shared<Dialog>();
            dialog_open = true;
            SDL_ShowOpenFolderDialog(chosen,
                                     new std::shared_ptr<Dialog>(dialog),
                                     window, nullptr, false);
          } else if (selected == 5)
            running = false;
        }
      }
      if (process)
        continue;
      if(selected<4)source_table=selected;
      std::array<slam::MenuTableView, 4> views;
      for (unsigned i = 0; i < 4; ++i)
        views[i] = {tables[i].title, tables[i].location().data / tables[i].dat,
                    fs::exists(tables[i].location().data / tables[i].dat) &&
                        fs::is_directory(tables[i].location().prepared),tables[i].source,
                    !tables[i].location(slam::AssetSource::WindowsDat).data.empty(),
                    !tables[i].location(slam::AssetSource::AmigaAdf).data.empty()};
      SDL_SetRenderDrawColor(renderer, 3, 5, 8, 255);
      SDL_RenderClear(renderer);
      menu_view.draw(renderer, w, h, selected, views, status, background,
                     !options.settings.modern_menu,
                     options.settings.reduced_motion);
      options.draw(renderer, w, h);
      if (!capture.empty() && frames && frame + 1 == frames) {
        auto *s = SDL_RenderReadPixels(renderer, nullptr);
        check(s != nullptr);
        check(SDL_SaveBMP(s, capture.string().c_str()));
        SDL_DestroySurface(s);
      }
      SDL_RenderPresent(renderer);
      if(!trace.empty() && gamepad.connected())controller_frames.push_back({{"event","controller_frame"},{"selected",selected},{"options_open",options.open}});
      ++menu_frames;
      SDL_Delay(8);
    }
    process.stop();
    save();
    if (!trace.empty()) {
      std::ofstream f(trace);
      int logical_w = 0, logical_h = 0, pixel_w = 0, pixel_h = 0;
      SDL_GetWindowSize(window, &logical_w, &logical_h);
      SDL_GetRenderOutputSize(renderer, &pixel_w, &pixel_h);
      f << json{{"project", "Slamtilt - Reborn"},
                {"renderer", SDL_GetRendererName(renderer)},
                {"window_size", {logical_w, logical_h}},
                {"render_size", {pixel_w, pixel_h}},
                {"pixel_density", SDL_GetWindowPixelDensity(window)},
                {"preview_open", menu_view.preview_open},
                {"frames", menu_frames},
                {"elapsed_ms", (SDL_GetTicksNS() - menu_started) / 1e6},
                {"selected", selected},
                {"asset_source",slam::asset_source_name(tables[source_table].source)},
                {"original_menu", background != nullptr},
                {"options_open", options.open},
                {"menu_style",
                 options.settings.modern_menu ? "reborn" : "classic"},
                {"events", journal},
                {"controller_frames",controller_frames},
                {"status", status}}
               .dump(2)
        << '\n';
    }
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "Slam Tilt menu: " << e.what() << '\n';
    return 2;
  }
}
