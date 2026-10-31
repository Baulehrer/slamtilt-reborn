#pragma once
#include <SDL3/SDL.h>
#include <algorithm>
#include <array>
#include <cstdlib>
#include <deque>
#include <map>

namespace slam {
#ifdef SLAM_GAMEPAD_FRONTEND_PROBE
void gamepad_frontend_probe_ready();
#endif
// SDL gamepads feed the same actions as the configured keyboard. Physics stays
// digital.
class GamepadInput {
public:
  using Bindings = std::array<int, 8>;
  static constexpr Bindings defaults{
      {SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER,
       SDL_GAMEPAD_BUTTON_SOUTH, SDL_GAMEPAD_BUTTON_DPAD_LEFT,
       SDL_GAMEPAD_BUTTON_DPAD_RIGHT, SDL_GAMEPAD_BUTTON_EAST,
       SDL_GAMEPAD_BUTTON_WEST, SDL_GAMEPAD_BUTTON_NORTH}};
  GamepadInput() {
    // Cabinet evmapy owns translation and hotkey chords; avoid duplicate actions.
    if (const char* mode=SDL_getenv("SLAMTILT_CABINET_KEYBOARD"); mode && mode[0]=='1')
      return;
    initialized_ = SDL_InitSubSystem(SDL_INIT_GAMEPAD);
    if (!initialized_)
      return;
    int n = 0;
    if (auto *ids = SDL_GetGamepads(&n)) {
      for (int i = 0; i < n; ++i)
        add(ids[i]);
      SDL_free(ids);
    }
  }
  ~GamepadInput() {
    if (initialized_ && SDL_WasInit(SDL_INIT_GAMEPAD)) {
      for (auto &item : devices_)
        SDL_CloseGamepad(item.second.handle);
      SDL_QuitSubSystem(SDL_INIT_GAMEPAD);
    }
  }
  GamepadInput(const GamepadInput &) = delete;
  GamepadInput &operator=(const GamepadInput &) = delete;

  // Call for each poll: changes to bindings or modal context release old
  // controls.
  bool poll(SDL_Event &out, const Bindings &keys, const Bindings &buttons,
            bool menu, bool capture = false) {
#ifdef SLAM_GAMEPAD_FRONTEND_PROBE
    gamepad_frontend_probe_ready();
#endif
    if (!configured_ || keys != keys_ || buttons != buttons_ || menu != menu_ ||
        capture != capture_) {
      release();
      keys_ = keys;
      buttons_ = buttons;
      menu_ = menu;
      capture_ = capture;
      configured_ = true;
      for (auto &item : devices_) {
        item.second.blocked = true;
        item.second.armed = false;
      }
    }
    update();
    for (;;) {
      if (!pending_.empty()) {
        out = pending_.front();
        pending_.pop_front();
        return true;
      }
      SDL_Event e;
      if (!SDL_PollEvent(&e))
        return false;
      if (e.type == SDL_EVENT_GAMEPAD_ADDED) {
        add(e.gdevice.which);
        update();
        continue;
      }
      if (e.type == SDL_EVENT_GAMEPAD_REMOVED) {
        auto it = devices_.find(e.gdevice.which);
        if (it != devices_.end()) {
          SDL_CloseGamepad(it->second.handle);
          devices_.erase(it);
        }
        pulse_until_ = 0;
        update();
        continue;
      }
      if (e.type == SDL_EVENT_GAMEPAD_REMAPPED) {
        auto it = devices_.find(e.gdevice.which);
        if (it != devices_.end()) {
          snapshot(it->second);
          it->second.blocked = true;
          it->second.armed = false;
        }
        pulse_until_ = 0;
        update();
        continue;
      }
      if (e.type == SDL_EVENT_WINDOW_FOCUS_LOST ||
          e.type == SDL_EVENT_WINDOW_MINIMIZED) {
        if (e.type == SDL_EVENT_WINDOW_FOCUS_LOST)
          focused_ = false;
        else
          minimized_ = true;
        physical_.fill(false);
        release();
        for (auto &item : devices_) {
          item.second.blocked = true;
          item.second.armed = false;
        }
      }
      if (e.type == SDL_EVENT_WINDOW_FOCUS_GAINED ||
          e.type == SDL_EVENT_WINDOW_RESTORED) {
        if (e.type == SDL_EVENT_WINDOW_FOCUS_GAINED)
          focused_ = true;
        else
          minimized_ = false;
        // Releases can be suppressed while unfocused: resynchronize, then
        // require neutral.
        for (auto &item : devices_) {
          snapshot(item.second);
          item.second.blocked = true;
          item.second.armed = false;
        }
      }
      if (e.type == SDL_EVENT_GAMEPAD_BUTTON_DOWN ||
          e.type == SDL_EVENT_GAMEPAD_BUTTON_UP ||
          e.type == SDL_EVENT_GAMEPAD_AXIS_MOTION) {
        const auto id = e.type == SDL_EVENT_GAMEPAD_AXIS_MOTION
                            ? e.gaxis.which
                            : e.gbutton.which;
        auto it = devices_.find(id);
        if (it == devices_.end())
          continue;
        auto &d = it->second;
        if (e.type == SDL_EVENT_GAMEPAD_AXIS_MOTION &&
            e.gaxis.axis < SDL_GAMEPAD_AXIS_COUNT)
          d.axes[e.gaxis.axis] = e.gaxis.value;
        else if (e.type != SDL_EVENT_GAMEPAD_AXIS_MOTION &&
                 e.gbutton.button < SDL_GAMEPAD_BUTTON_COUNT)
          d.buttons[e.gbutton.button] = e.type == SDL_EVENT_GAMEPAD_BUTTON_DOWN;
        update();
        if (capture_ && focused_ && !minimized_) {
          out = e;
          return true;
        }
        continue;
      }
      if (e.type == SDL_EVENT_KEY_DOWN || e.type == SDL_EVENT_KEY_UP) {
        const auto scan = e.key.scancode;
        if (scan > SDL_SCANCODE_UNKNOWN && scan < SDL_SCANCODE_COUNT) {
          physical_[scan] = e.type == SDL_EVENT_KEY_DOWN;
          if (virtual_[scan] && (e.type == SDL_EVENT_KEY_UP || !e.key.repeat))
            continue;
        }
      }
      out = e;
      return true;
    }
  }
  const bool *keyboard_state() {
    int count = 0;
    const bool *keyboard = SDL_GetKeyboardState(&count);
    combined_.fill(false);
    for (int i = 0; i < std::min(count, int(SDL_SCANCODE_COUNT)); ++i)
      combined_[i] = keyboard[i] || virtual_[i];
    return combined_.data();
  }
  float pull() const {
    if (menu_ || capture_ || !focused_ || minimized_)
      return 0;
    float value = 0;
    for (const auto &item : devices_)
      if (!item.second.blocked)
        value = std::max(
            value,
            std::max(0, int(item.second.axes[SDL_GAMEPAD_AXIS_RIGHT_TRIGGER])) /
                32767.f);
    return value;
  }
  bool held(int scan) const {
    return scan > 0 && scan < SDL_SCANCODE_COUNT && virtual_[scan];
  }
  unsigned connected() const { return unsigned(devices_.size()); }

private:
  struct Device {
    SDL_Gamepad *handle = nullptr;
    std::array<bool, SDL_GAMEPAD_BUTTON_COUNT> buttons{};
    std::array<Sint16, SDL_GAMEPAD_AXIS_COUNT> axes{};
    bool blocked = true, armed = false;
  };
  std::map<SDL_JoystickID, Device> devices_;
  Bindings keys_{}, buttons_{};
  std::array<bool, SDL_SCANCODE_COUNT> virtual_{}, physical_{}, combined_{};
  std::array<Uint64, SDL_SCANCODE_COUNT> repeats_{};
  std::deque<SDL_Event> pending_;
  bool initialized_ = false, configured_ = false, menu_ = false,
       capture_ = false, focused_ = true, minimized_ = false;
  Uint64 pulse_until_ = 0;
  static bool neutral(const Device &d) {
    for (bool b : d.buttons)
      if (b)
        return false;
    for (int i = 0; i < 4; ++i)
      if (std::abs(int(d.axes[i])) > 8000)
        return false;
    return d.axes[SDL_GAMEPAD_AXIS_RIGHT_TRIGGER] < 5000 &&
           d.axes[SDL_GAMEPAD_AXIS_LEFT_TRIGGER] < 5000;
  }
  static void snapshot(Device &d) {
    for (int i = 0; i < SDL_GAMEPAD_BUTTON_COUNT; ++i)
      d.buttons[i] = SDL_GetGamepadButton(d.handle, SDL_GamepadButton(i));
    for (int i = 0; i < SDL_GAMEPAD_AXIS_COUNT; ++i)
      d.axes[i] = SDL_GetGamepadAxis(d.handle, SDL_GamepadAxis(i));
  }
  void add(SDL_JoystickID id) {
    if (devices_.count(id))
      return;
    if (auto *pad = SDL_OpenGamepad(id)) {
      Device d;
      d.handle = pad;
      snapshot(d);
      devices_.emplace(id, d);
    }
  }
  void key(SDL_Scancode scan, bool down) {
    SDL_Event e{};
    e.type = down ? SDL_EVENT_KEY_DOWN : SDL_EVENT_KEY_UP;
    e.key.timestamp = SDL_GetTicksNS();
    e.key.which = 0xfffffff0u;
    e.key.scancode = scan;
    e.key.key = SDL_GetKeyFromScancode(scan, SDL_KMOD_NONE, false);
    e.key.down = down;
    if (auto *window = SDL_GetKeyboardFocus())
      e.key.windowID = SDL_GetWindowID(window);
    pending_.push_back(e);
  }
  void release() {
    pulse_until_ = 0;
    for (int i = 1; i < SDL_SCANCODE_COUNT; ++i)
      if (virtual_[i]) {
        virtual_[i] = false;
        if (!physical_[i])
          key(SDL_Scancode(i), false);
      }
    repeats_.fill(0);
  }
  void update() {
    std::array<bool, SDL_SCANCODE_COUNT> desired{};
    const auto now = SDL_GetTicks();
    auto mark = [&](int scan) {
      if (scan > 0 && scan < SDL_SCANCODE_COUNT)
        desired[scan] = true;
    };
    for (auto &item : devices_) {
      auto &d = item.second;
      if (!focused_ || minimized_ || capture_) {
        d.blocked = true;
        d.armed = false;
        continue;
      }
      if (d.blocked) {
        if (!neutral(d))
          continue;
        d.blocked = false;
      }
      const auto button = [&](SDL_GamepadButton b) { return d.buttons[b]; };
      const int x = d.axes[SDL_GAMEPAD_AXIS_LEFTX],
                y = d.axes[SDL_GAMEPAD_AXIS_LEFTY];
      if (menu_) {
        if (button(SDL_GAMEPAD_BUTTON_DPAD_LEFT) || x < -16000)
          mark(SDL_SCANCODE_LEFT);
        if (button(SDL_GAMEPAD_BUTTON_DPAD_RIGHT) || x > 16000)
          mark(SDL_SCANCODE_RIGHT);
        if (button(SDL_GAMEPAD_BUTTON_DPAD_UP) || y < -16000)
          mark(SDL_SCANCODE_UP);
        if (button(SDL_GAMEPAD_BUTTON_DPAD_DOWN) || y > 16000)
          mark(SDL_SCANCODE_DOWN);
        if (button(SDL_GAMEPAD_BUTTON_SOUTH))
          mark(SDL_SCANCODE_RETURN);
        if (button(SDL_GAMEPAD_BUTTON_EAST) || button(SDL_GAMEPAD_BUTTON_BACK))
          mark(SDL_SCANCODE_BACKSPACE);
        if (button(SDL_GAMEPAD_BUTTON_WEST))
          mark(SDL_SCANCODE_F3);
        if (button(SDL_GAMEPAD_BUTTON_NORTH))
          mark(SDL_SCANCODE_F2);
        if (button(SDL_GAMEPAD_BUTTON_LEFT_SHOULDER))
          mark(SDL_SCANCODE_PAGEUP);
        if (button(SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER))
          mark(SDL_SCANCODE_PAGEDOWN);
      } else {
        for (unsigned i = 0; i < buttons_.size(); ++i)
          if (buttons_[i] >= 0 && buttons_[i] < SDL_GAMEPAD_BUTTON_COUNT &&
              d.buttons[buttons_[i]])
            mark(keys_[i]);
        if (x < -16000)
          mark(keys_[3]);
        if (x > 16000)
          mark(keys_[4]);
        if (y < -16000)
          mark(keys_[5]);
        if (button(SDL_GAMEPAD_BUTTON_BACK))
          mark(SDL_SCANCODE_F10);
        const int trigger = d.axes[SDL_GAMEPAD_AXIS_RIGHT_TRIGGER];
        if (trigger > 18000)
          d.armed = true;
        if (d.armed && trigger < 5000) {
          d.armed = false;
          pulse_until_ = now + 80;
        }
      }
      if (button(SDL_GAMEPAD_BUTTON_START))
        mark(SDL_SCANCODE_ESCAPE);
    }
    if (!menu_ && !capture_ && focused_ && !minimized_ && now < pulse_until_)
      mark(keys_[2]);
    for (int i = 1; i < SDL_SCANCODE_COUNT; ++i) {
      if (desired[i] != virtual_[i]) {
        virtual_[i] = desired[i];
        if (!physical_[i])
          key(SDL_Scancode(i), desired[i]);
        repeats_[i] = desired[i] ? now + 350 : 0;
      } else if (menu_ && desired[i] && i >= SDL_SCANCODE_RIGHT &&
                 i <= SDL_SCANCODE_UP && now >= repeats_[i]) {
        key(SDL_Scancode(i), true);
        repeats_[i] = now + 90;
      }
    }
  }
};
} // namespace slam
