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

    def __init__(self) -> None:
        self.position = Vector2()
        self.rotation = 0
        self.turret_rotation = 0
        self.rotated_tank = tank_img[(0, 0)]
        self.rotated_turret = turret_img
        self.rot_offset = Vector2()

    def rotate(self, amnt: int):
        self.rotation += amnt
        use_img = tank_img[(0, 0)]
        self.rotated_tank, newrect = rot_center(use_img, -self.rotation, use_img.get_width() // 2, use_img.get_height() // 2)
        self.rot_offset.update(Vector2(newrect.width - use_img.get_width(), newrect.height - use_img.get_height()) * -0.5)

    def move(self, dist: int):
        move = Vector2()
        move.from_polar((dist, self.rotation - 90))
        self.position += move

    def render(self, surf: Surface, camerapos: Vector2):
        usepos = self.position - camerapos + self.rot_offset
        surf.blit(self.rotated_tank, Rect(usepos, self.rotated_tank.get_size()))
