from typing import Generator

from pygame.math import Vector2

from tank_game.tank import Tank


delta_time: float
asynchronous: list[Generator[None, None, None]]
debug: bool
all_tanks: list[Tank]
camera: Vector2
time_lasted: float
paused: bool
show_leaderboard: bool
total_time: float
pressed_keys: set[int]
