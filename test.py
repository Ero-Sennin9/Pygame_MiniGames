    # импорт модулей:
def test1():
    global times, condition1, condition2, condition, rad, time
    import pygame as pg
    import pymunk.pygame_util
    pymunk.pygame_util.positive_y_is_up = False
    import math
    import time

    # параметры PyGame
    RES = WIDTH, HEIGHT = 1200, 700  # размеры окна
    FPS = 60
    condition = True  # возможность прыжка для первого игрока
    condition1 = True  # возможность прыжка для второго игрока
    condition2 = True  # статус игры
    rad = 350  # радиус движущегося кольца
    SPEED = 15  # скорость кольца
    times = []  # хранение времени

    # инициализация pygame и pymunk
    pg.init()
    surface = pg.display.set_mode(RES)
    clock = pg.time.Clock()  # создание часов
    draw_options = pymunk.pygame_util.DrawOptions(surface)


    # настройки Pymunk
    space = pymunk.Space()  # пространство дял объектов
    space.gravity = 0, 0  # гравитация
    time = 0  # время


    def mouse_coll_func(arbiter, space, data):  # функции, обрабатывающие столкновения
        global condition, condition1, condition2
        condition, condition1 = True, True
        condition2 = False
        return True


    def mouse_coll_func2(arbiter, space, data):
        global condition
        condition = True
        return True


    def mouse_coll_func3(arbiter, space, data):
        global condition
        condition = False
        return True


    def mouse_coll_func4(arbiter, space, data):
        global condition1
        condition1 = True
        return True


    def mouse_coll_func5(arbiter, space, data):
        global condition1
        condition1 = False
        return True


    space.add_collision_handler(1, 2).post_solve = mouse_coll_func  # назначение функций, обрабатывающих столкновения
    space.add_collision_handler(2, 3).post_solve = mouse_coll_func2
    space.add_collision_handler(2, 3).separate = mouse_coll_func3
    space.add_collision_handler(1, 3).post_solve = mouse_coll_func4
    space.add_collision_handler(1, 3).separate = mouse_coll_func5


    def create_square(space, pos, colision, color, size, kin=False, mass=1):  # создание прямоугольника
        square_mass, square_size = mass, size  # масса и размер
        square_moment = pymunk.moment_for_box(square_mass, square_size)  # рассчет момента для объекта исходжя из размера и веса
        if kin:  # создаем объект исходжя из его типа
            square_body = pymunk.Body(square_mass, square_moment, pymunk.Body.KINEMATIC)
        else:
            square_body = pymunk.Body(square_mass, square_moment)  # по умолчанию - DINAMIC
        square_body.position = pos  # задаем координаты объекта
        square_shape = pymunk.Poly.create_box(square_body, square_size)  # создаем его отображение
        square_shape.elasticity = 0.6  # упругость
        square_shape.friction = 0.5  # трение
        square_shape.color = [*color, 255]  # цвет
        square_shape.collision_type = colision  # тип предмета необходим для обрабатывания сталкиваний
        space.add(square_body, square_shape)  # добавляем сам объект и его отображение в пространство
        return square_body

    def main():
        global times, condition1, condition2, condition, rad, time
        x1, y1 = WIDTH // 2, HEIGHT // 2  # центр движущегося кольца
        players = [create_square(space, (x1 - rad + 20, y1), 1, [255, 0, 0], (40, 40)),  # создание игроков
                   create_square(space, (x1 + rad - 20, y1), 2, [0, 0, 255], (40, 40))]
        square_body = players[1]
        square_body1 = players[0]
        impulse = 600  # импульс прыжков
        o = (rad * rad / 2) ** 0.5  # расстояние для построения элементов вращающегося кольца
        size = ((rad + 47) * 2 * math.sin(math.radians(22.5)), 40)  # размер элементов кольца
        circle = [create_square(space, (x1, y1 - rad), 3, [200, 162, 200], size, kin=True),  # создание кольца
                 create_square(space, (x1 + o, y1 - o), 3, [200, 162, 200], size, kin=True),
                 create_square(space, (x1 + rad, y1), 3, [200, 162, 200], size, kin=True),
                 create_square(space, (x1 + o, y1 + o), 3, [200, 162, 200], size, kin=True),
                 create_square(space, (x1, y1 + rad), 3, [200, 162, 200], size, kin=True),
                 create_square(space, (x1 - rad, y1), 3, [200, 162, 200], size, kin=True),
                 create_square(space, (x1 - o, y1 + o), 3, [200, 162, 200], size, kin=True),
                 create_square(space, (x1 - o, y1 - o), 3, [200, 162, 200], size, kin=True)]
        degree = 0  # угол поворота кольца
        row, col = 6, 10  # количество брусков в центре карты
        w, h = 80, 30  # их размер
        blocks = []
        for i in range(row):  # создание блоков в центре окна
            data4 = []
            for j in range(col):
                data4.append(create_square(space, (x1 - w * row / 2 + w / 2 + i * w, y1 - h * col / 2 + h / 2 + j * h), 3,
                                           [100, 100, 100], (w, h), mass=0.2))
            blocks.append(data4)

        grav = False  # значение гравитации(True - случайная гравитация, False - нулевая гравитация)
        while True:
            time += 1
            surface.fill(pg.Color('black'))
            angle = square_body.angle % (math.pi * 2)  # рассчет импульсов для двух тел в силу их вращения
            a = math.sin(angle) * impulse  # для первого тела
            b = math.cos(angle) * impulse
            angle1 = square_body1.angle % (math.pi * 2)
            a1 = math.sin(angle1) * impulse  # для второго тела
            b1 = math.cos(angle1) * impulse
            for i in pg.event.get():
                if i.type == pg.QUIT:  # закрытие игры
                    exit()
                elif condition2:  # cовершение прыжков
                    if i.type == pg.KEYDOWN and i.key == pg.K_UP and condition:
                        square_body.apply_impulse_at_local_point((-a, -b), (0, 0))
                    elif i.type == pg.KEYDOWN and i.key == pg.K_LEFT and condition:
                        square_body.apply_impulse_at_local_point((-b, a), (0, 0))
                    elif i.type == pg.KEYDOWN and i.key == pg.K_RIGHT and condition:
                        square_body.apply_impulse_at_local_point((b, -a), (0, 0))
                    elif i.type == pg.KEYDOWN and i.key == pg.K_DOWN and condition:
                        square_body.apply_impulse_at_local_point((a, b), (0, 0))
                    elif i.type == pg.KEYDOWN and i.key == pg.K_w and condition1:
                        square_body1.apply_impulse_at_local_point((-a1, -b1), (0, 0))
                    elif i.type == pg.KEYDOWN and i.key == pg.K_a and condition1:
                        square_body1.apply_impulse_at_local_point((-b1, a1), (0, 0))
                    elif i.type == pg.KEYDOWN and i.key == pg.K_d and condition1:
                        square_body1.apply_impulse_at_local_point((b1, -a1), (0, 0))
                    elif i.type == pg.KEYDOWN and i.key == pg.K_s and condition1:
                        square_body1.apply_impulse_at_local_point((a1, b1), (0, 0))
                    elif i.type == pg.KEYDOWN and i.key == pg.K_b:  # случайная гравитация
                        grav = True
                    elif i.type == pg.KEYDOWN and i.key == pg.K_n:  # нулевая гравитация
                        grav = False
                elif i.type == pg.KEYDOWN and i.key == pg.K_k:  # перезагрузка игры
                    time = 0  # обнуление времени
                    condition2 = True
                    players[0].position = (x1 + rad - 20, y1)  # размещение игроков в изначальных позициях
                    players[1].position = (x1 - rad + 20, y1)
                    for i1 in range(row):  # возвращение блоков в изначальные позиции
                        for j1 in range(col):
                            blocks[i1][j1].position = (x1 - w * row / 2 + w / 2 + i1 * w, y1 - h * col / 2 + h / 2 + j1 * h)
            degree += SPEED * 2 / 180 * math.pi / 60  # изменение угла поворота кольца
            degree %= 2 * math.pi
            for i in range(len(circle)):  # вращение кольца
                a = - rad * math.sin(degree + 45 / 180 * math.pi * i)  # вычисление позиций каждого из участков кольца
                b = rad * math.cos(degree + 45 / 180 * math.pi * i)
                circle[i].position = x1 - a, y1 - b
                circle[i].angle = degree + 45 / 180 * math.pi * i
            if time % (FPS / 2) == 0 and grav:  # установление случайной гравитации
                import random
                space.gravity = (random.randint(-1600, 1600), random.randint(-1600, 1600))
                print(time)
            elif not grav and condition2:  # нулевая гравитация
                space.gravity = 0, 0
            space.step(1 / FPS)  # обновление пространства с телами
            space.debug_draw(draw_options)  # отрисовка тел
            if not condition2:  # игра окончена
                grav = False
                font = pg.font.Font(None, 50)  # вывод сообщения об окончании игры
                font2 = pg.font.Font(None, 36)
                times.append(round(time / FPS, 2))
                text = font.render(f'Game Over, {times[0]}', True, pg.Color('green'))
                text2 = font2.render('Push K to restart', True, pg.Color('purple'))
                text_x = WIDTH // 2 - text.get_width() // 2
                text_y = HEIGHT // 2 - text.get_height() // 2
                surface.blit(text, (text_x, text_y))
                surface.blit(text2, (text_x, text_y + 50))
            else:
                times = []
            pg.display.flip()  # обновление экрана pygame
            clock.tick(FPS)
    main()