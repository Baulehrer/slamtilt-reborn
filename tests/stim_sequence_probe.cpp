#include <xmp.h>
#include <cstdlib>
#include <iostream>

int main(int argc, char **argv) {
  if (argc != 4) return 1;
  auto ctx = xmp_create_context();
  if (!ctx || xmp_load_module(ctx, argv[1]) || xmp_start_player(ctx, 44100, 0) ||
      xmp_set_player(ctx, XMP_PLAYER_MIX, 0) ||
      xmp_set_player(ctx, XMP_PLAYER_INTERP, XMP_INTERP_NEAREST) ||
      xmp_set_player(ctx, XMP_PLAYER_VOLUME, 66)) return 2;
  const int order = std::atoi(argv[2]);
  if (order < 0 || (order > 0 && xmp_set_position(ctx, order) < 0)) return 2;
  for (int tick = 0; tick < std::atoi(argv[3]); ++tick) {
    if (xmp_play_frame(ctx)) return 3;
    xmp_frame_info frame{}; xmp_get_frame_info(ctx, &frame);
    for (int ch = 0; ch < 4; ++ch) {
      const auto &c = frame.channel_info[ch];
      std::cout << c.period << ' ' << int(c.volume) << ' ' << int(c.instrument) << ' '
                << int(c.event.note) << ' ' << int(c.event.fxt) << ' ' << int(c.event.fxp) << ' ';
    }
    std::cout << frame.pos << ' ' << frame.row << ' ' << frame.frame << '\n';
  }
  xmp_end_player(ctx); xmp_release_module(ctx); xmp_free_context(ctx);
  return std::cout ? 0 : 4;
}
