#include "core/sha256.h"
#include <iostream>
#include <vector>
int main() {
  const std::vector<std::pair<std::string,std::string>> cases{
    {"","e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    {"abc","ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
    {"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq","248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"},
    {std::string(1000000,'a'),"cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"}};
  for(const auto& test:cases)if(slam::sha256({test.first.begin(),test.first.end()})!=test.second) {
    std::cerr<<"SHA-256 known vector failed at length "<<test.first.size()<<'\n';return 1;
  }
  return 0;
}
