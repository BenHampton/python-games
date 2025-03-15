from doom.ground_item import GroundItem

class ShotgunAmmo(GroundItem):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/shotgun/ammo/0.png',
                 item_type='ammo',
                 pos=(3.5, 3.5),
                 scale=0.2,
                 shift=2.5,
                 animation_time=90,
                 quantity=10,
                 weapon_id=2):
        super().__init__(game=game, path=path, item_type=item_type, pos=pos, scale=scale, shift=shift, animation_time=animation_time, quantity=quantity, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class ChaingunAmmo(GroundItem):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/chaingun/ammo/0.png',
                 item_type='ammo',
                 pos=(3.5, 6.5),
                 scale=0.4,
                 shift=1.2,
                 animation_time=90,
                 quantity=100,
                 weapon_id=4):
        super().__init__(game=game, path=path, item_type=item_type, pos=pos, scale=scale, shift=shift, animation_time=animation_time, quantity=quantity, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class PlasmaRifleAmmo(GroundItem):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/plasma_rifle/ammo/0.png',
                 item_type='ammo',
                 pos=(3.5, 7.5),
                 scale=0.5,
                 shift=1,
                 animation_time=90,
                 quantity=20,
                 weapon_id=5):
        super().__init__(game=game, path=path, item_type=item_type, pos=pos, scale=scale, shift=shift, animation_time=animation_time, quantity=quantity, weapon_id=weapon_id)
        self.size = 5
        self.available = True

