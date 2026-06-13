#version 330 core

in vec2 v_ndc;
out vec4 frag_color;

uniform mat4 m_inv_view_proj;
uniform vec3 cam_pos;
uniform vec3 horizon_color;
uniform vec3 top_color;
uniform vec3 fog_color;
uniform vec3 sun_dir;

void main() {
    vec4 world = m_inv_view_proj * vec4(v_ndc, 1.0, 1.0);
    vec3 wpos = world.xyz / world.w;
    vec3 dir = normalize(wpos - cam_pos);

    float t = clamp(dir.y, 0.0, 1.0);
    vec3 col = mix(horizon_color, top_color, pow(t, 0.55));

    // hazy band where sky meets the sea
    float haze = smoothstep(0.0, 0.18, t);
    col = mix(fog_color, col, haze);

    // faint glow toward the key light low on the horizon
    float glow = pow(max(dot(dir, sun_dir), 0.0), 8.0) * (1.0 - haze * 0.6);
    col += vec3(0.10, 0.09, 0.07) * glow;

    frag_color = vec4(col, 1.0);
}
