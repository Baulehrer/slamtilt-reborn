#version 450
layout(location=0) in vec4 tint;
layout(location=1) in vec2 uv;
layout(location=0) out vec4 output_color;
layout(set=2,binding=0) uniform sampler2D source_image;
layout(set=3,binding=0,std140) uniform Params {vec4 params;};
void main(){
  if(params.w>0.5){
    vec3 c=texture(source_image,uv).rgb;
    float l=max(max(c.r,c.g),c.b);
    output_color=vec4(c*smoothstep(.38,.95,l),1);return;
  }
  vec2 d=params.xy;
  vec3 c=texture(source_image,uv).rgb*.227027;
  c+=(texture(source_image,uv+d*1.384615).rgb+texture(source_image,uv-d*1.384615).rgb)*.316216;
  c+=(texture(source_image,uv+d*3.230769).rgb+texture(source_image,uv-d*3.230769).rgb)*.070270;
  output_color=vec4(c,1);
}
