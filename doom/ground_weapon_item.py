from doom.ground_item import GroundItem

class GroundShotgun(GroundItem):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/shotgun/ground/0.png',
                 item_type='ground_weapon',
                 pos=(3.5, 3.5),
                 scale=0.5,
                 animation_time=90,
                 weapon_id=2):
        super().__init__(game=game, path=path, item_type=item_type, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class GroundAxe(GroundItem):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/axe/ground/0.png',
                 item_type='ground_weapon',
                 pos=(1.5, 1.5),
                 scale=0.8,
                 animation_time=90,
                 weapon_id=3):
        super().__init__(game=game, path=path, item_type=item_type, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class GroundChaingun(GroundItem):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/chaingun/ground/0.png',
                 item_type='ground_weapon',
                 pos=(3.5, 6.5),
                 scale=0.2,
                 animation_time=90,
                 weapon_id=4):
        super().__init__(game=game, path=path, item_type=item_type, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class GroundPlasmaRifle(GroundItem):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/plasma_rifle/ground/0.png',
                 item_type='ground_weapon',
                 pos=(3.5, 7.5),
                 scale=0.2,
                 animation_time=90,
                 weapon_id=5):
        super().__init__(game=game, path=path, item_type=item_type, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True

class GroundBFG(GroundItem):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/bfg/ground/0.png',
                 item_type='ground_weapon',
                 pos=(4,4.5),
                 scale=0.5,
                 animation_time=90,
                 weapon_id=6):
        super().__init__(game=game, path=path, item_type=item_type, pos=pos, scale=scale, animation_time=animation_time, weapon_id=weapon_id)
        self.size = 5
        self.available = True