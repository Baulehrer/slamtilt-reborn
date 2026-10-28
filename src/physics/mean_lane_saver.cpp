#include "mean_lane_saver.h"
#include <algorithm>
#include <stdexcept>
namespace slam {
MeanLaneSaverEvent mean_lane_saver_tick(std::array<std::int32_t,3> &s,
                                      bool idle) {
  MeanLaneSaverEvent e;
  if (!s[2]) return e;
  if (s[0]>=0) {
    s[0]=static_cast<std::int32_t>(static_cast<std::uint32_t>(s[0])-1u);
    if(s[0]>=0) return e;
    s[0]=3;
  }
  if(!idle || s[1]<0) return e;
  e.draw_requested=true;
  e.drawn_frame=s[1];
  if(s[2]<0 && s[1]>0) --s[1];
  else if(s[2]>=0 && s[1]<2) ++s[1];
  else {
    s[2]=0;
    e.patch_requested=true;
    e.enabled=s[1]!=0;
  }
  return e;
}
void mean_lane_saver_patch(std::vector<std::uint8_t> &dat,
                          std::size_t normal_offset,std::size_t hit_offset,
                          bool enabled) {
  const std::size_t normal_source=enabled?0x9436e:0x94b2e;
  const std::size_t hit_source=enabled?0x9472e:0x94eee;
  const auto normal_dest=normal_offset+0x49e1;
  const auto hit_dest=hit_offset+0x49e1;
  if(normal_source+120>dat.size() || hit_source+512>dat.size() ||
     normal_dest+29*40+4>dat.size() || hit_dest+3*0x6040+31*40+4>dat.size())
    throw std::out_of_range("Mean lane saver collision patch");
  for(unsigned y=0;y<30;++y)
    std::copy_n(dat.begin()+normal_source+y*4,4,dat.begin()+normal_dest+y*40);
  for(unsigned plane=0;plane<4;++plane)
    for(unsigned y=0;y<32;++y)
      std::copy_n(dat.begin()+hit_source+plane*128+y*4,4,
                  dat.begin()+hit_dest+plane*0x6040+y*40);
}
} // namespace slam
