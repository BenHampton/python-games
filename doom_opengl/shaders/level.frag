#version 330 core

out vec4 frag_color;

in vec2 uv;
flat in int tex_id;

uniform sampler2DArray u_texture_array_0;

void main() {
    vec3 tex_col = texture(u_texture_array_0, vec3(uv, tex_id)).rgb;

    frag_color = vec4(tex_col, 1.0);
}