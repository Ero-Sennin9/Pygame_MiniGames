import pygame
import sys
import os

FPS = 50
size = WIDTH, HEIGHT = 800, 600
pygame.init()
screen = pygame.display.set_mode(size)


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    filename = "photos/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda s: s.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None  # размеры игрового поля
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '&':
                Tile('selector', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(level, x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_image(name, colorkey=None):
    fullname = os.path.join('photos', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    bgcolor = (51, 51, 51)
    font_color = (255, 255, 153)
    highlite_color = (153, 102, 255)
    font = pygame.font.Font('coders_crux/Coders_Crux.ttf', 72)
    surface_width = 800
    surface_height = 600

    surface_menu = pygame.display.set_mode([surface_width, surface_height])

    pygame.display.set_caption("Test")

    surface_menu.fill(bgcolor)

    def DrawText(text, font, surface_menu, x, y):
        textobj = font.render(text, 1, font_color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface_menu.blit(textobj, textrect)

    DrawText('"MINIGAMES"', font, surface_menu, (surface_width / 2) - 160, (surface_height / 2) - 80)
    DrawText('', font, surface_menu, (surface_width / 2) - 65, (surface_height / 2) - 40)
    DrawText('press any key to start', font, surface_menu, (surface_width / 2) - 290, (surface_height / 2) + 140)

    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        clock.tick(FPS)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, level, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.x = pos_x
        self.y = pos_y
        self.level = level
        self.repaint()

    def repaint(self):
        self.rect = self.image.get_rect().move(
            tile_width * self.x + 13, tile_height * self.y + 5)

    def move(self, dx, dy):
        x = self.x + dx
        y = self.y + dy
        if 0 <= x < level_x and 0 <= y < level_y:
            if self.level[y][x] != '#':
                self.x = x
                self.y = y
                self.repaint()

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    self.move(0, 1)
                elif event.key == pygame.K_LEFT:
                    self.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move(1, 0)


if __name__ == '__main__':
    pygame.display.set_caption('Перемещение героя')
    clock = pygame.time.Clock()
    tile_images = {
        'wall': load_image('Wall_Block_Tall.png'),
        'selector': load_image('Selector.png'),
        'empty': load_image('Plain_Block.png')
    }
    player_image = load_image('boy.png')
    tile_width = tile_height = 50

    start_screen()

    player = None
    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    player, level_x, level_y = generate_level(load_level('map.txt'))
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        player.update(events)
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    terminate()