import pygame
from pygame import *
from pygame.locals import *

from tank_game import global_vars, assets, config


def rot_center(image: Surface, angle: int, x: int, y: int) -> tuple[Surface, Rect]:

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect


def replace_image_colors(surf: Surface, colors: dict[tuple[int, int, int, int], Color]):
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            curcol = tuple(surf.get_at((x, y)))
            if curcol in colors:
                surf.set_at((x, y), colors[curcol])
    return surf


# Lifted from https://stackoverflow.com/a/32146853/8840278
def raycast_line(ray_origin: Vector2, ray_direction: Vector2, pt1: Vector2, pt2: Vector2):
    v1 = ray_origin - pt1
    v2 = pt2 - pt1
    v3 = Vector2(-ray_direction.y, ray_direction.x)

    dot = v2 * v3
    if abs(dot) < 0.000001:
        return None

    t1 = v2.cross(v1) / dot
    t2 = (v1 * v3) / dot

    if t1 >= 0.0 and (t2 >= 0.0 and t2 <= 1.0):
        return t1

    return None


def render_shot(surf: Surface, pos: Vector2, time: float):
    time_passed = 0
    while time_passed < time:
        time_passed += global_vars.delta_time
        pygame.draw.circle(surf, 'orange', pos - global_vars.camera, 15)
        yield


# This is an idea from Unity3D

def StartCoroutine(co):
    global_vars.asynchronous.append(co)


def WaitForSeconds(seconds: float):
    passed = 0
    while passed < seconds:
        passed += global_vars.delta_time
        yield


def get_load_frame() -> Surface:
    return assets.loading_images[int(global_vars.total_time // config.LOADING_TIME_BETWEEN_FRAMES) % len(assets.loading_images)]
