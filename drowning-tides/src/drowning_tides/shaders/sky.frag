#version 330 core

in vec2 v_ndc;
out vec4 frag_color;

uniform mat4 m_inv_view_proj;
uniform vec3 cam_pos;
uniform vec3 horizon_color;
uniform vec3 top_color;
uniform vec3 fog_color;
uniform vec3 sun_dir;
uniform vec3 moon_dir;
uniform vec3 sun_color;
uniform vec3 moon_color;
uniform float star_alpha;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}

void main() {
    vec4 world = m_inv_view_proj * vec4(v_ndc, 1.0, 1.0);
    vec3 wpos = world.xyz / world.w;
    vec3 dir = normalize(wpos - cam_pos);

    float t = clamp(dir.y, 0.0, 1.0);
    vec3 col = mix(horizon_color, top_color, pow(t, 0.55));

    // hazy band where sky meets the sea
    float haze = smoothstep(0.0, 0.18, t);
    col = mix(fog_color, col, haze);

    // stars fade in at night, denser overhead, gone at the horizon
    if (star_alpha > 0.001 && dir.y > 0.0) {
        vec2 g = dir.xz / (dir.y + 0.25) * 120.0;
        vec2 cell = floor(g);
        float h = hash(cell);
        float twinkle = step(0.985, h);
        vec2 f = fract(g) - 0.5;
        float point = (1.0 - smoothstep(0.0, 0.09, length(f))) * twinkle;
        point *= smoothstep(0.05, 0.35, dir.y);
        col += vec3(0.9, 0.92, 1.0) * point * star_alpha * 0.9;
    }

    // sun: soft glow + bright disc, only while above the horizon
    float sd = max(dot(dir, sun_dir), 0.0);
    float sun_up = smoothstep(-0.05, 0.05, sun_dir.y);
    float sun_glow = pow(sd, 8.0) * (1.0 - haze * 0.6);
    col += sun_color * 0.12 * sun_glow * sun_up;
    float sun_disc = smoothstep(1.0 - 0.020, 1.0 - 0.020 * 0.3, sd);
    col = mix(col, sun_color, sun_disc * sun_up);

    // moon: pale glow + disc at night
    float md = max(dot(dir, moon_dir), 0.0);
    float moon_up = smoothstep(-0.05, 0.05, moon_dir.y);
    float moon_glow = pow(md, 12.0) * (1.0 - haze * 0.6);
    col += moon_color * 0.08 * moon_glow * moon_up;
    float moon_disc = smoothstep(1.0 - 0.012, 1.0 - 0.012 * 0.3, md);
    col = mix(col, moon_color, moon_disc * moon_up);

    frag_color = vec4(col, 1.0);
}
