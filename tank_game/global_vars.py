from typing import Generator

from tank_game.tank import Tank


delta_time: float
asynchronous: list[Generator[None, None, None]]
debug: bool
all_tanks: list[Tank]
