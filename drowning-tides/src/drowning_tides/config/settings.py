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
CAM_DISTANCE = 14.0     # how far behind the boat
CAM_HEIGHT = 6.0        # how high above the waterline
CAM_LOOK_HEIGHT = 1.5   # look-at point above the boat origin
CAM_LERP = 4.0          # follow smoothing (higher = snappier), used as 1-exp(-k*dt)

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
