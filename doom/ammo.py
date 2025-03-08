from sprite_object import *

class Ammo(AnimatedSprite):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/shotgun/ammo/0.png',
                 pos=(1, 1),
                 scale=0.4,
                 shift=0,
                 animation_time=90,
                 quantity=0,
                 weapon_id=0):
        super().__init__(game=game, path=path, pos=pos, scale=scale, shift=shift, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.x, self.y = pos
        self.num_images = len(self.images)
        self.size = 10
        self.frame_counter = 0
        self.weapon_id = weapon_id
        self.quantity = quantity
        self.available = False

    def draw(self):
        if self.game.test_mode and self.available:
            dim = TEST_SPAWN_COVERAGE_DIM[self.game.current_level]
            dim_two = dim // 2
            radius = TEST_SPAWN_RADIUS[self.game.current_level]
            pg.draw.rect(self.game.screen, 'brown', (self.x * dim - dim_two, self.y * dim - dim_two, dim, dim), 2)
            pg.draw.circle(self.game.screen, 'brown', (self.x * dim,  self.y * dim), radius)

    def update(self):
        if self.available:
            self.check_animation_time()
            self.get_sprite()
            self.check_picked_up()
        if self.game.test_mode:
            self.draw()

    def check_picked_up(self):
        if self.game.player.map_pos in self.game.object_handler.ammo_positions:
            if self.game.player.map_pos == self.map_pos and  self.weapon_id == self.weapon_id:
                    for weapon_in_bag in self.game.player.weapon_bag:
                        if weapon_in_bag.weapon_id == self.weapon_id:
                            weapon_in_bag.add_ammo(self.quantity)
                            self.available = False

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

class ShotgunAmmo(Ammo):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/shotgun/ammo/0.png',
                 pos=(3.5, 3.5),
                 scale=0.2,
                 shift=2.5,
                 animation_time=90,
                 quantity=10,
                 weapon_id=2):
        super().__init__(game=game, path=path, pos=pos, scale=scale, shift=shift, animation_time=animation_time, quantity=quantity, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class ChaingunAmmo(Ammo):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/chaingun/ammo/0.png',
                 pos=(3.5, 6.5),
                 scale=0.4,
                 shift=1.2,
                 animation_time=90,
                 quantity=100,
                 weapon_id=4):
        super().__init__(game=game, path=path, pos=pos, scale=scale, shift=shift, animation_time=animation_time, quantity=quantity, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class PlasmaRifleAmmo(Ammo):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/plasma_rifle/ammo/0.png',
                 pos=(3.5, 7.5),
                 scale=0.5,
                 shift=1,
                 animation_time=90,
                 quantity=20,
                 weapon_id=5):
        super().__init__(game=game, path=path, pos=pos, scale=scale, shift=shift, animation_time=animation_time, quantity=quantity, weapon_id=weapon_id)
        self.size = 5
        self.available = True
