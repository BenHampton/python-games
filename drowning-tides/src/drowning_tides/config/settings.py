import math

import pygame as pg
from pyglm import glm

# opengl
MAJOR_VERSION = 3
MINOR_VERSION = 3
DEPTH_SIZE = 24

# resolution
FULLSCREEN = False              # start windowed (WIN_RES); True uses native desktop resolution
WIN_RES = glm.vec2(1280, 720)   # windowed size / fallback (overwritten at startup in fullscreen)

# control keys
KEYS = {
    'THROTTLE_UP': pg.K_w,
    'THROTTLE_DOWN': pg.K_s,
    'TURN_LEFT': pg.K_a,
    'TURN_RIGHT': pg.K_d,
    'QUIT': pg.K_ESCAPE,        # opens the pause menu (Resume to unpause)
    'CONSOLE': pg.K_BACKQUOTE,
    'FULLSCREEN': pg.K_F11,     # toggle fullscreen / windowed
    'MOUNT': pg.K_e,            # board / disembark the boat (only near land to disembark)
    'INTERACT': pg.K_f,         # context: fish (at helm over water) / talk to NPC (on foot)
}

# camera (projection)
ASPECT_RATIO = WIN_RES.x / WIN_RES.y
FOV_DEG = 55
V_FOV = glm.radians(FOV_DEG)
H_FOV = 2 * math.atan(math.tan(V_FOV * 0.5) * ASPECT_RATIO)
NEAR = 0.1
FAR = 2000.0

# camera (third-person follow)
CAM_DISTANCE = 14.0     # orbit distance (3D) from the look pivot
CAM_HEIGHT = 6.0        # legacy: unused by the orbit cam (kept for reference)
CAM_LOOK_HEIGHT = 1.5   # look-at point above the boat origin
CAM_LERP = 4.0          # follow smoothing (higher = snappier), used as 1-exp(-k*dt)

# camera mouse-look orbit (world-space yaw so the angle holds as the boat turns)
MOUSE_SENSITIVITY = 0.0025          # radians of orbit per pixel of mouse motion
INVERT_Y = False                    # flip vertical look (per-mode default is mouse up = view up)
CAM_PITCH_START = math.radians(24.0)
CAM_PITCH_MIN = math.radians(-5.0)  # don't dip the camera under the sea
CAM_PITCH_MAX = math.radians(80.0)  # don't flip overhead
CAM_DISTANCE_MIN = 6.0              # closest scroll-zoom
CAM_DISTANCE_MAX = 40.0             # farthest scroll-zoom
CAM_ZOOM_STEP = 2.0                 # distance units per scroll notch
FP_PITCH_MIN = math.radians(-85.0)  # first-person look-down limit
FP_PITCH_MAX = math.radians(85.0)   # first-person look-up limit

# on-foot (first-person, walk on land when docked)
DOCK_RANGE = 22.0                   # how close the boat must be to an island shore to disembark
PLAYER_SPEED = 9.0                  # walk speed (units/sec)
PLAYER_EYE_HEIGHT = 1.7             # camera eye height above the land plane
ISLAND_LAND_FRAC = 0.42            # mesa islands: stand on the grassy cap (frac of scale)
ISLAND_WALK_FRAC = 0.35            # mesa: walkable summit radius (frac of island radius)
ISLAND_SPAWN_FRAC = 0.15          # mesa: spawn near the summit centre
# the home island is a big FLAT-topped island so the village is easy to reach + visible
HOME_LAND_FRAC = 0.03             # flat shelf height (frac of scale): low level top (sync gen)
HOME_FLAT_FRAC = 0.40            # flat inside this radius frac; gentle ramp outside (sync gen)
HOME_SHORE_Y = 0.4              # ground height at the shore (just above water; ramp foot)
HOME_WALK_FRAC = 0.85            # walk out to the waterline (beyond this the beach is underwater)
HOME_SPAWN_FRAC = 0.78           # disembark on dry beach, walk up the ramp to the village

# boat physics
BOAT_MAX_SPEED = 22.0       # units / second forward
BOAT_MAX_REVERSE = 8.0      # units / second backward
BOAT_ACCEL = 14.0           # forward throttle acceleration
BOAT_REVERSE_ACCEL = 10.0   # reverse / braking acceleration
WATER_DRAG = 0.9            # linear drag coefficient (per second, exp decay)
BOAT_TURN_RATE = 1.4        # max yaw rad/sec at full turn authority
# turn authority scales with how fast we're moving: sluggish near stop, wide at speed
TURN_SPEED_FACTOR = 0.65    # fraction of max speed at which turning is fully authoritative
BOAT_START_POS = glm.vec3(0.0, 0.0, -384.0)  # moored alongside Freeport's pier T-head
BOAT_START_YAW = math.pi / 2                  # bow +X: lies parallel to the T-head crossbar
BOAT_COLLISION_RADIUS = 2.0     # boat's collision disc radius (world units)
BOAT_COLLISION_BLEED = 0.3      # speed retained after hitting land

# ------------------------------------------------------------------------ islands / map
# Designed archipelago after map-1 ("Sea of Treasures"). Each island is a unique seeded
# model baked by tools/gen_islands.py -> assets/models/islands/<name>_lod{0,1}.glb.
# kind: 'home' (gets a dock), 'island', or 'reef' (low, mostly submerged rocks).
# 'radius' is the collision disc (world units, ~= scale).
# (name, x, z, scale, yaw, seed, kind); collision radius == scale
_ISLAND_TABLE = [
    ('freeport',          0.0, -185.0, 195.0, 0.3, 11, 'home'),
    ('haven',          -260.0, -320.0, 20.0, 1.1, 22, 'island'),
    ('fogholms',       -120.0, -560.0, 16.0, 2.4, 33, 'island'),
    ('cedar_march',     380.0, -430.0, 40.0, 0.7, 44, 'island'),
    ('west_watch',      640.0, -360.0, 18.0, 2.0, 55, 'island'),
    ('wrights_isle',    520.0, -150.0, 12.0, 1.5, 66, 'island'),
    ('chain_town',      210.0,  140.0, 24.0, 2.8, 77, 'island'),
    ('ring_of_thorns', -180.0,  220.0, 30.0, 0.2, 88, 'island'),
    ('hags_rock',       430.0,  260.0, 10.0, 1.9, 99, 'island'),
    ('kingbreaker_reef',760.0,   60.0, 34.0, 0.0, 13, 'reef'),
    ('dagons_isle',     380.0,  620.0, 22.0, 1.3, 17, 'island'),
]
ISLANDS = [
    {'name': n, 'pos': (x, 0.0, z), 'scale': s, 'yaw': y, 'seed': sd, 'kind': k, 'radius': s}
    for (n, x, z, s, y, sd, k) in _ISLAND_TABLE
]

# culling / level-of-detail (industry-standard: frustum + distance cull, distance LOD swap)
ISLAND_LOD_DIST = 260.0         # within this camera distance use LOD0 (full), else LOD1
ISLAND_CULL_DIST = 1100.0       # beyond this (minus radius) the island is skipped entirely

# turquoise shallow-water shelf tinted into the sea near land (water.frag)
SHALLOW_COLOR = glm.vec3(0.10, 0.36, 0.40)   # muted teal lagoon shelf
SHALLOW_BAND = 26.0             # how far past an island's radius the shelf reaches
MAX_SHALLOW_ISLANDS = 24        # uniform array cap in the water shader

# water (grid follows the camera in the vertex shader so a high-res patch always
# surrounds the view; world-space phase keeps the waves from swimming)
WATER_LEVEL = 0.0
WATER_SIZE = 500.0      # half-extent of the moving water patch
WATER_GRID = 200        # subdivisions per axis (cell ~5 units -> waves resolve)

# water realism (water.frag): micro-ripple normals, refraction, depth transparency, reflection
WATER_DETAIL = 0.5                       # micro-ripple normal strength (sun glitter)
WATER_DETAIL_SCALE = 0.5                 # ripple frequency (world units)
WATER_REFRACTION = 0.025                 # seabed refraction wobble amount
WATER_CLARITY = 0.20                     # absorption k; higher = water turns opaque sooner
WATER_ABSORB = glm.vec3(0.45, 0.70, 0.72)  # underwater tint on the seabed seen through water
WATER_SUN_REFLECT_SHININESS = 800.0      # tightness of the reflected sun/moon disc

# atmosphere / dark maritime palette (CALM presets; storm presets below)
BG_COLOR = glm.vec3(0.06, 0.09, 0.12)
WATER_COLOR = glm.vec3(0.05, 0.10, 0.13)
WATER_COLOR_DEEP = glm.vec3(0.02, 0.05, 0.07)
FOG_COLOR = glm.vec3(0.18, 0.24, 0.28)      # hazy slate horizon
FOG_NEAR = 60.0
FOG_FAR = 700.0
SKY_HORIZON_COLOR = glm.vec3(0.20, 0.27, 0.31)
SKY_TOP_COLOR = glm.vec3(0.04, 0.07, 0.11)
SUN_DIR = glm.normalize(glm.vec3(-0.4, 0.55, -0.7))  # key light direction (toward light)
SUN_STRENGTH = 1.0      # calm key-light intensity

# storm mood presets (lerped toward by storm_intensity)
WATER_COLOR_STORM = glm.vec3(0.03, 0.06, 0.08)
WATER_COLOR_DEEP_STORM = glm.vec3(0.01, 0.03, 0.04)
FOG_COLOR_STORM = glm.vec3(0.09, 0.11, 0.13)        # grey, closes the horizon
FOG_NEAR_STORM = 18.0
FOG_FAR_STORM = 230.0
SKY_HORIZON_COLOR_STORM = glm.vec3(0.10, 0.12, 0.14)
SKY_TOP_COLOR_STORM = glm.vec3(0.02, 0.03, 0.05)
SUN_STRENGTH_STORM = 0.35   # dim, overcast

# ----------------------------------------------------------------- weather system
# scheduler timings (seconds); ranges are (min, max), picked randomly per cycle
WEATHER_CALM_RANGE = (20.0, 60.0)       # quiet gap before a storm rolls in
WEATHER_BUILDUP_RANGE = (15.0, 30.0)    # ramp up to peak
WEATHER_HOLD_RANGE = (20.0, 45.0)       # sustained near peak
WEATHER_EASE_RANGE = (15.0, 30.0)       # ramp back down to calm
WEATHER_PEAK_RANGE = (0.5, 1.0)         # random peak storm_intensity
STORM_INTENSITY_LERP = 0.5              # how fast intensity tracks its target (/sec)
STORM_KILL_RATE = 0.6                   # fast target decay used by /storm-kill (/sec)

# wind
WIND_MAX_STRENGTH = 1.0                 # normalized; scales rain slant + current
WIND_WANDER_RATE = 0.06                 # rad/sec random walk of wind direction
WIND_START_DIR = glm.vec2(1.0, 0.3)     # initial wind heading (xz), normalized at use
CURRENT_PUSH = 4.0                      # boat drift speed (units/sec) at full storm

# ------------------------------------------------------------------- Gerstner waves
N_WAVES = 4
GRAVITY = 9.8
WAVE_WAVELENGTHS = (60.0, 37.0, 23.0, 13.0)
WAVE_AMP_RATIOS = (1.0, 0.6, 0.35, 0.2)     # relative amplitude per component
WAVE_DIR_SPREAD = 0.6                        # radians fanned around the wind dir
WAVE_STEEPNESS = 0.85                        # Gerstner Q (sharpness); <1 avoids loops
WAVE_CALM_AMP = 0.07                          # gentle swell even in calm
WAVE_STORM_AMP = 1.6                          # base amplitude scale at full storm
WAVE_MAX_AMPLITUDE = 1.8                      # hard playability cap on total height

# ------------------------------------------------------------------------- rain
RAIN_COUNT = 7000
RAIN_FALL_SPEED = 45.0          # units/sec downward
RAIN_STREAK_LEN = 1.3           # length of each streak
RAIN_BOX = glm.vec3(70.0, 45.0, 70.0)   # spawn volume (half-extents) around camera
RAIN_COLOR = glm.vec3(0.6, 0.68, 0.75)
RAIN_MAX_ALPHA = 0.5            # alpha at full storm
RAIN_WIND_SLANT = 18.0         # horizontal velocity (units/sec) per unit wind strength

# ------------------------------------------------------------------- boat (storm)
BOAT_SCALE = 1.4
BOAT_MAX_TILT = glm.radians(12.0)   # never-flip clamp on wave-induced pitch/roll
BOAT_TILT_EASE = 4.0                # how fast tilt tracks the wave slope (/sec)

# authored boat model: drop a CC0 glTF (e.g. Kenney Watercraft Kit) into assets/models/
# and set BOAT_MODEL to its filename to replace the procedural hull. Tune scale/yaw to fit.
BOAT_MODEL = 'boat-fishing.glb'     # Kenney Watercraft Kit (CC0); None -> procedural hull
BOAT_MODEL_SCALE = 1.7             # world scale applied to the authored model
BOAT_MODEL_YAW = 0.0               # radians; offset if the model's bow isn't +Z
BOAT_MODEL_Y_OFFSET = -0.85        # sink the hull into the waterline (world units)

# ------------------------------------------------------------------------ console
CONSOLE_HEIGHT = 30             # px height of the input bar
CONSOLE_FONT_SIZE = 18
CONSOLE_BG_COLOR = (10, 14, 18, 200)        # rgba, translucent bar
CONSOLE_TEXT_COLOR = (210, 220, 225)
CONSOLE_PROMPT = '> '

# ------------------------------------------------------------------- post / bloom
BLOOM_THRESHOLD = 0.6       # luminance above which pixels bloom
BLOOM_INTENSITY = 0.85      # how much bloom is added back in the composite
BLOOM_PASSES = 3            # separable blur ping-pong iterations (wider, softer glow)

# ------------------------------------------------------------------- day / night cycle
DAY_LENGTH = 180.0          # seconds for a full dawn->day->dusk->night loop (short; tune later)
DAY_TIMESCALE = 1.0         # time multiplier (console: /timescale)
DAY_START = 0.30            # starting phase in [0,1) (early morning)
SUN_ARC_TILT = 0.5          # z-component of the sun's arc plane (visual angle of the arc)

SUN_COLOR = glm.vec3(0.98, 0.86, 0.70)     # softened, overcast warm key light / sun disc
MOON_COLOR = glm.vec3(0.55, 0.62, 0.78)    # cold pale moonlight / moon disc
SUN_DISC_SIZE = 0.020       # angular size of the sun disc (1 - cos cutoff; bigger = larger)
MOON_DISC_SIZE = 0.012
STAR_DENSITY = 120.0        # star grid scale (higher = more, smaller stars)
STAR_BRIGHTNESS = 0.9

# time-of-day palette keyframes (ascending 't' in [0,1); interpolated, wraps 0.75 -> 0.00).
# Tuned toward DREDGE's muted, overcast, fog-closed maritime mood (low saturation, low contrast).
DAY_KEYFRAMES = [
    {  # deep night — eerie dark, misty
        't': 0.00,
        'sky_top': glm.vec3(0.012, 0.020, 0.035),
        'sky_horizon': glm.vec3(0.045, 0.065, 0.090),
        'water_color': glm.vec3(0.020, 0.038, 0.052),
        'water_color_deep': glm.vec3(0.006, 0.018, 0.026),
        'fog_color': glm.vec3(0.045, 0.065, 0.085),
        'fog_near': 38.0, 'fog_far': 360.0,
        'sun_strength': 0.16,
    },
    {  # dawn — pale, misty, desaturated
        't': 0.25,
        'sky_top': glm.vec3(0.075, 0.095, 0.140),
        'sky_horizon': glm.vec3(0.340, 0.300, 0.300),
        'water_color': glm.vec3(0.060, 0.090, 0.110),
        'water_color_deep': glm.vec3(0.018, 0.045, 0.060),
        'fog_color': glm.vec3(0.300, 0.300, 0.320),
        'fog_near': 45.0, 'fog_far': 480.0,
        'sun_strength': 0.50,
    },
    {  # day — overcast, muted grey-teal (not bright tropical blue)
        't': 0.50,
        'sky_top': glm.vec3(0.130, 0.190, 0.260),
        'sky_horizon': glm.vec3(0.420, 0.470, 0.490),
        'water_color': glm.vec3(0.055, 0.110, 0.140),
        'water_color_deep': glm.vec3(0.018, 0.050, 0.070),
        'fog_color': glm.vec3(0.340, 0.400, 0.430),
        'fog_near': 60.0, 'fog_far': 620.0,
        'sun_strength': 0.82,
    },
    {  # dusk — muted, melancholic orange-grey
        't': 0.75,
        'sky_top': glm.vec3(0.060, 0.070, 0.115),
        'sky_horizon': glm.vec3(0.420, 0.260, 0.240),
        'water_color': glm.vec3(0.055, 0.085, 0.110),
        'water_color_deep': glm.vec3(0.018, 0.038, 0.055),
        'fog_color': glm.vec3(0.270, 0.210, 0.220),
        'fog_near': 48.0, 'fog_far': 520.0,
        'sun_strength': 0.45,
    },
]

# ------------------------------------------------------------------- fog banks
# Independent of storms; can roll in day or night. Scheduler mirrors the storm one.
FOG_CALM_RANGE = (25.0, 70.0)       # clear gap between fog banks
FOG_BUILDUP_RANGE = (8.0, 18.0)     # roll-in
FOG_HOLD_RANGE = (10.0, 30.0)       # sustained
FOG_EASE_RANGE = (8.0, 20.0)        # fade-out
FOG_PEAK_RANGE = (0.4, 1.0)         # random peak fog_intensity
FOG_MAX_DURATION = 60.0             # cap on a bank's active time (TODO: more realistic later)
FOG_KILL_RATE = 0.5                 # fast decay used by /fog-kill (/sec)
FOG_DENSE_NEAR = 12.0               # fog_near at full fog_intensity
FOG_DENSE_FAR = 140.0               # fog_far at full fog_intensity
FOG_TINT = glm.vec3(0.16, 0.18, 0.20)   # fog-bank colour blended into the fog

# ------------------------------------------------------------------- clouds
# Cover (0..1) wanders through the day; storms force overcast (see weather.py).
CLOUD_WANDER_RANGE = (20.0, 60.0)       # seconds before a new random cover target
CLOUD_EASE = 0.15                       # how fast cover transitions (/sec)
CLOUD_SCALE = 1.6                       # cloud noise frequency on the sky dome
CLOUD_SPEED = 0.02                      # drift speed (scrolls with the wind)
CLOUD_COLOR = glm.vec3(0.80, 0.82, 0.85)        # sunlit cloud top
CLOUD_COLOR_DARK = glm.vec3(0.30, 0.33, 0.37)   # shadowed cloud base
CLOUD_COLOR_STORM = glm.vec3(0.12, 0.13, 0.15)  # heavy overcast in storms

# ------------------------------------------------------------------- aurora (cosmic night)
AURORA_STRENGTH = 0.25                  # subtle/creeping
AURORA_COLOR_A = glm.vec3(0.10, 0.45, 0.35)     # eerie teal
AURORA_COLOR_B = glm.vec3(0.30, 0.15, 0.45)     # violet

# ------------------------------------------------------------------- lightning
LIGHTNING_RATE = 0.35                   # flash attempts/sec at full storm (scaled by intensity)
LIGHTNING_DECAY = 9.0                   # flash brightness decay (/sec)
LIGHTNING_COLOR = glm.vec3(0.70, 0.78, 1.0)     # cool flash tint added across the scene
LIGHTNING_SCENE_BOOST = 0.9             # how much a flash brightens sea/land/boat
BOLT_CHANCE = 0.4                       # fraction of flashes that draw a visible bolt
BOLT_LIFETIME = 0.18                    # seconds a bolt stays visible
BOLT_SEGMENTS = 14                      # jagged segments per bolt
BOLT_COLOR = glm.vec3(0.85, 0.90, 1.0)

# ------------------------------------------------------------------- god rays (post)
GODRAY_SAMPLES = 48
GODRAY_DECAY = 0.96
GODRAY_WEIGHT = 0.5
GODRAY_INTENSITY = 0.6

# ------------------------------------------------------------------- town / NPCs (phase 3)
TOWN_HOUSE_COUNT = 6
HOUSE_WALL_COLOR = (0.52, 0.43, 0.31)       # driftwood brown
HOUSE_ROOF_COLOR = (0.55, 0.30, 0.20)       # muted orange-red
DOCK_COLOR = (0.34, 0.25, 0.16)
NPC_COUNT = 4
NPC_BODY_COLOR = (0.30, 0.34, 0.42)
NPC_HEAD_COLOR = (0.62, 0.50, 0.42)
NPC_INTERACT_RANGE = 6.0
NPC_BOAT_COUNT = 3
NPC_BOAT_SPEED = 4.5

# ------------------------------------------------------------------- fishing (phase 4)
# (name, rarity weight, aberrated)
FISH_TABLE = [
    ('Herring', 30, False), ('Cod', 25, False), ('Mackerel', 20, False),
    ('Sea Bass', 12, False), ('Lantern Eel', 7, False),
    ('Pale Drifter', 4, True), ('Hollow Catch', 2, True),
]
FISH_CAST_TIME = 1.6                         # seconds from cast to bite

# ------------------------------------------------------------------- aberration (phase 5)
ABERRATION_NIGHT = 0.35                      # night ramps chromatic aberration
ABERRATION_STORM = 0.40                      # storms ramp it
ABERRATION_CATCH = 1.0                       # spike when an aberrated fish is caught
ABERRATION_DECAY = 0.6                       # catch-spike fade (/sec)
ABERRATION_MAX = 1.2
ABERRATION_STRENGTH = 0.004                  # max per-channel UV offset at aberration = 1
