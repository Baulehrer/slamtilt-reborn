#include "frontend/port_options.h"
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>

static void check(bool value, const char *message) {
  if (!value)
    throw std::runtime_error(message);
}
int main(int argc, char **argv) {
#ifndef __linux__
  std::cerr << "This fixture requires Linux XDG preference isolation.\n";
  return 77;
#else
  std::filesystem::path temp;
  try {
    temp = std::filesystem::temp_directory_path() /
           ("reborn-gamepad-" +
            std::to_string(
                std::chrono::steady_clock::now().time_since_epoch().count()));
    std::filesystem::create_directories(temp);
    SDL_setenv_unsafe("XDG_DATA_HOME", temp.string().c_str(), 1);
    SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
    SDL_SetHint(SDL_HINT_GAMECONTROLLER_IGNORE_DEVICES_EXCEPT, "0xf00d/0x0042");
    check(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMEPAD), SDL_GetError());
    SDL_VirtualJoystickDesc desc{};
    SDL_INIT_INTERFACE(&desc);
    desc.type = SDL_JOYSTICK_TYPE_GAMEPAD;
    desc.vendor_id = 0xf00d;
    desc.product_id = 0x0042;
    desc.naxes = SDL_GAMEPAD_AXIS_COUNT;
    desc.nbuttons = SDL_GAMEPAD_BUTTON_COUNT;
    desc.axis_mask = (1u << SDL_GAMEPAD_AXIS_COUNT) - 1;
    desc.button_mask = (1u << SDL_GAMEPAD_BUTTON_COUNT) - 1;
    desc.name = "Reborn virtual acceptance pad";
    auto id = SDL_AttachVirtualJoystick(&desc);
    check(id != 0, SDL_GetError());
    auto *joy = SDL_OpenJoystick(id);
    check(joy, SDL_GetError());
    SDL_SetJoystickVirtualAxis(joy, SDL_GAMEPAD_AXIS_LEFT_TRIGGER,
                               SDL_JOYSTICK_AXIS_MIN);
    SDL_SetJoystickVirtualAxis(joy, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER,
                               SDL_JOYSTICK_AXIS_MIN);
    SDL_UpdateJoysticks();
    PortOptions options;
    options.load(true);
    std::vector<std::string> passed;
    {
      slam::GamepadInput input;
      bool menu = false;
      auto drain = [&]() {
        std::vector<SDL_Event> events;
        SDL_Event e;
        unsigned count = 0;
        while (input.poll(e, options.settings.keys,
                          options.settings.gamepad_buttons, menu,
                          options.gamepad_binding())) {
          events.push_back(e);
          check(++count < 1000, "Input event loop failed to drain");
        }
        return events;
      };
      auto button = [&](SDL_GamepadButton b, bool down) {
        check(SDL_SetJoystickVirtualButton(joy, b, down), SDL_GetError());
        SDL_UpdateJoysticks();
        return drain();
      };
      auto axis = [&](Sint16 value) {
        check(SDL_SetJoystickVirtualAxis(joy, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER,
                                         value),
              SDL_GetError());
        SDL_UpdateJoysticks();
        return drain();
      };
      auto has = [](const auto &events, Uint32 type, SDL_Scancode scan) {
        return std::count_if(events.begin(), events.end(),
                             [&](const SDL_Event &e) {
                               return e.type == type && e.key.scancode == scan;
                             });
      };
      auto focus = [&](Uint32 type) {
        SDL_Event e{};
        e.type = type;
        check(SDL_PushEvent(&e), SDL_GetError());
        return drain();
      };
      auto key = [](SDL_Keycode code) {
        SDL_Event e{};
        e.type = SDL_EVENT_KEY_DOWN;
        e.key.key = code;
        e.key.scancode = SDL_GetScancodeFromKey(code, nullptr);
        return e;
      };
      drain();
      check(input.connected() == 1, "SDL virtual gamepad not opened");
      check(has(button(SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, true),
                SDL_EVENT_KEY_DOWN, SDL_SCANCODE_LSHIFT) == 1,
            "Left flipper press missing");
      check(input.keyboard_state()[SDL_SCANCODE_LSHIFT],
            "Polled Mean flipper state missing");
      check(has(button(SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, false),
                SDL_EVENT_KEY_UP, SDL_SCANCODE_LSHIFT) == 1,
            "Flipper release missing");
      passed.push_back(
          "real SDL virtual button -> key edges and polled Mean state");
      button(SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER, true);
      focus(SDL_EVENT_WINDOW_FOCUS_LOST);
      check(!input.keyboard_state()[SDL_SCANCODE_RSHIFT],
            "Focus loss left a flipper held");
      focus(SDL_EVENT_WINDOW_FOCUS_GAINED);
      check(!input.keyboard_state()[SDL_SCANCODE_RSHIFT],
            "Held pad leaked across focus gain");
      button(SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER, false);
      check(has(button(SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER, true),
                SDL_EVENT_KEY_DOWN, SDL_SCANCODE_RSHIFT) == 1,
            "Pad failed to rearm after neutral");
      focus(SDL_EVENT_WINDOW_FOCUS_LOST);
      SDL_SetJoystickVirtualButton(joy, SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER,
                                   false);
      SDL_UpdateJoysticks();
      SDL_FlushEvent(SDL_EVENT_GAMEPAD_BUTTON_UP);
      focus(SDL_EVENT_WINDOW_FOCUS_GAINED);
      check(has(button(SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER, true),
                SDL_EVENT_KEY_DOWN, SDL_SCANCODE_RSHIFT) == 1,
            "Lost background release did not resync on focus return");
      menu = true;
      drain();
      check(!input.keyboard_state()[SDL_SCANCODE_RSHIFT],
            "Opening menu left game action held");
      button(SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER, false);
      check(has(button(SDL_GAMEPAD_BUTTON_DPAD_DOWN, true), SDL_EVENT_KEY_DOWN,
                SDL_SCANCODE_DOWN) == 1,
            "Dpad menu navigation missing");
      SDL_Delay(370);
      check(has(drain(), SDL_EVENT_KEY_DOWN, SDL_SCANCODE_DOWN) == 1,
            "Held navigation repeat missing");
      button(SDL_GAMEPAD_BUTTON_DPAD_DOWN, false);
      passed.push_back("focus/modal neutral barrier and menu held navigation");
      menu = false;
      drain();
      check(has(button(SDL_GAMEPAD_BUTTON_START, true), SDL_EVENT_KEY_DOWN,
                SDL_SCANCODE_ESCAPE) == 1,
            "Start/options missing");
      button(SDL_GAMEPAD_BUTTON_START, false);
      check(has(button(SDL_GAMEPAD_BUTTON_BACK, true), SDL_EVENT_KEY_DOWN,
                SDL_SCANCODE_F10) == 1,
            "Back/table-menu missing");
      button(SDL_GAMEPAD_BUTTON_BACK, false);
      passed.push_back("reserved Start/options and Back/table menu");
      check(!has(axis(0), SDL_EVENT_KEY_DOWN, SDL_SCANCODE_RETURN),
            "Trigger noise fired launch");
      check(!has(axis(SDL_JOYSTICK_AXIS_MAX), SDL_EVENT_KEY_DOWN,
                 SDL_SCANCODE_RETURN),
            "Pull fired before release");
      check(input.pull() > .99f, "Analog trigger position lost");
      check(has(axis(SDL_JOYSTICK_AXIS_MIN), SDL_EVENT_KEY_DOWN,
                SDL_SCANCODE_RETURN) == 1,
            "Pull/release launch missing");
      check(input.keyboard_state()[SDL_SCANCODE_RETURN],
            "Launch pulse unavailable to Mean polling");
      check(!has(drain(), SDL_EVENT_KEY_DOWN, SDL_SCANCODE_RETURN),
            "Launch pulse repeated");
      SDL_Delay(100);
      check(has(drain(), SDL_EVENT_KEY_UP, SDL_SCANCODE_RETURN) == 1,
            "Launch pulse stuck");
      axis(SDL_JOYSTICK_AXIS_MAX);
      focus(SDL_EVENT_WINDOW_FOCUS_LOST);
      focus(SDL_EVENT_WINDOW_FOCUS_GAINED);
      check(!has(axis(SDL_JOYSTICK_AXIS_MIN), SDL_EVENT_KEY_DOWN,
                 SDL_SCANCODE_RETURN),
            "Focus restore fired armed plunger");
      passed.push_back("analog pull/release one-shot, noise rejection, pulse "
                       "release and focus cancellation");
      options.handle(key(SDLK_ESCAPE));
      menu = true;
      drain();
      options.select_option(PortOptions::PadLeftFlipper);
      options.handle(key(SDLK_RETURN));
      check(options.gamepad_binding(), "Controller binding did not open");
      for (const auto &e : button(SDL_GAMEPAD_BUTTON_WEST, true))
        options.handle(e);
      check(options.settings.gamepad_buttons[0] == SDL_GAMEPAD_BUTTON_WEST,
            "Raw controller capture failed");
      check(options.settings.gamepad_buttons[6] ==
                SDL_GAMEPAD_BUTTON_LEFT_SHOULDER,
            "Occupied binding was not swapped");
      button(SDL_GAMEPAD_BUTTON_WEST, false);
      options.select_option(PortOptions::Apply);
      options.handle(key(SDLK_RETURN));
      menu = false;
      drain();
      PortOptions restored;
      restored.load(true);
      check(restored.settings.gamepad_buttons ==
                options.settings.gamepad_buttons,
            "Controller mapping did not persist");
      check(has(button(SDL_GAMEPAD_BUTTON_WEST, true), SDL_EVENT_KEY_DOWN,
                SDL_SCANCODE_LSHIFT) == 1,
            "Remapped physical button did not drive flipper");
      SDL_Event physical = key(SDLK_LSHIFT);
      SDL_PushEvent(&physical);
      check(!has(drain(), SDL_EVENT_KEY_DOWN, SDL_SCANCODE_LSHIFT),
            "Mixed keyboard/pad generated duplicate press");
      check(!has(button(SDL_GAMEPAD_BUTTON_WEST, false), SDL_EVENT_KEY_UP,
                 SDL_SCANCODE_LSHIFT),
            "Pad release cancelled held keyboard action");
      physical.type = SDL_EVENT_KEY_UP;
      SDL_PushEvent(&physical);
      check(has(drain(), SDL_EVENT_KEY_UP, SDL_SCANCODE_LSHIFT) == 1,
            "Keyboard release lost after mixed input");
      button(SDL_GAMEPAD_BUTTON_WEST, true);
      options.settings.keys[0] = SDL_SCANCODE_Z;
      check(has(drain(), SDL_EVENT_KEY_UP, SDL_SCANCODE_LSHIFT) == 1 &&
                !input.keyboard_state()[SDL_SCANCODE_Z],
            "Held action leaked through keyboard remapping");
      button(SDL_GAMEPAD_BUTTON_WEST, false);
      check(has(button(SDL_GAMEPAD_BUTTON_WEST, true), SDL_EVENT_KEY_DOWN,
                SDL_SCANCODE_Z) == 1,
            "New keyboard target did not rearm");
      auto second = SDL_AttachVirtualJoystick(&desc);
      auto *joy2 = SDL_OpenJoystick(second);
      check(joy2, SDL_GetError());
      SDL_SetJoystickVirtualAxis(joy2, SDL_GAMEPAD_AXIS_LEFT_TRIGGER,
                                 SDL_JOYSTICK_AXIS_MIN);
      SDL_SetJoystickVirtualAxis(joy2, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER,
                                 SDL_JOYSTICK_AXIS_MIN);
      SDL_UpdateJoysticks();
      drain();
      SDL_SetJoystickVirtualButton(joy2, SDL_GAMEPAD_BUTTON_WEST, true);
      SDL_UpdateJoysticks();
      drain();
      check(!has(button(SDL_GAMEPAD_BUTTON_WEST, false), SDL_EVENT_KEY_UP,
                 SDL_SCANCODE_Z) &&
                input.keyboard_state()[SDL_SCANCODE_Z],
            "One pad released another pad's held action");
      SDL_DetachVirtualJoystick(second);
      check(has(drain(), SDL_EVENT_KEY_UP, SDL_SCANCODE_Z) == 1,
            "Last device release was lost");
      SDL_CloseJoystick(joy2);
      button(SDL_GAMEPAD_BUTTON_WEST, true);
      check(SDL_DetachVirtualJoystick(id), SDL_GetError());
      drain();
      check(input.connected() == 0 && !input.keyboard_state()[SDL_SCANCODE_Z],
            "Disconnect left controller/held action");
      passed.push_back("mixed keyboard/pad holds, keyboard-remap neutral "
                       "barrier and two-pad aggregation");
      passed.push_back("raw pad rebinding, duplicate swap, persistence, "
                       "remapped action and disconnect release");
    }
    SDL_CloseJoystick(joy);
    SDL_Quit();
    nlohmann::json report = {{"status", "PASS"},
                             {"backend", "SDL virtual gamepad, dummy video"},
                             {"checks", passed},
                             {"physical_hardware", false}};
    if (argc > 1)
      std::ofstream(argv[1]) << report.dump(2) << '\n';
    std::cout << report.dump(2) << '\n';
    std::filesystem::remove_all(temp);
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "Gamepad acceptance: " << e.what() << " SDL=" << SDL_GetError()
              << '\n';
    SDL_Quit();
    if (!temp.empty())
      std::filesystem::remove_all(temp);
    return 1;
  }
#endif
}
