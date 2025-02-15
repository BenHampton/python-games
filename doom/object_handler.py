from sprite_object import *
from npc  import *

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.count = 1 # replace with enemy count
        self.sprite_list = []
        self.npc_list = []
        self.nps_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites'
        self.anim_sprite_path = 'resources/sprites/animated_sprites'
        add_sprite = self.add_sprite
        add_npc = self.add_npc

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
        # r2 - right
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(5.1, 7.8)))
        add_sprite(AnimatedSprite(game, path=red_flame_path, pos=(7.9, 7.8)))

        #npc map
        if not self.game.npc_disabled:
            add_npc(NPC(game))

    def check_win(self):
        if self.count < 1:
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1000)
            print("first")
            self.game.test_level_change()
            print("second")

    def update(self):
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)