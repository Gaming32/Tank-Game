from __future__ import annotations
import random

from tank_game.tank import Tank
from tank_game.assets import enemy_tank as tank_img, enemy_turret as turret_img
from tank_game import config, global_vars


class AITank(Tank):
    default_tank = tank_img
    default_turret = turret_img
    ready: bool = False

    def begin(self):
        side = random.randrange(4)
        pos = random.uniform(-960, 960) if side in (0, 1) else random.uniform(-540, 540)
        if side == 0:
            self.position.y = -668
            self.position.x = pos
            self.rotate(180)
        elif side == 1:
            self.position.y = 540
            self.position.x = pos
        elif side == 2:
            self.position.x = -1088
            self.position.y = pos
            self.rotate(90)
        elif side == 3:
            self.position.x = 960
            self.position.y = pos
            self.rotate(-90)
        yield from self.move_async(128, config.MOVE_SPEED)
        self.ready = True

    def update(self, player: Tank, ais: AITank):
        if not self.ready:
            return
        if not self.rotating_async:
            global_vars.asynchronous.append(self.rotate_async(random.randint(-180, 180), config.ROTATE_SPEED))
        if not self.moving_async:
            global_vars.asynchronous.append(self.move_async(random.randrange(675), config.MOVE_SPEED))
