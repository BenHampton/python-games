#version 330 core

in vec3 v_world;
in vec3 v_normal;
in vec3 v_color;
out vec4 frag_color;

uniform vec3 cam_pos;
uniform vec3 fog_color;
uniform vec3 sun_dir;
uniform float sun_strength;
uniform float fog_near;
uniform float fog_far;

float hash(vec3 p) {
    p = fract(p * 0.3183099 + 0.1);
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float vnoise(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float n000 = hash(i + vec3(0, 0, 0)), n100 = hash(i + vec3(1, 0, 0));
    float n010 = hash(i + vec3(0, 1, 0)), n110 = hash(i + vec3(1, 1, 0));
    float n001 = hash(i + vec3(0, 0, 1)), n101 = hash(i + vec3(1, 0, 1));
    float n011 = hash(i + vec3(0, 1, 1)), n111 = hash(i + vec3(1, 1, 1));
    return mix(mix(mix(n000, n100, f.x), mix(n010, n110, f.x), f.y),
               mix(mix(n001, n101, f.x), mix(n011, n111, f.x), f.y), f.z);
}

void main() {
    vec3 N = normalize(v_normal);
    vec3 V = normalize(cam_pos - v_world);

    // procedural surface detail: break up the flat vertex colour like a coarse texture
    float n = vnoise(v_world * 0.6) * 0.6 + vnoise(v_world * 2.3) * 0.4;
    vec3 albedo = v_color * (0.82 + 0.36 * n);

    // flat-shaded low-poly lighting, moody ambient that dims with the storm
    float diff = max(dot(N, sun_dir), 0.0);
    vec3 ambient = vec3(0.22, 0.26, 0.30) * (0.55 + 0.45 * sun_strength);
    vec3 sun = vec3(0.85, 0.80, 0.70) * sun_strength;
    vec3 col = albedo * (ambient + diff * sun);

    // subtle cool rim to lift the silhouette off the dark sea
    float rim = pow(1.0 - max(dot(N, V), 0.0), 3.0);
    col += vec3(0.10, 0.14, 0.16) * rim;

    float dist = length(cam_pos - v_world);
    float fogf = clamp((dist - fog_near) / (fog_far - fog_near), 0.0, 1.0);
    col = mix(col, fog_color, fogf);

    frag_color = vec4(col, 1.0);
}
