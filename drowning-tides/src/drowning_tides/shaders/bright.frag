#version 330 core

in vec2 v_uv;
out vec4 frag_color;

uniform sampler2D u_scene;
uniform float u_threshold;

void main() {
    vec3 c = texture(u_scene, v_uv).rgb;
    float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
    float k = max(l - u_threshold, 0.0) / max(l, 1e-4);
    frag_color = vec4(c * k, 1.0);
}
