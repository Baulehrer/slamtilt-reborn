#version 450
layout(location=0) in vec4 tint;
layout(location=1) in vec2 uv;
layout(location=0) out vec4 output_color;
layout(set=2,binding=0) uniform sampler2D source_image;
layout(set=2,binding=1) uniform sampler2D glow_image;
layout(set=3,binding=0,std140) uniform Params {
  vec4 shape; // source pixel size, output width/height
  vec4 light; // strength, bloom, sharpness, saturation
  vec4 crt;   // scanlines, mask, curvature, color fringe
  vec4 flags; // clean scaling, dmd, unused
};
vec2 clean_uv(vec2 v){
  vec2 size=1./shape.xy;
  vec2 p=v*size;vec2 cell=floor(p);
  // Sharp bilinear scaling: flat texel interiors, a one-output-pixel transition.
  vec2 scale=max(vec2(1),shape.zw*shape.xy);
  vec2 offset=fract(p)-.5;
  vec2 region=.5-.5/scale;
  vec2 fraction=(offset-clamp(offset,-region,region))*scale+.5;
  return (cell+fraction)*shape.xy;
}
void main(){
  vec2 p=uv*2.-1.;
  vec2 bent=p*(1.+crt.z*dot(p,p)*.35);
  vec2 v=mix(uv,bent*.5+.5,light.x);
  if(any(lessThan(v,vec2(0)))||any(greaterThan(v,vec2(1)))){output_color=vec4(0,0,0,1);return;}
  vec2 sample_uv=flags.x>.5?clean_uv(v):v;
  vec3 original=texture(source_image,v).rgb;
  vec3 color=texture(source_image,sample_uv).rgb;
  vec2 dx=vec2(shape.x,0),dy=vec2(0,shape.y);
  vec3 nearby=(texture(source_image,sample_uv+dx).rgb+texture(source_image,sample_uv-dx).rgb+texture(source_image,sample_uv+dy).rgb+texture(source_image,sample_uv-dy).rgb)*.25;
  // Limit sharpening to avoid ringing around the ball and thin geometry.
  color+=clamp(color-nearby,vec3(-.12),vec3(.12))*light.z;
  if(crt.w>0.){
    vec2 shift=vec2(crt.w/max(shape.z,1.),0);
    color.r=texture(source_image,sample_uv+shift).r;
    color.b=texture(source_image,sample_uv-shift).b;
  }
  float l=dot(color,vec3(.2126,.7152,.0722));color=mix(vec3(l),color,light.w);
  if(light.y>0.)color+=texture(glow_image,v).rgb*light.y;
  float scan=.5+.5*cos(v.y/shape.y*6.2831853);
  color*=1.-crt.x*scan*.65;
  float column=mod(floor(gl_FragCoord.x),3.);
  vec3 mask_color=column<1.?vec3(1.,.72,.72):column<2.?vec3(.72,1.,.72):vec3(.72,.72,1.);
  color*=mix(vec3(1),mask_color,crt.y);
  color*=1.-crt.z*.4*dot(p,p);
  output_color=vec4(clamp(mix(original,color,light.x),0.,1.),1)*tint;
}
