import math

import pygame as pg
from pyglm import glm

# opengl
MAJOR_VERSION = 3
MINOR_VERSION = 3
DEPTH_SIZE = 24

# resolution
WIN_RES = glm.vec2(1280, 720)

# control keys
KEYS = {
    'THROTTLE_UP': pg.K_w,
    'THROTTLE_DOWN': pg.K_s,
    'TURN_LEFT': pg.K_a,
    'TURN_RIGHT': pg.K_d,
    'QUIT': pg.K_ESCAPE,
    'CONSOLE': pg.K_BACKQUOTE,
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
INVERT_Y = False                    # flip vertical look
CAM_PITCH_START = math.radians(24.0)
CAM_PITCH_MIN = math.radians(-5.0)  # don't dip the camera under the sea
CAM_PITCH_MAX = math.radians(80.0)  # don't flip overhead
CAM_DISTANCE_MIN = 6.0              # closest scroll-zoom
CAM_DISTANCE_MAX = 40.0             # farthest scroll-zoom
CAM_ZOOM_STEP = 2.0                 # distance units per scroll notch

# boat physics
BOAT_MAX_SPEED = 22.0       # units / second forward
BOAT_MAX_REVERSE = 8.0      # units / second backward
BOAT_ACCEL = 14.0           # forward throttle acceleration
BOAT_REVERSE_ACCEL = 10.0   # reverse / braking acceleration
WATER_DRAG = 0.9            # linear drag coefficient (per second, exp decay)
BOAT_TURN_RATE = 1.4        # max yaw rad/sec at full turn authority
# turn authority scales with how fast we're moving: sluggish near stop, wide at speed
TURN_SPEED_FACTOR = 0.65    # fraction of max speed at which turning is fully authoritative
BOAT_START_POS = glm.vec3(0.0, 0.0, 0.0)

# water (grid follows the camera in the vertex shader so a high-res patch always
# surrounds the view; world-space phase keeps the waves from swimming)
WATER_LEVEL = 0.0
WATER_SIZE = 500.0      # half-extent of the moving water patch
WATER_GRID = 200        # subdivisions per axis (cell ~5 units -> waves resolve)

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
WAVE_STEEPNESS = 0.7                         # Gerstner Q (sharpness); <1 avoids loops
WAVE_CALM_AMP = 0.05                          # gentle swell even in calm
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

# ------------------------------------------------------------------------ console
CONSOLE_HEIGHT = 30             # px height of the input bar
CONSOLE_FONT_SIZE = 18
CONSOLE_BG_COLOR = (10, 14, 18, 200)        # rgba, translucent bar
CONSOLE_TEXT_COLOR = (210, 220, 225)
CONSOLE_PROMPT = '> '

# ------------------------------------------------------------------- day / night cycle
DAY_LENGTH = 180.0          # seconds for a full dawn->day->dusk->night loop (short; tune later)
DAY_TIMESCALE = 1.0         # time multiplier (console: /timescale)
DAY_START = 0.30            # starting phase in [0,1) (early morning)
SUN_ARC_TILT = 0.5          # z-component of the sun's arc plane (visual angle of the arc)

SUN_COLOR = glm.vec3(1.00, 0.85, 0.65)     # warm key light / sun disc
MOON_COLOR = glm.vec3(0.55, 0.62, 0.78)    # cold pale moonlight / moon disc
SUN_DISC_SIZE = 0.020       # angular size of the sun disc (1 - cos cutoff; bigger = larger)
MOON_DISC_SIZE = 0.012
STAR_DENSITY = 120.0        # star grid scale (higher = more, smaller stars)
STAR_BRIGHTNESS = 0.9

# time-of-day palette keyframes (ascending 't' in [0,1); interpolated, wraps 0.75 -> 0.00)
DAY_KEYFRAMES = [
    {  # deep night — eerie dark
        't': 0.00,
        'sky_top': glm.vec3(0.010, 0.020, 0.040),
        'sky_horizon': glm.vec3(0.040, 0.060, 0.100),
        'water_color': glm.vec3(0.020, 0.040, 0.060),
        'water_color_deep': glm.vec3(0.005, 0.020, 0.030),
        'fog_color': glm.vec3(0.050, 0.070, 0.100),
        'fog_near': 40.0, 'fog_far': 420.0,
        'sun_strength': 0.18,
    },
    {  # dawn
        't': 0.25,
        'sky_top': glm.vec3(0.060, 0.090, 0.160),
        'sky_horizon': glm.vec3(0.420, 0.300, 0.280),
        'water_color': glm.vec3(0.070, 0.100, 0.130),
        'water_color_deep': glm.vec3(0.020, 0.050, 0.070),
        'fog_color': glm.vec3(0.300, 0.270, 0.300),
        'fog_near': 55.0, 'fog_far': 620.0,
        'sun_strength': 0.60,
    },
    {  # day
        't': 0.50,
        'sky_top': glm.vec3(0.100, 0.200, 0.340),
        'sky_horizon': glm.vec3(0.450, 0.550, 0.600),
        'water_color': glm.vec3(0.060, 0.130, 0.170),
        'water_color_deep': glm.vec3(0.020, 0.060, 0.090),
        'fog_color': glm.vec3(0.300, 0.400, 0.460),
        'fog_near': 70.0, 'fog_far': 800.0,
        'sun_strength': 1.00,
    },
    {  # dusk
        't': 0.75,
        'sky_top': glm.vec3(0.060, 0.070, 0.130),
        'sky_horizon': glm.vec3(0.500, 0.260, 0.220),
        'water_color': glm.vec3(0.060, 0.090, 0.120),
        'water_color_deep': glm.vec3(0.020, 0.040, 0.060),
        'fog_color': glm.vec3(0.280, 0.200, 0.220),
        'fog_near': 55.0, 'fog_far': 600.0,
        'sun_strength': 0.50,
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
