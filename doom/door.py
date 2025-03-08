class Door:
    def __init__(self, game):
        self.game = game
        self.door_active_coords = None

    def check_door(self, x, y, dx, dy, scale):
        self.handle_checking_door(int(x + dx * scale), int(y))
        self.handle_checking_door(int(x), int(y + dy * scale))

    def handle_checking_door(self, x, y):
        door_pos = (x, y) in self.game.map.door_interation_coords
        if door_pos:
            self.door_active_coords = (x, y)
            return True
        else:
            self.door_active_coords = None
            return False

    def handle_open_door(self, pos):
        x, y = pos
        self.door_interation_coords.pop((x, y))
        x_offset = x + 1
        self.door_coords.pop((x_offset, y))
        self.world_map.pop((x_offset, y))

