#ifdef NDEBUG
#undef NDEBUG
#endif
#include "frontend/mean_highscores.h"
#include <cassert>
#include <limits>
static void key(MeanHighscores& scores, SDL_Scancode code) {
  SDL_Event event{}; event.type = SDL_EVENT_KEY_DOWN; event.key.scancode = code;
  assert(scores.handle(event));
}
int main() {
  const auto path = std::filesystem::temp_directory_path() / "slam-mean-highscores-test.json";
  std::filesystem::remove(path);
  MeanHighscores scores; scores.load_path(path);
  assert(!scores.begin(0)); scores.reset_session();
  assert(scores.begin(std::numeric_limits<std::uint64_t>::max()));
  key(scores, SDL_SCANCODE_A); key(scores, SDL_SCANCODE_B); key(scores, SDL_SCANCODE_BACKSPACE);
  key(scores, SDL_SCANCODE_C); key(scores, SDL_SCANCODE_RETURN);
  assert(!scores.editing && scores.entries()[0].initials == "AC ");
  assert(!scores.begin(10)); // Same game cannot be recorded twice.
  MeanHighscores loaded; loaded.load_path(path);
  assert(loaded.entries().size() == 1 && loaded.entries()[0].score == std::numeric_limits<std::uint64_t>::max());
  for (unsigned i = 1; i <= 6; ++i) {
    scores.reset_session(); assert(scores.begin(i)); key(scores, SDL_SCANCODE_ESCAPE);
  }
  assert(scores.entries().size() == 5 && scores.entries().back().score == 3);
  scores.reset_session(); assert(!scores.begin(3));
  std::ofstream(path) << "{\"version\":1,\"entries\":[{\"score\":-1,\"initials\":\"ABC\"}]}";
  loaded.load_path(path); assert(loaded.entries().empty() && !loaded.error.empty());
  std::ofstream(path) << "bad json";
  loaded.load_path(path); assert(loaded.entries().empty());
  std::filesystem::remove(path);
  scores.load(false); scores.reset_session(); assert(scores.begin(7)); key(scores, SDL_SCANCODE_RETURN);
  assert(!std::filesystem::exists(path));
}
