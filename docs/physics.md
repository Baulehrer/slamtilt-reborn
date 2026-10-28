# Physics — first-phase boundary

Status: UNKNOWN. No ball update routine or state layout has yet been demonstrated. No native approximation is claimed as original physics.

Windows full `0x40b720` reads object fields at unaligned offsets +2, +0xa, +0xc, +0xe, +0x10, +0x12 and shifts them arithmetically by 16. This establishes fixed-point-like coordinate extraction in a pixel/mask copying routine (width320), not physics. The unusual unaligned accesses may encode legacy big-endian structures; that remains unproven.

Highest-value next action: trace writes to screen-visible ball coordinates in the Mean demo, identify the per-frame state update, and capture deterministic initial/100-frame states. Then inspect collision references as an island. No fixed timestep, gravity, force or flipper coefficient has been established.
