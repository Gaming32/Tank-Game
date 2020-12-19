from tank_game.tank import Tank
from tank_game.assets import enemy_tank as tank_img, enemy_turret as turret_img


class AITank(Tank):
    default_tank = tank_img
    default_turret = turret_img
