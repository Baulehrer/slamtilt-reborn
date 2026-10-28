#include "assets/ball_mask.h"
#include <iostream>
int main(int argc,char**argv){try{
  if(argc!=2)return 2;
  const auto bank=slam::load_windows_ball_pixel_bank(argv[1]);
  for(int y=0;y<600;++y)if(bank[y/8]!=slam::load_windows_ball_pixels(argv[1],y))throw std::runtime_error("Ball bank row mismatch");
  std::cout<<"600Y positions/75original shading groups exact\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
