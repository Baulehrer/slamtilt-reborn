#pragma once
#include <SDL3/SDL.h>
#include "assets/asset_source.h"
#include <array>
#include <filesystem>
#include <memory>
#include <string>
namespace slam {
struct MenuTableView {
  std::string title;
  std::filesystem::path dat;
  bool ready = false;
  AssetSource source=AssetSource::WindowsDat;
  bool pc_available=false,amiga_available=false;
};
// Presentation only. Own this object inside the renderer's lifetime.
class RebornMenu {
public:
  bool preview_open = false;
  RebornMenu();
  ~RebornMenu();
  RebornMenu(const RebornMenu &) = delete;
  RebornMenu &operator=(const RebornMenu &) = delete;
  static std::array<SDL_FRect, 7> regions(int w, int h, bool classic);
  static std::array<SDL_FRect,2> source_regions(int w,int h,bool classic);
  void draw(SDL_Renderer *, int w, int h, int selected,
            const std::array<MenuTableView, 4> &, const std::string &status,
            SDL_Texture *classic_background, bool classic, bool reduced_motion);

private:
  struct Impl;
  std::unique_ptr<Impl> impl_;
};
} // namespace slam
