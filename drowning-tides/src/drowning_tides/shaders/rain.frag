#version 330 core

in float v_along;
out vec4 frag_color;

uniform vec3 u_rain_color;
uniform float u_alpha;

void main() {
    // fade toward the trailing (top) end of the streak
    float a = u_alpha * mix(0.25, 1.0, v_along);
    frag_color = vec4(u_rain_color, a);
}
