from sprite_object import *

class GroundItem(AnimatedSprite):
    def __init__(self,
                 game,
                 path='resources/sprites/weapon/shotgun/ground/0.png',
                 item_id =0,
                 pos=(1, 1),
                 scale=0.4,
                 shift=0.16,
                 animation_time=90,
                 quantity=0,
                 weapon_id=0):
        super().__init__(game=game, path=path, pos=pos, scale=scale, shift=shift, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.x, self.y = pos
        self.quantity = quantity
        self.available = False
        self.num_images = len(self.images)
        self.size = 10
        self.frame_counter = 0
        self.weapon_id = weapon_id
        self.item_id = item_id
        self.items = {1: 'ammo', 2: 'ground_gun'}

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
        item_name = self.items.get(self.item_id)
        print(item_name)
        if item_name == 'ammo':
            self.check_picked_up_ammo_item()
        if item_name == 'ground_gun':
            self.check_picked_up_ground_weapon_item()

    #todo when picked up -> gun fires
    def check_picked_up_ammo_item(self):
        if self.game.player.map_pos in self.game.object_handler.ammo_positions:
            if self.game.player.map_pos == self.map_pos and  self.weapon_id == self.weapon_id:
                    for weapon_in_bag in self.game.player.weapon_bag:
                        if weapon_in_bag.weapon_id == self.weapon_id:
                            weapon_in_bag.add_ammo(self.quantity)
                            self.available = False

    #todo lag when picked up gun
    def check_picked_up_ground_weapon_item(self):
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