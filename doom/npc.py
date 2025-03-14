from sprite_object import *
from random import randint, random

class NPC(AnimatedSprite):
    def __init__(self,
                 game,
                 path='resources/sprites/npc/soldier/0.png',
                 pos=(10.5, 5.5),
                 scale=0.6,
                 shift=0.38,
                 animation_time=100):
    # def __init__(self, game, path, pos, scale, shift, animation_time):
        super(NPC, self).__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

        self.attack_dist = randint(3, 6)
        self.speed = 0.01
        self.size = 10
        self.health = 100
        self.attack_damage = 10
        self.accuracy = 0.15
        self.search_step_count = 0
        self.alive = True
        self.pain = False
        self.frame_count = 0

        self.ray_casting_value = False
        self.player_search_trigger = False

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()
        if self.game.test_mode:
            self.draw_ray_cast_for_test()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self):
        next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos

        if self.game.test_mode:
            dim = TEST_SPAWN_COVERAGE_DIM[self.game.current_level]
            pg.draw.rect(self.game.screen, 'green', (dim * next_x, dim * next_y, dim, dim))

        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)

    def attack(self):
        if self.animation_trigger:
            if not self.game.sound_disabled:
                self.game.sound.npc_attack.play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_count < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_count += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_casting_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                if not self.game.sound_disabled:
                    self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True

                self.health -= self.game.weapon.damage
                self.check_health()

    def check_health(self):
        if self.health < 1:
            self.alive = False
            if not self.game.sound_disabled:
                self.game.sound.npc_death.play()

    def reset_search_step_count(self):
        self.search_step_count = 0

    def run_logic(self):
        if self.alive:
            if self.game.npc_disabled_walk:
                return
            self.ray_casting_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()
            if self.pain:
                self.animate_pain()

            elif self.ray_casting_value:
                self.player_search_trigger = True
                self.reset_search_step_count()

                if self.dist < self.attack_dist and not self.game.npc_disabled:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.movement()

            elif self.player_search_trigger:
                self.animate(self.walk_images)
                self.movement()
                self.search_step_count += 1

                if self.search_step_count == 500:
                    self.player_search_trigger = False

            else:
                self.animate(self.idle_images)
        else:
            self.animate_death()

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos  # player coords
        x_map, y_map = self.game.player.map_pos  # coors of players tile

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontal
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True

    def draw_ray_cast_for_test(self):
        dim = TEST_SPAWN_COVERAGE_DIM[self.game.current_level]
        dim_two = dim // 2
        radius = TEST_SPAWN_RADIUS[self.game.current_level]
        pg.draw.rect(self.game.screen, 'orange',(self.x * dim - dim_two, self.y * dim - dim_two, dim, dim), 2)
        pg.draw.circle(self.game.screen, 'orange',(dim * self.x, dim * self.y),  radius)

        if self.ray_cast_player_npc():
            pg.draw.line(self.game.screen, 'orange',(dim * self.game.player.x, dim * self.game.player.y),(dim * self.x, dim * self.y), 2)

class SoldierNPC(NPC):
    def __init__(self,
                 game,
                 path='resources/sprites/npc/soldier/0.png',
                 pos=(10.5, 5.5),
                 scale=0.6,
                 shift=0.38,
                 animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)

class CacoDemonNPC(NPC):
    def __init__(self,
                 game,
                 path='resources/sprites/npc/caco_demon/0.png',
                 pos=(10.5, 6.5),
                 scale=0.7,
                 shift=0.27,
                 animation_time=250):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 1.0
        self.health = 150
        self.attack_damage = 25
        self.speed = 0.03
        self.accuracy = 0.35

class CyberDemonNPC(NPC):
    def __init__(self,
                 game,
                 path='resources/sprites/npc/cyber_demon/0.png',
                 pos=(11.5, 6.0),
                 scale=1.3,
                 shift=0.04,
                 animation_time=210):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 6
        self.health = 200
        self.attack_damage = 15
        self.speed = 0.005
        self.accuracy = 0.25

