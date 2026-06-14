#version 330 core

in vec2 v_uv;
out vec4 frag_color;

uniform sampler2D u_tex;
uniform vec2 u_dir;   // texel-scaled blur direction (horizontal or vertical)

void main() {
    float w0 = 0.227027, w1 = 0.194595, w2 = 0.121622, w3 = 0.054054, w4 = 0.016216;
    vec3 c = texture(u_tex, v_uv).rgb * w0;
    c += (texture(u_tex, v_uv + u_dir * 1.0).rgb + texture(u_tex, v_uv - u_dir * 1.0).rgb) * w1;
    c += (texture(u_tex, v_uv + u_dir * 2.0).rgb + texture(u_tex, v_uv - u_dir * 2.0).rgb) * w2;
    c += (texture(u_tex, v_uv + u_dir * 3.0).rgb + texture(u_tex, v_uv - u_dir * 3.0).rgb) * w3;
    c += (texture(u_tex, v_uv + u_dir * 4.0).rgb + texture(u_tex, v_uv - u_dir * 4.0).rgb) * w4;
    frag_color = vec4(c, 1.0);
}
