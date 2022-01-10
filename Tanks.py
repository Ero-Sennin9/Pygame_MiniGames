import pygame as pg
import sys
import os
import math
import random
import pygame.sprite


def tanks():
    FPS = 60  # настройки pygame
    pg.init()
    SIZE = WIDTH, HEIGHT = 1500, 700
    screen = pg.display.set_mode(SIZE)
    running = True
    clock = pg.time.Clock()
    SPEED_TANK = 4  # максимальная скорость танка
    SPEED_PATRON = 20  # скорость патрона
    TANK_A = round(0.2, 1)  # ускорение танка при нажатии на кнопки движения
    GRASS_STONES = (80, 80)  # размер камней и травы


    def load_image(name, colorkey=None):  # загрузка изображения для спрайта
        fullname = os.path.join('data', name)
        # если файла не существует, то выходим
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


    all_sprites = pg.sprite.Group()  # создание групп спрайтов для каждого типа объектов
    players = pg.sprite.Group()
    rocks = pg.sprite.Group()
    grasses = pg.sprite.Group()
    patrons = pg.sprite.Group()
    boom = pg.sprite.Group()
    health = pg.sprite.Group()
    fires = pg.sprite.Group()


    def angle_p(vec):  # рассчет угла поворота исходя из вектора скорости
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


    class AnimatedSprite(pygame.sprite.Sprite):  # анимация спрайтов
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

        def cut_sheet(self, sheet, columns, rows, paddings):  # нарезка кадров для анимации
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

        def update(self):  # сама анимация
            self.cur_frame = self.cur_frame + 1
            self.image = self.frames[self.cur_frame]


    class Boom(AnimatedSprite):  # анимация взрыва
        sheet = load_image('boom.png')

        def __init__(self, x, y):
            super().__init__(x, y, self.sheet, 8, 4)
            boom.add(self)  # добавление спрайта в группу взрывов

        def update(self):  # анимация взрыва
            self.cur_frame = self.cur_frame + 1
            if self.cur_frame == self.count_frames - 1:  # уничтожение спрайта, если анимация окончена
                self.kill()
            self.image = self.frames[self.cur_frame]


    class Fire(AnimatedSprite):  # анимация пожара
        sheet = load_image('fire.png')

        def __init__(self, player, time):
            super().__init__(player.rect.centerx, player.rect.centery - 40, self.sheet, 4, 4)
            fires.add(self)  # добавление спрайта в группу пожара
            self.time = time
            self.player = player

        def update(self):  # анимация взрыва
            self.rect.center = self.player.rect.centerx, self.player.rect.centery - 40
            self.cur_frame = self.cur_frame + 1
            self.cur_frame %= self.count_frames
            self.time -= 1
            if self.time <= 0:  # уничтожение спрайта, если эффект окончен
                self.kill()
            self.image = self.frames[self.cur_frame]
            self.player.damage(0.089)


    class HealthBar(pg.sprite.Sprite):  # класс полоски здоровья
        def __init__(self, size, pos, height):
            super().__init__(health)
            bar = pygame.Surface(size)  # рисование полоски
            bar.fill(pygame.Color("green"))
            pygame.draw.rect(bar, pygame.Color("black"), (0, 0, *size), 3)
            self.image = bar
            self.rect = self.image.get_rect()
            self.rect.center = pos  # позиция полоски
            self.size = size
            self.height = height  # высота полоски над центром спрайта игрока

        def update(self, player):  # обновление состояние полоски
            self.image.fill(pygame.Color("white"))
            pygame.draw.rect(self.image, pygame.Color("Green"), (2, 0, (self.size[0] - 3) * player.hp / 100, self.size[1]), 0)
            pygame.draw.rect(self.image, pygame.Color("black"), (0, 0, *self.size), 3)
            self.image = self.image.convert()  # делаем прозрачной полоску в месте белого цвета
            self.image.set_colorkey(pygame.Color("white"))
            self.image = self.image.convert_alpha()
            self.rect.center = player.rect.centerx, player.rect.centery - self.height  # рисование полоски с учетом высоты


    class Tank(pg.sprite.Sprite):  # класс танка
        data = [pygame.transform.scale(load_image('tank1.png'), (40, 55)),
                pygame.transform.scale(load_image('tank2.png'), (40, 55))]  # загрузка изображений двух игроков

        def __init__(self, pos, rotation, player, control):
            super().__init__(players)
            self.pos = pos
            self.control = control  # клавиши для управления танком
            self.image = pygame.transform.rotate(self.data[player - 1], 360 - rotation)  # картинки для спрайтов исходя из номера игрока
            self.image2 = self.data[player - 1]  # а также поворот картинки
            self.mask = pygame.mask.from_surface(self.image)  # создание маски
            self.rect = self.image.get_rect()
            self.rect.center = pos
            self.angle = rotation  # переменная дл хранения изменяющегося угла танка
            self.rotation = rotation  # хранения поворота при спавне
            self.velocity = [0, 0]  # изначальный вектор скорости
            self.data = [False, False, False, False]  # возможность ускорений танка по всем направлениям
            self.slowing = 1  # замедление танка
            self.hp = 100  # здоровье танка
            self.health_bar = HealthBar([100, 18], (self.pos[0], self.pos[1] - 50), 50)  # задание полоски здоровья

        def move(self, events):  # управление танком
            for i in events:
                if i.type == pg.KEYDOWN or i.type == pg.KEYUP:  # при удерживании кнопки управления танком значение передвижения в данном направлении становится True
                    if i.key == self.control[0]:
                        self.data[0] = not self.data[0]
                    if i.key == self.control[1]:
                        self.data[1] = not self.data[1]
                    if i.key == self.control[2]:
                        self.data[2] = not self.data[2]
                    if i.key == self.control[3]:
                        self.data[3] = not self.data[3]
            self.velocity = [round(self.velocity[0], 1), round(self.velocity[1], 1)]  # округление скоростей, так как почему-то в процессе прибавления и убавления они изменяются
            if self.data[0] and self.velocity[1] > -SPEED_TANK:  # ускорение танка в соответсвии с удерживаемыми кнопками
                self.velocity[1] -= TANK_A
            elif self.velocity[1] < 0:
                self.velocity[1] += TANK_A
            if self.data[1] and self.velocity[0] < SPEED_TANK:
                self.velocity[0] += TANK_A
            elif self.velocity[0] > 0:
                self.velocity[0] -= TANK_A
            if self.data[2] and self.velocity[1] < SPEED_TANK:  # и, следовательно, замедление в случае отпускания кнопок
                self.velocity[1] += TANK_A
            elif self.velocity[1] > 0:
                self.velocity[1] -= TANK_A
            if self.data[3] and self.velocity[0] > -SPEED_TANK:
                self.velocity[0] -= TANK_A
            elif self.velocity[0] < 0:
                self.velocity[0] += TANK_A
            if angle_p(self.velocity) != None and any(self.data):  # поворот танка исходя из вектора скорости
                self.rotate(angle_p(self.velocity))
            if self.rect.centerx >= WIDTH - 20 and self.velocity[0] > 0:  # танк не может уйти за границы карты
                self.velocity[0] = 0
            elif self.rect.centery >= HEIGHT - 20 and self.velocity[1] > 0:
                self.velocity[1] = 0
            if self.rect.centerx <= 20 and self.velocity[0] < 0:
                self.velocity[0] = 0
            elif self.rect.centery <= 20 and self.velocity[1] < 0:
                self.velocity[1] = 0

            self.rect.move_ip(self.velocity[0] / self.slowing, self.velocity[1] / self.slowing)  # передвижение танка с учетом замдления
            self.mask = pg.mask.from_surface(self.image)  # обновление маски, так как он все время поворачивается
            if pg.sprite.spritecollide(self, rocks, dokill=False, collided=pg.sprite.collide_mask):  # при столкновении с камнем снижается скорость и наносится урон
                self.slowing = 4
                self.damage(0.02)
            else:
                self.slowing = 1

        def rotate(self, angle):  # поворот танка
            self.image = pg.transform.rotate(self.image2, 360 - angle)
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center  # сохранение центра необходимо для корректного вылета пули
            self.angle = angle

        def shoot(self):  # выстрел
            a, b = math.sin(math.radians(self.angle)) * SPEED_PATRON, -math.cos(math.radians(self.angle)) * SPEED_PATRON  # рассчет вектора скорости пули исходя из угла поворота танка
            Patron((a, b), self.rect.center, self.angle, self)  # создание пули

        def update(self):  # обновление состояние танка
            self.health_bar.update(self)  # обновление полоски со здоровьем

        def damage(self, dam):  # нанесение урона танку
            self.hp -= dam

        def return_hp(self):  # возвращение танка в начальную позицию
            self.hp = 100
            self.velocity = [0, 0]
            self.angle = self.rotation
            self.data = [False, False, False, False]
            self.image = pg.transform.rotate(self.image2, 360 - self.rotation)


    class Patron(pg.sprite.Sprite):
        pat = pg.transform.scale(pg.transform.rotate(load_image('patron.png', (255, 255, 255)), 90), (10, 40))  # открытие избражения с пулей и ее сжатие

        def __init__(self, speed, pos, rotation, player):
            super().__init__(patrons)
            self.speed = speed
            self.image = pg.transform.rotate(self.pat, 360 - rotation)  # поворот ее на соответствующий градус исходя из поворота танка
            self.mask = pygame.mask.from_surface(self.image)  # создание маски для пули
            self.rect = self.image.get_rect()
            self.rect.center = pos
            self.player = player
            self.collide_with_tank = True  # возможность столкновения с танком

        def update(self):
            for elem in players:
                if elem != self.player:
                    if not pg.sprite.collide_mask(self, elem):  # если не сталкивается с другим игроком, то продолжает движение
                        self.rect.move_ip(*self.speed)
                    else:
                        if self.collide_with_tank:
                            dam = random.randint(4, 10) if random.randint(1, 3) == 2 else random.randint(22, 30)
                            elem.damage(dam)  # нанесение урона при обратном
                            if dam >= 20:  # попадание по танку
                                Boom(*elem.rect.center)  # взрыв танка
                                self.kill()  # уничтожение пули
                                if random.randint(1, 10) == 1:  # c небольшой вероятностью вызывается пожар
                                    Fire(elem, random.randint(10 * FPS, 20 * FPS))
                            else:  # если произошел рикошет - меняем направление пули
                                angle = (angle_p(self.speed) + random.randint(-28, 28)) % 360
                                angle = 360 - abs(angle) if angle < 0 else angle
                                self.speed = (math.sin(math.radians(angle)) * SPEED_PATRON,
                                              -math.cos(math.radians(angle)) * SPEED_PATRON)
                                self.image = pg.transform.rotate(self.pat, 360 - angle)
                                self.mask = pygame.mask.from_surface(self.image)
                            self.collide_with_tank = False
                        else:
                            self.rect.move_ip(*self.speed)

            if pg.sprite.spritecollide(self, rocks, dokill=False, collided=pygame.sprite.collide_mask):  # столкновение с камнем
                Boom(*self.rect.center)  # взрыв пули
                self.kill()  # уничтожение пули
            if self.rect.centerx >= WIDTH + self.rect.width or self.rect.centerx <= -self.rect.width:  # уничтожение пули при вылете за границы для оптимизации игры
                self.kill()  # уничтожение пули
            if self.rect.centery >= HEIGHT + self.rect.width or self.rect.centery <= -self.rect.width:
                self.kill()  # уничтожение пули


    class Stone(pg.sprite.Sprite):  # класс камня
        stone = pg.transform.scale(load_image('stone.png'), GRASS_STONES)  # открытие картинки с камнем

        def __init__(self, pos):
            super().__init__(rocks)  # добавление спрайта в группу камней
            self.image = self.stone
            self.rect = self.image.get_rect()
            self.rect.center = pos
            self.mask = pygame.mask.from_surface(self.image)  # создание маски для камня


    class Grass(pg.sprite.Sprite):  # класс куста
        grass = pg.transform.scale(load_image('grass.png'), GRASS_STONES)  # открытие картинки с кустом

        def __init__(self, pos):
            super().__init__(grasses)
            self.image = self.grass
            self.rect = self.image.get_rect()
            self.rect.center = pos


    def generate_level(value_of_grass, value_of_stones):  # генерация уровня
        for i in range(value_of_grass):
            while True:
                el = Grass((random.randint(GRASS_STONES[0] / 2 + 1, WIDTH - (GRASS_STONES[0] / 2 + 1)),  # создание травы
                            random.randint(GRASS_STONES[0] / 2 + 1, HEIGHT - (GRASS_STONES[0] / 2 + 1))))
                if not pg.sprite.spritecollide(el, all_sprites, dokill=False, collided=pygame.sprite.collide_circle):  # проверка на столкновение с другими объектам
                    all_sprites.add(el)
                    break
                else:
                    el.kill()
        for j in range(value_of_stones):
            while True:
                el = Stone((random.randint(GRASS_STONES[0] / 2 + 1, WIDTH - (GRASS_STONES[0] / 2 + 1)),  # создание камней
                            random.randint(GRASS_STONES[0] / 2 + 1, HEIGHT - (GRASS_STONES[0] / 2 + 1))))
                if not pg.sprite.spritecollide(el, all_sprites, dokill=False, collided=pygame.sprite.collide_circle):  # проверка на столкновение с другими объектами
                    all_sprites.add(el)
                    break
                else:
                    el.kill()


    pole = load_image('pole.jpg')  # загрузка изображения игрового поля
    game = True  # статус игры
    result = []  # результат игры
    score = [0, 0]  # счет
    font, font2 = pg.font.Font(None, 50), pg.font.Font(None, 36)  # шрифты для текста
    colision = True  # необходима для нанесения урона при аварии
    if True:
        player1 = Tank((50, HEIGHT / 2), 90, 1, [pg.K_w, pg.K_d, pg.K_s, pg.K_a])  # создание игроков
        player2 = Tank((WIDTH - 50, HEIGHT / 2), 270, 2, [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT])
        all_sprites.add(player1, player2)  # добавление их в группу всех спрайтов для отслеживания столкновений при генрации карты
        generate_level(25, 25)  # генерация уровня
        while running:
            events = pg.event.get()
            if (player1.hp <= 0 or player2.hp <= 0) and game:
                if player1.hp <= 0:  # окончание игры, если у кого-то из игроков здоровья меньше 0
                    game = False
                    result.append(1)
                if player2.hp <= 0:
                    game = False
                    result.append(2)
                if len(result) == 2:  # если у игроков одновременно здоровье стало меньше нуля - ничья
                    text0 = 'ничья'
                    score = [score[0] + 1, score[1] + 1]
                else:
                    text0 = 'победил первый игрок' if 2 in result else 'победил второй игрок'
                    score = [score[0] + 1, score[1]] if 2 in result else [score[0], score[1] + 1]
            for event in events:
                if event.type == pg.QUIT:  # выход из игры
                    running = False
                if event.type == pg.MOUSEBUTTONDOWN and game:  # выстрел за второго игрока
                    player2.shoot()
                if event.type == pg.KEYDOWN and event.key == pg.K_e and game:  # выстрел за первого игрока
                    player1.shoot()
                if event.type == pg.KEYDOWN and event.key == pg.K_p:  # перезагрузка игры
                    game = True
                    player1.rect.center = (50, HEIGHT / 2)  # размещение игроков в стартовых позициях
                    player2.rect.center = (WIDTH - 50, HEIGHT / 2)
                    player1.return_hp(), player2.return_hp()  # восстановление здоровья у игроков

            if game:
                player1.move(events), player2.move(events)  # передвижение игроков
            players.update(), patrons.update(), boom.update(), fires.update() # обновление спрайтов(анимация, движение, взрывы, обновление полоски здоровья)
            if pygame.sprite.collide_mask(player1, player2):  # при столкновении двух танков наносится урон и накладывается эффект замедления
                player1.slowing, player2.slowing = 4, 4
                if colision:
                    speedx, speedy = abs(player1.velocity[0] - player2.velocity[0]), abs(player1.velocity[1] - player2.velocity[1])
                    speed = (speedx ** 2 + speedy ** 2) ** 0.5
                    damage = (speed / (2 * (SPEED_TANK * 2) ** 2) ** 0.5) * 100
                    damage = random.choice([damage / 4, damage / 3, damage / 2, damage])
                    player1.damage(damage), player2.damage(damage)  # нанесение урона при аварии
                    if damage >= 30:
                        Boom(*player1.rect.center), Boom(*player2.rect.center)  # взрывы при аварии
                    colision = False
                player1.damage(0.03), player2.damage(0.03)
            else:
                colision = True
            screen.blit(pole, (0, 0)), rocks.draw(screen), players.draw(screen)  # отрисовка кадра
            patrons.draw(screen), fires.draw(screen), health.draw(screen), grasses.draw(screen), boom.draw(screen)
            if not game:  # если игра окончена, выводится сообщение с результатом
                text = font.render(f'Игра окончена, {text0}', True, pygame.Color('red'))  # рендер текста
                text2 = font2.render('Нажмите p для перезапуска', True, pygame.Color('yellow'))
                text_x = WIDTH // 2 - text.get_width() // 2  # размещение текста в центре экрана
                text_y = HEIGHT // 2 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))  # отображение текста
                screen.blit(text2, (text_x, text_y + 50))
            else:
                result = []
            text = font.render(f'{score[0]} : {score[1]}', True, pygame.Color('green'))  # рендер текста
            text_x, text_y = text.get_width() // 2, text.get_height() // 2  # размещение текста в верхнем левом углу
            screen.blit(text, (text_x, text_y))  # отображение текста
            clock.tick(FPS)
            pg.display.flip()  # обновление дисплея

