#include "assets/table_profile.h"
#include "mean_step.h"
#include "mean_material_bundle.h"
#include <cstring>
#include <stdexcept>

namespace slam {
namespace {
std::int32_t signed_bits(std::uint32_t value) {
  std::int32_t result;
  std::memcpy(&result, &value, sizeof(result));
  return result;
}
std::int32_t add(std::int32_t a, std::int32_t b) {
  return signed_bits(static_cast<std::uint32_t>(a) +
                     static_cast<std::uint32_t>(b));
}
std::int32_t sub(std::int32_t a, std::int32_t b) {
  return signed_bits(static_cast<std::uint32_t>(a) -
                     static_cast<std::uint32_t>(b));
}
std::int32_t sar(std::int32_t value, unsigned shift) {
  const auto bits = static_cast<std::uint32_t>(value);
  return signed_bits((bits >> shift) |
                     (value < 0 ? (~std::uint32_t{0} << (32 - shift)) : 0));
}
std::int16_t word(const std::vector<std::uint8_t> &bytes, std::size_t offset) {
  if (offset > bytes.size() || bytes.size() - offset < 2)
    throw std::runtime_error("Original Mean lookup data truncated");
  const auto bits = static_cast<std::uint16_t>(
      bytes[offset] | (std::uint16_t(bytes[offset + 1]) << 8));
  std::int16_t value;
  std::memcpy(&value, &bits, sizeof(value));
  return value;
}
} // namespace
std::uint16_t MeanObject::u16(std::size_t offset) const {
  if (offset > bytes.size() || bytes.size() - offset < 2)
    throw std::out_of_range("Mean object field");
  return bytes[offset] | (std::uint16_t(bytes[offset + 1]) << 8);
}
std::int32_t MeanObject::i32(std::size_t offset) const {
  if (offset > bytes.size() || bytes.size() - offset < 4)
    throw std::out_of_range("Mean object field");
  return signed_bits(std::uint32_t(u16(offset)) |
                     (std::uint32_t(u16(offset + 2)) << 16));
}
void MeanObject::put16(std::size_t offset, std::uint16_t value) {
  if (offset > bytes.size() || bytes.size() - offset < 2)
    throw std::out_of_range("Mean object field");
  bytes[offset] = value & 255;
  bytes[offset + 1] = value >> 8;
}
void MeanObject::put32(std::size_t offset, std::int32_t value) {
  if (offset > bytes.size() || bytes.size() - offset < 4)
    throw std::out_of_range("Mean object field");
  put16(offset, static_cast<std::uint32_t>(value) & 65535);
  put16(offset + 2, static_cast<std::uint32_t>(value) >> 16);
}
bool MeanCollisionBits::sample(std::int32_t x, std::int32_t y,
                               unsigned plane) const {
  if (x < 0 || x >= 320 || y < 0 || y >= 616 || plane > extra_planes)
    throw std::out_of_range("Mean collision coordinate");
  return sample_linear(x,y,plane);
}
bool MeanCollisionBits::sample_linear(std::int32_t x,std::int32_t y,unsigned plane) const {
  if(plane>extra_planes)throw std::out_of_range("Mean collision plane");
  const auto offset=std::int64_t(hit_offset)+std::int64_t(plane)*std::int64_t(stride)+std::int64_t(y)*40+(x>=0?std::int64_t(x)/8:-((-std::int64_t(x)+7)/8));
  if(offset<0 || offset>=std::int64_t(dat.size()))throw std::out_of_range("Mean collision DAT address");
  return (dat[std::size_t(offset)] & (128 >> (std::uint32_t(x)&7)))!=0;
}
std::uint16_t MeanCollisionBits::extra_plane_mask(std::int32_t x,
                                                  std::int32_t y) const {
  std::uint16_t mask = 0;
  for (unsigned plane = 1; plane <= extra_planes; ++plane)
    if (sample(x, y, plane))
      mask |= 1 << (plane - 1);
  return mask;
}
std::uint16_t MeanCollisionBits::extra_plane_mask_linear(std::int32_t x,std::int32_t y) const {
  std::uint16_t mask=0;
  for(unsigned plane=1;plane<=extra_planes;++plane)if(sample_linear(x,y,plane))mask|=1<<(plane-1);
  return mask;
}

void mean_set_layer(MeanObject &ball, unsigned layer, std::uint32_t base) {
  table_set_layer(ball, mean_table_profile(), layer, base);
}
void mean_advance_ball(std::uint16_t &number, std::uint16_t &extra) {
  if (static_cast<std::int16_t>(extra) > 0)
    --extra;
  else
    ++number;
}
void mean_reset_ball(MeanObject &ball) {
  ball.put16(0x22, 0);
  ball.put16(0x2a, 0);
  ball.put16(0x28, 40);
  ball.put16(0x38, 65535);
  ball.put16(0x3a, 65535);
  ball.put16(0x5c, 1);
  ball.put16(0x1c, 0);
  ball.put32(0x60, 3);
  ball.put32(0, 0x11f0000);
  ball.put32(4, 0x23b0000);
  ball.put32(0x14, 0);
  ball.put32(0x18, 0);
  ball.put16(0x48, 0);
  ball.put32(8, ball.i32(0));
  ball.put32(12, ball.i32(4));
  // Caller408943 assigns state0 after initializer returns.
  ball.put16(0x58, 0);
}
void mean_initialize_ball(MeanObject &ball, std::uint32_t dat_base) {
  // Original41ab94 restores geometry/render descriptors without clearing the record.
  mean_set_layer(ball, 0, dat_base);
  mean_reset_ball(ball);
}
bool mean_launch_kick(MeanObject &ball, bool pressed) {
  if (ball.i32(0) <= 0x12e0000 || ball.i32(4) <= 0x2440000 || !pressed)
    return false;
  ball.put32(0x18, -0x40000);
  return true;
}
bool mean_lower_switch(const MeanObject &ball) {
  return ball.i32(4) >= 0x1c20000;
}
std::uint32_t mean_lower_switch_points(const MeanObject &ball) {
  return mean_lower_switch(ball) ? 25000 : 0;
}
void mean_integrate(MeanObject &ball) {
  ball.put32(8, ball.i32(0));
  ball.put32(12, ball.i32(4));
  ball.put32(0, add(ball.i32(0), ball.i32(0x14)));
  ball.put32(4, add(ball.i32(4), ball.i32(0x18)));
}
bool mean_free_velocity(MeanObject &ball, const MeanLookup &lookup) {
  if (ball.u16(0x22) != 0) {
    if (lookup.field_43e728.size() != 2050)
      return false;
    const auto target_x = static_cast<std::int16_t>(ball.u16(0x24));
    const auto target_y = static_cast<std::int16_t>(ball.u16(0x26));
    auto dx = target_x - sar(ball.i32(0), 16);
    auto dy = target_y - sar(ball.i32(4), 16);
    if (static_cast<std::int16_t>(ball.u16(0x22)) < 0) {
      dx = -dx;
      dy = -dy;
    }
    const auto ax = dx < 0 ? -dx : dx, ay = dy < 0 ? -dy : dy;
    if (!ax && !ay)
      return false;
    const auto angle =
        ax < ay ? 1024 - word(lookup.field_43e728, ((ax * 1024) / ay) * 2)
                : word(lookup.field_43e728, ((ay * 1024) / ax) * 2);
    ball.put16(0x2a, dy < 0 ? (dx < 0 ? 2048 + angle : 4096 - angle)
                            : (dx < 0 ? 2048 - angle : angle));
  }
  const auto index = sar(ball.i32(0x28), 16);
  if (index < 0)
    throw std::out_of_range("Mean lookup index");
  const auto amount = sar(ball.i32(0x26), 16);
  const auto component_x = word(lookup.field_43e764, std::size_t(index) * 2);
  const auto component_y =
      word(lookup.field_43e764, std::size_t(index) * 2 + 0x800);
  const auto dx = sar(signed_bits(std::uint32_t(std::int32_t(component_x)) *
                                  std::uint32_t(amount)),
                      10);
  const auto dy = sar(signed_bits(std::uint32_t(std::int32_t(component_y)) *
                                  std::uint32_t(amount)),
                      10);
  ball.put32(0x14, sub(ball.i32(0x14), dx));
  ball.put32(0x18, add(ball.i32(0x18), dy));
  return true;
}
bool mean_wall_response(MeanObject &ball, const MeanLookup &lookup,
                        std::int32_t field_43e724, std::int32_t field_43e564,
                        MeanContactEvent *event,
                        MeanMaterialBundleState *material_state) {
  // 409c7c high word at+48 selects callback; 409c91 high word at+3c
  // selects the material case inside the Mean callback41e00c.
  const auto selected_callback = sar(ball.i32(0x46), 16);
  const auto material = sar(ball.i32(0x3a), 16);
  if (selected_callback < 0 || selected_callback > 4 || material < 0 ||
      (selected_callback == 0 && material > 7))
    return false;
  const auto angle = sar(ball.i32(0x1c), 16);
  if (angle < 0 || angle > 0xfff)
    throw std::out_of_range("Mean response angle");
  const auto multiply = [](std::int32_t a, std::int32_t b) {
    return signed_bits(std::uint32_t(a) * std::uint32_t(b));
  };
  const auto component_s = word(lookup.field_43e764, std::size_t(angle) * 2);
  const auto component_c = word(lookup.field_43e744, std::size_t(angle) * 2);
  const auto vx = sar(add(ball.i32(0x14), field_43e724), 8);
  const auto vy = sar(add(ball.i32(0x18), field_43e564), 8);
  auto tangent = sub(sar(multiply(component_s, vx), 14),
                     sar(multiply(component_c, vy), 14));
  auto normal = add(sar(multiply(component_c, vx), 14),
                    sar(multiply(component_s, vy), 14));
  if (selected_callback >= 3) {
    normal = sar(sub(0, multiply(normal, 16)), 8);
  } else if (selected_callback == 2) {
    normal = material > 2
                 ? 0
                 : sar(sub(0, multiply(normal, material == 0 ? 32 : 16)), 8);
  } else if (selected_callback == 1) {
    const bool bottom = ball.i32(0) > 0x1270000 && ball.i32(4) >= 0x2460000;
    const int factor = material == 1 ? 8 : bottom ? 80 : 16;
    normal = material > 1 ? 0 : sar(sub(0, multiply(normal, factor)), 8);
    if (material == 1) {
      tangent = 0;
      mean_set_layer(ball, 0, std::uint32_t(ball.i32(0x40)) - 0xbf9d6);
      ball.put16(0x22, 0);
      ball.put16(0x2a, 0);
      ball.put16(0x5c, 0);
      ball.put16(0x1c, 0);
      ball.put32(0x60, 0xaa1);
      ball.put16(0x28, 40);
    }
  } else {
    if (material >= 6) {
      MeanMaterialBundleState initial_state;
      bool services = false;
      mean_material_bundle(ball, material, normal, tangent,
                           material_state ? *material_state : initial_state,
                           services);
      if (event && services)
        event->sample_descriptor = 0x437cf0;
    } else if (material == 5) {
      // 41e255..41e266: base target response; additional rule awards external.
      normal = sar(sub(0, multiply(normal, 64)), 8);
      if (event) {
        event->points = 50000;
        event->material5_rules = true;
      }
    } else if (material == 3 || (material == 4 && normal > 64)) {
      // Human-mode branches41e092 /41e154; mode-specific bonus is external.
      normal = material == 3 ? -256 : -416;
      if (event)
        event->sample_descriptor = 0x437d14;
      if (event) {
        event->points = 0x1aae;
        event->field_438b_state = material == 3                ? 0x438b38
                                  : ball.i32(0) <= 160 * 65536 ? 0x438b08
                                                               : 0x438b14;
      }
    } else {
      const std::int32_t factor = material == 1 ? 32 : material == 2 ? 200 : 80;
      normal = sar(sub(0, multiply(normal, factor)), 8);
      if (material == 2 && normal < -256)
        normal = -256;
    }
  }
  if (normal > 0)
    return true; // 409ca1 skips velocity writes.
  if (angle < 0x800) {
    tangent = sub(tangent, sar(multiply(component_c, 5), 14));
    normal = add(normal, sar(multiply(component_s, 5), 14));
    if (normal > 0)
      normal = 0;
  }
  const auto inverse = (-angle) & 0xfff;
  const auto inverse_s = word(lookup.field_43e764, std::size_t(inverse) * 2);
  const auto inverse_c = word(lookup.field_43e744, std::size_t(inverse) * 2);
  const auto out_x = sub(sar(multiply(normal, inverse_c), 14),
                         sar(multiply(tangent, inverse_s), 14));
  const auto out_y = sub(0, add(sar(multiply(tangent, inverse_c), 14),
                                sar(multiply(normal, inverse_s), 14)));
  ball.put32(0x14, sub(signed_bits(std::uint32_t(out_x) << 8), field_43e724));
  ball.put32(0x18, sub(signed_bits(std::uint32_t(out_y) << 8), field_43e564));
  return true;
}
unsigned mean_separate(MeanObject &ball, const MeanCollisionBits &bits,
                       std::int16_t table_43e744_value,
                       std::int16_t table_43e764_value,
                       std::int32_t field_43e71c, std::int32_t field_43e410) {
  for (unsigned count = 1; count <= 16; ++count) {
    ball.put32(0, sub(ball.i32(0), table_43e744_value));
    ball.put32(4, sub(ball.i32(4), table_43e764_value));
    if (!bits.sample_linear(sar(add(ball.i32(0), field_43e71c), 16),
                     sar(add(ball.i32(4), field_43e410), 16)))
      return count;
  }
  return 16;
}
} // namespace slam
