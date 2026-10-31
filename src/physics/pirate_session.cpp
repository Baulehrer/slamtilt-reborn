#include "physics/pirate_session.h"
#include "assets/native_data_profiles.h"
#include "assets/amiga_data_profiles.h"
#include "assets/amiga_data_profiles_v2.h"
#include "core/sha256.h"
#include "core/retail_music_start.h"
#include <algorithm>
#include <fstream>
namespace slam {
namespace {
std::vector<std::uint8_t> read(const std::filesystem::path& path,
                              const char* expected,const char* alternate=nullptr,const char* amiga=nullptr,const char* upgraded=nullptr) {
  std::ifstream file(path,std::ios::binary);
  if(!file)throw std::runtime_error("Missing Pirate input: "+path.string());
  std::vector<std::uint8_t> bytes{std::istreambuf_iterator<char>(file),{}};
  const auto hash=sha256(bytes);
  if(hash!=expected&&(!alternate||hash!=alternate)&&(!amiga||hash!=amiga)&&(!upgraded||hash!=upgraded))throw std::runtime_error("Unsupported Pirate input: "+path.string());
  return bytes;
}
std::uint32_t word(const std::vector<std::uint8_t>& bytes,unsigned offset,unsigned n=4) {
  std::uint32_t value=0;
  for(unsigned i=0;i<n;++i)value|=std::uint32_t(bytes.at(offset+i))<<(8*i);
  return value;
}
}
PirateSession::PirateSession(const std::filesystem::path& prepared,
                             const std::filesystem::path& dat,PirateTickMode mode):mode_(mode) {
  // Post-F1 snapshots: full mode uses pirate_full_tick_oracle.py with the
  // canonical ball pool and original startup bindings; physics-only retains
  // pirate_human_oracle.py's isolated context. Both identities are pinned.
  initial_image_=read(prepared/"human-image.bin",mode_==PirateTickMode::Full?"5c112a970a16ab4d768201c98b2838f2200bc4996de719db8477e3f42fbf0379":"c4498aa71402c87b34a5748b757ee28baf29bb3d9783538a0607d21b5fd8fdfa",mode_==PirateTickMode::Full?native_pirate_image_sha256:nullptr,mode_==PirateTickMode::Full?native_amiga_pirate_image_sha256:nullptr,mode_==PirateTickMode::Full?native_amiga_v2_pirate_image_sha256:nullptr);
  initial_runtime_=read(prepared/"human-runtime.bin",mode_==PirateTickMode::Full?"0ddf844045e1e69ac9c949a638f83601901720a6ad2b057d18c861b2013dbca5":"abd07b3aa0048a5238d02ca07caf75156abf0272d6108f60b546017da92d5450");
  initial_dat_=read(dat,"6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6",amiga_table_sha256("pirate").data(),amiga_v2_table_sha256("pirate").data());
  reset();
}
void PirateSession::reset() {
  machine_=PirateStepLift{};
  machine_.image=initial_image_;machine_.runtime=initial_runtime_;machine_.dat=initial_dat_;
  // Original405b6a..405b78: the isolated snapshot assigned the math table
  // after ABI startup, so finish that pointer binding before gameplay.
  if(mode_==PirateTickMode::Full)machine_.wr(0x46b778,machine_.rd(0x46c66c,4),4);
  if(mode_==PirateTickMode::Full)initialize_retail_music_start(machine_);
  ticks_=0;left_=right_=false;
  enable_audio_events(audio_enabled_);
}
void PirateSession::enable_audio_events(bool enable) {
  if(enable&&mode_!=PirateTickMode::Full)throw std::runtime_error("Audio requires the full original table context");
  audio_enabled_=enable;audio_requests_.clear();machine_.call_observer={};
  if(!enable)return;
  // Base request already made before the retained post-F1 snapshot.
  audio_requests_.push_back({0x90,int(word(machine_.image,0x54a68)),int(word(machine_.image,0x54a64))});
  machine_.call_observer=[this](PirateStepLift& state,std::uint32_t address){
    int service=0;
    switch(address){
      case 0x406600:service=0x5c;break;
      case 0x406268:service=0x80;break;
      case 0x406240:service=0x84;break;
      case 0x40621c:service=0x88;break;
      case 0x4061f8:service=0x8c;break;
      case 0x4061c4:service=0x90;break;
      default:return;
    }
    // Observe entry registers; original service and its state writes still run.
    if(service==0x5c)audio_requests_.push_back({service,int(std::int32_t(state.r[2])),int(std::int32_t(state.r[3])),state.r[0]});
    else if(service==0x80||service==0x8c)audio_requests_.push_back({service,0,0});
    else audio_requests_.push_back({service,int(std::int32_t(state.r[2])),int(std::int32_t(state.r[0]))});
  };
}
std::vector<AudioRequest> PirateSession::take_audio_requests() {
  auto result=std::move(audio_requests_);audio_requests_.clear();return result;
}
bool PirateSession::new_game() {
  if(phase()!=0)return false; // Original F1 guard404d4f..404d7e.
  machine_.invoke(0x408ae0,1);left_=right_=false;return true;
}
bool PirateSession::initials_active() const {
  return phase()==3&&word(machine_.image,0x6c61c)==6;
}
bool PirateSession::initials_key(std::uint32_t scan) {
  if(!initials_active())return false;
  machine_.invoke(0x405d54,scan);return true;
}
bool PirateSession::initials_character(char character) {
  const auto value=character>='a'&&character<='z'?character-'a'+'A':character;
  if(value=='\r'||value=='\n')return initials_key(0x1c);
  if(value=='\b')return initials_key(0x0e);
  for(unsigned offset=0x54b88;offset+8<machine_.image.size();offset+=8){
    const auto scan=word(machine_.image,offset);if(!scan)break;
    if(word(machine_.image,offset+4)==std::uint32_t(value))return initials_key(scan);
  }
  return false;
}
bool PirateSession::game_over() const {return phase()==0&&word(machine_.image,0x6c684)==0;}
unsigned PirateSession::ball_number() const {
  const auto record=word(machine_.image,0x6b758);
  return word(machine_.image,record-0x400000+14,2);
}
std::array<std::uint32_t,15> PirateSession::lifecycle_state() const {
  const auto record=word(machine_.image,0x6b758)-0x400000;
  return {phase(),ball_count(),word(machine_.image,0x6c680),word(machine_.image,0x6c684),
    word(machine_.image,record+14,2),word(machine_.image,record+16,2),
    word(machine_.image,0x6c61c),word(machine_.image,0x6c620),
    word(machine_.image,record,1),word(machine_.image,record+1,1),
    word(machine_.image,record+2,1),word(machine_.image,record+3,1),
    word(machine_.image,record+4,1),word(machine_.image,record+5,1),word(machine_.image,0x6c60c)};
}
std::array<std::uint8_t,50> PirateSession::highscores() const {
  std::array<std::uint8_t,50> result{};
  std::copy_n(machine_.image.begin()+0x6c542,50,result.begin());return result;
}
void PirateSession::set_highscores(const std::array<std::uint8_t,50>& records) {
  if(ticks_)throw std::runtime_error("Load Pirate highscores before the first tick");
  for(unsigned row=0;row<5;++row){
    for(unsigned c=0;c<6;++c){const auto b=records[row*10+c];if((b&15)>9||(b>>4)>9)throw std::runtime_error("Invalid Pirate score BCD");}
    if(records[row*10+9])throw std::runtime_error("Invalid Pirate initials terminator");
    for(unsigned c=6;c<9;++c){const auto ch=records[row*10+c];if(ch&&ch!=' '&&!(ch>='A'&&ch<='Z')&&!(ch>='0'&&ch<='9'))throw std::runtime_error("Invalid Pirate initials character");}
  }
  std::copy(records.begin(),records.end(),machine_.image.begin()+0x6c542);
}
void PirateSession::launch() {
  // Original Enter-down handler calls Pirate+40 before setting its one-shot latch.
  machine_.invoke(0x434160);machine_.wr(0x46c5fc,0xffffffff,4);
}
bool PirateSession::special_left() {
  if(mode_!=PirateTickMode::Full)throw std::runtime_error("Special action requires the full original table context");
  // Retail404a7c/404ab4: key-down is rejected only while Tilted. The
  // descriptor+4c callback itself guards the earned feature; no phase gate.
  if(machine_.rd(0x46b764,4))return false;
  machine_.invoke(0x4341dc);
  return true;
}
void PirateSession::flippers(bool left,bool right) {
  const auto edge=[&](bool down,unsigned side,std::uint32_t callback,std::uint32_t address){
    if(down&&(!machine_.rd(0x46c6ac,4)||machine_.rd(0x46b764,4)))return;
    const auto signed_edge=down?1u:0xffffffffu;
    const auto bits=machine_.rd(0x46c610,1);
    machine_.wr(0x46c610,down?(bits|side):(bits&~side),1);
    machine_.invoke(callback,signed_edge);
    machine_.wr(side==1?0x46c6d0:0x46c6d4,down?0xffffffff:0,4);
    if(!down||!machine_.rd(0x46c6c0,4)){
      machine_.wr(address,signed_edge,4);
      // Pirate graphics descriptor+1c is positive: right Shift also drives upper.
      if(side==2)machine_.wr(0x454b60,signed_edge,4);
    }
  };
  if(left!=left_){edge(left,1,0x434268,0x454b58);left_=left;}
  if(right!=right_){edge(right,2,0x434340,0x454b5c);right_=right;}
}
bool PirateSession::nudge(int direction) {
  if(direction < -1 || direction > 1)throw std::invalid_argument("Invalid Pirate nudge direction");
  if(mode_!=PirateTickMode::Full)throw std::runtime_error("Nudge requires the full original table context");
  if(!phase())return false;
  // Retail4049e3/404a25/404a67. Even after Tilt, the original accepts
  // waveform requests;405eec alone guards warning/Tilt accumulation.
  machine_.wr(direction?0x454aac:0x454af8,std::uint32_t(direction?direction:-1),4);
  machine_.invoke(0x405eec);
  return true;
}
std::array<std::uint32_t,18> PirateSession::nudge_state() const {
  constexpr std::array<std::uint32_t,17> addresses={0x454aac,0x454aa8,0x454ab0,0x454af8,0x454afc,
    0x46c600,0x46c604,0x46c4a4,0x46c5f8,0x46c5f4,0x46c6e4,0x46b764,
    0x46c6d0,0x46c6d4,0x454b58,0x454b5c,0x454b60};
  std::array<std::uint32_t,18> result{};
  for(unsigned i=0;i<addresses.size();++i)result[i]=word(machine_.image,addresses[i]-0x400000);
  result.back()=word(machine_.image,0x6c610,1);
  return result;
}
std::array<std::uint32_t,5> PirateSession::magnasaver_state() const {
  // Earned charge, active window, force-record type, lamp command, Tilt.
  return {word(machine_.image,0x6e536,2),word(machine_.image,0x6e552,2),
    word(machine_.image,0x6584c,2),word(machine_.image,0x6e450,1),
    word(machine_.image,0x6b764,4)};
}
void PirateSession::step() {
  if(mode_==PirateTickMode::Full)machine_.invoke(0x405234,std::uint32_t((ticks_+1)*5));
  else{machine_.invoke(0x409154);machine_.invoke(0x40950c);}
  ++ticks_;
  if(ticks_%4==0){
    if(lamps_enabled_)machine_.invoke(0x408da8);
    if(mode_==PirateTickMode::Full)machine_.invoke(0x408674); // Original render-owned integer ball compaction.
  }
}
void PirateSession::enable_lamps(bool enable) {
  if(enable&&mode_!=PirateTickMode::Full)throw std::runtime_error("Lamps require the full original table context");
  lamps_enabled_=enable;
}
void PirateSession::diagnostic_waypoint(const TableProfile& profile,unsigned layer,int x,int y,unsigned ball_index) {
  if(mode_!=PirateTickMode::Full||ball_index>=8||ball_index>=ball_count()||
      word(machine_.image,0x6c15c+100*ball_index+0x58,2)!=2)
    throw std::runtime_error("Diagnostic shot requires a free canonical Pirate ball");
  if(profile.dat_sha256!="6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6"||
      layer>=profile.layers.size()||x<0||x>=320||y<0||y>=600)
    throw std::runtime_error("Invalid diagnostic Pirate shot");
  MeanObject object;const auto current=ball(ball_index);std::copy(current.begin(),current.end(),object.bytes.begin());
  table_set_layer(object,profile,layer,0x1100000);
  for(const auto offset:{0,8})object.put32(offset,x*65536);
  for(const auto offset:{4,12})object.put32(offset,y*65536);
  object.put32(20,0);object.put32(24,0);
  std::copy(object.bytes.begin(),object.bytes.end(),machine_.image.begin()+0x6c15c+100*ball_index);
}
std::vector<std::uint8_t> PirateSession::rule_state() const {
  return {machine_.image.begin()+0x6e220,machine_.image.begin()+0x6e580};
}
std::vector<std::uint8_t> PirateSession::ball_pool_state() const {
  return {machine_.image.begin()+0x6c15c,machine_.image.begin()+0x6c47c};
}
std::vector<std::uint8_t> PirateSession::video_state() const {
  // Preserve original byte order and range order for oracle comparisons.
  std::vector<std::uint8_t> result;result.reserve(892);
  for(const auto& range:std::array<std::array<unsigned,2>,3>{{
      {0x6e0b4,0x6e220},{0x65970,0x65a80},{0x6c67c,0x6c77c}}})
    result.insert(result.end(),machine_.image.begin()+range[0],machine_.image.begin()+range[1]);
  return result;
}
std::vector<std::uint8_t> PirateSession::lamp_states() const {
  const auto table=word(machine_.image,0x6b74c);
  const auto count=word(machine_.image,0x6c6a4);
  if(count>256)throw std::runtime_error("Invalid original lamp count");
  std::vector<std::uint8_t> result;result.reserve(count*2);
  for(unsigned i=0;i<count;++i){
    const auto descriptor=word(machine_.image,table-0x400000+i*4);
    const auto state=word(machine_.image,descriptor-0x400000+8,2);
    result.push_back(state&255);result.push_back(state>>8);
  }
  return result;
}
std::array<std::uint8_t,100> PirateSession::ball(unsigned index) const {
  if(index>=8)throw std::out_of_range("Pirate ball index");
  const auto address=word(machine_.image,0x54b68+index*4);
  if(mode_==PirateTickMode::Full){
    if(address!=0x46c15c+index*100)throw std::out_of_range("Pirate canonical ball pool changed");
    std::array<std::uint8_t,100> state{};
    std::copy_n(machine_.image.begin()+address-0x400000,100,state.begin());return state;
  }
  if(address<0x1000000||address-0x1000000+100>machine_.runtime.size())
    throw std::out_of_range("Pirate ball pointer");
  std::array<std::uint8_t,100> state{};
  std::copy_n(machine_.runtime.begin()+address-0x1000000,100,state.begin());return state;
}
std::array<std::uint16_t,3> PirateSession::poses() const {
  return {std::uint16_t(word(machine_.image,0x6c786,2)),std::uint16_t(word(machine_.image,0x6c76c,2)),std::uint16_t(word(machine_.image,0x6c752,2))};
}
unsigned PirateSession::phase() const {return word(machine_.image,0x6c6ac);}
unsigned PirateSession::ball_count() const {return word(machine_.image,0x6c67c);}
std::array<std::uint32_t,11> PirateSession::timing_state() const {
  return {word(machine_.image,0x6c734),word(machine_.image,0x6c744),
    word(machine_.image,0x6c740),word(machine_.image,0x6c704),
    word(machine_.runtime,0x900c),word(machine_.image,0x6c6b4),
    word(machine_.image,0x6c6b8),phase(),word(machine_.image,0x6c68c),
    word(machine_.image,0x6e554,2),word(machine_.image,0x6e53a,2)};
}
std::array<std::uint8_t,1920> PirateSession::dmd_pixels() const {
  std::array<std::uint8_t,1920> pixels{};
  const auto address=word(machine_.image,0x6c47c);
  if(address<0x1000000||address-0x1000000+pixels.size()>machine_.runtime.size())
    throw std::out_of_range("Pirate DMD pointer");
  std::copy_n(machine_.runtime.begin()+address-0x1000000,pixels.size(),pixels.begin());
  for(auto level:pixels)if(level>3)throw std::runtime_error("Unsupported Pirate DMD intensity");
  return pixels;
}
std::array<std::uint8_t,4> PirateSession::dmd_palette_indices() const {
  // 404f09..404f15: returned descriptor+8 -> table-data descriptor+20.
  // 406137..406190 maps intensity bytes through these four palette indices.
  return {machine_.image.at(0x65844),machine_.image.at(0x65845),
    machine_.image.at(0x65846),machine_.image.at(0x65847)};
}
}
