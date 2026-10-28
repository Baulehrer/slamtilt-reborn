#include "assets/native_retail_data.h"
#include <fstream>
int main(int argc,char** argv){
 if(argc!=2)return 2;
 const auto data=slam::native_retail_data_image();
 std::ofstream output(argv[1],std::ios::binary);
 output.write(reinterpret_cast<const char*>(data.data()),data.size());
 return output?0:1;
}
