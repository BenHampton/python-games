#version 330 core

layout (location = 0) in vec2 in_position;

out vec2 v_ndc;

void main() {
    v_ndc = in_position;
    gl_Position = vec4(in_position, 1.0, 1.0);
}
