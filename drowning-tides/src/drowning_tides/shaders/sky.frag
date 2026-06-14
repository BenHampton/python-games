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

// weather / atmosphere
uniform float u_time;
uniform vec2 u_wind_dir;
uniform float u_cloud_cover;
uniform float u_storm;
uniform float u_lightning;
uniform float u_cloud_scale;
uniform float u_cloud_speed;
uniform vec3 u_cloud_lit;
uniform vec3 u_cloud_dark;
uniform vec3 u_cloud_storm;
uniform float u_aurora;
uniform vec3 u_aurora_a;
uniform vec3 u_aurora_b;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}

float vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
    float v = 0.0, amp = 0.5;
    for (int i = 0; i < 5; ++i) {
        v += amp * vnoise(p);
        p *= 2.02;
        amp *= 0.5;
    }
    return v;
}

void main() {
    vec4 world = m_inv_view_proj * vec4(v_ndc, 1.0, 1.0);
    vec3 wpos = world.xyz / world.w;
    vec3 dir = normalize(wpos - cam_pos);

    float t = clamp(dir.y, 0.0, 1.0);
    vec3 col = mix(horizon_color, top_color, pow(t, 0.55));
    float haze = smoothstep(0.0, 0.18, t);
    col = mix(fog_color, col, haze);

    // --- subtle cosmic aurora (night only) ---
    if (star_alpha > 0.1 && u_aurora > 0.001) {
        float band = smoothstep(0.12, 0.30, dir.y) * (1.0 - smoothstep(0.45, 0.80, dir.y));
        vec2 auv = vec2(atan(dir.z, dir.x) * 2.0, dir.y * 4.0);
        float a = pow(fbm(auv + vec2(u_time * 0.05, 0.0)), 2.0);
        vec3 acol = mix(u_aurora_a, u_aurora_b, fbm(auv * 0.5 - u_time * 0.03));
        col += acol * (a * band * u_aurora * star_alpha);
    }

    // --- stars ---
    if (star_alpha > 0.001 && dir.y > 0.0) {
        vec2 g = dir.xz / (dir.y + 0.25) * 120.0;
        float h = hash(floor(g));
        vec2 f = fract(g) - 0.5;
        float point = (1.0 - smoothstep(0.0, 0.09, length(f))) * step(0.985, h);
        point *= smoothstep(0.05, 0.35, dir.y);
        col += vec3(0.9, 0.92, 1.0) * point * star_alpha * 0.9;
    }

    // --- sun + moon ---
    float sd = max(dot(dir, sun_dir), 0.0);
    float sun_up = smoothstep(-0.05, 0.05, sun_dir.y);
    col += sun_color * 0.12 * pow(sd, 8.0) * (1.0 - haze * 0.6) * sun_up;
    col = mix(col, sun_color, smoothstep(0.980, 0.994, sd) * sun_up);
    float md = max(dot(dir, moon_dir), 0.0);
    float moon_up = smoothstep(-0.05, 0.05, moon_dir.y);
    col += moon_color * 0.08 * pow(md, 12.0) * (1.0 - haze * 0.6) * moon_up;
    col = mix(col, moon_color, smoothstep(0.988, 0.9964, md) * moon_up);

    // --- drifting clouds on the sky dome ---
    if (dir.y > 0.01) {
        vec2 cuv = dir.xz / max(dir.y, 0.10) * u_cloud_scale + u_wind_dir * u_time * u_cloud_speed;
        float d = fbm(cuv);
        float thresh = mix(0.78, 0.18, u_cloud_cover);
        float cov = smoothstep(thresh, thresh + 0.22, d);
        cov *= smoothstep(0.02, 0.18, dir.y);          // fade into the horizon haze
        float lit = smoothstep(thresh, thresh + 0.45, d);
        vec3 cloud = mix(u_cloud_dark, u_cloud_lit, lit);
        cloud += sun_color * 0.10 * pow(sd, 4.0) * sun_up;   // rim toward the sun
        cloud = mix(cloud, u_cloud_storm, u_storm);
        col = mix(col, cloud, cov);
    }

    // --- lightning: flash the sky/clouds (brighter where there's cloud cover) ---
    col += vec3(0.70, 0.78, 1.0) * u_lightning * (0.25 + 0.75 * u_cloud_cover);

    frag_color = vec4(col, 1.0);
}
