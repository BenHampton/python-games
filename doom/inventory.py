from doom.weapon import PistolWeapon


class Inventory:
    def __init__(self, game):
        self.game = game
        self.bag = []
        self.switch_weapons = False

    def update(self):
        pass

    def draw(self):
        pass

 # def update(self):
 #        if self.switch_weapons:
 #            self.draw()
 #        # self.selected_weapon.update(self.game)
 #
 #    def draw(self):
 #        # print(self.selected_weapon(self.game))
 #        self.game.weapon = self.selected_weapon(self.game)
 #        # self.selected_weapon.test(self.game)
 #        self.switch_weapons = False
 #        # [weapon.test() for weapon in self.bag]

