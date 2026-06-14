#version 330 core

out vec4 frag_color;

uniform vec3 u_color;
uniform float u_alpha;

void main() {
    // bright (HDR) so the bloom pass makes the bolt glow
    frag_color = vec4(u_color * (1.0 + 3.0 * u_alpha), u_alpha);
}
