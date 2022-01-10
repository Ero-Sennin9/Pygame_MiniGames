#импорт модулей:
import pygame as pg
from random import randrange
import pymunk.pygame_util
pymunk.pygame_util.positive_y_is_up = False
import math

def test():
    #параметры PyGame
    RES = WIDTH, HEIGHT = 1200, 700
    FPS = 60
    condition = True
    condition1 = True
    condition2 = True
    rad = 350

    pg.init()
    surface = pg.display.set_mode(RES)
    clock = pg.time.Clock()
    clock2 = pg.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(surface)

    #настройки Pymunk
    space = pymunk.Space()
    space.gravity = 0, 0
    time = 0


    def mouse_coll_func(arbiter, space, data):
        s1, s2 = arbiter.shapes
        global condition, condition1, condition2
        condition, condition1 = True, True
        condition2 = False
        # arbiter.shapes[0].body.apply_impulse_at_local_point((0, 20000), (0, 0))
        return True


    def mouse_coll_func2(arbiter, space, data):
        s1, s2 = arbiter.shapes
        global condition
        condition = True
        return True


    def mouse_coll_func3(arbiter, space, data):
        s1, s2 = arbiter.shapes
        global condition
        condition = False
        return True


    def mouse_coll_func4(arbiter, space, data):
        s1, s2 = arbiter.shapes
        global condition1
        condition1 = True
        # print('condition1', condition1)
        return True


    def mouse_coll_func5(arbiter, space, data):
        s1, s2 = arbiter.shapes
        global condition1
        condition1 = False
        # print('condition1', condition1)
        return True


    space.add_collision_handler(
        1, 2
    ).post_solve = mouse_coll_func
    space.add_collision_handler(
        2, 3
    ).post_solve = mouse_coll_func2
    space.add_collision_handler(
        2, 3
    ).separate = mouse_coll_func3

    space.add_collision_handler(
        1, 3
    ).post_solve = mouse_coll_func4
    space.add_collision_handler(
        1, 3
    ).separate = mouse_coll_func5



    def create_square(space, pos, colision, data7):
        square_mass, square_size = 1, (40, 40)
        square_moment = pymunk.moment_for_box(square_mass, square_size)
        square_body = pymunk.Body(square_mass, square_moment)
        square_body.position = pos
        square_shape = pymunk.Poly.create_box(square_body, square_size)
        square_shape.elasticity = 0.6
        square_shape.friction = 0.5
        square_shape.color = [*data7, 255]
        square_shape.collision_type = colision
        space.add(square_body, square_shape)
        return square_body


    def create_kin(space, pos, colision, r):
        square_mass, square_size = 1, ((rad + 47) * 2 * math.sin(math.radians(22.5)), 40)
        square_moment = pymunk.moment_for_box(square_mass, square_size)
        square_body = pymunk.Body(square_mass, square_moment, pymunk.Body.KINEMATIC)
        square_body.position = pos
        square_shape = pymunk.Poly.create_box(square_body, square_size)
        square_shape.elasticity = 0.6
        square_shape.friction = 0.5
        square_shape.color = [r, r, 255, 255]
        square_shape.collision_type = colision
        space.add(square_body, square_shape)
        return square_body


    def create_bruh(space, pos, colision, r, w, h):
        square_mass, square_size = 0.2, (w, h)
        square_moment = pymunk.moment_for_box(square_mass, square_size)
        square_body = pymunk.Body(square_mass, square_moment)
        square_body.position = pos
        square_shape = pymunk.Poly.create_box(square_body, square_size)
        square_shape.elasticity = 0.6
        square_shape.friction = 0.5
        square_shape.color = [r / 2, 255 - r, 255 - r, 255]
        square_shape.collision_type = colision
        space.add(square_body, square_shape)
        return square_body


    x1, y1 = 600, 350
    data = [create_square(space, (x1 - rad + 20, y1), 1, [255, 0, 0]),
            create_square(space, (x1 + rad - 20, y1), 2, [0, 0, 255])]
    square_body = data[1]
    square_body1 = data[0]
    impulse = 600
    x1, y1 = 600, 350
    o = (rad * rad / 2) ** 0.5
    data2 = [create_kin(space, (x1, y1 - rad), 3, 100),
             create_kin(space, (x1 + o, y1 - o), 3, 100),
             create_kin(space, (x1 + rad, y1), 3, 100),
             create_kin(space, (x1 + o, y1 + o), 3, 100),
             create_kin(space, (x1, y1 + rad), 3, 100),
             create_kin(space, (x1 - rad, y1), 3, 100),
             create_kin(space, (x1 - o, y1 + o), 3, 100),
             create_kin(space, (x1 - o, y1 - o), 3, 100)]
    degree = 0
    row, col = 5, 10
    w, h = 80, 30
    data3 = []
    for i in range(row):
        data4 = []
        for j in range(col):

            data4.append(create_bruh(space,
                                     (x1 - w * row / 2 + w / 2 + i * w, y1 - h * col / 2 + h / 2 + j * h), 3, 100, w, h))
        data3.append(data4)

    grav = False
    while True:
        time += 1
        surface.fill(pg.Color('black'))
        angle = square_body.angle % (math.pi * 2)
        a = math.sin(angle) * impulse
        b = math.cos(angle) * impulse
        angle1 = square_body1.angle % (math.pi * 2)
        a1 = math.sin(angle1) * impulse
        b1 = math.cos(angle1) * impulse
        for i in pg.event.get():
            if i.type == pg.QUIT:
                exit()
            elif condition2:
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
                elif i.type == pg.KEYDOWN and i.key == pg.K_b:
                    grav = True
                elif i.type == pg.KEYDOWN and i.key == pg.K_n:
                    grav = False
            elif i.type == pg.KEYDOWN and i.key == pg.K_k:
                condition2 = True
                data[0].position = (x1 + rad - 20, y1)
                data[1].position = (x1 - rad + 20, y1)
                for i1 in range(row):
                    for j1 in range(col):
                        data3[i1][j1].position = (x1 - w * row / 2 + w / 2 + i1 * w, y1 - h * col / 2 + h / 2 + j1 * h)
        if not condition2:
            grav = False
            space.gravity = 0, 1600
            font = pg.font.Font(None, 50)
            font2 = pg.font.Font(None, 36)
            text = font.render('Game Over', True, (100, 255, 100))
            text2 = font2.render('Push K to restart', True, (255, 100, 255))
            text_x = WIDTH // 2 - text.get_width() // 2
            text_y = HEIGHT // 2 - text.get_height() // 2
            surface.blit(text, (text_x, text_y))
            surface.blit(text2, (text_x, text_y + 50))
        degree += 30 / 180 * math.pi / 60
        degree %= 2 * math.pi
        for i in range(len(data2)):
            a = - rad * math.sin(degree + 45 / 180 * math.pi * i)
            b = rad * math.cos(degree + 45 / 180 * math.pi * i)
            data2[i].position = x1 - a, y1 - b
            data2[i].angle = degree + 45 / 180 * math.pi * i
        if time // 60 and grav:
            time %= 60
            data6 = [(0, 1600), (1600, 0), (0, -1600), (-1600, 0), (0, 0)]
            import random
            space.gravity = random.choice(data6)
        elif not grav and condition2:
            space.gravity = 0, 0
        # square_body.angle = 0
        # space.reindex_shapes_for_body(square_body)
        # square_body.center_of_gravity = (0, 0)
        # print(square_body.rotation_vector)
        # print(square_body.center_of_gravity.angle_de)
        space.step(1 / FPS)
        space.debug_draw(draw_options)
        pg.display.flip()
        clock.tick(FPS)
