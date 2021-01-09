import pygame
from pygame import *
from pygame.font import Font

from tank_game import config
from tank_game.leaderboard import Score, ScoreList


def trim_ellipses(s: str, l: int):
    if len(s) <= l:
        return s
    return s[:l-3] + '...'


class LeaderboardGUI:
    scores: list[Score]

    def __init__(self, scores: ScoreList) -> None:
        self.scores = scores

    def render(self, surf: Surface):
        box = surf.get_rect()
        box.x += 100
        box.y += 100
        box.width -= 200
        pygame.draw.rect(surf, (51, 50, 50), box, 0, 50)
        if self.scores is None:
            render = config.SCORE_FONT.render('Unable to load scores!', True, (255, 255, 255))
            drect = render.get_rect()
            drect.x = 960 - drect.centerx
            drect.y = 590 - drect.centery
            surf.blit(render, drect)
        else:
            y = 150
            for score in self.scores:
                render = config.SCORE_FONT.render(trim_ellipses(score.name, 46), True, (255, 255, 255))
                drect = render.get_rect()
                drect.x = 125
                drect.y = y
                surf.blit(render, drect)

                render = config.SCORE_FONT.render(trim_ellipses(str(score.score) + '/' + str(score.seconds), 46), True, (255, 255, 255))
                drect = render.get_rect()
                drect.x = 1795 - drect.width
                drect.y = y
                surf.blit(render, drect)
                y += drect.height * 1.25
