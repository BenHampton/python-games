from doom.ground_weapon import GroundShotgun, GroundAxe, GroundChaingun
from weapon import *
from npc  import *
from random import choices, randrange

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.ground_weapon_list = []
        self.weapon_bag_list = []
        self.nps_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites'
        self.anim_sprite_path = 'resources/sprites/animated_sprites'
        add_sprite = self.add_sprite

        red_flame_path = 'resources/sprites/animated_sprites/red_light/0.png'
        # color with index (g1) - first line Left Object second line Right Object
        # sprite map
        add_sprite(SpriteObject(game, pos=(11.8, 3.2)))
        # add_sprite(SpriteObject(game, pos=(4.5, 4.5)))
        # add_sprite(SpriteObject(game, pos=(1, 1)))
        # g1 - back wall
        add_sprite(AnimatedSprite(game, pos=(14.9, 1.1)))
        add_sprite(AnimatedSprite(game, pos=(14.9, 7.9)))
        # r1 - center
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(5.9, 3.1)))
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(5.9, 4.9)))
        # r2 - right
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(5.1, 7.8)))
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(7.9, 7.8)))

        # spawn items
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}

        # spawn npc
        self.npc_positions = {}
        self.total_enemies = NUM_OF_NPCS * (self.game.map_level + 1)
        self.weights = [70, 20, 10]
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.spawn_npc()
        # test add npc
        # add_npc(NPC(game))
        # add_npc(NPC(game, pos=(11.5, 4.5)))

        # spawn ground weapons
        self.ground_weapon_positions = {}
        self.total_ground_weapons = 1
        self.available_ground_weapons = [GroundShotgun, GroundAxe, GroundChaingun]
        self.weights = [70, 30]
        # test add ground weapon:
        add_weapon = self.add_ground_weapon
        shotgun_path = 'resources/sprites/weapon/shotgun/ground/0.png'
        add_weapon(GroundShotgun(game, path=shotgun_path, pos=(3.5, 3.5), scale=0.8))

        axe_path = 'resources/sprites/weapon/axe/ground/0.png'
        add_weapon(GroundAxe(game, path=axe_path, pos=(1.5, 1.5), scale=0.8))

        chaingun_path = 'resources/sprites/weapon/chaingun/ground/0.png'
        add_weapon(GroundChaingun(game, path=chaingun_path, pos=(3.5, 6.5), scale=0.2))
        # self.spawn_ground_weapon()


        self.all_weapons = {1: PistolWeapon, 2: ShotgunWeapon, 3: AxeWeapon, 4: ChaingunWeapon}
        # init inventory weapon bag
        self.add_weapon_to_bag(PistolWeapon)

    def spawn_npc(self):
        for i in range(self.total_enemies):
            npc = choices(self.npc_types, self.weights)[0]
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

    def spawn_ground_weapon(self):
        for i in range(len(self.available_ground_weapons)):
            weapon = choices(self.available_ground_weapons, self.weights)[0]
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            self.add_ground_weapon(weapon(self.game, pos=(x + 0.5, y + 0.5)))

    def completed_game(self):
        self.game.object_renderer.win()
        pg.display.flip()
        pg.time.delay(1500)
        self.game.completed_game_results()

    def check_completed_level(self):
        if not len(self.npc_positions):
            if (self.game.map_level + 1) == len(self.game.map.all_maps):
                self.completed_game()
            else:
                self.game.object_renderer.level_completed()
                pg.display.flip()
                pg.time.delay(1500)
                self.game.next_level()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        self.ground_weapon_positions = {gw.map_pos for gw in self.ground_weapon_list if gw.available}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        [weapon.update() for weapon in self.ground_weapon_list]
        self.check_completed_level()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_ground_weapon(self, weapon):
        self.ground_weapon_list.append(weapon)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)

    def add_weapon_to_bag(self, weapon):
        self.game.player.weapon_bag.append(weapon)


