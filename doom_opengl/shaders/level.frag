#version 330 core

out vec4 frag_color;

in vec2 uv;
in float shading;
flat in int tex_id;

const vec3 gamma = vec3(2.2);
const vec3 inv_gamma = 1 / gamma;

uniform sampler2DArray u_texture_array_0;

void main() {
    vec3 tex_col = texture(u_texture_array_0, vec3(uv, tex_id)).rgb;
    tex_col = pow(tex_col, gamma);

    tex_col *= shading;

    tex_col = pow(tex_col, inv_gamma);
    frag_color = vec4(tex_col, 1.0);
}