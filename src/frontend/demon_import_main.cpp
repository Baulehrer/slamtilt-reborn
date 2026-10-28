#include "assets/mean_import.h"
#include <iostream>
#include <stdexcept>
int main(int argc,char**argv){try{
  std::filesystem::path executable=std::filesystem::absolute(argv[0]);
#ifdef __linux__
  executable=std::filesystem::read_symlink("/proc/self/exe");
#endif
  std::filesystem::path recipe=SLAM_DEMON_IMPORT_RECIPE;
  const auto bundled=executable.parent_path().parent_path()/"share/slamtilt/demon-retail-startup.json";
  if(std::filesystem::is_regular_file(bundled))recipe=bundled;
  if(argc==3&&std::string(argv[1])=="--check"){
    std::string error;if(!slam::verify_retail_data(argv[2],recipe,&error))throw std::runtime_error(error);
    std::cout<<"Demon data verified\n";return 0;
  }
  if(argc==2&&std::string(argv[1])=="--help"){
    std::cout<<"Usage: slamdemon-import DAT_DIRECTORY NEW_OUTPUT (or EXE DAT_DIRECTORY NEW_OUTPUT for legacy import)\nNative import of the supported Windows Retail revision. No Python, Wine or emulator.\n";return 0;
  }
  if(argc!=3&&argc!=4)throw std::runtime_error("Usage: slamdemon-import DAT_DIRECTORY NEW_OUTPUT");
  const bool dat_only=argc==3;
  slam::import_retail(dat_only?std::filesystem::path{}:std::filesystem::path(argv[1]),argv[dat_only?1:2],argv[dat_only?2:3],recipe);
  std::cout<<"Demon data ready: "<<argv[dat_only?2:3]<<" (5 verified files)\n";
}catch(const std::exception&e){std::cerr<<"slamdemon-import: "<<e.what()<<'\n';return 2;}}
