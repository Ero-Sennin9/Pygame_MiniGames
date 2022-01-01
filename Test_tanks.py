import pygame as pg
import sys
import os
import math
import random


#  настройки pygame
import pygame.sprite

FPS = 60
pg.init()
SIZE = WIDTH, HEIGHT = 1500, 700
screen = pg.display.set_mode(SIZE)
running = True
clock = pg.time.Clock()
SPEED_TANK = 4
SPEED_PATRON = 20
TANK_A = round(0.2, 1)
GRASS_STONES = (80, 80)


def terminate():  # закрытие окна
    pg.quit()
    sys.exit()


def load_image(name, colorkey=None):  # загрузка изображения для спрайта
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


all_sprites = pg.sprite.Group()  # создание групп спрайтов
players = pg.sprite.Group()
rocks = pg.sprite.Group()
grasses = pg.sprite.Group()
patrons = pg.sprite.Group()
boom = pg.sprite.Group()
health = pg.sprite.Group()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, sheet, columns, rows, count_frames=None,
                 paddings=(0, 0, 0, 0)):
        super().__init__(all_sprites)
        self.frames = []
        if count_frames is not None:
            self.count_frames = count_frames
        else:
            self.count_frames = columns * rows
        self.cut_sheet(sheet, columns, rows, paddings)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.center = x, y

    def cut_sheet(self, sheet, columns, rows, paddings):
        self.rect = pygame.Rect(
            0, 0, (sheet.get_width() - paddings[1] - paddings[3]) // columns,
                  (sheet.get_height() - paddings[0] - paddings[2]) // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (
                    paddings[3] + self.rect.w * i,
                    paddings[0] + self.rect.h * j
                )
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
                if self.count_frames == len(self.frames):
                    return

    def update(self):
        self.cur_frame = self.cur_frame + 1
        if self.cur_frame == self.count_frames - 1:
            self.kill()
        self.image = self.frames[self.cur_frame]


class Boom(AnimatedSprite):
    sheet = load_image('boom.png')

    def __init__(self, x, y):
        super().__init__(x, y, self.sheet, 8, 4)
        boom.add(self)


class HealthBar(pg.sprite.Sprite):
    def __init__(self, size, pos, height):
        super().__init__(health)
        bar = pygame.Surface(size)
        bar.fill(pygame.Color("green"))
        pygame.draw.rect(bar, pygame.Color("black"), (0, 0, *size), 3)
        self.image = bar
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.size = size
        self.height = height

    def update(self, player):
        self.image.fill(pygame.Color("white"))
        pygame.draw.rect(self.image, pygame.Color("Green"), (0, 0, (self.size[0] - 2) * player.hp / 100, self.size[1]), 0)
        pygame.draw.rect(self.image, pygame.Color("black"), (0, 0, *self.size), 3)
        self.image = self.image.convert()
        self.image.set_colorkey(pygame.Color("white"))
        self.image = self.image.convert_alpha()
        self.rect.center = player.rect.centerx, player.rect.centery - self.height


class Tank(pg.sprite.Sprite):
    data = [load_image('tank1.png'), load_image('tank2.png')]

    def __init__(self, pos, rotation, player, control):
        super().__init__(players)
        self.pos = pos
        self.control = control  # клавиши для управления танком
        self.image = pygame.transform.rotate(self.data[player - 1], 360 - rotation)  # картинки для спрайтов исходя из номера игрока
        self.image2 = self.data[player - 1]  # а также поворот для картинки
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.angle = rotation
        self.velocity = [0, 0]  # изначальный вектор скорости
        self.data = [False, False, False, False]  # возможность ускорений танка по всем направлениям
        self.slowing = 1  # замедление танка
        self.hp = 100
        self.health_bar = HealthBar([100, 18], (self.pos[0], self.pos[1] - 50), 50)

    def move(self, events):  # управление танком
        for i in events:
            if i.type == pg.KEYDOWN or i.type == pg.KEYUP:
                if i.key == self.control[0]:
                    self.data[0] = not self.data[0]
                if i.key == self.control[1]:
                    self.data[1] = not self.data[1]
                if i.key == self.control[2]:
                    self.data[2] = not self.data[2]
                if i.key == self.control[3]:
                    self.data[3] = not self.data[3]
        self.velocity = [round(self.velocity[0], 1), round(self.velocity[1], 1)]
        if self.data[0] and self.velocity[1] > -SPEED_TANK:
            self.velocity[1] -= TANK_A
        elif self.velocity[1] < 0:
            self.velocity[1] += TANK_A
        if self.data[1] and self.velocity[0] < SPEED_TANK:
            self.velocity[0] += TANK_A
        elif self.velocity[0] > 0:
            self.velocity[0] -= TANK_A
        if self.data[2] and self.velocity[1] < SPEED_TANK:
            self.velocity[1] += TANK_A
        elif self.velocity[1] > 0:
            self.velocity[1] -= TANK_A
        if self.data[3] and self.velocity[0] > -SPEED_TANK:
            self.velocity[0] -= TANK_A
        elif self.velocity[0] < 0:
            self.velocity[0] += TANK_A
        self.rect.move_ip(self.velocity[0] / self.slowing, self.velocity[1] / self.slowing)
        if self.angle_p(self.velocity) != None and any(self.data):  # поворот танка исходя из вектора скорости
            self.rotate(self.angle_p(self.velocity))
        self.mask = pg.mask.from_surface(self.image)
        if pg.sprite.spritecollide(self, rocks, dokill=False, collided=pg.sprite.collide_mask):
            self.slowing = 4
            self.hp -= 0.044
        else:
            self.slowing = 1

    def rotate(self, angle):  # поворот танка
        self.image = pg.transform.rotate(self.image2, 360 - angle)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center  # сохранение центра необходимо для корректного вылета пули
        self.angle = angle

    def shoot(self):  # выстрел
        a, b = math.sin(math.radians(self.angle)) * SPEED_PATRON, -math.cos(math.radians(self.angle)) * SPEED_PATRON  # рассчет вектора скорости исходя из угла поворота танка
        Patron((a, b), self.rect.center, self.angle, self)  # создание пули

    def angle_p(self, vec):  # рассчет угла поворота исходя из вектора скорости
        x, y = vec
        result = None
        if x == 0 or y == 0:
            if x == 0:
                if y < 0:
                    result = 0
                elif y > 0:
                    result = 180
            elif y == 0:
                if x < 0:
                    result = 270
                elif x > 0:
                    result = 90
        else:
            angle1 = math.degrees(math.atan(abs(y) / abs(x)))
            if x < 0 and y < 0:
                result = 270 + angle1
            elif x > 0 and y > 0:
                result = 90 + angle1
            elif x > 0 and y < 0:
                result = 90 - angle1
            elif x < 0 and y > 0:
                result = 270 - angle1
        return result

    def update(self):
        self.health_bar.update(self)

    def damage(self, dam):
        self.hp -= dam

    def return_hp(self):
        self.hp = 100


class Patron(pg.sprite.Sprite):
    pat = pg.transform.scale(pg.transform.rotate(load_image('patron.png', (255, 255, 255)), 90), (10, 40))

    def __init__(self, speed, pos, rotation, player):
        super().__init__(patrons)
        self.speed = speed
        self.image = pg.transform.rotate(self.pat, 360 - rotation)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.player = player

    def update(self):
        for elem in players:
            if elem != self.player:
                if not pg.sprite.collide_mask(self, elem):
                    self.rect.move_ip(*self.speed)
                else:
                    elem.damage(30)
                    Boom(*elem.rect.center)  # взрыв
                    self.kill()
        if pg.sprite.spritecollide(self, rocks, dokill=False, collided=pygame.sprite.collide_mask):
            Boom(*self.rect.center)  # взрыв
            self.kill()
        if self.rect.centerx >= WIDTH + 100 or self.rect.centerx <= -100:
            self.kill()
        if self.rect.centery >= HEIGHT + 100 or self.rect.centery <= -100:
            self.kill()


class Stone(pg.sprite.Sprite):
    stone = pg.transform.scale(load_image('stone.png'), GRASS_STONES)

    def __init__(self, pos):
        super().__init__(rocks)
        self.image = self.stone
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.mask = pygame.mask.from_surface(self.image)
        self.radius = 35


class Grass(pg.sprite.Sprite):
    grass = pg.transform.scale(load_image('grass.png'), GRASS_STONES)

    def __init__(self, pos):
        super().__init__(grasses)
        self.image = self.grass
        self.rect = self.image.get_rect()
        self.rect.center = pos
        # self.mask = pygame.mask.from_surface(self.image)


def generate_level(value_of_grass):  # генерация уровня
    for i in range(value_of_grass):
        while True:
            el = Grass((random.randint(GRASS_STONES[0] / 2 + 1, WIDTH - (GRASS_STONES[0] / 2 + 1)),
                        random.randint(GRASS_STONES[0] / 2 + 1, HEIGHT - (GRASS_STONES[0] / 2 + 1))))
            if not pg.sprite.spritecollide(el, all_sprites, dokill=False, collided=pygame.sprite.collide_circle):
                all_sprites.add(el)
                break
            else:
                el.kill()
        while True:
            el = Stone((random.randint(GRASS_STONES[0] / 2 + 1, WIDTH - (GRASS_STONES[0] / 2 + 1)),
                        random.randint(GRASS_STONES[0] / 2 + 1, HEIGHT - (GRASS_STONES[0] / 2 + 1))))
            if not pg.sprite.spritecollide(el, all_sprites, dokill=False, collided=pygame.sprite.collide_circle):
                all_sprites.add(el)
                break
            else:
                el.kill()


pole = load_image('pole.jpg')
game = True
result = []
if __name__ == '__main__':
    player1 = Tank((50, HEIGHT / 2), 90, 1, [pg.K_w, pg.K_d, pg.K_s, pg.K_a])
    player2 = Tank((WIDTH - 50, HEIGHT / 2), 270, 2, [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT])
    all_sprites.add(player1, player2)
    generate_level(30)
    while running:
        events = pg.event.get()
        if player1.hp <= 0 and game:
            game = False
            result.append(1)
        if player2.hp <= 0 and game:
            game = False
            result.append(2)
        for event in events:
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and game:  # выстрел за второго игрока
                player2.shoot()
            if event.type == pg.KEYDOWN and event.key == pg.K_e and game:  # выстрел за первого игрока
                player1.shoot()
            if event.type == pg.KEYDOWN and event.key == pg.K_p:
                game = True
                player1.rect.center = (50, HEIGHT / 2)
                player2.rect.center = (WIDTH - 50, HEIGHT / 2)
                player1.return_hp()
                player2.return_hp()

        screen.blit(pole, (0, 0))
        if game:
            player1.move(events)  # передвижение игроков
            player2.move(events)
        players.update()
        patrons.update()
        boom.update()
        patrons.draw(screen)
        rocks.draw(screen)
        players.draw(screen)
        health.draw(screen)
        grasses.draw(screen)
        boom.draw(screen)
        if not game:
            if len(result) == 2:
                text = 'ничья'
            else:
                text = 'победил первый игрок' if 2 in result else 'победил второй игрок'
            font = pg.font.Font(None, 50)
            font2 = pg.font.Font(None, 36)
            text = font.render(f'Игра окончена, {text}', True, pygame.Color('red'))
            text2 = font2.render('Нажмите p для перезапуска', True, pygame.Color('yellow'))
            text_x = WIDTH // 2 - text.get_width() // 2
            text_y = HEIGHT // 2 - text.get_height() // 2
            screen.blit(text, (text_x, text_y))
            screen.blit(text2, (text_x, text_y + 50))
        else:
            result = []
        clock.tick(FPS)
        pg.display.flip()
    pg.quit()
    terminate()