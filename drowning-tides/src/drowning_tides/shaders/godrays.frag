#version 330 core

in vec2 v_uv;
out vec4 frag_color;

uniform sampler2D u_scene;
uniform vec2 u_sun_uv;     // sun screen position
uniform int u_samples;
uniform float u_decay;
uniform float u_weight;
uniform float u_intensity; // 0 -> god rays off (sun down / overcast / behind camera)

void main() {
    if (u_intensity <= 0.0) {
        frag_color = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    vec2 delta = (v_uv - u_sun_uv) / float(u_samples);
    vec2 uv = v_uv;
    float illum = 1.0;
    vec3 acc = vec3(0.0);
    for (int i = 0; i < u_samples; ++i) {
        uv -= delta;
        vec3 s = texture(u_scene, uv).rgb;
        float lum = max(max(s.r, s.g), s.b);   // bright sky contributes; dark geometry blocks
        acc += s * smoothstep(0.3, 0.9, lum) * illum;
        illum *= u_decay;
    }
    acc *= u_weight / float(u_samples) * u_intensity;
    frag_color = vec4(acc, 1.0);
}
