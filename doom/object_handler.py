from sprite_object import *
from npc  import *
from random import choices, randrange

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.nps_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites'
        self.anim_sprite_path = 'resources/sprites/animated_sprites'
        add_sprite = self.add_sprite
        self.npc_positions = {}

        #spawn npc
        self.total_enemies = NUM_OF_NPCS * (self.game.map_level + 1)
        self.weights = [70, 20, 10]
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        self.spawn_npc()

        red_flame_path = 'resources/sprites/animated_sprites/red_light/0.png'
        # color with index (g1) - first line Left Object second line Right Object
        # sprite map
        add_sprite(SpriteObject(game, pos=(11.8, 3.2)))
        # g1 - back wall
        add_sprite(AnimatedSprite(game, pos=(14.9, 1.1)))
        add_sprite(AnimatedSprite(game, pos=(14.9, 7.9)))
        # r1 - center
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(5.9, 3.1)))
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(5.9, 4.9)))
        # r2 - right
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(5.1, 7.8)))
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(7.9, 7.8)))

        #npc map
        # add_npc(NPC(game))
        # add_npc(NPC(game, pos=(11.5, 4.5)))

    def spawn_npc(self):
        for i in range(self.total_enemies):
            npc = choices(self.npc_types, self.weights)[0]
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

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
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_completed_level()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)