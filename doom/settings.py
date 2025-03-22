import math

# game settings
FULL_HEIGHT = 800
WIDTH = 1300
HUD_HEIGHT = FULL_HEIGHT * (1/8)
HEIGHT = FULL_HEIGHT - HUD_HEIGHT
RES = WIDTH, HEIGHT = WIDTH, HEIGHT
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = (HEIGHT // 2)
FPS = 0

# Test settings
TEST_SPAWN_COVERAGE_DIM = [35, 17, 19.5, 14] #[30] for Test
TEST_SPAWN_RADIUS = [7, 4, 4, 3, 1]

# HUD settings
FULL_HUB_HEIGHT = FULL_HEIGHT - HUD_HEIGHT
HALF_HUB_HEIGHT = HUD_HEIGHT + (FULL_HUB_HEIGHT // 2)
HUD_SECTIONS = 6

# player settings
PLAYER_POS = 1.5, 5 #current_map
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 100

# NPC
NUM_OF_NPCS = 3

# mouse settings
MOUSE_SENSITIVITY = 0.0003
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

# floor settings
FLOOR_COLOR = (30, 30, 30)

# ray casting settings
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

# texture settings
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

enemy_data = {
    'soldier': {
        'health': 100,
        'attack_damage': 10,
        'attack_dist': 3,
        'accuracy': 0.15,
        'scale': 0.6,
        'shift': 0.38,
        'speed': 0.01,
        'animation_time': 100,
        'path': 'resources/sprites/npc/soldier/0.png'
    },
    'caco_demon': {
        'health': 150,
        'attack_damage': 25,
        'attack_dist': 1.0,
        'accuracy': 0.35,
        'scale': 0.7,
        'shift': 0.27,
        'speed': 0.03,
        'animation_time': 250,
        'path': 'resources/sprites/npc/caco_demon/0.png'
    },
    'cyber_demon': {
        'health': 200,
        'attack_damage': 15,
        'attack_dist': 6,
        'accuracy': 0.25,
        'scale': 1.3,
        'shift': 0.04,
        'speed': 0.005,
        'animation_time': 210,
        'path': 'resources/sprites/npc/cyber_demon/0.png'
    }
}

weapon_data = {
    'pistol': {
        'id': 1,
        'cooldown': 80,
        'damage': 5,
        'scale': 5,
        'animation_time': 90,
        'ammo': 15,
        'is_automatic': False,
        'infinite': True,
        'graphic': 'resources/sprites/weapon/pistol/0.png'
    },
    'shotgun': {
        'id': 2,
        'cooldown': 50,
        'damage': 35,
        'scale': 0.4,
        'animation_time': 90,
        'ammo': 15,
        'is_automatic': False,
        'infinite': False,
        'graphic': 'resources/sprites/weapon/shotgun/0.png'
    },
    'axe': {
        'id': 3,
        'cooldown': 100,
        'damage': 40,
        'scale': 0.4,
        'animation_time': 90,
        'ammo': 15,
        'is_automatic': False,
        'infinite': False,
        'graphic': 'resources/sprites/weapon/axe/0.png'
    },
    'chaingun': {
        'id': 4,
        'cooldown': 300,
        'damage': 45,
        'scale': 0.4,
        'animation_time': 70,
        'ammo': 50,
        'is_automatic': True,
        'infinite': False,
        'graphic': 'resources/sprites/weapon/chaingun/0.png'
    },
    'plasma_rifle': {
        'id': 5,
        'cooldown': 50,
        'damage': 60,
        'scale': 4.3,
        'animation_time': 105,
        'ammo': 15,
        'is_automatic': False,
        'infinite': False,
        'graphic': 'resources/sprites/plasma_rifle/0.png'
    },
    'bfg': {
        'id': 6,
        'cooldown': 400,
        'damage': 85,
        'scale': 3,
        'animation_time': 105,
        'ammo': 15,
        'is_automatic': False,
        'infinite': False,
        'graphic': 'resources/sprites/weapon/bfg/0.png'
    },
    'double_barrel': {
        'id': 7,
        'cooldown': 50,
        'damage': 8,
        'scale': 3,
        'animation_time': 105,
        'ammo': 12,
        'is_automatic': False,
        'infinite': False,
        'graphic': 'resources/sprites/weapon/double_barrel/0.png'
    },
}

ground_weapon_data = {
    'pistol': {
        'id': 1,
        'scale': 5,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/pistol/ground/0.png'
    },
    'shotgun': {
        'id': 2,
        'scale': 0.8,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/shotgun/ground/0.png'
    },
    'axe': {
        'id': 3,
        'scale': 0.8,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/axw/ground/0.png'
    },
    'chaingun': {
        'id': 4,
        'scale': 0.2,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/chaingun/ground/0.png'
    },
    'plasma_rifle': {
        'id': 5,
        'scale': 0.2,
        'animation_time': 90,
        'graphic': 'resources/sprites/plasma_rifle/ground/0.png'
    },
    'bfg': {
        'id': 6,
        'scale': 0.5,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/bfg/ground/0.png'
    },
    'double_barrel': {
        'id': 7,
        'scale': 0.5,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/double_barrel/ground/0.png'
    },
}

ammo_data = {
    'pistol': { #todo
        'id': 1,
        'scale': 0.2,
        'size': 5,
        'shift': 2.5,
        'quantity': 10,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/pistol/ammo/0.png'
    },
    'shotgun': {
        'id': 2,
        'scale': 0.2,
        'size': 5,
        'shift': 2.5,
        'quantity': 10,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/shotgun/ammo/0.png'
    },
    'axe': { #todo
        'id': 3,
        'scale': 0.8,
        'size': 5,
        'shift': 2.5,
        'quantity': 10,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/axw/ammo/0.png'
    },
    'chaingun': {
        'id': 4,
        'scale': 0.4,
        'size': 5,
        'shift': 1.2,
        'quantity': 100,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/chaingun/ammo/0.png'
    },
    'plasma_rifle': {
        'id': 5,
        'scale': 0.5,
        'size': 5,
        'shift': 1,
        'quantity': 20,
        'animation_time': 90,
        'graphic': 'resources/sprites/plasma_rifle/ammo/0.png'
    },
    'bfg': { #todo
        'id': 6,
        'scale': 0.5,
        'size': 5,
        'shift': 2.5,
        'quantity': 10,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/bfg/ammo/0.png'
    },
    'double_barrel': { #todo
        'id': 7,
        'scale': 0.5,
        'size': 5,
        'shift': 2.5,
        'quantity': 10,
        'animation_time': 90,
        'graphic': 'resources/sprites/weapon/double_barrel/ammo/0.png'
    },
}

armor_data = {
    'armor': {
        'points': 50,
    }
}

potion_data = {
    'health_potion': {
        'points': 50,
    }
}