from tank_game.promise import PromisingThread
import pygame
from pygame import *
from pygame.font import Font

from tank_game import config, global_vars
from tank_game.utils import get_load_frame


def trim_ellipses(s: str, l: int):
    if len(s) <= l:
        return s
    return s[:l-3] + '...'


class LeaderboardGUI:
    promise: PromisingThread
    should_close: bool

    def __init__(self, promise: PromisingThread) -> None:
        self.promise = promise
        self.should_close = False

    def render(self, surf: Surface):
        box = surf.get_rect()
        box.x += 100
        box.y += 100
        box.width -= 200
        pygame.draw.rect(surf, (51, 50, 50), box, 0, 50)
        if not self.promise.done:
            if K_ESCAPE in global_vars.pressed_keys:
                self.promise.cancel()
                self.should_close = not global_vars.debug
            render = config.SCORE_FONT.render('Loading scores...', True, (255, 255, 255))
            load_frame = get_load_frame()
            newimg = Surface((render.get_width() + 100 + load_frame.get_width(), max(render.get_height(), load_frame.get_height()))).convert_alpha()
            newimg.fill((0, 0, 0, 0))
            rrect = render.get_rect()
            lrect = load_frame.get_rect()
            lrect.y += newimg.get_height() // 2 - lrect.height // 2
            newimg.blit(load_frame, lrect)
            rrect.x += lrect.width + 100
            rrect.y += newimg.get_height() // 2 - rrect.height // 2
            newimg.blit(render, rrect)
            drect = newimg.get_rect()
            drect.x = 960 - drect.centerx
            drect.y = 590 - drect.centery
            surf.blit(newimg, drect)
            return
        scores = self.promise.return_value[1]
        if scores is None or isinstance(scores, str):
            message = scores if scores is not None and len(scores) < 100 else 'Unable to load scores!'
            render = config.SCORE_FONT.render(message, True, (255, 255, 255))
            drect = render.get_rect()
            drect.x = 960 - drect.centerx
            drect.y = 590 - drect.centery
            surf.blit(render, drect)
        else:
            y = 150
            for score in scores:
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
