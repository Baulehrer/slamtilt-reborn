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
  const float width = classic ? 640.f : 1280.f,
              height = classic ? 512.f : 800.f;
  const float s = std::min(w / width, h / height);
  return {s, (w - width * s) / 2, (h - height * s) / 2};
}
std::array<SDL_FRect, 7> logical_regions(bool classic) {
  if (classic)
    return {{{170, 182, 310, 55},
             {170, 242, 310, 55},
             {170, 302, 310, 55},
             {170, 362, 310, 55},
             {276, 420, 105, 45},
             {168, 420, 103, 45},
             {480, 483, 150, 25}}};
  return {{{56, 225, 470, 88},
           {56, 326, 470, 88},
           {56, 427, 470, 88},
           {56, 528, 470, 88},
           {56, 649, 166, 49},
           {1112, 36, 112, 38},
           {234, 649, 292, 49}}};
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
void line(SDL_Renderer *r, float x1, float y1, float x2, float y2,
          SDL_Color c) {
  SDL_SetRenderDrawColor(r, c.r, c.g, c.b, c.a);
  SDL_RenderLine(r, x1, y1, x2, y2);
}
void glow(SDL_Renderer *r, SDL_FRect rect, SDL_Color color, int strength = 5) {
  for (int i = strength; i > 0; --i) {
    auto c = color;
    c.a = Uint8(3 + (strength - i) * 2);
    UiSkin::round_rect(r,
                       {rect.x - i * 4.f, rect.y - i * 4.f, rect.w + i * 8.f,
                        rect.h + i * 8.f},
                       16 + i * 3.f, c);
  }
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
  std::array<SDL_FRect,2> regions=classic?std::array<SDL_FRect,2>{{{8,452,48,20},{62,452,80,20}}}:
                                              std::array<SDL_FRect,2>{{{56,707,70,22},{134,707,100,22}}};
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
  auto regions = logical_regions(classic);
  const auto source_controls=[&](){
    const auto& table=tables[im.active];
    const std::array<SDL_FRect,2> controls=classic?std::array<SDL_FRect,2>{{{8,452,48,20},{62,452,80,20}}}:
                                                        std::array<SDL_FRect,2>{{{56,707,70,22},{134,707,100,22}}};
    for(unsigned i=0;i<2;++i){
      const bool active=(table.source==AssetSource::AmigaAdf)==bool(i);
      const bool available=i?table.amiga_available:table.pc_available;
      box(controls[i],4,active?SDL_Color{91,75,40,255}:SDL_Color{22,35,45,255});
      text(i?"AMIGA":"PC",controls[i].x+8,controls[i].y+4,classic?9:10,
           available?(active?gold:cyan):SDL_Color{95,106,112,255},true);
    }
    if(classic){text("F3  DATENQUELLE",8,438,8,{160,181,190,255},true);if(table.source==AssetSource::AmigaAdf)text("Gemeinsame Regeln",8,474,8,{160,181,190,255});}
    else text(std::string("F3  ")+asset_source_label(table.source),251,713,10,{160,181,190,255},true);
  };
  if (classic) {
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
    auto b = regions[selected];
    b.x += x;
    b.y += y;
    SDL_SetRenderDrawColor(r, gold.r, gold.g, gold.b, 255);
    SDL_RenderRect(r, &b);
    text("ARROWS / ENTER  -  O Options  -  F10 Main Menu in game", 8, 482, 10,
         {222, 205, 154, 255});
    box(regions[6], 4, {32, 45, 52, 255});
    text("F2  IMPORT DATA", 490, 486, 10, cyan, true);
    text(fitted(skin, status, 10, 470), 8, 498, 10, {157, 175, 187, 255});
    source_controls();
    SDL_SetRenderScale(r, 1, 1);
    return;
  }
  // Procedural cabinet materials: no bundled original artwork.
  gradient(r, {x, y, 1280, 800}, {17, 27, 39, 255}, {3, 8, 14, 255});
  for (int j = 0; j < 800; j += 4)
    line(r, x, y + j, x + 1280, y + j,
         {130, 151, 164, Uint8(j % 12 == 0 ? 5 : 2)});
  for (int k = -8; k < 20; ++k)
    line(r, x + k * 110.f, y + 800, x + k * 110.f + 430, y + 260,
         {36, 113, 131, 13});
  for (int i = 0; i < 17; ++i) {
    float px =
        std::fmod(149.f * i + std::sin(t * .14f + i) * 23 + 1280, 1280.f);
    float py = std::fmod(73.f * i + std::cos(t * .12f + i) * 29 + 800, 800.f);
    box({px, py, 2, 2}, 1, {255, 192, 93, Uint8(22 + i % 5 * 9)});
  }
  glow(r, {66 + x, 90 + y, 409, 4}, gold, 8);
  glow(r, {1062 + x, 210 + y, 5, 356}, cyan, 7);
  text("SLAMTILT", 55, 34, 68, {0, 0, 0, 210}, true);
  text("SLAMTILT", 52, 29, 68, {103, 130, 146, 255}, true);
  text("SLAMTILT", 52, 25, 68, {233, 239, 239, 255}, true);
  SDL_Rect clip{int(x + 52), int(y + 65), 430, 28};
  SDL_SetRenderClipRect(r, &clip);
  text("SLAMTILT", 52, 25, 68, {117, 142, 155, 255}, true);
  SDL_SetRenderClipRect(r, nullptr);
  text("R E B O R N", 57, 107, 21, gold, true);
  line(r, x + 58, y + 142, x + 525, y + 142, {218, 174, 86, 140});
  text("FOUR TABLES. ONE MORE GAME.", 58, 159, 11, {133, 157, 176, 255}, true);
  text("SELECT YOUR TABLE", 58, 199, 12, {215, 226, 234, 255}, true);
  // Amber dot-matrix annunciator with static scanlines and warm lamp border.
  box({580, 35, 500, 66}, 12, {62, 48, 24, 255});
  box({583, 38, 494, 60}, 10, {11, 13, 12, 255});
  for (int yy = 47; yy < 91; yy += 5)
    for (int xx = 593; xx < 1064; xx += 5)
      box({float(xx), float(yy), 1.4f, 1.4f}, .7f, {137, 78, 20, 26});
  text("PLAYER ONE  /  READY TO ROLL", 601, 48, 12, {176, 117, 49, 255}, true);
  text(fitted(skin, tables[im.active].title, 19, 450, true), 601, 65, 19, gold,
       true);
  for (int i = 0; i < 4; ++i) {
    auto b = regions[i];
    const bool on = selected == i;
    auto accent = accents[i];
    if (on)
      glow(r, {x + b.x, y + b.y, b.w, b.h}, accent, 5);
    box({b.x, b.y + 3, b.w, b.h}, 14, {0, 0, 0, 130});
    box(b, 12, on ? SDL_Color{151, 119, 60, 255} : SDL_Color{56, 73, 86, 255});
    box({b.x + 1, b.y + 1, b.w - 2, b.h - 2}, 11,
        on ? SDL_Color{42, 44, 38, 255} : SDL_Color{18, 28, 40, 255});
    line(r, x + b.x + 15, y + b.y + 2, x + b.x + b.w - 15, y + b.y + 2,
         on ? SDL_Color{244, 210, 133, 210} : SDL_Color{130, 156, 173, 80});
    box({b.x + 12, b.y + 12, 54, 64}, 7, {6, 12, 18, 255});
    if (im.previews[i]) {
      SDL_FRect src{90, 80, 140, 190}, dest{x + b.x + 13, y + b.y + 13, 52, 62};
      SDL_RenderTexture(r, im.previews[i], &src, &dest);
    } else {
      text("0" + std::to_string(i + 1), b.x + 23, b.y + 25, 19, accent, true);
    }
    box({b.x + 2, b.y + 18, 3, b.h - 36}, 1, accent);
    text(tables[i].title, b.x + 82, b.y + 16, i == 3 ? 22 : 25,
         on ? SDL_Color{254, 235, 183, 255} : SDL_Color{218, 227, 236, 255},
         true);
    text(tables[i].ready ? (tables[i].source==AssetSource::AmigaAdf?"AMIGA  /  READY TO PLAY":"PC  /  READY TO PLAY") : "IMPORT ORIGINAL DATA", b.x + 83,
         b.y + 55, 10, tables[i].ready ? accent : SDL_Color{151, 152, 147, 255},
         true);
    text(on ? ">" : "+", b.x + b.w - 30, b.y + 30, 20,
         on ? gold : SDL_Color{98, 125, 145, 255}, true);
  }
  auto panel = SDL_FRect{566, 128, 658, 582};
  box({panel.x + 5, panel.y + 9, panel.w, panel.h}, 20, {0, 0, 0, 100});
  box(panel, 18, {58, 78, 90, 255});
  box({568, 130, 654, 578}, 17, {9, 18, 27, 255});
  for (int n = 0; n < 4; ++n) {
    float py = 165 + n * 151.f;
    line(r, x + 600, y + py, x + 1204, y + py + 70, {32, 67, 78, 80});
  }
  text("THE ORIGINAL PLAYFIELD", 590, 147, 10, {133, 156, 172, 255}, true);
  text("NATIVE / 200 HZ", 1073, 147, 10, cyan, true);
  const auto accent = accents[im.active];
  SDL_FRect play{x + 751, y + 183, 260, 487.5f};
  glow(r, {play.x - 3, play.y - 3, play.w + 6, play.h + 6}, accent, 7);
  box({744, 176, 274, 503}, 12, {107, 129, 137, 255});
  box({747, 179, 268, 497}, 10, {1, 5, 9, 255});
  if (im.previews[im.active]) {
    SDL_RenderTexture(r, im.previews[im.active], nullptr, &play);
    if (!reduced_motion) {
      SDL_Rect area{int(play.x), int(play.y), int(play.w), int(play.h)};
      SDL_SetRenderClipRect(r, &area);
      float yy = std::fmod(t * 48.f, 650.f) - 100;
      gradient(r, {play.x, play.y + yy, play.w, 48}, {255, 235, 170, 0},
               {255, 235, 170, 19});
      SDL_SetRenderClipRect(r, nullptr);
    }
  } else {
    text("ORIGINAL", 799, 350, 17, {121, 147, 165, 255}, true);
    text("DATA NEEDED", 784, 380, 17, gold, true);
  }
  // Cabinet lamps and physical fasteners frame the playfield, not simulation.
  for (int i = 0; i < 7; ++i) {
    const float yy = 218 + i * 62.f;
    auto lamp = accent;
    lamp.a = Uint8(90 + 70 * (.5f + .5f * std::sin(t * 1.2f + i * .6f)));
    if (reduced_motion)
      lamp.a = 160;
    box({703, yy, 10, 10}, 5, {7, 11, 15, 255});
    box({705, yy + 2, 6, 6}, 3, lamp);
    box({1053, yy, 10, 10}, 5, {7, 11, 15, 255});
    box({1055, yy + 2, 6, 6}, 3, lamp);
  }
  for (auto pt : std::array<SDL_FPoint, 4>{
           {{582, 143}, {1206, 143}, {582, 691}, {1206, 691}}}) {
    box({pt.x - 3, pt.y - 3, 7, 7}, 3, {93, 116, 129, 255});
    line(r, x + pt.x - 2, y + pt.y, x + pt.x + 2, y + pt.y, {16, 29, 39, 255});
  }
  text("PREVIEW", 594, 665, 9, {117, 145, 160, 255}, true);
  text("ORIGINAL DATA", 1073, 665, 9, {117, 145, 160, 255}, true);
  for (int idx : {4, 5, 6}) {
    auto b = regions[idx];
    bool on = selected == idx;
    box({b.x, b.y + 3, b.w, b.h}, 10, {0, 0, 0, 150});
    box(b, 9, on ? SDL_Color{146, 116, 59, 255} : SDL_Color{65, 82, 90, 255});
    box({b.x + 1, b.y + 1, b.w - 2, b.h - 2}, 8,
        on ? SDL_Color{64, 59, 39, 255} : SDL_Color{23, 35, 45, 255});
    text(idx == 4   ? "OPTIONS"
         : idx == 5 ? "QUIT"
                    : "F2  IMPORT ORIGINAL DATA",
         b.x + (idx == 5 ? 25 : 18), b.y + (idx == 5 ? 10 : 15),
         idx == 5 ? 11 : 12, on ? gold : SDL_Color{192, 210, 221, 255}, true);
  }
  line(r, x + 56, y + 735, x + 1224, y + 735, {59, 81, 93, 255});
  source_controls();
  text("ARROWS  SELECT     ENTER  PLAY     O  OPTIONS", 57, 752, 10,
       {162, 182, 194, 255}, true);
  text("IN GAME: F10  MAIN MENU", 989, 752, 10, {162, 182, 194, 255}, true);
  text(fitted(skin, status, 11, 1160), 57, 775, 11, {121, 151, 166, 255});
  SDL_SetRenderScale(r, 1, 1);
}
} // namespace slam
