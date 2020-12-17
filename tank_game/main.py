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
show_fps = False

while running:
    ms_time = clock.tick(config.FRAMERATE_CAP)
    delta_time = ms_time / 1000
    if delta_time > 0:
        thisfps = 1 / delta_time
    else:
        thisfps = 1000
    smoothfps = (smoothfps * fps_smoothing) + (thisfps * (1 - fps_smoothing))

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
            elif (event.key == K_f) and (event.mod & KMOD_ALT) and (event.mod & KMOD_SHIFT):
                show_fps = not show_fps
        if event.type == KEYUP:
            if event.key in (K_w, K_s):
                move_dir = 0
            elif event.key in (K_a, K_d):
                rotate_dir = 0

    screen.fill((128, 128, 128))

    if rotate_dir:
        tank.rotate(int(rotate_dir * config.ROTATE_SPEED * delta_time))
    if move_dir:
        tank.move(int(move_dir * config.MOVE_SPEED * delta_time))
    tank.render(screen, camera)

    if show_fps:
        fps_display = config.FPS_FONT.render(f'FPS: {thisfps:.1f}/{smoothfps:.1f} ({ms_time}ms)', False, (255, 255, 255))
        screen.blit(fps_display, fps_display.get_rect())

    pygame.display.update()
