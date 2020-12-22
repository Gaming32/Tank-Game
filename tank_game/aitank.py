from __future__ import annotations
import random

from tank_game.tank import Tank
from tank_game.assets import enemy_tank as tank_img, enemy_turret as turret_img
from tank_game.utils import StartCoroutine, WaitForSeconds
from tank_game import config, global_vars


class AITank(Tank):
    default_tank = tank_img
    default_turret = turret_img
    ready: bool = False

    shoot_speed = tuple[float, float]

    aiming_async: bool

    def begin(self, surf):
        self.aiming_async = False
        self.show_sight = False
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
        self.shoot_speed = (random.uniform(0, 1), random.uniform(0.5, 2.5))
        StartCoroutine(self.always_shooting(surf))
        self.ready = True

    def always_shooting(self, surf):
        while not self.dead():
            yield from WaitForSeconds(random.uniform(*self.shoot_speed))
            while global_vars.paused:
                yield
            shoot_action = self.shoot(surf, global_vars.all_tanks, False)
            StartCoroutine(shoot_action)

    def update(self, player: Tank, ais: AITank):
        if not self.ready:
            return
        if not self.aiming_async:
            StartCoroutine(self.aim(player, random.random() * 5, 1))
        if not self.rotating_async:
            if random.random() > .90: # 10% of rotating randomly
                rotate = random.randint(-720, 720)
            else:
                rotate = (player.position - self.position).as_polar()[1] + 90
                rotate -= self.rotation
            StartCoroutine(self.rotate_async(rotate, random.random() * config.ROTATE_SPEED))
        if not self.moving_async:
            StartCoroutine(self.move_async(random.randrange(675), random.random() * config.MOVE_SPEED))

    def aim(self, player: Tank, time: float, speed: int):
        while self.aiming_async:
            yield
        self.aiming_async = True
        span = 0
        while span < time:
            # to_rotate = min(speed * global_vars.delta_time, amnt - currot)
            dest_rotate = ((player.position - self.position).as_polar()[1] + 90) % 360
            rotate = self.turret_rotation - dest_rotate
            if rotate == 0:
                break
            elif rotate > 0:
                dir = -1
            else:
                dir = 1
            self.set_turret_rotation(self.turret_rotation + speed * dir)
            span += global_vars.delta_time
            yield
        self.aiming_async = False
