#version 330 core

layout (location = 0) in float in_along;     // 0 = top, 1 = bottom of the streak
layout (location = 1) in vec3 in_offset;     // per-instance base offset in the box

uniform mat4 m_proj;
uniform mat4 m_view;
uniform vec3 u_cam_center;
uniform vec3 u_box;          // half-extents of the spawn volume
uniform vec2 u_wind_vel;     // horizontal drift velocity (xz)
uniform float u_fall;        // downward speed
uniform float u_streak_len;
uniform float u_time;

out float v_along;

void main() {
    // animate the drop, then wrap it back inside the box
    vec3 p = in_offset;
    p.x += u_wind_vel.x * u_time;
    p.z += u_wind_vel.y * u_time;
    p.y -= u_fall * u_time;
    p = mod(p + u_box, 2.0 * u_box) - u_box;

    vec3 base = u_cam_center + p;

    // orient the streak along its velocity vector
    vec3 vdir = normalize(vec3(u_wind_vel.x, -u_fall, u_wind_vel.y));
    vec3 world = base - vdir * (u_streak_len * in_along);

    v_along = in_along;
    gl_Position = m_proj * m_view * vec4(world, 1.0);
}
