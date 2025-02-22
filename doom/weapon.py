from pygame.display import update

from sprite_object import *

class Weapon(AnimatedSprite):
    # def __init__(self, game, path, scale, animation_time):
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
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 10
        self.weapon_id = weapon_id

    def animate_shot(self):
        if self.weapon_id == self.game.player.active_weapon_id:
            if self.reloading:
                self.player.shot = False
                if self.animation_trigger:
                    self.images.rotate(-1)
                    self.image = self.images[0]
                    self.frame_counter += 1
                    if self.frame_counter == self.num_images:
                        self.reloading = False
                        self.frame_counter = 0

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
                 scale=0.4,
                 animation_time=90,
                 weapon_id=1):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time,weapon_id=weapon_id)
        self.damage = 10
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
        self.frame_counter = 0

