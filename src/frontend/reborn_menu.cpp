#include "reborn_menu.h"
#include "assets/windows_table.h"
#include "frontend/ui_skin.h"
#include <algorithm>
#include <cmath>
#include <vector>
namespace slam {
namespace {
constexpr SDL_Color gold{255, 193, 79, 255}, cyan{94, 219, 218, 255};
const std::array<SDL_Color, 4> accents{
    {gold, {88, 211, 189, 255}, {112, 168, 255, 255}, {189, 125, 242, 255}}};
struct Canvas {
  float scale, x, y;
  SDL_FRect rect(SDL_FRect r) const {
    return {x + r.x * scale, y + r.y * scale, r.w * scale, r.h * scale};
  }
};
Canvas canvas(int w, int h, bool classic) {
  const float width = 640.f, height = 512.f;
  (void)classic;
  const float s = std::min(w / width, h / height);
  return {s, (w - width * s) / 2, (h - height * s) / 2};
}
std::array<SDL_FRect, 7> logical_regions(bool classic) {
  (void)classic;
  return {{{170, 182, 310, 55},
             {170, 242, 310, 55},
             {170, 302, 310, 55},
             {170, 362, 310, 55},
             {276, 420, 105, 45},
             {168, 420, 103, 45},
             {480, 483, 150, 25}}};

}
void gradient(SDL_Renderer *r, SDL_FRect b, SDL_Color top, SDL_Color bottom) {
  auto f = [](SDL_Color c) {
    return SDL_FColor{c.r / 255.f, c.g / 255.f, c.b / 255.f, c.a / 255.f};
  };
  SDL_Vertex v[4]{{{b.x, b.y}, f(top), {0, 0}},
                  {{b.x + b.w, b.y}, f(top), {0, 0}},
                  {{b.x + b.w, b.y + b.h}, f(bottom), {0, 0}},
                  {{b.x, b.y + b.h}, f(bottom), {0, 0}}};
  const int indices[]{0, 1, 2, 0, 2, 3};
  SDL_RenderGeometry(r, nullptr, v, 4, indices, 6);
}
std::string fitted(UiSkin &skin, const std::string &text, float size,
                   float width, bool bold = false) {
  if (skin.width(text, size, bold) <= width)
    return text;
  auto s = text;
  while (!s.empty() && skin.width(s + "...", size, bold) > width)
    s.pop_back();
  return s + "...";
}
} // namespace
struct RebornMenu::Impl {
  UiSkin skin;
  SDL_Renderer *renderer = nullptr;
  std::array<SDL_Texture *, 4> previews{};
  std::array<std::filesystem::path, 4> paths{};
  std::array<bool, 4> attempted{};
  int active = 0;
  ~Impl() { clear(); }
  void clear() {
    for (auto *&t : previews) {
      SDL_DestroyTexture(t);
      t = nullptr;
    }
    attempted.fill(false);
  }
  void load(SDL_Renderer *r, const std::array<MenuTableView, 4> &tables) {
    if (renderer != r) {
      clear();
      renderer = r;
    }
    for (unsigned i = 0; i < tables.size(); ++i) {
      if (paths[i] != tables[i].dat) {
        SDL_DestroyTexture(previews[i]);
        previews[i] = nullptr;
        attempted[i] = false;
        paths[i] = tables[i].dat;
      }
      if (attempted[i] || paths[i].empty())
        continue;
      attempted[i] = true;
      try {
        auto image = load_windows_table(paths[i]);
        auto *t = SDL_CreateTexture(r, SDL_PIXELFORMAT_RGBA32,
                                    SDL_TEXTUREACCESS_STATIC, image.width,
                                    image.height);
        if (!t)
          continue;
        if (!SDL_UpdateTexture(t, nullptr, image.rgba.data(),
                               image.width * 4)) {
          SDL_DestroyTexture(t);
          continue;
        }
        SDL_SetTextureScaleMode(t, SDL_SCALEMODE_LINEAR);
        previews[i] = t;
      } catch (const std::exception &) {
      }
    }
  }
};
RebornMenu::RebornMenu() : impl_(std::make_unique<Impl>()) {}
RebornMenu::~RebornMenu() = default;
std::array<SDL_FRect, 7> RebornMenu::regions(int w, int h, bool classic) {
  auto result = logical_regions(classic);
  const auto c = canvas(w, h, classic);
  for (auto &r : result)
    r = c.rect(r);
  return result;
}
std::array<SDL_FRect,2> RebornMenu::source_regions(int w,int h,bool classic) {
  std::array<SDL_FRect,2> regions{{{8,452,48,20},{62,452,80,20}}};
  const auto c=canvas(w,h,classic);for(auto& r:regions)r=c.rect(r);return regions;
}
void RebornMenu::draw(SDL_Renderer *r, int w, int h, int selected,
                      const std::array<MenuTableView, 4> &tables,
                      const std::string &status,
                      SDL_Texture *classic_background, bool classic,
                      bool reduced_motion) {
  if (w <= 0 || h <= 0)
    return;
  auto &im = *impl_;
  auto &skin = im.skin;
  im.load(r, tables);
  if (selected >= 0 && selected < 4)
    im.active = selected;
  selected = std::clamp(selected, 0, 6);
  const auto c = canvas(w, h, classic);
  SDL_SetRenderScale(r, c.scale, c.scale);
  const float x = c.x / c.scale, y = c.y / c.scale;
  SDL_SetRenderDrawBlendMode(r, SDL_BLENDMODE_BLEND);
  const auto box = [&](SDL_FRect b, float radius, SDL_Color color) {
    b.x += x;
    b.y += y;
    UiSkin::round_rect(r, b, radius, color);
  };
  const auto text = [&](const std::string &s, float xx, float yy, float size,
                        SDL_Color color, bool bold = false) {
    skin.text(r, s, x + xx, y + yy, size, color, bold);
  };
  const float t =
      reduced_motion ? 0.f : float(SDL_GetTicks() % 600000) / 1000.f;
  auto regions = logical_regions(true);
  const auto source_controls=[&](){
    const auto& table=tables[im.active];
    const std::array<SDL_FRect,2> controls{{{8,452,48,20},{62,452,80,20}}};
    for(unsigned i=0;i<2;++i){
      const bool active=(table.source==AssetSource::AmigaAdf)==bool(i);
      const bool available=i?table.amiga_available:table.pc_available;
      box(controls[i],4,active?SDL_Color{91,75,40,255}:SDL_Color{22,35,45,255});
      text(i?"AMIGA":"PC",controls[i].x+8,controls[i].y+4,classic?9:10,
           available?(active?gold:cyan):SDL_Color{95,106,112,255},true);
    }
    {text("F3  DATENQUELLE",8,438,8,{160,181,190,255},true);if(table.source==AssetSource::AmigaAdf)text("Gemeinsame Regeln",8,474,8,{160,181,190,255});}

  };
  if (true) {
    SDL_FRect dst{x, y, 640, 480};
    if (classic_background)
      SDL_RenderTexture(r, classic_background, nullptr, &dst);
    else {
      text("SLAMTILT", 112, 40, 64, {221, 228, 233, 255}, true);
      text("REBORN", 236, 112, 30, gold, true);
      for (int i = 0; i < 6; ++i) {
        box(regions[i], 10, {61, 55, 28, 255});
        text(i < 4    ? tables[i].title
             : i == 4 ? "Options"
                      : "Quit",
             regions[i].x + 12, regions[i].y + 12, 17, gold, true);
      }
    }
    if (!classic) {
      // Keep the original artwork intact; the subtitle occupies its dark seam.
      box({245, 163, 150, 15}, 0, {9, 10, 7, 235});
      text("R E B O R N", 267, 164, 11, {210, 222, 94, 255}, true);
      const float space = (w / c.scale - 640.f) / 2.f;
      if ((space >= 100 || preview_open) && im.previews[im.active]) {
        const float px = preview_open ? x + 224 : x + 654, py = y + 158;
        SDL_FRect frame{px, py, preview_open ? 190.f : std::min(space - 22, 190.f), 300};
        gradient(r, frame, {43, 43, 32, 255}, {12, 14, 10, 255});
        float tw = 0, th = 0;
        SDL_GetTextureSize(im.previews[im.active], &tw, &th);
        if (tw > 0 && th > 0) {
          const float scale = std::min((frame.w - 12) / tw, (frame.h - 12) / th);
          SDL_FRect target{frame.x + (frame.w - tw * scale) / 2,
                           frame.y + (frame.h - th * scale) / 2,
                           tw * scale, th * scale};
          SDL_RenderTexture(r, im.previews[im.active], nullptr, &target);
        }
      }
    }
    auto b = regions[selected];
    b.x += x;
    b.y += y;
    SDL_SetRenderDrawColor(r, 215, 232, 77, 255);
    if (classic) SDL_RenderRect(r, &b);
    else {
      SDL_SetRenderDrawColor(r, 220, 237, 94, 255);
      if (!preview_open)
        SDL_RenderLine(r, b.x + 60, b.y + b.h - 6, b.x + b.w - 60, b.y + b.h - 6);
      box({480, 454, 150, 22}, 3, {44, 47, 25, 255});
      text(preview_open ? "V  CLOSE PREVIEW" : "V  TABLE PREVIEW", 490, 459, 9, {222, 232, 109, 255}, true);
    }
    text(SDL_HasGamepad()?"PAD: D-PAD / A SELECT  -  START OPTIONS  -  X SOURCE":"ARROWS / ENTER   O OPTIONS   V PREVIEW", 8, 482, 10,
         {222, 205, 154, 255});
    box(regions[6], 4, {32, 45, 52, 255});
    text("F2  IMPORT DATA", 490, 486, 10, cyan, true);
    text(fitted(skin, status, 10, 470), 8, 498, 10, {157, 175, 187, 255});
    source_controls();
    SDL_SetRenderScale(r, 1, 1);
    return;
  }
}
} // namespace slam
