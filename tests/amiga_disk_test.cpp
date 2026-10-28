#include "assets/amiga_disk.h"
#include "core/sha256.h"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
namespace {
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
void put(std::vector<std::uint8_t>& b,unsigned at,unsigned v){for(unsigned i=0;i<4;++i)b[at+i]=std::uint8_t(v>>(24-i*8));}
template<class F>void rejected(F f){bool failed=false;try{f();}catch(const std::exception&){failed=true;}require(failed,"Malformed SLAM was accepted");}
std::string lower(std::string s){for(auto&c:s)if(c>='A'&&c<='Z')c=char(c-'A'+'a');return s;}
void synthetic(){
 std::vector<std::uint8_t>b(22);b[0]='S';b[1]='L';b[2]='A';b[3]='M';put(b,4,0x50);put(b,8,1);put(b,12,4);
 b[17]=10;b[18]=0x2d;b[21]=9; // literal 0 + 01011010 -> Z
 require(slam::decode_slam(b)==std::vector<std::uint8_t>{0x5a},"SLAM literal fixture mismatch");
 rejected([&]{slam::decode_slam(b,0);});
 for(unsigned size=0;size<22;++size)rejected([&]{slam::decode_slam(std::vector<std::uint8_t>(b.begin(),b.begin()+size));});
 auto bad=b;bad[0]=0;rejected([&]{slam::decode_slam(bad);});bad=b;bad[7]=0x51;rejected([&]{slam::decode_slam(bad);});
 bad=b;put(bad,8,0);rejected([&]{slam::decode_slam(bad);});bad=b;put(bad,12,0xffffffff);rejected([&]{slam::decode_slam(bad);});
 bad=b;bad[17]=9;rejected([&]{slam::decode_slam(bad);});bad=b;bad[21]=17;rejected([&]{slam::decode_slam(bad);});
 bad=b;bad[21]=0;rejected([&]{slam::decode_slam(bad);});
 bad=b;put(bad,8,2);bad[18]=0xc8;bad[19]=0;bad[21]=10;rejected([&]{slam::decode_slam(bad);});
}
}
int main(int argc,char**argv){try{
 synthetic();
 if(argc==1){std::cout<<"SLAM literal/bounds/malformed fixtures PASS\n";return 0;}
 require(argc==3||argc==4,"Usage: amiga_disk_test ADF_FOLDER REFERENCE_DECODED_DIR [REPORT]");
 const auto files=slam::read_amiga_adf_set(argv[1]);nlohmann::json rows=nlohmann::json::array();unsigned compared=0;
 std::map<std::string,std::filesystem::path> references;
 if(std::filesystem::is_directory(argv[2]))for(auto&p:std::filesystem::recursive_directory_iterator(argv[2]))if(p.is_regular_file())references.emplace(lower(p.path().lexically_relative(argv[2]).generic_string()),p.path());
 for(const auto&[name,bytes]:files){nlohmann::json row{{"name",name},{"size",bytes.size()},{"sha256",slam::sha256(bytes)}};
  if(bytes.size()>=4&&std::equal(bytes.begin(),bytes.begin()+4,"SLAM")){
   const auto decoded=slam::decode_slam(bytes);row["decoded_size"]=decoded.size();row["decoded_sha256"]=slam::sha256(decoded);
   if(const auto at=references.find(name);at!=references.end()){
    std::ifstream f(at->second,std::ios::binary);const std::vector<std::uint8_t> expected{std::istreambuf_iterator<char>(f),{}};
    require(decoded==expected,"Native SLAM differs from reference output");++compared;
   }
  }
  rows.push_back(std::move(row));
 }
 nlohmann::json result{{"status","VERIFIED_NATIVE_ADF_AND_SLAM"},{"reference_decoded_matches",compared},{"files",rows}};
 if(argc==4){std::ofstream f(argv[3]);f<<result.dump(2)<<'\n';require(bool(f),"Cannot write test report");}
 else std::cout<<result.dump(2)<<'\n';
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
