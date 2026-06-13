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

void main() {
    vec3 N = normalize(v_normal);
    vec3 V = normalize(cam_pos - v_world);

    // flat-shaded low-poly lighting, moody ambient that dims with the storm
    float diff = max(dot(N, sun_dir), 0.0);
    vec3 ambient = vec3(0.22, 0.26, 0.30) * (0.55 + 0.45 * sun_strength);
    vec3 sun = vec3(0.85, 0.80, 0.70) * sun_strength;
    vec3 col = v_color * (ambient + diff * sun);

    // subtle cool rim to lift the silhouette off the dark sea
    float rim = pow(1.0 - max(dot(N, V), 0.0), 3.0);
    col += vec3(0.10, 0.14, 0.16) * rim;

    float dist = length(cam_pos - v_world);
    float fogf = clamp((dist - fog_near) / (fog_far - fog_near), 0.0, 1.0);
    col = mix(col, fog_color, fogf);

    frag_color = vec4(col, 1.0);
}
