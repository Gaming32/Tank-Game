import random

import pygame
from pygame import *
from pygame.locals import *

pygame.init()
# FULLSCREEN = 0
screen = pygame.display.set_mode((1920, 1080), FULLSCREEN | SCALED)

from tank_game import config, global_vars
from tank_game.utils import StartCoroutine
from tank_game.tank import Tank
from tank_game.aitank import AITank


def reset_tank():
    tank.health = config.PLAYER_START_HEALTH
    tank.position.update()
    tank.rotate(-tank.rotation)
    tank.set_turret_rotation(0)


asynchronous = []
global_vars.asynchronous = asynchronous
pygame.mouse.set_system_cursor(SYSTEM_CURSOR_CROSSHAIR)


tank = Tank(config.PLAYER_START_HEALTH)
global_vars.camera = Vector2(-960, -540)
enemies: list[AITank] = []

for _ in range(random.randrange(5) + 1):
    enemy = AITank(config.ENEMY_START_HEALTH)
    StartCoroutine(enemy.begin(screen))
    enemies.append(enemy)


rotate_dir = 0
move_dir = 0
shot_active = False


clock = pygame.time.Clock()
running = True

smoothfps = 1000
fps_smoothing = 0.9
global_vars.debug = False
global_vars.all_tanks = [tank] + enemies

while running:
    ms_time = clock.tick(config.FRAMERATE_CAP)
    delta_time = ms_time / 1000
    if delta_time > 0:
        thisfps = 1 / delta_time
    else:
        thisfps = 1000
    smoothfps = (smoothfps * fps_smoothing) + (thisfps * (1 - fps_smoothing))
    global_vars.delta_time = delta_time

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_w:
                move_dir = 1
            elif event.key == K_s:
                move_dir = -1
            elif event.key == K_a:
                rotate_dir = -1
            elif event.key == K_d:
                rotate_dir = 1
            elif event.key == K_F3:
            # elif (event.key == K_f) and (event.mod & KMOD_ALT) and (event.mod & KMOD_SHIFT):
                global_vars.debug = not global_vars.debug
        elif event.type == KEYUP:
            if event.key in (K_w, K_s):
                move_dir = 0
            elif event.key in (K_a, K_d):
                rotate_dir = 0
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                shot_active = True

    screen.fill((128, 128, 128))

    to_remove = []
    for fun in asynchronous:
        if next(fun, 'async_end') == 'async_end':
            to_remove.append(fun)
    for fun in to_remove:
        asynchronous.remove(fun)

    if tank.tank_moved_since_turret or Vector2(pygame.mouse.get_rel()):
        tank.set_turret_rotation((Vector2(pygame.mouse.get_pos()) - (tank.position + Vector2(64, 0) + tank.turret_offset - global_vars.camera)).as_polar()[1] + 90)
    if rotate_dir:
        tank.rotate(int(rotate_dir * config.ROTATE_SPEED * delta_time))
    if move_dir:
        dist = int(move_dir * config.MOVE_SPEED * delta_time)
        if not tank.will_collide(dist, enemies):
            tank.move(dist)
    tank.render(screen, global_vars.camera)

    remove_enemies = []
    for enemy in enemies:
        if enemy.dead():
            remove_enemies.append(enemy)
            continue
        enemy.update(tank, enemies)
        enemy.render(screen, global_vars.camera)
    for enemy in remove_enemies:
        enemies.remove(enemy)
        global_vars.all_tanks.remove(enemy)
        new = AITank(config.ENEMY_START_HEALTH)
        StartCoroutine(new.begin(screen))
        enemies.append(new)
        global_vars.all_tanks.append(new)

    if shot_active:
        StartCoroutine(tank.shoot(screen, enemies))
        shot_active = False

    if tank.dead():
        reset_tank()

    if global_vars.debug:
        fps_display = config.FPS_FONT.render(f'FPS: {thisfps:.1f}/{smoothfps:.1f} ({ms_time}ms)', False, (255, 255, 255))
        screen.blit(fps_display, fps_display.get_rect())

    pygame.display.update()
