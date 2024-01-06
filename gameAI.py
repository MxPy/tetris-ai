#! .venv\Scripts\python.exe
#https://github.com/StanislavPetrovV/Python-Tetris

import pygame
from copy import deepcopy
from random import choice, randrange
import numpy as np

class TetrisGame:
    def __init__(self):
        self.W, self.H = 10, 20
        self.TILE = 45
        self.GAME_RES = self.W * self.TILE, self.H * self.TILE
        self.RES = 750, 940
        self.FPS = 60
        self.f_iteration = 0
        self.record = 0
        pygame.init()
        self.sc = pygame.display.set_mode(self.RES)
        self.game_sc = pygame.Surface(self.GAME_RES)
        self.clock = pygame.time.Clock()

        self.grid = [pygame.Rect(x * self.TILE, y * self.TILE, self.TILE, self.TILE) for x in range(self.W) for y in range(self.H)]

        self.figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                            [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                            [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                            [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                            [(0, 0), (0, -1), (0, 1), (-1, -1)],
                            [(0, 0), (0, -1), (0, 1), (1, -1)],
                            [(0, 0), (0, -1), (0, 1), (-1, 0)]]

        self.figures = [[pygame.Rect(x + self.W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in self.figures_pos]
        self.figure_rect = pygame.Rect(0, 0, self.TILE - 2, self.TILE - 2)
        self.field = [[0 for i in range(self.W)] for j in range(self.H)]

        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000

        self.bg = pygame.image.load('img/bg.jpg').convert()
        self.game_bg = pygame.image.load('img/bg2.jpg').convert()

        self.main_font = pygame.font.Font('font/font.ttf', 65)
        self.font = pygame.font.Font('font/font.ttf', 45)

        self.title_tetris = self.main_font.render('TETRIS', True, pygame.Color('darkorange'))
        self.title_score = self.font.render('score:', True, pygame.Color('green'))
        self.title_record = self.font.render('record:', True, pygame.Color('purple'))

        self.get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))

        self.figure, self.next_figure = deepcopy(choice(self.figures)), deepcopy(choice(self.figures))
        self.color, self.next_color = self.get_color(), self.get_color()

        self.score, self.lines = 0, 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

    def check_borders(self):
        for i in range(4):
            if self.figure[i].x < 0 or self.figure[i].x > self.W - 1:
                return False
            elif self.figure[i].y > self.H - 1 or self.field[self.figure[i].y][self.figure[i].x]:
                return False
        return True


    def get_record(self):
        try:
            with open('record') as f:
                return f.readline()
        except FileNotFoundError:
            with open('record', 'w') as f:
                f.write('0')

    def set_record(self, record, score):
        rec = max(int(record), score)
        with open('record', 'w') as f:
            f.write(str(rec))
            
    def reset(self):
        self.set_record(self.record, self.score)
        self.field = [[0 for i in range(self.W)] for i in range(self.H)]
        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000
        self.score = 0
        self.f_iteration = 0

    def play_step(self, action):
        reward = 0
        self.f_iteration += 1
        self.record = self.get_record()
        dx, rotate = 0, False
        self.sc.blit(self.bg, (0, 0))
        self.sc.blit(self.game_sc, (20, 20))
        self.game_sc.blit(self.game_bg, (0, 0))
        # delay for full lines
        for i in range(self.lines):
            pygame.time.wait(200)
            
            
        # control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_DOWN:
                    self.anim_limit = 100
                elif event.key == pygame.K_UP:
                    rotate = True
            
        # [rotate, left, right, down]
        if np.array_equal(action, [1, 0, 0, 0]):
            rotate = True
        elif np.array_equal(action, [0, 1, 0, 0]):
            dx = -1
        elif np.array_equal(action, [0, 0, 1, 0]):
            dx = 1
        else:
            pass#self.anim_limit = 100
            
        # move x
        figure_old = deepcopy(self.figure)
        for i in range(4):
            self.figure[i].x += dx
            if not self.check_borders():
                self.figure = deepcopy(figure_old)
                break
        # move y
        self.anim_count += self.anim_speed
        if self.anim_count > self.anim_limit:
            self.anim_count = 0
            figure_old = deepcopy(self.figure)
            for i in range(4):
                self.figure[i].y += 1
                if not self.check_borders():
                    for i in range(4):
                        self.field[figure_old[i].y][figure_old[i].x] = self.color
                    self.figure, self.color = self.next_figure, self.next_color
                    self.next_figure, self.next_color = deepcopy(choice(self.figures)), self.get_color()
                    self.anim_limit = 2000
                    break
        # rotate
        center = self.figure[0]
        figure_old = deepcopy(self.figure)
        if rotate:
            for i in range(4):
                x = self.figure[i].y - center.y
                y = self.figure[i].x - center.x
                self.figure[i].x = center.x - x
                self.figure[i].y = center.y + y
                if not self.check_borders():
                    self.figure = deepcopy(figure_old)
                    break
        # check lines
        line, self.lines = self.H - 1, 0
        for row in range(self.H - 1, -1, -1):
            count = 0
            for i in range(self.W):
                if self.field[row][i]:
                    count += 1
                self.field[line][i] = self.field[row][i]
            if count < self.W:
                line -= 1
            else:
                self.anim_speed += 3
                self.lines += 1
                reward = 10
                print("sth")
        # compute score
        self.score += self.scores[self.lines]
        # draw grid
        [pygame.draw.rect(self.game_sc, (40, 40, 40), i_rect, 1) for i_rect in self.grid]
        # draw figure
        for i in range(4):
            self.figure_rect.x = self.figure[i].x * self.TILE
            self.figure_rect.y = self.figure[i].y * self.TILE
            pygame.draw.rect(self.game_sc, self.color, self.figure_rect)
        # draw field
        for y, raw in enumerate(self.field):
            for x, col in enumerate(raw):
                if col:
                    self.figure_rect.x, self.figure_rect.y = x * self.TILE, y * self.TILE
                    pygame.draw.rect(self.game_sc, col, self.figure_rect)
        # draw next figure
        for i in range(4):
            self.figure_rect.x = self.next_figure[i].x * self.TILE + 380
            self.figure_rect.y = self.next_figure[i].y * self.TILE + 185
            pygame.draw.rect(self.sc, self.next_color, self.figure_rect)
        # draw titles
        self.sc.blit(self.title_tetris, (485, -10))
        self.sc.blit(self.title_score, (535, 780))
        self.sc.blit(self.font.render(str(self.score), True, pygame.Color('white')), (550, 840))
        self.sc.blit(self.title_record, (525, 650))
        self.sc.blit(self.font.render(self.record, True, pygame.Color('gold')), (550, 710))
        # game over
        game_over = False
        for i in range(self.W):
            if self.field[0][i]:
                reward = -10
                game_over = True
                self.reset()
                return reward, game_over, self.score

        pygame.display.flip()
        self.clock.tick(self.FPS)
        return reward, game_over, self.score     

if __name__ == "__main__":
    tetris_game = TetrisGame()
    while True:
        print(tetris_game.play_step([0,0,0,0]))
        print(tetris_game.field)
    
    
    
