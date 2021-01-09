from pygame import *
import pygame.font

from tank_game.textbox import Textbox


ROTATE_SPEED = 360
MOVE_SPEED = 500

FRAMERATE_CAP = 75

FPS_FONT = pygame.font.SysFont('courier', 70)
SCORE_FONT = pygame.font.Font(None, 70)
FINAL_INFO_HEADER_FONT = pygame.font.Font(None, 180)
FINAL_INFO_BODY_FONT = pygame.font.Font(None, 80)

TURRET_OFFSET = 35

ENEMY_START_HEALTH = 68
PLAYER_START_HEALTH = 250

ENTER_SCORE_BOX = Textbox(
    Rect(585, 900, 750, 50),
    pygame.font.Font(None, 45),
    Color(255, 255, 255),
    Color(127, 127, 127),
    Color(0, 0, 0),
    2, 15, ''
)
