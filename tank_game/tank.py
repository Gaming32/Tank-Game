from __future__ import annotations
import operator
from math import inf

import pygame
from pygame import *
from pygame.locals import *
from pygame.math import Vector2

from tank_game.assets import tank as tank_img, turret as turret_img
from tank_game.utils import rot_center, raycast_line, render_shot
from tank_game import consts, config, global_vars


class Tank:
    position: Vector2
    rotation: int
    turret_rotation: int

    rotated_tank: Surface
    rotated_turret: Surface

    half_size: Vector2

    rot_offset: Vector2
    turret_rot_offset: Vector2
    turret_offset: Vector2
    real_turret_offset: Vector2

    tot_dist: list[int, int]
    frame: list[int, int]

    default_tank: dict[tuple[int, int], Surface] = tank_img
    default_turret: Surface = turret_img

    tank_moved_since_turret: bool

    moving_async: bool
    rotating_async: bool

    max_health: float
    health: float

    show_sight: bool
    score: int

    def __init__(self, health: float = 100) -> None:
        self.position = Vector2()
        self.rotation = 0
        self.turret_rotation = 0
        self.rotated_tank = self.default_tank[(0, 0)]
        self.rotated_turret = self.default_turret
        self.rot_offset = Vector2()
        self.turret_rot_offset = Vector2()
        self.turret_offset = Vector2(0, config.TURRET_OFFSET)
        self.half_size = Vector2(self.default_turret.get_size()) // 2
        real_tur_off = Vector2(self.half_size)
        real_tur_off.y *= -0.25
        self.real_turret_offset = self.turret_offset + real_tur_off
        self.tot_dist = [0, 0]
        self.frame = [0, 0]
        self.tank_moved_since_turret = True
        self.moving_async = False
        self.rotating_async = False
        self.max_health = health
        self.health = health
        self.show_sight = False
        self.score = 0

    def update_image(self):
        use_img = self.default_tank[tuple(self.frame)]
        self.rotated_tank, newrect = rot_center(use_img, -self.rotation, *self.half_size)
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
        # toffset_tup = tuple(self.turret_offset + (use_img.get_width() // 2, use_img.get_height() // 2))
        toffset_tup = tuple(self.real_turret_offset)
        self.rotated_turret, newrect = rot_center(use_img, -self.turret_rotation, *toffset_tup)
        self.turret_rot_offset.update(Vector2(newrect.width - use_img.get_width(), newrect.height - use_img.get_height()) * -0.5)
        self.tank_moved_since_turret = False

    def move(self, dist: int):
        move = Vector2()
        move.from_polar((dist, self.rotation - 90))
        predict = self.position + move
        camrect = Rect(global_vars.camera, (1920, 1080))
        if not camrect.collidepoint(self.position) or camrect.collidepoint(predict):
            self.position.update(predict)
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
            to_move = min(speed * global_vars.delta_time, dist - curmov)
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
            to_rotate = min(speed * global_vars.delta_time, amnt - currot)
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
        
    def gethbox(self) -> tuple[Vector2, Vector2, Vector2, Vector2]:
        ori_offset = self.half_size.rotate(self.rotation)
        origin_corner = self.position - ori_offset + self.half_size # Top left corner
        blc = Vector2() # Bottom left corner
        blc.from_polar((128, self.rotation))
        blc += origin_corner
        trc = Vector2() # Top right corner
        trc.from_polar((128, self.rotation + 90))
        trc += origin_corner
        brc = Vector2() # Bottom right corner
        brc.from_polar((consts.dimension_sqrt2, self.rotation + 45))
        brc += origin_corner
        return origin_corner, blc, trc, brc

    def render(self, surf: Surface, camerapos: Vector2):
        # Render tank
        usepos = self.position - camerapos + self.rot_offset
        userect = Rect(usepos, self.rotated_tank.get_size())
        if global_vars.debug:
            pygame.draw.rect(surf, 'green', userect, 3)
        surf.blit(self.rotated_tank, userect)
        # Render sight
        if self.show_sight:
            usepos = self.position - camerapos + self.real_turret_offset
            dest = Vector2()
            dest.from_polar((2048, self.turret_rotation - 90))
            dest += usepos
            pygame.draw.line(surf, 'red', usepos, dest, 3)
        # Render turret
        usepos = self.position - self.turret_offset - camerapos + self.turret_rot_offset
        userect = Rect(usepos, self.rotated_turret.get_size())
        if global_vars.debug:
            pygame.draw.rect(surf, 'red', userect, 3)
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
        # Render hitbox
        if global_vars.debug:
            pts = self.gethbox()
            for i in range(4):
                for j in range(i, 4):
                    pygame.draw.line(surf, 'blue', pts[i] - camerapos, pts[j] - camerapos, 3)

    def get_collision(self, dist: int, within: int, angle: int, tanks: list[Tank]) -> tuple[bool, float, Tank]:
        if dist == 0:
            return False
        if dist > 0:
            rel_angle = 0
        else:
            rel_angle = 180
        ver_angle = angle + rel_angle
        ver_angle_lt = (ver_angle - 45) % 360
        ver_angle_gt = (ver_angle + 45) % 360
        close_dist = inf
        close_tank = None
        for other in tanks:
            if other is self:
                continue
            ang = (other.position - self.position).as_polar()[1] + 90
            ang %= 360
            if ver_angle_lt < ang < ver_angle_gt:
                if (tdist := self.position.distance_squared_to(other.position)) < close_dist:
                    close_dist = tdist
                    close_tank = other
        return close_dist <= within, close_dist, close_tank

    def will_collide(self, dist: int, tanks: list[Tank]) -> bool:
        return self.get_collision(dist, 16384, self.rotation, tanks)[0]

    def get_shot(self, tanks: list[Tank]) -> tuple[bool, float, Tank]:
        # 1,073,741,824 is 32,768*32,768 (this means we can shoot things up to 32,768 pixels away)
        did, dist, other = self.get_collision(96, 1073741824, self.turret_rotation, tanks)
        would_hit = False
        hitdist = None
        if did:
            pts = other.gethbox()
            would_hit = False
            turret_vec = Vector2()
            turret_vec.from_polar((1, self.turret_rotation + 270))
            for i in range(4):
                for j in range(i, 4):
                    hitdist = raycast_line(self.position, turret_vec, pts[i], pts[j])
                    if hitdist is not None:
                        would_hit = True
                        break
                if would_hit:
                    break
        return would_hit, hitdist, other

    def shoot(self, surf: Surface, tanks: list[Tank], count_points=True):
        would_hit, hitdist, hitted = self.get_shot(tanks)
        if would_hit:
            hitpoint = Vector2()
            hitpoint.from_polar((hitdist, self.turret_rotation + 270))
            hitpoint += self.position
            # yield from self._move_shoot(surf, hitpoint)
            yield from render_shot(surf, hitpoint, 0.5)
            hitted.health -= 34
            self.score += 100 if hitted.dead() else 50

    def _move_shoot(self, surf: Surface, dest: Vector2):
        curpos = Vector2(self.position)
        angle = curpos.angle_to(dest)
        last_angle = angle
        move = Vector2()
        move.from_polar((1, angle + 180))
        while angle == last_angle:
            curpos += move * global_vars.delta_time
            pygame.draw.circle(surf, 'brown', curpos - global_vars.camera, 3)
            last_angle = angle
            angle = curpos.angle_to(dest)
            yield
    
    def dead(self) -> bool:
        return self.health <= 0
