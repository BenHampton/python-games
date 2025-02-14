import pygame as pg

class Sound:
    def __init__(self, game):
        self.game = game
        pg.mixer.init()
        self.path = 'resources/sound/'

        # game
        self.theme = pg.mixer.Sound(self.path + 'theme.mp3')

        # weapons
        self.shotgun = pg.mixer.Sound(self.path + 'shotgun.wav')

        # player
        self.player_pain = pg.mixer.Sound(self.path + 'player_pain.wav')

        # npc
        self.npc_pain = pg.mixer.Sound(self.path + 'npc_pain.wav')
        self.npc_attack = pg.mixer.Sound(self.path + 'npc_attack.wav')
        self.npc_death = pg.mixer.Sound(self.path + 'npc_death.wav')