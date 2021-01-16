from pygame import Color, image, transform

from tank_game.utils import replace_image_colors


_enemy_color_map = {
    tuple(Color(0x5C, 0x40, 0x33, 255)): Color(0x35, 0x25, 0x1D, 255),
    tuple(Color(0x35, 0x25, 0x1D, 255)): Color(0x5C, 0x40, 0x33, 255)
}

tank = {
    (0, 0): image.load('assets/tank00.bmp').convert_alpha(),
    (0, 1): image.load('assets/tank01.bmp').convert_alpha(),
    (1, 0): image.load('assets/tank10.bmp').convert_alpha(),
    (1, 1): image.load('assets/tank11.bmp').convert_alpha(),
}

enemy_tank = {}

for imgid in tank:
    enemy_tank_img = transform.scale(replace_image_colors(tank[imgid].copy(), _enemy_color_map), (128, 128))
    tank[imgid] = transform.scale(tank[imgid], (128, 128))
    enemy_tank[imgid] = enemy_tank_img


turret = image.load('assets/turret.bmp').convert_alpha()
enemy_turret = transform.scale(replace_image_colors(turret.copy(), _enemy_color_map), (128, 128))
turret = transform.scale(turret, (128, 128))


loading_images = [
    image.load('assets/loading0.bmp').convert_alpha(),
    image.load('assets/loading1.bmp').convert_alpha()
]
for (i, img) in enumerate(loading_images):
    loading_images[i] = transform.scale(img, (100, 100))
