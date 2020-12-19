from tank_game import config
from pygame import *
from pygame.locals import *
from pygame.math import Vector2

from tank_game.assets import tank as tank_img, turret as turret_img
from tank_game.utils import rot_center


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

    def __init__(self) -> None:
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
        usepos = self.position - camerapos + self.rot_offset
        surf.blit(self.rotated_tank, Rect(usepos, self.rotated_tank.get_size()))
        usepos = self.position - self.turret_offset - camerapos + self.turret_rot_offset
        surf.blit(self.rotated_turret, Rect(usepos, self.rotated_turret.get_size()))
