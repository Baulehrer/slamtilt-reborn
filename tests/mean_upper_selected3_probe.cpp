#include "physics/mean_upper_capture.h"
#include <nlohmann/json.hpp>
#include <iostream>
int main(){slam::MeanObject b;b.put16(0x58,3);b.put16(0x5a,1);slam::MeanUpperCaptureState s;s.field_43f394=-1;s.field_43f1e6=3;nlohmann::json out=nlohmann::json::array();for(int i=0;i<200;++i){slam::MeanUpperCaptureEvent e;if(!slam::mean_upper_capture_tick(b,s,e))return 2;if(i%4==3&&s.field_438b5c[0]>=0)--s.field_438b5c[0];out.push_back({{"timer",s.field_43f36a},{"gate",s.field_43f364},{"field394",s.field_43f394},{"field1f2",s.field_43f1f2},{"mode",s.table_mode},{"slot1",s.field_438b5c},{"score",e.score_request},{"release",e.release_requested},{"start",e.selected3_start_requested}});if(e.release_requested)break;}std::cout<<out.dump();}
