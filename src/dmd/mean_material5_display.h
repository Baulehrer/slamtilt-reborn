#pragma once
#include "assets/mean_score_font.h"
#include "dmd/windows_dmd.h"
#include "dmd/mean_display_scheduler.h"
#include "dmd/mean_bonus_pixels.h"
#include <filesystem>
namespace slam {
struct MeanMaterial5DisplayAssets {
  WindowsDmdPixels frame_151304{};
  std::array<WindowsDmdPixels,8> frames_13038e{};
  std::array<WindowsDmdPixels, 16> frames_1359ce{};
  std::array<WindowsDmdPixels, 5> frames_1377ce{};
  std::array<WindowsDmdPixels, 16> frames_11670e{};
  std::array<WindowsDmdPixels, 10> frames_11544e{}, frames_11418e{};
  WindowsDmdPixels frame_11652e{}, frame_14fa0e{}, frame_105eae{};
  std::array<WindowsDmdPixels, 8> frames_10518e{};
  WindowsDmdPixels frame_14fbee{}, frame_15018e{}, frame_14ecee{}, frame_14f82e{};
  std::array<WindowsDmdPixels, 23> frames_13f92e{};
  std::array<WindowsDmdPixels, 12> frames_12a7ae{};
  std::array<WindowsDmdPixels, 7> frames_12be2e{}, frames_12cb4e{};
  MeanBonusPixels text_font{};
  std::array<WindowsDmdPixels, 9> frames_14244e{};
  std::array<WindowsDmdPixels, 13> frames_14352e{};
  std::array<WindowsDmdPixels, 27> frames_137f4e{};
  std::array<WindowsDmdPixels, 19> frames_13bf0e{};
  WindowsDmdPixels mode6_ready{};
  std::array<WindowsDmdPixels, 6> frames_11904e{}, frames_119b8e{};
  std::array<WindowsDmdPixels, 20> frames_11a6ce{};
  std::array<WindowsDmdPixels, 16> frames_10a7ce{};
  std::array<WindowsDmdPixels, 20> frames_10c5ce{};
  std::array<WindowsDmdPixels, 6> frames_12d86e{}, frames_10176e{};
  std::array<WindowsDmdPixels, 7> frames_fb9ae{};
  std::array<WindowsDmdPixels, 12> frames_fa32e{};
  std::array<WindowsDmdPixels, 5> frames_151e44{};
  std::array<WindowsDmdPixels, 15> frames_ffb4e{};
  std::array<WindowsDmdPixels, 18> frames_13380e{};
  std::array<WindowsDmdPixels, 9> frames_11f94e{};
  std::array<WindowsDmdPixels, 20> frames_1022ae{};
  std::array<WindowsDmdPixels, 14> frames_14a5ae{};
  std::array<WindowsDmdPixels, 12> frames_14bfee{};
  WindowsDmdPixels frame_10464e{}, frame_1506ac{};
  std::array<WindowsDmdPixels, 25> frames_12336e{};
  std::array<WindowsDmdPixels, 14> frames_12624e{};
  std::array<WindowsDmdPixels, 6> frames_144bae{}; // original frameindices-1..4
  std::array<WindowsDmdPixels, 10> frames_1483ee{};
  WindowsDmdPixels frame_13b00e{}, frame_151c64{};
  WindowsDmdPixels frame_14f46e{}, frame_14f64e{};
  std::array<WindowsDmdPixels, 19> frames_111dee{};
  std::array<WindowsDmdPixels, 7> reward_pages{};
  std::array<WindowsDmdPixels, 6> frames_109c8e{};
  std::array<WindowsDmdPixels, 9> frames_108bae{};
  std::array<std::array<std::uint8_t, 240>, 17> masks_fdd4e{};
  WindowsDmdPixels frame_150e2c{}, frame_150a6c{}, frame_150c4c{};
  std::array<WindowsDmdPixels, 8> frames_1474ee{}, frames_1496ae{};
  std::array<WindowsDmdPixels, 17> frames_12e3ae{};
};
MeanMaterial5DisplayAssets
load_mean_material5_display(const std::filesystem::path &);
struct MeanMaterial5Display {
  MeanDisplayScheduler scheduler;
  std::uint32_t callback = 0, counter = 0, field_050 = 0;
  std::uint32_t field_058=0; // Live mode total, Original43f058.
  bool stop_audio_8c=false; // Per-step service8c request from410c8c.
  std::uint32_t minigame_lap_points=20000000;
  // Signed highword of the original player gear fixed-point field.
  std::int32_t gear=2;
  std::uint32_t field_43efcc = 0, field_43efdc = 0;
  std::uint16_t field_358 = 0, field_362 = 0, field_1fe = 0, field_1f2 = 0, field_204 = 0;
  std::uint16_t field_1d8 = 4, field_38a = 0;
  WindowsDmdPixels pixels{}, restore_pixels{}; // Original43efd0 calloc buffer.
  bool request(const MeanDisplayRequest &r, std::uint32_t score,
               bool save_page = false) {
    if (!mean_display_request(scheduler, r)) return false;
    if (save_page) restore_pixels = pixels;
    callback = r.callback;
    counter = static_cast<std::uint32_t>(r.ebx);
    field_050 = score;
    return true;
  }
  void start(std::uint32_t address, std::uint32_t score) {
    scheduler = {};
    scheduler.field_780 = 4; scheduler.field_784 = 2;
    scheduler.field_790 = address;
    callback = address;
    counter = 0;
    field_050 = score;
  }
};
// Originaltarget/bank/extra-ball callbacks: pixels andcounter. Awardcounter45
// external lamp/display setupservices omitted here; no overall scheduler
// equivalence.
void mean_material5_display_step(MeanMaterial5Display &,
                                 const MeanMaterial5DisplayAssets &,
                                 const MeanScoreFont &,
                                 const std::array<std::uint8_t, 4> &);
} // namespace slam

namespace slam {
MeanDisplayDispatch mean_material5_display_scheduled_step(MeanMaterial5Display &,
    const MeanMaterial5DisplayAssets &, const MeanScoreFont &,
    const std::array<std::uint8_t, 4> &);
} // namespace slam

namespace slam {
struct MeanDisplayEffects {
  bool release_reward=false, release_mode6=false, request_438afc=false;
};
inline MeanDisplayEffects mean_display_callback_effects(std::uint32_t callback,
    unsigned counter, MeanDisplayDispatch dispatch) {
  return {dispatch==MeanDisplayDispatch::Idle,
          dispatch==MeanDisplayDispatch::Callback && callback==0x410b00 && counter==267,
          dispatch==MeanDisplayDispatch::Callback &&
              ((callback==0x410d34 && counter==75) ||
               (callback==0x412908 && counter==16) ||
               (callback==0x411710 && counter==12) ||
               (callback==0x4126ec && counter==20))};
}
} // namespace slam
