#include "assets/mean_import.h"
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
namespace fs=std::filesystem;
int main(int argc,char** argv) {
  try {
    fs::path executable=fs::absolute(argv[0]);
#ifdef __linux__
    executable=fs::read_symlink("/proc/self/exe");
#endif
    const auto metadata=executable.parent_path()/"share/slamtilt";
    fs::path recipe=SLAM_IMPORT_SOURCE_RECIPE,profile=SLAM_IMPORT_SOURCE_PROFILE;
    if(fs::is_directory(metadata)) { recipe=metadata/"mean-demo-startup.json";profile=metadata/"mean-data.sha256"; }
    bool adf=false;bool check=false;std::vector<std::string> args;
    for(int i=1;i<argc;++i) {
      const std::string option=argv[i];
      if(option=="--help"||option=="-h") {
        std::cout<<"Usage: slamimport --adf ADF_FOLDER NEW_OUTPUT\n       slamimport DAT_DIRECTORY NEW_OUTPUT\n"
                   "       slamimport EXE DAT_DIRECTORY NEW_OUTPUT (legacy import)\n"
                   "       slamimport --check DATA_DIRECTORY [--profile FILE]\n"
                   "Native DAT-only import; optional legacy EXE mode. No Python or emulator.\n";
        return 0;
      }
      if(option=="--profile"&&i+1<argc)profile=argv[++i];
      else if(option=="--recipe"&&i+1<argc)recipe=argv[++i];
      else if(option=="--adf")adf=true;
      else if(option=="--check")check=true;
      else args.push_back(option);
    }
    if(adf) {
      if(check||args.size()!=2)throw std::runtime_error("Usage: slamimport --adf ADF_FOLDER NEW_OUTPUT");
      slam::import_amiga_adfs(args[0],args[1],recipe.parent_path(),profile);
      std::cout<<"Four Amiga tables imported (shared native rules)\n";return 0;
    }
    if(check&&args.size()==1) {
      std::string error;
      if(!slam::verify_mean_data(args[0],profile,&error))throw std::runtime_error(error);
      std::cout<<"Mean data verified\n";return 0;
    }
    if(check||(args.size()!=2&&args.size()!=3))throw std::runtime_error("Usage: slamimport DAT_DIRECTORY NEW_OUTPUT, or --check DATA_DIRECTORY");
    const bool dat_only=args.size()==2;
    slam::import_mean(dat_only?fs::path{}:fs::path(args[0]),args[dat_only?0:1],args[dat_only?1:2],recipe,profile);
    std::cout<<"Mean data ready: "<<args.back()<<" (8 verified files, native import)\n";
    return 0;
  } catch(const std::exception& error) { std::cerr<<"slamimport: "<<error.what()<<'\n';return 2; }
}
