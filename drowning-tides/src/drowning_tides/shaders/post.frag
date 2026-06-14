#version 330 core

in vec2 v_uv;
out vec4 frag_color;

uniform sampler2D u_scene;
uniform sampler2D u_bloom;
uniform sampler2D u_godrays;
uniform vec2 u_texel;     // 1.0 / resolution
uniform float time;
uniform float u_bloom_intensity;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}

// ACES filmic tonemap (Narkowicz approximation)
vec3 aces(vec3 x) {
    return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
}

void main() {
    // painterly smear: jittered taps averaged to break crisp edges into strokes
    float ang = hash(v_uv * 512.0) * 6.2831853;
    vec2 jit = vec2(cos(ang), sin(ang)) * u_texel * 1.6;

    vec3 col = texture(u_scene, v_uv).rgb * 0.40;
    col += texture(u_scene, v_uv + jit).rgb * 0.15;
    col += texture(u_scene, v_uv - jit).rgb * 0.15;
    col += texture(u_scene, v_uv + jit.yx * vec2(1.0, -1.0)).rgb * 0.15;
    col += texture(u_scene, v_uv + jit.yx * vec2(-1.0, 1.0)).rgb * 0.15;

    // additive bloom (soft glow on bright water/sky/glints) + god-ray shafts
    col += texture(u_bloom, v_uv).rgb * u_bloom_intensity;
    col += texture(u_godrays, v_uv).rgb;

    // filmic tonemap brings the HDR scene + bloom back into range
    col = aces(col);

    // muted maritime grade: slight desaturation + teal-shadow / warm-highlight split tone
    float l = dot(col, vec3(0.299, 0.587, 0.114));
    col = mix(vec3(l), col, 0.85);
    vec3 shadow_tint = vec3(0.92, 1.00, 1.05);
    vec3 highlight_tint = vec3(1.05, 1.00, 0.94);
    col *= mix(shadow_tint, highlight_tint, smoothstep(0.2, 0.8, l));
    col = (col - 0.5) * 1.06 + 0.5;             // mild contrast

    // soft vignette
    vec2 d = v_uv - 0.5;
    col *= mix(0.74, 1.0, smoothstep(0.9, 0.32, length(d)));

    // faint canvas grain
    col += (hash(v_uv * 1024.0 + time) - 0.5) * 0.025;

    frag_color = vec4(clamp(col, 0.0, 1.0), 1.0);
}
