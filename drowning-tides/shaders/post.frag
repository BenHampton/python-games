#version 330 core

in vec2 v_uv;
out vec4 frag_color;

uniform sampler2D u_scene;
uniform vec2 u_texel;     // 1.0 / resolution
uniform float time;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
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

    // grade toward a cool, dark maritime palette
    col = pow(col, vec3(1.05, 1.0, 0.95));            // gentle channel curve
    col *= vec3(0.95, 1.0, 1.04);                     // cool tint
    col = (col - 0.5) * 1.08 + 0.5;                   // mild contrast

    // soft vignette
    vec2 d = v_uv - 0.5;
    float vig = smoothstep(0.85, 0.35, length(d));
    col *= mix(0.78, 1.0, vig);

    // faint canvas grain
    float grain = (hash(v_uv * 1024.0 + time) - 0.5) * 0.03;
    col += grain;

    frag_color = vec4(clamp(col, 0.0, 1.0), 1.0);
}
