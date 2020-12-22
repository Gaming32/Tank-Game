from typing import Generator

from pygame.math import Vector2

from tank_game.tank import Tank


delta_time: float
asynchronous: list[Generator[None, None, None]]
debug: bool
all_tanks: list[Tank]
camera: Vector2
