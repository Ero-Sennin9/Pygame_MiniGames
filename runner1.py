import pygame
import os
import random


def runner():
    pygame.init()

    SCREEN_HEIGHT = 600
    SCREEN_WIDTH = 1100
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    RUN = [pygame.image.load(os.path.join("Assets/Player", "PLRUN1_2.png")),
           pygame.image.load(os.path.join("Assets/Player", "PLRUN2_2.png")),
           pygame.image.load(os.path.join("Assets/Player", "PLRUN3_2.png")),
           pygame.image.load(os.path.join("Assets/Player", "PLRUN4_2.png")),
           pygame.image.load(os.path.join("Assets/Player", "PLRUN5_2.png")),
           pygame.image.load(os.path.join("Assets/Player", "PLRUN6_2.png"))]

    JUMP = [pygame.image.load(os.path.join("Assets/Player", "PLJUMP1_2.png")),
            pygame.image.load(os.path.join("Assets/Player", "PLJUMP2_2.png")),
            pygame.image.load(os.path.join("Assets/Player", "PLJUMP3_2.png")),
            pygame.image.load(os.path.join("Assets/Player", "PLJUMP4_2.png")),
            pygame.image.load(os.path.join("Assets/Player", "PLJUMP5_2.png")),
            pygame.image.load(os.path.join("Assets/Player", "PLJUMP6_2.png")),
            pygame.image.load(os.path.join("Assets/Player", "PLJUMP7_2.png")),
            pygame.image.load(os.path.join("Assets/Player", "PLJUMP8_2.png"))]

    BACK = [pygame.image.load(os.path.join("Assets/Player", "image.png"))]

    SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Objects", "SmallCactus1.png")),
                    pygame.image.load(os.path.join("Assets/Objects", "SmallCactus2.png")),
                    pygame.image.load(os.path.join("Assets/Objects", "SmallCactus3.png"))]
    LARGE_OBJECTS = [pygame.image.load(os.path.join("Assets/Objects", "rock_large.png")),
                    pygame.image.load(os.path.join("Assets/Objects", "tree_large.png")),
                    pygame.image.load(os.path.join("Assets/Objects", "LargeCactus3.png"))]

    BIRD = [pygame.image.load(os.path.join("Assets/Bird", "bird1.png")),
            pygame.image.load(os.path.join("Assets/Bird", "bird2.png")),
            pygame.image.load(os.path.join("Assets/Bird", "bird3.png"))]

    BG = pygame.image.load(os.path.join("Assets/Other", "back-2.png"))

    COIN = [pygame.image.load(os.path.join("Assets/Other", "coin.png"))]

    BOOST = [pygame.image.load(os.path.join("Assets/Other", "boost.png"))]

    class Player:
        X_POS = 80
        Y_POS = 450
        Y_POS_DUCK = 480
        JUMP_VEL = 8.5

        def __init__(self):
            self.back_img = BACK
            self.run_img = RUN
            self.jump_img = JUMP

            self.hero_back = False
            self.hero_run = True
            self.hero_jump = False

            self.step_index = 0
            self.jump_vel = self.JUMP_VEL
            self.image = self.run_img[0]
            self.image_jump = self.jump_img[0]
            self.hero_rect = self.image.get_rect()
            self.hero_rect.x = self.X_POS
            self.hero_rect.y = self.Y_POS

        def update(self, userInput):
            global run
            run = True
            if self.hero_back:
                self.back()
            if self.hero_run:
                self.run()
            if self.hero_jump:
                self.jump()

            if self.step_index >= 10:
                self.step_index = 0

            if userInput[pygame.K_UP] and not self.hero_jump:
                self.hero_back = False
                self.hero_run = False
                self.hero_jump = True
            elif userInput[pygame.K_DOWN] and not self.hero_jump:
                self.hero_back = True
                self.hero_run = False
                self.hero_jump = False
            elif not (self.hero_jump or userInput[pygame.K_DOWN]):
                self.hero_back = False
                self.hero_run = True
                self.hero_jump = False
            elif userInput[pygame.QUIT]:
                run = False

        def back(self):
            self.image = self.back_img[0]
            self.hero_rect = self.image.get_rect()
            self.hero_rect.x = self.X_POS
            self.hero_rect.y = self.Y_POS_DUCK
            self.step_index += 1

        def run(self):
            self.image = self.run_img[self.step_index // 5]
            self.hero_rect = self.image.get_rect()
            self.hero_rect.x = self.X_POS
            self.hero_rect.y = self.Y_POS
            self.step_index += 1

        def jump(self):
            self.image = self.jump_img[self.step_index // 4]
            self.player_rect = self.image.get_rect()
            self.player_rect.x = self.X_POS
            self.player_rect.y = self.Y_POS
            self.step_index += 1
            if self.hero_jump:
                self.hero_rect.y -= self.jump_vel * 4
                self.jump_vel -= 0.8
            if self.jump_vel < - self.JUMP_VEL:
                self.hero_jump = False
                self.jump_vel = self.JUMP_VEL

        def draw(self, SCREEN):
            SCREEN.blit(self.image, (self.hero_rect.x, self.hero_rect.y))

    class Obstacle:
        def __init__(self, image, type):
            self.image = image
            self.type = type
            self.rect = self.image[self.type].get_rect()
            self.rect.x = SCREEN_WIDTH

        def update(self):
            self.rect.x -= game_speed
            if self.rect.x < -self.rect.width:
                obstacles.pop()

        def draw(self, SCREEN):
            SCREEN.blit(self.image[self.type], self.rect)

    class Obstacle_coin:
        def __init__(self, image):
            self.image = image
            self.rect = self.image[0].get_rect()
            self.rect.x = SCREEN_WIDTH

        def update(self):
            self.rect.x -= game_speed

            if self.rect.x < -self.rect.width:
                coins.pop()

        def draw(self, SCREEN):
            SCREEN.blit(self.image[0], self.rect)

    class Coin(Obstacle_coin):
        def __init__(self, image):
            super().__init__(image)
            self.rect.y = 470

    class Obstacle_boost:
        def __init__(self, image):
            self.image = image
            self.rect = self.image[0].get_rect()
            self.rect.x = SCREEN_WIDTH * int(random.randint(5, 10))

        def update(self):
            self.rect.x -= game_speed
            if self.rect.x < -self.rect.width:
                boosts.pop()

        def draw(self, SCREEN):
            SCREEN.blit(self.image[0], self.rect)

    class Boost(Obstacle_boost):
        def __init__(self, image):
            super().__init__(image)
            self.rect.y = 430

    class SmallCactus(Obstacle):
        def __init__(self, image):
            self.type = random.randint(0, 2)
            super().__init__(image, self.type)
            self.rect.y = 470

    class LargeObgects(Obstacle):
        def __init__(self, image):
            self.type = random.randint(0, 2)
            super().__init__(image, self.type)
            self.rect.y = 445

    class Bird(Obstacle):
        def __init__(self, image):
            self.type = 0
            super().__init__(image, self.type)
            self.rect.y = 420
            self.index = 0

        def draw(self, SCREEN):
            if self.index >= 9:
                self.index = 0
            SCREEN.blit(self.image[self.index // 5], self.rect)
            self.index += 1

    def main():
        global game_speed, x_pos_bg, y_pos_bg, points, obstacles, coins, coini, boosts
        run = True
        clock = pygame.time.Clock()
        player = Player()
        game_speed = 20
        x_pos_bg = 0
        y_pos_bg = 380
        points = 0
        font = pygame.font.Font('freesansbold.ttf', 20)
        obstacles = []
        coins = []
        boosts = []
        death_count = 0
        coini = 0

        def score():
            global points, game_speed
            points += 1
            if points % 100 == 0:
                game_speed += 1

            text = font.render("Points: " + str(points), True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (1000, 40)
            SCREEN.blit(text, textRect)

        def coin_score():
            text = font.render("Coins: " + str(coini), True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (80, 40)
            SCREEN.blit(text, textRect)

        def background():
            global x_pos_bg, y_pos_bg
            image_width = BG.get_width()
            SCREEN.blit(BG, (0, 0))
            if x_pos_bg <= -image_width:
                SCREEN.blit(BG, (image_width, 0))
                x_pos_bg = 0
            x_pos_bg -= game_speed

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            SCREEN.fill((255, 255, 255))
            userInput = pygame.key.get_pressed()

            background()

            player.draw(SCREEN)
            player.update(userInput)

            if len(obstacles) == 0:
                if random.randint(0, 2) == 0:
                    obstacles.append(SmallCactus(SMALL_CACTUS))
                elif random.randint(0, 2) == 1:
                    obstacles.append(LargeObgects(LARGE_OBJECTS))
                elif random.randint(0, 2) == 2:
                    obstacles.append(Bird(BIRD))

            if len(boosts) == 0:
                boosts.append(Boost(BOOST))

            for boost in boosts:
                boost.draw(SCREEN)
                boost.update()
                if player.hero_rect.colliderect(boost.rect):
                    boosts.pop()
                    if game_speed < 2:
                        game_speed = 1
                    else:
                        game_speed -= 1

            for obstacle in obstacles:
                for boost in boosts:
                    if boost.rect.colliderect(obstacle.rect):
                        boosts.pop()

            if len(coins) == 0:
                coins.append(Coin(COIN))

            for coin in coins:
                coin.draw(SCREEN)
                coin.update()
                if player.hero_rect.colliderect(coin.rect):
                    coins.pop()
                    coini += 1

            for obstacle in obstacles:
                for coin in coins:
                    if coin.rect.colliderect(obstacle.rect):
                        coins.pop()

            score()
            coin_score()

            for obstacle in obstacles:
                obstacle.draw(SCREEN)
                obstacle.update()
                if player.hero_rect.colliderect(obstacle.rect):
                    pygame.time.delay(1000)
                    death_count += 1
                    menu(death_count)
            clock.tick(30)
            pygame.display.update()

    def menu(death_count):
        global points, coini

        run = True
        while run:
            SCREEN.fill((255, 255, 255))
            font = pygame.font.Font('freesansbold.ttf', 30)
            if death_count == 0:
                text = font.render("Press any Key to Start", True, (0, 0, 0))
            elif death_count > 0:
                text = font.render("Press any Key to Restart", True, (0, 0, 0))
                score = font.render("Your Score: " + str(points), True, (0, 0, 0))
                coinsi = font.render("Coins: " + str(coini), True, (0, 0, 0))
                coinsRect = coinsi.get_rect()
                scoreRect = score.get_rect()
                scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
                coinsRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                SCREEN.blit(coinsi, coinsRect)
                SCREEN.blit(score, scoreRect)
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        run = False
            textRect = text.get_rect()
            textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            SCREEN.blit(text, textRect)
            SCREEN.blit(RUN[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
            pygame.display.update()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    main()

    menu(death_count=0)
