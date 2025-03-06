from pygame.display import update

from sprite_object import *

class Weapon(AnimatedSprite):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/pistol/0.png',
                 scale=0.4,
                 animation_time=90,
                 weapon_id=-1):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.reloading = False
        self.available = False
        self.is_automatic = False
        self.is_handhold = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 0
        self.ammo_cap = 0
        self.ammo = 0
        self.weapon_id = weapon_id

    def animate_shot(self):
        if self.game.player.active_weapon is not None and self.weapon_id == self.game.player.active_weapon.weapon_id:
            if self.reloading:
                self.player.shot = False
                if self.animation_trigger and self.game.weapon.ammo > 0:
                    self.images.rotate(-1)
                    self.image = self.images[0]
                    self.frame_counter += 1
                    if self.frame_counter == self.num_images:
                        self.reloading = False
                        self.frame_counter = 0
                        self.game.weapon.ammo -= 1
            if self.is_automatic and self.game.player.shot:
                if self.animation_trigger and self.game.weapon.ammo > 0:
                    self.images.rotate(-1)
                    self.image = self.images[0]
                    self.frame_counter += 1
                    if self.frame_counter == self.num_images:
                        self.frame_counter = 0
                        self.game.weapon.ammo -= 1

    def add_ammo(self, ammo):
        #todo calculate incoming ammo and ammo_cap
        self.ammo += ammo

    def draw(self):
        self.game.screen.blit(self.images[0], self.weapon_pos)

    def update(self):
        self.check_animation_time()
        self.animate_shot()

    @property
    def get_weapon_id(self):
        return int(self.weapon_id)

class PistolWeapon(Weapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/pistol/0.png',
                 scale=5,
                 animation_time=90,
                 weapon_id=1):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time,weapon_id=weapon_id)
        self.damage = 10
        self.ammo = 10
        self.ammo_cap = 50
        self.frame_counter = 0

class ShotgunWeapon(Weapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/shotgun/0.png',
                 scale=0.4,
                 animation_time=90,
                 weapon_id=2):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time,weapon_id=weapon_id)
        self.damage = 50
        self.ammo = 5
        self.ammo_cap = 25
        self.frame_counter = 0

class AxeWeapon(Weapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/axe/0.png',
                 scale=0.4,
                 animation_time=90,
                 weapon_id=3):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time,weapon_id=weapon_id)
        self.damage = 35
        self.frame_counter = 0

class ChaingunWeapon(Weapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/chaingun/0.png',
                 scale=3,
                 animation_time=70,
                 weapon_id=4):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time,weapon_id=weapon_id)
        self.damage = 45
        self.ammo = 100
        self.ammo_cap = 200
        self.frame_counter = 0
        self.is_automatic = True

class PlasmaRifleWeapon(Weapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/plasma_rifle/0.png',
                 scale=4.3,
                 animation_time=105,
                 weapon_id=5):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time,weapon_id=weapon_id)
        self.damage = 35
        self.ammo = 25
        self.ammo_cap = 25
        self.frame_counter = 0

class BFGWeapon(Weapon):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/bfg/0.png',
                 scale=3,
                 animation_time=105,
                 weapon_id=6):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time,weapon_id=weapon_id)
        self.damage = 65
        self.ammo = 50
        self.ammo_cap = 50
        self.frame_counter = 0



