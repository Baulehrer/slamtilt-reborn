#ifdef NDEBUG
#undef NDEBUG
#endif
#include "core/atomic_file.h"
#include "frontend/frontend_runtime.h"
#include "frontend/pirate_highscores.h"
#include <cassert>
#include <fstream>
#include <iostream>
int main(int argc, char **argv) {
  if (argc > 1 && std::string(argv[1]) == "--child")
    return 7;
  namespace fs = std::filesystem;
  auto dir = fs::temp_directory_path() /
             ("slam-windows-" + std::to_string(GetCurrentProcessId()));
  fs::create_directories(dir);
  auto target = dir / "preferences.json", tmp = dir / "preferences.tmp";
  {
    std::ofstream f(target);
    f << "old";
  }
  {
    std::ofstream f(tmp);
    f << "new";
  }
  slam::atomic_replace_file(tmp, target);
  std::string contents;
  {
    std::ifstream f(target);
    f >> contents;
  }
  assert(contents == "new");
  PirateHighscores scores;
  PirateHighscores::Records records{};
  assert(scores.save(dir / "scores.json", records));
  records[0] = 0x12;
  assert(scores.save(dir / "scores.json", records));
  assert(scores.load(dir / "scores.json") == records);
  assert(SDL_Init(0));
  slam::frontend::ChildSession child;
  assert(child.start({fs::absolute(argv[0]).string(), "--child"},
                     dir / "table-profiles.json"));
  std::optional<int> result;
  for (int i = 0; i < 200 && !result; ++i) {
    result = child.poll();
    SDL_Delay(10);
  }
  assert(result && *result == 7);
  assert(slam::frontend::runtime_executable(dir, "slamview").extension() ==
         ".exe");
  SDL_Quit();
  fs::remove_all(dir);
  std::cout << "PASS Windows replace-existing preferences, highscore "
               "roundtrip/overwrite, .exe child process exit\n";
}
