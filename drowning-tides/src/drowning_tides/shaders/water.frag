#version 330 core

in vec3 v_world;
in vec3 v_normal;
out vec4 frag_color;

uniform vec3 cam_pos;
uniform vec3 water_color;
uniform vec3 water_color_deep;
uniform vec3 fog_color;
uniform vec3 light_dir;     // key light (sun by day, moon by night), points toward the light
uniform vec3 light_color;   // warm by day, cold by night
uniform vec3 sky_color;     // current horizon colour, reflected by the surface
uniform float sun_strength;
uniform float fog_near;
uniform float fog_far;
uniform float storm_intensity;
uniform float time;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void main() {
    vec3 N = normalize(v_normal);
    vec3 V = normalize(cam_pos - v_world);
    float dist = length(cam_pos - v_world);

    // brush-stroke variation
    vec2 uv = v_world.xz * 0.04;
    float n = noise(uv + vec2(time * 0.05, time * 0.03)) * 0.6
            + noise(uv * 2.7 - time * 0.02) * 0.4;

    // wave-facing term darkens troughs, lightens crests/foam on the slopes
    float crest = clamp(v_world.y * 0.6 + 0.5, 0.0, 1.0);
    vec3 col = mix(water_color_deep, water_color, n * 0.5 + crest * 0.5);

    // diffuse from the (now real) surface normal, lit by the day/night key light
    float diff = max(dot(N, light_dir), 0.0);
    col *= (0.55 + 0.45 * diff) * (0.5 + 0.5 * sun_strength);

    // sun/moon glint: a specular trail toward the light, sharper as the storm builds
    vec3 H = normalize(light_dir + V);
    float shininess = mix(60.0, 200.0, storm_intensity);
    float spec = pow(max(dot(N, H), 0.0), shininess);
    col += light_color * spec * (0.25 + 0.75 * sun_strength);

    // whitecaps: foam on the steepest crests, mostly during storms but a touch always
    float foam = smoothstep(0.8, 1.25, v_world.y / 1.2) * (0.15 + 0.85 * storm_intensity);
    foam *= 0.5 + 0.5 * n;   // break it up so it reads as flecks, not a sheet
    col = mix(col, vec3(0.55, 0.60, 0.62), clamp(foam, 0.0, 1.0) * 0.3);

    // fresnel: grazing angles reflect the sky/horizon colour so water shifts with the day
    float fres = pow(1.0 - max(dot(N, V), 0.0), 4.0);
    col = mix(col, sky_color, fres * 0.5);

    // distance fog
    float fogf = clamp((dist - fog_near) / (fog_far - fog_near), 0.0, 1.0);
    col = mix(col, fog_color, fogf);

    frag_color = vec4(col, 1.0);
}
