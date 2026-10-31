#pragma once
#include "frontend/ui_skin.h"
#include "input/gamepad_input.h"
#include "renderer/visual_settings.h"
#include <SDL3/SDL.h>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif
#include <algorithm>
#include <array>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <memory>
#include <nlohmann/json.hpp>
#include <sstream>
#include <string>
#include <vector>

enum class PortAction {
  LeftFlipper,
  RightFlipper,
  Plunger,
  NudgeLeft,
  NudgeRight,
  NudgeUp,
  SpecialLeft,
  SpecialRight
};

// Frontend settings never change simulation coordinates or cadence.
struct PortSettings {
  slam::VisualSettings visual;
#ifdef __EMSCRIPTEN__
  bool fullscreen = false, smooth = false;
#else
  bool fullscreen = true, smooth = false;
#endif
  bool modern_menu = true, reduced_motion = false;
  float zoom = 1.f, dmd_size = 1.f, volume = 1.f;
  int dmd_position = 0, aspect = 0, color = 0;
  int window_width = 1280, window_height = 800, fullscreen_mode = 0;
  float overlay_x = .5f, overlay_y = .05f;
  float music_volume = 1.f, sfx_volume = 1.f;
  int custom_r = 255, custom_g = 160, custom_b = 0;
  std::array<int, 8> keys{{SDL_SCANCODE_LSHIFT, SDL_SCANCODE_RSHIFT,
                           SDL_SCANCODE_RETURN, SDL_SCANCODE_LALT,
                           SDL_SCANCODE_RALT, SDL_SCANCODE_SPACE,
                           SDL_SCANCODE_LCTRL, SDL_SCANCODE_RCTRL}};
  slam::GamepadInput::Bindings gamepad_buttons=slam::GamepadInput::defaults;
  SDL_Scancode key(PortAction action) const {
    return static_cast<SDL_Scancode>(keys[static_cast<std::size_t>(action)]);
  }
};

class PortOptions {
public:
  PortSettings settings;
  std::vector<SDL_Point> exclusive_resolutions;
  bool open = false;
  std::string error;
  bool shaders_available = false;
  bool full_controls = true;
  bool space_specials = false;
  bool nudge_controls = false;
  bool main_menu_available = SDL_getenv("SLAM_FRONTEND_SESSION") != nullptr;
  std::string shader_status = "Original SDL rendering";
  enum Option {
    Fullscreen = 0,
    Zoom = 1,
    DmdPosition = 2,
    DmdSize = 3,
    Filtering = 4,
    Aspect = 5,
    DmdColors = 6,
    Volume = 7,
    WindowSize = 8,
    FullscreenType = 9,
    OverlayX = 10,
    OverlayY = 11,
    CustomRed = 12,
    CustomGreen = 13,
    CustomBlue = 14,
    Music = 15,
    Effects = 16,
    LeftFlipper = 17,
    RightFlipper = 18,
    Plunger = 19,
    NudgeLeft = 20,
    NudgeRight = 21,
    NudgeUp = 22,
    Reset = 23,
    Apply = 24,
    Cancel = 25,
    Preset = 26,
    Quality = 27,
    Strength = 28,
    Bloom = 29,
    Sharpness = 30,
    Saturation = 31,
    Scanlines = 32,
    Mask = 33,
    Curvature = 34,
    Chromatic = 35,
    DmdGlow = 36,
    SpecialLeft = 37,
    SpecialRight = 38,
    MainMenu = 39,
    MenuStyle = 40,
    ReducedMotion = 41,
    PadLeftFlipper = 42, PadRightFlipper, PadPlunger, PadNudgeLeft,
    PadNudgeRight, PadNudgeUp, PadSpecialLeft, PadSpecialRight
  };
  void select_option(Option option) {
    selected_ = option;
    for (int c = 0; c < 6; ++c)
      for (int id : category_rows(c))
        if (id == option)
          category_ = c;
  }
  Option selected_option() const { return static_cast<Option>(selected_); }
  void select_category(int c) {
    category_ = std::clamp(c, 0, 5);
    selected_ = category_rows(category_).front();
    first_row_ = 0;
  }

  void load(bool enable) {
    persistent_ = enable;
    if (!enable)
      return;
    const char *dir = SDL_GetPrefPath("SlamTiltNative", "SlamTilt");
    if (!dir) {
      error = SDL_GetError();
      return;
    }
    path_ = std::filesystem::path(dir) / "options.json";
    try {
      std::ifstream file(path_);
      if (!file)
        return;
      nlohmann::json j;
      file >> j;
      if (j.at("version").get<int>() != 1)
        return;
      PortSettings s;
      s.fullscreen = j.at("fullscreen").get<bool>();
      s.modern_menu = j.value("modern_menu", true);
      s.reduced_motion = j.value("reduced_motion", false);
      s.gamepad_buttons=j.value("gamepad_buttons",slam::GamepadInput::defaults);
      s.smooth = j.at("smooth").get<bool>();
      s.zoom = j.at("zoom").get<float>();
      s.dmd_size = j.at("dmd_size").get<float>();
      s.volume = j.at("volume").get<float>();
      s.dmd_position = j.at("dmd_position").get<int>();
      s.aspect = j.at("aspect").get<int>();
      s.color = j.at("color").get<int>();
      s.window_width = j.value("window_width", 1280);
      s.window_height = j.value("window_height", 800);
      s.fullscreen_mode = j.value("fullscreen_mode", 0);
      s.overlay_x = j.value("overlay_x", .5f);
      s.overlay_y = j.value("overlay_y", .05f);
      s.music_volume = j.value("music_volume", 1.f);
      s.sfx_volume = j.value("sfx_volume", 1.f);
      s.custom_r = j.value("custom_r", 255);
      s.custom_g = j.value("custom_g", 160);
      s.custom_b = j.value("custom_b", 0);
      if (j.contains("visual"))
        s.visual = j.at("visual").get<slam::VisualSettings>();
      if (j.contains("keys")) {
        const auto keys = j.at("keys").get<std::vector<int>>();
        if (keys.size() < 6 || keys.size() > s.keys.size())
          throw std::runtime_error("invalid controls");
        std::copy(keys.begin(), keys.end(), s.keys.begin());
        for (std::size_t i = keys.size(); i < s.keys.size(); ++i) {
          if (std::find(s.keys.begin(), s.keys.begin() + i, s.keys[i]) ==
              s.keys.begin() + i)
            continue;
          for (int fallback = SDL_SCANCODE_A; fallback < SDL_SCANCODE_COUNT;
               ++fallback)
            if (allowed_key(fallback) &&
                std::find(s.keys.begin(), s.keys.begin() + i, fallback) ==
                    s.keys.begin() + i) {
              s.keys[i] = fallback;
              break;
            }
        }
      }
      if (!valid(s))
        throw std::runtime_error("invalid settings");
#ifdef __EMSCRIPTEN__
      s.fullscreen = false;
      s.fullscreen_mode = 0;
#endif
      settings = s;
    } catch (...) {
      settings = PortSettings{};
    }
  }

  void suspend_interaction() {
    dragging_ = -1;
    preview_ = false;
  }
  bool contains_point(float px, float py) const {
    px /= draw_scale_;
    py /= draw_scale_;
    return open && px >= x_ && px <= x_ + width_ && py >= y_ &&
           py <= y_ + height_;
  }
  bool gamepad_binding() const {return open && binding_>=8;}
  bool handle(const SDL_Event &event) {
    if(gamepad_binding()) {
      if(event.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN) {
        const int button=event.gbutton.button;
        if(button==SDL_GAMEPAD_BUTTON_START || button==SDL_GAMEPAD_BUTTON_BACK)binding_=-1;
        else if(button>=0 && button<SDL_GAMEPAD_BUTTON_COUNT) {
          const int action=binding_-8;
          const int previous=settings.gamepad_buttons[action];
          for(auto& current:settings.gamepad_buttons)if(current==button)current=previous;
          settings.gamepad_buttons[action]=button;binding_=-1;error.clear();
        }
        return true;
      }
      if(event.type==SDL_EVENT_KEY_DOWN){if(event.key.key==SDLK_ESCAPE)binding_=-1;return true;}
      if(event.type==SDL_EVENT_KEY_UP || event.type==SDL_EVENT_GAMEPAD_BUTTON_UP || event.type==SDL_EVENT_GAMEPAD_AXIS_MOTION)return true;
    }
    if (main_menu_available && event.type == SDL_EVENT_KEY_DOWN &&
        !event.key.repeat && event.key.key == SDLK_F10) {
      return_to_menu();
      return true;
    }
    if (open && binding_ >= 0 && event.type == SDL_EVENT_KEY_DOWN &&
        !event.key.repeat) {
      if (event.key.key == SDLK_ESCAPE) {
        binding_ = -1;
        error.clear();
        return true;
      }
      int code = event.key.scancode;
      if (!allowed_key(code) ||
          std::find(settings.keys.begin(), settings.keys.end(), code) !=
              settings.keys.end())
        error = "Reserved or already assigned key";
      else {
        settings.keys[binding_] = code;
        binding_ = -1;
        error.clear();
      }
      return true;
    }
    if (event.type == SDL_EVENT_KEY_DOWN && !event.key.repeat &&
        event.key.key == SDLK_ESCAPE) {
      if (open)
        cancel();
      else {
        saved_ = settings;
        open = true;
        error.clear();
      }
      return true;
    }
    if (!open)
      return false;
    if ((event.type == SDL_EVENT_KEY_DOWN || event.type == SDL_EVENT_KEY_UP) &&
        event.key.key == SDLK_V) {
      preview_ = event.type == SDL_EVENT_KEY_DOWN;
      return true;
    }
    if (event.type == SDL_EVENT_KEY_DOWN && !event.key.repeat) {
      switch (event.key.key) {
      case SDLK_PAGEUP:
        select_category((category_+5)%6);break;
      case SDLK_PAGEDOWN:
        select_category((category_+1)%6);break;
      case SDLK_TAB:
        select_category(
            (category_ + ((event.key.mod & SDL_KMOD_SHIFT) ? 5 : 1)) % 6);
        break;
      case SDLK_UP:
        navigate(-1);
        break;
      case SDLK_DOWN:
        navigate(1);
        break;
      case SDLK_LEFT:
        adjust(-1);
        break;
      case SDLK_RIGHT:
        adjust(1);
        break;
      case SDLK_RETURN:
      case SDLK_SPACE:
        activate();
        break;
      case SDLK_BACKSPACE:
        cancel();
        break;
      default:
        break;
      }
    } else if (event.type == SDL_EVENT_MOUSE_WHEEL) {
      navigate(event.wheel.y > 0 ? -1 : 1);
    } else if (event.type == SDL_EVENT_MOUSE_BUTTON_DOWN &&
               event.button.button == SDL_BUTTON_LEFT) {
      const float px = event.button.x / draw_scale_,
                  py = event.button.y / draw_scale_;
      for (const auto &hit : hits_)
        if (px >= hit.rect.x && px <= hit.rect.x + hit.rect.w &&
            py >= hit.rect.y && py <= hit.rect.y + hit.rect.h) {
          if (hit.id < 0) {
            select_category(-hit.id - 1);
            break;
          }
          selected_ = hit.id;
          if (slider(selected_)) {
            if (py >= hit.rect.y + 25) {
              dragging_ = selected_;
              set_slider(px, hit.rect);
            }
          } else
            activate();
          break;
        }
    } else if (event.type == SDL_EVENT_MOUSE_MOTION) {
      const float px = event.motion.x / draw_scale_,
                  py = event.motion.y / draw_scale_;
      hover_ = -100;
      for (const auto &hit : hits_) {
        if (dragging_ == hit.id) {
          selected_ = dragging_;
          set_slider(px, hit.rect);
        }
        if (px >= hit.rect.x && px <= hit.rect.x + hit.rect.w &&
            py >= hit.rect.y && py <= hit.rect.y + hit.rect.h)
          hover_ = hit.id;
      }
    } else if (event.type == SDL_EVENT_MOUSE_BUTTON_UP)
      dragging_ = -1;
    return event.type != SDL_EVENT_QUIT &&
           event.type != SDL_EVENT_WINDOW_CLOSE_REQUESTED &&
           event.type != SDL_EVENT_WINDOW_RESIZED &&
           event.type != SDL_EVENT_WINDOW_PIXEL_SIZE_CHANGED;
  }

  void draw(SDL_Renderer *renderer, int w, int h) {
    if (!open || preview_)
      return;
    if (!skin_)
      skin_ = std::make_shared<slam::UiSkin>();
    auto &skin = *skin_;
    draw_scale_ = std::clamp(std::min(w / 1120.f, h / 800.f), .55f, 1.8f);
    SDL_SetRenderScale(renderer, draw_scale_, draw_scale_);
    const float sw = w / draw_scale_, sh = h / draw_scale_;
    width_ = std::min(1020.f, sw - 24);
    height_ = std::min(704.f, sh - 24);
    x_ = (sw - width_) / 2;
    y_ = (sh - height_) / 2;
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(renderer, 3, 6, 12, 175);
    SDL_FRect dim{0, 0, sw, sh};
    SDL_RenderFillRect(renderer, &dim);
    const auto box = [&](SDL_FRect rect, float radius, SDL_Color color) {
      slam::UiSkin::round_rect(renderer, rect, radius, color);
    };
    box({x_ + 5, y_ + 10, width_, height_}, 20, {0, 0, 0, 130});
    box({x_ - 2, y_ - 2, width_ + 4, height_ + 4}, 20, {123, 135, 139, 255});
    box({x_ - 1, y_ - 1, width_ + 2, height_ + 2}, 20, {61, 83, 96, 255});
    box({x_, y_, width_, height_}, 19, {21, 22, 15, 252});
    for (int stripe = 20; stripe < int(height_) - 20; stripe += 4) {
      SDL_SetRenderDrawColor(renderer, 153, 180, 194, 5);
      SDL_RenderLine(renderer, x_ + 10, y_ + stripe, x_ + width_ - 10,
                     y_ + stripe);
    }
    box({x_ + 17, y_ + 18, width_ - 34, 66}, 11, {43, 44, 28, 255});
    SDL_SetRenderDrawColor(renderer, 203, 222, 226, 80);
    SDL_RenderLine(renderer, x_ + 29, y_ + 19, x_ + width_ - 29, y_ + 19);
    SDL_SetRenderDrawColor(renderer, 196, 139, 57, 130);
    SDL_RenderLine(renderer, x_ + 24, y_ + 89, x_ + width_ - 24, y_ + 89);
    for (auto screw :
         std::array<SDL_FPoint, 4>{{{x_ + 12, y_ + 12},
                                    {x_ + width_ - 12, y_ + 12},
                                    {x_ + 12, y_ + height_ - 12},
                                    {x_ + width_ - 12, y_ + height_ - 12}}}) {
      box({screw.x - 3, screw.y - 3, 6, 6}, 3, {124, 144, 153, 255});
      SDL_SetRenderDrawColor(renderer, 28, 43, 53, 255);
      SDL_RenderLine(renderer, screw.x - 2, screw.y, screw.x + 2, screw.y);
    }
    box({x_ + 24, y_ + 25, 4, 43}, 2, {210, 228, 65, 255});
    skin.text(renderer, "SLAMTILT - REBORN", x_ + 44, y_ + 22,
              width_ < 680 ? 22 : 28, {245, 246, 250, 255}, true);
    skin.text(renderer, "OPTIONS", x_ + 46,
              y_ + 61, width_ < 680 ? 9 : 11, {148, 162, 184, 255});
    if (width_ > 750)
      skin.text(renderer, "Hold V to preview the table", x_ + width_ - 240,
                y_ + 73, 11, {142, 164, 186, 255});
    const float sidebar = width_ < 680 ? 120.f : 196.f;
    const float content_x = x_ + sidebar + 24,
                content_w = width_ - sidebar - 48;
    const float top = y_ + 110, bottom = y_ + height_ - 134;
    const char *categories[] = {"Display", "Visual Effects", "DMD",
                                "Audio",   "Controls",       "General"};
    hits_.clear();
    for (int c = 0; c < 6; ++c) {
      SDL_FRect tab{x_ + 14, top + c * 54, sidebar - 18, 44};
      if (category_ == c || hover_ == -c - 1)
        box(tab, 9,
            category_ == c ? SDL_Color{65, 69, 27, 255}
                           : SDL_Color{25, 38, 50, 255});
      if (category_ == c)
        box({tab.x, tab.y + 11, 3, 22}, 1, {210, 228, 65, 255});
      skin.text(renderer, categories[c], tab.x + 12, tab.y + 10,
                width_ < 680 ? 13 : 17,
                category_ == c ? SDL_Color{228, 240, 109, 255}
                               : SDL_Color{158, 174, 196, 255},
                category_ == c);
      hits_.push_back({tab, -c - 1});
    }
    skin.text(renderer, categories[category_], content_x, y_ + 87, 19,
              {238, 242, 249, 255}, true);
    if (last_draw_selection_ != selected_) {
      last_draw_selection_ = selected_;
      selection_started_ = SDL_GetTicks();
    }
    const float selection_phase =
        settings.reduced_motion
            ? 1.f
            : std::min(1.f, (SDL_GetTicks() - selection_started_) / 120.f);
    auto rows = category_rows(category_);
    visible_rows_ = std::max(1, int((bottom - top) / 52));
    auto it = std::find(rows.begin(), rows.end(), selected_);
    int index = it == rows.end() ? 0 : int(it - rows.begin());
    if (index < first_row_)
      first_row_ = index;
    if (index >= first_row_ + visible_rows_)
      first_row_ = index - visible_rows_ + 1;
    first_row_ = std::clamp(first_row_, 0,
                            std::max(0, int(rows.size()) - visible_rows_));
    for (int i = first_row_;
         i < int(rows.size()) && i < first_row_ + visible_rows_; ++i) {
      const int id = rows[i];
      const float yy = top + (i - first_row_) * 52;
      SDL_FRect row{content_x, yy, content_w, 47};
      const bool selected = selected_ == id;
      box(row, 8,
          selected       ? SDL_Color{80, 74, 54, 255}
          : hover_ == id ? SDL_Color{64, 65, 38, 255}
                         : SDL_Color{61, 61, 43, 255});
      box({row.x + 1, row.y + 1, row.w - 2, row.h - 2}, 7,
          selected ? SDL_Color{38, 40, 36, 255} : SDL_Color{24, 25, 18, 255});
      SDL_SetRenderDrawColor(renderer, 127, 153, 167, selected ? 90 : 35);
      SDL_RenderLine(renderer, row.x + 9, row.y + 1, row.x + row.w - 9,
                     row.y + 1);
      if (selected)
        box({row.x, row.y + 14 - 5 * selection_phase, 3,
             19 + 10 * selection_phase},
            1, {210, 228, 65, 255});
      const auto text = row_text(id);
      const auto split = text.find(": ");
      const auto label =
          split == std::string::npos ? text : text.substr(0, split);
      const auto value =
          split == std::string::npos ? "" : text.substr(split + 2);
      const float font = width_ < 680 ? 12.f : 15.f;
      skin.text(renderer, label, row.x + 13, row.y + 7, font,
                {207, 218, 234, 255}, selected);
      if (id == 0) {
        const SDL_FRect toggle{row.x + row.w - 91, row.y + 8, 77, 28};
        box(toggle, 14,
            fullscreen_shown() ? SDL_Color{86, 99, 32, 255}
                                : SDL_Color{57, 66, 81, 255});
        box({toggle.x + (fullscreen_shown() ? 51.f : 5.f), toggle.y + 5, 18,
             18},
            9,
            fullscreen_shown() ? SDL_Color{137, 239, 208, 255}
                                : SDL_Color{170, 182, 199, 255});
        skin.text(renderer, fullscreen_shown() ? "ON" : "OFF",
                  toggle.x + (fullscreen_shown() ? 11.f : 30.f), toggle.y + 5,
                  12, {225, 239, 237, 255}, true);
      } else
        skin.text(renderer, value,
                  row.x + row.w - 15 - skin.width(value, font, true), row.y + 7,
                  font, {228, 240, 109, 255}, true);
      if (slider(id)) {
        const auto range = slider_range(id);
        float t = std::clamp((current_slider(id) - range.first) /
                                 (range.second - range.first),
                             0.f, 1.f);
        box({row.x + 14, row.y + 34, row.w - 28, 3}, 1, {58, 71, 89, 255});
        box({row.x + 14, row.y + 34, (row.w - 28) * t, 3}, 1,
            {191, 212, 62, 255});
        box({row.x + 10 + (row.w - 28) * t, row.y + 31, 9, 9}, 4,
            {219, 248, 240, 255});
      }
      hits_.push_back({row, id});
    }
    if (int(rows.size()) > visible_rows_) {
      const float track = bottom - top;
      box({content_x + content_w + 8, top, 3, track}, 1, {35, 46, 61, 255});
      box({content_x + content_w + 8, top + track * first_row_ / rows.size(), 3,
           track * visible_rows_ / rows.size()},
          1, {116, 143, 169, 255});
    }
    std::string help =
        binding_ >= 8 ? "Press a pad button. Start / Back cancels."
        : binding_ >= 0    ? "Press a new key. Escape cancels binding."
        : !error.empty() ? error
        : category_ == 1
            ? (shaders_available
                   ? "Live preview. Effects never change physics or timing."
                   : "GPU shaders unavailable. Classic filtering remains "
                     "available.")
        : category_ == 2
            ? "Overlay position can also be changed by dragging the DMD."
        : category_ == 4
            ? "Select a key or pad binding. Pad: D-pad / A / B; LB / RB tabs."
        : category_ == 5
            ? "Reborn and Original share your tables, controls and saved games."
            : "Preview changes now. Apply to save, or Cancel to restore.";
    if (error.empty() && binding_ < 0 && settings.visual.preset == 0 &&
        (category_ == 1 || category_ == 2))
      help = "Original bypasses all effects, including DMD glow.";
    const float help_font = width_ < 680 ? 11.f : 13.f;
    if (skin.width(help, help_font) > content_w) {
      while (!help.empty() && skin.width(help + "...", help_font) > content_w)
        help.pop_back();
      help += "...";
    }
    skin.text(renderer, help, content_x, y_ + height_ - 118,
              width_ < 680 ? 11 : 13,
              !error.empty() ? SDL_Color{255, 140, 117, 255}
                             : SDL_Color{142, 164, 186, 255});
    const int button_count = main_menu_available ? 4 : 3;
    const float button_w = (content_w - 8 * (button_count - 1)) / button_count;
    const char *actions[] = {"Reset Defaults", "Apply", "Cancel", "Main Menu"};
    for (int i = 0; i < button_count; ++i) {
      const int id = i == 3 ? 39 : 23 + i;
      SDL_FRect button{content_x + i * (button_w + 8), y_ + height_ - 79,
                       button_w, 39};
      const bool lit = selected_ == id || hover_ == id || i == 1;
      // Raised, inset switches echo the original yellow-green menu bars.
      box(button, 12, {8, 10, 5, 255});
      box({button.x + 2, button.y + 2, button.w - 4, button.h - 5}, 10,
          lit ? SDL_Color{114, 122, 32, 255} : SDL_Color{57, 60, 31, 255});
      box({button.x + 4, button.y + 5, button.w - 8, button.h - 11}, 8,
          lit ? SDL_Color{59, 66, 18, 255} : SDL_Color{28, 32, 16, 255});
      SDL_SetRenderDrawColor(renderer, lit ? 222 : 121, lit ? 235 : 132, 65, 255);
      SDL_RenderLine(renderer, button.x + 12, button.y + 4,
                     button.x + button.w - 12, button.y + 4);
      SDL_RenderLine(renderer, button.x + 12, button.y + button.h - 7,
                     button.x + button.w - 12, button.y + button.h - 7);
      const float font = width_ < 680 ? 11.f : 14.f;
      skin.text(renderer, actions[i],
                button.x + (button.w - skin.width(actions[i], font, true)) / 2,
                button.y + 9, font,
                lit ? SDL_Color{237, 244, 144, 255}
                    : SDL_Color{189, 197, 145, 255},
                true);
      hits_.push_back({button, id});
    }
    skin.text(
        renderer,
        SDL_HasGamepad()?"PAD: LB/RB tabs   D-PAD adjust   A select   B cancel":"TAB  category     ARROWS  adjust     ENTER  select     ESC  cancel",
        x_ + 24, y_ + height_ - 25, width_ < 680 ? 9 : 11,
        {119, 139, 162, 255});
    SDL_SetRenderScale(renderer, 1, 1);
  }

private:
  struct Hit {
    SDL_FRect rect;
    int id;
  };
  std::vector<Hit> hits_;
  std::shared_ptr<slam::UiSkin> skin_;
  int category_ = 0, hover_ = -100, dragging_ = -1;
  bool preview_ = false;
  int last_draw_selection_ = -100;
  Uint64 selection_started_ = 0;
  float height_ = 600;
  std::vector<int> category_rows(int c) const {
    switch (c) {
    case 0:
      return {0, 8, 9, 1, 5, 4};
    case 1:
      return {26, 27, 28, 29, 30, 31, 32, 33, 34, 35};
    case 2:
      return {2, 3, 6, 36, 10, 11, 12, 13, 14};
    case 3:
      return {7, 15, 16};
    case 5:
      return {40, 41};
    default:
      std::vector<int> rows=space_specials?std::vector<int>{17,18,19,20,21,22,37,38}:
          full_controls?std::vector<int>{17,18,19,20,21,22,37}:
          nudge_controls?std::vector<int>{17,18,19,20,21,22}:std::vector<int>{17,18,19};
      const auto keyboard_rows=rows;
      for(int id:keyboard_rows)rows.push_back(id==37?48:id==38?49:42+id-17);
      return rows;
    }
  }
  void navigate(int direction) {
    auto rows = category_rows(category_);
    rows.insert(rows.end(), {23, 24, 25});
    if (main_menu_available)
      rows.push_back(39);
    auto it = std::find(rows.begin(), rows.end(), selected_);
    int index = it == rows.end() ? 0 : int(it - rows.begin());
    selected_ = rows[(index + int(rows.size()) + direction) % rows.size()];
  }
  static bool slider(int id) {
    return id == 1 || id == 3 || id == 7 || (id >= 10 && id <= 16) ||
           (id >= 28 && id <= 36);
  }
  static std::pair<float, float> slider_range(int id) {
    if (id == 1)
      return {.75f, 2};
    if (id == 3)
      return {.5f, 2};
    if (id >= 12 && id <= 14)
      return {0, 255};
    if (id == 31 || id == 35)
      return {0, 2};
    if (id == 34)
      return {0, .3f};
    return {0, 1};
  }
  float current_slider(int id) {
    if (id == 12)
      return float(settings.custom_r);
    if (id == 13)
      return float(settings.custom_g);
    if (id == 14)
      return float(settings.custom_b);
    return slider_value(id);
  }
  float &slider_value(int id) {
    switch (id) {
    case 1:
      return settings.zoom;
    case 3:
      return settings.dmd_size;
    case 7:
      return settings.volume;
    case 10:
      return settings.overlay_x;
    case 11:
      return settings.overlay_y;
    case 15:
      return settings.music_volume;
    case 16:
      return settings.sfx_volume;
    case 28:
      return settings.visual.strength;
    case 29:
      return settings.visual.bloom;
    case 30:
      return settings.visual.sharpness;
    case 31:
      return settings.visual.saturation;
    case 32:
      return settings.visual.scanlines;
    case 33:
      return settings.visual.mask;
    case 34:
      return settings.visual.curvature;
    case 35:
      return settings.visual.chromatic;
    default:
      return settings.visual.dmd_glow;
    }
  }
  void set_slider(float x, SDL_FRect rect) {
    const auto range = slider_range(selected_);
    float value =
        range.first + std::clamp((x - rect.x - 14) / (rect.w - 28), 0.f, 1.f) *
                          (range.second - range.first);
    if (selected_ >= 12 && selected_ <= 14) {
      int *rgb[] = {&settings.custom_r, &settings.custom_g, &settings.custom_b};
      *rgb[selected_ - 12] = int(std::lround(value));
    } else
      slider_value(selected_) = value;
    if (selected_ >= 28 && selected_ <= 35)
      settings.visual.preset = 6;
  }
  bool fullscreen_shown() const {
#ifdef __EMSCRIPTEN__
    return EM_ASM_INT({return !!document.fullscreenElement;});
#else
    return settings.fullscreen;
#endif
  }
  std::string row_text(int id) const {
    if(id>=42 && id<=49) {
      const char* actions[]={"Left flipper","Right flipper","Plunger","Nudge left","Nudge right","Nudge up","Left special","Right special"};
      const auto button=SDL_GamepadButton(settings.gamepad_buttons[id-42]);
      const char* name=SDL_GetGamepadStringForButton(button);
      return std::string("Pad ")+actions[id-42]+": "+(name?name:"unassigned");
    }
    const char *positions[] = {"Top", "Left", "Right", "Overlay"};
    const char *aspects[] = {"Fit", "Stretch", "Crop"};
    const char *colors[] = {"Original", "Amber", "White", "Custom"};
    switch (id) {
    case 0:
#ifdef __EMSCRIPTEN__
      return "Browser fullscreen";
#else
      return std::string("Fullscreen: ") + (settings.fullscreen ? "On" : "Off");
#endif
    case 1:
      return "Zoom: " + percent(settings.zoom);
    case 2:
      return std::string("Position: ") + positions[settings.dmd_position];
    case 3:
      return "Size: " + percent(settings.dmd_size);
    case 4:
      return std::string("Filtering: ") +
             (settings.smooth ? "Smooth" : "Pixels");
    case 5:
      return std::string("Aspect ratio: ") + aspects[settings.aspect];
    case 6:
      return std::string("Colors: ") + colors[settings.color];
    case 7:
      return "Master volume: " + percent(settings.volume);
    case 8:
      return "Resolution: " + std::to_string(settings.window_width) + " x " +
             std::to_string(settings.window_height);
    case 9:
      return std::string("Fullscreen mode: ") +
             (settings.fullscreen_mode ? "Exclusive" : "Desktop");
    case 10:
      return "Overlay X: " + percent(settings.overlay_x);
    case 11:
      return "Overlay Y: " + percent(settings.overlay_y);
    case 12:
      return "Custom red: " + std::to_string(settings.custom_r);
    case 13:
      return "Custom green: " + std::to_string(settings.custom_g);
    case 14:
      return "Custom blue: " + std::to_string(settings.custom_b);
    case 15:
      return "Music: " + percent(settings.music_volume);
    case 16:
      return "Sound effects: " + percent(settings.sfx_volume);
    case 26:
      return std::string("Preset: ") +
             slam::visual_preset_name(settings.visual.preset);
    case 27:
      return std::string("Quality: ") + (settings.visual.quality == 0 ? "Low"
                                         : settings.visual.quality == 1
                                             ? "Balanced"
                                             : "High");
    case 40:
      return std::string("Main menu: ") +
             (settings.modern_menu ? "Reborn" : "Original");
    case 41:
      return std::string("Reduced motion: ") +
             (settings.reduced_motion ? "On" : "Off");
    case 38:
      return "Right special: " +
             key_name(static_cast<std::size_t>(PortAction::SpecialRight));
    case 37:
      return "Left special: " +
             key_name(static_cast<std::size_t>(PortAction::SpecialLeft));
    default:
      break;
    }
    if (id >= 17 && id <= 22) {
      const char *labels[] = {"Left flipper", "Right flipper", "Plunger",
                              "Nudge left",   "Nudge right",   "Nudge up"};
      return std::string(labels[id - 17]) + ": " + key_name(id - 17);
    }
    const char *labels[] = {"Strength",   "Bloom",        "Sharpness",
                            "Saturation", "Scanlines",    "CRT mask",
                            "Curvature",  "Color fringe", "DMD glow"};
    const float values[] = {
        settings.visual.strength,  settings.visual.bloom,
        settings.visual.sharpness, settings.visual.saturation,
        settings.visual.scanlines, settings.visual.mask,
        settings.visual.curvature, settings.visual.chromatic,
        settings.visual.dmd_glow};
    return id >= 28 && id <= 36
               ? std::string(labels[id - 28]) + ": " + percent(values[id - 28])
               : "";
  }
  static constexpr int binding_start_ = 17;
  static constexpr int action_start_ = 23;
  int binding_ = -1;
  int selected_ = 0, first_row_ = 0, visible_rows_ = 12;
  bool persistent_ = false;
  PortSettings saved_;
  std::filesystem::path path_;
  float x_ = 0, y_ = 0, width_ = 440, draw_scale_ = 1;
  static bool allowed_key(int code) {
    if (code <= SDL_SCANCODE_UNKNOWN || code >= SDL_SCANCODE_COUNT)
      return false;
    switch (code) {
    case SDL_SCANCODE_ESCAPE:
    case SDL_SCANCODE_P:
    case SDL_SCANCODE_R:
    case SDL_SCANCODE_M:
    case SDL_SCANCODE_C:
    case SDL_SCANCODE_HOME:
    case SDL_SCANCODE_END:
    case SDL_SCANCODE_UP:
    case SDL_SCANCODE_DOWN:
    case SDL_SCANCODE_LEFT:
    case SDL_SCANCODE_RIGHT:
      return false;
    default:
      return true;
    }
  }
  static bool valid(const PortSettings &s) {
    for(unsigned i=0;i<s.gamepad_buttons.size();++i) {
      const int b=s.gamepad_buttons[i];
      if(b<0 || b>=SDL_GAMEPAD_BUTTON_COUNT || b==SDL_GAMEPAD_BUTTON_START || b==SDL_GAMEPAD_BUTTON_BACK)return false;
      for(unsigned j=0;j<i;++j)if(s.gamepad_buttons[j]==b)return false;
    }
    for (std::size_t i = 0; i < s.keys.size(); ++i) {
      if (!allowed_key(s.keys[i]))
        return false;
      for (std::size_t j = 0; j < i; ++j)
        if (s.keys[j] == s.keys[i])
          return false;
    }
    return slam::valid_visual(s.visual) && std::isfinite(s.zoom) &&
           s.zoom >= .75f && s.zoom <= 2.f && std::isfinite(s.dmd_size) &&
           s.dmd_size >= .5f && s.dmd_size <= 2.f && std::isfinite(s.volume) &&
           s.volume >= 0 && s.volume <= 1 && s.dmd_position >= 0 &&
           s.dmd_position <= 3 && s.aspect >= 0 && s.aspect <= 2 &&
           s.color >= 0 && s.color <= 3 && s.window_width >= 320 &&
           s.window_width <= 7680 && s.window_height >= 240 &&
           s.window_height <= 4320 && s.fullscreen_mode >= 0 &&
           s.fullscreen_mode <= 1 && std::isfinite(s.overlay_x) &&
           s.overlay_x >= 0 && s.overlay_x <= 1 && std::isfinite(s.overlay_y) &&
           s.overlay_y >= 0 && s.overlay_y <= 1 &&
           std::isfinite(s.music_volume) && s.music_volume >= 0 &&
           s.music_volume <= 1 && std::isfinite(s.sfx_volume) &&
           s.sfx_volume >= 0 && s.sfx_volume <= 1 && s.custom_r >= 0 &&
           s.custom_r <= 255 && s.custom_g >= 0 && s.custom_g <= 255 &&
           s.custom_b >= 0 && s.custom_b <= 255;
  }
  static std::string percent(float value) {
    return std::to_string(static_cast<int>(std::lround(value * 100))) + "%";
  }
  std::string key_name(std::size_t index) const {
    const char *name =
        SDL_GetScancodeName(static_cast<SDL_Scancode>(settings.keys[index]));
    return name && *name ? name : std::to_string(settings.keys[index]);
  }
  void cancel() {
    preview_ = false;
    dragging_ = -1;
    binding_ = -1;
    settings = saved_;
    open = false;
    error.clear();
  }
  void return_to_menu() {
    if (open)
      cancel();
    SDL_Event event{};
    event.type = SDL_EVENT_QUIT;
    SDL_PushEvent(&event);
  }
  void activate() {
    if(selected_>=42 && selected_<=49){binding_=8+selected_-42;error.clear();return;}
    if (main_menu_available && selected_ == 39) {
      return_to_menu();
      return;
    }
    if (selected_ == SpecialRight) {
      binding_ = static_cast<int>(PortAction::SpecialRight);
      error.clear();
      return;
    }
    if (selected_ == SpecialLeft) {
      binding_ = static_cast<int>(PortAction::SpecialLeft);
      error.clear();
      return;
    }
    if (selected_ >= binding_start_ && selected_ < action_start_) {
      binding_ = selected_ - binding_start_;
      error.clear();
      return;
    }
    if (selected_ == action_start_)
      settings = PortSettings{};
    else if (selected_ == action_start_ + 1)
      apply();
    else if (selected_ == action_start_ + 2)
      cancel();
    else
      adjust(1);
  }
  void adjust(int direction) {
    if (selected_ >= 28 && selected_ <= 36) {
      auto range = slider_range(selected_);
      auto &value = slider_value(selected_);
      value =
          std::clamp(value + direction * (range.second - range.first) * .05f,
                     range.first, range.second);
      if (selected_ != 36)
        settings.visual.preset = 6;
      return;
    }
    switch (selected_) {
    case 0:
#ifdef __EMSCRIPTEN__
      EM_ASM({window.rebornFullscreen();});
#else
      settings.fullscreen = !settings.fullscreen;
#endif
      break;
    case 1:
      settings.zoom = std::clamp(settings.zoom + direction * .05f, .75f, 2.f);
      break;
    case 2:
      settings.dmd_position = (settings.dmd_position + direction + 4) % 4;
      break;
    case 3:
      settings.dmd_size =
          std::clamp(settings.dmd_size + direction * .05f, .5f, 2.f);
      break;
    case 4:
      settings.smooth = !settings.smooth;
      break;
    case 5:
      settings.aspect = (settings.aspect + direction + 3) % 3;
      break;
    case 6:
      settings.color = (settings.color + direction + 4) % 4;
      break;
    case 7:
      settings.volume =
          std::clamp(settings.volume + direction * .05f, 0.f, 1.f);
      break;
    case 8: {
      if (settings.fullscreen_mode == 1 && !exclusive_resolutions.empty()) {
        std::size_t index = 0;
        for (std::size_t i = 0; i < exclusive_resolutions.size(); ++i)
          if (exclusive_resolutions[i].x == settings.window_width &&
              exclusive_resolutions[i].y == settings.window_height)
            index = i;
        index = (index + exclusive_resolutions.size() + direction) %
                exclusive_resolutions.size();
        settings.window_width = exclusive_resolutions[index].x;
        settings.window_height = exclusive_resolutions[index].y;
        break;
      }
      const int widths[] = {1280, 1366, 1920}, heights[] = {800, 768, 1080};
      int index = settings.window_width == 1366   ? 1
                  : settings.window_width == 1920 ? 2
                                                  : 0;
      index = (index + direction + 3) % 3;
      settings.window_width = widths[index];
      settings.window_height = heights[index];
      break;
    }
    case 9:
      settings.fullscreen_mode = 1 - settings.fullscreen_mode;
      if (settings.fullscreen_mode == 1 && !exclusive_resolutions.empty()) {
        const auto match =
            std::find_if(exclusive_resolutions.begin(),
                         exclusive_resolutions.end(), [&](SDL_Point p) {
                           return p.x == settings.window_width &&
                                  p.y == settings.window_height;
                         });
        if (match == exclusive_resolutions.end()) {
          settings.window_width = exclusive_resolutions.front().x;
          settings.window_height = exclusive_resolutions.front().y;
        }
      }
      break;
    case 10:
      settings.overlay_x =
          std::clamp(settings.overlay_x + direction * .05f, 0.f, 1.f);
      break;
    case 11:
      settings.overlay_y =
          std::clamp(settings.overlay_y + direction * .05f, 0.f, 1.f);
      break;
    case 12:
      settings.custom_r = std::clamp(settings.custom_r + direction * 5, 0, 255);
      break;
    case 13:
      settings.custom_g = std::clamp(settings.custom_g + direction * 5, 0, 255);
      break;
    case 14:
      settings.custom_b = std::clamp(settings.custom_b + direction * 5, 0, 255);
      break;
    case 15:
      settings.music_volume =
          std::clamp(settings.music_volume + direction * .05f, 0.f, 1.f);
      break;
    case 16:
      settings.sfx_volume =
          std::clamp(settings.sfx_volume + direction * .05f, 0.f, 1.f);
      break;
    case 23:
      settings = PortSettings{};
      break;
    case 40:
      settings.modern_menu = !settings.modern_menu;
      break;
    case 41:
      settings.reduced_motion = !settings.reduced_motion;
      break;
    case 26:
      slam::visual_preset(settings.visual,
                          settings.visual.preset == 6
                              ? (direction > 0 ? 0 : 5)
                              : (settings.visual.preset + direction + 6) % 6);
      break;
    case 27:
      settings.visual.quality = (settings.visual.quality + direction + 3) % 3;
      break;
    default:
      break;
    }
  }
  void apply() {
    if (persistent_ && !path_.empty()) {
      try {
        nlohmann::json j = {{"version", 1},
                            {"visual", settings.visual},
                            {"fullscreen", settings.fullscreen},
                            {"smooth", settings.smooth},
                            {"modern_menu", settings.modern_menu},
                            {"reduced_motion", settings.reduced_motion},
                            {"zoom", settings.zoom},
                            {"dmd_size", settings.dmd_size},
                            {"volume", settings.volume},
                            {"dmd_position", settings.dmd_position},
                            {"aspect", settings.aspect},
                            {"color", settings.color},
                            {"window_width", settings.window_width},
                            {"window_height", settings.window_height},
                            {"fullscreen_mode", settings.fullscreen_mode},
                            {"overlay_x", settings.overlay_x},
                            {"overlay_y", settings.overlay_y},
                            {"music_volume", settings.music_volume},
                            {"sfx_volume", settings.sfx_volume},
                            {"custom_r", settings.custom_r},
                            {"custom_g", settings.custom_g},
                            {"custom_b", settings.custom_b},
                            {"keys", settings.keys},
                            {"gamepad_buttons",settings.gamepad_buttons}};
        const auto temporary = path_.string() + ".tmp";
        std::ofstream file(temporary, std::ios::trunc);
        file << j.dump(2) << '\n';
        file.close();
        if (!file)
          throw std::runtime_error("settings write failed");
        if (!SDL_RenamePath(temporary.c_str(), path_.string().c_str()))
          throw std::runtime_error(SDL_GetError());
      } catch (const std::exception &e) {
        error = e.what();
        return;
      }
    }
    saved_ = settings;
    error.clear();
    open = false;
  }
};
