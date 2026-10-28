// Standalone original-menu decoder smoke probe; writes a private PPM snapshot.
#include "assets/menu_assets.h"
#include <fstream>
#include <iostream>
int main(int argc,char**argv) {
  try {
    if(argc!=3)return 2;
    const auto image=slam::load_windows_menu(argv[1]);
    std::ofstream out(argv[2],std::ios::binary);
    out<<"P6\n"<<image.width<<' '<<image.height<<"\n255\n";
    for(std::size_t i=0;i<image.rgba.size();i+=4)
      out.write(reinterpret_cast<const char*>(image.rgba.data()+i),3);
    if(!out)return 2;
    std::cout<<image.width<<'x'<<image.height<<" original menu decoded\n";
  }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
}
