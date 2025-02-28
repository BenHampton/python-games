
from settings import *
from player import *
from fire import *
from block import *

pg.init()
pg.display.set_caption("Platformer")
window = pg.display.set_mode((WIDTH, HEIGHT))

def get_block(size):
    path = join('assets', 'Terrain', "Terrain.png")
    image = pg.image.load(path).convert_alpha()
    surface = pg.Surface((size, size), pg.SRCALPHA, 32)
    rect = pg.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pg.transform.scale2x(surface)

def get_background(name):
    image = pg.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

        for obj in objects:
            obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pg.display.update()

def handle_vertical_collision(player, objects, dy):
    collide_objects = []
    for obj in objects:
        if pg.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collide_objects.append(obj)

    return collide_objects

def collide(player, objects, dx):

    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pg.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pg.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if (keys[pg.K_LEFT] or keys[pg.K_a]) and not collide_left:
        player.move_left(PLAYER_VEL)
    if (keys[pg.K_RIGHT] or keys[pg.K_d]) and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "Fire":
            player.make_hit()

def main(window):
    clock = pg.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)

    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)

    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    # blocks = [Block(0, HEIGHT - block_size, block_size)]

    objects = [*floor,
            Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size),
               fire]

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                run = False
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0)
                or (player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0)):
            offset_x += player.x_vel

if __name__ == "__main__":
    main(window)