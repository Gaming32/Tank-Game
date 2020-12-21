from __future__ import annotations
import operator
from math import inf

import pygame
from pygame import *
from pygame.locals import *
from pygame.math import Vector2

from tank_game.assets import tank as tank_img, turret as turret_img
from tank_game.utils import rot_center
from tank_game import config, global_vars


class Tank:
    position: Vector2
    rotation: int
    turret_rotation: int

    rotated_tank: Surface
    rotated_turret: Surface

    rot_offset: Vector2
    turret_rot_offset: Vector2
    turret_offset: Vector2

    tot_dist: list[int, int]
    frame: list[int, int]

    default_tank: dict[tuple[int, int], Surface] = tank_img
    default_turret: Surface = turret_img

    tank_moved_since_turret: bool

    moving_async: bool
    rotating_async: bool

    max_health: float
    health: float

    def __init__(self, health: float = 100) -> None:
        self.position = Vector2()
        self.rotation = 0
        self.turret_rotation = 0
        self.rotated_tank = self.default_tank[(0, 0)]
        self.rotated_turret = self.default_turret
        self.rot_offset = Vector2()
        self.turret_rot_offset = Vector2()
        self.turret_offset = Vector2(0, config.TURRET_OFFSET)
        self.tot_dist = [0, 0]
        self.frame = [0, 0]
        self.tank_moved_since_turret = True
        self.moving_async = False
        self.rotating_async = False
        self.max_health = health
        self.health = health

    def update_image(self):
        use_img = self.default_tank[tuple(self.frame)]
        self.rotated_tank, newrect = rot_center(use_img, -self.rotation, use_img.get_width() // 2, use_img.get_height() // 2)
        self.rot_offset.update(Vector2(newrect.width - use_img.get_width(), newrect.height - use_img.get_height()) * -0.5)

    def rotate(self, amnt: int):
        self.rotation += amnt
        self.turret_offset.from_polar((config.TURRET_OFFSET, self.rotation + 90))
        if amnt > 0:
            self.tot_dist[0] += amnt / 4
            self.tot_dist[1] -= amnt / 4
        else:
            self.tot_dist[0] -= amnt / 4
            self.tot_dist[1] += amnt / 4
        self.set_frame(False)
        self.update_image()

    def set_turret_rotation(self, rot: int):
        self.turret_rotation = rot
        use_img = self.default_turret
        toffset_tup = tuple(self.turret_offset + (use_img.get_width() // 2, use_img.get_height() // 2))
        self.rotated_turret, newrect = rot_center(use_img, -self.turret_rotation, *toffset_tup)
        self.turret_rot_offset.update(Vector2(newrect.width - use_img.get_width(), newrect.height - use_img.get_height()) * -0.5)
        self.tank_moved_since_turret = False

    def move(self, dist: int):
        move = Vector2()
        move.from_polar((dist, self.rotation - 90))
        self.position += move
        self.tot_dist[0] += dist
        self.tot_dist[1] += dist
        self.set_frame()
        self.tank_moved_since_turret = True

    def move_async(self, dist: int, speed: int, collision: bool = True):
        while self.moving_async:
            yield
        self.moving_async = True
        curmov = 0
        useop = operator.lt if dist >= 0 else operator.gt
        while useop(curmov, dist):
            to_move = speed * global_vars.delta_time
            if not (collision and self.will_collide(to_move, global_vars.all_tanks)):
                self.move(to_move)
            curmov += to_move
            yield
        self.moving_async = False

    def rotate_async(self, amnt: int, speed: int):
        while self.rotating_async:
            yield
        self.rotating_async = True
        currot = 0
        useop = operator.lt if amnt >= 0 else operator.gt
        while useop(currot, amnt):
            to_rotate = speed * global_vars.delta_time
            self.rotate(to_rotate)
            currot += to_rotate
            yield
        self.rotating_async = False

    def set_frame(self, update_img=True):
        old_frame = self.frame[:]
        use_dist = self.tot_dist[:]
        use_dist[0] /= 8
        use_dist[1] /= 8
        self.frame[0] = int(self.tot_dist[0] / 8 % 2)
        self.frame[1] = int(self.tot_dist[1] / 8 % 2)
        if update_img and self.frame != old_frame:
            self.update_image()

    def render(self, surf: Surface, camerapos: Vector2):
        # Render tank
        usepos = self.position - camerapos + self.rot_offset
        userect = Rect(usepos, self.rotated_tank.get_size())
        if global_vars.debug:
            pygame.draw.rect(surf, 'green', userect, 1)
        surf.blit(self.rotated_tank, userect)
        # Render turret
        usepos = self.position - self.turret_offset - camerapos + self.turret_rot_offset
        userect = Rect(usepos, self.rotated_turret.get_size())
        if global_vars.debug:
            pygame.draw.rect(surf, 'red', userect, 1)
        surf.blit(self.rotated_turret, userect)
        # Render health
        max_health_width = self.max_health
        usepos = self.position - camerapos
        usepos.x += 64 - ( max_health_width / 2)
        usepos.y -= 32
        userect = Rect(usepos, (max_health_width, 25))
        pygame.draw.rect(surf, 'red', userect)
        userect = Rect(usepos, (self.health, 25))
        pygame.draw.rect(surf, 'green', userect)
    
    def will_collide(self, dist: int, tanks: list[Tank]):
        if dist == 0:
            return False
        if dist > 0:
            angle = 0
        else:
            angle = 180
        ver_angle = self.rotation + angle
        ver_angle_lt = (ver_angle - 90) % 360
        ver_angle_gt = (ver_angle + 90) % 360
        close_dist = inf
        for other in tanks:
            if other is self:
                continue
            ang = (other.position - self.position).as_polar()[1] + 90
            if ver_angle_lt < ang < ver_angle_gt:
                if (tdist := self.position.distance_squared_to(other.position)) < close_dist:
                    close_dist = tdist
        return close_dist <= 16384
