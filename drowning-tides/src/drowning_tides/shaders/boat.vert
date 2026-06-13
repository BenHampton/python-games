#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_color;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec3 v_world;
out vec3 v_normal;
out vec3 v_color;

void main() {
    vec4 world = m_model * vec4(in_position, 1.0);
    v_world = world.xyz;
    v_normal = mat3(m_model) * in_normal;
    v_color = in_color;
    gl_Position = m_proj * m_view * world;
}
