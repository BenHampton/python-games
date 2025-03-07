from utils.utility import Utility

class EnemyCounter:
    def __init__(self, game):
        self.game = game
        self.text_font = Utility.get_font('doom.ttf', 25)

    def draw(self):
        self.count()

    def count(self):
        total = self.game.object_handler.total_enemies
        text = self.text_font.render(f'Enemies left: {total}', True, 'white')
        self.game.screen.blit(text,(7, 10))

