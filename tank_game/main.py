import random
import logging
import sys

import pygame
from pygame import *
from pygame.locals import *

pygame.init()
# FULLSCREEN = 0
screen = pygame.display.set_mode((1920, 1080), FULLSCREEN | SCALED)
logging.basicConfig(
    format='[%(asctime)s] [%(threadName)s/%(levelname)s] [%(filename)s:%(lineno)i]: %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)

logging.info('Loading assets...')
try:
    from tank_game import config, global_vars, leaderboard_secrets
    from tank_game.utils import StartCoroutine
    from tank_game.tank import Tank
    from tank_game.aitank import AITank
    from tank_game.guileaderboard import LeaderboardGUI
except:
    logging.fatal('Error loading required assets, quitting!', exc_info=True)
    sys.exit(1)
logging.info('Assets loaded!')

logging.info('Initializing pygame.mixer...')
try:
    pygame.mixer.init()
except Exception:
    logging.warning("Error initializing mixer, you won't be able to hear any sound during your experience", exc_info=True)
    global_vars.use_sound = False
else:
    logging.info('Mixer initialized!')
    global_vars.use_sound = True

from tank_game import music


def reset_tank():
    global_vars.time_lasted = 0
    tank.health = config.PLAYER_START_HEALTH
    tank.score = 0
    tank.position.update()
    tank.rotate(-tank.rotation)
    tank.set_turret_rotation(0)


def create_enemies():
    for _ in range(random.randint(2, 4)):
        enemy = AITank(config.ENEMY_START_HEALTH)
        StartCoroutine(enemy.begin(screen))
        enemies.append(enemy)


def is_leaderboard_showing():
    if not (global_vars.show_leaderboard and leaderboard is not None):
        return 0
    elif leaderboard.promise.done or leaderboard.should_close:
        return 2
    return 1


asynchronous = []
global_vars.asynchronous = asynchronous
global_vars.total_time = 0
global_vars.pressed_keys = set()
pygame.mouse.set_system_cursor(SYSTEM_CURSOR_CROSSHAIR)


global_vars.time_lasted = 0
tank = Tank(config.PLAYER_START_HEALTH)
global_vars.camera = Vector2(-960, -540)
enemies: list[AITank] = []
create_enemies()


rotate_dir = 0
move_dir = 0
shot_active = False

death_screen_open = False
global_vars.paused = False
global_vars.show_leaderboard = False
death_screen_close = False

enter_score = config.ENTER_SCORE_BOX
ldboard_manager = leaderboard_secrets.manager
leaderboard: LeaderboardGUI = None


clock = pygame.time.Clock()
running = True

smoothfps = 1000
fps_smoothing = 0.9
global_vars.debug = False
global_vars.all_tanks = [tank] + enemies

music.play_random_song()

while running:
    ms_time = clock.tick(config.FRAMERATE_CAP)
    delta_time = ms_time / 1000
    if delta_time > 0:
        thisfps = 1 / delta_time
    else:
        thisfps = 1000
    smoothfps = (smoothfps * fps_smoothing) + (thisfps * (1 - fps_smoothing))
    global_vars.delta_time = delta_time
    global_vars.total_time += delta_time

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            global_vars.pressed_keys.add(event.key)
            if global_vars.paused:
                if not global_vars.show_leaderboard:
                    global_vars.show_leaderboard = enter_score.handle_key(event)
                    if global_vars.show_leaderboard:
                        leaderboard = LeaderboardGUI(
                            ldboard_manager.newscore(enter_score.text, tank.score, global_vars.time_lasted, include_scores=True)
                        )
            if event.key == K_w:
                move_dir = 1
            elif event.key == K_s:
                move_dir = -1
            elif event.key == K_a:
                rotate_dir = -1
            elif event.key == K_d:
                rotate_dir = 1
            elif event.key == K_F3:
                global_vars.debug = not global_vars.debug
            elif event.key in (K_SPACE, K_ESCAPE):
                ldb_showing = is_leaderboard_showing()
                if death_screen_open and ((event.key == K_ESCAPE and ldb_showing != 1) or ldb_showing == 2):
                    death_screen_close = True
        elif event.type == KEYUP:
            global_vars.pressed_keys.discard(event.key)
            if event.key in (K_w, K_s):
                move_dir = 0
            elif event.key in (K_a, K_d):
                rotate_dir = 0
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if death_screen_open:
                    if is_leaderboard_showing() == 2:
                        death_screen_close = True
                else:
                    shot_active = True

    screen.fill((128, 128, 128))

    to_remove = []
    for fun in asynchronous:
        if next(fun, 'async_end') == 'async_end':
            to_remove.append(fun)
    for fun in to_remove:
        asynchronous.remove(fun)

    if not global_vars.paused:
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
        if not global_vars.paused:
            enemy.update(tank, enemies)
        enemy.render(screen, global_vars.camera)
    for enemy in remove_enemies:
        enemies.remove(enemy)
        global_vars.all_tanks.remove(enemy)
        new = AITank(config.ENEMY_START_HEALTH)
        StartCoroutine(new.begin(screen))
        enemies.append(new)
        global_vars.all_tanks.append(new)

    if not global_vars.paused:
        if shot_active:
            StartCoroutine(tank.shoot(screen, enemies))
            shot_active = False

    if not global_vars.paused:
        if tank.dead():
            death_screen_open = True
            global_vars.paused = True
            global_vars.show_leaderboard = False
            enter_score.clear()
            music.stop_music()
        else:
            global_vars.time_lasted += delta_time

    if global_vars.debug:
        fps_display = config.FPS_FONT.render(f'FPS: {thisfps:.1f}/{smoothfps:.1f} ({ms_time}ms)', False, (255, 255, 255))
        screen.blit(fps_display, fps_display.get_rect())

    if not global_vars.paused:
        score_disp = config.SCORE_FONT.render(f'Score: {tank.score}', True, 'purple')
        score_rect = score_disp.get_rect()
        score_rect.x = 960 - score_rect.centerx
        score_rect.y = 35
        screen.blit(score_disp, score_rect)

        time_disp = config.SCORE_FONT.render(f'Time: {int(global_vars.time_lasted)}', True, 'purple')
        time_rect = time_disp.get_rect()
        time_rect.x = 960 - time_rect.centerx
        time_rect.y = score_rect.bottom + 15
        screen.blit(time_disp, time_rect)

    elif not global_vars.show_leaderboard:
        rendered = config.FINAL_INFO_HEADER_FONT.render('You Died!', True, 'darkgreen')
        dest_rect = rendered.get_rect()
        dest_rect.x = 960 - dest_rect.centerx
        dest_rect.y = 200 - dest_rect.centery
        screen.blit(rendered, dest_rect)

        rendered = config.FINAL_INFO_BODY_FONT.render(f'You had a final score of {tank.score}', True, 'darkgreen')
        dest_rect = rendered.get_rect()
        dest_rect.x = 960 - dest_rect.centerx
        dest_rect.y = 350 - dest_rect.centery
        screen.blit(rendered, dest_rect)

        rendered = config.FINAL_INFO_BODY_FONT.render(f'And you survived for {global_vars.time_lasted:.3f} seconds', True, 'darkgreen')
        dest_rect = rendered.get_rect()
        dest_rect.x = 960 - dest_rect.centerx
        dest_rect.y = 500 - dest_rect.centery
        screen.blit(rendered, dest_rect)

        rendered = config.FINAL_INFO_BODY_FONT.render('Press escape to play again.', True, 'darkgreen')
        dest_rect = rendered.get_rect()
        dest_rect.x = 960 - dest_rect.centerx
        dest_rect.y = 650 - dest_rect.centery
        screen.blit(rendered, dest_rect)

        rendered = config.FINAL_INFO_BODY_FONT.render('Enter your name below and press enter to submit a score:', True, 'darkgreen')
        dest_rect = rendered.get_rect()
        dest_rect.x = 960 - dest_rect.centerx
        dest_rect.y = 800 - dest_rect.centery
        screen.blit(rendered, dest_rect)

        enter_score.render(screen, True)

    else:
        leaderboard.render(screen)

    death_screen_close = death_screen_close or (global_vars.show_leaderboard and leaderboard.should_close)
    if death_screen_open and death_screen_close:
        death_screen_open = False
        death_screen_close = False
        global_vars.paused = False
        global_vars.show_leaderboard = False
        rmco = []
        for co in asynchronous:
            if not hasattr(co, 'long_lasting'):
                rmco.append(co)
        for co in rmco:
            asynchronous.remove(co)
        reset_tank()
        enemies.clear()
        create_enemies()
        global_vars.all_tanks[1:] = enemies
        music.play_random_song()

    pygame.display.update()
