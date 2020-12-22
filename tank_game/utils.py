from math import inf

import pygame
from pygame import Color, Surface, Vector2


def rot_center(image: pygame.Surface, angle: int, x: int, y: int) -> tuple[pygame.Surface, pygame.Rect]:
    
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
