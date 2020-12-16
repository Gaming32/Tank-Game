from sys import stdout

import pygame
from pygame import *
from pygame.locals import *

pygame.init()
# FULLSCREEN = 0
screen = pygame.display.set_mode((1920, 1080), FULLSCREEN | SCALED)

from tank_game.tank import Tank
from tank_game import config


tank = Tank()
camera = Vector2(-960, -540)

rotate_dir = 0
move_dir = 0


clock = pygame.time.Clock()
running = True

smoothfps = 1000
fps_smoothing = 0.9

while running:
    delta_time = clock.tick() / 1000
    if delta_time > 0:
        thisfps = 1 / delta_time
    else:
        thisfps = 1000
    smoothfps = (smoothfps * fps_smoothing) + (thisfps * (1 - fps_smoothing))
    stdout.write(f'FPS: {int(smoothfps)}{" " * 24}\r')

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_w:
                move_dir = 1
            elif event.key == K_s:
                move_dir = -1
            elif event.key == K_a:
                rotate_dir = -1
            elif event.key == K_d:
                rotate_dir = 1
        if event.type == KEYUP:
            if event.key in (K_w, K_s):
                move_dir = 0
            elif event.key in (K_a, K_d):
                rotate_dir = 0

    screen.fill((128, 128, 128))

    if move_dir:
        tank.move(int(move_dir * config.MOVE_SPEED * delta_time))
    if rotate_dir:
        tank.rotate(int(rotate_dir * config.ROTATE_SPEED * delta_time))
    tank.render(screen, camera)
    pygame.display.update()
