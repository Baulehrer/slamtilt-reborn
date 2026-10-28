#ifdef NDEBUG
#undef NDEBUG
#endif
#include "frontend/frontend_runtime.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
int main() {
  using namespace slam::frontend;
  setenv("SDL_VIDEODRIVER", "dummy", 1);
  assert(SDL_Init(SDL_INIT_VIDEO));
  const auto dir = fs::temp_directory_path() /
                   ("reborn-runtime-" + std::to_string(SDL_GetTicksNS()));
  fs::create_directories(dir);
  const auto file = dir / "frontend.json";
  std::string warning;
  {
    std::ofstream f(file);
    f << "{invalid";
  }
  auto recovered = preferences(file, warning);
  assert(recovered.empty() && !warning.empty());
  unsigned backups = 0;
  for (auto &p : fs::directory_iterator(dir))
    if (p.path() != file) {
      ++backups;
      std::ifstream f(p.path());
      std::string text((std::istreambuf_iterator<char>(f)), {});
      assert(text == "{invalid");
    }
  assert(backups == 1);
  {
    std::ofstream f(file);
    f << R"({"selected":3,"menu":"x","tables":{"demon":{"data":"private $ data","prepared":"prepared"}}})";
  }
  warning.clear();
  auto existing = preferences(file, warning);
  assert(warning.empty() && existing["selected"] == 3);
  auto tables = catalog();
  auto restored=tables[0];
  restore_table(restored,{{"data","old-pc-data"},{"prepared","old-pc-prepared"}});
  assert(restored.source==slam::AssetSource::WindowsDat&&restored.location().data=="old-pc-data");
  restored.set_location(slam::AssetSource::AmigaAdf,"amiga-data","amiga-prepared");
  assert(restored.location(slam::AssetSource::WindowsDat).data=="old-pc-data");
  auto persisted=table_preferences(restored);auto reloaded=tables[0];restore_table(reloaded,persisted);
  assert(reloaded.source==slam::AssetSource::AmigaAdf&&reloaded.location().data=="amiga-data");
  assert(reloaded.select_source(slam::AssetSource::WindowsDat)&&reloaded.location().data=="old-pc-data");
  assert(!tables[0].select_source(slam::AssetSource::AmigaAdf));
  assert(slam::highscore_filename("mean",slam::AssetSource::WindowsDat)=="mean-highscores.json");
  assert(slam::highscore_filename("mean",slam::AssetSource::AmigaAdf)=="amiga-mean-highscores.json");
  tables[3].location().data = dir / "$(literal) path";
  tables[3].location().prepared = dir / "prepared";
  auto args = launch_arguments(tables[3], 3, dir, dir / "state.json", 4);
  assert(args[2] == tables[3].location().prepared.string() &&
         args[3] == (tables[3].location().data / "DEMON.DAT").string());
  ChildSession missing;
  assert(!missing.start({(dir / "absent-executable").string()},
                        dir / "profiles.json"));
  assert(!missing);
  {
    ChildSession child;
    assert(child.start({"/bin/sh","-c","test \"$SLAM_ASSET_SOURCE\" = amiga"},dir/"profiles.json",slam::AssetSource::AmigaAdf));
    std::optional<int> result;for(unsigned i=0;i<200&&!result;++i){result=child.poll();SDL_Delay(5);}
    assert(result&&*result==0);
  }
  {
    ChildSession child;
    assert(child.start({"/bin/sh", "-c", "exit 8"}, dir / "profiles.json"));
    std::optional<int> result;
    for (unsigned i = 0; i < 200 && !result; ++i) {
      result = child.poll();
      SDL_Delay(5);
    }
    assert(result && *result == 8 && !child);
  }
  {
    ChildSession child;
    assert(child.start({"/bin/sleep", "60"}, dir / "profiles.json"));
    const auto before = SDL_GetTicks();
    child.stop();
    assert(!child && SDL_GetTicks() - before < 2000);
  }
  fs::remove_all(dir);
  SDL_Quit();
  std::cout << "preferences recovery, argv and child lifecycle PASS\n";
}
