#version 330 core

in vec3 v_world;
in vec3 v_normal;
in float v_view_z;
out vec4 frag_color;

uniform vec3 cam_pos;
uniform vec3 water_color;
uniform vec3 water_color_deep;
uniform vec3 fog_color;
uniform vec3 light_dir;     // key light (sun by day, moon by night), points toward the light
uniform vec3 light_color;   // warm by day, cold by night
uniform vec3 sky_color;     // current horizon colour
uniform vec3 sky_top;       // current zenith colour (for the reflection gradient)
uniform float sun_strength;
uniform float fog_near;
uniform float fog_far;
uniform float storm_intensity;
uniform float time;

// scene behind the water (for refraction + depth-based transparency)
uniform sampler2D u_scene;
uniform sampler2D u_depth;
uniform vec2 u_resolution;
uniform float u_near;
uniform float u_far;
uniform float u_refraction;
uniform float u_clarity;      // absorption k (bigger -> sea gets opaque sooner with depth)
uniform vec3 u_absorb;        // underwater tint applied to the seabed seen through the water
uniform float u_detail;       // micro-ripple normal strength
uniform float u_detail_scale;
uniform float u_sun_reflect_shininess;

// turquoise shallow-water shelf near islands
uniform int u_island_count;
uniform vec2 u_island_xz[24];
uniform float u_island_radius[24];
uniform vec3 u_shallow_color;
uniform float u_shallow_band;

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

float ripple(vec2 p, vec2 flow) {
    return noise(p + flow) + 0.5 * noise(p * 2.3 - flow * 1.7);
}

float linear_depth(float d) {
    float z = d * 2.0 - 1.0;
    return (2.0 * u_near * u_far) / (u_far + u_near - z * (u_far - u_near));
}

void main() {
    vec3 N = normalize(v_normal);
    vec3 V = normalize(cam_pos - v_world);
    float dist = length(cam_pos - v_world);

    // --- see-through shallows: depth-based transparency, discard where occluded ---
    vec2 suv = gl_FragCoord.xy / u_resolution;
    float scene_z = linear_depth(texture(u_depth, suv).r);
    float thickness = scene_z - v_view_z;
    if (thickness <= 0.03) discard;   // something opaque is in front of the water here

    // --- micro-ripple detail normals (sun glitter); fade out with distance ---
    float detail_fade = clamp(1.0 - dist / 220.0, 0.0, 1.0);
    if (detail_fade > 0.0) {
        vec2 p = v_world.xz * u_detail_scale;
        vec2 flow = vec2(time * 0.6, time * 0.45);
        float e = 0.35;
        float h0 = ripple(p, flow);
        float hx = ripple(p + vec2(e, 0.0), flow);
        float hz = ripple(p + vec2(0.0, e), flow);
        vec3 dN = vec3(-(hx - h0), 0.0, -(hz - h0)) * (u_detail * detail_fade);
        N = normalize(N + dN);
    }

    // --- water body colour by depth/slope (brush variation) ---
    vec2 uvn = v_world.xz * 0.04;
    float n = noise(uvn + vec2(time * 0.05, time * 0.03)) * 0.6
            + noise(uvn * 2.7 - time * 0.02) * 0.4;
    float crest = clamp(v_world.y * 0.6 + 0.5, 0.0, 1.0);
    vec3 deep = mix(water_color_deep, water_color, n * 0.5 + crest * 0.5);
    float diff = max(dot(N, light_dir), 0.0);
    deep *= (0.55 + 0.45 * diff) * (0.5 + 0.5 * sun_strength);

    // --- transparency: refract the seabed lookup and blend by water thickness ---
    vec2 refr = N.xz * u_refraction * clamp(thickness * 0.1, 0.0, 1.0);
    vec3 seabed = texture(u_scene, clamp(suv + refr, vec2(0.001), vec2(0.999))).rgb;
    float opacity = 1.0 - exp(-thickness * u_clarity);
    vec3 col = mix(seabed * u_absorb, deep, opacity);

    // --- reflections: sky gradient + reflected sun/moon disc, by Fresnel ---
    vec3 R = reflect(-V, N);
    vec3 refl = mix(sky_color, sky_top, clamp(R.y, 0.0, 1.0));
    float sun_refl = pow(max(dot(R, light_dir), 0.0), u_sun_reflect_shininess);
    refl += light_color * sun_refl * sun_strength;
    float fres = 0.04 + 0.96 * pow(1.0 - max(dot(N, V), 0.0), 4.0);
    col = mix(col, refl, fres * 0.6);

    // --- sharp sun/moon glint (glitters thanks to the detail normals) ---
    vec3 H = normalize(light_dir + V);
    float shininess = mix(120.0, 400.0, storm_intensity);
    float spec = pow(max(dot(N, H), 0.0), shininess);
    col += light_color * spec * (0.3 + 0.7 * sun_strength);

    // --- whitecaps on the steepest crests ---
    float foam = smoothstep(0.8, 1.25, v_world.y / 1.2) * (0.15 + 0.85 * storm_intensity);
    foam *= 0.5 + 0.5 * n;
    col = mix(col, vec3(0.55, 0.60, 0.62), clamp(foam, 0.0, 1.0) * 0.3);

    // --- island shallows tint + frothy shore foam ring ---
    float shallow = 0.0;
    float foam_edge = 0.0;
    for (int i = 0; i < u_island_count; ++i) {
        float dd = distance(v_world.xz, u_island_xz[i]) - u_island_radius[i];
        shallow = max(shallow, 1.0 - clamp(dd / u_shallow_band, 0.0, 1.0));
        foam_edge = max(foam_edge, 1.0 - clamp(abs(dd - 1.5) / 4.5, 0.0, 1.0));
    }
    col = mix(col, u_shallow_color, shallow * 0.30);
    col = mix(col, vec3(0.72, 0.78, 0.80), foam_edge * (0.5 + 0.5 * n) * 0.5);

    // --- distance fog ---
    float fogf = clamp((dist - fog_near) / (fog_far - fog_near), 0.0, 1.0);
    col = mix(col, fog_color, fogf);

    frag_color = vec4(col, 1.0);
}
