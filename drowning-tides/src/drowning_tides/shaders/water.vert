#version 330 core

layout (location = 0) in vec2 in_position;   // local patch coords (x, z)

uniform mat4 m_proj;
uniform mat4 m_view;
uniform vec2 u_center;        // patch centre (camera xz, snapped)

const int N_WAVES = 4;
uniform vec2 u_wave_dir[N_WAVES];
uniform float u_wave_k[N_WAVES];
uniform float u_wave_w[N_WAVES];
uniform float u_wave_amp[N_WAVES];
uniform float u_wave_q[N_WAVES];
uniform float u_time;
uniform vec2 u_shelter_center;   // town / home-island "main point" (xz)
uniform vec4 u_shelter;          // x=R0, y=R1, z=min gain, w=max gain

out vec3 v_world;
out vec3 v_normal;
out float v_view_z;   // positive view-space distance (for depth/thickness)

void main() {
    vec2 base = in_position + u_center;   // world xz before displacement

    float h = 0.0;
    vec2 horiz = vec2(0.0);
    float nx = 0.0, nz = 0.0, ny_sub = 0.0;

    for (int i = 0; i < N_WAVES; ++i) {
        vec2 d = u_wave_dir[i];
        float k = u_wave_k[i];
        float a = u_wave_amp[i];
        float q = u_wave_q[i];
        float phase = k * dot(d, base) - u_wave_w[i] * u_time;
        float c = cos(phase);
        float s = sin(phase);

        h += a * s;
        horiz += q * a * d * c;

        float wa = k * a;
        nx += d.x * wa * c;
        nz += d.y * wa * c;
        ny_sub += q * wa * s;
    }

    // rougher seas the further from the town (must match waves.py::shelter_gain)
    float g = u_shelter.z + (u_shelter.w - u_shelter.z)
              * smoothstep(u_shelter.x, u_shelter.y, distance(base, u_shelter_center));
    h *= g; horiz *= g; nx *= g; nz *= g; ny_sub *= g;

    vec3 world = vec3(base.x + horiz.x, h, base.y + horiz.y);
    v_world = world;
    v_normal = normalize(vec3(-nx, 1.0 - ny_sub, -nz));

    vec4 view = m_view * vec4(world, 1.0);
    v_view_z = -view.z;
    gl_Position = m_proj * view;
}
