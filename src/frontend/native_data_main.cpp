#include "assets/native_retail_data.h"
#include <fstream>
#include <iostream>
#include <stdexcept>
int main(int argc,char**argv) {
  try {
    if(argc!=2)throw std::runtime_error("Usage: slamnative-data NEW_OUTPUT");
    const auto image=slam::native_retail_data_image();
    if(image.size()!=0x100000)throw std::runtime_error("Invalid native data image size");
    std::ofstream file(argv[1],std::ios::binary);
    file.write(reinterpret_cast<const char*>(image.data()),image.size());
    if(!file)throw std::runtime_error("Cannot write native data image");
    std::cout<<"Native engine/table data generated\n";
  }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
}
