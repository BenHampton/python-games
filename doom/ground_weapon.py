from sprite_object import *

class GroundWeapon(AnimatedSprite):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/shotgun/ground/0.png',
                 pos=(1, 1),
                 scale=0.4,
                 animation_time=90,
                 weapon_id=0):
        super().__init__(game=game, path=path, pos=pos, scale=scale, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.x, self.y = pos
        self.available = False
        self.num_images = len(self.images)
        self.size = 10
        self.frame_counter = 0
        self.weapon_id = weapon_id

    def draw(self):
        if self.game.test_mode and self.available:
            dim = TEST_SPAWN_COVERAGE_DIM[self.game.current_level]
            dim_two = dim // 2
            radius = TEST_SPAWN_RADIUS[self.game.current_level]
            pg.draw.rect(self.game.screen, 'pink', (self.x * dim - dim_two, self.y * dim - dim_two, dim, dim), 2)
            pg.draw.circle(self.game.screen, 'pink', (self.x * dim,  self.y * dim), radius)

    def update(self):
        if self.available:
            self.check_animation_time()
            self.get_sprite()
            self.check_picked_up()
        if self.game.test_mode:
            self.draw()

    def check_picked_up(self):
        if self.game.player.map_pos in self.game.object_handler.ground_weapon_positions:
            for weapon in self.game.map.map_weapons:
                if self.game.player.map_pos == self.map_pos:
                    if weapon(self).weapon_id == self.weapon_id:
                        weapon_from_ground = self.game.object_handler.all_weapons[weapon(self).weapon_id]
                        self.game.object_handler.add_weapon_to_bag(weapon_from_ground)
                        self.available = False

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

class GroundShotgun(GroundWeapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/shotgun/ground/0.png',
                 pos=(3.5, 3.5),
                 scale=0.8,
                 animation_time=90,
                 weapon_id=2):
        super().__init__(game=game, path=path, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class GroundAxe(GroundWeapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/axe/ground/0.png',
                 pos=(1.5, 1.5),
                 scale=0.8,
                 animation_time=90,
                 weapon_id=3):
        super().__init__(game=game, path=path, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class GroundChaingun(GroundWeapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/chaingun/ground/0.png',
                 pos=(3.5, 6.5),
                 scale=0.2,
                 animation_time=90,
                 weapon_id=4):
        super().__init__(game=game, path=path, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class GroundPlasmaRifle(GroundWeapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/plasma_rifle/ground/0.png',
                 pos=(3.5, 7.5),
                 scale=0.2,
                 animation_time=90,
                 weapon_id=5):
        super().__init__(game=game, path=path, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class GroundBFG(GroundWeapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/bfg/ground/0.png',
                 pos=(4,4.5),
                 scale=0.5,
                 animation_time=90,
                 weapon_id=6):
        super().__init__(game=game, path=path, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True
