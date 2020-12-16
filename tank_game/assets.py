from pygame import image, transform


tank = {
    (0, 0): image.load('assets/tank00.bmp').convert_alpha(),
    (0, 1): image.load('assets/tank01.bmp').convert_alpha(),
    (1, 0): image.load('assets/tank10.bmp').convert_alpha(),
    (1, 1): image.load('assets/tank11.bmp').convert_alpha(),
}

for imgid in tank:
    tank[imgid] = transform.scale(tank[imgid], (128, 128))


turret = image.load('assets/turret.bmp').convert_alpha()
turret = transform.scale(turret, (128, 128))
